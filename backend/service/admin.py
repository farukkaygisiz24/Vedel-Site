from django.contrib import admin

from sales.models import PaymentAllocation

from .models import Device, Job, JobLine, JobSoldUnit


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'party', 'interval_months', 'last_serviced_on', 'next_due')
    search_fields = ('name', 'place', 'party__first_name', 'party__last_name', 'party__company_name')
    list_filter = ('interval_months',)


class JobLineInline(admin.TabularInline):
    model = JobLine
    extra = 0


class JobSoldUnitInline(admin.TabularInline):
    model = JobSoldUnit
    extra = 0


class JobPaymentAllocationInline(admin.TabularInline):
    model = PaymentAllocation
    extra = 0
    fields = ('payment', 'amount')
    raw_id_fields = ('payment',)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('number', 'date', 'time', 'party', 'assignee', 'status', 'grand_total', 'created_by')
    list_filter = ('status',)
    search_fields = ('number', 'party__first_name', 'party__last_name', 'party__company_name')
    inlines = [JobLineInline, JobSoldUnitInline, JobPaymentAllocationInline]
