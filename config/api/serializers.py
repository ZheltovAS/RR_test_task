from rest_framework import serializers
from .models import Payment, Organization


class WebhookSerializer(serializers.ModelSerializer):
    """Сериализатор для входящих банковских вебхуков."""
    class Meta:
        model = Payment
        fields = [
            'operation_id',
            'amount',
            'payer_inn',
            'document_number',
            'document_date'
        ]


class OrganizationBalanceSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения баланса организации."""
    class Meta:
        model = Organization
        fields = ['inn', 'balance']
