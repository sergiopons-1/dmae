from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QRect
 
 
class EstanteriaWidget(QWidget):

    libro_colocado = pyqtSignal(str) 
 
    def __init__(self, color_esperado: str, capacidad: int = 2,
                 rect: QRect = None, parent=None):
        super().__init__(parent)
 
        self.color_esperado = color_esperado
        self.capacidad = capacidad
        self.libros_colocados = 0
        self._llena = False
 
        if rect:
            self.setGeometry(rect)
 
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background: transparent;")
 
    def acepta(self, color: str) -> bool:
        return (
            color == self.color_esperado
            and self.libros_colocados < self.capacidad
            and not self._llena
        )
 
    def colocar_libro(self):
        self.libros_colocados += 1
        if self.libros_colocados >= self.capacidad:
            self._llena = True
        self.libro_colocado.emit(self.color_esperado)

    def reset(self):
        self.libros_colocados = 0
        self._llena = False
