from django.urls import path
from . import views

app_name = 'alquileres' 
urlpatterns = [
    path('', views.index, name='index'),  # Página de inicio

    # Rutas para Alojamientos
    path('alojamientos/', views.list_alojamientos, name='alojamientos'),  # This should list all alojamientos
    path('alojamiento/<int:alojamiento_id>/', views.show_alojamiento, name='show_alojamiento'),  # This should show a specific alojamiento
    path('propietario/<int:propietario_id>/alojamientos/', views.list_alojamientos_propietario, name='list_alojamientos_propietario'),  # Alojamientos de un propietario específico
    path('create_alojamiento/', views.create_alojamiento, name='create_alojamiento'),
    path('edit_alojamiento/<int:alojamiento_id>/', views.edit_alojamiento, name='edit_alojamiento'),
    path('alojamientos/<int:alojamiento_id>/reservas/', views.list_reservas_alojamiento, name='list_reservas_alojamiento'),

    

    # Rutas para Propietarios
    path('propietarios/', views.list_propietarios, name='list_propietarios'),  # Lista de propietarios
    path('propietario/<int:propietario_id>/', views.show_propietario, name='show_propietario'),  # Detalle de propietario

    # Rutas para Clientes
    path('clientes/', views.list_clientes, name='list_clientes'),  # Lista de clientes
    path('cliente/<int:cliente_id>/', views.show_cliente, name='show_cliente'),  # Detalle de cliente

    # Rutas para Reservas
    path('reservas/', views.list_reservas, name='list_reservas'),  # Lista de reservas
    path('reserva/<int:reserva_id>/', views.show_reserva, name='show_reserva'),  # Detalle de reserva
    path('cliente/<int:cliente_id>/reservas/', views.list_reservas_cliente, name='list_reservas_cliente'),  # Reservas de un cliente específico
    path('alojamiento/<int:alojamiento_id>/reservas/', views.list_reservas_alojamiento, name='list_reservas_alojamiento'),  # Reservas de un alojamiento específico
    path('create_reserva/<int:alojamiento_id>/', views.create_reserva, name='create_reserva'),
    path('pago_reserva/<int:reserva_id>/', views.pago_reserva, name='pago_reserva'),

    path('register/', views.register, name='register'),  # Registro de usuario
    path('login/', views.login_view, name='login'),  # Inicio de sesión
    path('logout/', views.logout_view, name='logout'),  # Cierre de sesión
]
