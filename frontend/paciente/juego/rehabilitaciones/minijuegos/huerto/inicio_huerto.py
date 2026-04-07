from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QRect
from shared.widgets.buttons import RectanguloTransparente, BackButton
from shared.widgets.juego.puntaje import Puntaje


class BibliotecaCompletada(QWidget):
    def __init__(self, router):
        super().__init__()
        self.router = router
        self._fondo_original = QPixmap("assets/images/juego/biblioteca_completada.png")
        self._huerto_x = 794 / 1440
        self._huerto_y = 616 / 1024
        self._huerto_w = 328 / 1440
        self._huerto_h = 398 / 1024
        # Proporciones de biblioteca tomadas de pantalla_inicial_juego.
        self._biblioteca_x = 115 / 1440
        self._biblioteca_y = 613 / 1024
        self._biblioteca_w = 408 / 1440
        self._biblioteca_h = 408 / 1024
        self._puntuacion_biblioteca = 0
        self.setStyleSheet("background-color: black;")
        
        self.fondo = QLabel(self)
        self.fondo.setScaledContents(False)
        self.fondo.setStyleSheet("background-color: black;")
        self.fondo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fondo.lower()

        self.btn_huerto = RectanguloTransparente(
            self._huerto_x,
            self._huerto_y,
            self._huerto_w,
            self._huerto_h,
            self.abrir_huerto,
            self,
        )

        self.back_button = BackButton(text="Volver", accion=self.volver, parent=self)
        self.back_button.setFixedWidth(130)
        self.back_button.raise_()

        self.badge_puntuacion = Puntaje(self)
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
            self._ajustar_boton_huerto(imagen_rect)
            self._ajustar_back_button(imagen_rect)
            self._ajustar_badge_biblioteca(imagen_rect)

    def _ajustar_boton_huerto(self, imagen_rect: QRect):
        self.btn_huerto.setGeometry(
            int(imagen_rect.x() + self._huerto_x * imagen_rect.width()),
            int(imagen_rect.y() + self._huerto_y * imagen_rect.height()),
            int(self._huerto_w * imagen_rect.width()),
            int(self._huerto_h * imagen_rect.height()),
        )

    def _ajustar_back_button(self, imagen_rect: QRect):
        margen_x = 20
        margen_y = 20
        self.back_button.move(imagen_rect.x() + margen_x, imagen_rect.y() + margen_y)
        self.back_button.raise_()

    def _ajustar_badge_biblioteca(self, imagen_rect: QRect):
        if self._puntuacion_biblioteca <= 0:
            self.badge_puntuacion.hide()
            return

        radio = max(24, int(40 * min(imagen_rect.width() / 1440, imagen_rect.height() / 1024)))
        diametro = radio * 2

        biblioteca_x = int(imagen_rect.x() + self._biblioteca_x * imagen_rect.width())
        biblioteca_y = int(imagen_rect.y() + self._biblioteca_y * imagen_rect.height())
        biblioteca_w = int(self._biblioteca_w * imagen_rect.width())

        cx = biblioteca_x + int(0.96 * biblioteca_w)
        cy = biblioteca_y + int(0.07 * diametro)

        self.badge_puntuacion.set_puntaje(self._puntuacion_biblioteca)
        self.badge_puntuacion.set_diametro(diametro)
        self.badge_puntuacion.move(cx - radio, cy - radio)
        self.badge_puntuacion.show()
        self.badge_puntuacion.raise_()

    def set_puntuacion_biblioteca(self, puntuacion: int):
        try:
            self._puntuacion_biblioteca = max(0, int(puntuacion))
        except (TypeError, ValueError):
            self._puntuacion_biblioteca = 0
        self._ajustar_fondo()

    def volver(self):
        self.router.show_mi_progreso_paciente()

    def abrir_huerto(self):
        if hasattr(self.router, "show_huerto"):
            self.router.show_huerto()
        else:
            pass