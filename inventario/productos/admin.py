from django.contrib import admin
from .models import Producto
from .models import Movimiento, Proveedor, Categoria, Lote

admin.site.register(Producto)
admin.site.register(Movimiento)
admin.site.register(Proveedor)
admin.site.register(Categoria)
admin.site.register(Lote)
