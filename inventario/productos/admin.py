from django.contrib import admin
from .models import Producto
from .models import Movimiento, Proveedor

admin.site.register(Producto)
admin.site.register(Movimiento)
admin.site.register(Proveedor)
