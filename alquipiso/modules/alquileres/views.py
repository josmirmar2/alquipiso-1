from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from alquipiso import settings
from .forms import AlojamientoForm, UserRegistrationForm, ReservaForm, UserEditForm
from .models import Cliente, Propietario, Notificacion
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import stripe
import logging
from django.core.mail import send_mail
from datetime import timedelta
from django.utils.timezone import now
from datetime import datetime
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
logger = logging.getLogger(__name__)


stripe.api_key = settings.STRIPE_SECRET_KEY


from modules.alquileres.models import *

# Create your views here.


def index(request):
    ciudad = request.GET.get('ciudad', '')
    fecha_entrada = request.GET.get('fecha_entrada', '')
    fecha_salida = request.GET.get('fecha_salida', '')

    # Obtener todos los alojamientos si no hay filtros
    alojamientos = Alojamiento.objects.all()

    # Filtrar por ciudad si es que se proporcionó
    if ciudad:
        alojamientos = alojamientos.filter(ciudad__iexact=ciudad)

    # Filtrar por fechas si se proporcionaron
    if fecha_entrada and fecha_salida:
        try:
            # Convertir las fechas de strings a objetos datetime
            fecha_entrada = datetime.strptime(fecha_entrada, '%Y-%m-%d').date()  # Convertimos a date
            fecha_salida = datetime.strptime(fecha_salida, '%Y-%m-%d').date()  # Convertimos a date

            # Filtrar alojamientos disponibles (no solapados con reservas existentes)
            alojamientos_disponibles = []

            for alojamiento in alojamientos:
                # Consultamos las reservas existentes para ese alojamiento
                reservas_existentes = Reserva.objects.filter(alojamiento=alojamiento)

                disponible = True
                for reserva in reservas_existentes:
                    # Caso 1: La búsqueda está completamente dentro de una reserva existente
                    if fecha_entrada >= reserva.fecha_entrada and fecha_salida <= reserva.fecha_salida:
                        disponible = False
                        break

                    # Caso 2: La reserva existente está completamente dentro de las fechas de la búsqueda
                    if fecha_entrada <= reserva.fecha_entrada and fecha_salida >= reserva.fecha_salida:
                        disponible = False
                        break

                    # Caso 3: La fecha de entrada de la búsqueda está dentro del rango de una reserva existente
                    if fecha_entrada >= reserva.fecha_entrada and fecha_entrada < reserva.fecha_salida:
                        disponible = False
                        break

                    # Caso 4: La fecha de salida de la búsqueda está dentro del rango de una reserva existente
                    if fecha_salida > reserva.fecha_entrada and fecha_salida <= reserva.fecha_salida:
                        disponible = False
                        break

                    # Caso 5: Las fechas de la búsqueda son exactamente iguales a una reserva existente
                    if fecha_entrada == reserva.fecha_entrada and fecha_salida == reserva.fecha_salida:
                        disponible = False
                        break

                # Si el alojamiento es disponible, lo agregamos a la lista de alojamientos disponibles
                if disponible:
                    alojamientos_disponibles.append(alojamiento)

            # Mostrar solo los alojamientos disponibles
            return render(request, 'index.html', {
                'alojamientos': alojamientos_disponibles,
                'ciudad': ciudad,
                'fecha_entrada': fecha_entrada,
                'fecha_salida': fecha_salida,
                'welcome_text': "Encuentra tu próximo destino con AlquiPiso",
            })

        except ValueError:
            # Si la fecha no es válida, simplemente no filtramos por fechas y mostramos todos los alojamientos
            return render(request, 'index.html', {
                'alojamientos': alojamientos,
                'welcome_text': "Encuentra tu próximo destino con AlquiPiso",
            })

    # Si no hay búsqueda por fechas, simplemente mostramos todos los alojamientos
    return render(request, 'index.html', {
        'alojamientos': alojamientos,
        'welcome_text': "Encuentra tu próximo destino con AlquiPiso",
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
        form.instance.alojamiento = alojamiento  # Asignar el alojamiento al formulario
        if form.is_valid():
            # Crear la reserva
            reserva = form.save(commit=False)
            reserva.alojamiento = alojamiento  # Asignar el alojamiento a la reserva
            reserva.cliente = request.user.cliente # Asignar el cliente actual a la reserva
            reserva.precio_total = reserva.calcular_precio_total()  # Calcular el precio total
            reserva.fecha_reserva = timezone.now()
            reserva.save()

            # Crear notificación para el propietario
            propietario = alojamiento.propietario.user
            mensaje = f"Se ha realizado una nueva reserva para su alojamiento '{alojamiento.nombre}' del {reserva.fecha_entrada} al {reserva.fecha_salida}."
            Notificacion.objects.create(recipiente=propietario, mensaje=mensaje)

            # Crear notificación para el cliente
            mensaje_cliente = f"Ha realizado una reserva en el alojamiento '{alojamiento.nombre}' del {reserva.fecha_entrada} al {reserva.fecha_salida}."
            Notificacion.objects.create(recipiente=request.user, mensaje=mensaje_cliente)

            # Redirigir a la página de detalles de la reserva
            return redirect('alquileres:detalles_reserva', reserva_id=reserva.id)  # Redirigir a la vista de detalles de la reserva
    else:
        form = ReservaForm()

    return render(request, 'create_reserva.html', {'form': form, 'alojamiento': alojamiento, 'precio': alojamiento.precio})

@login_required
def detalles_reserva(request, reserva_id):
    # Obtener la reserva de la base de datos
    reserva = get_object_or_404(Reserva, id=reserva_id)

    # Pasar la clave pública de Stripe desde settings
    stripe_public_key = settings.STRIPE_PUBLIC_KEY  # Asegúrate de tener esta configuración en tu settings.py

    return render(request, 'detalles_reserva.html', {
        'reserva': reserva,
        'stripe_public_key': stripe_public_key,  # Incluir la clave pública de Stripe
    })

@login_required
def procesar_pago(request, reserva_id):
    # Obtener el modelo de la reserva
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if request.method == 'POST':
        try:
            # Crear una sesión de Stripe Checkout
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'eur',
                            'product_data': {
                                'name': reserva.alojamiento.nombre,
                            },
                            'unit_amount': int(reserva.precio_total * 100),  # Convertir euros a céntimos
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=request.build_absolute_uri('/alquileres/pago-exitoso/'),
                cancel_url=request.build_absolute_uri('/alquileres/pago-cancelado/'),
                metadata={
                    'reserva_id': reserva.id,  # Incluir la referencia de la reserva
                },
            )
            # Devolver la URL de la sesión en formato JSON
            return JsonResponse({'url': session.url})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

def pago_exitoso(request):
    return render(request, 'pago_exitoso.html')

def pago_cancelado(request):
    return render(request, 'pago_cancelado.html')

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

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        cliente_email = session.get('customer_details', {}).get('email')
        reserva_id = session.get('metadata', {}).get('reserva_id')

        if reserva_id:
            from .models import Reserva
            reserva = Reserva.objects.filter(id=reserva_id).select_related('alojamiento').first()
            if reserva:
                reserva.pagado = True
                reserva.save()

                alojamiento = reserva.alojamiento
                reserva_link = f"{request.scheme}://{request.get_host()}/reservas/{reserva.id}/"
                image_url = f"{request.scheme}://{request.get_host()}{alojamiento.imagen.url}"

                # Datos para el correo
                context = {
                    'alojamiento': alojamiento,
                    'reserva': reserva,
                    'reserva_link': reserva_link,
                    'image_url': image_url,
                }

                # Correo para el cliente
                if cliente_email:
                    subject = 'Confirmación de Reserva'
                    body = render_to_string('emails/reserva_confirmada.html', context)

                    cliente_email_message = EmailMultiAlternatives(
                        subject=subject,
                        body='Tu reserva ha sido confirmada.',
                        from_email=settings.EMAIL_HOST_USER,
                        to=[cliente_email],
                    )
                    cliente_email_message.attach_alternative(body, "text/html")
                    cliente_email_message.send()

                # Correo para el propietario
                propietario_email = alojamiento.propietario.user.email
                if propietario_email:
                    subject = 'Nueva Reserva Recibida'
                    body = render_to_string('emails/reserva_confirmada.html', context)

                    propietario_email_message = EmailMultiAlternatives(
                        subject=subject,
                        body='Has recibido una nueva reserva.',
                        from_email=settings.EMAIL_HOST_USER,
                        to=[propietario_email],
                    )
                    propietario_email_message.attach_alternative(body, "text/html")
                    propietario_email_message.send()

                # Crear notificación para el cliente y propietario tras pago exitoso
                cliente_mensaje = f"El pago de su reserva en '{reserva.alojamiento.nombre}' ha sido exitoso."
                Notificacion.objects.create(recipiente=reserva.cliente.user, mensaje=cliente_mensaje)

                propietario_mensaje = f"El cliente ha pagado la reserva en su alojamiento '{reserva.alojamiento.nombre}' del {reserva.fecha_entrada} al {reserva.fecha_salida}."
                Notificacion.objects.create(recipiente=reserva.alojamiento.propietario.user, mensaje=propietario_mensaje)

    return JsonResponse({'status': 'success'})


@login_required
def delete_reserva(request, reserva_id):
    """
    Cancelar una reserva con restricciones.
    """
    reserva = get_object_or_404(Reserva, id=reserva_id)

    # Verificar si el usuario es el cliente asociado a la reserva
    if reserva.cliente.user != request.user:
        messages.error(request, "No tienes permiso para cancelar esta reserva.")
        return redirect('alquileres:detalles_reserva', reserva_id=reserva.id)

    # Validar restricciones para cancelar reservas pagadas
    if reserva.pagado:
        dias_para_inicio = (reserva.fecha_entrada - now().date()).days
        if dias_para_inicio <= 30:
            messages.error(
                request,
                "No puedes cancelar esta reserva porque faltan menos de 30 días para su inicio."
            )
            return redirect('alquileres:detalles_reserva', reserva_id=reserva.id)

    # Si pasa las restricciones, eliminar la reserva
    reserva.delete()
    messages.success(request, "Reserva cancelada con éxito.")
    return redirect('alquileres:list_reservas_cliente', cliente_id=request.user.cliente.id)

def eliminar_reservas_no_pagadas():
    """
    Eliminar automáticamente reservas pendientes de pago después de 24 horas.
    """
    limite = now() - timedelta(hours=24)
    reservas_pendientes = Reserva.objects.filter(pagado=False, fecha_reserva__lte=limite)

    eliminadas = reservas_pendientes.count()
    reservas_pendientes.delete()

    return f"{eliminadas} reservas pendientes de pago eliminadas."

@login_required
def marcar_notificaciones_como_leidas(request):
    if request.method == 'POST':
        # Marcar todas las notificaciones no leídas del usuario como leídas
        notificaciones_actualizadas = Notificacion.objects.filter(recipiente=request.user, leido=False).update(leido=True)

        # Verificar si se actualizaron notificaciones
        if notificaciones_actualizadas > 0:
            return JsonResponse({'status': 'success', 'message': 'Notificaciones marcadas como leídas'})
        else:
            return JsonResponse({'status': 'error', 'message': 'No hay notificaciones no leídas'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

@login_required
def vista_con_notificaciones(request):
    # Obtener las últimas 6 notificaciones del usuario
    notificaciones = Notificacion.objects.filter(recipiente=request.user).order_by('-timestamp')[:6]

    # Filtrar las notificaciones no leídas del usuario logueado
    notificaciones_no_leidas = Notificacion.objects.filter(recipiente=request.user, leido=False)

    # Debug: Imprimir las notificaciones no leídas en la consola del servidor
    print(f"Usuario logueado: {request.user.id}, Notificaciones no leídas: {notificaciones_no_leidas}")

    # Pasar las notificaciones al template
    return render(request, 'base.html', {
        'notificaciones': notificaciones,
        'notificaciones_no_leidas': notificaciones_no_leidas
    })

def validar_fechas_disponibles(fecha_entrada, fecha_salida, ciudad):
    # Filtramos alojamientos por ciudad
    alojamientos = Alojamiento.objects.filter(ciudad__iexact=ciudad)

    # Convertir las fechas de entrada y salida a datetime.date para evitar problemas de comparación
    if isinstance(fecha_entrada, datetime):
        fecha_entrada = fecha_entrada.date()  # Convertimos a datetime.date
    if isinstance(fecha_salida, datetime):
        fecha_salida = fecha_salida.date()  # Convertimos a datetime.date

    for alojamiento in alojamientos:
        # Consultamos las reservas existentes para ese alojamiento
        reservas_existentes = Reserva.objects.filter(alojamiento=alojamiento)

        for reserva in reservas_existentes:
            # Caso 1: Las fechas de la búsqueda engloban las fechas de la reserva
            if fecha_entrada >= reserva.fecha_entrada and fecha_salida <= reserva.fecha_salida:
                raise ValidationError(
                    f"Las fechas seleccionadas están completamente dentro de una reserva existente."
                )
            # Caso 2: Las fechas de la reserva engloban las fechas de la búsqueda
            if fecha_entrada <= reserva.fecha_entrada and fecha_salida >= reserva.fecha_salida:
                raise ValidationError(
                    f"Las fechas seleccionadas engloban una reserva existente."
                )
            # Caso 3: La fecha de salida de la búsqueda está dentro del rango de una reserva existente
            if fecha_salida > reserva.fecha_entrada and fecha_salida <= reserva.fecha_salida:
                raise ValidationError(
                    f"La fecha de salida seleccionada cae dentro de una reserva existente."
                )
            # Caso 4: La fecha de entrada de la búsqueda está dentro del rango de una reserva existente
            if fecha_entrada >= reserva.fecha_entrada and fecha_entrada < reserva.fecha_salida:
                raise ValidationError(
                    f"La fecha de entrada seleccionada cae dentro de una reserva existente."
                )

    return True

@login_required
def user_profile(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('alquileres:user_profile')
    else:
        form = UserEditForm(instance=request.user, user=request.user)

    return render(request, 'user_profile.html', {'form': form})