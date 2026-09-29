from django.shortcuts import render

from ..models import Barrio, Rol, Usuario


def inicio(request):
    contexto = {
        'total_barrios': Barrio.objects.count(),
        'total_roles': Rol.objects.count(),
        'total_usuarios': Usuario.objects.count(),
    }
    return render(request, 'reclamos_app/inicio.html', contexto)
