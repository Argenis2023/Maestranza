from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages

from .models import Categoria, Producto, Proveedor, Movimiento, HistorialPrecio
from .forms import MovimientoForm, ProductoForm, ProveedorForm

# -------- PRODUCTOS --------

def lista_productos(request):
    query = request.GET.get('q', '')
    productos = Producto.objects.all()
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(numero_serie__icontains=query) |
            Q(ubicacion__icontains=query) |
            Q(proveedores__nombre__icontains=query)
        ).distinct()
    productos_criticos = [p for p in productos if p.stock <= p.stock_minimo]
    return render(request, "productos/lista_productos.html", {
        "productos": productos,
        "productos_criticos": productos_criticos,
        "q": query,
    })

def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save(commit=False)
            nuevo_precio = form.cleaned_data.get('precio_actual', None)
            producto.save()
            form.save_m2m()  # Para proveedores, categoría, etc.

            # Guardar historial de precios si hay precio definido
            if nuevo_precio is not None:
                HistorialPrecio.objects.create(producto=producto, precio=nuevo_precio)
            messages.success(request, "Producto agregado correctamente.")
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'productos/agregar_producto.html', {'form': form})

def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            producto_edit = form.save(commit=False)
            nuevo_precio = form.cleaned_data.get('precio_actual', None)
            old_precio = producto.precio_actual
            producto_edit.save()
            form.save_m2m()

            # Guardar historial SOLO si el precio cambió
            if nuevo_precio is not None and old_precio != nuevo_precio:
                HistorialPrecio.objects.create(producto=producto_edit, precio=nuevo_precio)
            messages.success(request, "Producto editado correctamente.")
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/editar_producto.html', {'form': form, 'producto': producto})

def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, "Producto eliminado correctamente.")
        return redirect('lista_productos')
    return render(request, 'productos/eliminar_producto.html', {'producto': producto})

# -------- MOVIMIENTOS --------

def registrar_movimiento(request):
    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.usuario = request.user
            movimiento.save()
            return redirect('lista_productos')
    else:
        form = MovimientoForm()
    return render(request, 'productos/registrar_movimiento.html', {'form': form})

def historial_movimientos(request):
    movimientos = Movimiento.objects.select_related('producto', 'usuario').order_by('-fecha')
    return render(request, "productos/historial_movimientos.html", {"movimientos": movimientos})

# -------- PROVEEDORES --------

def lista_proveedores(request):
    proveedores = Proveedor.objects.all()
    return render(request, 'productos/lista_proveedores.html', {'proveedores': proveedores})

def agregar_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Proveedor agregado correctamente.")
            return redirect('lista_proveedores')
    else:
        form = ProveedorForm()
    return render(request, 'productos/agregar_proveedor.html', {'form': form})

def editar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, "Proveedor editado correctamente.")
            return redirect('lista_proveedores')
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'productos/editar_proveedor.html', {'form': form, 'proveedor': proveedor})

def eliminar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        proveedor.delete()
        messages.success(request, "Proveedor eliminado correctamente.")
        return redirect('lista_proveedores')
    return render(request, 'productos/eliminar_proveedor.html', {'proveedor': proveedor})

from django.core.mail import send_mail

def registrar_movimiento(request):
    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.usuario = request.user
            movimiento.save()

            producto = movimiento.producto
            # Verifica si el producto quedó en stock crítico
            if producto.stock <= producto.stock_minimo:
                send_mail(
                    'Alerta de stock crítico',
                    f'El producto "{producto.nombre}" está en stock crítico (stock: {producto.stock})',
                    'Maestrana Inventario',  # Remitente
                    ['maestranzainventario@gmail.com'],  # Cambia por tu correo real
                    fail_silently=False,
                )

            return redirect('lista_productos')
    else:
        form = MovimientoForm()
    return render(request, 'productos/registrar_movimiento.html', {'form': form})

from .forms import CategoriaForm

def lista_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'productos/lista_categorias.html', {'categorias': categorias})

def agregar_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría agregada correctamente.")
            return redirect('lista_categorias')
    else:
        form = CategoriaForm()
    return render(request, 'productos/agregar_categoria.html', {'form': form})

def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría editada correctamente.")
            return redirect('lista_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'productos/editar_categoria.html', {'form': form, 'categoria': categoria})

def eliminar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, "Categoría eliminada correctamente.")
        return redirect('lista_categorias')
    return render(request, 'productos/eliminar_categoria.html', {'categoria': categoria})
