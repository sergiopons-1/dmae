from PyQt6.QtWidgets import (QDialog, QGridLayout, QWidget, QCompleter)
from PyQt6.QtCore import Qt
import re
from shared.widgets.buttons import PrimaryButton
from shared.widgets.fondo import BeigeBg
from shared.widgets.text import FormField, FormComboField, TextoInicio
from shared.widgets.imagenes import Imagenes
from shared.widgets.layout import CenterLayout
from api_cliente import singin, obtener_clinicas

PRIMARY = "#0E4C66"
BLACK = "#000000"
USERNAME_RE = re.compile(r'^[\w.@+-]+$')
EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

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

        self.label = TextoInicio(label="Registro especialista", tamano=24, upper=True, negrita=True)
        self.nombre_usuario = FormField(label="Nombre de usuario", tamano=14)
        self.error_username = TextoInicio(label="", tamano=12, error=True)
        self.error_username.setVisible(False)
        self.nombre = FormField(label="Nombre", tamano=14)
        self.apellidos = FormField(label="Apellidos", tamano=14)
        self.correo = FormField(label="Correo electrónico", tamano=14)
        self.error_correo = TextoInicio(label="", tamano=12, error=True)
        self.error_correo.setVisible(False)  
        self.contraseña = FormField(label="Contraseña", tamano=14, password=True)
        self.clinica = FormComboField(label="Clínica", tamano=14)
        self.clinica.input.lineEdit().setPlaceholderText("Buscar clínica")
        self.error_clinica = TextoInicio(label="", tamano=12, error=True)
        self.error_clinica.setVisible(False)
        self.label_error = TextoInicio(label="", tamano=12, error=True)
        self.label_error.setVisible(False)
        self.registrarse = PrimaryButton(text="Registrarse", accion=self.register)
        self.texto = TextoInicio(label="¿Ya tienes cuenta?, Inicia sesión", tamano=16, accion=self.inicio_sesion)

        self.center_layout.addWidget(self.label)
        self.center_layout.addWidget(self.nombre_usuario)
        self.center_layout.addWidget(self.error_username)
        self.center_layout.addWidget(self.nombre)
        self.center_layout.addWidget(self.apellidos)
        self.center_layout.addWidget(self.correo)        
        self.center_layout.addWidget(self.error_correo)
        self.center_layout.addWidget(self.contraseña)
        self.center_layout.addWidget(self.clinica)
        self.center_layout.addWidget(self.error_clinica)
        self.center_layout.addWidget(self.label_error)
        self.center_layout.addWidget(self.registrarse)
        self.center_layout.addWidget(self.texto)
        

        self.center_widget = QWidget()
        self.center_widget.setLayout(self.center_layout)
        main_layout.addWidget(self.center_widget, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)

        self._cargar_clinicas()

    def _cargar_clinicas(self):
        self.clinica.input.clear()
        self.clinica.input.addItem("Selecciona una clínica", None)

        status_code, data = obtener_clinicas()
        if status_code != 200 or not isinstance(data, list):
            self.label_error.setText("No se pudieron cargar las clínicas. Inténtalo de nuevo.")
            self.label_error.setVisible(True)
            return

        nombres_clinicas = []
        for item in data:
            clinic_id = item.get("id")
            nombre = (item.get("nombre") or "").strip()
            if clinic_id is None or not nombre:
                continue
            self.clinica.input.addItem(nombre, clinic_id)
            nombres_clinicas.append(nombre)

        completer = QCompleter(nombres_clinicas, self.clinica.input)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.clinica.input.setCompleter(completer)
        
    def register(self):
        username = self.nombre_usuario.text().strip()
        password = self.contraseña.text().strip()
        email = self.correo.text().strip()
        first_name = self.nombre.text().strip()
        last_name = self.apellidos.text().strip()

        self.error_username.setVisible(False)
        self.error_correo.setVisible(False)
        self.error_clinica.setVisible(False)
        self.label_error.setVisible(False)

        if not all([username, password, email, first_name, last_name]):
            self.label_error.setText("Todos los campos son obligatorios")
            self.label_error.setVisible(True)
            return

        clinic_id = self.clinica.input.currentData()
        if clinic_id is None:
            clinic_name = self.clinica.input.currentText().strip().lower()
            for i in range(self.clinica.input.count()):
                if (self.clinica.input.itemText(i) or "").strip().lower() == clinic_name:
                    clinic_id = self.clinica.input.itemData(i)
                    self.clinica.input.setCurrentIndex(i)
                    break

        if clinic_id is None:
            self.error_clinica.setText("Selecciona una clínica válida")
            self.error_clinica.setVisible(True)
            return

        if len(username) > 150:
            self.error_username.setText("Máximo 150 caracteres")
            self.error_username.setVisible(True)
            return

        if not USERNAME_RE.match(username):
            self.error_username.setText("Solo letras, dígitos y @/./+/-/_")
            self.error_username.setVisible(True)
            return

        if len(first_name) > 150:
            self.label_error.setText("El nombre no puede superar 150 caracteres")
            self.label_error.setVisible(True)
            return

        if len(last_name) > 150:
            self.label_error.setText("Los apellidos no pueden superar 150 caracteres")
            self.label_error.setVisible(True)
            return

        if len(email) > 254:
            self.error_correo.setText("Máximo 254 caracteres")
            self.error_correo.setVisible(True)
            return

        if not EMAIL_RE.match(email):
            self.error_correo.setText("Correo electrónico no válido")
            self.error_correo.setVisible(True)
            return

        status_code, data = singin(username, password, email, first_name, last_name, clinic_id)

        if status_code == 201:
            self.router.set_specialist_session(
                token=data.get('token', ''),
                nombre=data.get('nombre', f'{first_name} {last_name}'.strip()),
                username=username,
                email=data.get('email', email),
                clinic_id=data.get('clinic_id'),
            )
            self.router.show_inicio_especialista()
            self.nombre_usuario.input.clear()
            self.correo.input.clear()
            self.nombre.input.clear()
            self.apellidos.input.clear()
            self.contraseña.input.clear()

        elif status_code == 400:
            error = data.get('error', 'Datos inválidos')
            if 'usuario' in error.lower():
                self.error_username.setText(error)
                self.error_username.setVisible(True)
            elif 'correo' in error.lower():
                self.error_correo.setText(error)
                self.error_correo.setVisible(True)
            else:
                self.label_error.setText(error)
                self.label_error.setVisible(True)
        elif status_code is None:
            self.label_error.setText(data.get('error', 'No se pudo conectar al servidor'))
            self.label_error.setVisible(True)
        else:
            self.label_error.setText("Error inesperado, intenta de nuevo")
            self.label_error.setVisible(True)

    def inicio_sesion(self):
        self.router.show_specialist_login()
        self.nombre_usuario.input.clear()
        self.nombre.input.clear()
        self.apellidos.input.clear()
        self.correo.input.clear()
        self.contraseña.input.clear()
        self.clinica.input.setCurrentIndex(0)
        self.error_username.setVisible(False)
        self.error_correo.setVisible(False)
        self.error_clinica.setVisible(False)
        self.label_error.setVisible(False)