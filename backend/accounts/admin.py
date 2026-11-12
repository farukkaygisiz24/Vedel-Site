from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AuthToken, Customer


@admin.register(Customer)
class CustomerAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'role', 'is_active', 'date_joined')
    fieldsets = UserAdmin.fieldsets + (
        ('B2C', {'fields': ('phone', 'role', 'stock_categories')}),
    )
    filter_horizontal = ('stock_categories',)


@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    readonly_fields = ('key', 'user', 'created_at')
