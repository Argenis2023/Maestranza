from django.urls import path
from .views import lista_productos
from .views import registrar_movimiento
from .views import historial_movimientos
from .views import agregar_producto, editar_producto
from .views import eliminar_producto
from .views import lista_proveedores
from .views import agregar_proveedor, editar_proveedor, eliminar_proveedor


urlpatterns = [
    path('', lista_productos, name='lista_productos'),
    path('movimiento/', registrar_movimiento, name='registrar_movimiento'),
    path('historial/', historial_movimientos, name='historial_movimientos'),
    path('agregar/', agregar_producto, name='agregar_producto'),
    path('editar/<int:pk>/', editar_producto, name='editar_producto'),
    path('eliminar/<int:pk>/', eliminar_producto, name='eliminar_producto'),
    path('proveedores/', lista_proveedores, name='lista_proveedores'),
    path('proveedores/agregar/', agregar_proveedor, name='agregar_proveedor'),
    path('proveedores/editar/<int:pk>/', editar_proveedor, name='editar_proveedor'),
    path('proveedores/eliminar/<int:pk>/', eliminar_proveedor, name='eliminar_proveedor'),

]
