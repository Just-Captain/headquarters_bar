from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import User, Check

from decimal import Decimal

@receiver(post_save, sender=Check)
def update_total_spent(sender, instance, created, **kwargs):
    if created:
        amount = Decimal(instance.amount)  # Преобразование типа float в тип decimal.Decimal
        instance.user_profile.total_spent += amount
        instance.user_profile.save()


@receiver(pre_save, sender=User)
def set_discount_percentage(sender, instance, **kwargs):
    if instance.is_special:
        if instance.discount_percentage != 15:
            instance.previous_discount_percentage = instance.discount_percentage
            instance.discount_percentage = 15
    else:
        instance.previous_discount_percentage = instance.discount_percentage
        instance.discount_percentage = instance.calculate_discount_percentage()