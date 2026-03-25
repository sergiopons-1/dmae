import secrets
import string

from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QDialog)
from PyQt6.QtCore import Qt
from shared.widgets.buttons import PrimaryButton
from shared.widgets.banner import Banner
from shared.widgets.layout import CenterLayout
from shared.widgets.sidebar import SidebarEspecialista
from shared.widgets.text import TextoInicio

class GenerarCodigoPaciente(QDialog):
    def __init__(self, router, nombre=""):
        super().__init__()
        self.router = router
        self.nombre_especialista = nombre
        self._codigo_actual = self._generar_codigo()

        main = QHBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        self.sidebar = SidebarEspecialista(nombre=nombre, parent=self)
        self.sidebar.go_logout.connect(self.router.show_inicio)
        main.addWidget(self.sidebar)


        center_layout = CenterLayout(espacio=40)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.banner = Banner(self)
        center_layout.addWidget(self.banner)

        self.label = TextoInicio(label="El código del paciente es:", tamano=35, negrita=True, upper=True)
        self.codigo = TextoInicio(label=self._codigo_actual, tamano=35, negrita=True, upper=True)
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

    def set_codigo(self, codigo: str):
        self._codigo_actual = (codigo or "").strip() or self._generar_codigo()
        self.codigo.setText(self._codigo_actual)

    def mostrar_banner_exito(self, mensaje: str, duracion_ms: int = 3000):
        self.banner.mostrar(mensaje, tipo="success", duracion_ms=duracion_ms)

    def _generar_codigo(self, longitud: int = 7) -> str:
        caracteres = string.ascii_uppercase + string.digits
        return "".join(secrets.choice(caracteres) for _ in range(longitud))

    def volver(self):
        self.router.show_pacientes_especialista()