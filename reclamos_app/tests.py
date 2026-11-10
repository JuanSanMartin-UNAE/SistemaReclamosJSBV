"""Pruebas de autenticación, sesión y del túnel ngrok."""

from datetime import timedelta
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.core import mail
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.test import (
    Client,
    RequestFactory,
    SimpleTestCase,
    TestCase,
    override_settings,
)

from reclamos.hosts import (
    construir_hosts_permitidos,
    construir_origenes_csrf,
    host_es_ngrok,
    normalizar_origen,
)
from reclamos.middleware import EncabezadosProxyNgrok

from reclamos_app.forms import PerfilUsuarioForm, RegistroForm
from reclamos_app.models import Rol

Usuario = get_user_model()


class MatrizPruebasAutenticacionTest(TestCase):
    """
    Verificación automatizada de los casos declarados en la Tabla 12 (Informe 4)
    para el módulo de Autenticación y Usuarios (HU-01 y RNF-01).
    """

    def setUp(self):
        self.client = Client()
        self.rol_usuario, _ = Rol.objects.get_or_create(nombre_rol="Usuario")

        self.doc_prueba = "1234567"
        self.password_prueba = "Password2026!"

        self.usuario = Usuario.objects.create_user(
            num_documento=self.doc_prueba,
            nombre="Juan",
            apellido="San Martin",
            telefono="0981123456",
            correo_electronico="juan@example.com",
            password=self.password_prueba,
            rol=self.rol_usuario,
        )

    def _datos_registro(self, **cambios):
        """Arma un alta pública válida, distinta de la cuenta de prueba.

        Args:
            **cambios: Campos que reemplazan a los valores válidos.

        Returns:
            dict: Datos para el POST de registro.
        """
        datos = {
            "num_documento": "1234568",
            "nombre": "Carlos",
            "apellido": "Gonzalez",
            "telefono": "0982999888",
            "correo_electronico": "carlos@example.com",
            "password1": "OtraPassword2026!",
            "password2": "OtraPassword2026!",
        }
        datos.update(cambios)
        return datos

    def test_qa_t01_inicio_sesion_correcto(self):
        """QA_T01: la clave correcta abre la sesión y lleva al panel."""
        self.assertTrue(self.usuario.password.startswith("pbkdf2_sha256$"))
        self.assertNotIn(self.password_prueba, self.usuario.password)
        self.assertEqual(
            settings.PASSWORD_HASHERS[0].rsplit(".", 1)[-1], "PBKDF2PasswordHasher"
        )
        self.assertTrue(self.usuario.check_password(self.password_prueba))
        self.assertTrue(
            self.client.login(
                username=self.doc_prueba,
                password=self.password_prueba,
            )
        )
        self.client.logout()
        respuesta = self.client.post(
            "/ingresar/",
            {
                "username": self.doc_prueba,
                "password": self.password_prueba,
                "recordarme": "on",
            },
        )
        self.assertRedirects(respuesta, "/panel/")
        self.assertIn("_auth_user_id", self.client.session)

    def test_qa_t01_inicio_sesion_clave_incorrecta(self):
        """QA_T01: una clave errónea no abre la sesión."""
        self.assertFalse(
            self.client.login(
                username=self.doc_prueba,
                password="ClaveErronea2026",
            )
        )
        with self.assertLogs("reclamos_app.views.autenticacion", level="INFO"):
            respuesta = self.client.post(
                "/ingresar/",
                {
                    "username": self.doc_prueba,
                    "password": "ClaveErronea2026",
                },
            )
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_ca01_registro_exige_los_datos_minimos(self):
        """CA-01: documento, nombre, apellido, teléfono, correo y clave."""
        formulario = RegistroForm(data={})
        self.assertFalse(formulario.is_valid())
        for campo in (
            "num_documento",
            "nombre",
            "apellido",
            "telefono",
            "correo_electronico",
            "password1",
        ):
            self.assertIn(campo, formulario.errors)
        minimo = next(
            item["OPTIONS"]["min_length"]
            for item in settings.AUTH_PASSWORD_VALIDATORS
            if item["NAME"].endswith("MinimumLengthValidator")
        )
        self.assertEqual(minimo, 8)

    def test_qa_t02_bloqueo_documento_duplicado(self):
        """QA_T02: el documento repetido no se guarda y el formulario lo explica."""
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Usuario.objects.create_user(
                    num_documento=self.doc_prueba,
                    nombre="Carlos",
                    apellido="Gonzalez",
                    telefono="0982999888",
                    password="OtraPassword2026!",
                    rol=self.rol_usuario,
                )
        respuesta = self.client.post(
            "/registro/",
            self._datos_registro(num_documento=self.doc_prueba),
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(
            respuesta,
            "Ya existe un usuario con este número de documento.",
        )
        self.assertEqual(
            Usuario.objects.filter(num_documento=self.doc_prueba).count(), 1
        )

        with patch.object(RegistroForm, "save", side_effect=IntegrityError):
            with self.assertLogs("reclamos_app.views.autenticacion", level="WARNING"):
                carrera = self.client.post("/registro/", self._datos_registro())
        self.assertEqual(carrera.status_code, 200)
        self.assertContains(
            carrera,
            "Ya existe un usuario con este número de documento.",
        )

    def test_ca03_el_perfil_no_cambia_el_documento(self):
        """CA-03: el perfil muestra el documento bloqueado y conserva su valor."""
        self.assertRedirects(
            Client().get("/perfil/"),
            "/ingresar/?next=/perfil/",
        )
        self.client.force_login(self.usuario)
        pagina = self.client.get("/perfil/")
        self.assertContains(pagina, "disabled")
        self.assertContains(pagina, self.doc_prueba)
        respuesta = self.client.post(
            "/perfil/",
            {
                "num_documento": "9999999",
                "nombre": "Juan Carlos",
                "apellido": "San Martin",
                "telefono": "0981123456",
                "correo_electronico": "juan@example.com",
            },
        )
        self.assertRedirects(respuesta, "/perfil/")
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.num_documento, self.doc_prueba)
        self.assertEqual(self.usuario.nombre, "Juan Carlos")

        Usuario.objects.create_user(
            num_documento="1234569",
            nombre="Ana",
            apellido="Benitez",
            telefono="0981555666",
            correo_electronico="ana@example.com",
            password=self.password_prueba,
            rol=self.rol_usuario,
        )
        ajeno = self.client.post(
            "/perfil/",
            {
                "nombre": "Juan Carlos",
                "apellido": "San Martin",
                "telefono": "0981123456",
                "correo_electronico": "ana@example.com",
            },
        )
        self.assertEqual(ajeno.status_code, 200)
        self.assertContains(ajeno, "este correo electrónico")
        with patch.object(PerfilUsuarioForm, "save", side_effect=IntegrityError):
            with self.assertLogs("reclamos_app.views.autenticacion", level="WARNING"):
                fallo = self.client.post(
                    "/perfil/",
                    {
                        "nombre": "Juan Carlos",
                        "apellido": "San Martin",
                        "telefono": "0981123456",
                        "correo_electronico": "juan@example.com",
                    },
                )
        self.assertEqual(fallo.status_code, 200)
        self.assertContains(fallo, "No se pudo guardar el perfil")

    def test_qa_t06_seguridad_tiempo_expiracion_sesion(self):
        """QA_T06: a los 10 minutos sin actividad la sesión deja de servir."""
        self.assertEqual(settings.SESSION_COOKIE_AGE, 600)
        self.assertTrue(settings.SESSION_SAVE_EVERY_REQUEST)
        self.client.login(
            username=self.doc_prueba,
            password=self.password_prueba,
        )
        self.client.get("/panel/")
        registro = Session.objects.get(session_key=self.client.session.session_key)
        restante = (registro.expire_date - timezone.now()).total_seconds()
        self.assertGreater(restante, 500)
        self.assertLessEqual(restante, 600)
        registro.expire_date = timezone.now() - timedelta(seconds=1)
        registro.save()
        self.assertRedirects(
            self.client.get("/panel/"),
            "/ingresar/?next=/panel/",
        )


class HostsNgrokTest(SimpleTestCase):
    """Reglas de hosts y orígenes, sin depender de las variables del entorno."""

    def test_reconoce_dominios_de_ngrok_y_rechaza_parecidos(self):
        self.assertTrue(host_es_ngrok(".ngrok-free.app"))
        self.assertTrue(host_es_ngrok("abc.ngrok-free.dev"))
        self.assertTrue(host_es_ngrok("https://*.ngrok.app"))
        self.assertTrue(host_es_ngrok("https://tunel.ngrok.io"))
        self.assertFalse(host_es_ngrok("localhost"))
        self.assertFalse(host_es_ngrok("ngrok-free.app.evil.com"))

    def test_comodines_solo_cuando_el_tunel_esta_habilitado(self):
        hosts = construir_hosts_permitidos(
            ["localhost", ".ngrok-free.app"],
            permitir_ngrok=False,
            hostname_fijado="",
        )
        self.assertEqual(hosts, ["localhost"])
        self.assertNotIn(
            "https://*.ngrok-free.app",
            construir_origenes_csrf(
                ["https://*.ngrok-free.app"],
                permitir_ngrok=False,
                hostname_fijado="",
            ),
        )

    def test_dominio_fijado_sustituye_a_los_comodines(self):
        hosts = construir_hosts_permitidos(
            ["localhost", ".ngrok-free.app"],
            permitir_ngrok=False,
            hostname_fijado="junta.example.com",
        )
        self.assertEqual(hosts, ["localhost", "junta.example.com"])
        origenes = construir_origenes_csrf(
            [],
            permitir_ngrok=False,
            hostname_fijado="junta.example.com",
        )
        self.assertIn("https://junta.example.com", origenes)
        self.assertNotIn("https://*.ngrok.app", origenes)

    def test_origen_con_comodin_conserva_el_esquema(self):
        self.assertEqual(
            normalizar_origen("https://*.ngrok-free.app"),
            "https://*.ngrok-free.app",
        )


class EncabezadosProxyNgrokTest(SimpleTestCase):
    """El protocolo de confianza es el último valor que agrega ngrok."""

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = EncabezadosProxyNgrok(lambda request: request)

    def _pedir(self, host, proto):
        return self.factory.get(
            "/",
            HTTP_HOST=host,
            HTTP_X_FORWARDED_PROTO=proto,
            HTTP_X_FORWARDED_HOST="evil.example",
        )

    @override_settings(
        BEHIND_PROXY=True,
        ALLOW_NGROK=True,
        NGROK_HOSTNAME="",
        SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO", "https"),
    )
    def test_se_queda_con_el_https_final_del_tunel(self):
        procesada = self.middleware(
            self._pedir(
                "demo.ngrok-free.app",
                "http, https",
            )
        )
        self.assertEqual(procesada.META.get("HTTP_X_FORWARDED_PROTO"), "https")
        self.assertNotIn("HTTP_X_FORWARDED_HOST", procesada.META)
        self.assertTrue(procesada.is_secure())

    @override_settings(
        BEHIND_PROXY=True,
        ALLOW_NGROK=True,
        NGROK_HOSTNAME="",
        SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO", "https"),
    )
    def test_un_https_inicial_seguido_de_http_no_es_seguro(self):
        procesada = self.middleware(
            self._pedir(
                "demo.ngrok.app",
                "https, http",
            )
        )
        self.assertNotIn("HTTP_X_FORWARDED_PROTO", procesada.META)
        self.assertFalse(procesada.is_secure())

    @override_settings(
        BEHIND_PROXY=True,
        ALLOW_NGROK=True,
        NGROK_HOSTNAME="",
        SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO", "https"),
    )
    def test_localhost_ignora_el_protocolo_falsificado(self):
        peticion = self._pedir("localhost:8000", "https")
        with self.assertLogs("django.security", level="WARNING"):
            procesada = self.middleware(peticion)
        self.assertNotIn("HTTP_X_FORWARDED_PROTO", procesada.META)
        self.assertFalse(procesada.is_secure())

    @override_settings(
        BEHIND_PROXY=True,
        ALLOW_NGROK=False,
        NGROK_HOSTNAME="junta.ngrok.app",
        SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO", "https"),
    )
    def test_sin_comodines_solo_el_host_fijado_es_https(self):
        fijado = self.middleware(self._pedir("junta.ngrok.app", "https"))
        self.assertTrue(fijado.is_secure())
        with self.assertLogs("django.security", level="WARNING"):
            otro = self.middleware(self._pedir("otro.ngrok.app", "https"))
        self.assertFalse(otro.is_secure())


class TunelNgrokIntegracionTest(TestCase):
    """Login, CSRF y enlaces absolutos tal como llegan desde ngrok."""

    def setUp(self):
        self.rol_usuario, _ = Rol.objects.get_or_create(nombre_rol="Usuario")
        self.doc_prueba = "7654321"
        self.password_prueba = "Password2026!"
        self.usuario = Usuario.objects.create_user(
            num_documento=self.doc_prueba,
            nombre="Ana",
            apellido="Benitez",
            telefono="0981555666",
            correo_electronico="ana@example.com",
            password=self.password_prueba,
            rol=self.rol_usuario,
        )
        self.encabezados = {
            "HTTP_HOST": "demo.ngrok-free.app",
            "HTTP_X_FORWARDED_PROTO": "http, https",
        }

    def test_la_barra_final_no_cambia_de_sitio(self):
        """La redirección es relativa: el navegador conserva el HTTPS de ngrok."""
        respuesta = self.client.get("/ingresar", **self.encabezados)
        self.assertEqual(respuesta.status_code, 301)
        self.assertEqual(respuesta["Location"], "/ingresar/")
        self.assertFalse(respuesta["Location"].startswith("http://"))

    def test_el_ingreso_local_sigue_disponible(self):
        respuesta = self.client.get("/ingresar/", HTTP_HOST="localhost")
        self.assertEqual(respuesta.status_code, 200)

    def test_post_de_ingreso_por_ngrok_acepta_el_origen_https(self):
        cliente = Client(enforce_csrf_checks=True)
        pagina = cliente.get("/ingresar/", **self.encabezados)
        self.assertEqual(pagina.status_code, 200)
        respuesta = cliente.post(
            "/ingresar/",
            {
                "username": self.doc_prueba,
                "password": self.password_prueba,
                "csrfmiddlewaretoken": cliente.cookies["csrftoken"].value,
            },
            HTTP_ORIGIN="https://demo.ngrok-free.app",
            HTTP_REFERER="https://demo.ngrok-free.app/ingresar/",
            **self.encabezados,
        )
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn("/panel/", respuesta["Location"])

    def test_post_desde_otro_origen_sigue_bloqueado(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.get("/ingresar/", **self.encabezados)
        respuesta = cliente.post(
            "/ingresar/",
            {
                "username": self.doc_prueba,
                "password": self.password_prueba,
                "csrfmiddlewaretoken": cliente.cookies["csrftoken"].value,
            },
            HTTP_ORIGIN="https://evil.example",
            **self.encabezados,
        )
        self.assertEqual(respuesta.status_code, 403)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_enlace_de_recuperacion_usa_https_del_tunel(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.get("/recuperar/", **self.encabezados)
        respuesta = cliente.post(
            "/recuperar/",
            {
                "email": "ana@example.com",
                "csrfmiddlewaretoken": cliente.cookies["csrftoken"].value,
            },
            HTTP_ORIGIN="https://demo.ngrok-free.app",
            HTTP_REFERER="https://demo.ngrok-free.app/recuperar/",
            **self.encabezados,
        )
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(
            "https://demo.ngrok-free.app/recuperar/",
            mail.outbox[0].body,
        )
