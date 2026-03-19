from PyQt6.QtWidgets import (QDialog, QGridLayout, QWidget)
from PyQt6.QtCore import Qt
from shared.widgets.buttons import PrimaryButton
from shared.widgets.fondo import BeigeBg
from shared.widgets.text import FormField, TextoInicio
from shared.widgets.imagenes import Imagenes
from shared.widgets.layout import CenterLayout
from api_cliente import login


PRIMARY = "#0E4C66"
BLACK = "#000000"

class IniciarSesion(QDialog, BeigeBg):

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
       
        center_layout = CenterLayout(espacio=40)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = TextoInicio(label="Iniciar sesión", tamano=24, upper=True, negrita=True)
        self.nombre_usuario = FormField(label="Nombre de usuario", tamano=14)
        self.contraseña = FormField(label="Contraseña", tamano=14, password=True)
        self.texto_error = TextoInicio(label="", tamano=12, error=True)
        self.texto_error.setVisible(False)  
        self.iniciar_sesion = PrimaryButton(text="Iniciar sesión", accion=self.inicio_sesion)
        self.texto = TextoInicio(label="¿No tienes cuenta?, Regístrate", tamano=16, accion=self.registro)

        center_layout.addWidget(self.label)
        center_layout.addWidget(self.nombre_usuario)
        center_layout.addWidget(self.texto_error)
        center_layout.addWidget(self.contraseña)
        center_layout.addWidget(self.iniciar_sesion)
        center_layout.addWidget(self.texto)

        center_widget = QWidget()
        center_widget.setLayout(center_layout)
        main_layout.addWidget(center_widget, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)

    def registro(self):
        self.router.show_specialist_registration()
    
    def inicio_sesion(self):
        username = self.nombre_usuario.text()
        password = self.contraseña.text()

        status_code, data = login(username, password)

        if status_code == 200:
            self.token = data['token']
            self.router.show_inicio_especialista()
        else:
            self.texto_error.setText(data.get('error', 'Error desconocido'))
            self.texto_error.setVisible(True)