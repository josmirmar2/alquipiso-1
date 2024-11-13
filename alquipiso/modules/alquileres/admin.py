from django.contrib import admin
from modules.alquileres.models import *

# Register your models here.

admin.site.register(Alojamiento)
admin.site.register(Cliente)
admin.site.register(Propietario)
admin.site.register(Reserva)