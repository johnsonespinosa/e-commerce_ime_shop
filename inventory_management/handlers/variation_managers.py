from django.db import models


class VariationManager(models.Manager):
    def get_variations_by_product(self, product_id):
        return self.filter(product_id=product_id)

    def filter_by_state(self, state):
        return self.filter(state=state)

    def group_by_category(self):
        return self.values('category').annotate(count=models.Count('id'))
