"""Registro de los catálogos en el administrador de Django."""

from django.contrib import admin

from .forms import UsuarioAdminForm
from .models import (
    Barrio,
    Bitacora,
    CargoFuncionario,
    ClasificacionReclamo,
    Conexion,
    EstadoReclamo,
    Funcionario,
    Prioridad,
    Notificacion,
    Reclamo,
    Reconsideracion,
    Rol,
    TipoReclamo,
    Usuario,
)

admin.site.site_header = "Junta de Saneamiento de Bella Vista"
admin.site.site_title = "Sistema de Reclamos"
admin.site.index_title = "Administración del sistema"


@admin.register(Barrio)
class BarrioAdmin(admin.ModelAdmin):
    """Listado y búsqueda de barrios."""

    list_display = ("id_barrio", "nombre_barrio", "fecha_alta")
    search_fields = ("nombre_barrio",)


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    """Listado y búsqueda de roles."""

    list_display = ("id_rol", "nombre_rol", "activo", "fecha_alta")
    list_filter = ("activo",)
    search_fields = ("nombre_rol",)


@admin.register(ClasificacionReclamo)
class ClasificacionReclamoAdmin(admin.ModelAdmin):
    """Listado y búsqueda de clasificaciones de reclamo."""

    list_display = ("id_tipo_reclamo", "nombre", "fecha_alta")
    search_fields = ("nombre",)


@admin.register(CargoFuncionario)
class CargoFuncionarioAdmin(admin.ModelAdmin):
    """Listado y búsqueda de cargos."""

    list_display = ("id_cargo", "nombre_cargo", "clase_reclamo_atiende", "fecha_alta")
    list_filter = ("clase_reclamo_atiende",)
    search_fields = ("nombre_cargo",)
    autocomplete_fields = ("clase_reclamo_atiende",)


@admin.register(EstadoReclamo)
class EstadoReclamoAdmin(admin.ModelAdmin):
    """Listado y búsqueda de estados de reclamo."""

    list_display = ("id_estado", "nombre_estado", "fecha_alta")
    search_fields = ("nombre_estado",)


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    """Listado y búsqueda de funcionarios."""

    list_display = (
        "id_funcionario",
        "nombre_apellido",
        "cargo",
        "cant_maxima_despachada",
        "fecha_alta",
    )
    list_filter = ("cargo",)
    search_fields = ("nombre_apellido",)
    autocomplete_fields = ("cargo",)


@admin.register(Prioridad)
class PrioridadAdmin(admin.ModelAdmin):
    """Listado y búsqueda de prioridades."""

    list_display = ("id_prioridades", "nombre_prioridad", "fecha_alta")
    search_fields = ("nombre_prioridad",)


@admin.register(TipoReclamo)
class TipoReclamoAdmin(admin.ModelAdmin):
    """Listado y búsqueda de tipos de reclamo."""

    list_display = (
        "id_tipo_reclamo",
        "reclamo",
        "clase_reclamo",
        "plazo_dias",
        "fecha_alta",
    )
    list_filter = ("clase_reclamo",)
    search_fields = ("reclamo",)
    autocomplete_fields = ("clase_reclamo",)


@admin.register(Conexion)
class ConexionAdmin(admin.ModelAdmin):
    """Listado de conexiones de agua."""

    list_display = ("id_conexiones", "numero_medidor", "usuario", "barrio")
    search_fields = ("numero_medidor", "usuario__nombre", "usuario__apellido")
    autocomplete_fields = ("usuario", "barrio")


@admin.register(Reclamo)
class ReclamoAdmin(admin.ModelAdmin):
    """Listado de reclamos registrados por los usuarios."""

    list_display = (
        "id_reclamo",
        "tipo",
        "estado",
        "barrio",
        "conexion",
        "funcionario",
        "fecha_hora",
    )
    list_filter = ("estado", "posee_conexion", "barrio")
    search_fields = (
        "descripcion",
        "conexion__numero_medidor",
        "conexion__usuario__nombre",
        "conexion__usuario__apellido",
        "conexion__usuario__num_documento",
    )
    autocomplete_fields = (
        "tipo",
        "estado",
        "prioridad",
        "funcionario",
        "barrio",
        "conexion",
    )
    date_hierarchy = "fecha_hora"


@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
    """Listado de notas de seguimiento."""

    list_display = ("id_nota", "reclamo", "funcionario", "fecha_comentario")
    search_fields = ("comentario",)
    autocomplete_fields = ("reclamo", "funcionario")


@admin.register(Reconsideracion)
class ReconsideracionAdmin(admin.ModelAdmin):
    """Listado de pedidos de reconsideración."""

    list_display = (
        "id_reincidencia",
        "reclamo",
        "usuario",
        "fecha_reconsideracion",
    )
    search_fields = ("descargo",)
    autocomplete_fields = ("reclamo", "usuario", "prioridad", "funcionario")


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    """Listado de avisos enviados por un reclamo."""

    list_display = ("id_notificacion", "reclamo", "usuario", "fecha_envio")
    search_fields = ("mensaje", "usuario__num_documento")
    autocomplete_fields = ("reclamo", "usuario")


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    """Listado y edición de usuarios, incluida la contraseña."""

    form = UsuarioAdminForm
    list_display = (
        "id_usuario",
        "num_documento",
        "apellido",
        "nombre",
        "rol",
        "barrio",
        "is_active",
        "is_staff",
    )
    list_filter = ("is_active", "is_staff", "is_superuser", "rol", "barrio")
    search_fields = ("num_documento", "nombre", "apellido", "correo_electronico")
    readonly_fields = ("fecha_inicio", "last_login")
    filter_horizontal = ("groups", "user_permissions")
    fieldsets = (
        (
            "Datos personales",
            {
                "fields": (
                    "num_documento",
                    "nombre",
                    "apellido",
                    "telefono",
                    "correo_electronico",
                    "direccion",
                    "barrio",
                ),
            },
        ),
        (
            "Acceso",
            {
                "fields": (
                    "contrasenha_plana",
                    "rol",
                    "is_active",
                    "fecha_inicio",
                    "last_login",
                ),
            },
        ),
        (
            "Permisos",
            {
                "classes": ("collapse",),
                "fields": ("is_staff", "is_superuser", "groups", "user_permissions"),
            },
        ),
    )
