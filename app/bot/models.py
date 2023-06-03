from django.db import models

# Create your models here.


class Client(models.Model):
    telegram_id = models.IntegerField(unique=True)
    unique_id = models.IntegerField(unique=True)
    phone = models.CharField(max_length=10)
    balance = models.IntegerField(default=0)
    vip = models.BooleanField(default=False)

class Personal(models.Model):
    telegram_id = models.IntegerField(unique=True)
    unique_id = models.IntegerField(unique=True)