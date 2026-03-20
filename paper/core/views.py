from django.shortcuts import render, redirect
from .models import Categoria, Producto

# Create your views here.
def home(request):
    categorias = Categoria.objects.all()
    productos_destacados = Producto.objects.order_by('-id')[:8]
    return render(request, 'usuario/inicio.html', {
        'categorias': categorias,
        'productos_destacados': productos_destacados
    })

def productos(request, categoria_id):
    categoria = Categoria.objects.get(id=categoria_id)
    productos = Producto.objects.filter(categoria=categoria)
    return render(request, 'usuario/productos.html', {'categoria': categoria, 'productos': productos})

def producto(request, producto_id):
    producto = Producto.objects.get(id=producto_id)
    categorias = Categoria.objects.all()
    categoria = Categoria.objects.get(id=producto.categoria.id)
    return render(request, 'usuario/producto.html', {'producto': producto, 'categorias': categorias, 'categoria': categoria})

def agregar_carrito(request, producto_id):
    producto = Producto.objects.get(id=producto_id)
    carrito = request.session.get('carrito', {})
    
    # Check if carrito is actually a list from old session data
    if isinstance(carrito, list):
        carrito = {}
        request.session['carrito'] = carrito
    
    # Store quantity as value, product id as key
    producto_id_str = str(producto_id)
    if producto_id_str in carrito:
        carrito[producto_id_str] += 1
    else:
        carrito[producto_id_str] = 1
        
    request.session['carrito'] = carrito
    request.session.modified = True
    return redirect('carrito')

def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    
    # If the user has an old session where carrito is a list, reset it to an empty dict
    if isinstance(carrito, list):
        carrito = {}
        request.session['carrito'] = carrito
        request.session.modified = True
    
    # Get all products in cart
    producto_ids = [int(pid) for pid in carrito.keys()]
    productos_en_carrito = Producto.objects.filter(id__in=producto_ids)
    
    # Calculate quantities
    carrito_items = []
    total = 0
    for producto in productos_en_carrito:
        cantidad = carrito[str(producto.id)]
        precio_actual = producto.precio_oferta if producto.precio_oferta and producto.precio_oferta < producto.precio else producto.precio
        subtotal = precio_actual * cantidad
        total += subtotal
        carrito_items.append({
            'producto': producto,
            'cantidad': cantidad,
            'subtotal': subtotal
        })
        
    categorias = Categoria.objects.all()
    return render(request, 'usuario/carrito.html', {
        'carrito_items': carrito_items,
        'total': total,
        'categorias': categorias
    })

def eliminar_producto(request, producto_id):
    carrito = request.session.get('carrito', {})
    producto_id_str = str(producto_id)
    if producto_id_str in carrito:
        del carrito[producto_id_str]
        request.session['carrito'] = carrito
    return redirect('carrito')

def editar_carrito(request, producto_id):
    if request.method == 'POST':
        carrito = request.session.get('carrito', {})
        producto_id_str = str(producto_id)
        if producto_id_str in carrito:
            try:
                nueva_cantidad = int(request.POST.get('cantidad', 1))
                if nueva_cantidad > 0:
                    carrito[producto_id_str] = nueva_cantidad
                else:
                    del carrito[producto_id_str]
                request.session['carrito'] = carrito
            except ValueError:
                pass
    return redirect('carrito')

def buscar(request):
    query = request.GET.get('q', '')
    categorias = Categoria.objects.all()
    productos = Producto.objects.filter(nombre__icontains=query) if query else []
    return render(request, 'usuario/productos.html', {
        'productos': productos,
        'categoria': None,
        'categorias': categorias,
        'query': query
    })