from django import forms
from .models import *

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
        fields = ['nombre', 'direccion', 'descripcion', 'precio', 'imagen']
