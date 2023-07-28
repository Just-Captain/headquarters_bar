from django.contrib import admin

from bot.models import User, Worker, Check

admin.site.register(User)
admin.site.register(Worker)

@admin.register(Check)
class CheckAdmin(admin.ModelAdmin):
    list_filter = ('user_profile', 'worker_profile', 'amount')
    list_display = ('user_profile', 'amount', 'create_at', 'worker_profile')

    def __str__(self) -> str:
        return f"Клиент: {self.user_profile} | Сумма чека: {self.amount}"
    
    class Meta:
        verbose_name = "Чек"
        verbose_name_plural = "Чеки"