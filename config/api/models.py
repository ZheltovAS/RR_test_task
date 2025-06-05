from django.db import models


class Organization(models.Model):
    """Модель организации с балансом."""
    inn = models.CharField(
        max_length=12,
        unique=True,
        verbose_name="ИНН организации",
        db_collation='utf8mb4_bin'
    )
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name="Текущий баланс"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Организации"

    def __str__(self):
        return f"Организация ИНН {self.inn}"


class Payment(models.Model):
    """Модель банковского платежа."""
    operation_id = models.UUIDField(
        unique=True,
        verbose_name="Уникальный ID операции",
        editable=False
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Сумма платежа"
    )
    payer_inn = models.CharField(
        max_length=12,
        verbose_name="ИНН плательщика"
    )
    document_number = models.CharField(
        max_length=50,
        verbose_name="Номер платежного документа"
    )
    document_date = models.DateTimeField(
        verbose_name="Дата и время документа"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        indexes = [
            models.Index(fields=['operation_id']),
            models.Index(fields=['payer_inn']),
        ]

    def __str__(self):
        return f"Платеж №{self.document_number}"


class BalanceLog(models.Model):
    """Лог изменений баланса организации."""
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='balance_logs'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Сумма изменения"
    )
    old_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Баланс до изменения"
    )
    new_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Баланс после изменения"
    )
    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Связанный платеж"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Лог баланса"
        verbose_name_plural = "Логи баланса"
        ordering = ['-created_at']

    def __str__(self):
        return (f"Изменение баланса для {self.organization.inn} "
                f"на сумму {self.amount}")
