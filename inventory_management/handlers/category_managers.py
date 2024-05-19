from django.db import models


class CategoryManager(models.Manager):
    def get_categories_by_level(self, level):
        return self.filter(level=level)

    def filter_by_name(self, name):
        return self.filter(name__icontains=name)

    def move_category(self, old_parent, new_parent, category):
        if old_parent!= new_parent:
            category.parent = new_parent
            category.save()
