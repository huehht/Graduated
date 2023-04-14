from enum import Enum
from typing import List

from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QColor, QPainter, QMouseEvent, QPen, QPalette, QBrush
from PyQt5.QtWidgets import QWidget

from figures import Figure, Circle, Curve, Ellipse, Line, Polygon, Rect, Triangle


class FigureType(Enum):
    Line = 0
    Curve = 1
    Rectangle = 2
    Triangle = 3
    Circle = 4
    Ellipse = 5
    Polygon = 6


class MatterType(Enum):
    Fluid = 0
    Jelly = 1
    Snow = 2
    Solid = 3


class Minidraw_controller(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # self.ui = Ui_Minidraw_controller()
        # self.ui.setupUi(self)

        self.draw_status = False
        self.current_point = None

        self.current_line_color = Qt.white
        self.current_line_width = 7
        self.current_figure_type = FigureType.Curve

        self.figure_array = []
        self.figure_array_backup = []

        self.p_current_figure = None

        self.is_drawing_polygon = False
        self.is_simulating = False

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.current_point = event.pos()
            if not self.p_current_figure:
                if self.current_figure_type == FigureType.Line:
                    self.p_current_figure = Line(self.current_point,
                                                 self.current_line_width,
                                                 self.current_line_color)
                elif self.current_figure_type == FigureType.Curve:
                    self.p_current_figure = Curve(self.current_point)
                elif self.current_figure_type == FigureType.Rectangle:
                    self.p_current_figure = Rect(self.current_point)
                elif self.current_figure_type == FigureType.Triangle:
                    self.p_current_figure = Triangle(self.current_point)
                elif self.current_figure_type == FigureType.Circle:
                    self.p_current_figure = Circle(self.current_point)
                elif self.current_figure_type == FigureType.Ellipse:
                    self.p_current_figure = Ellipse(self.current_point)
                elif self.current_figure_type == FigureType.Polygon:
                    self.p_current_figure = Polygon(self.current_point)
                    self.is_drawing_polygon = True
                self.draw_status = True
        elif event.button() == Qt.RightButton:
            if self.is_drawing_polygon:
                # self.p_current_figure.finalize_polygon()
                self.is_drawing_polygon = False
                self.figure_array.append(self.p_current_figure)
                self.p_current_figure = None
                self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.draw_status:
            self.current_point = event.pos()
            self.p_current_figure.draw_dynamic(self.get_painter(),
                                               self.current_point)
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.current_point = event.pos()
        self.draw_status = False
        if self.p_current_figure:
            self.p_current_figure.set_width(self.current_line_width)
            self.p_current_figure.set_color(self.current_line_color)
            self.p_current_figure.add_point(self.current_point)
            if self.current_figure_type != FigureType.Polygon:
                self.figure_array.append(self.p_current_figure)
                self.p_current_figure = None
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        window_h = self.height()
        window_w = self.width()
        min_size = min(window_h, window_w)
        window_h = window_w = min_size

        painter.setPen(QPen(QColor(0x4FB99F), 4))
        rectBoundary = QRect(window_w * 0.04, window_h * 0.04 - 3,
                             window_w * 0.92 - 6, window_h * 0.92 + 3)
        painter.drawRect(rectBoundary)

        pal = self.palette()
        pal.setColor(QPalette.Background, 0x112F41)
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        painter.setPen(QPen(self.current_line_color, self.current_line_width))
        if self.p_current_figure is not None:
            self.p_current_figure.draw_dynamic(painter, self.current_point)

        for figure in self.figure_array:
            painter.setPen(QPen(figure.get_color(), figure.get_width()))
            figure.draw(painter)

        if self.current_figure_type != "k_polygon":
            if self.is_drawing_ploygon:
                self.is_drawing_ploygon = False
                if self.p_current_figure is not None:
                    self.figure_array.append(self.p_current_figure)
                    self.p_current_figure = None

        for particle in self.taichi_simulation.particles:
            painter.setPen(QPen(particle.c, 1))
            painter.setBrush(QBrush(particle.c))
            rectangle = QRect(particle.x[0] * self.window_w,
                              particle.x[1] * self.window_h, 4, 4)
            painter.drawEllipse(rectangle)
