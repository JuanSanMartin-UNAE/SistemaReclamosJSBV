"""Flujo de reclamos domiciliarios, zonales y de su reconsideración."""

import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.utils import timezone

from reclamos_app.models import (
    Barrio,
    Bitacora,
    CargoFuncionario,
    ClasificacionReclamo,
    Conexion,
    EstadoReclamo,
    Funcionario,
    Notificacion,
    Reclamo,
    Reconsideracion,
    TipoReclamo,
    Rol,
)
from reclamos_app.reglas import asegurar_catalogo_reclamos, prioridad_inicial

Usuario = get_user_model()
FECHA = "2026-11-01"
DESCRIPCION = "El agua se corta todas las mañanas y vuelve con poca presión."
MOTIVO = "La intermitencia continúa todas las mañanas después del cierre."


class FlujoReclamoTest(TestCase):
    """Un usuario registra intermitencias y pide reconsiderar el cierre."""

    def setUp(self):
        """Prepara usuarios, un barrio y el catálogo mínimo del flujo."""
        rol_admin = Rol.objects.create(nombre_rol="Administrador", fecha_alta=FECHA)
        rol_usuario = Rol.objects.create(nombre_rol="Usuario", fecha_alta=FECHA)
        self.barrio = Barrio.objects.create(nombre_barrio="Centro", fecha_alta=FECHA)
        self.admin = Usuario.objects.create_superuser(
            num_documento="8100001",
            nombre="Ada",
            apellido="Admin",
            telefono="0981100001",
            password="Password2026!",
            rol=rol_admin,
        )
        self.comun = Usuario.objects.create_user(
            num_documento="8100002",
            nombre="Nora",
            apellido="Perez",
            telefono="0981100002",
            password="Password2026!",
            rol=rol_usuario,
            barrio=self.barrio,
            direccion="Calle Palma 123",
        )
        self.otro = Usuario.objects.create_user(
            num_documento="8100003",
            nombre="Luis",
            apellido="Benitez",
            telefono="0981100003",
            password="Password2026!",
            rol=rol_usuario,
            barrio=self.barrio,
        )
        self.tipo = asegurar_catalogo_reclamos()
        self.prioridad = prioridad_inicial()
        self.pendiente = EstadoReclamo.objects.get(nombre_estado="Pendiente")
        self.resuelto = EstadoReclamo.objects.get(nombre_estado="Resuelto")
        self.en_proceso = EstadoReclamo.objects.get(nombre_estado="En proceso")
        self.media = tempfile.TemporaryDirectory()
        self.addCleanup(self.media.cleanup)
        self.client.force_login(self.comun)

    def _datos(self, **cambios):
        """Arma el alta de un reclamo de intermitencia.

        Args:
            **cambios: Campos que reemplazan a los valores válidos.

        Returns:
            dict: Datos de un POST válido, con los reemplazos aplicados.
        """
        datos = {
            "categoria": self.tipo.clase_reclamo_id,
            "tipo": self.tipo.pk,
            "barrio": self.barrio.pk,
            "descripcion": DESCRIPCION,
            "latitud": "",
            "longitud": "",
            "numero_medidor": "",
        }
        datos.update(cambios)
        return datos

    def _crear(self, texto=DESCRIPCION):
        """Crea un reclamo pendiente del usuario común.

        Args:
            texto: Descripción del reclamo.

        Returns:
            Reclamo: Instancia guardada.
        """
        conexion = Conexion.objects.create(
            usuario=self.comun,
            numero_medidor="12A",
            barrio=self.barrio,
        )
        return Reclamo.objects.create(
            fecha_hora=timezone.now(),
            descripcion=texto,
            barrio=self.barrio,
            tipo=self.tipo,
            estado=self.pendiente,
            conexion=conexion,
            prioridad=self.prioridad,
            posee_conexion=True,
        )

    def test_anonimo_va_al_ingreso(self):
        """Sin sesión, el listado exige identificarse."""
        respuesta = Client().get("/reclamos/")
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn("/ingresar/", respuesta["Location"])

    def test_registra_intermitencia_y_solo_el_titular_la_ve(self):
        """El alta, la evidencia y la privacidad del reclamo."""
        ClasificacionReclamo.objects.create(nombre="Sin tipos")
        TipoReclamo.objects.create(
            clase_reclamo=self.tipo.clase_reclamo,
            reclamo="Aviso en minuscula",
            plazo_dias=3,
        )
        formulario = self.client.get("/reclamos/nuevo/")
        self.assertEqual(formulario.status_code, 200)
        self.assertContains(formulario, "Registrar reclamo")
        self.assertNotContains(formulario, "Sin tipos")
        self.assertNotContains(formulario, "Aviso en minuscula")
        self.assertContains(formulario, "TECNICO")
        self.assertContains(formulario, "COMERCIAL")
        self.assertContains(formulario, self.tipo.reclamo)
        self.assertContains(formulario, f'data-clase="{self.tipo.clase_reclamo_id}"')
        self.assertContains(formulario, 'id="map"')
        self.assertContains(formulario, 'id="enviarReclamo"')
        self.assertContains(formulario, "csrfmiddlewaretoken")
        invalido = self.client.post(
            "/reclamos/nuevo/",
            self._datos(descripcion="Corta", posee_conexion="on"),
        )
        self.assertEqual(invalido.status_code, 200)
        self.assertContains(invalido, "al menos 15 caracteres")
        self.assertContains(invalido, "número de medidor")

        with override_settings(MEDIA_ROOT=self.media.name):
            archivo = SimpleUploadedFile(
                "nota.txt", b"texto", content_type="text/plain"
            )
            rechazada = self.client.post(
                "/reclamos/nuevo/",
                self._datos(foto=archivo),
            )
            self.assertContains(rechazada, "JPG, PNG o WEBP")
            foto = SimpleUploadedFile(
                "corte.png",
                b"\x89PNG\r\n",
                content_type="image/png",
            )
            alta = self.client.post(
                "/reclamos/nuevo/",
                self._datos(posee_conexion="on", numero_medidor="12A", foto=foto),
            )
        reclamo = Reclamo.objects.get()
        self.assertRedirects(alta, f"/reclamos/{reclamo.pk}/")
        self.assertTrue(reclamo.posee_conexion)
        self.assertEqual(reclamo.conexion.numero_medidor, "12A")
        self.assertTrue(reclamo.foto_evidencia)
        self.assertEqual(str(reclamo), f"Reclamo {reclamo.pk} — {self.tipo}")
        self.assertIn("12A", str(reclamo.conexion))

        detalle = self.client.get(f"/reclamos/{reclamo.pk}/")
        self.assertContains(detalle, "Medidor 12A")
        self.assertContains(detalle, reclamo.foto_evidencia)
        self.assertNotContains(detalle, "Editar")
        listado = self.client.get("/reclamos/")
        self.assertContains(listado, "PERDIDA DE AGUA EN LA VIA PUBLICA")

        edicion = self.client.post(
            f"/reclamos/{reclamo.pk}/editar/",
            self._datos(
                posee_conexion="on",
                numero_medidor="12A",
                descripcion="El agua se corta de lunes a sábado por la mañana.",
            ),
            follow=True,
        )
        self.assertRedirects(edicion, f"/reclamos/{reclamo.pk}/")
        self.assertContains(edicion, "no se puede modificar")
        reclamo.refresh_from_db()
        self.assertEqual(reclamo.descripcion, DESCRIPCION)

        self.client.force_login(self.otro)
        self.assertEqual(self.client.get(f"/reclamos/{reclamo.pk}/").status_code, 404)
        self.assertNotContains(self.client.get("/reclamos/"), "mañana")
        panel = self.client.get("/panel/")
        self.assertContains(panel, "Todavía no registraste reclamos.")

        self.client.force_login(self.comun)
        self.assertContains(self.client.get("/panel/"), reclamo.num_reclamo)

        self.client.force_login(self.admin)
        self.assertContains(self.client.get("/reclamos/"), "Nora Perez")
        panel_admin = self.client.get("/panel/")
        self.assertContains(panel_admin, "Total reclamos")
        self.assertContains(panel_admin, "Nora Perez")
        self.assertContains(panel_admin, "GOOGLE_MAPS_API_KEY")
        self.assertNotContains(panel_admin, "leaflet")
        with override_settings(GOOGLE_MAPS_API_KEY="clave-prueba"):
            self.assertContains(
                self.client.get("/panel/"),
                "maps.googleapis.com/maps/api/js?key=clave-prueba",
            )
        lejos = Barrio.objects.create(nombre_barrio="Lejos", fecha_alta=FECHA)
        self.assertNotContains(
            self.client.get(f"/panel/?barrio={lejos.pk}"),
            "Nora Perez",
        )
        self.assertEqual(
            self.client.get(f"/reclamos/{reclamo.pk}/gestionar/").status_code,
            200,
        )

    def test_reconsideracion_y_cupo_del_funcionario(self):
        """La reconsideración reabre el caso y el cupo frena la sexta asignación."""
        reclamo = self._crear()
        pedido = self.client.post(
            f"/reclamos/{reclamo.pk}/reconsiderar/",
            {"descargo": MOTIVO},
            follow=True,
        )
        self.assertContains(pedido, "no admite una reconsideración")
        self.assertEqual(Reconsideracion.objects.count(), 0)

        reclamo.estado = self.resuelto
        reclamo.save(update_fields=["estado"])
        self.assertTrue(reclamo.esta_cerrado())
        self.assertEqual(
            self.client.get(f"/reclamos/{reclamo.pk}/editar/").status_code,
            302,
        )
        corto = self.client.post(
            f"/reclamos/{reclamo.pk}/reconsiderar/",
            {"descargo": "Sigue igual"},
        )
        self.assertEqual(corto.status_code, 200)
        self.assertContains(corto, "más detalle")

        alta = self.client.post(
            f"/reclamos/{reclamo.pk}/reconsiderar/",
            {"descargo": MOTIVO},
        )
        self.assertRedirects(alta, f"/reclamos/{reclamo.pk}/")
        reconsideracion = Reconsideracion.objects.get()
        self.assertIn(str(reclamo.pk), str(reconsideracion))
        self.assertEqual(
            self.client.get(f"/reclamos/{reclamo.pk}/reconsiderar/").status_code,
            302,
        )

        self.assertEqual(
            self.client.get(
                f"/reconsideraciones/{reconsideracion.pk}/resolver/"
            ).status_code,
            302,
        )
        self.client.force_login(self.admin)
        resolucion = self.client.post(
            f"/reconsideraciones/{reconsideracion.pk}/resolver/",
            {"reabrir": "on", "respuesta": "Se reabre el caso por la intermitencia."},
        )
        self.assertRedirects(resolucion, f"/reclamos/{reclamo.pk}/")
        reclamo.refresh_from_db()
        self.assertEqual(reclamo.estado, self.en_proceso)
        nota = Bitacora.objects.get()
        self.assertIn("reabre", str(nota))
        self.assertContains(self.client.get(f"/reclamos/{reclamo.pk}/"), "Se reabre")
        self.assertEqual(
            self.client.get(
                f"/reconsideraciones/{reconsideracion.pk}/resolver/"
            ).status_code,
            302,
        )

        cargo = CargoFuncionario.objects.create(
            nombre_cargo="Inspector",
            clase_reclamo_atiende=self.tipo.clase_reclamo,
            fecha_alta=FECHA,
        )
        funcionario = Funcionario.objects.create(
            nombre_apellido="Luis Benitez",
            cargo=cargo,
            cant_maxima_despachada=5,
            fecha_alta=FECHA,
        )
        asignados = [self._crear(f"{DESCRIPCION} caso {numero}") for numero in range(5)]
        for caso in asignados:
            respuesta = self.client.post(
                f"/reclamos/{caso.pk}/gestionar/",
                {
                    "estado": self.pendiente.pk,
                    "prioridad": self.prioridad.pk,
                    "funcionario": funcionario.pk,
                },
            )
            self.assertRedirects(respuesta, f"/reclamos/{caso.pk}/")
        sexto = self._crear(f"{DESCRIPCION} caso extra")
        with self.assertLogs("reclamos_app.formularios_reclamo", level="INFO") as log:
            rechazo = self.client.post(
                f"/reclamos/{sexto.pk}/gestionar/",
                {
                    "estado": self.pendiente.pk,
                    "prioridad": self.prioridad.pk,
                    "funcionario": funcionario.pk,
                },
            )
        self.assertEqual(rechazo.status_code, 200)
        self.assertContains(rechazo, "máximo de 5 reclamos activos")
        self.assertTrue(any("cupo" in mensaje for mensaje in log.output))
        sexto.refresh_from_db()
        self.assertIsNone(sexto.funcionario)

        primero = asignados[0]
        self.client.post(
            f"/reclamos/{primero.pk}/gestionar/",
            {
                "estado": self.resuelto.pk,
                "prioridad": self.prioridad.pk,
                "funcionario": funcionario.pk,
            },
        )
        self.assertRedirects(
            self.client.post(
                f"/reclamos/{sexto.pk}/gestionar/",
                {
                    "estado": self.en_proceso.pk,
                    "prioridad": self.prioridad.pk,
                    "funcionario": funcionario.pk,
                },
            ),
            f"/reclamos/{sexto.pk}/",
        )
        sexto.refresh_from_db()
        self.assertEqual(sexto.funcionario, funcionario)
        self.assertEqual(sexto.clase_estado(), "text-bg-primary")

        cerrado = self._crear()
        cerrado.estado = EstadoReclamo.objects.create(nombre_estado="Archivado")
        cerrado.save(update_fields=["estado"])
        self.assertFalse(cerrado.esta_cerrado())
        self.assertEqual(cerrado.clase_estado(), "text-bg-secondary")

    def test_qa_t03_perdida_en_la_via_publica(self):
        """QA_T03: reclamo zonal con foto, coordenadas y estado pendiente."""
        tamano = int(2.1 * 1024 * 1024)
        foto = SimpleUploadedFile(
            "perdida.jpg",
            b"\xff\xd8\xff" + b"0" * (tamano - 3),
            content_type="image/jpeg",
        )
        with override_settings(MEDIA_ROOT=self.media.name):
            alta = self.client.post(
                "/reclamos/nuevo/",
                self._datos(
                    latitud="-27.0345",
                    longitud="-55.5398",
                    foto=foto,
                ),
            )
        reclamo = Reclamo.objects.get()
        self.assertRedirects(alta, f"/reclamos/{reclamo.pk}/")
        self.assertFalse(reclamo.posee_conexion)
        self.assertIsNone(reclamo.conexion_id)
        self.assertEqual(Conexion.objects.count(), 0)
        self.assertEqual(reclamo.estado.nombre_estado, "Pendiente")
        self.assertEqual(float(reclamo.latitud), -27.0345)
        self.assertEqual(float(reclamo.longitud), -55.5398)
        self.assertTrue(reclamo.foto_evidencia.startswith("reclamos/"))
        self.assertEqual(reclamo.num_reclamo, f"{reclamo.pk:06d}")
        self.assertTrue(
            Notificacion.objects.filter(reclamo=reclamo, usuario=self.comun).exists()
        )
        detalle = self.client.get(f"/reclamos/{reclamo.pk}/")
        self.assertContains(detalle, "Vía pública, sin conexión")
        self.assertContains(detalle, reclamo.num_reclamo)
        self.client.force_login(self.otro)
        self.assertEqual(self.client.get(f"/reclamos/{reclamo.pk}/").status_code, 404)

    def test_via_publica_rechaza_un_punto_fuera_de_bella_vista(self):
        """Sin coordenadas, o fuera del distrito, el alta zonal no se guarda."""
        sin_punto = self.client.post("/reclamos/nuevo/", self._datos())
        self.assertEqual(sin_punto.status_code, 200)
        self.assertContains(sin_punto, "punto del reclamo")
        fuera = self.client.post(
            "/reclamos/nuevo/",
            self._datos(latitud="-25.0000", longitud="-55.5398"),
        )
        self.assertEqual(fuera.status_code, 200)
        self.assertContains(fuera, "Bella Vista")
        self.assertEqual(Reclamo.objects.count(), 0)
