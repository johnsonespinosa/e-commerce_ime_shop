from django.db import models
from django.db.models import Sum, F, Prefetch
from django.utils.translation import gettext_lazy as _

from inventory_management.models import Variation

class ProductManager(models.Manager):
    """
    Custom manager for the Product model to optimize database queries and provide additional functionality.
    """

    def get_all_products(self):
        """
        Retrieves all products along with their categories and associated variations.
        
        Returns:
            QuerySet: All products with optimized related data.
        """
        # Pre-fetching variations to avoid the N+1 query problem
        variants_prefetch = Prefetch(
            'variations',
            queryset=Variation.objects.select_related('product'),  # Ensures that the product relation is also prefetched
        )
        return self.select_related('category').prefetch_related(variants_prefetch)

    def get_products_with_stock(self):
        """
        Annotates each product with its total stock across all inventories.
        
        Returns:
            QuerySet: Products annotated with their total stock.
        """
        return self.annotate(stock=Sum('inventories__current_stock'))

    def get_products_by_variation(self, variation_id):
        """
        Filters products based on a given variation ID.
        
        Args:
            variation_id (int): The ID of the variation to filter by.
            
        Returns:
            QuerySet: Products filtered by the specified variation ID.
        """
        return self.prefetch_related(Prefetch('variations', queryset=Variation.objects.filter(id=variation_id)))

    def get_products_by_category(self, category_id):
        """
        Filters products based on a given category ID.
        
        Args:
            category_id (int): The ID of the category to filter by.
            
        Returns:
            QuerySet: Products filtered by the specified category ID.
        """
        return self.select_related('category').filter(category_id=category_id)

    def get_products_by_supplier(self, supplier_id):
        """
        Filters products based on a given supplier ID.
        
        Args:
            supplier_id (int): The ID of the supplier to filter by.
            
        Returns:
            QuerySet: Products filtered by the specified supplier ID.
        """
        return self.select_related('supplier').filter(supplier_id=supplier_id)

    def get_products_with_low_stock(self, threshold):
        """
        Filters products based on a low stock threshold.
        
        Args:
            threshold (int): The minimum stock level to filter by.
            
        Returns:
            QuerySet: Products with stock levels below the specified threshold.
        """
        return self.annotate(stock_count=Sum('inventories__current_stock')).filter(stock_count__lte=threshold)

    def get_products_in_price_range(self, min_price, max_price):
        """
        Filters products within a specified price range.
        
        Args:
            min_price (float): The minimum price to filter by.
            max_price (float): The maximum price to filter by.
            
        Returns:
            QuerySet: Products within the specified price range.
        """
        return self.filter(sale_price__range=(min_price, max_price))

    def sales_summary(self):
        """
        Provides a summary of total sales and gains across all products.
        
        Returns:
            dict: A dictionary containing total sales and gains.
        """
        total_sales = self.aggregate(total_sales=Sum(F('sale_price') * F('stock')))['total_sales'] or 0
        total_gains = self.aggregate(total_gains=Sum(F('sale_price') * F('stock') - F('purchase_price') * F('stock')))['total_gains'] or 0
        return {'total_sales': total_sales, 'total_gains': total_gains}
