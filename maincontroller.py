from enum import Enum
from typing import List

from PyQt5.QtCore import Qt, QPoint, QRect, QCoreApplication
from PyQt5.QtGui import QColor, QPainter, QMouseEvent, QPen, QPalette, QBrush
from PyQt5.QtWidgets import QWidget, QFileDialog

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
        self.window_h = self.height()
        self.window_w = self.width()
        min_size = min(self.window_h, self.window_w)
        self.window_h = self.window_w = min_size

        painter.setPen(QPen(QColor(0x4FB99F), 4))
        rectBoundary = QRect(self.window_w * 0.04, self.window_h * 0.04 - 3,
                             self.window_w * 0.92 - 6,
                             self.window_h * 0.92 + 3)
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

    def add_objects(self):
        for i in range(len(self.figure_array)):
            p_figure = self.figure_array[i]
            has_init_velocity = False

            # 1. wrong type, just ignore it.
            if not isinstance(p_figure,
                              Line) and p_figure.get_color() == Qt.red:
                continue

            # 2. get next figure: if next figure is velocity line, then can set velocity
            p_next_figure = self.figure_array[(i + 1) % len(self.figure_array)]
            if isinstance(p_next_figure,
                          Line) and p_next_figure.get_color() == Qt.red:
                has_init_velocity = True

            ptype = None

            # 3. get type of particles according to line color:
            #  black: solid
            #  white: snow
            #  orange: jelly
            #  blue: fluid
            figure_color = p_figure.get_color()
            if figure_color == Qt.black:
                ptype = 'Solid'
            elif figure_color == Qt.white:
                ptype = 'Snow'
            elif figure_color == QColor(0xED553B):
                ptype = 'Jelly'
            else:
                ptype = 'Fluid'

            p_points = p_figure.p_point_array

            # get object shape and create object
            # if figure type is rectangle
            if isinstance(p_figure, Rect):
                assert len(p_points) == 2
                x0 = float(p_points[0].x()) / self.window_w
                y0 = float(p_points[0].y()) / self.window_h
                x1 = float(p_points[1].x()) / self.window_w
                y1 = float(p_points[1].y()) / self.window_h
                if has_init_velocity:
                    velocity_vector = p_next_figure.get_line_vector()
                    taichi_simulation.add_object_rectangle(
                        Vec(x0, y0), Vec(x1, y1), figure_color, 800, ptype,
                        Vec(velocity_vector.x() / velocity_ratio,
                            velocity_vector.y() / velocity_ratio))
                else:
                    taichi_simulation.add_object_rectangle(
                        Vec(x0, y0), Vec(x1, y1), figure_color, 800, ptype)

            # if figure type is polygon, triangle or free-hand
            elif isinstance(p_figure, Polygon) or isinstance(
                    p_figure, Triangle) or isinstance(p_figure, Curve):
                x0 = float(p_points[0].x()) / self.window_w
                y0 = float(p_points[0].y()) / self.window_h
                x1 = float(p_points[1].x()) / self.window_w
                y1 = float(p_points[1].y()) / self.window_h

                if has_init_velocity:
                    velocity_vector = p_next_figure.get_line_vector()
                    taichi_simulation.add_object_polygon(
                        p_figure, figure_color, 800, ptype,
                        Vec(velocity_vector.x() / velocity_ratio,
                            velocity_vector.y() / velocity_ratio))
                else:
                    taichi_simulation.add_object_polygon(
                        p_figure, figure_color, 800, ptype)

            # if figure type is circle
            elif isinstance(p_figure, Circle):
                p_points = p_figure.p_point_array
                assert len(p_points) == 2
                x0 = float(p_points[0].x()) / self.window_w
                y0 = float(p_points[0].y()) / self.window_h
                x1 = float(p_points[1].x()) / self.window_w
                y1 = float(p_points[1].y()) / self.window_h
                if has_init_velocity:
                    velocity_vector = p_next_figure.get_line_vector()
                    taichi_simulation.add_object_circle(
                        Vec((x0 + x1) / 2, (y0 + y1) / 2), (x1 - x0) / 2,
                        figure_color, 800, ptype,
                        Vec(velocity_vector.x() / velocity_ratio,
                            velocity_vector.y() / velocity_ratio))
                else:
                    taichi_simulation.add_object_circle(
                        Vec((x0 + x1) / 2, (y0 + y1) / 2), (x1 - x0) / 2,
                        figure_color, 800, ptype)

        # insert figure_array to the end of figure_array_backup, NOTE: no need to clear figure_Array_backup here
        self.figure_array_backup.extend(self.figure_array)

        # the end, clear figure_array
        self.figure_array.clear()

    def simulate(self):
        # 1. create objects and add them to particles
        self.add_objects()

        # 2. start simulation
        step = 0
        while True:
            QCoreApplication.processEvents()  # response to new message
            if not self.is_simulating:
                break
            taichi_simulation.simulateOnce()

            # 3. update frame, draw the particles in the window
            if step % int(self.frame_dt / self.dt) == 0:
                self.update()
            step += 1

    def reset_simulation(self):
        self.is_simulating = False
        self.figure_array.clear()
        taichi_simulation.particles.clear()

        self.figure_array = self.figure_array_backup
        self.figure_array_backup.clear()  # clear backup figure array here
        self.update()

    def clear_simulation(self):
        self.is_simulating = False
        self.figure_array.clear()
        self.figure_array_backup.clear()
        taichi_simulation.particles.clear()
        self.update()

    def undo(self):
        if len(self.figure_array) > 0:
            self.figure_array.pop()
        self.update()

    def clearFigure(self):
        self.figure_array.clear()
        self.update()

    def set_snow_type(self, type):
        if 1 <= type <= 6:
            self.snow_type = type

    def save_scene(self):
        pix = self.grab()  # get screen shot
        img_name = "temp.png"
        img_path = QFileDialog.getSaveFileName(
            self, "Save Scene", img_name, "Image Files (*.png *.jpg *.bmp)")
        if img_path:
            pix.save(img_path[0])
