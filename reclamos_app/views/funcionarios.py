"""Vistas de consulta y mantenimiento de funcionarios."""

from django.urls import reverse_lazy

from ..forms import FuncionarioForm
from ..models import Funcionario
from .base import CrearView, EditarView, EliminarView, ListaView


class FuncionarioLista(ListaView):
    """Listado paginado de funcionarios."""

    model = Funcionario
    template_name = "reclamos_app/funcionarios/lista.html"
    context_object_name = "funcionarios"
    queryset = Funcionario.objects.select_related(
        "cargo",
        "cargo__clase_reclamo_atiende",
    )


class FuncionarioCrear(CrearView):
    """Alta de un funcionario."""

    model = Funcionario
    form_class = FuncionarioForm
    titulo = "Nuevo funcionario"
    icono = "bi-person-gear"
    success_url = reverse_lazy("reclamos_app:funcionario_lista")


class FuncionarioEditar(EditarView):
    """Edición de un funcionario."""

    model = Funcionario
    form_class = FuncionarioForm
    titulo = "Editar funcionario"
    icono = "bi-person-gear"
    success_url = reverse_lazy("reclamos_app:funcionario_lista")


class FuncionarioEliminar(EliminarView):
    """Baja de un funcionario."""

    model = Funcionario
    success_url = reverse_lazy("reclamos_app:funcionario_lista")
