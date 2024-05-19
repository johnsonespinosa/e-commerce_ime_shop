from django.db import models
from django.core.exceptions import ValidationError
from django_extensions.db.fields import AutoSlugField
from django.db.models import Sum
from mptt.models import MPTTModel, TreeForeignKey

# Modelo para categorías de productos, usando MPTTModel para estructura de árbol
class Category(MPTTModel):
    # Campo para el nombre de la categoría
    name = models.CharField(max_length=100, db_index=True)
    # Campo para la categoría principal, permite relaciones jerárquicas
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        # Define el orden de inserción por nombre
        order_insertion_by = ['name']

    class Meta:
        # Configura el nombre de la tabla en la base de datos
        db_table = "Categories"
        # Nombres humanos legibles para referirse a una sola categoría o varias categorías
        verbose_name = "categoría"
        verbose_name_plural = "categorías"

    # Método para obtener una representación en cadena del objeto
    def __str__(self):
        return self.name
    
# Modelo para proveedores
class Supplier(models.Model):
    # Nombre del proveedor
    name = models.CharField(max_length=255, unique=True, db_index=True, verbose_name="Nombre", help_text="Nombre del proveedor")
    # URL de la tienda en línea
    url = models.URLField(blank=True, null=True,
                          help_text="URL de la tienda online del proveedor")
    # tipo de proveedor
    supplier_type = models.CharField(max_length=100, blank=True, null=True,
                                     help_text="Tipo de proveedor (por ejemplo, mayorista, minorista)", verbose_name="Tipo")
    # Descripción del proveedor
    description = models.TextField(blank=True, null=True,
                                   help_text="Breve descripción del proveedor.")
    # Imagen del proveedor
    image = models.ImageField(upload_to='suppliers/', blank=True, null=True,
                              help_text="Imagen del proveedor")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Suppliers"
        verbose_name = "proveedor"
        verbose_name_plural = "proveedores"

# Modelo para productos
class Product(models.Model):
    # Campo para la categoría del producto
    category = models.ForeignKey(Category, on_delete=models.RESTRICT, related_name='products',
                                 help_text="Categoria del producto", db_index=True, verbose_name="Categoría")
    # Campo para el proveedor del producto
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, null=True, related_name='products',
                                 help_text="Proveedor del producto", db_index=True, verbose_name="Proveedor")
    # Campo para la descripción del producto
    description = models.TextField(help_text="Descripción del Producto", verbose_name="Descripción")
    # Campo para el precio de compra del producto
    purchase_price = models.DecimalField(default=0.00, max_digits=10, decimal_places=2,
                                         help_text="Precio de compra del producto", verbose_name="Precio de compra")
    # Campo para el precio de venta del producto
    sale_price = models.DecimalField(default=0.00, blank=True, max_digits=10, decimal_places=2,
                                     help_text="Precio de venta del producto", verbose_name="Precio de venta")
    # Campo para generar un slug único basado en el nombre del producto
    slug = AutoSlugField(populate_from='description', unique=True)
    # Campo para registrar la fecha de creación del producto
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    # Campo para almacenar la imagen del producto, con validador para limitar el tamaño del archivo
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    # Sobreescribe el método save para validar que el precio de venta sea mayor que el precio de compra
    def save(self, *args, **kwargs):
        if self.sale_price <= self.purchase_price:
            raise ValidationError("El precio de venta debe ser mayor que el precio de compra.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.description


    class Meta:
        # Define el orden de los productos por nombre y categoría
        ordering = ['registration_date', 'category']
        # Nombres humanos legibles para referirse a un producto
        verbose_name = 'producto'
        verbose_name_plural = 'productos'
        # Configura el nombre de la tabla en la base de datos
        db_table = "Products"

# Modelo para variaciones de productos
class Variation(models.Model):
    # Constantes para las categorías de variación
    VAR_CATEGORIES = [
        ('talla', 'Talla'),
        ('color', 'Color'),
    ]
    # Constantes para los estados de la variación
    STATE = [
        ('disponible', 'Disponible'),
        ('no disponible', 'No disponible'),
        ('eliminado', 'Eliminado'),
    ]
    # Campo para el producto asociado
    product = models.ForeignKey(Product, related_name='variations', on_delete=models.CASCADE)
    # Campo para la categoría de la variación
    category = models.CharField(max_length=120, choices=VAR_CATEGORIES, default='talla')
    # Campo para el nombre de la variación
    name = models.CharField(max_length=120, help_text="Nombre de la variación")
    # Campo para el estado de la variación
    state = models.CharField(max_length=120, choices=STATE, default='disponible')

    # Método para obtener una representación en cadena del objeto
    def __str__(self):
        return self.name

    class Meta:
        # Configura el nombre de la tabla en la base de datos
        db_table = "Variations"
        # Nombres humanos legibles para referirse a una variación
        verbose_name = "variación"
        verbose_name_plural = "variaciones"

# Modelo para el seguimiento del stock de productos
class Inventory(models.Model):
    # Campo para el producto asociado
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventories')
    # Campo para el stock actual del producto
    current_stock = models.PositiveIntegerField(default=0, help_text="Stock disponible del producto")
    # Campo para indicar si el producto está activo o no
    active = models.BooleanField(default=True, help_text="Indica si el producto está activo o no.")
    # Campo para registrar la última fecha de modificación del inventario
    modification_date = models.DateTimeField(auto_now=True)

    # Método para obtener una representación en cadena del objeto
    def __str__(self):
        return f"{self.product.name} - {self.current_stock}"

    class Meta:
        # Configura el nombre de la tabla en la base de datos
        db_table = "Inventories"
        # Nombres humanos legibles para referirse a un inventario
        verbose_name = "inventario"
        verbose_name_plural = "inventarios"

# Modelo para manejar problemas específicos con los productos
class ProductIssue(models.Model):
    # Constantes para los tipos de problemas
    PRODUCT_ISSUE_TYPES = [
        ('por defecto', 'Por defecto'),
        ('dañado', 'Dañado'),
    ]
    # Campo para el producto asociado
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='issue')
    # Campo para el tipo de problema
    issue_type = models.CharField(max_length=20, choices=PRODUCT_ISSUE_TYPES, default='por defecto')
    # Campo para notas adicionales sobre el problema
    notes = models.TextField(blank=True, null=True, help_text="Detalles adicionales sobre el problema")

    # Método para obtener una representación en cadena del objeto
    def __str__(self):
        return f"{self.product.name} - {self.issue_type}"

    class Meta:
        # Configura el nombre de la tabla en la base de datos
        db_table = "ProductIssues"
        # Nombres humanos legibles para referirse a una baja
        verbose_name = "baja"
        verbose_name_plural = "bajas"
