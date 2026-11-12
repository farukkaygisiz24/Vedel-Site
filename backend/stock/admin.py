from django.contrib import admin

from .models import Category, Product, StockMovement


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku_prefix', 'brand', 'is_klima', 'slug')
    search_fields = ('name', 'sku_prefix', 'brand', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'brand', 'name', 'category', 'device_kind', 'outdoor_name', 'stock_qty', 'alert_on', 'alert_qty', 'buy_price', 'sale_price', 'is_active')
    list_filter = ('category',)
    search_fields = ('sku', 'brand', 'name')
    readonly_fields = ('sku',)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'product', 'qty', 'reason', 'buy_price', 'supplier', 'created_by')
    list_filter = ('reason',)
