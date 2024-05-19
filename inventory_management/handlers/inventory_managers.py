from django.db import models


class InventoryManager(models.Manager):
    def filter_by_product(self, product_id):
        return self.filter(product_id=product_id)

    def find_low_stock(self, threshold):
        return self.filter(current_stock__lte=threshold)
