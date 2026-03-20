import secrets
import string

from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QDialog)
from PyQt6.QtCore import Qt
from shared.widgets.buttons import PrimaryButton
from shared.widgets.layout import CenterLayout
from shared.widgets.especialista.sidebar import Sidebar
from shared.widgets.text import TextoInicio, FormField

class GenerarCodigoPaciente(QDialog):
    def __init__(self, router, nombre="Carlos Mateo"):
        super().__init__()
        self.router = router
        self.nombre_especialista = nombre

        main = QHBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        self.sidebar = Sidebar(nombre=nombre, parent=self)
        self.sidebar.go_logout.connect(self.router.show_inicio)
        main.addWidget(self.sidebar)


        center_layout = CenterLayout(espacio=40)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = TextoInicio(label="El código del paciente es:", tamano=35, negrita=True, upper=True)
        self.codigo = TextoInicio(label=self._generar_codigo(), tamano=35, negrita=True, upper=True)
        self.cambiar_contrasena = PrimaryButton(text="VOLVER", tamano=15, accion=self.volver)
        

        center_layout.addWidget(self.label)
        center_layout.addWidget(self.codigo)
        center_layout.addWidget(self.cambiar_contrasena)

        center_widget = QWidget()
        center_widget.setStyleSheet("background-color: #FFF7E7;")
        center_widget.setLayout(center_layout)
        main.addWidget(center_widget)

    def set_nombre_especialista(self, nombre: str):
        self.nombre_especialista = (nombre or "Especialista").strip() or "Especialista"
        self.sidebar.set_nombre(self.nombre_especialista)

    def showEvent(self, event):
        self.codigo.setText(self._generar_codigo())
        super().showEvent(event)

    def _generar_codigo(self, longitud: int = 7) -> str:
        caracteres = string.ascii_uppercase + string.digits
        return "".join(secrets.choice(caracteres) for _ in range(longitud))

    def volver(self):
        self.router.show_pacientes_especialista()