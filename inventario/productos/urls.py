from django.urls import path
from .views import (
    lista_productos, registrar_movimiento, historial_movimientos,
    agregar_producto, editar_producto, eliminar_producto,
    lista_proveedores, agregar_proveedor, editar_proveedor, eliminar_proveedor,
    lista_categorias, agregar_categoria, editar_categoria, eliminar_categoria,
    lista_lotes, crear_lote, editar_lote, eliminar_lote
)

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
    path('categorias/', lista_categorias, name='lista_categorias'),
    path('categorias/agregar/', agregar_categoria, name='agregar_categoria'),
    path('categorias/editar/<int:pk>/', editar_categoria, name='editar_categoria'),
    path('categorias/eliminar/<int:pk>/', eliminar_categoria, name='eliminar_categoria'),
    path('lotes/', lista_lotes, name='lista_lotes'),
    path('lotes/crear/', crear_lote, name='crear_lote'),
    path('lotes/editar/<int:pk>/', editar_lote, name='editar_lote'),
    path('lotes/eliminar/<int:pk>/', eliminar_lote, name='eliminar_lote'),
]
