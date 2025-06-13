from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from datetime import date, timedelta

from .models import Categoria, Producto, Proveedor, Movimiento, HistorialPrecio, Lote
from .forms import MovimientoForm, ProductoForm, ProveedorForm, LoteForm, CategoriaForm
from django.core.mail import send_mail

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django import forms

from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.utils import timezone
from datetime import timedelta

# -------- PRODUCTOS --------

@login_required
@permission_required('productos.view_producto', raise_exception=True)
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

@login_required
@permission_required('productos.add_producto', raise_exception=True)
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

@login_required
@permission_required('productos.change_producto', raise_exception=True)
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

@login_required
@permission_required('productos.delete_producto', raise_exception=True)
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, "Producto eliminado correctamente.")
        return redirect('lista_productos')
    return render(request, 'productos/eliminar_producto.html', {'producto': producto})

# -------- MOVIMIENTOS --------

@login_required
@permission_required('productos.add_movimiento', raise_exception=True)
def registrar_movimiento(request):
    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.usuario = request.user

            try:
                if movimiento.tipo == 'OUT':
                    lote = form.cleaned_data['lote']
                    if lote and movimiento.cantidad > lote.cantidad:
                        form.add_error('cantidad', f'Solo hay {lote.cantidad} unidades en el lote seleccionado.')
                        return render(request, 'productos/registrar_movimiento.html', {'form': form})

                    if lote:
                        lote.cantidad -= movimiento.cantidad
                        lote.save()

                elif movimiento.tipo == 'IN':
                    pass

                movimiento.save()

                producto = movimiento.producto
                if producto.stock <= producto.stock_minimo:
                    send_mail(
                        'Alerta de stock crítico',
                        f'El producto "{producto.nombre}" está en stock crítico (stock: {producto.stock})',
                        'Maestrana Inventario',
                        ['maestranzainventario@gmail.com', 'fide.rodriguez@duocuc.cl'],
                        fail_silently=False,
                    )

                messages.success(request, "Movimiento registrado correctamente.")
                return redirect('lista_productos')
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = MovimientoForm()
    return render(request, 'productos/registrar_movimiento.html', {'form': form})

@login_required
@permission_required('productos.view_movimiento', raise_exception=True)
def historial_movimientos(request):
    movimientos = Movimiento.objects.select_related('producto', 'usuario').order_by('-fecha')
    return render(request, "productos/historial_movimientos.html", {"movimientos": movimientos})

# -------- PROVEEDORES --------

@login_required
@permission_required('productos.view_proveedor', raise_exception=True)
def lista_proveedores(request):
    proveedores = Proveedor.objects.all()
    return render(request, 'productos/lista_proveedores.html', {'proveedores': proveedores})

@login_required
@permission_required('productos.add_proveedor', raise_exception=True)
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

@login_required
@permission_required('productos.change_proveedor', raise_exception=True)
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

@login_required
@permission_required('productos.delete_proveedor', raise_exception=True)
def eliminar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        proveedor.delete()
        messages.success(request, "Proveedor eliminado correctamente.")
        return redirect('lista_proveedores')
    return render(request, 'productos/eliminar_proveedor.html', {'proveedor': proveedor})

# -------- LOTES --------

@login_required
@permission_required('productos.add_lote', raise_exception=True)
def crear_lote(request):
    producto_id = request.GET.get('producto')
    initial = {}
    if producto_id:
        initial['producto'] = producto_id
    if request.method == 'POST':
        form = LoteForm(request.POST, initial=initial)
        if form.is_valid():
            form.save()
            messages.success(request, "Lote agregado correctamente.")
            return redirect('lista_lotes')
    else:
        form = LoteForm(initial=initial)
    return render(request, 'productos/crear_lote.html', {'form': form})

@login_required
@permission_required('productos.view_lote', raise_exception=True)
def lista_lotes(request):
    hoy = date.today()
    proximos = hoy + timedelta(days=30)
    lotes_vencidos = Lote.objects.filter(fecha_vencimiento__lt=hoy)
    lotes_proximos = Lote.objects.filter(fecha_vencimiento__range=[hoy, proximos])
    lotes_ok = Lote.objects.filter(fecha_vencimiento__gt=proximos)
    return render(request, 'productos/lista_lotes.html', {
        'lotes_vencidos': lotes_vencidos,
        'lotes_proximos': lotes_proximos,
        'lotes_ok': lotes_ok,
    })

@login_required
@permission_required('productos.change_lote', raise_exception=True)
def editar_lote(request, pk):
    lote = get_object_or_404(Lote, pk=pk)
    if request.method == 'POST':
        form = LoteForm(request.POST, instance=lote)
        if form.is_valid():
            form.save()
            return redirect('lista_lotes')
    else:
        form = LoteForm(instance=lote)
    return render(request, 'productos/editar_lote.html', {'form': form, 'lote': lote})

@login_required
@permission_required('productos.delete_lote', raise_exception=True)
def eliminar_lote(request, pk):
    lote = get_object_or_404(Lote, pk=pk)
    if request.method == 'POST':
        lote.delete()
        return redirect('lista_lotes')
    return render(request, 'productos/eliminar_lote.html', {'lote': lote})

# -------- CATEGORIAS --------

@login_required
@permission_required('productos.view_categoria', raise_exception=True)
def lista_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'productos/lista_categorias.html', {'categorias': categorias})

@login_required
@permission_required('productos.add_categoria', raise_exception=True)
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

@login_required
@permission_required('productos.change_categoria', raise_exception=True)
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

@login_required
@permission_required('productos.delete_categoria', raise_exception=True)
def eliminar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, "Categoría eliminada correctamente.")
        return redirect('lista_categorias')
    return render(request, 'productos/eliminar_categoria.html', {'categoria': categoria})

# -------- GESTIÓN DE USUARIOS --------

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label='Grupo')

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'group']

    def save(self, commit=True):
        user = super().save(commit=False)
        pwd = self.cleaned_data["password"]
        if pwd:
            user.set_password(pwd)
        if commit:
            user.save()
            user.groups.clear()
            user.groups.add(self.cleaned_data["group"])
        return user

@login_required
def gestionar_usuarios(request):
    usuarios = User.objects.all().order_by('username')
    grupos = Group.objects.all()
    if request.method == 'POST':
        # Crear o editar usuario
        if 'save_user' in request.POST:
            if request.POST.get('user_id'):
                usuario = get_object_or_404(User, pk=request.POST['user_id'])
                form = UserForm(request.POST, instance=usuario)
            else:
                form = UserForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Usuario guardado correctamente.')
                return redirect('usuarios')  # IMPORTANTE: nombre de la url en urls.py
            else:
                messages.error(request, 'Corrige los errores.')
        # Eliminar usuario
        elif 'delete_user' in request.POST:
            usuario = get_object_or_404(User, pk=request.POST['delete_user'])
            if usuario.is_superuser:
                messages.error(request, 'No puedes eliminar al superusuario.')
            else:
                usuario.delete()
                messages.success(request, 'Usuario eliminado.')
            return redirect('usuarios')
    else:
        form = UserForm()

    return render(request, 'usuarios/usuarios.html', {
        'usuarios': usuarios,
        'grupos': grupos,
        'form': form,
    })

@login_required
@permission_required('productos.view_producto', raise_exception=True)
def exportar_inventario_pdf(request):
    productos = Producto.objects.all().order_by('nombre')
    now = timezone.now()
    from .models import Lote
    proximos = now.date() + timedelta(days=30)
    lotes_proximos_queryset = Lote.objects.filter(fecha_vencimiento__range=[now.date(), proximos])

    # Crea una lista con los días para vencer calculados
    lotes_proximos = []
    for lote in lotes_proximos_queryset:
        dias_para_vencer = (lote.fecha_vencimiento - now.date()).days
        lotes_proximos.append({
            'producto': lote.producto,
            'numero_lote': lote.numero_lote,
            'fecha_vencimiento': lote.fecha_vencimiento,
            'cantidad': lote.cantidad,
            'proveedor': lote.proveedor,
            'dias_para_vencer': dias_para_vencer,
        })

    html_string = render_to_string('productos/reporte_inventario_pdf.html', {
        'productos': productos,
        'lotes_proximos': lotes_proximos,
        'usuario': request.user,
        'now': now,
    })
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_inventario.pdf"'
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    return response