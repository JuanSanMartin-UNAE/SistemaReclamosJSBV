from .autenticacion import (
    Ingresar, Recuperar, RecuperarCompleto, RecuperarConfirmar, RecuperarEnviado, Registro, Salir, bienvenida,
)
from .panel import panel
from .barrios import BarrioCrear, BarrioEditar, BarrioEliminar, BarrioLista
from .cargos_funcionarios import (
    CargoFuncionarioCrear, CargoFuncionarioEditar, CargoFuncionarioEliminar, CargoFuncionarioLista,
)
from .clasificaciones_reclamo import (
    ClasificacionReclamoCrear, ClasificacionReclamoEditar, ClasificacionReclamoEliminar, ClasificacionReclamoLista,
)
from .estados_reclamo import (
    EstadoReclamoCrear, EstadoReclamoEditar, EstadoReclamoEliminar, EstadoReclamoLista,
)
from .funcionarios import FuncionarioCrear, FuncionarioEditar, FuncionarioEliminar, FuncionarioLista
from .prioridades import PrioridadCrear, PrioridadEditar, PrioridadEliminar, PrioridadLista
from .roles import RolCrear, RolEditar, RolEliminar, RolLista
from .tipos_reclamo import TipoReclamoCrear, TipoReclamoEditar, TipoReclamoEliminar, TipoReclamoLista
from .usuarios import UsuarioCrear, UsuarioEditar, UsuarioEliminar, UsuarioLista
