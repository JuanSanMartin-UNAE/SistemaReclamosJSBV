from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import Client, TestCase

from reclamos_app.models import Rol

Usuario = get_user_model()


class MatrizPruebasAutenticacionTest(TestCase):
    """
    Verificación automatizada de los casos declarados en la Tabla 12 (Informe 4)
    para el módulo de Autenticación y Usuarios (HU-01 y RNF-01).
    """

    def setUp(self):
        self.client = Client()
        self.rol_usuario, _ = Rol.objects.get_or_create(nombre_rol='Usuario')

        self.doc_prueba = '1234567'
        self.password_prueba = 'Password2026!'

        self.usuario = Usuario.objects.create_user(
            num_documento=self.doc_prueba,
            nombre='Juan',
            apellido='San Martin',
            telefono='0981123456',
            password=self.password_prueba,
            rol=self.rol_usuario,
        )

    def test_qa_t01_inicio_sesion_correcto(self):
        """
        [QA_T01] Validación de inicio de sesión con credenciales correctas.
        Resultado esperado: El usuario autentica y se abre la sesión.
        """
        login_exitoso = self.client.login(
            username=self.doc_prueba,
            password=self.password_prueba,
        )
        self.assertTrue(
            login_exitoso,
            'Error: El usuario con credenciales válidas no pudo iniciar sesión.',
        )

    def test_qa_t01_inicio_sesion_clave_incorrecta(self):
        """
        [QA_T01 - Variante] Rechazo de autenticación con contraseña incorrecta.
        """
        login_fallido = self.client.login(
            username=self.doc_prueba,
            password='ClaveErronea2026',
        )
        self.assertFalse(
            login_fallido,
            'Error: El sistema permitió el acceso con clave errónea.',
        )

    def test_qa_t02_bloqueo_documento_duplicado(self):
        """
        [QA_T02] Bloqueo por documento duplicado en registro de usuario.
        Resultado esperado: Dispara excepción de integridad referencial (UNIQUE).
        """
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Usuario.objects.create_user(
                    num_documento=self.doc_prueba,
                    nombre='Carlos',
                    apellido='Gonzalez',
                    telefono='0982999888',
                    password='OtraPassword2026!',
                    rol=self.rol_usuario,
                )

    def test_qa_t06_seguridad_tiempo_expiracion_sesion(self):
        """
        [QA_T06] Requisito RNF-01: Control de tiempo de sesión de 10 minutos (600 segundos).
        """
        self.assertEqual(
            settings.SESSION_COOKIE_AGE,
            600,
            'Error: SESSION_COOKIE_AGE no está configurado en 600 segundos (10 minutos).',
        )
        self.assertTrue(
            settings.SESSION_SAVE_EVERY_REQUEST,
            'Error: SESSION_SAVE_EVERY_REQUEST debe ser True para reiniciar el conteo con cada interacción.',
        )
