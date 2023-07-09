from django.contrib import admin

from bot.models import User, Worker, Check

admin.site.register(User)
admin.site.register(Worker)
admin.site.register(Check)
