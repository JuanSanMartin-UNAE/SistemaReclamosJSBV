"""Recorre catálogos, formularios y reglas de acceso exigidas por la calidad."""

import os

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from reclamos.settings import _bandera_entorno
from reclamos_app.forms import BarrioForm, RegistroForm, UsuarioForm
from reclamos_app.models import (
    Barrio,
    CargoFuncionario,
    ClasificacionReclamo,
    EstadoReclamo,
    Funcionario,
    Prioridad,
    Rol,
    TipoReclamo,
)

Usuario = get_user_model()
FECHA = "2026-11-09"


class CalidadCatalogosTest(TestCase):
    """Un administrador recorre cada catálogo y un usuario común no entra."""

    def setUp(self):
        """Prepara roles, un administrador y un usuario sin permisos."""
        self.rol_admin = Rol.objects.create(
            nombre_rol="Administrador", fecha_alta=FECHA
        )
        self.rol_usuario = Rol.objects.create(nombre_rol="Usuario", fecha_alta=FECHA)
        self.admin = Usuario.objects.create_superuser(
            num_documento="8000001",
            nombre="Ada",
            apellido="Admin",
            telefono="0981000001",
            password="Password2026!",
            rol=self.rol_admin,
        )
        self.comun = Usuario.objects.create_user(
            num_documento="8000002",
            nombre="Nora",
            apellido="Perez",
            telefono="0981000002",
            password="Password2026!",
            rol=self.rol_usuario,
        )
        self.barrio = Barrio.objects.create(nombre_barrio="Centro", fecha_alta=FECHA)
        self.client.force_login(self.admin)

    def test_anonimo_y_usuario_comun_no_administran(self):
        """El catálogo exige sesión de administrador."""
        anonimo = Client()
        portada = anonimo.get("/")
        self.assertEqual(portada.status_code, 200)
        self.assertContains(portada, 'href="#inicio"')
        self.assertContains(portada, "Cómo funciona")
        respuesta = anonimo.get("/barrios/")
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn("/ingresar/", respuesta["Location"])

        self.client.force_login(self.comun)
        respuesta = self.client.get("/barrios/")
        self.assertRedirects(respuesta, "/panel/")

    def test_panel_muestra_totales_solo_al_administrador(self):
        """El panel del administrador incluye los conteos; el del usuario, no."""
        self.assertRedirects(self.client.get("/"), "/panel/")
        self.assertRedirects(self.client.get("/registro/"), "/panel/")
        respuesta = self.client.get("/panel/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Total reclamos")
        self.assertContains(respuesta, "Pendientes")
        self.assertContains(respuesta, "En proceso")
        self.assertContains(respuesta, "Resueltos")
        self.assertContains(respuesta, "Filtrar")
        self.assertContains(respuesta, "Agregar reclamo")
        self.assertNotContains(respuesta, "Registrar reclamo")
        self.assertIn("total_reclamos", respuesta.context)
        self.assertContains(self.client.get("/reportes/"), "Por barrio")
        self.assertContains(self.client.get("/configuracion/"), "Usuarios")

        self.client.force_login(self.comun)
        respuesta = self.client.get("/panel/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Mis reclamos")
        self.assertNotContains(respuesta, "Total reclamos")
        self.assertNotIn("total_reclamos", respuesta.context)
        self.assertRedirects(self.client.get("/reportes/"), "/panel/")

    def test_textos_de_modelos_y_permiso_de_administrador(self):
        """Los modelos se muestran por su nombre y el rol define al administrador."""
        self.assertEqual(str(self.barrio), "Centro")
        self.assertEqual(str(self.rol_admin), "Administrador")
        self.assertEqual(str(self.admin), "Admin, Ada")
        self.assertEqual(self.admin.get_full_name(), "Ada Admin")
        self.assertEqual(self.admin.get_short_name(), "Ada")
        self.assertEqual(self.admin.iniciales, "AA")
        self.assertTrue(self.admin.es_administrador)
        self.assertTrue(self.admin.es_gestor)
        self.assertFalse(self.comun.es_administrador)
        self.assertFalse(self.comun.es_gestor)
        self.comun.is_staff = True
        self.assertTrue(self.comun.es_administrador)
        rol_interno = Rol.objects.create(
            nombre_rol="USUARIO INTERNO ADMINISTRATIVO", fecha_alta=FECHA
        )
        interno = Usuario.objects.create_user(
            num_documento="8000099",
            nombre="Iris",
            apellido="Interna",
            telefono="0981000099",
            password="Password2026!",
            rol=rol_interno,
        )
        self.assertFalse(interno.es_administrador)
        self.assertTrue(interno.es_administrativo)
        self.assertTrue(interno.es_gestor)
        self.client.force_login(interno)
        escritorio = self.client.get("/panel/")
        self.assertContains(escritorio, "Total reclamos")
        self.assertContains(escritorio, "Reportes")
        self.assertContains(
            self.client.get("/configuracion/"), "administrador del sistema"
        )

    def test_documento_vacio_no_crea_usuario(self):
        """Crear un usuario sin documento queda registrado y se rechaza."""
        with self.assertLogs("reclamos_app.models.usuario", level="ERROR"):
            with self.assertRaises(ValueError):
                Usuario.objects.create_user(
                    num_documento="",
                    nombre="Sin",
                    apellido="Documento",
                    telefono="0981000003",
                    password="Password2026!",
                )

    def _recorrer(self, lista, nuevo, modelo, datos, cambio, campo):
        """Ejecuta listar, crear, editar y eliminar un registro de catálogo."""
        self.assertEqual(self.client.get(lista).status_code, 200)
        self.assertEqual(self.client.get(nuevo).status_code, 200)
        alta = self.client.post(nuevo, datos)
        self.assertEqual(alta.status_code, 302, alta.content)
        objeto = modelo.objects.get(**{campo: datos[campo]})
        edicion = self.client.post(
            f"{lista}{objeto.pk}/editar/",
            {**datos, **cambio},
        )
        self.assertEqual(edicion.status_code, 302, edicion.content)
        objeto.refresh_from_db()
        self.assertEqual(getattr(objeto, campo), cambio[campo])
        self.assertEqual(str(objeto), cambio[campo])
        confirmacion = self.client.get(f"{lista}{objeto.pk}/eliminar/")
        self.assertEqual(confirmacion.status_code, 200)
        baja = self.client.post(f"{lista}{objeto.pk}/eliminar/")
        self.assertEqual(baja.status_code, 302)
        self.assertFalse(modelo.objects.filter(pk=objeto.pk).exists())

    def test_catalogo_de_barrios(self):
        """Alta, edición y baja de un barrio distinto del usado en otras pruebas."""
        self._recorrer(
            "/barrios/",
            "/barrios/nuevo/",
            Barrio,
            {"nombre_barrio": "San Blas", "fecha_alta": FECHA},
            {"nombre_barrio": "San Blas Norte"},
            "nombre_barrio",
        )

    def test_catalogo_de_roles(self):
        """Alta, edición y baja de un rol."""
        self._recorrer(
            "/roles/",
            "/roles/nuevo/",
            Rol,
            {"nombre_rol": "Operador", "fecha_alta": FECHA, "activo": "SI"},
            {"nombre_rol": "Operador de turno"},
            "nombre_rol",
        )

    def test_catalogo_de_clasificaciones_cargos_y_tipos(self):
        """Recorre las clasificaciones y los catálogos que dependen de ellas."""
        self._recorrer(
            "/clasificaciones/",
            "/clasificaciones/nuevo/",
            ClasificacionReclamo,
            {"nombre": "Comercial", "fecha_alta": FECHA},
            {"nombre": "Comercial general"},
            "nombre",
        )
        clase = ClasificacionReclamo.objects.create(nombre="Tecnico", fecha_alta=FECHA)
        self._recorrer(
            "/cargos/",
            "/cargos/nuevo/",
            CargoFuncionario,
            {
                "nombre_cargo": "Inspector",
                "clase_reclamo_atiende": clase.pk,
                "fecha_alta": FECHA,
            },
            {"nombre_cargo": "Inspector senior"},
            "nombre_cargo",
        )
        cargo = CargoFuncionario.objects.create(
            nombre_cargo="Operario",
            clase_reclamo_atiende=clase,
            fecha_alta=FECHA,
        )
        self._recorrer(
            "/funcionarios/",
            "/funcionarios/nuevo/",
            Funcionario,
            {
                "nombre_apellido": "Luis Benitez",
                "cargo": cargo.pk,
                "cant_maxima_despachada": 5,
                "fecha_alta": FECHA,
            },
            {"nombre_apellido": "Luis Benitez Diaz"},
            "nombre_apellido",
        )
        self.assertEqual(str(clase), "Tecnico")
        self.assertEqual(str(cargo), "Operario")
        self._recorrer(
            "/tipos/",
            "/tipos/nuevo/",
            TipoReclamo,
            {
                "reclamo": "Falta de agua",
                "clase_reclamo": clase.pk,
                "plazo_dias": 3,
                "fecha_alta": FECHA,
            },
            {"reclamo": "Baja presion"},
            "reclamo",
        )

    def test_catalogo_de_estados_y_prioridades(self):
        """Alta, edición y baja de estados y prioridades."""
        self._recorrer(
            "/estados/",
            "/estados/nuevo/",
            EstadoReclamo,
            {"nombre_estado": "Recibido", "fecha_alta": FECHA},
            {"nombre_estado": "En analisis"},
            "nombre_estado",
        )
        self._recorrer(
            "/prioridades/",
            "/prioridades/nuevo/",
            Prioridad,
            {"nombre_prioridad": "Alta", "fecha_alta": FECHA},
            {"nombre_prioridad": "Urgente"},
            "nombre_prioridad",
        )
        self.assertEqual(str(EstadoReclamo(nombre_estado="Recibido")), "Recibido")
        self.assertEqual(str(Prioridad(nombre_prioridad="Alta")), "Alta")

    def test_catalogo_de_usuarios_y_baja_protegida(self):
        """Crea un usuario y no borra un barrio que todavía tiene vecinos."""
        self.assertEqual(self.client.get("/usuarios/").status_code, 200)
        alta = self.client.post(
            "/usuarios/nuevo/",
            {
                "num_documento": "8000003",
                "nombre": "Lia",
                "apellido": "Gomez",
                "telefono": "0981000003",
                "correo_electronico": "lia@example.com",
                "direccion": "Calle 1",
                "barrio": self.barrio.pk,
                "rol": self.rol_usuario.pk,
                "is_active": "on",
                "contrasenha_plana": "Password2026!",
            },
        )
        self.assertEqual(alta.status_code, 302, alta.content)
        creado = Usuario.objects.get(num_documento="8000003")
        self.assertTrue(creado.check_password("Password2026!"))
        edicion = self.client.post(
            f"/usuarios/{creado.pk}/editar/",
            {
                "num_documento": "8000003",
                "nombre": "Lia",
                "apellido": "Gomez Ruiz",
                "telefono": "0981000003",
                "correo_electronico": "lia@example.com",
                "direccion": "Calle 1",
                "barrio": self.barrio.pk,
                "rol": self.rol_usuario.pk,
                "is_active": "on",
                "contrasenha_plana": "",
            },
        )
        self.assertEqual(edicion.status_code, 302, edicion.content)
        creado.refresh_from_db()
        self.assertEqual(creado.apellido, "Gomez Ruiz")
        self.assertTrue(creado.check_password("Password2026!"))

        with self.assertLogs("reclamos_app.views.base", level="WARNING"):
            bloqueada = self.client.post(f"/barrios/{self.barrio.pk}/eliminar/")
        self.assertEqual(bloqueada.status_code, 302)
        self.assertTrue(Barrio.objects.filter(pk=self.barrio.pk).exists())

        self.assertEqual(
            self.client.post(f"/usuarios/{creado.pk}/eliminar/").status_code,
            302,
        )
        self.assertFalse(Usuario.objects.filter(pk=creado.pk).exists())


class CalidadFormulariosYSesionTest(TestCase):
    """Valida formularios públicos y las dos formas de conservar la sesión."""

    def setUp(self):
        """Crea el rol de registro y una cuenta para ingresar."""
        self.rol = Rol.objects.create(nombre_rol="Usuario", fecha_alta=FECHA)
        self.barrio = Barrio.objects.create(nombre_barrio="Itapua", fecha_alta=FECHA)
        self.usuario = Usuario.objects.create_user(
            num_documento="7000001",
            nombre="Juan",
            apellido="San Martin",
            telefono="0981123456",
            correo_electronico="juan@example.com",
            password="Password2026!",
            rol=self.rol,
            barrio=self.barrio,
        )

    def _datos_registro(self, **cambios):
        """Arma los datos mínimos de un registro público."""
        datos = {
            "num_documento": "7000002",
            "nombre": "Ana",
            "apellido": "Benitez",
            "telefono": "0981555666",
            "correo_electronico": "ana@example.com",
            "direccion": "Calle 2",
            "barrio": self.barrio.pk,
            "password1": "Password2026!",
            "password2": "Password2026!",
        }
        datos.update(cambios)
        return datos

    def test_registro_crea_la_cuenta_e_inicia_sesion(self):
        """Un registro válido entra al panel con el rol Usuario."""
        respuesta = self.client.post("/registro/", self._datos_registro())
        self.assertRedirects(respuesta, "/panel/")
        cuenta = Usuario.objects.get(num_documento="7000002")
        self.assertEqual(cuenta.rol, self.rol)
        self.assertTrue(cuenta.check_password("Password2026!"))

    def test_registro_rechaza_correo_y_claves_invalidas(self):
        """El formulario informa correo repetido, claves distintas y clave débil."""
        repetido = RegistroForm(
            data=self._datos_registro(
                correo_electronico="juan@example.com",
            )
        )
        self.assertFalse(repetido.is_valid())
        self.assertIn("correo_electronico", repetido.errors)

        distintas = RegistroForm(
            data=self._datos_registro(password2="OtraPassword2026!")
        )
        self.assertFalse(distintas.is_valid())
        self.assertIn("password2", distintas.errors)

        debil = RegistroForm(
            data=self._datos_registro(
                password1="12345678",
                password2="12345678",
            )
        )
        with self.assertLogs("reclamos_app.forms", level="INFO"):
            self.assertFalse(debil.is_valid())
        self.assertIn("password2", debil.errors)

    def test_usuario_nuevo_exige_contrasena_valida(self):
        """El alta administrativa exige una contraseña que cumpla los validadores."""
        base = {
            "num_documento": "7000003",
            "nombre": "Eva",
            "apellido": "Ortiz",
            "telefono": "0981777888",
            "correo_electronico": "eva@example.com",
            "is_active": True,
        }
        sin_clave = UsuarioForm(data=base)
        self.assertFalse(sin_clave.is_valid())
        self.assertIn("contrasenha_plana", sin_clave.errors)

        debil = UsuarioForm(data={**base, "contrasenha_plana": "12345678"})
        with self.assertLogs("reclamos_app.forms", level="INFO"):
            self.assertFalse(debil.is_valid())

    def test_formulario_vacio_marca_el_campo(self):
        """Un campo con error recibe la clase de Bootstrap is-invalid."""
        formulario = BarrioForm(data={})
        self.assertFalse(formulario.is_valid())
        clases = formulario.fields["nombre_barrio"].widget.attrs["class"]
        self.assertIn("is-invalid", clases)

    def test_recordarme_conserva_o_cierra_la_sesion(self):
        """Sin recordarme la sesión termina al cerrar el navegador."""
        ingreso = self.client.post(
            "/ingresar/",
            {
                "username": "7000001",
                "password": "Password2026!",
            },
        )
        self.assertEqual(ingreso.status_code, 302)
        self.assertEqual(self.client.session.get("_session_expiry"), 0)

        self.client.post("/salir/")
        self.assertNotIn("_auth_user_id", self.client.session)

        recordada = Client()
        respuesta = recordada.post(
            "/ingresar/",
            {
                "username": "7000001",
                "password": "Password2026!",
                "recordarme": "on",
            },
        )
        self.assertEqual(respuesta.status_code, 302)
        self.assertIsNone(recordada.session.get("_session_expiry"))
        self.assertGreaterEqual(recordada.session.get_expiry_age(), 500)

    def test_recuperar_contrasena_muestra_el_formulario(self):
        """La pantalla de recuperación responde al visitante."""
        self.assertEqual(self.client.get("/recuperar/").status_code, 200)
        self.assertEqual(self.client.get("/recuperar/enviado/").status_code, 200)
        self.assertEqual(self.client.get("/recuperar/completo/").status_code, 200)

    def test_puntos_de_entrada_wsgi_y_asgi(self):
        """Los módulos de despliegue exponen la aplicación invocable."""
        from reclamos import asgi, wsgi

        self.assertTrue(callable(wsgi.application))
        self.assertTrue(callable(asgi.application))

    def test_bandera_de_entorno(self):
        """La bandera ausente, afirmativa, negativa o vacía respeta su contrato."""
        self.assertTrue(_bandera_entorno("BANDERA_INEXISTENTE_QA", True))
        os.environ["BANDERA_QA"] = "si"
        self.assertTrue(_bandera_entorno("BANDERA_QA", False))
        os.environ["BANDERA_QA"] = "0"
        self.assertFalse(_bandera_entorno("BANDERA_QA", True))
        os.environ["BANDERA_QA"] = "   "
        self.assertFalse(_bandera_entorno("BANDERA_QA", False))
        del os.environ["BANDERA_QA"]
