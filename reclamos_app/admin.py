from django.contrib import admin

from .forms import UsuarioAdminForm
from .models import (
    Barrio, CargoFuncionario, ClasificacionReclamo, EstadoReclamo, Funcionario,
    Prioridad, Rol, TipoReclamo, Usuario,
)

admin.site.site_header = 'Junta de Saneamiento de Bella Vista'
admin.site.site_title = 'Sistema de Reclamos'
admin.site.index_title = 'Administración del sistema'


@admin.register(Barrio)
class BarrioAdmin(admin.ModelAdmin):
    list_display = ('id_barrio', 'nombre_barrio', 'fecha_alta')
    search_fields = ('nombre_barrio',)


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id_rol', 'nombre_rol', 'activo', 'fecha_alta')
    list_filter = ('activo',)
    search_fields = ('nombre_rol',)


@admin.register(ClasificacionReclamo)
class ClasificacionReclamoAdmin(admin.ModelAdmin):
    list_display = ('id_tipo_reclamo', 'nombre', 'fecha_alta')
    search_fields = ('nombre',)


@admin.register(CargoFuncionario)
class CargoFuncionarioAdmin(admin.ModelAdmin):
    list_display = ('id_cargo', 'nombre_cargo', 'clase_reclamo_atiende', 'fecha_alta')
    list_filter = ('clase_reclamo_atiende',)
    search_fields = ('nombre_cargo',)
    autocomplete_fields = ('clase_reclamo_atiende',)


@admin.register(EstadoReclamo)
class EstadoReclamoAdmin(admin.ModelAdmin):
    list_display = ('id_estado', 'nombre_estado', 'fecha_alta')
    search_fields = ('nombre_estado',)


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('id_funcionario', 'nombre_apellido', 'cargo', 'cant_maxima_despachada', 'fecha_alta')
    list_filter = ('cargo',)
    search_fields = ('nombre_apellido',)
    autocomplete_fields = ('cargo',)


@admin.register(Prioridad)
class PrioridadAdmin(admin.ModelAdmin):
    list_display = ('id_prioridades', 'nombre_prioridad', 'fecha_alta')
    search_fields = ('nombre_prioridad',)


@admin.register(TipoReclamo)
class TipoReclamoAdmin(admin.ModelAdmin):
    list_display = ('id_tipo_reclamo', 'reclamo', 'clase_reclamo', 'plazo_dias', 'fecha_alta')
    list_filter = ('clase_reclamo',)
    search_fields = ('reclamo',)
    autocomplete_fields = ('clase_reclamo',)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    form = UsuarioAdminForm
    list_display = ('id_usuario', 'num_documento', 'apellido', 'nombre', 'rol', 'barrio', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'rol', 'barrio')
    search_fields = ('num_documento', 'nombre', 'apellido', 'correo_electronico')
    readonly_fields = ('fecha_inicio', 'last_login')
    filter_horizontal = ('groups', 'user_permissions')
    fieldsets = (
        ('Datos personales', {
            'fields': ('num_documento', 'nombre', 'apellido', 'telefono', 'correo_electronico', 'direccion', 'barrio'),
        }),
        ('Acceso', {
            'fields': ('contrasenha_plana', 'rol', 'is_active', 'fecha_inicio', 'last_login'),
        }),
        ('Permisos', {
            'classes': ('collapse',),
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )
