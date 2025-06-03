from django.db import models

class Proveedor(models.Model):
    nombre = models.CharField(max_length=200)
    contacto = models.CharField(max_length=200, blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    direccion = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return self.nombre
    
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre
    
class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    numero_serie = models.CharField(max_length=100, unique=True)
    ubicacion = models.CharField(max_length=100)
    imagen_url = models.URLField(max_length=300, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=1)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    proveedores = models.ManyToManyField(Proveedor, blank=True)  
    precio_actual = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self):
        return f"{self.nombre} ({self.numero_serie})"

from django.conf import settings

TIPOS_MOVIMIENTO = [
    ('IN', 'Entrada'),
    ('OUT', 'Salida'),
]

class Movimiento(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=3, choices=TIPOS_MOVIMIENTO)
    cantidad = models.PositiveIntegerField()
    motivo = models.CharField(max_length=255, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Actualiza el stock automáticamente según el movimiento
        if self.tipo == 'IN':
            self.producto.stock += self.cantidad
        elif self.tipo == 'OUT':
            if self.cantidad > self.producto.stock:
                raise ValueError('No hay suficiente stock para realizar la salida.')
            self.producto.stock -= self.cantidad
        self.producto.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.producto.nombre} ({self.cantidad})"


class HistorialPrecio(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="historial_precios")
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.producto.nombre} - ${self.precio} ({self.fecha:%d/%m/%Y})"
