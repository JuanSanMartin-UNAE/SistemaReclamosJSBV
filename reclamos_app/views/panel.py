from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..models import Barrio, Rol, Usuario


@login_required
def panel(request):
    contexto = {}
    if request.user.es_administrador:
        contexto.update({
            'total_barrios': Barrio.objects.count(),
            'total_roles': Rol.objects.count(),
            'total_usuarios': Usuario.objects.count(),
            'usuarios_activos': Usuario.objects.filter(is_active=True).count(),
            'ultimos_usuarios': Usuario.objects.select_related('barrio', 'rol').order_by('-fecha_inicio')[:5],
        })
    return render(request, 'reclamos_app/panel.html', contexto)
