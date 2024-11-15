from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import AlojamientoForm, UserRegistrationForm, ReservaForm
from .models import Cliente, Propietario
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from modules.alquileres.models import *

# Create your views here.

def index(request):
    alojamientos = Alojamiento.objects.all()  # Obtén todos los alojamientos de la base de datos
    welcome_text = "Encuentra tu próximo destino con AlquiPiso"
    return render(request, 'index.html', {
        'alojamientos': alojamientos,
        'welcome_text': welcome_text,
    })

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
    return render(request, 'list_propietarios.html', {'propietarios': propietarios})

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
    if request.user.is_authenticated:
        # Si el usuario ya está autenticado, redirigirlo a la página de inicio
        return redirect('alquileres:index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Verifica que los campos no estén vacíos
        if not username or not password:
            messages.error(request, 'Por favor ingresa tanto el nombre de usuario como la contraseña.')
            return redirect('alquileres:login')

        # Autenticar al usuario
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Si la autenticación es exitosa, iniciar sesión y redirigir
            login(request, user)
            return redirect('alquileres:index')  # Redirige a la página principal
        else:
            # Si la autenticación falla, mostrar mensaje de error
            messages.error(request, 'Credenciales inválidas. Intenta de nuevo.')
    
    # Si no es una solicitud POST, simplemente muestra la página de login
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

def create_reserva(request, alojamiento_id):
    # Obtener el alojamiento de la base de datos
    alojamiento = get_object_or_404(Alojamiento, id=alojamiento_id)
    
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            # Crear la reserva
            reserva = form.save(commit=False)
            reserva.alojamiento = alojamiento  # Asignar el alojamiento a la reserva
            reserva.cliente = request.user.cliente # Asignar el cliente actual a la reserva
            reserva.precio_total = reserva.calcular_precio_total()  # Calcular el precio total
            reserva.fecha_reserva = timezone.now()
            reserva.save()
            return redirect('alquileres:pago_reserva', reserva_id=reserva.id)  # Redirigir después de guardar
    else:
        form = ReservaForm()

    return render(request, 'create_reserva.html', {'form': form, 'alojamiento': alojamiento, 'precio': alojamiento.precio})

@login_required
def pago_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente=request.user.cliente)
    
    if request.method == 'POST':
        # Aquí se procesaría el pago ficticio. Si es exitoso:
        reserva.pagado = True
        reserva.save()
        # Redirigir a una página de confirmación o al índice
        return redirect('alquileres:list_reservas_cliente', cliente_id=request.user.cliente.id)
    
    # Renderizamos el formulario de pago
    return render(request, 'pago_reserva.html', {'reserva': reserva})

@login_required
def edit_alojamiento(request, alojamiento_id):
    alojamiento = get_object_or_404(Alojamiento, id=alojamiento_id)

    # Verificar que el usuario autenticado sea el propietario del alojamiento
    if request.user != alojamiento.propietario.user:
        messages.error(request, "No tienes permiso para editar este alojamiento.")
        return redirect('alquileres:show_alojamiento', alojamiento_id=alojamiento_id)

    if request.method == 'POST':
        form = AlojamientoForm(request.POST, request.FILES, instance=alojamiento)
        if form.is_valid():
            form.save()
            messages.success(request, "Alojamiento actualizado con éxito.")
            return redirect('alquileres:show_alojamiento', alojamiento_id=alojamiento_id)
        else:
            messages.error(request, "Hubo un error al actualizar el alojamiento.")
    else:
        form = AlojamientoForm(instance=alojamiento)

    return render(request, 'edit_alojamiento.html', {'form': form, 'alojamiento': alojamiento})

@login_required
def list_reservas_alojamiento(request, alojamiento_id):
    alojamiento = get_object_or_404(Alojamiento, id=alojamiento_id)
    reservas = Reserva.objects.filter(alojamiento=alojamiento)

    return render(request, 'list_reservas_alojamiento.html', {
        'alojamiento': alojamiento,
        'reservas': reservas
    })