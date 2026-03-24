from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from auth.initial_window import InitialWindow
from auth.inicio_sesion import IniciarSesion
from auth.registro import Registro
from especialista.inicio_especialista import InicioEspecialista
from especialista.perfil.perfil_especialista import PerfilEspecialista
from especialista.perfil.cambio_contraseña_especialista import CambiarContraseña
from especialista.pacientes.mis_pacientes import PacientesEspecialista
from especialista.pacientes.registrar_paciente import RegistrarPaciente
from especialista.pacientes.generacion_codigo import GenerarCodigoPaciente
from especialista.pacientes.progreso_individual import ProgresoIndividual
from especialista.pacientes.escribir_notas import PublicarNota
from api_cliente import logout as logout_api



class Router(QMainWindow):
    def __init__(self):
        super().__init__()
        self.auth_token = None
        self.refresh_token = None
        self.especialista_nombre = "Especialista"
        self.especialista_username = ""
        self.especialista_email = ""
        self.clinic_id = None

        self.setWindowTitle("Pueblo a la Vista")
        logo_path = Path(__file__).resolve().parents[1] / "assets" / "images" / "logo.png"
        self.setWindowIcon(QIcon(str(logo_path)))
        
        self.resize(800, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        #Crear pantalla
        #Auth
        self.inicio = InitialWindow(self)
        self.iniciar_sesion = IniciarSesion(self)
        self.registro = Registro(self)

        #Especialista
        self.inicio_especialista = InicioEspecialista(self)
        self.perfil_especialista = PerfilEspecialista(self)
        self.cambiar_contrasena = CambiarContraseña(self)
        self.pacientes_especialista = PacientesEspecialista(self)
        self.registrar_paciente = RegistrarPaciente(self)
        self.generar_codigo = GenerarCodigoPaciente(self)
        self.progreso_individual = ProgresoIndividual(self)
        self.publicar_nota_paciente = PublicarNota(self)

        #Añadir al stack
        self.stack.addWidget(self.inicio)
        self.stack.addWidget(self.iniciar_sesion)
        self.stack.addWidget(self.registro)

        self.stack.addWidget(self.inicio_especialista)
        self.stack.addWidget(self.perfil_especialista)  
        self.stack.addWidget(self.cambiar_contrasena)
        self.stack.addWidget(self.pacientes_especialista)
        self.stack.addWidget(self.registrar_paciente)
        self.stack.addWidget(self.generar_codigo)
        self.stack.addWidget(self.progreso_individual)
        self.stack.addWidget(self.publicar_nota_paciente)

        # Pantalla mostrada al ejecutar el programa
        self.stack.setCurrentWidget(self.inicio)

    def _sync_specialist_name(self):
        vistas = [
            self.inicio_especialista,
            self.perfil_especialista,
            self.cambiar_contrasena,
            self.pacientes_especialista,
            self.registrar_paciente,
            self.generar_codigo,
            self.progreso_individual,
            self.publicar_nota_paciente,
        ]
        for vista in vistas:
            if hasattr(vista, "set_nombre_especialista"):
                vista.set_nombre_especialista(self.especialista_nombre)

        if hasattr(self.perfil_especialista, "set_datos_especialista"):
            self.perfil_especialista.set_datos_especialista(
                username=self.especialista_username,
                nombre=self.especialista_nombre,
                email=self.especialista_email,
            )

    def set_specialist_session(self, token: str, refresh_token: str = "", nombre: str = "", username: str = "", email: str = "", clinic_id=None):
        self.auth_token = token
        self.refresh_token = refresh_token or ""
        self.especialista_nombre = (nombre or "").strip()
        self.especialista_username = username or ""
        self.especialista_email = email or ""
        self.clinic_id = clinic_id
        self._sync_specialist_name()

    def clear_specialist_session(self):
        self.auth_token = None
        self.refresh_token = None
        self.especialista_nombre = ""
        self.especialista_username = ""
        self.especialista_email = ""
        self.clinic_id = None
        self._sync_specialist_name()

    def logout_specialist_session(self):
        if self.refresh_token:
            logout_api(self.refresh_token, self.auth_token)
        self.show_inicio()


    def show_inicio(self):
        self.clear_specialist_session()
        self.stack.setCurrentWidget(self.inicio)

    def show_specialist_login(self):
        self.stack.setCurrentWidget(self.iniciar_sesion)

    def show_specialist_registration(self):
        self.stack.setCurrentWidget(self.registro)


    
    def show_inicio_especialista(self):
        self.stack.setCurrentWidget(self.inicio_especialista)
    
    def show_perfil_especialista(self):
        self.stack.setCurrentWidget(self.perfil_especialista)

    def show_cambiar_contrasena(self):
        self.stack.setCurrentWidget(self.cambiar_contrasena)

    def show_pacientes_especialista(self):
        if hasattr(self.pacientes_especialista, "recargar_pacientes"):
            self.pacientes_especialista.recargar_pacientes()
        self.stack.setCurrentWidget(self.pacientes_especialista)

    def show_registrar_paciente(self):
        self.stack.setCurrentWidget(self.registrar_paciente)

    def show_generar_codigo(self, codigo: str = ""):
        if hasattr(self.generar_codigo, "set_codigo"):
            self.generar_codigo.set_codigo(codigo)
        self.stack.setCurrentWidget(self.generar_codigo)
    
    def show_progreso_individual(self, paciente=None):
        if paciente is not None and hasattr(self.progreso_individual, "set_paciente"):
            self.progreso_individual.set_paciente(paciente)
        self.stack.setCurrentWidget(self.progreso_individual)
    
    def show_publicar_nota_paciente(self):
        if hasattr(self.publicar_nota_paciente, "set_paciente_id"):
            paciente_id = getattr(self.progreso_individual, "_paciente_id", None)
            nombre_paciente = getattr(self.progreso_individual, "_nombre_paciente", "Paciente")
            self.publicar_nota_paciente.set_paciente_id(paciente_id, nombre_paciente)
        self.stack.setCurrentWidget(self.publicar_nota_paciente)