from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from auth.initial_window import InitialWindow
from auth.inicio_sesion import IniciarSesion
from auth.registro import Registro
from especialista.inicio_especialista import InicioEspecialista
from especialista.perfil_especialista import PerfilEspecialista
from especialista.cambio_contraseña_especialista import CambiarContraseña
from especialista.mis_pacientes import PacientesEspecialista
from especialista.registrar_paciente import RegistrarPaciente
from especialista.generacion_codigo import GenerarCodigoPaciente
from especialista.progreso_individual import ProgresoIndividual
from especialista.escribir_notas import PublicarNota



class Router(QMainWindow):
    def __init__(self):
        super().__init__()

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
        self.stack.setCurrentWidget(self.pacientes_especialista)


    def show_inicio(self):
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
        self.stack.setCurrentWidget(self.pacientes_especialista)

    def show_registrar_paciente(self):
        self.stack.setCurrentWidget(self.registrar_paciente)

    def show_generar_codigo(self):
        self.stack.setCurrentWidget(self.generar_codigo)
    
    def show_progreso_individual(self, paciente=None):
        if paciente is not None and hasattr(self.progreso_individual, "set_paciente"):
            self.progreso_individual.set_paciente(paciente)
        self.stack.setCurrentWidget(self.progreso_individual)
    
    def show_publicar_nota_paciente(self):
        self.stack.setCurrentWidget(self.publicar_nota_paciente)