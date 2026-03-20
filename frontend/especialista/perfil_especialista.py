from PyQt6.QtWidgets import QHBoxLayout, QWidget
from PyQt6.QtCore import Qt
from shared.widgets.especialista.sidebar import Sidebar
from shared.widgets.text import TextoInicio, DatosPerfil
from shared.widgets.buttons import PrimaryButton
from shared.widgets.layout import CenterLayout

class PerfilEspecialista(QWidget):
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

        self.label = TextoInicio(label="Mi perfil", tamano=22, negrita=True, upper=True)
        self.nombre_usuario = DatosPerfil(label="Nombre de usuario:", label2="nombre_usuario", tamano=15)
        self.nombre = DatosPerfil(label="Nombre:", label2="nombre", tamano=15)
        self.apellidos = DatosPerfil(label="Apellidos:", label2="apellidos", tamano=15)
        self.correo = DatosPerfil(label="Correo electrónico:", label2="correo", tamano=15)
        self.cambiar_contrasena = PrimaryButton(text="CAMBIAR CONTRASEÑA", tamano=15, accion=self.cambio_contrasena)
        

        center_layout.addWidget(self.label)
        center_layout.addWidget(self.nombre_usuario)
        center_layout.addWidget(self.nombre)
        center_layout.addWidget(self.apellidos)
        center_layout.addWidget(self.correo)
        center_layout.addWidget(self.cambiar_contrasena)

        center_widget = QWidget()
        center_widget.setStyleSheet("background-color: #FFF7E7;")
        center_widget.setLayout(center_layout)
        main.addWidget(center_widget)

    def set_nombre_especialista(self, nombre: str):
        self.nombre_especialista = (nombre or "Especialista").strip() or "Especialista"
        self.sidebar.set_nombre(self.nombre_especialista)

    def set_datos_especialista(self, username: str, nombre: str, email: str = ""):
        nombre_limpio = (nombre or "Especialista").strip() or "Especialista"
        self.set_nombre_especialista(nombre_limpio)

        if " " in nombre_limpio:
            first_name, last_name = nombre_limpio.split(" ", 1)
        else:
            first_name, last_name = nombre_limpio, ""

        self.nombre_usuario.dato.setText(username or "-")
        self.nombre.dato.setText(first_name)
        self.apellidos.dato.setText(last_name or "-")
        self.correo.dato.setText(email or "-")

    def cambio_contrasena(self):
        self.router.show_cambiar_contrasena()