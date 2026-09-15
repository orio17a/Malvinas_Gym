from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.urls import reverse

from .models import EstadoAptoFisico, EstadoSocio, Socio


class EliminarSocioTests(TestCase):
    def setUp(self):
        self.operador = get_user_model().objects.create_user(username="operador")
        self.operador.user_permissions.add(
            Permission.objects.get(content_type__app_label="socios", codename="delete_socio")
        )
        self.client.force_login(self.operador)
        self.inactivo = EstadoSocio.objects.create(nombre="Inactivo")
        self.socio = Socio.objects.create(
            estado_apto_fisico=EstadoAptoFisico.objects.create(nombre="Pendiente"),
            nombre="Ana", apellido="Perez", dni="12345678",
            fecha_ingreso=date.today(), estado_socio=self.inactivo,
        )
        self.url = reverse("socios:eliminar", args=[self.socio.pk])

    def test_get_no_elimina(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)
        self.assertTrue(Socio.objects.filter(pk=self.socio.pk).exists())

    def test_sin_permiso_no_elimina(self):
        self.operador.user_permissions.clear()
        self.assertEqual(self.client.post(self.url).status_code, 403)
        self.assertTrue(Socio.objects.filter(pk=self.socio.pk).exists())

    def test_otros_estados_no_se_eliminan(self):
        for nombre in ("Activo", "Pendiente"):
            with self.subTest(estado=nombre):
                self.socio.estado_socio = EstadoSocio.objects.create(nombre=nombre)
                self.socio.save()
                self.assertRedirects(
                    self.client.post(self.url),
                    reverse("socios:detalle", args=[self.socio.pk]),
                    fetch_redirect_response=False,
                )
                self.assertTrue(Socio.objects.filter(pk=self.socio.pk).exists())

    def test_elimina_inactivo_y_conserva_usuario(self):
        cuenta = get_user_model().objects.create_user(username="socio", is_active=False)
        self.socio.usuario = cuenta
        self.socio.save()
        self.assertRedirects(self.client.post(self.url), reverse("socios:lista"), fetch_redirect_response=False)
        self.assertFalse(Socio.objects.filter(pk=self.socio.pk).exists())
        cuenta.refresh_from_db()
        self.assertFalse(cuenta.is_active)

    def test_protected_error_conserva_socio(self):
        with patch.object(Socio, "delete", side_effect=ProtectedError("Historial", {self.socio})):
            respuesta = self.client.post(self.url)
        self.assertRedirects(respuesta, reverse("socios:detalle", args=[self.socio.pk]), fetch_redirect_response=False)
        self.socio.refresh_from_db()
        self.assertEqual(self.socio.estado_socio, self.inactivo)


class ReactivarSocioTests(TestCase):
    def setUp(self):
        self.operador = get_user_model().objects.create_user(username="reactivador")
        self.operador.user_permissions.add(
            Permission.objects.get(content_type__app_label="socios", codename="change_socio")
        )
        self.client.force_login(self.operador)
        self.activo = EstadoSocio.objects.create(nombre="Activo")
        self.inactivo = EstadoSocio.objects.create(nombre="Inactivo")
        self.cuenta = get_user_model().objects.create_user(username="cuenta", is_active=False)
        self.socio = Socio.objects.create(
            estado_apto_fisico=EstadoAptoFisico.objects.create(nombre="Pendiente"),
            nombre="Ana", apellido="Perez", dni="12345678", fecha_ingreso=date.today(),
            estado_socio=self.inactivo, usuario=self.cuenta,
        )
        self.url = reverse("socios:reactivar", args=[self.socio.pk])

    def test_reactiva_sin_modificar_usuario(self):
        self.assertRedirects(self.client.post(self.url), reverse("socios:detalle", args=[self.socio.pk]), fetch_redirect_response=False)
        self.socio.refresh_from_db()
        self.cuenta.refresh_from_db()
        self.assertEqual(self.socio.estado_socio, self.activo)
        self.assertFalse(self.cuenta.is_active)

    def test_get_no_modifica(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)
        self.socio.refresh_from_db()
        self.assertEqual(self.socio.estado_socio, self.inactivo)

    def test_permiso_obligatorio(self):
        self.operador.user_permissions.clear()
        self.assertEqual(self.client.post(self.url).status_code, 403)
        self.socio.refresh_from_db()
        self.assertEqual(self.socio.estado_socio, self.inactivo)

    def test_rechaza_otros_estados(self):
        pendiente = EstadoSocio.objects.create(nombre="Pendiente")
        for estado in (self.activo, pendiente):
            with self.subTest(estado=estado.nombre):
                self.socio.estado_socio = estado
                self.socio.save()
                with patch.object(Socio, "save") as guardar:
                    self.assertEqual(self.client.post(self.url).status_code, 302)
                    guardar.assert_not_called()
                self.socio.refresh_from_db()
                self.assertEqual(self.socio.estado_socio, estado)


class EstadoSocioFormularioTests(TestCase):
    def test_estado_no_es_un_campo_editable(self):
        from .forms import SocioForm

        form = SocioForm(data={"estado_socio": "999"})
        self.assertNotIn("estado_socio", form.fields)
        self.assertNotIn("estado_socio", form.Meta.fields)

    def test_alta_sin_estado_activo_no_crea_usuario(self):
        from .services import crear_socio_con_usuario

        with self.assertRaisesMessage(ValueError, "EstadoSocio llamado Activo"):
            crear_socio_con_usuario(dni="12345678", nombre="Ana", apellido="Perez")
        self.assertFalse(get_user_model().objects.filter(username="12345678").exists())

    def test_servicio_impone_activo(self):
        from .services import crear_socio_con_usuario

        activo = EstadoSocio.objects.create(nombre="Activo")
        inactivo = EstadoSocio.objects.create(nombre="Inactivo")
        with patch("apps.socios.services.Usuario") as usuarios, patch("apps.socios.services.Rol"), patch("apps.socios.services.EstadoUsuario"), patch("apps.socios.services.Socio.objects.create") as crear:
            usuarios.objects.filter.return_value.exists.return_value = False
            crear_socio_con_usuario(
                dni="12345678", nombre="Ana", apellido="Perez",
                estado_socio=inactivo, estado_socio_id=inactivo.pk,
            )
            self.assertEqual(crear.call_args.kwargs["estado_socio"], activo)
            self.assertNotIn("estado_socio_id", crear.call_args.kwargs)
