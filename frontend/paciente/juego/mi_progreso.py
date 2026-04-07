from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from shared.widgets.sidebar import SidebarPaciente
from shared.widgets.text import TextoInicio
from shared.widgets.buttons import PrimaryButton
from shared.widgets.tabla import TablaPacientes
from api_cliente import obtener_mi_progreso, iniciar_rehabilitacion

BG_COLOR = "#FFF7E7"

class MiProgreso(QWidget):
    def __init__(self, router, nombre=""):
        super().__init__()
        self.router = router
        self.nombre_paciente = nombre
        self._datos_progreso = []

        main = QHBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        self.sidebar = SidebarPaciente(nombre=nombre, parent=self)
        self.sidebar.go_logout.connect(self.router.show_inicio)
        main.addWidget(self.sidebar)


        content = QWidget()
        content.setStyleSheet(f"background-color: {BG_COLOR};")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(40, 30, 40, 20)
        content_layout.setSpacing(20)

        self.label = TextoInicio(label="Mi Progreso", tamano=22, negrita=True, upper=True)
        content_layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.iniciar_nueva_rehabilitacion = PrimaryButton(text="Iniciar nueva rehabilitación", 
                                                          tamano=12, accion=self.iniciar_rehabilitacion)
        content_layout.addWidget(self.iniciar_nueva_rehabilitacion, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.tabla_progreso = TablaPacientes(
            columnas=5,
            min_height=420,
            headers=["Número", "Fecha inicio", "Fecha fin", "Estado", "Puntuación"],
        )
        self.tabla_progreso.fila_clickada.connect(self._on_fila_rehabilitacion_click)
        content_layout.addWidget(self.tabla_progreso)

        main.addWidget(content, stretch=1)
        self._actualizar_tabla()

    def _on_fila_rehabilitacion_click(self, fila: dict):
        if not isinstance(fila, dict):
            return

        estado_codigo = str(fila.get("estado_codigo", "")).strip().lower()
        if estado_codigo != "en_curso":
            return

        id_rehabilitacion = fila.get("idRehabilitacion")
        try:
            id_rehabilitacion = int(id_rehabilitacion)
        except (TypeError, ValueError):
            return

        if hasattr(self.router, "continuar_rehabilitacion"):
            self.router.continuar_rehabilitacion(id_rehabilitacion)


    def cargar_datos(self, datos: list):
        """
        Método público para cargar datos desde la API.
        datos: lista de dicts con claves: nombre, apellidos, rehabilitaciones, especialista
        """
        self._datos_progreso = datos
        self._actualizar_tabla()

    def showEvent(self, event):
        super().showEvent(event)
        self._cargar_datos_reales()

    # ── Tabla ─────────────────────────────────────────────────
    def _actualizar_tabla(self):
        if self._datos_progreso:
            datos_ordenados = sorted(
                self._datos_progreso,
                key=lambda item: item.get("Fecha inicio", ""),
            )
            self.tabla_progreso.set_datos(datos_ordenados)
            return

        self.tabla_progreso.set_datos([
            {
                "Número": "-",
                "Fecha inicio": "-",
                "Fecha fin": "-",
                "Estado": "Sin rehabilitaciones registradas",
                "Puntuación": "-",
            }
        ])

    def _cargar_datos_reales(self):
        token = getattr(self.router, "auth_token", None)
        if not token:
            self._datos_progreso = []
            self._actualizar_tabla()
            return

        status_code, data = obtener_mi_progreso(token)
        if status_code == 200 and isinstance(data, dict):
            rehabilitaciones = data.get("rehabilitaciones", [])
            self._datos_progreso = rehabilitaciones if isinstance(rehabilitaciones, list) else []
        else:
            self._datos_progreso = []

        self._actualizar_tabla()



    def iniciar_rehabilitacion(self):
        token = getattr(self.router, "auth_token", None)
        if not token:
            return

        status_code, data = iniciar_rehabilitacion(token)
        if status_code == 201:
            if isinstance(data, dict) and hasattr(self.router, "set_rehabilitacion_activa"):
                self.router.set_rehabilitacion_activa(data.get("idRehabilitacion"))
            self._cargar_datos_reales()
            self.router.show_pantalla_pueblo()