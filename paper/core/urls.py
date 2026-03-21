from django.urls import path
from . import views

urlpatterns = [
    # Público
    path('', views.home, name='home'),
    path('productos/<int:categoria_id>/', views.productos, name='productos'),
    path('producto/<int:producto_id>/', views.producto, name='producto'),
    path('buscar/', views.buscar, name='buscar'),

    # Carrito
    path('carrito/', views.ver_carrito, name='carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_carrito, name='agregar_carrito'),
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('carrito/editar/<int:producto_id>/', views.editar_carrito, name='editar_carrito'),
    path('carrito/descuento/', views.aplicar_descuento, name='aplicar_descuento'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),

    # Pedidos usuario
    path('checkout/', views.checkout, name='checkout'),
    path('pedido/<int:pedido_id>/confirmado/', views.pedido_confirmado, name='pedido_confirmado'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),

    # Panel admin propio
    path('panel/', views.admin_dashboard, name='admin_dashboard'),
    path('panel/productos/', views.admin_productos, name='admin_productos'),
    path('panel/productos/nuevo/', views.admin_producto_nuevo, name='admin_producto_nuevo'),
    path('panel/productos/<int:producto_id>/editar/', views.admin_producto_editar, name='admin_producto_editar'),
    path('panel/productos/<int:producto_id>/eliminar/', views.admin_producto_eliminar, name='admin_producto_eliminar'),
    path('panel/pedidos/', views.admin_pedidos, name='admin_pedidos'),
    path('panel/pedidos/<int:pedido_id>/estado/', views.admin_pedido_estado, name='admin_pedido_estado'),
]