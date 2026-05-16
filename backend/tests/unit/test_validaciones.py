from datetime import date, timedelta
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
if str(BACKEND_DIR) not in sys.path:
	sys.path.insert(0, str(BACKEND_DIR))

from django.core.exceptions import ValidationError
from django.test import TestCase

from eye_tracking.models import AjustesPaciente
from juego.models import Edificio, Progreso, Rehabilitacion
from usuarios.models import Clinica, Especialista, Paciente, Usuario


class ValidacionesModeloTestCase(TestCase):
	@classmethod
	def setUpTestData(cls):
		cls.clinica = Clinica.objects.create(
			nombre="Clinica Test",
			direccion="Calle Test 123",
			codigoPostal="28000",
		)

		cls.usuario_especialista = Usuario.objects.create_user(
			username="especialista_test",
			password="password123",
			rol="especialista",
			clinica=cls.clinica,
			first_name="Juan Antonio",
			last_name="Perez",
		)
		cls.especialista = Especialista.objects.create(usuario=cls.usuario_especialista)

		cls.usuario_paciente = Usuario.objects.create_user(
			username="paciente_test",
			password="password123",
			rol="paciente",
			clinica=cls.clinica,
			first_name="Juan",
			last_name="Garcia",
		)
		cls.paciente = Paciente.objects.create(
			usuario=cls.usuario_paciente,
			especialista=cls.especialista,
			dni="12345678",
			fechaNacimiento=date(1995, 5, 10),
			codigoInicioSesion="ABC123",
		)

		cls.ajustes_paciente = AjustesPaciente.objects.create(
			paciente=cls.usuario_paciente,
			esta_calibrado=False,
			sensibilidad=1.0,
		)

		cls.progreso = Progreso.objects.create(paciente=cls.usuario_paciente)
		cls.rehabilitacion = Rehabilitacion.objects.create(
			progreso=cls.progreso,
		)
		cls.edificio = Edificio.objects.create(
			rehabilitacion=cls.rehabilitacion,
		)

	def _crear_usuario_paciente(self, username):
		return Usuario.objects.create_user(
			username=username,
			password="password123",
			rol="paciente",
			clinica=self.clinica,
		)

	def test_usuario_especialista_y_paciente(self):
		self.assertTrue(self.usuario_especialista.es_especialista())
		self.assertFalse(self.usuario_especialista.es_paciente())
		self.assertTrue(self.usuario_paciente.es_paciente())
		self.assertFalse(self.usuario_paciente.es_especialista())

	def test_clinica_codigo_postal_minimo_cinco_caracteres(self):
		clinica = Clinica(
			nombre="Clinica Invalida",
			direccion="Calle Test 456",
			codigoPostal="1234",
		)

		with self.assertRaises(ValidationError):
			clinica.full_clean()

	def test_clinica_codigo_postal_exactamente_cinco_caracteres_es_valido(self):
		clinica = Clinica(
			nombre="Clinica Valida",
			direccion="Calle Test 789",
			codigoPostal="54321",
		)

		clinica.full_clean()
		self.assertEqual(clinica.codigoPostal, "54321")

	def test_clinica_codigo_postal_mayor_de_cinco_caracteres_no_es_valido(self):
		clinica = Clinica(
			nombre="Clinica Invalida Longitud",
			direccion="Calle Larga 99",
			codigoPostal="123456",
		)

		with self.assertRaises(ValidationError):
			clinica.full_clean()

	def test_paciente_dni_debe_tener_ocho_digitos(self):
		paciente = Paciente(
			usuario=self.usuario_paciente,
			especialista=self.especialista,
			dni="1234567",
			fechaNacimiento=date(1990, 1, 1),
		)

		with self.assertRaises(ValidationError):
			paciente.full_clean()

	def test_paciente_dni_con_letras_no_es_valido(self):
		paciente = Paciente(
			usuario=self.usuario_paciente,
			especialista=self.especialista,
			dni="12A45678",
			fechaNacimiento=date(1990, 1, 1),
		)

		with self.assertRaises(ValidationError):
			paciente.full_clean()

	def test_paciente_dni_valido_con_ocho_digitos(self):
		usuario_paciente_nuevo = self._crear_usuario_paciente("paciente_test_dni_valido")

		paciente = Paciente(
			usuario=usuario_paciente_nuevo,
			especialista=self.especialista,
			dni="23456789",
			fechaNacimiento=date(1990, 1, 1),
		)

		paciente.full_clean()
		self.assertEqual(paciente.dni, "23456789")

	def test_paciente_codigo_inicio_sesion_repetido_no_es_valido(self):
		usuario_paciente_nuevo = self._crear_usuario_paciente("paciente_test_codigo_repetido")

		paciente = Paciente(
			usuario=usuario_paciente_nuevo,
			especialista=self.especialista,
			dni="34567890",
			fechaNacimiento=date(1993, 6, 15),
			codigoInicioSesion="ABC123",
		)

		with self.assertRaises(ValidationError):
			paciente.full_clean()

	def test_paciente_fecha_nacimiento_no_puede_ser_futura(self):
		paciente = Paciente(
			usuario=self.usuario_paciente,
			especialista=self.especialista,
			dni="87654321",
			fechaNacimiento=date.today() + timedelta(days=1),
		)

		with self.assertRaises(ValidationError):
			paciente.full_clean()

	def test_paciente_fecha_nacimiento_hoy_es_valida(self):
		usuario_paciente_nuevo = self._crear_usuario_paciente("paciente_test_fecha_hoy")

		paciente = Paciente(
			usuario=usuario_paciente_nuevo,
			especialista=self.especialista,
			dni="45678901",
			fechaNacimiento=date.today(),
		)

		paciente.full_clean()
		self.assertEqual(paciente.fechaNacimiento, date.today())

	def test_ajustes_paciente_sensibilidad_fuera_de_rango_no_es_valida(self):
		ajustes = AjustesPaciente(
			paciente=self.usuario_paciente,
			esta_calibrado=False,
			sensibilidad=3.5,
		)

		with self.assertRaises(ValidationError):
			ajustes.full_clean()

	def test_ajustes_paciente_sensibilidad_minima_valida(self):
		usuario_paciente_nuevo = Usuario.objects.create_user(
			username="paciente_test_sensibilidad_minima",
			password="password123",
			rol="paciente",
			clinica=self.clinica,
		)

		ajustes = AjustesPaciente(
			paciente=usuario_paciente_nuevo,
			esta_calibrado=True,
			sensibilidad=0.2,
		)

		ajustes.full_clean()
		self.assertEqual(ajustes.sensibilidad, 0.2)

	def test_ajustes_paciente_sensibilidad_maxima_valida(self):
		usuario_paciente_nuevo = self._crear_usuario_paciente("paciente_test_sensibilidad_maxima")

		ajustes = AjustesPaciente(
			paciente=usuario_paciente_nuevo,
			esta_calibrado=True,
			sensibilidad=3.0,
		)

		ajustes.full_clean()
		self.assertEqual(ajustes.sensibilidad, 3.0)

	def test_rehabilitacion_puntuacion_fuera_de_rango_no_es_valida(self):
		rehabilitacion = Rehabilitacion(
			progreso=self.progreso,
			puntuacionRehabilitacion=16,
		)

		with self.assertRaises(ValidationError):
			rehabilitacion.full_clean()

	def test_rehabilitacion_estado_invalido_no_es_valido(self):
		rehabilitacion = Rehabilitacion(
			progreso=self.progreso,
			estado="estado_inexistente",
		)

		with self.assertRaises(ValidationError):
			rehabilitacion.full_clean()

	def test_rehabilitacion_puntuacion_limites_validos(self):
		rehabilitacion_min = Rehabilitacion(
			progreso=self.progreso,
			puntuacionRehabilitacion=0,
		)
		rehabilitacion_max = Rehabilitacion(
			progreso=self.progreso,
			puntuacionRehabilitacion=15,
		)

		rehabilitacion_min.full_clean()
		rehabilitacion_max.full_clean()
		self.assertEqual(rehabilitacion_min.puntuacionRehabilitacion, 0)
		self.assertEqual(rehabilitacion_max.puntuacionRehabilitacion, 15)

	def test_edificio_puntuacion_fuera_de_rango_no_es_valida(self):
		edificio = Edificio(
			rehabilitacion=self.rehabilitacion,
			puntuacionEdificio=4,
		)

		with self.assertRaises(ValidationError):
			edificio.full_clean()

	def test_edificio_estado_y_nombre_validos_por_defecto(self):
		edificio = Edificio(rehabilitacion=self.rehabilitacion)

		edificio.full_clean()
		self.assertEqual(edificio.estadoEdificio, Edificio.EstadoEdificio.BLOQUEADO)
		self.assertEqual(edificio.nombre, Edificio.NombreEdificio.BIBLIOTECA)

	def test_edificio_puntuacion_limites_validos(self):
		edificio_min = Edificio(
			rehabilitacion=self.rehabilitacion,
			puntuacionEdificio=0,
		)
		edificio_max = Edificio(
			rehabilitacion=self.rehabilitacion,
			puntuacionEdificio=3,
		)

		edificio_min.full_clean()
		edificio_max.full_clean()
		self.assertEqual(edificio_min.puntuacionEdificio, 0)
		self.assertEqual(edificio_max.puntuacionEdificio, 3)
