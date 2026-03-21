from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count
from .models import Categoria, Producto, Descuento, Pedido, DetallePedido
from django.contrib.auth.models import User
import json

def es_admin(user):
    return user.is_staff

def get_categorias():
    return Categoria.objects.all()

#publico

def home(request):
    productos_destacados = Producto.objects.order_by('-id')[:8]
    return render(request, 'usuario/inicio.html', {
        'categorias': get_categorias(),
        'productos_destacados': productos_destacados
    })

def productos(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    orden = request.GET.get('orden', '')
    lista = Producto.objects.filter(categoria=categoria)
    if orden == 'precio_asc':
        lista = lista.order_by('precio')
    elif orden == 'precio_desc':
        lista = lista.order_by('-precio')
    elif orden == 'nombre':
        lista = lista.order_by('nombre')
    return render(request, 'usuario/productos.html', {
        'categoria': categoria,
        'productos': lista,
        'categorias': get_categorias(),
        'orden': orden
    })

def producto(request, producto_id):
    prod = get_object_or_404(Producto, id=producto_id)
    relacionados = Producto.objects.filter(categoria=prod.categoria).exclude(id=prod.id)[:4]
    return render(request, 'usuario/producto.html', {
        'producto': prod,
        'categorias': get_categorias(),
        'categoria': prod.categoria,
        'relacionados': relacionados
    })

def buscar(request):
    query = request.GET.get('q', '').strip()
    productos = Producto.objects.filter(nombre__icontains=query) if query else []
    return render(request, 'usuario/productos.html', {
        'productos': productos,
        'categorias': get_categorias(),
        'categoria': None,
        'query': query
    })

# CARRITO

def agregar_carrito(request, producto_id):
    get_object_or_404(Producto, id=producto_id)
    carrito = request.session.get('carrito', {})
    if isinstance(carrito, list):
        carrito = {}
    pid = str(producto_id)
    carrito[pid] = carrito.get(pid, 0) + 1
    request.session['carrito'] = carrito
    request.session.modified = True
    messages.success(request, 'Producto agregado al carrito.')
    return redirect(request.META.get('HTTP_REFERER', 'carrito'))

def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    if isinstance(carrito, list):
        carrito = {}
        request.session['carrito'] = carrito

    ids = [int(pid) for pid in carrito.keys()]
    productos_db = Producto.objects.filter(id__in=ids)

    items = []
    subtotal = 0
    for p in productos_db:
        cantidad = carrito[str(p.id)]
        precio = p.precio_vigente()
        sub = precio * cantidad
        subtotal += sub
        items.append({'producto': p, 'cantidad': cantidad, 'subtotal': sub})

    descuento_pct = request.session.get('descuento_pct', 0)
    descuento_monto = subtotal * descuento_pct / 100
    total = subtotal - descuento_monto

    return render(request, 'usuario/carrito.html', {
        'carrito_items': items,
        'subtotal': subtotal,
        'descuento_pct': descuento_pct,
        'descuento_monto': descuento_monto,
        'total': total,
        'categorias': get_categorias()
    })

def eliminar_producto(request, producto_id):
    carrito = request.session.get('carrito', {})
    carrito.pop(str(producto_id), None)
    request.session['carrito'] = carrito
    return redirect('carrito')

def editar_carrito(request, producto_id):
    if request.method == 'POST':
        carrito = request.session.get('carrito', {})
        pid = str(producto_id)
        try:
            cantidad = int(request.POST.get('cantidad', 1))
            if cantidad > 0:
                carrito[pid] = cantidad
            else:
                carrito.pop(pid, None)
            request.session['carrito'] = carrito
        except ValueError:
            pass
    return redirect('carrito')

def aplicar_descuento(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip().upper()
        try:
            desc = Descuento.objects.get(codigo=codigo, activo=True)
            request.session['descuento_pct'] = float(desc.porcentaje)
            request.session['descuento_codigo'] = codigo
            messages.success(request, f'Descuento del {desc.porcentaje}% aplicado.')
        except Descuento.DoesNotExist:
            messages.error(request, 'Código de descuento inválido o expirado.')
    return redirect('carrito')

# autentificación

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get('next', 'home'))
        messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = AuthenticationForm()
    return render(request, 'usuario/login.html', {'form': form, 'categorias': get_categorias()})

def registro_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Bienvenido, {user.username}.')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'usuario/registro.html', {'form': form, 'categorias': get_categorias()})

def logout_view(request):
    logout(request)
    return redirect('home')

# CHECKOUT

@login_required
def checkout(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        return redirect('carrito')

    ids = [int(pid) for pid in carrito.keys()]
    productos_db = Producto.objects.filter(id__in=ids)

    items = []
    subtotal = 0
    for p in productos_db:
        cantidad = carrito[str(p.id)]
        precio = p.precio_vigente()
        sub = precio * cantidad
        subtotal += sub
        items.append({'producto': p, 'cantidad': cantidad, 'subtotal': sub, 'precio': precio})

    descuento_pct = request.session.get('descuento_pct', 0)
    descuento_monto = subtotal * descuento_pct / 100
    total = subtotal - descuento_monto

    if request.method == 'POST':
        direccion = request.POST.get('direccion', '').strip()
        if not direccion:
            messages.error(request, 'Ingresa una dirección de entrega.')
            return render(request, 'usuario/checkout.html', {
                'items': items, 'subtotal': subtotal,
                'descuento_pct': descuento_pct, 'descuento_monto': descuento_monto,
                'total': total, 'categorias': get_categorias()
            })

        pedido = Pedido.objects.create(
            usuario=request.user,
            total=total,
            descuento_aplicado=descuento_pct,
            direccion=direccion
        )
        for item in items:
            DetallePedido.objects.create(
                pedido=pedido,
                producto=item['producto'],
                cantidad=item['cantidad'],
                precio_unitario=item['precio']
            )
            # Descontar stock
            p = item['producto']
            p.stock = max(0, p.stock - item['cantidad'])
            p.save()

        # Limpiar sesión
        request.session['carrito'] = {}
        request.session.pop('descuento_pct', None)
        request.session.pop('descuento_codigo', None)
        messages.success(request, f'Pedido #{pedido.id} confirmado.')
        return redirect('pedido_confirmado', pedido_id=pedido.id)

    return render(request, 'usuario/checkout.html', {
        'items': items,
        'subtotal': subtotal,
        'descuento_pct': descuento_pct,
        'descuento_monto': descuento_monto,
        'total': total,
        'categorias': get_categorias()
    })

@login_required
def pedido_confirmado(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    return render(request, 'usuario/pedido_confirmado.html', {
        'pedido': pedido,
        'categorias': get_categorias()
    })

@login_required
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'usuario/mis_pedidos.html', {
        'pedidos': pedidos,
        'categorias': get_categorias()
    })

#  PANEL ADMIN PROPIO

@user_passes_test(es_admin)
def admin_dashboard(request):
    total_ventas = Pedido.objects.aggregate(total=Sum('total'))['total'] or 0
    total_pedidos = Pedido.objects.count()
    total_productos = Producto.objects.count()
    total_usuarios = User.objects.count()
    pedidos_recientes = Pedido.objects.order_by('-fecha')[:10]
    return render(request, 'admin_panel/dashboard.html', {
        'total_ventas': total_ventas,
        'total_pedidos': total_pedidos,
        'total_productos': total_productos,
        'total_usuarios': total_usuarios,
        'pedidos_recientes': pedidos_recientes,
        'categorias': get_categorias()
    })

@user_passes_test(es_admin)
def admin_productos(request):
    productos = Producto.objects.select_related('categoria').order_by('-id')
    return render(request, 'admin_panel/productos.html', {
        'productos': productos,
        'categorias': get_categorias()
    })

@user_passes_test(es_admin)
def admin_producto_nuevo(request):
    if request.method == 'POST':
        try:
            p = Producto(
                nombre=request.POST['nombre'],
                codigo_barras=request.POST['codigo_barras'],
                categoria_id=request.POST['categoria'],
                precio=request.POST['precio'],
                precio_oferta=request.POST['precio_oferta'],
                stock=request.POST['stock'],
            )
            if 'imagen' in request.FILES:
                p.imagen = request.FILES['imagen']
            p.full_clean()
            p.save()
            messages.success(request, 'Producto creado.')
            return redirect('admin_productos')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'admin_panel/producto_form.html', {
        'categorias': get_categorias(),
        'accion': 'Crear'
    })

@user_passes_test(es_admin)
def admin_producto_editar(request, producto_id):
    p = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        try:
            p.nombre = request.POST['nombre']
            p.codigo_barras = request.POST['codigo_barras']
            p.categoria_id = request.POST['categoria']
            p.precio = request.POST['precio']
            p.precio_oferta = request.POST['precio_oferta']
            p.stock = request.POST['stock']
            if 'imagen' in request.FILES:
                p.imagen = request.FILES['imagen']
            p.full_clean()
            p.save()
            messages.success(request, 'Producto actualizado.')
            return redirect('admin_productos')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'admin_panel/producto_form.html', {
        'producto': p,
        'categorias': get_categorias(),
        'accion': 'Editar'
    })

@user_passes_test(es_admin)
def admin_producto_eliminar(request, producto_id):
    p = get_object_or_404(Producto, id=producto_id)
    p.delete()
    messages.success(request, 'Producto eliminado.')
    return redirect('admin_productos')

@user_passes_test(es_admin)
def admin_pedidos(request):
    pedidos = Pedido.objects.select_related('usuario').order_by('-fecha')
    return render(request, 'admin_panel/pedidos.html', {
        'pedidos': pedidos,
        'categorias': get_categorias()
    })

@user_passes_test(es_admin)
def admin_pedido_estado(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id)
        pedido.estado = request.POST.get('estado', pedido.estado)
        pedido.save()
    return redirect('admin_pedidos')