from django.apps import AppConfig


class InventoryConfig(AppConfig):
    name = 'inventory'
    verbose_name = 'Inventory Application'

    def ready(self):
        import inventory.signals