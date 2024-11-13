from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Alojamiento(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.FloatField()
    imagen = models.ImageField(upload_to='media', null=True, blank=True)
    propietario = models.ForeignKey('Propietario', on_delete=models.CASCADE, related_name='alojamientos')
    
class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=1)
    telefono = models.CharField(max_length=100)

class Propietario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=1)
    telefono = models.CharField(max_length=100)

class Reserva(models.Model):
    id = models.AutoField(primary_key=True)
    alojamiento = models.ForeignKey(Alojamiento, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_entrada = models.DateField()
    fecha_salida = models.DateField()
    fecha_reserva = models.DateField()
    precio_total = models.FloatField()
    pagado = models.BooleanField()

    def __str__(self):
        return f"Reserva de {self.cliente.user.username} para {self.alojamiento.nombre}"
    