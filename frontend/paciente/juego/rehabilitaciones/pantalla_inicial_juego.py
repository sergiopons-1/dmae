from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QRect
from shared.widgets.buttons import RectanguloTransparente, BackButton


class PantallaPueblo(QWidget):
    def __init__(self, router):
        super().__init__()
        self.router = router
        self._fondo_original = QPixmap("assets/images/juego/inicio_juego.png")
        self._biblioteca_x = 115 / 1440
        self._biblioteca_y = 613 / 1024
        self._biblioteca_w = 408 / 1440
        self._biblioteca_h = 408 / 1024
        self.setStyleSheet("background-color: black;")
        
        self.fondo = QLabel(self)
        self.fondo.setScaledContents(False)
        self.fondo.setStyleSheet("background-color: black;")
        self.fondo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fondo.lower()

        self.btn_biblioteca = RectanguloTransparente(
            self._biblioteca_x,
            self._biblioteca_y,
            self._biblioteca_w,
            self._biblioteca_h,
            self.abrir_biblioteca,
            self,
        )

        self.back_button = BackButton(text="Volver", accion=self.volver, parent=self)
        self.back_button.setFixedWidth(130)
        self.back_button.raise_()
        self._ajustar_fondo()

    def showEvent(self, event):
        super().showEvent(event)
        self._ajustar_fondo()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._ajustar_fondo()

    def _ajustar_fondo(self):
        self.fondo.setGeometry(self.rect())
        if not self._fondo_original.isNull():
            tamano_escalado = self._fondo_original.size()
            tamano_escalado.scale(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
            self.fondo.setPixmap(
                self._fondo_original.scaled(
                    tamano_escalado,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            imagen_rect = QRect(
                (self.width() - tamano_escalado.width()) // 2,
                (self.height() - tamano_escalado.height()) // 2,
                tamano_escalado.width(),
                tamano_escalado.height(),
            )
            self._ajustar_boton_biblioteca(imagen_rect)
            self._ajustar_back_button(imagen_rect)

    def _ajustar_boton_biblioteca(self, imagen_rect: QRect):
        self.btn_biblioteca.setGeometry(
            int(imagen_rect.x() + self._biblioteca_x * imagen_rect.width()),
            int(imagen_rect.y() + self._biblioteca_y * imagen_rect.height()),
            int(self._biblioteca_w * imagen_rect.width()),
            int(self._biblioteca_h * imagen_rect.height()),
        )

    def _ajustar_back_button(self, imagen_rect: QRect):
        margen_x = 20
        margen_y = 20
        self.back_button.move(imagen_rect.x() + margen_x, imagen_rect.y() + margen_y)
        self.back_button.raise_()

    def volver(self):
        self.router.show_mi_progreso_paciente()

    def abrir_biblioteca(self):
        if hasattr(self.router, "show_biblioteca"):
            self.router.show_biblioteca()