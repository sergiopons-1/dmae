from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import Qt

from shared.widgets.buttons import PrimaryButton
from shared.widgets.fondo import BeigeBg
from shared.widgets.text import TextoInicio
from shared.widgets.layout import MainLayout, CenterLayout


class NoInicioSesion(QDialog, BeigeBg):
	def __init__(self, router):
		super().__init__()
		self.router = router
		self._construir_ui()

	def _construir_ui(self):
		main_layout = MainLayout()
		self.setLayout(main_layout)
		self.setStyleSheet("background-color: #FFF7E7;")

		center_layout = CenterLayout(espacio=24)
		center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

		self.mensaje = TextoInicio(
			label="La sesión ha caducado, inicie sesión de nuevo",
			tamano=24,
			negrita=True,
			alin=Qt.AlignmentFlag.AlignCenter,
			color="#0E4C66",
		)
		self.mensaje.lbl.setWordWrap(True)

		self.btn_login = PrimaryButton(
			text="Ir a iniciar sesión",
			tamano=14,
			accion=self._ir_login,
		)

		center_layout.addWidget(self.mensaje)
		center_layout.addWidget(self.btn_login)
		main_layout.addLayout(center_layout)

	def _ir_login(self):
		if hasattr(self.router, "show_login"):
			self.router.show_login()
