from django import forms
from .models import *
from django.forms import DateInput

class UserRegistrationForm(forms.Form):
    email = forms.EmailField()
    nombre = forms.CharField(max_length=100)
    apellido = forms.CharField(max_length=100)
    telefono = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    
    CLIENTE = 'cliente'
    PROPIETARIO = 'propietario'
    ROLE_CHOICES = [
        (CLIENTE, 'Cliente'),
        (PROPIETARIO, 'Propietario'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password != confirm_password:
            raise forms.ValidationError('Las contraseñas no coinciden.')

        return cleaned_data
    

class AlojamientoForm(forms.ModelForm):
    class Meta:
        model = Alojamiento
        fields = ['nombre', 'direccion', 'ciudad', 'descripcion', 'precio', 'imagen']


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['fecha_entrada', 'fecha_salida', 'pagado']
        widgets = {
            'fecha_entrada': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'fecha_entrada'}),
            'fecha_salida': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'fecha_salida'}),
        }
    
    precio_total = forms.FloatField(required=False, disabled=True, label="Precio Total")

    def calcular_precio_total(self):
        # Obtener los datos del formulario
        fecha_entrada = self.cleaned_data.get('fecha_entrada')
        fecha_salida = self.cleaned_data.get('fecha_salida')
        alojamiento = self.instance.alojamiento
        
        if fecha_entrada and fecha_salida:
            # Calcular la duración de la estancia (en días)
            duracion = (fecha_salida - fecha_entrada).days
            if duracion > 0:
                # Calcular el precio total
                precio_total = duracion * alojamiento.precio
                return precio_total
        return 0