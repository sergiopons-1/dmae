from PyQt6.QtWidgets import (QDialog, QGridLayout, QWidget)
from PyQt6.QtCore import Qt
from shared.widgets.buttons import PrimaryButton
from shared.widgets.banner import Banner
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
        main_layout.addWidget(self.imagen, 0, 0, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,)
       
        center_layout = CenterLayout(espacio=40)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = TextoInicio(label="Inicio sesión", tamano=24, upper=True, negrita=True)
        self.banner = Banner(self)
        self.nombre_usuario = FormField(label="Nombre de usuario", tamano=14)
        self.contraseña = FormField(label="Contraseña", tamano=14, password=True)
        self.error_username = TextoInicio(label="", tamano=12, error=True)
        self.error_username.setVisible(False)  
        self.iniciar_sesion = PrimaryButton(text="Iniciar sesión", accion=self.inicio_sesion)
        self.error_contrasena = TextoInicio(label="", tamano=12, error=True)
        self.error_contrasena.setVisible(False)  
        self.texto = TextoInicio(label="¿No tienes cuenta?, Regístrate", tamano=16, accion=self.registro)

        center_layout.addWidget(self.label)
        center_layout.addWidget(self.banner)
        center_layout.addWidget(self.nombre_usuario)
        center_layout.addWidget(self.error_username)
        center_layout.addWidget(self.contraseña)
        center_layout.addWidget(self.error_contrasena)
        center_layout.addWidget(self.iniciar_sesion)
        center_layout.addWidget(self.texto)

        center_widget = QWidget()
        center_widget.setLayout(center_layout)
        main_layout.addWidget(center_widget, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)

    def registro(self):
        self.router.show_specialist_registration()
        self.nombre_usuario.input.clear()
        self.contraseña.input.clear()
        self.banner.ocultar()
        self.error_username.setVisible(False)
        self.error_contrasena.setVisible(False)

    def mostrar_banner_exito(self, mensaje: str, duracion_ms: int = 3000):
        self.banner.mostrar(mensaje, tipo="success", duracion_ms=duracion_ms)
        
    def inicio_sesion(self):
        username = self.nombre_usuario.text()
        password = self.contraseña.text()
        self.banner.ocultar()
        self.contraseña.input.clear()

        status_code, data = login(username, password)

        if status_code == 200:
            rol = (data.get('rol') or '').lower()
            nombre = data.get('nombre', '')
            email = data.get('email', '')
            token = data.get('token', '')
            refresh_token = data.get('refresh', '')
            
            if rol == 'especialista':
                self.router.set_specialist_session(
                    token=token,
                    refresh_token=refresh_token,
                    nombre=nombre,
                    username=username,
                    email=email,
                    clinic_id=data.get('clinic_id'),
                )
                self.router.show_inicio_especialista()
            elif rol == 'paciente':
                self.router.set_patient_session(
                    token=token,
                    refresh_token=refresh_token,
                    nombre=nombre,
                    username=username,
                    email=email,
                    dni=data.get('dni', ''),
                    birth_date=data.get('birth_date', ''),
                )
                self.router.show_inicio_paciente()
            else:
                self.error_username.setText('Rol de usuario no válido')
                self.error_username.setVisible(True)
                self.error_contrasena.setVisible(False)
                return
            self.nombre_usuario.input.clear()
            self.error_username.setVisible(False)
            self.error_contrasena.setVisible(False)
        else:
            error = data.get('error', 'Error desconocido')
            if error == 'Nombre de usuario incorrecto':
                self.error_username.setText('Nombre de usuario incorrecto')
                self.error_username.setVisible(True)
                self.error_contrasena.setVisible(False)
            elif error == 'Contraseña incorrecta':
                self.error_contrasena.setText('Contraseña incorrecta')
                self.error_contrasena.setVisible(True)
                self.error_username.setVisible(False)
            elif error == 'El usuario no es especialista':
                self.error_username.setText('Nombre de usuario incorrecto')
                self.error_username.setVisible(True)
                self.error_contrasena.setVisible(False)
            else:
                self.error_username.setText(error)
                self.error_contrasena.setText(error)
                self.error_username.setVisible(True)
                self.error_contrasena.setVisible(True)
