import logging
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from .models import Organization, Payment, BalanceLog
from .serializers import WebhookSerializer, OrganizationBalanceSerializer

logger = logging.getLogger(__name__)


class BankWebhookView(APIView):
    """Обработчик входящих вебхуков от банка."""

    def post(self, request):
        serializer = WebhookSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        payment_data = serializer.validated_data

        # Проверка дублирования операции
        if Payment.objects.filter(
            operation_id=payment_data['operation_id']
        ).exists():
            logger.info(
                "Получен дубликат операции: %s",
                payment_data['operation_id']
            )
            return Response(status=status.HTTP_200_OK)

        try:
            with transaction.atomic():
                # Получение или создание организации
                organization, created = Organization.objects.get_or_create(
                    inn=payment_data['payer_inn'],
                    defaults={'balance': 0}
                )

                # Фиксация текущего баланса для лога
                current_balance = organization.balance

                # Создание записи о платеже
                payment = Payment.objects.create(**payment_data)

                # Обновление баланса организации
                organization.balance += payment_data['amount']
                organization.save()

                # Создание лога изменения баланса
                BalanceLog.objects.create(
                    organization=organization,
                    amount=payment_data['amount'],
                    old_balance=current_balance,
                    new_balance=organization.balance,
                    payment=payment
                )

                logger.info(
                    "Начислено %s на счет организации %s. Новый баланс: %s",
                    payment_data['amount'],
                    organization.inn,
                    organization.balance
                )

            return Response(status=status.HTTP_201_CREATED)

        except Exception as error:
            logger.exception(
                "Ошибка обработки платежа %s: %s",
                payment_data['operation_id'],
                str(error)
            )
            return Response(
                {"error": "Внутренняя ошибка сервера"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OrganizationBalanceView(RetrieveAPIView):
    """Представление для получения баланса организации."""
    queryset = Organization.objects.all()
    serializer_class = OrganizationBalanceSerializer
    lookup_field = 'inn'

    def retrieve(self, request, *args, **kwargs):
        try:
            organization = self.get_object()
            serializer = self.get_serializer(organization)
            return Response(serializer.data)
        except Organization.DoesNotExist:
            return Response(
                {"error": "Организация с указанным ИНН не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )
