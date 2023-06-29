from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from django.db.models.manager import BaseManager
from asgiref.sync import sync_to_async
import asyncio

class AsyncManager(BaseManager.from_queryset(models.QuerySet)):
    """
    Менеджер модели, который добавляет поддержку асинхронных операций с базой данных.
    """

class UserProfile(models.Model):
    id = models.BigAutoField(primary_key=True)
    external_id = models.PositiveIntegerField(verbose_name='ID пользователя', unique=True)
    phone_number = models.CharField(verbose_name='Номер телефона', max_length=20)
    qr_code = models.ImageField(verbose_name='QR-код пользователя', upload_to='qr_codes', blank=True, null=True)
    is_special = models.BooleanField(verbose_name='VIP клиент', default=False)
    discount_percentage = models.IntegerField(verbose_name='Текущий процент скидки', default=0)
    previous_discount_percentage = models.IntegerField(verbose_name='Предыдущий процент скидки', default=0)
    total_spent = models.DecimalField(verbose_name='Сумма потраченных средств', max_digits=10, decimal_places=2, default=0)
    menu_total = models.FloatField(verbose_name='Сумма текущего меню', default=0.0)
    previous_menu_total = models.FloatField(verbose_name='Предыдущая сумма меню', default=0.0)
    menu_total_timestamp = models.DateTimeField(verbose_name='Время внесения суммы меню', blank=True, null=True)
    signature = models.CharField(verbose_name="Цифровая подпись",max_length=1000, default=0)
    objects = AsyncManager()

    def calculate_discount_percentage(self):

        if self.total_spent >= 5000:
            discount_percentage = 10
        elif self.total_spent >= 3000:
            discount_percentage = 7
        elif self.total_spent >= 2000:
            discount_percentage = 5
        elif self.total_spent >= 1000:
            discount_percentage = 3
        else:
            discount_percentage = 0

        return discount_percentage

    
    @classmethod
    async def create(cls, name):
        loop = asyncio.get_running_loop()
        obj = cls(name=name)
        await loop.run_in_executor(None, obj.save)
        return obj

    def __str__(self):
        return "JobProfile"
    
    async def update_name(self, new_name):
        loop = asyncio.get_running_loop()
        self.name = new_name
        await loop.run_in_executor(None, self.save)

    @sync_to_async
    def save(self, *args, **kwargs):
        """
        Переопределение метода save() для поддержки асинхронного сохранения объекта в базе данных.
        """
        if self.is_special:
            self.discount_percentage = 15

        return super().save(*args, **kwargs)

    def __str__(self):
        return "UserProfile"

    class Meta:
        verbose_name = 'Профиль клиента'
        verbose_name_plural = 'Профили клиентов'

@receiver(pre_save, sender=UserProfile)
def set_discount_percentage(sender, instance, **kwargs):
    if instance.is_special:
        if instance.discount_percentage != 15:
            instance.previous_discount_percentage = instance.discount_percentage
            instance.discount_percentage = 15
    else:
        instance.previous_discount_percentage = instance.discount_percentage
        instance.discount_percentage = instance.calculate_discount_percentage()


class JobProfile(models.Model):
    id = models.BigAutoField(primary_key=True)
    external_id = models.PositiveIntegerField(verbose_name='ID работника', unique=True)
    phone_number = models.CharField(verbose_name='Номер телефона', max_length=20)


    objects = AsyncManager()
    @sync_to_async
    def save(self, *args, **kwargs):
        """
        Переопределение метода save() для поддержки асинхронного сохранения объекта в базе данных.
        """
        return super().save(*args, **kwargs)
    
    @classmethod
    async def create(cls, name):
        loop = asyncio.get_running_loop()
        obj = cls(name=name)
        await loop.run_in_executor(None, obj.save)
        return obj

    def __str__(self):
        return "JobProfile"
    
    async def update_name(self, new_name):
        loop = asyncio.get_running_loop()
        self.name = new_name
        await loop.run_in_executor(None, self.save)

    class Meta:
        verbose_name = 'Профиль работника'
        verbose_name_plural = 'Профили работников'