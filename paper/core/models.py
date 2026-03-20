from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
# Create your models here.

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    codigo_barras = models.CharField(max_length=13)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    # Allow blank=True so the field is optional in forms/admin
    # Allow null=True so the database column can store NULL
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    precio_oferta = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    stock = models.IntegerField(validators=[MinValueValidator(0)])

    def clean(self):
        if self.precio is not None and self.precio_oferta is not None:
            if self.precio_oferta >= self.precio:
                raise ValidationError("El precio de oferta no puede ser mayor o igual al precio regular")
    
    def __str__(self):
        return self.nombre

class Carrito(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"


class generador_codigos_descuentos(models.Model):
    codigo = models.CharField(max_length=100, unique=True)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    def __str__(self):
        return self.codigo

class Descuento(models.Model):
    codigo = models.CharField(max_length=100, unique=True)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    def __str__(self):
        return self.codigo