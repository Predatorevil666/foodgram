from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from users.models import Subscription, User


class UserAdmin(BaseUserAdmin):
    """Админ-панель для управления пользователями."""

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = ('username', 'email',)
    list_filter = ('username', 'email')


class SubscriptionAdmin(admin.ModelAdmin):
    """Админ-панель для управления подписками."""

    list_display = ('user', 'author')
    search_fields = ('user', 'author')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
