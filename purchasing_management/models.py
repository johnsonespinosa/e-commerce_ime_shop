from django.db import models

from inventory_management.models import Product, Supplier


class Purchase(models.Model):
    STATE = [
        ('cancelada', 'Cancelada'),
        ('finalizada', 'Finalizada'),
        ('pendiente', 'Pendiente')
    ]
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchases')
    tax = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    state = models.CharField(max_length=120, choices=STATE, default='finalizada')
    purchase_date = models.DateTimeField(auto_now_add=True, help_text="Fecha de compra")
    delivery_date = models.DateField(null=True, blank=True, help_text="Fecha de entrega")

    @property
    def total(self):
        # Calcula el total de la compra sumando los subtotales de todos los artículos.
        return sum(item.subtotal for item in self.items.all()) + self.tax

    def __str__(self):
        # Representación de cadena del objeto Compra.
        return f"{self.state} - {self.total}"

    class Meta:
        verbose_name = 'compra'
        verbose_name_plural = 'compras'
        db_table = "Purchases"


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchase_items')
    quantity = models.PositiveIntegerField(default=1, help_text='Cantidad de productos')

    @property
    def subtotal(self):
        # Calcula el subtotal de la compra.
        return self.product.purchase_price * self.quantity

    def __str__(self):
        # Representación de cadena del objeto Artículo de compra.
        return f"{self.purchase.purchase_date} - {self.product.name} - {self.quantity}"

    class Meta:
        verbose_name = 'detalle'
        verbose_name_plural = 'detalles'
        db_table = "PurchaseItems"
