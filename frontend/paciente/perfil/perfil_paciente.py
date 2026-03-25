from PyQt6.QtWidgets import QHBoxLayout, QWidget
from PyQt6.QtCore import Qt
from shared.widgets.sidebar import SidebarPaciente
from shared.widgets.text import TextoInicio, DatosPerfil
from shared.widgets.buttons import PrimaryButton
from shared.widgets.layout import CenterLayout

class PerfilPaciente(QWidget):
    def __init__(self, router, nombre=""):
        super().__init__()
        self.router = router
        self.nombre_paciente = nombre

        main = QHBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        self.sidebar = SidebarPaciente(nombre=nombre, parent=self)
        self.sidebar.go_logout.connect(self.router.show_inicio)
        main.addWidget(self.sidebar)


        center_layout = CenterLayout(espacio=40)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = TextoInicio(label="Mi perfil", tamano=22, negrita=True, upper=True)
        self.username = DatosPerfil(label="Nombre de usuario:", label2="username", tamano=15)
        self.dni = DatosPerfil(label="DNI:", label2="dni", tamano=15)
        self.nombre = DatosPerfil(label="Nombre:", label2="nombre", tamano=15)
        self.apellidos = DatosPerfil(label="Apellidos:", label2="apellidos", tamano=15)
        self.correo = DatosPerfil(label="Correo electrónico:", label2="correo", tamano=15)
        self.fecha_nacimiento = DatosPerfil(label="Fecha de nacimiento:", label2="fecha_nacimiento", tamano=15)
        self.cambiar_contrasena = PrimaryButton(text="CAMBIAR CONTRASEÑA", tamano=15, accion=self.cambio_contrasena)
        

        center_layout.addWidget(self.label)
        center_layout.addWidget(self.username)
        center_layout.addWidget(self.dni)
        center_layout.addWidget(self.nombre)
        center_layout.addWidget(self.apellidos)
        center_layout.addWidget(self.correo)
        center_layout.addWidget(self.fecha_nacimiento)
        center_layout.addWidget(self.cambiar_contrasena)

        center_widget = QWidget()
        center_widget.setStyleSheet("background-color: #FFF7E7;")
        center_widget.setLayout(center_layout)
        main.addWidget(center_widget)

    def set_nombre_paciente(self, nombre: str):
        self.nombre_paciente = (nombre or "Paciente").strip() or "Paciente"
        self.sidebar.set_nombre(self.nombre_paciente)

    def set_datos_paciente(self, username: str = "", dni: str = "", nombre: str = "", email: str = "", fecha_nacimiento: str = ""):
        nombre_limpio = (nombre or "Paciente").strip() or "Paciente"
        self.set_nombre_paciente(nombre_limpio)

        if " " in nombre_limpio:
            first_name, last_name = nombre_limpio.split(" ", 1)
        else:
            first_name, last_name = nombre_limpio, ""

        self.username.dato.setText(username or "-")
        self.dni.dato.setText(dni or "-")
        self.nombre.dato.setText(first_name)
        self.apellidos.dato.setText(last_name or "-")
        self.correo.dato.setText(email or "-")
        self.fecha_nacimiento.dato.setText(fecha_nacimiento or "-")

    def cambio_contrasena(self):
        self.router.show_cambiar_contrasena()