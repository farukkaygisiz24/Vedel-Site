from django.contrib import admin

from .models import Party, Payment, PaymentAllocation, Sale, SaleLine


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ('number', 'display_name', 'kind', 'phone', 'email', 'created_by', 'created_at')
    list_filter = ('kind',)
    search_fields = (
        'number',
        'first_name',
        'last_name',
        'company_name',
        'phone',
        'phone2',
        'contact2_name',
        'email',
        'tax_no',
        'national_id',
    )


class SaleLineInline(admin.TabularInline):
    model = SaleLine
    extra = 0


class PaymentAllocationInline(admin.TabularInline):
    model = PaymentAllocation
    extra = 0
    fields = ('payment', 'amount')
    raw_id_fields = ('payment',)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('number', 'date', 'party', 'grand_total', 'invoice_status', 'created_by')
    list_filter = ('work_type', 'invoice_status')
    inlines = [SaleLineInline, PaymentAllocationInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'party', 'amount', 'method', 'date', 'created_by')
    list_filter = ('method',)
    search_fields = ('party__number', 'party__first_name', 'party__last_name', 'party__company_name')
