from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QPoint, QSize, QRect, pyqtSignal, QTimer
from PyQt6.QtGui import QImage, QPixmap, QCursor
 
 
class LibroWidget(QLabel):

    soltado = pyqtSignal(object, QPoint)
 
    BASE_PATH = "assets/images/juego/edificios/biblioteca"
    TAMANO_VISUAL = QSize(84, 56)

    _ARCHIVOS_SELECCIONADOS = {
        "rojo": "libro_rojo_seleccionado.png",
        "azul": "libro_azul_seleccionado.png",
        "verde": "libro_verde_seleccionado_.png",
        "amarillo": "libro_amarillo_seleccionado.png",
    }
 
    def __init__(self, color: str, pos_inicial: QPoint, parent=None):
        super().__init__(parent)
 
        self.color = color                 
        self.pos_inicial = pos_inicial     
        self.colocado = False               
        self._arrastrando = False
        self._movido_en_arrastre = False
        self._modo_click_activo = False
        self._offset = QPoint()            
        self._mostrando_seleccionado = False

        self._timer_seguimiento = QTimer(self)
        self._timer_seguimiento.setInterval(16)
        self._timer_seguimiento.timeout.connect(self._seguir_raton)
 
        # Carga de imágenes
        self._img_normal_base = self._cargar_pixmap_base(
            f"{self.BASE_PATH}/libros/libro_{color}.png"
        )
        self._img_seleccionado_base = self._cargar_pixmap_base(
            f"{self.BASE_PATH}/libros_seleccionados/{self._ARCHIVOS_SELECCIONADOS[color]}"
        )
 
        self.aplicar_escala(1.0)
        self.move(pos_inicial)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setScaledContents(True)
        self.setStyleSheet("border: none; background-color: transparent;")

    def _cargar_pixmap_base(self, ruta: str) -> QPixmap:
        pixmap = QPixmap(ruta)
        return self._recortar_margen_blanco(pixmap)

    def aplicar_escala(self, escala: float):
        ancho = max(int(self.TAMANO_VISUAL.width() * escala), 1)
        alto = max(int(self.TAMANO_VISUAL.height() * escala), 1)
        tamano = QSize(ancho, alto)

        self._img_normal = self._img_normal_base.scaled(
            tamano,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._img_seleccionado = self._img_seleccionado_base.scaled(
            tamano,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setFixedSize(tamano)
        if self._mostrando_seleccionado:
            self.setPixmap(self._img_seleccionado)
        else:
            self.setPixmap(self._img_normal)

    def _recortar_margen_blanco(self, pixmap: QPixmap) -> QPixmap:
        """
        Recorta bordes transparentes o casi blancos para evitar halo blanco.
        """
        image = pixmap.toImage().convertToFormat(QImage.Format.Format_ARGB32)
        w, h = image.width(), image.height()

        min_x, min_y = w, h
        max_x, max_y = -1, -1

        for y in range(h):
            for x in range(w):
                px = image.pixelColor(x, y)
                if self._pixel_util(px):
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)

        if max_x < min_x or max_y < min_y:
            return pixmap

        return pixmap.copy(QRect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1))

    @staticmethod
    def _pixel_util(pixel) -> bool:
        if pixel.alpha() < 10:
            return False
        return not (pixel.red() > 245 and pixel.green() > 245 and pixel.blue() > 245)
 
    def _set_normal(self):
        self._mostrando_seleccionado = False
        self.setPixmap(self._img_normal)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
 
    def _set_seleccionado(self):
        self._mostrando_seleccionado = True
        self.setPixmap(self._img_seleccionado)
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
 
    def marcar_colocado(self):
        self.colocado = True
        self._desactivar_modo_click(restaurar=False)
        self.hide()  
 
    def volver_origen(self):
        self._desactivar_modo_click(restaurar=False)
        parent = self.parentWidget()
        if parent is not None and hasattr(parent, "_escalar_punto"):
            self.move(parent._escalar_punto(self.pos_inicial))
        else:
            self.move(self.pos_inicial)
        self._set_normal()

    def _activar_modo_click(self):
        self._modo_click_activo = True
        self._set_seleccionado()
        self.raise_()
        self._timer_seguimiento.start()

    def _desactivar_modo_click(self, restaurar: bool = True):
        self._modo_click_activo = False
        if self._timer_seguimiento.isActive():
            self._timer_seguimiento.stop()
        if restaurar:
            self._set_normal()

    def _seguir_raton(self):
        if not self._modo_click_activo or self.colocado:
            return
        parent = self.parentWidget()
        if parent is None:
            return
        cursor_local = parent.mapFromGlobal(QCursor.pos())
        self.move(cursor_local - self._offset)
 
    def mousePressEvent(self, event):
        if self.colocado:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            if self._modo_click_activo:
                self._desactivar_modo_click(restaurar=True)
                pos_global = event.globalPosition().toPoint()
                self.soltado.emit(self, pos_global)
                return

            self._arrastrando = True
            self._movido_en_arrastre = False
            self._offset = event.position().toPoint()
            self._set_seleccionado()
            self.raise_()
 
    def mouseMoveEvent(self, event):
        if self._arrastrando:
            self._movido_en_arrastre = True
            nueva_pos = self.mapToParent(
                event.position().toPoint() - self._offset
            )
            self.move(nueva_pos)
 
    def mouseReleaseEvent(self, event):
        if self._arrastrando and event.button() == Qt.MouseButton.LeftButton:
            self._arrastrando = False
            if self._movido_en_arrastre:
                self._set_normal()
                pos_global = self.mapToGlobal(event.position().toPoint())
                self.soltado.emit(self, pos_global)
            else:
                self._activar_modo_click()
 