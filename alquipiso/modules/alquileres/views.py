from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import AlojamientoForm, UserRegistrationForm
from .models import Cliente, Propietario
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from modules.alquileres.models import *

# Create your views here.

def index(request):
    return render(request, 'index.html', {'welcome_text': 'Welcome to AlquiPiso!'})

def list_alojamientos(request):
    alojamientos = Alojamiento.objects.all()
    return render(request, 'list_alojamientos.html', {'alojamientos': alojamientos})

def show_alojamiento(request, alojamiento_id):
    alojamiento = get_object_or_404(Alojamiento, pk=alojamiento_id)
    return render(request, 'show_alojamiento.html', {'alojamiento': alojamiento})

def list_alojamientos_propietario(request, propietario_id):
    if not hasattr(request.user, 'propietario'):
        return redirect('index')
    try:
        propietario = Propietario.objects.get(id=propietario_id)
        alojamientos = Alojamiento.objects.filter(propietario=propietario)
    except Propietario.DoesNotExist:
        alojamientos = []
    return render(request, 'list_alojamientos.html', {'alojamientos': alojamientos})

def list_propietarios(request):
    propietarios = Propietario.objects.all()
    return render(request, 'propietarios.html', {'propietarios': propietarios})

def show_propietario(request, propietario_id):
    propietario = Propietario.objects.get(pk=propietario_id)
    return render(request, 'propietario.html', {'propietario': propietario})

def list_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'list_clientes.html', {'clientes': clientes})

def show_cliente(request, cliente_id):
    cliente = Cliente.objects.get(pk=cliente_id)
    return render(request, 'show_cliente.html', {'cliente': cliente})

def list_reservas(request):
    reservas = Reserva.objects.all()
    return render(request, 'list_reservas.html', {'reservas': reservas})

def show_reserva(request, reserva_id):
    reserva = Reserva.objects.get(pk=reserva_id)
    return render(request, 'show_reserva.html', {'reserva': reserva})

def list_reservas_cliente(request, cliente_id):
    cliente = Cliente.objects.get(pk=cliente_id)
    reservas = Reserva.objects.filter(cliente=cliente)
    return render(request, 'list_reservas.html', {'reservas': reservas})

def list_reservas_alojamiento(request, alojamiento_id):
    alojamiento = Alojamiento.objects.get(pk=alojamiento_id)
    reservas = Reserva.objects.filter(alojamiento=alojamiento)
    return render(request, 'list_reservas.html', {'reservas': reservas})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Obtener datos del formulario
            email = form.cleaned_data['email']
            nombre = form.cleaned_data['nombre']
            apellido = form.cleaned_data['apellido']
            telefono = form.cleaned_data['telefono']
            password = form.cleaned_data['password']
            role = form.cleaned_data['role']
            
            # Verificar si el correo ya está registrado
            if User.objects.filter(email=email).exists():
                messages.error(request, 'El correo electrónico ya está registrado.')
                return redirect('alquileres:register')

            # Crear un usuario base
            user = User.objects.create_user(username=email, email=email, password=password)
            user.first_name = nombre
            user.last_name = apellido
            user.save()
            
            # Crear el cliente o propietario según la elección
            if role == UserRegistrationForm.CLIENTE:
                cliente = Cliente.objects.create(user=user, telefono=telefono)
            elif role == UserRegistrationForm.PROPIETARIO:
                propietario = Propietario.objects.create(user=user, telefono=telefono)

            # Iniciar sesión automáticamente
            login(request, user)
            
            # Redirigir a la página de inicio o a donde quieras
            return redirect('index')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Log the user in
            login(request, user)  # Correct way to call login
            return redirect('alquileres:index')  # Redirect to the home page or desired page
        else:
            # Show error message if authentication fails
            messages.error(request, 'Invalid login credentials.')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('alquileres:index') # Redirect to the home page or desired page

@login_required
def create_alojamiento(request):
    # Verificar que el usuario autenticado sea un propietario
    if not hasattr(request.user, 'propietario'):
        return redirect('index')  # O redirige a la página que prefieras si el usuario no es propietario

    if request.method == 'POST':
        form = AlojamientoForm(request.POST, request.FILES)
        if form.is_valid():
            alojamiento = form.save(commit=False)
            # Asignar el propietario actual al alojamiento
            alojamiento.propietario = request.user.propietario
            alojamiento.save()
            return redirect('alquileres:list_alojamientos_propietario', propietario_id=request.user.propietario.id )  # Redirigir a la página de propiedades del propietario
    else:
        form = AlojamientoForm()

    return render(request, 'create_alojamiento.html', {'form': form})