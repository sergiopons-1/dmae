from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel


class Puntaje(QLabel):
    def __init__(self, parent=None, color_fondo: str = "#0E4C66", color_texto: str = "white"):
        super().__init__(parent)
        self._color_fondo = color_fondo
        self._color_texto = color_texto
        self._valor = 0

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.hide()

    def set_puntaje(self, valor: int):
        try:
            self._valor = max(0, int(valor))
        except (TypeError, ValueError):
            self._valor = 0

        if self._valor <= 0:
            self.hide()
            return

        self.setText(f"+{self._valor}")
        self.show()

    def set_diametro(self, diametro: int):
        diametro = max(1, int(diametro))
        radio = diametro // 2
        font_size = max(20, radio // 1.5)

        self.setFixedSize(diametro, diametro)
        self.setStyleSheet(
            f"background-color: {self._color_fondo}; color: {self._color_texto}; "
            f"font-size: {font_size}px; font-weight: 800; border-radius: {radio}px;"
        )