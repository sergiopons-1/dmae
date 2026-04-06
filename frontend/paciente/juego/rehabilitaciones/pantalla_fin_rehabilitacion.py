from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal

from shared.widgets.buttons import PrimaryButton
from shared.widgets.text import TextoInicio

class PantallaFinRehabilitacion(QWidget):
	volver_a_jugar = pyqtSignal()
	salir_del_edificio = pyqtSignal()

	PUNTOS_MAX = 3

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setStyleSheet("background-color: #FFF7E7;")
		self.setSizePolicy(
			QSizePolicy.Policy.Expanding,
			QSizePolicy.Policy.Expanding,
		)
		self._construir_ui()
		self.set_resultado(0)

	def _construir_ui(self):
		layout = QVBoxLayout(self)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(0)

		contenido = QWidget(self)
		contenido.setStyleSheet("background-color: #FFF7E7;")
		layout_contenido = QVBoxLayout(contenido)
		layout_contenido.setContentsMargins(40, 30, 40, 30)
		layout_contenido.setSpacing(18)

		self._txt_titulo = TextoInicio(
			"",
			tamano=26,
			negrita=True,
			alin=Qt.AlignmentFlag.AlignCenter,
			color="#0E4C66",
		)

		self._txt_puntuacion = TextoInicio(
			"",
			tamano=18,
			negrita=True,
			alin=Qt.AlignmentFlag.AlignCenter,
		)

		self._panel_info = QFrame()
		self._panel_info.setStyleSheet(
			"background-color: #E5E5E5; border: 1px solid #2B6B8C;"
		)
		panel_layout = QVBoxLayout(self._panel_info)
		panel_layout.setContentsMargins(22, 22, 22, 22)
		panel_layout.setSpacing(20)

		self._txt_info = TextoInicio(
			"",
			tamano=12,
			negrita=True,
			alin=Qt.AlignmentFlag.AlignCenter,
			color="#0E4C66",
		)
		self._txt_info.lbl.setWordWrap(True)

		self._btn_volver = PrimaryButton(
			"Volver a jugar",
			tamano=12,
			accion=self.volver_a_jugar,
			parent=self._panel_info,
		)
		self._btn_salir = PrimaryButton(
			"Salir del edificio",
			tamano=12,
			accion=self.salir_del_edificio,
			parent=self._panel_info,
		)

		botones = QHBoxLayout()
		botones.setSpacing(24)
		botones.addStretch(1)
		botones.addWidget(self._btn_volver)
		botones.addWidget(self._btn_salir)
		botones.addStretch(1)

		panel_layout.addWidget(self._txt_info)
		panel_layout.addLayout(botones)

		layout_contenido.addStretch(1)
		layout_contenido.addWidget(self._txt_titulo)
		layout_contenido.addWidget(self._txt_puntuacion)
		layout_contenido.addSpacing(16)
		layout_contenido.addWidget(self._panel_info)
		layout_contenido.addStretch(1)

		layout.addWidget(contenido)

	@classmethod
	def _calcular_puntos(cls, libros_colocados: int) -> int:
		if libros_colocados <= 1:
			return 0
		if libros_colocados <= 4:
			return 1
		if libros_colocados <= 7:
			return 2
		return 3

	def set_resultado(self, libros_colocados: int):
		puntos = self._calcular_puntos(libros_colocados)
		superado = puntos >= 2

		if superado:
			self._txt_titulo.setText("¡ENHORABUENA!\nHas superado el minijuego")
			self._txt_puntuacion.lbl.setStyleSheet("color: #2CC43D;")
			self._txt_info.setText(
				"El minijuego se registrará como completado, se\n"
				"guardará la información."
			)
			self._btn_volver.hide()
		else:
			self._txt_titulo.setText("¡VAYA!\nNo se ha superado el minijuego")
			self._txt_puntuacion.lbl.setStyleSheet("color: #FF2E2E;")
			self._txt_info.setText(
				"El minijuego no se registrará como completado, pero\n"
				"puedes volver a intentarlo cuando quieras\n"
				"¡NO TE DESANIMES!"
			)
			self._btn_volver.show()

		self._txt_puntuacion.setText(f"Puntuación final: {puntos}/{self.PUNTOS_MAX}")
