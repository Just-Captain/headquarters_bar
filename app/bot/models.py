from django.db import models

DISCOUNT_CHOICES = [
    (0, '0%'),
    (3, '3%'),
    (5, '5%'),
    (7, '7%'),
    (10, '10%'),
    (15, '15%'),
]

class User(models.Model):
    external_id = models.PositiveIntegerField(verbose_name='ID пользователя', unique=True)
    phone_number = models.CharField(verbose_name='Номер телефона', max_length=20)
    qr_code = models.ImageField(verbose_name='QR-код пользователя', upload_to='qr_codes', blank=True, null=True)
    is_special = models.BooleanField(verbose_name='VIP клиент', default=False)
    discount_percentage = models.IntegerField(verbose_name='Текущий процент скидки', default=0)
    previous_discount_percentage = models.IntegerField(verbose_name='Предыдущий процент скидки', default=0)
    total_spent = models.DecimalField(verbose_name='Сумма потраченных средств', max_digits=10, decimal_places=2, default=0)
    signature = models.CharField(verbose_name="Цифровая подпись",max_length=1000, default=0)

    def calculate_discount_percentage(self):

        if self.total_spent >= 50000:
            discount_percentage = 10
        elif self.total_spent >= 30000:
            discount_percentage = 7
        elif self.total_spent >= 20000:
            discount_percentage = 5
        else:
            discount_percentage = 3

        return discount_percentage


    def __str__(self):
        return f"{self.phone_number}"

    class Meta:
        verbose_name = 'Профиль клиента'
        verbose_name_plural = 'Профили клиентов'


class Worker(models.Model):
    name = models.CharField(verbose_name="Имя", max_length=30, default="None", unique=False)
    external_id = models.PositiveIntegerField(verbose_name='ID работника', unique=True)
    phone_number = models.CharField(verbose_name='Номер телефона', max_length=20)

    def __str__(self):
        return f"{self.phone_number}"
    
    class Meta:
        verbose_name = 'Профиль работника'
        verbose_name_plural = 'Профили работников'


class Check(models.Model):
    user_profile = models.ForeignKey(User, verbose_name="Клиент", on_delete=models.DO_NOTHING)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    create_at = models.DateTimeField(verbose_name='Дата и время', blank=True, null=True)
    worker_profile = models.ForeignKey(Worker, verbose_name="Работник", on_delete=models.DO_NOTHING)

    def __str__(self) -> str:
        return f"Клиент:{self.user_profile} | Сумма чека:{self.amount}"
    
    class Meta:
        verbose_name = "Чек"
        verbose_name_plural = "Чеки"