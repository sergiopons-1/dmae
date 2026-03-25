from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QTimer


class Banner(QLabel):
    _STYLES = {
        "success": {
            "background": "#D4EDDA",
            "color": "#155724",
            "border": "#C3E6CB",
        },
        "error": {
            "background": "#F8D7DA",
            "color": "#721C24",
            "border": "#F5C6CB",
        },
        "warning": {
            "background": "#FFF3CD",
            "color": "#856404",
            "border": "#FFEEBA",
        },
        "info": {
            "background": "#D1ECF1",
            "color": "#0C5460",
            "border": "#BEE5EB",
        },
    }

    def __init__(self, parent=None):
        super().__init__("", parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setVisible(False)
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.ocultar)
        self._aplicar_estilo("success")

    def _aplicar_estilo(self, tipo: str):
        estilo = self._STYLES.get(tipo, self._STYLES["info"])
        self.setStyleSheet(
            f"""
            QLabel {{
                background-color: {estilo['background']};
                color: {estilo['color']};
                border: 1px solid {estilo['border']};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
                font-weight: 700;
            }}
            """
        )

    def mostrar(self, mensaje: str, tipo: str = "success", duracion_ms: int = 5000):
        self._hide_timer.stop()
        self._aplicar_estilo(tipo)
        self.setText(mensaje)
        self.setVisible(True)
        if duracion_ms and duracion_ms > 0:
            self._hide_timer.start(duracion_ms)

    def ocultar(self):
        self._hide_timer.stop()
        self.setVisible(False)
        self.clear()