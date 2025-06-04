from django import forms
from .models import Movimiento, Producto, Proveedor, Categoria, Lote

class MovimientoForm(forms.ModelForm):
    lote = forms.ModelChoiceField(
        queryset=Lote.objects.none(), 
        required=False, 
        label="Lote (solo para salidas)"
    )

    class Meta:
        model = Movimiento
        fields = ['producto', 'tipo', 'cantidad', 'motivo', 'lote']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si hay datos del POST, filtra lotes por producto seleccionado
        if 'producto' in self.data:
            try:
                producto_id = int(self.data.get('producto'))
                self.fields['lote'].queryset = Lote.objects.filter(producto_id=producto_id, cantidad__gt=0).order_by('fecha_vencimiento')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['lote'].queryset = Lote.objects.filter(producto=self.instance.producto, cantidad__gt=0).order_by('fecha_vencimiento')
        else:
            self.fields['lote'].queryset = Lote.objects.none()

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre',
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

class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = ['producto', 'numero_lote', 'cantidad', 'fecha_vencimiento', 'proveedor']
        widgets = {
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
        }

class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = '__all__'
        widgets = {
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'})
        }
