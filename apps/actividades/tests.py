from datetime import time

from django.test import TestCase

from .forms import HorarioForm
from .models import Actividad, EstadoActividad, EstadoProfesor, Horario, Profesor


class HorarioFormValidationTests(TestCase):
	def setUp(self):
		estado_actividad, _ = EstadoActividad.objects.get_or_create(
			nombre="Activo"
		)
		estado_profesor, _ = EstadoProfesor.objects.get_or_create(
			nombre="Activo"
		)
		self.actividad = Actividad.objects.create(
			nombre="Yoga",
			estado_actividad=estado_actividad,
		)
		self.otra_actividad = Actividad.objects.create(
			nombre="Pilates",
			estado_actividad=estado_actividad,
		)
		self.profesor = Profesor.objects.create(
			nombre="Ana",
			apellido="Gomez",
			dni="10000001",
			telefono="",
			estado_profesor=estado_profesor,
		)
		self.otro_profesor = Profesor.objects.create(
			nombre="Luis",
			apellido="Perez",
			dni="10000002",
			telefono="",
			estado_profesor=estado_profesor,
		)

	def datos(self, actividad, profesor):
		return {
			"actividad": actividad.pk,
			"profesor": profesor.pk,
			"dia": "Lunes",
			"hora_inicio": "10:00",
			"hora_fin": "11:00",
			"cupo": 20,
		}

	def crear_horario(self, actividad, profesor):
		return Horario.objects.create(
			actividad=actividad,
			profesor=profesor,
			dia="Lunes",
			hora_inicio=time(10, 0),
			hora_fin=time(11, 0),
			cupo=20,
		)

	def test_permite_misma_actividad_y_hora_con_otro_profesor(self):
		self.crear_horario(self.actividad, self.profesor)

		form = HorarioForm(self.datos(self.actividad, self.otro_profesor))

		self.assertTrue(form.is_valid())

	def test_bloquea_mismo_profesor_en_otra_actividad_solapada(self):
		self.crear_horario(self.actividad, self.profesor)

		form = HorarioForm(self.datos(self.otra_actividad, self.profesor))

		self.assertFalse(form.is_valid())
		self.assertIn("ya tiene un horario", form.errors["__all__"][0])
