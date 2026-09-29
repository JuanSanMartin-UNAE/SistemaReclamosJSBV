from django.contrib import admin

from .forms import UsuarioForm
from .models import Barrio, Rol, Usuario


@admin.register(Barrio)
class BarrioAdmin(admin.ModelAdmin):
    list_display = ('id_barrio', 'nombre_barrio', 'fecha_alta')
    search_fields = ('nombre_barrio',)


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id_rol', 'nombre_rol', 'activo', 'fecha_alta')
    list_filter = ('activo',)
    search_fields = ('nombre_rol',)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id_usuario', 'num_documento', 'apellido', 'nombre', 'rol', 'barrio', 'activo')
    list_filter = ('activo', 'rol', 'barrio')
    search_fields = ('num_documento', 'nombre', 'apellido', 'correo_electronico')
    form = UsuarioForm
