from django import forms
from .models import *
from django.forms import DateInput
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

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
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_entrada = cleaned_data.get('fecha_entrada')
        fecha_salida = cleaned_data.get('fecha_salida')

        if not fecha_entrada or not fecha_salida:
            raise ValidationError("Ambas fechas son obligatorias.")

        if fecha_entrada >= fecha_salida:
            raise ValidationError("La fecha de entrada debe ser anterior a la fecha de salida.")

        alojamiento = self.instance.alojamiento
        if not alojamiento:
            raise ValidationError("El alojamiento no está definido.")

        # Consultar reservas existentes para el alojamiento
        reservas_existentes = Reserva.objects.filter(alojamiento=alojamiento)

        for reserva in reservas_existentes:
            # Caso 1: Fecha de salida cae durante una reserva existente
            if fecha_salida > reserva.fecha_entrada and fecha_salida <= reserva.fecha_salida:
                raise ValidationError(
                    f"Las fecha de salida seleccionada ({fecha_salida}) cae dentro de una reserva existente: "
                    f"{reserva.fecha_entrada} a {reserva.fecha_salida}."
                )

            # Caso 2: Fecha de entrada cae durante una reserva existente
            if fecha_entrada >= reserva.fecha_entrada and fecha_entrada < reserva.fecha_salida:
                raise ValidationError(
                    f"La fecha de entrada seleccionada ({fecha_entrada}) cae dentro de una reserva existente: "
                    f"{reserva.fecha_entrada} a {reserva.fecha_salida}."
                )

            # Caso 3: Ambas fechas están contenidas dentro de una reserva existente
            if fecha_entrada >= reserva.fecha_entrada and fecha_salida <= reserva.fecha_salida:
                raise ValidationError(
                    f"El rango de fechas seleccionadas ({fecha_entrada} a {fecha_salida}) "
                    f"está completamente contenido dentro de una reserva existente: "
                    f"{reserva.fecha_entrada} a {reserva.fecha_salida}."
                )

            # Caso 4: Reserva existente contenida dentro de las fechas seleccionadas
            if fecha_entrada <= reserva.fecha_entrada and fecha_salida >= reserva.fecha_salida:
                raise ValidationError(
                    f"Una reserva existente ({reserva.fecha_entrada} a {reserva.fecha_salida}) "
                    f"está completamente contenida dentro del rango seleccionado."
                )

        return cleaned_data


class UserEditForm(forms.ModelForm):
    current_password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label='Contraseña actual'
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label='Nueva contraseña'
    )
    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label='Confirmar nueva contraseña'
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')  # Pasamos el usuario actual para validar la contraseña
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get('current_password')
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')

        # Validar si el usuario desea cambiar su contraseña
        if current_password or new_password or confirm_new_password:
            # Asegurarse de que se proporcionaron todos los campos de contraseña
            if not current_password:
                raise forms.ValidationError('Debes proporcionar tu contraseña actual.')
            if not new_password:
                raise forms.ValidationError('Debes proporcionar una nueva contraseña.')
            if not confirm_new_password:
                raise forms.ValidationError('Debes confirmar tu nueva contraseña.')

            # Verificar que la contraseña actual sea correcta
            if not check_password(current_password, self.user.password):
                raise forms.ValidationError('La contraseña actual no es correcta.')

            # Asegurarse de que las nuevas contraseñas coincidan
            if new_password != confirm_new_password:
                raise forms.ValidationError('Las nuevas contraseñas no coinciden.')

        return cleaned_data

    def save(self, commit=True):
        # Guardar los cambios del usuario
        user = super().save(commit=False)

        # Cambiar la contraseña si se proporciona una nueva
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)

        if commit:
            user.save()
        return user
