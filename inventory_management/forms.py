from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def clean_image(self):
        image = self.cleaned_data.get('image', False)
        if image:
            if image.size > 1024*1024:  # 1MB
                raise forms.ValidationError("Archivo de imagen demasiado grande (máximo 1 MB)")
            if image.height > 600 or image.width > 800:
                raise forms.ValidationError("Dimensiones de la imagen demasiado grandes (máximo 800x600 píxeles)")
            return image
        else:
            raise forms.ValidationError("No se pudo leer la imagen cargada")
