from django.urls import path

from . import views

app_name = 'reclamos_app'

urlpatterns = [
    path('', views.inicio, name='inicio'),

    path('barrios/', views.BarrioLista.as_view(), name='barrio_lista'),
    path('barrios/nuevo/', views.BarrioCrear.as_view(), name='barrio_crear'),
    path('barrios/<int:pk>/editar/', views.BarrioEditar.as_view(), name='barrio_editar'),
    path('barrios/<int:pk>/eliminar/', views.BarrioEliminar.as_view(), name='barrio_eliminar'),

    path('roles/', views.RolLista.as_view(), name='rol_lista'),
    path('roles/nuevo/', views.RolCrear.as_view(), name='rol_crear'),
    path('roles/<int:pk>/editar/', views.RolEditar.as_view(), name='rol_editar'),
    path('roles/<int:pk>/eliminar/', views.RolEliminar.as_view(), name='rol_eliminar'),

    path('usuarios/', views.UsuarioLista.as_view(), name='usuario_lista'),
    path('usuarios/nuevo/', views.UsuarioCrear.as_view(), name='usuario_crear'),
    path('usuarios/<int:pk>/editar/', views.UsuarioEditar.as_view(), name='usuario_editar'),
    path('usuarios/<int:pk>/eliminar/', views.UsuarioEliminar.as_view(), name='usuario_eliminar'),
]
