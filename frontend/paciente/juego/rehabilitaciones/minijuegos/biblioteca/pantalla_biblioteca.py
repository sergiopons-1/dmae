import random
from PyQt6.QtWidgets import QWidget, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from shared.widgets.juego.biblioteca.libro import LibroWidget
from shared.widgets.juego.biblioteca.estanteria import EstanteriaWidget
 
ESTANTERIAS_CONFIG = [
    ("rojo",     2, QRect(60,  20, 230, 140)),
    ("azul",     2, QRect(310, 20, 230, 140)),
    ("verde",    2, QRect(60,  175, 230, 140)), 
    ("amarillo", 2, QRect(310, 175, 230, 140)),  
]

ESTANTERIAS_VISUALES_CONFIG = {
    "rojo": QRect(72, 34, 206, 100),
    "azul": QRect(272, 34, 206, 100),
    "verde": QRect(72, 178, 206, 88),
    "amarillo": QRect(272, 178, 206, 88),
}

LIBROS_CONFIG = [
    ("rojo",     20 / 580, 300 / 420),
    ("azul",     150 / 580, 300 / 420),
    ("verde",    280 / 580, 300 / 420),
    ("amarillo", 410 / 580, 300 / 420),
    ("rojo",     20 / 580, 352 / 420),
    ("azul",     150 / 580, 352 / 420),
    ("verde",    280 / 580, 352 / 420),
    ("amarillo", 410 / 580, 352 / 420),
]
 
LIBRO_DE_PIE_PATH = "assets/images/juego/edificios/biblioteca/libros_de_pie/libro_{color}_de_pie.png"
 
class GameCanvas(QWidget):

    juego_completado = pyqtSignal(int)   
    fallo_color = pyqtSignal()
 
    CANVAS_W = 580
    CANVAS_H = 420
    MARGEN_ESTANTERIA_IZQ = 0
    MARGEN_ESTANTERIA_DER = 10
    MARGEN_ESTANTERIA_SUP = 0
    MARGEN_ESTANTERIA_INF = 30
    SEPARACION_SLOTS_ESTANTERIA = -80
    ESCALA_LIBRO_DE_PIE = 1
 
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(1, 1)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
 
        self._libros_colocados = 0
        self._total_libros = len(LIBROS_CONFIG)
        self._puntuacion = 0
        self._overlay_completado: QWidget | None = None
        self._escala_actual = 1.0
        self._origen_contenido = QPoint(0, 0)
 
        self._estanterias: list[EstanteriaWidget] = []
        self._libros: list[LibroWidget] = []
        self._libros_de_pie: dict[tuple, QLabel] = {}  
        self._estanterias_por_color: dict[str, EstanteriaWidget] = {}
 
        self._construir_fondo()
        self._construir_estanterias()
        self.reiniciar_partida()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._ajustar_layout()

    def showEvent(self, event):
        super().showEvent(event)
        self._ajustar_layout()
 
    def _construir_fondo(self):
        fondo = QLabel(self)
        fondo.setScaledContents(False)
        pixmap = QPixmap("assets/images/juego/edificios/biblioteca/biblioteca_vacia.png")
        fondo.setPixmap(pixmap)
        fondo.setGeometry(0, 0, self.CANVAS_W, self.CANVAS_H)
        fondo.lower()  
        self._fondo = fondo
 
    def _construir_estanterias(self):
        for color, capacidad, rect in ESTANTERIAS_CONFIG:
            est = EstanteriaWidget(color, capacidad, rect, parent=self)
            est.libro_colocado.connect(self._on_libro_colocado_en_estanteria)
            self._estanterias.append(est)
            self._estanterias_por_color[color] = est
            est.show()
 
    def _posiciones_por_fila(self) -> list[list[QPoint]]:
        filas: dict[float, list[tuple[float, float]]] = {}
        for _, x_rel, y_rel in LIBROS_CONFIG:
            filas.setdefault(y_rel, []).append((x_rel, y_rel))

        return [
            [self._punto_relativo(x_rel, y_rel) for x_rel, y_rel in sorted(filas[y], key=lambda pos: pos[0])]
            for y in sorted(filas)
        ]

    def _punto_relativo(self, x_rel: float, y_rel: float) -> QPoint:
        return QPoint(
            int(x_rel * self.CANVAS_W),
            int(y_rel * self.CANVAS_H),
        )

    def _crear_libro(self, color: str, pos: QPoint):
        libro = LibroWidget(color, pos, parent=self)
        libro.soltado.connect(self._on_libro_soltado)
        self._libros.append(libro)
        libro.show()

    def _construir_libros(self):
        colores = ["rojo", "azul", "verde", "amarillo"]
        random.shuffle(colores)
        colores_inferiores = colores[1:] + colores[:1]

        posiciones_superiores, posiciones_inferiores = self._posiciones_por_fila()

        for color, pos in zip(colores, posiciones_superiores):
            self._crear_libro(color, pos)

        for color, pos in zip(colores_inferiores, posiciones_inferiores):
            self._crear_libro(color, pos)

    def _limpiar_widgets(self, widgets):
        for widget in widgets:
            widget.setParent(None)
            widget.deleteLater()

    def reiniciar_partida(self):
        if self._overlay_completado is not None:
            self._overlay_completado.setParent(None)
            self._overlay_completado.deleteLater()
            self._overlay_completado = None

        self._limpiar_widgets(self._libros)
        self._libros.clear()

        self._limpiar_widgets(self._libros_de_pie.values())
        self._libros_de_pie.clear()

        self._libros_colocados = 0
        self._puntuacion = 0

        for estanteria in self._estanterias:
            estanteria.reset()

        self._construir_libros()
        self._ajustar_layout()

    def _ajustar_layout(self):
        if self.width() <= 0 or self.height() <= 0:
            return

        escala_x = self.width() / self.CANVAS_W
        escala_y = self.height() / self.CANVAS_H
        self._escala_actual = min(escala_x, escala_y)

        ancho = max(int(self.CANVAS_W * self._escala_actual), 1)
        alto = max(int(self.CANVAS_H * self._escala_actual), 1)
        origen_x = (self.width() - ancho) // 2
        origen_y = (self.height() - alto) // 2
        self._origen_contenido = QPoint(origen_x, origen_y)

        if hasattr(self, "_fondo"):
            pixmap = QPixmap("assets/images/juego/edificios/biblioteca/biblioteca_vacia.png")
            self._fondo.setGeometry(origen_x, origen_y, ancho, alto)
            self._fondo.setPixmap(
                pixmap.scaled(
                    ancho,
                    alto,
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

        for color, _, rect in ESTANTERIAS_CONFIG:
            estanteria = self._estanterias_por_color[color]
            estanteria.setGeometry(self._escalar_rect(rect))

        for libro in self._libros:
            if not libro.colocado:
                libro.aplicar_escala(self._escala_actual)
                libro.move(self._escalar_punto(libro.pos_inicial))

        for (color, indice), lbl in self._libros_de_pie.items():
            estanteria = self._estanterias_por_color.get(color)
            if estanteria is None:
                continue
            slot = self._calcular_slot_libro_de_pie(estanteria, indice)
            pixmap = self._cargar_pixmap_libro_de_pie(color, slot.width(), slot.height())
            lbl.setPixmap(pixmap)
            lbl.setFixedSize(pixmap.size())
            x = slot.x() + (slot.width() - pixmap.width()) // 2
            y = slot.y() + slot.height() - pixmap.height()
            lbl.move(x, y)

        if self._overlay_completado is not None:
            ow = min(300, max(int(ancho * 0.55), 220))
            oh = min(200, max(int(alto * 0.45), 160))
            ox = self._origen_contenido.x() + (ancho - ow) // 2
            oy = self._origen_contenido.y() + (alto - oh) // 2
            self._overlay_completado.setGeometry(ox, oy, ow, oh)

    def _escalar_punto(self, punto: QPoint) -> QPoint:
        return QPoint(
            self._origen_contenido.x() + int(punto.x() * self._escala_actual),
            self._origen_contenido.y() + int(punto.y() * self._escala_actual),
        )

    def _escalar_rect(self, rect: QRect) -> QRect:
        return QRect(
            self._origen_contenido.x() + int(rect.x() * self._escala_actual),
            self._origen_contenido.y() + int(rect.y() * self._escala_actual),
            max(int(rect.width() * self._escala_actual), 1),
            max(int(rect.height() * self._escala_actual), 1),
        )

    def _on_libro_soltado(self, libro: LibroWidget, pos_global: QPoint):
        estanteria_bajo_cursor = None

        for est in self._estanterias:
            pos_local = est.mapFromGlobal(pos_global)
            if est.rect().contains(pos_local):
                estanteria_bajo_cursor = est
                break

        if estanteria_bajo_cursor is None:
            libro.volver_origen()
            return

        if estanteria_bajo_cursor.acepta(libro.color):
            self._colocar_libro(libro, estanteria_bajo_cursor)
            return

        if libro.color != estanteria_bajo_cursor.color_esperado:
            self.fallo_color.emit()
            return

        libro.volver_origen()
 
    def _colocar_libro(self, libro: LibroWidget, estanteria: EstanteriaWidget):
        indice_en_estanteria = estanteria.libros_colocados 
        slot_libro_de_pie = self._calcular_slot_libro_de_pie(
            estanteria, indice_en_estanteria
        )
 
        lbl = QLabel(self)
        pixmap = self._cargar_pixmap_libro_de_pie(
            libro.color,
            slot_libro_de_pie.width(),
            slot_libro_de_pie.height(),
        )
        lbl.setPixmap(pixmap)
        lbl.setFixedSize(pixmap.size())
        x = slot_libro_de_pie.x() + (slot_libro_de_pie.width() - pixmap.width()) // 2
        y = slot_libro_de_pie.y() + slot_libro_de_pie.height() - pixmap.height()
        lbl.move(x, y)
        lbl.show()
        lbl.raise_()
 
        key = (libro.color, indice_en_estanteria)
        self._libros_de_pie[key] = lbl
 
        libro.marcar_colocado()
        estanteria.colocar_libro() 
        self._puntuacion += 10
 
    def _on_libro_colocado_en_estanteria(self, color: str):
        self._libros_colocados += 1
        if self._libros_colocados >= self._total_libros:
            self.juego_completado.emit(self._puntuacion)
 
    def _calcular_slot_libro_de_pie(self, estanteria: EstanteriaWidget, indice: int) -> QRect:
        rect_visual = ESTANTERIAS_VISUALES_CONFIG.get(
            estanteria.color_esperado,
            estanteria.geometry(),
        )
        rect_visual = self._escalar_rect(rect_visual)

        huecos = max(estanteria.capacidad - 1, 0)
        ancho_util = (
            rect_visual.width()
            - self.MARGEN_ESTANTERIA_IZQ
            - self.MARGEN_ESTANTERIA_DER
            - huecos * self.SEPARACION_SLOTS_ESTANTERIA
        )
        ancho_slot = max(ancho_util // estanteria.capacidad, 1)
        x = (
            rect_visual.x()
            + self.MARGEN_ESTANTERIA_IZQ
            + indice * (ancho_slot + self.SEPARACION_SLOTS_ESTANTERIA)
        )
        y = rect_visual.y() + self.MARGEN_ESTANTERIA_SUP
        h = rect_visual.height() - self.MARGEN_ESTANTERIA_SUP - self.MARGEN_ESTANTERIA_INF
        return QRect(x, y, ancho_slot, h)

    def _cargar_pixmap_libro_de_pie(self, color: str, max_w: int, max_h: int) -> QPixmap:
        ruta = LIBRO_DE_PIE_PATH.format(color=color)
        original = QPixmap(ruta)
        recortado = self._recortar_margen_blanco(original)
        w_objetivo = max(int(max_w * self.ESCALA_LIBRO_DE_PIE), 1)
        h_objetivo = max(int(max_h * self.ESCALA_LIBRO_DE_PIE), 1)
        return recortado.scaled(
            w_objetivo,
            h_objetivo,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

    def _recortar_margen_blanco(self, pixmap: QPixmap) -> QPixmap:
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
    
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)