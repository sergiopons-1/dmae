from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from paciente.juego.rehabilitaciones.minijuegos.biblioteca.pantalla_biblioteca import (GameCanvas)
 
class BibliotecaWidget(QWidget):

    minijuego_finalizado = pyqtSignal(int)
    juego_completado = pyqtSignal(int)
 
    TOTAL_LIBROS = 8
 
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #FFF7E7;")  
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self._libros_colocados = 0
        self._overlay_completado = None
        self._minijuego_terminado = False
        self._construir_ui()
 
   
    def _construir_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(12)
 
        layout.addWidget(self._hud_superior())
        layout.addWidget(self._crear_canvas(), stretch=1)
        layout.addWidget(self._hud_inferior())
 
    def _hud_superior(self) -> QWidget:
        contenedor = QWidget()
        contenedor.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Minimum,
        )
        h = QHBoxLayout(contenedor)
        h.setContentsMargins(16, 12, 4, 14)
 
        # Botón salir
        btn_salir = QPushButton("← Salir")
        btn_salir.setFlat(True)
        btn_salir.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        btn_salir.setStyleSheet(
            "color: #1a3a5c; background: transparent; border: none;"
        )
        btn_salir.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_salir.clicked.connect(self._on_salir_pulsado)
 
        # Título instrucción
        titulo = QLabel("COLOCA LOS LIBROS EN LAS ESTANTERÍAS ADECUADAS")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        titulo.setStyleSheet("color: #1a3a5c;")
 
        h.addWidget(btn_salir, stretch=0)
        h.addWidget(titulo, stretch=1)
        h.addSpacing(60)   # equilibra el botón izquierdo
 
        return contenedor
 
    def _crear_canvas(self) -> GameCanvas:
        self._canvas = GameCanvas(self)
        self._canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self._canvas.juego_completado.connect(self._on_juego_completado)
        self._canvas.fallo_color.connect(self._on_fallo_color)
        for est in self._canvas._estanterias:
            est.libro_colocado.connect(self._on_libro_colocado)
        return self._canvas

    def reiniciar_partida(self):
        self._libros_colocados = 0
        self._minijuego_terminado = False
        self._lbl_contador.setText(f"LLEVAS 0 DE {self.TOTAL_LIBROS}")
        if self._overlay_completado is not None:
            self._overlay_completado.setParent(None)
            self._overlay_completado.deleteLater()
            self._overlay_completado = None
        self._canvas.reiniciar_partida()
 
    def _hud_inferior(self) -> QWidget:
        contenedor = QWidget()
        contenedor.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Minimum,
        )
        h = QHBoxLayout(contenedor)
        h.setContentsMargins(0, 12, 0, 14)

        linea = QFrame()
        linea.setFrameShape(QFrame.Shape.HLine)
        linea.setStyleSheet("color: #1a3a5c;")
 
        self._lbl_contador = QLabel(f"LLEVAS 0 DE {self.TOTAL_LIBROS}")
        self._lbl_contador.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_contador.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self._lbl_contador.setStyleSheet("color: #1a3a5c;")
 
        h.addWidget(self._lbl_contador)
 
        wrapper = QWidget()
        v = QVBoxLayout(wrapper)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(2)
        v.addWidget(linea)
        v.addWidget(contenedor)
        return wrapper
 
 
    def _on_libro_colocado(self, color: str):
        self._libros_colocados += 1
        self._lbl_contador.setText(
            f"LLEVAS {self._libros_colocados} DE {self.TOTAL_LIBROS}"
        )
 
    def _on_juego_completado(self, puntuacion: int):
        if self._overlay_completado is None:
            self._mostrar_overlay_completado()
        self.juego_completado.emit(puntuacion)

    def _on_fallo_color(self):
        self._finalizar_minijuego()

    def _on_salir_pulsado(self):
        self._finalizar_minijuego()

    def _finalizar_minijuego(self):
        if self._minijuego_terminado:
            return
        self._minijuego_terminado = True

        if self._overlay_completado is not None:
            self._overlay_completado.setParent(None)
            self._overlay_completado.deleteLater()
            self._overlay_completado = None

        self.minijuego_finalizado.emit(self._libros_colocados)
 
    def _mostrar_overlay_completado(self):
        """
        Muestra el panel '¡MINIJUEGO COMPLETADO!' encima del canvas,
        igual que en el diseño de Figma.
        """
        overlay = QWidget(self._canvas)
        self._overlay_completado = overlay
        overlay.setStyleSheet(
            "background-color: white; border: 2px solid #1a3a5c; border-radius: 8px;"
        )
 
        v = QVBoxLayout(overlay)
        v.setContentsMargins(30, 30, 30, 30)
        v.setSpacing(20)
 
        lbl = QLabel("¡MINIJUEGO\nCOMPLETADO!")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #1a3a5c; border: none;")
 
        btn_continuar = QPushButton("CONTINUAR")
        btn_continuar.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        btn_continuar.setStyleSheet(
            """
            QPushButton {
                background-color: #1a3a5c;
                color: white;
                border-radius: 6px;
                padding: 12px 30px;
            }
            QPushButton:hover {
                background-color: #2a5a8c;
            }
            """
        )
        btn_continuar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_continuar.clicked.connect(self._finalizar_minijuego)
 
        v.addWidget(lbl)
        v.addWidget(btn_continuar, alignment=Qt.AlignmentFlag.AlignCenter)
 
        ow, oh = 300, 200
        ox = (self._canvas.width() - ow) // 2
        oy = (self._canvas.height() - oh) // 2
        overlay.setGeometry(ox, oy, ow, oh)
        overlay.show()
        overlay.raise_()