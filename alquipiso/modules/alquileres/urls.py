from django.urls import path

from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'alquileres' 
urlpatterns = [
    path('', views.index, name='index'),  # Página de inicio

    # Rutas para Alojamientos
    path('alojamientos/', views.list_alojamientos, name='alojamientos'),  # This should list all alojamientos
    path('propietario/<int:propietario_id>/alojamientos/', views.list_alojamientos_propietario, name='list_alojamientos_propietario'),  # Alojamientos de un propietario específico
    path('create_alojamiento/', views.create_alojamiento, name='create_alojamiento'),
    path('edit_alojamiento/<int:alojamiento_id>/', views.edit_alojamiento, name='edit_alojamiento'),
    path('alojamientos/<int:alojamiento_id>/reservas/', views.list_reservas_alojamiento, name='list_reservas_alojamiento'),
    path('delete_alojamiento/<int:alojamiento_id>/', views.delete_alojamiento, name='delete_alojamiento'),

    path('perfil/', views.user_profile, name='user_profile'),

    # Rutas para Propietarios
    path('propietarios/', views.list_propietarios, name='list_propietarios'),  # Lista de propietarios
    path('propietario/<int:propietario_id>/', views.show_propietario, name='show_propietario'),  # Detalle de propietario

    # Rutas para Clientes
    path('clientes/', views.list_clientes, name='list_clientes'),  # Lista de clientes
    path('cliente/<int:cliente_id>/', views.show_cliente, name='show_cliente'),  # Detalle de cliente

    # Rutas para Reservas
    path('reservas/', views.list_reservas, name='list_reservas'),  # Lista de reservas
    path('reserva/<int:reserva_id>/', views.detalles_reserva, name='detalles_reserva'),  # Detalle de reserva
    path('cliente/<int:cliente_id>/reservas/', views.list_reservas_cliente, name='list_reservas_cliente'),  # Reservas de un cliente específico
    path('alojamiento/<int:alojamiento_id>/reservas/', views.list_reservas_alojamiento, name='list_reservas_alojamiento'),  # Reservas de un alojamiento específico
    path('create_reserva/<int:alojamiento_id>/', views.create_reserva, name='create_reserva'),
    path('detalles_reserva/<int:reserva_id>/', views.detalles_reserva, name='detalles_reserva'),
    path('pagar/<int:reserva_id>/', views.procesar_pago, name='procesar_pago'),
    path('pago-exitoso/', views.pago_exitoso, name='pago_exitoso'),
    path('pago-cancelado/', views.pago_cancelado, name='pago_cancelado'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('cancelar_reserva/<int:reserva_id>/', views.delete_reserva, name='delete_reserva'),
    path('notificaciones/marcar_como_leidas/', views.marcar_notificaciones_como_leidas, name='marcar_notificaciones_como_leidas'),



    path('register/', views.register, name='register'),  # Registro de usuario
    path('login/', views.login_view, name='login'),  # Inicio de sesión
    path('logout/', views.logout_view, name='logout'),  # Cierre de sesión
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
