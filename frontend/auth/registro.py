from PyQt6.QtWidgets import (QDialog, QGridLayout, QWidget)
from PyQt6.QtCore import Qt
from shared.widgets.buttons import PrimaryButton
from shared.widgets.fondo import BeigeBg
from shared.widgets.text import FormField, TextoInicio
from shared.widgets.imagenes import Imagenes
from shared.widgets.layout import CenterLayout


PRIMARY = "#0E4C66"
BLACK = "#000000"

class Registro(QDialog, BeigeBg):

    def __init__(self, router):
        super().__init__()
        self.router = router
        self.a()

    def a(self):
        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)
        main_layout.setRowStretch(0, 1)
        main_layout.setColumnStretch(0, 1)

        self.imagen = Imagenes(enlace="assets/images/logo.png", ancho=80, alto=80)
        main_layout.addWidget(
            self.imagen,
            0,
            0,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
        )
       
        self.center_layout = CenterLayout(espacio=40)
        self.center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = TextoInicio(label="Registro", tamano=24, upper=True, negrita=True)
        self.nombre_usuario = FormField(label="Nombre de usuario", tamano=14)
        self.nombre = FormField(label="Nombre", tamano=14)
        self.apellidos = FormField(label="Apellidos", tamano=14)
        self.correo = FormField(label="Correo electrónico", tamano=14)
        self.contraseña = FormField(label="Contraseña", tamano=14, password=True)
        self.registrarse = PrimaryButton(text="Registrarse", accion=self.register)
        self.texto = TextoInicio(label="¿Ya tienes cuenta?, Inicia sesión", tamano=16, accion=self.inicio_sesion)

        self.center_layout.addWidget(self.label)
        self.center_layout.addWidget(self.nombre_usuario)
        self.center_layout.addWidget(self.nombre)
        self.center_layout.addWidget(self.apellidos)
        self.center_layout.addWidget(self.correo)        
        self.center_layout.addWidget(self.contraseña)
        self.center_layout.addWidget(self.registrarse)
        self.center_layout.addWidget(self.texto)

        self.center_widget = QWidget()
        self.center_widget.setLayout(self.center_layout)
        main_layout.addWidget(self.center_widget, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self._apply_responsive()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_responsive()

    def _apply_responsive(self):
        w = self.width()
        self.center_layout.apply_responsive(w)

        # Ajustes de widgets según tamaño
        if w < 900:
            self.imagen.setFixedSize(56, 56)
            self.registrarse.setMaximumWidth(220)
        else:
            self.imagen.setFixedSize(80, 80)
            self.registrarse.setMaximumWidth(300)

    def register(self):
        self.router.show_inicio_especialista()

    def inicio_sesion(self):
        self.router.show_specialist_login()
