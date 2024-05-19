from django.contrib import admin
from django.db.models import Prefetch

from inventory_management.models import Product
from .forms import PurchaseItemFormSet, PurchaseForm, PurchaseItemForm
from .models import Purchase, PurchaseItem


# Inline para PurchaseItem que utiliza el formset personalizado
class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    formset = PurchaseItemFormSet
    extra = 1


# Configuración del panel de administración para Purchase
@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    form = PurchaseForm
    readonly_fields = ('purchase_date', 'total')  # Campos de solo lectura
    inlines = [PurchaseItemInline]
    list_display = ('supplier', 'total', 'state', 'purchase_date', 'delivery_date')
    list_filter = ('supplier', 'state')
    search_fields = ('supplier__name',)

    def get_queryset(self, request):
        # Optimización de consultas utilizando select_related
        return super().get_queryset(request).select_related('supplier')


# Configuración del panel de administración para PurchaseItem
@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    form = PurchaseItemForm
    list_display = ('purchase', 'product', 'quantity', 'subtotal')
    list_filter = ('purchase__supplier', 'product')

    def get_queryset(self, request):
        # Optimización de consultas utilizando prefetch_related
        return super().get_queryset(request).prefetch_related(
            Prefetch('product', queryset=Product.objects.select_related('category'))
        )
