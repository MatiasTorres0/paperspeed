from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('productos/<int:categoria_id>/', views.productos, name='productos'),
    path('producto/<int:producto_id>/', views.producto, name='producto'),
    path('agregar_carrito/<int:producto_id>/', views.agregar_carrito, name='agregar_carrito'),
    path('carrito/', views.ver_carrito, name='carrito'),
    path('eliminar_producto/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('editar_carrito/<int:producto_id>/', views.editar_carrito, name='editar_carrito'),
    path('buscar/', views.buscar, name='buscar'),
]
