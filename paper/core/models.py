from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    codigo_barras = models.CharField(max_length=13)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    precio_oferta = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.IntegerField(validators=[MinValueValidator(0)])

    def precio_vigente(self):
        if self.precio_oferta and self.precio_oferta < self.precio:
            return self.precio_oferta
        return self.precio

    def clean(self):
        if self.precio is not None and self.precio_oferta is not None:
            if self.precio_oferta >= self.precio:
                raise ValidationError("El precio de oferta no puede ser mayor o igual al precio regular")

    def __str__(self):
        return self.nombre

class Descuento(models.Model):
    codigo = models.CharField(max_length=100, unique=True)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    activo = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.codigo} ({self.porcentaje}%)"

class Pedido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    descuento_aplicado = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    direccion = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"