from django import forms
from .models import Movimiento, Producto, Proveedor, Categoria

class MovimientoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        fields = ['producto', 'tipo', 'cantidad', 'motivo']

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre',
            'descripcion',
            'numero_serie',
            'ubicacion',
            'categoria',        # Nuevo campo categoría
            'imagen_url',
            'stock_minimo',
            'proveedores',
            'precio_actual',    # Nuevo campo precio_actual
        ]
        widgets = {
            'proveedores': forms.CheckboxSelectMultiple,
            'categoria': forms.Select,   # Widget select para categoría (opcional, Django lo asigna por defecto)
        }

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'contacto', 'telefono', 'email', 'direccion']

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
