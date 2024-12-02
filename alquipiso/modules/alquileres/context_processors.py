from .models import Notificacion

def notificaciones(request):
    if request.user.is_authenticated:
        # Obtener las 6 notificaciones más recientes
        notificaciones = Notificacion.objects.filter(recipiente=request.user).order_by('-timestamp')[:6]
        # Obtener el conteo de notificaciones no leídas
        notificaciones_no_leidas = Notificacion.objects.filter(recipiente=request.user, leido=False).count()
        return {
            'notificaciones': notificaciones,
            'notificaciones_no_leidas': notificaciones_no_leidas,
        }
    return {
        'notificaciones': [],
        'notificaciones_no_leidas': 0,
    }
