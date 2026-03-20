from django.shortcuts import render
from .models import Categoria, Producto

# Create your views here.
def home(request):
    categorias = Categoria.objects.all()
    return render(request, 'usuario/inicio.html', {'categorias': categorias})

def productos(request, categoria_id):
    categoria = Categoria.objects.get(id=categoria_id)
    productos = Producto.objects.filter(categoria=categoria)
    return render(request, 'usuario/productos.html', {'categoria': categoria, 'productos': productos})

def producto(request, producto_id):
    producto = Producto.objects.get(id=producto_id)
    categorias = Categoria.objects.all()
    categoria = Categoria.objects.get(id=producto.categoria.id)
    return render(request, 'usuario/producto.html', {'producto': producto, 'categorias': categorias, 'categoria': categoria})
