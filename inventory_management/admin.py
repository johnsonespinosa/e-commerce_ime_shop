from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.contrib import messages
from.models import Category, Product, Supplier, Variation, Inventory, ProductIssue


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        
class ProductResource(resources.ModelResource):
    class Meta:
        model = Product


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    resource_class = CategoryResource
    list_display = ('name', 'parent')
    search_fields = ('name',)
    list_per_page = 5
    
class VariationInline(admin.StackedInline):
    model = Variation
    extra = 6
    
# Clase ModelAdmin personalizada para el modelo Supplier
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'supplier_type', 'description')
    fields = ('name', 'url', 'supplier_type', 'description', 'image')

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    inlines = [VariationInline]
    resource_class = ProductResource
    list_display = ('category', 'supplier', 'description', 'purchase_price', 'sale_price', 'registration_date', 'stock')
    search_fields = ('category__name', 'supplier__name', 'description')
    list_filter = ('category', 'supplier')
    readonly_fields = ('slug',)
    
    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['messages'] = messages
        return super().add_view(request, form_url=form_url, extra_context=extra_context)
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        
        # Ejemplo de filtro por rango de precios
        min_price = request.GET.get('min_price', None)
        max_price = request.GET.get('max_price', None)
        if min_price and max_price:
            queryset = queryset.filter(purchase_price__range=(min_price, max_price))
        
        return queryset
    
    def stock(self, obj):
        # Obtener el stock del producto a través de su relación con Inventory
        inventory = Inventory.objects.filter(product=obj).first()  # Asume que solo hay un inventario por producto
        return inventory.current_stock if inventory else 0
    stock.short_description = 'Stock'  # Nombre corto para la columna

@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'category', 'state')
    search_fields = ('product__name', 'category', 'state')

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'current_stock', 'active', 'modification_date')
    search_fields = ('product__name', 'current_stock', 'active')

@admin.register(ProductIssue)
class ProductIssueAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'issue_type', 'notes')
    search_fields = ('product__name', 'issue_type', 'notes')
