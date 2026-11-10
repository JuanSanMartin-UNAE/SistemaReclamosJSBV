"""Rutas de la aplicación de reclamos."""

from django.urls import path

from . import views

app_name = "reclamos_app"

urlpatterns = [
    path("", views.bienvenida, name="bienvenida"),
    path("panel/", views.panel, name="panel"),
    path("reportes/", views.reportes, name="reportes"),
    path("configuracion/", views.configuracion, name="configuracion"),
    path("ingresar/", views.Ingresar.as_view(), name="ingresar"),
    path("salir/", views.Salir.as_view(), name="salir"),
    path("registro/", views.Registro.as_view(), name="registro"),
    path("perfil/", views.Perfil.as_view(), name="perfil"),
    path("recuperar/", views.Recuperar.as_view(), name="recuperar"),
    path(
        "recuperar/enviado/", views.RecuperarEnviado.as_view(), name="recuperar_enviado"
    ),
    path(
        "recuperar/<uidb64>/<token>/",
        views.RecuperarConfirmar.as_view(),
        name="recuperar_confirmar",
    ),
    path(
        "recuperar/completo/",
        views.RecuperarCompleto.as_view(),
        name="recuperar_completo",
    ),
    path("barrios/", views.BarrioLista.as_view(), name="barrio_lista"),
    path("barrios/nuevo/", views.BarrioCrear.as_view(), name="barrio_crear"),
    path(
        "barrios/<int:pk>/editar/", views.BarrioEditar.as_view(), name="barrio_editar"
    ),
    path(
        "barrios/<int:pk>/eliminar/",
        views.BarrioEliminar.as_view(),
        name="barrio_eliminar",
    ),
    path("roles/", views.RolLista.as_view(), name="rol_lista"),
    path("roles/nuevo/", views.RolCrear.as_view(), name="rol_crear"),
    path("roles/<int:pk>/editar/", views.RolEditar.as_view(), name="rol_editar"),
    path("roles/<int:pk>/eliminar/", views.RolEliminar.as_view(), name="rol_eliminar"),
    path(
        "cargos/", views.CargoFuncionarioLista.as_view(), name="cargo_funcionario_lista"
    ),
    path(
        "cargos/nuevo/",
        views.CargoFuncionarioCrear.as_view(),
        name="cargo_funcionario_crear",
    ),
    path(
        "cargos/<int:pk>/editar/",
        views.CargoFuncionarioEditar.as_view(),
        name="cargo_funcionario_editar",
    ),
    path(
        "cargos/<int:pk>/eliminar/",
        views.CargoFuncionarioEliminar.as_view(),
        name="cargo_funcionario_eliminar",
    ),
    path(
        "clasificaciones/",
        views.ClasificacionReclamoLista.as_view(),
        name="clasificacion_reclamo_lista",
    ),
    path(
        "clasificaciones/nuevo/",
        views.ClasificacionReclamoCrear.as_view(),
        name="clasificacion_reclamo_crear",
    ),
    path(
        "clasificaciones/<int:pk>/editar/",
        views.ClasificacionReclamoEditar.as_view(),
        name="clasificacion_reclamo_editar",
    ),
    path(
        "clasificaciones/<int:pk>/eliminar/",
        views.ClasificacionReclamoEliminar.as_view(),
        name="clasificacion_reclamo_eliminar",
    ),
    path("estados/", views.EstadoReclamoLista.as_view(), name="estado_reclamo_lista"),
    path(
        "estados/nuevo/",
        views.EstadoReclamoCrear.as_view(),
        name="estado_reclamo_crear",
    ),
    path(
        "estados/<int:pk>/editar/",
        views.EstadoReclamoEditar.as_view(),
        name="estado_reclamo_editar",
    ),
    path(
        "estados/<int:pk>/eliminar/",
        views.EstadoReclamoEliminar.as_view(),
        name="estado_reclamo_eliminar",
    ),
    path("funcionarios/", views.FuncionarioLista.as_view(), name="funcionario_lista"),
    path(
        "funcionarios/nuevo/",
        views.FuncionarioCrear.as_view(),
        name="funcionario_crear",
    ),
    path(
        "funcionarios/<int:pk>/editar/",
        views.FuncionarioEditar.as_view(),
        name="funcionario_editar",
    ),
    path(
        "funcionarios/<int:pk>/eliminar/",
        views.FuncionarioEliminar.as_view(),
        name="funcionario_eliminar",
    ),
    path("prioridades/", views.PrioridadLista.as_view(), name="prioridad_lista"),
    path("prioridades/nuevo/", views.PrioridadCrear.as_view(), name="prioridad_crear"),
    path(
        "prioridades/<int:pk>/editar/",
        views.PrioridadEditar.as_view(),
        name="prioridad_editar",
    ),
    path(
        "prioridades/<int:pk>/eliminar/",
        views.PrioridadEliminar.as_view(),
        name="prioridad_eliminar",
    ),
    path("tipos/", views.TipoReclamoLista.as_view(), name="tipo_reclamo_lista"),
    path("tipos/nuevo/", views.TipoReclamoCrear.as_view(), name="tipo_reclamo_crear"),
    path(
        "tipos/<int:pk>/editar/",
        views.TipoReclamoEditar.as_view(),
        name="tipo_reclamo_editar",
    ),
    path(
        "tipos/<int:pk>/eliminar/",
        views.TipoReclamoEliminar.as_view(),
        name="tipo_reclamo_eliminar",
    ),
    path("reclamos/", views.ReclamoLista.as_view(), name="reclamo_lista"),
    path("reclamos/nuevo/", views.ReclamoCrear.as_view(), name="reclamo_crear"),
    path(
        "reclamos/<int:pk>/",
        views.ReclamoDetalle.as_view(),
        name="reclamo_detalle",
    ),
    path(
        "reclamos/<int:pk>/editar/",
        views.ReclamoEditar.as_view(),
        name="reclamo_editar",
    ),
    path(
        "reclamos/<int:pk>/gestionar/",
        views.ReclamoGestionar.as_view(),
        name="reclamo_gestionar",
    ),
    path(
        "reclamos/<int:pk>/reconsiderar/",
        views.ReconsideracionCrear.as_view(),
        name="reconsideracion_crear",
    ),
    path(
        "reconsideraciones/<int:pk>/resolver/",
        views.ReconsideracionResolver.as_view(),
        name="reconsideracion_resolver",
    ),
    path("usuarios/", views.UsuarioLista.as_view(), name="usuario_lista"),
    path("usuarios/nuevo/", views.UsuarioCrear.as_view(), name="usuario_crear"),
    path(
        "usuarios/<int:pk>/editar/",
        views.UsuarioEditar.as_view(),
        name="usuario_editar",
    ),
    path(
        "usuarios/<int:pk>/eliminar/",
        views.UsuarioEliminar.as_view(),
        name="usuario_eliminar",
    ),
]
