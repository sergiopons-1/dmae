from pathlib import Path

from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QSizePolicy
from auth.initial_window import InitialWindow
from auth.inicio_sesion import IniciarSesion
from auth.registro import Registro
from auth.no_inicio_sesion import NoInicioSesion
from especialista.inicio_especialista import InicioEspecialista
from especialista.perfil.perfil_especialista import PerfilEspecialista
from auth.cambio_contraseña import CambiarContraseña
from especialista.pacientes.mis_pacientes import PacientesEspecialista
from especialista.pacientes.registrar_paciente import RegistrarPaciente
from especialista.pacientes.generacion_codigo import GenerarCodigoPaciente
from especialista.pacientes.progreso_individual import ProgresoIndividual
from especialista.pacientes.escribir_notas import PublicarNota

from paciente.inicio_paciente import InicioPaciente
from paciente.perfil.perfil_paciente import PerfilPaciente
from paciente.juego.mi_progreso import MiProgreso
from paciente.ajustes.ajustes import Ajustes 
from paciente.juego.rehabilitaciones.pantalla_inicial_juego import PantallaPueblo
from paciente.juego.rehabilitaciones.pantalla_fin_rehabilitacion import PantallaFinRehabilitacion
from paciente.juego.rehabilitaciones.minijuegos.huerto.inicio_huerto import BibliotecaCompletada
from shared.widgets.juego.biblioteca.biblioteca import BibliotecaWidget
from eye_tracking.eye_tracking_controller import EyeTrackingController
from eye_tracking.persistencia_local import cargar_user_settings

from api_cliente import (
    logout as logout_api,
    registrar_puntuacion_minijuego,
    obtener_detalle_rehabilitacion,
    set_auth_expired_handler,
)




class Router(QMainWindow):
    def __init__(self):
        super().__init__()
        self.auth_token = None
        self.refresh_token = None
        self.user_rol = None
        
        # Datos de especialista
        self.especialista_nombre = "Especialista"
        self.especialista_username = ""
        self.especialista_email = ""
        self.clinic_id = None
        
        # Datos de paciente
        self.paciente_nombre = "Paciente"
        self.paciente_username = ""
        self.paciente_email = ""
        self.paciente_id = None
        self.rehabilitacion_activa_id = None
        self.rehabilitacion_activa_detalle = {}
        
        # Eye tracking controller
        self.eye_tracking_controller = None

        self.setWindowTitle("Pueblo a la Vista")
        logo_path = Path(__file__).resolve().parents[1] / "assets" / "images" / "logo.png"
        self.setWindowIcon(QIcon(str(logo_path)))

        fondo_path = Path(__file__).resolve().parents[1] / "assets" / "images" / "juego" / "inicio_juego.png"
        fondo = QPixmap(str(fondo_path))
        if not fondo.isNull():
            self.resize(fondo.size())
        else:
            self.resize(800, 600)

        self.stack = QStackedWidget()
        self.stack.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.setCentralWidget(self.stack)

        #Crear pantalla
        #Auth
        self.inicio = InitialWindow(self)
        self.iniciar_sesion = IniciarSesion(self)
        self.registro = Registro(self)
        self.no_inicio_sesion = NoInicioSesion(self)

        #Especialista
        self.inicio_especialista = InicioEspecialista(self)
        self.perfil_especialista = PerfilEspecialista(self)
        self.cambiar_contrasena = CambiarContraseña(self)
        self.pacientes_especialista = PacientesEspecialista(self)
        self.registrar_paciente = RegistrarPaciente(self)
        self.generar_codigo = GenerarCodigoPaciente(self)
        self.progreso_individual = ProgresoIndividual(self)
        self.publicar_nota_paciente = PublicarNota(self)

        #Paciente
        self.inicio_paciente = InicioPaciente(self)
        self.perfil_paciente = PerfilPaciente(self)
        self.ajustes_paciente = Ajustes(self)
        self.mi_progreso_paciente = MiProgreso(self)
        self.pantalla_pueblo = PantallaPueblo(self)
        self.pantalla_biblioteca = BibliotecaWidget(self)
        self.pantalla_biblioteca.minijuego_finalizado.connect(self.show_pantalla_fin_rehabilitacion)
        self.pantalla_fin_rehabilitacion = PantallaFinRehabilitacion(self)
        self.inicio_huerto = BibliotecaCompletada(self)
        self.pantalla_fin_rehabilitacion.salir_del_edificio.connect(self._on_fin_salir_del_edificio)
        self.pantalla_fin_rehabilitacion.volver_a_jugar.connect(self._on_fin_volver_a_jugar)

        #Añadir al stack
        self.stack.addWidget(self.inicio)
        self.stack.addWidget(self.iniciar_sesion)
        self.stack.addWidget(self.registro)
        self.stack.addWidget(self.no_inicio_sesion)

        self.stack.addWidget(self.inicio_especialista)
        self.stack.addWidget(self.perfil_especialista)  
        self.stack.addWidget(self.cambiar_contrasena)
        self.stack.addWidget(self.pacientes_especialista)
        self.stack.addWidget(self.registrar_paciente)
        self.stack.addWidget(self.generar_codigo)
        self.stack.addWidget(self.progreso_individual)
        self.stack.addWidget(self.publicar_nota_paciente)

        self.stack.addWidget(self.inicio_paciente)
        self.stack.addWidget(self.perfil_paciente)
        self.stack.addWidget(self.ajustes_paciente)
        self.stack.addWidget(self.mi_progreso_paciente)
        self.stack.addWidget(self.pantalla_pueblo)
        self.stack.addWidget(self.pantalla_biblioteca)
        self.stack.addWidget(self.pantalla_fin_rehabilitacion)
        self.stack.addWidget(self.inicio_huerto)

        set_auth_expired_handler(self.show_no_inicio_sesion)

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
    
    def _sync_patient_name(self):
        vistas = [
            self.inicio_paciente,
            self.perfil_paciente,
            self.cambiar_contrasena,
            self.ajustes_paciente,
            self.mi_progreso_paciente,
        ]
        for vista in vistas:
            if hasattr(vista, "set_nombre_paciente"):
                vista.set_nombre_paciente(self.paciente_nombre)

        if hasattr(self.perfil_paciente, "set_datos_paciente"):
            self.perfil_paciente.set_datos_paciente(
                username=self.paciente_username,
                dni=self.paciente_dni,
                nombre=self.paciente_nombre,
                email=self.paciente_email,
                fecha_nacimiento=self.birth_date,
            )

    def set_specialist_session(self, token: str, refresh_token: str = "", nombre: str = "", username: str = "", email: str = "", clinic_id=None):
        self.auth_token = token
        self.refresh_token = refresh_token or ""
        self.user_rol = 'especialista'
        self.especialista_nombre = (nombre or "").strip()
        self.especialista_username = username or ""
        self.especialista_email = email or ""
        self.clinic_id = clinic_id
        self._sync_specialist_name()
    
    def set_patient_session(self, token: str, refresh_token: str = "", username: str = "", nombre: str = "", dni: str = "", email: str = "", birth_date: str = "", paciente_id=None):
        self.auth_token = token
        self.refresh_token = refresh_token or ""
        self.user_rol = 'paciente'
        self.paciente_username = username or ""
        self.paciente_nombre = (nombre or "").strip()
        self.paciente_dni = dni or ""
        self.paciente_email = email or ""
        self.birth_date = birth_date or ""
        self.paciente_id = paciente_id
        self._sync_patient_name()

    def clear_specialist_session(self):
        self.auth_token = None
        self.refresh_token = None
        self.user_rol = None
        self.especialista_nombre = ""
        self.especialista_username = ""
        self.especialista_email = ""
        self.clinic_id = None
        self._sync_specialist_name()
    
    def clear_patient_session(self):
        self.auth_token = None
        self.refresh_token = None
        self.user_rol = None
        self.paciente_username = ""
        self.paciente_nombre = ""
        self.paciente_dni = ""
        self.paciente_email = ""
        self.birth_date = ""
        self.paciente_id = None
        self.rehabilitacion_activa_id = None
        self.rehabilitacion_activa_detalle = {}
        self._detener_eye_tracking()
        self._sync_patient_name()

    def logout_specialist_session(self):
        if self.refresh_token:
            logout_api(self.refresh_token, self.auth_token)
        self.show_inicio()
    
    def logout_patient_session(self):
        if self.refresh_token:
            logout_api(self.refresh_token, self.auth_token)
        self.show_inicio()


    def show_inicio(self):
        if self.user_rol == 'especialista':
            self.clear_specialist_session()
        elif self.user_rol == 'paciente':
            self.clear_patient_session()
        self.stack.setCurrentWidget(self.inicio)

    def show_no_inicio_sesion(self):
        if self.user_rol == 'especialista':
            self.clear_specialist_session()
        elif self.user_rol == 'paciente':
            self.clear_patient_session()
        self.stack.setCurrentWidget(self.no_inicio_sesion)

    def show_login(self):
        self.stack.setCurrentWidget(self.iniciar_sesion)

    def show_specialist_login(self):
        self.show_login()

    def show_specialist_registration(self):
        self.stack.setCurrentWidget(self.registro)


    
    def show_inicio_especialista(self):
        self.stack.setCurrentWidget(self.inicio_especialista)
    
    def show_perfil_especialista(self):
        self.stack.setCurrentWidget(self.perfil_especialista)

    def show_cambiar_contrasena(self, force_password_change: bool = False):
        if hasattr(self.cambiar_contrasena, "set_modo_forzado"):
            self.cambiar_contrasena.set_modo_forzado(force_password_change)
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

    #Paciente
    def show_inicio_paciente(self):
        self.stack.setCurrentWidget(self.inicio_paciente)

    def show_perfil_paciente(self):
        self.stack.setCurrentWidget(self.perfil_paciente)

    def show_ajustes_paciente(self):
        self.stack.setCurrentWidget(self.ajustes_paciente)

    def show_mi_progreso_paciente(self):
        if hasattr(self.mi_progreso_paciente, "_cargar_datos_reales"):
            self.mi_progreso_paciente._cargar_datos_reales()
        self.stack.setCurrentWidget(self.mi_progreso_paciente)


    def show_perfil_actual(self):
        if self.user_rol == 'paciente':
            self.show_perfil_paciente()
        else:
            self.show_perfil_especialista()

    def logout_current_session(self):
        if self.user_rol == 'paciente':
            self.logout_patient_session()
        else:
            self.logout_specialist_session()


    #Juego
    def show_pantalla_pueblo(self):
        # Detener eye tracking cuando vuelve al pueblo
        self._detener_eye_tracking()
        self.stack.setCurrentWidget(self.pantalla_pueblo)

    def set_rehabilitacion_activa(self, id_rehabilitacion: int | None):
        self.rehabilitacion_activa_id = id_rehabilitacion

    def continuar_rehabilitacion(self, id_rehabilitacion: int):
        if not self.auth_token:
            return

        status_code, data = obtener_detalle_rehabilitacion(id_rehabilitacion, self.auth_token)
        if status_code != 200 or not isinstance(data, dict):
            return

        self.rehabilitacion_activa_id = id_rehabilitacion
        self.rehabilitacion_activa_detalle = data

        puntuacion_biblioteca = self._puntuacion_biblioteca_en_rehabilitacion_activa()
        if puntuacion_biblioteca >= 2:
            self.show_inicio_huerto(puntuacion_biblioteca)
            return

        self.stack.setCurrentWidget(self.pantalla_pueblo)

    def show_biblioteca(self):
        if hasattr(self.pantalla_biblioteca, "reiniciar_partida"):
            self.pantalla_biblioteca.reiniciar_partida()
        
        # Iniciar eye tracking para controlar el ratón con la mirada
        self._iniciar_eye_tracking()
        
        self.stack.setCurrentWidget(self.pantalla_biblioteca)

    def show_inicio_huerto(self, puntuacion_biblioteca: int = 0):
        # Detener eye tracking cuando avanza a la siguiente zona
        self._detener_eye_tracking()
        
        if hasattr(self.inicio_huerto, "set_puntuacion_biblioteca"):
            self.inicio_huerto.set_puntuacion_biblioteca(puntuacion_biblioteca)
        self.stack.setCurrentWidget(self.inicio_huerto)

    def _puntuacion_biblioteca_en_rehabilitacion_activa(self) -> int:
        detalle = self.rehabilitacion_activa_detalle
        if not isinstance(detalle, dict):
            return 0

        edificios = detalle.get("edificios", [])
        if not isinstance(edificios, list):
            return 0

        for edificio in edificios:
            if not isinstance(edificio, dict):
                continue
            if str(edificio.get("nombre", "")).strip().lower() != "biblioteca":
                continue
            try:
                return int(edificio.get("puntuacion", 0))
            except (TypeError, ValueError):
                return 0
        return 0

    def _on_fin_salir_del_edificio(self):
        if hasattr(self.pantalla_fin_rehabilitacion, "ha_superado") and self.pantalla_fin_rehabilitacion.ha_superado():
            puntos = self.pantalla_fin_rehabilitacion.puntos_finales() if hasattr(self.pantalla_fin_rehabilitacion, "puntos_finales") else 0
            self.show_inicio_huerto(puntos)
            return
        self.show_pantalla_pueblo()

    def _on_fin_volver_a_jugar(self):
        if hasattr(self.pantalla_fin_rehabilitacion, "ha_superado") and self.pantalla_fin_rehabilitacion.ha_superado():
            puntos = self.pantalla_fin_rehabilitacion.puntos_finales() if hasattr(self.pantalla_fin_rehabilitacion, "puntos_finales") else 0
            self.show_inicio_huerto(puntos)
            return
        self.show_biblioteca()

    def show_pantalla_fin_rehabilitacion(self, libros_colocados: int):
        # Detener eye tracking cuando termina la rehabilitación
        self._detener_eye_tracking()
        
        # Biblioteca puntua de 0 a 3, que coincide con puntuacionEdificio.
        if libros_colocados <= 1:
            puntos_minijuego = 0
        elif libros_colocados <= 4:
            puntos_minijuego = 1
        elif libros_colocados <= 7:
            puntos_minijuego = 2
        else:
            puntos_minijuego = 3

        if self.auth_token:
            registrar_puntuacion_minijuego(
                edificio="biblioteca",
                puntuacion=puntos_minijuego,
                token=self.auth_token,
                id_rehabilitacion=self.rehabilitacion_activa_id,
            )

        if hasattr(self.pantalla_fin_rehabilitacion, "set_resultado"):
            self.pantalla_fin_rehabilitacion.set_resultado(libros_colocados)
        self.stack.setCurrentWidget(self.pantalla_fin_rehabilitacion)

    # Eye Tracking methods
    def _iniciar_eye_tracking(self, widget_area=None):
        """Inicia el eye tracking during una rehabilitación."""
        if self.paciente_id is None:
            return False
        
        # Obtener sensibilidad guardada
        configuracion = cargar_user_settings(self.paciente_id)
        sensibilidad = configuracion.get("sensibilidad", 1.0) if configuracion else 1.0
        
        self.eye_tracking_controller = EyeTrackingController(
            sensibilidad=sensibilidad,
            paciente_id=self.paciente_id
        )
        
        if self.eye_tracking_controller.iniciar(widget_area):
            return True
        else:
            self.eye_tracking_controller = None
            return False
    
    def _detener_eye_tracking(self):
        """Detiene el eye tracking."""
        if self.eye_tracking_controller is not None:
            self.eye_tracking_controller.detector.establecer_matriz_calibracion(None)
            self.eye_tracking_controller.detector.limpiar_calibracion()
            self.eye_tracking_controller.detener()
            self.eye_tracking_controller = None
