from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.core.exceptions import ValidationError

# Create your models here.

class Alojamiento(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.FloatField()
    imagen = models.ImageField(upload_to='', null=True, blank=True)
    propietario = models.ForeignKey('Propietario', on_delete=models.CASCADE, related_name='alojamientos')
    activo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.imagen:
            # Redimensionar imagen
            img_path = self.imagen.path
            img = Image.open(img_path)

            # Aplicar redimensionamiento
            max_size = (800, 600)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)  # Cambiado de Image.ANTIALIAS

            # Sobrescribir la imagen
            img.save(img_path)
    
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

    def calcular_precio_total(self):
        # Calcular la duración de la estancia (en días)
        if self.fecha_entrada and self.fecha_salida:
            duracion = (self.fecha_salida - self.fecha_entrada).days
            if duracion > 0:
                return duracion * self.alojamiento.precio
        return 0

    def clean(self):
        # Validación para asegurarse de que la fecha de salida sea después de la fecha de entrada
        if self.fecha_salida < self.fecha_entrada:
            raise ValidationError('La fecha de salida no puede ser anterior a la fecha de entrada.')


    def __str__(self):
        return f"Reserva de {self.cliente.user.username} para {self.alojamiento.nombre}"
    
class Notificacion(models.Model):
    recipiente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    mensaje = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.recipiente.username}: {self.mensaje}"