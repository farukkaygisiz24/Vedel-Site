from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Müşteri hesapları'

    def ready(self):
        from .search import register_search_lookups

        register_search_lookups()
