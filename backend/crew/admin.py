from django.contrib import admin

from .models import CrewDocument, CrewMember


class CrewDocumentInline(admin.TabularInline):
    model = CrewDocument
    extra = 0
    fields = ('title', 'file', 'original_name', 'expires_on')


@admin.register(CrewMember)
class CrewMemberAdmin(admin.ModelAdmin):
    list_display = ('number', 'first_name', 'last_name', 'national_id', 'phone', 'title', 'user', 'is_active')
    search_fields = ('number', 'first_name', 'last_name', 'national_id', 'phone', 'title', 'address')
    raw_id_fields = ('user',)
    list_filter = ('is_active',)
    inlines = [CrewDocumentInline]
