from enum import Enum
import math
import taichi as ti
from PyQt5.QtCore import Qt, QPoint, QRect, QCoreApplication
from PyQt5.QtGui import QColor, QPainter, QMouseEvent, QPen, QPalette, QBrush
from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from figures import Figure, Circle, Curve, Ellipse, Line, Polygon, Rect, Triangle
import simulation

# ti.init(arch=ti.gpu)  # Try to run on GPU


class FigureType(Enum):
    Line = 0
    Curve = 1
    Rectangle = 2
    Triangle = 3
    Circle = 4
    Ellipse = 5
    Polygon = 6
    # Edit = 7
    # Del = 8


MatterType = dict(NoType=0, Fluid=1, Jelly=2, Steel=3, Plastic=4)


# @ti.data_oriented
class Minidraw_controller(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # self.ui = Ui_Minidraw_controller()
        # self.ui.setupUi(self)
        self.dt = 1e-4
        self.frame_dt = 2e-3

        # self.window_h = self.height()
        # self.window_w = self.width()
        self.window_h = 900
        self.window_w = 1200
        self.draw_status = False
        self.current_point = None
        self.usingFEM = False
        self.usingMPM = True

        self.current_line_color = Qt.white
        self.current_line_width = 3
        self.current_figure_type = FigureType.Curve

        self.figure_array = []
        self.figure_array_backup = []
        self.del_figure = []
        self.status_stack = []

        self.p_current_figure = None
        self.isAdding = True
        self.isEdit = False
        self.isDel = False
        self.isDraw = False

        self.add_mesh = False
        self.is_drawing_polygon = False
        self.is_simulating = False
        self.fem_simulation = simulation.FEM()
        self.taichi_simulation = simulation.Simulations(
            self.window_w, self.window_h)

    def point_in_polygon(self, figure, point: QPoint):
        pt_x = point.x()
        pt_y = point.y()
        if isinstance(figure, Rect):
            return pt_x <= max(figure.start_x, figure.end_x) and pt_x >= min(
                figure.start_x, figure.end_x) and pt_y <= max(
                    figure.start_y, figure.end_y) and pt_y >= min(
                        figure.start_y, figure.end_y)
        elif isinstance(figure, Circle):
            radius = abs(figure.start_x - figure.end_x)
            center_x = (figure.start_x + figure.end_x) / 2
            center_y = (figure.start_y + figure.end_y) / 2
            return radius**2 >= (center_x - pt_x)**2 + (center_y - pt_y)**2
        else:
            points = figure.p_point_array
            nums = len(points)
            count = 0
            for i in range(nums):
                x1, y1 = points[i].x(), points[i].y()
                x2, y2 = points[(i + 1) % nums].x(), points[(i + 1) % nums].y()
                if min(y1, y2) < pt_y <= max(y1, y2):
                    x = (pt_y - y1) * (x2 - x1) / (y2 - y1) + x1
                    if x <= pt_x:
                        count += 1
            return count % 2 == 1

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.current_point = event.pos()
            if self.isEdit:
                ind = self.edit_objects_getind()
                self.status_stack.append(['e', ind])
            elif self.isDel:
                # ind=self.del_objects()
                # self.status_stack.append(['d',ind])
                pass
            elif not self.p_current_figure and self.isAdding:
                self.status_stack.append(['a'])
                if self.current_figure_type == FigureType.Line:
                    self.p_current_figure = Line(self.current_point)
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

        if self.isEdit:
            self.edit_objects(self.current_point, event.pos())
            self.current_point = event.pos()
        elif self.draw_status:
            self.current_point = event.pos()
            # self.p_current_figure.draw_dynamic(self.get_painter(),
            #                                    self.current_point)
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.draw_status = False
        if self.isDel:
            ind = self.del_objects()
            self.status_stack.append(['d', ind])
            self.isDel = False
        elif self.isEdit:
            ind = self.edit_objects(self.current_point, event.pos())
            self.current_point = event.pos()
            self.del_figure.append(self.figure_array.pop(ind))
            self.isEdit = False
        elif self.p_current_figure and self.isAdding:
            self.current_point = event.pos()
            self.p_current_figure.set_width(self.current_line_width)
            self.p_current_figure.set_color(self.current_line_color)
            self.p_current_figure.add_point(self.current_point)
            if self.current_figure_type != FigureType.Polygon:
                self.figure_array.append(self.p_current_figure)
                self.p_current_figure = None
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        min_size = min(self.window_h, self.window_w)
        self.window_h = self.window_w = min_size

        painter.setPen(QPen(QColor(0x4FB99F), 4))
        rectBoundary = QRect(self.window_w * 0.04, self.window_h * 0.04 - 3,
                             self.window_w * 0.92 - 6,
                             self.window_h * 0.92 + 3)
        painter.drawRect(rectBoundary)

        pal = self.palette()
        pal.setColor(QPalette.Background, QColor(0x112F41))
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        painter.setPen(QPen(self.current_line_color, self.current_line_width))
        if self.p_current_figure:
            self.p_current_figure.draw_dynamic(painter, self.current_point)

        for figure in self.figure_array:
            painter.setPen(QPen(figure.get_color(), figure.get_width()))
            figure.draw(painter)

        if self.current_figure_type != "k_polygon":
            if self.is_drawing_polygon:
                self.is_drawing_polygon = False
                if self.p_current_figure is not None:
                    self.figure_array.append(self.p_current_figure)
                    self.p_current_figure = None

        if self.usingMPM:
            pos_n = self.taichi_simulation.x.to_numpy()
            matr_n = self.taichi_simulation.material.to_numpy()

            for i in range(self.taichi_simulation.n_particles):
                if matr_n[i] == MatterType['NoType']:
                    continue
                elif matr_n[i] == MatterType['Fluid']:
                    color = Qt.blue
                elif matr_n[i] == MatterType['Jelly']:
                    color = QColor(0xED553B)
                elif matr_n[i] == MatterType['Plastic']:
                    color = Qt.black
                elif matr_n[i] == MatterType['Steel']:
                    color = Qt.white
                painter.setPen(QPen(color, 1))
                painter.setBrush(QBrush(color))
                rectangle = QRect((pos_n[i][0] * self.window_w).astype(int),
                                  (pos_n[i][1] * self.window_h).astype(int), 2,
                                  2)
                painter.drawEllipse(rectangle)

        elif self.usingFEM:
            pos_n = self.fem_simulation.pos.to_numpy()
            node_f2v = self.fem_simulation.f2v.to_numpy()
            matr_n = self.fem_simulation.matr.to_numpy()
            for i in range(self.fem_simulation.NF):
                for j in range(3):
                    a, b = node_f2v[i][j], node_f2v[i][(j + 1) % 3]
                    if matr_n[a] == MatterType['NoType']:
                        break
                    elif matr_n[a] == MatterType['Fluid']:
                        color = Qt.blue
                    elif matr_n[a] == MatterType['Jelly']:
                        color = QColor(0xED553B)
                    elif matr_n[a] == MatterType['Plastic']:
                        color = Qt.black
                    elif matr_n[a] == MatterType['Steel']:
                        color = Qt.white
                    painter.setPen(QPen(color, 1))
                    painter.setBrush(QBrush(color))
                    painter.drawLine(pos_n[a][0] * self.window_w,
                                     pos_n[a][1] * self.window_h,
                                     pos_n[b][0] * self.window_w,
                                     pos_n[b][1] * self.window_h)

    def add_objects(self):
        for i in range(len(self.figure_array)):
            p_figure = self.figure_array[i]
            # has_init_velocity = False

            # 1. wrong type, just ignore it.
            if not isinstance(p_figure,
                              Line) and p_figure.get_color() == Qt.red:
                continue

            # 2. get next figure: if next figure is velocity line, then can set velocity
            p_next_figure = self.figure_array[(i + 1) % len(self.figure_array)]
            if isinstance(p_next_figure,
                          Line) and p_next_figure.get_color() == Qt.red:
                # has_init_velocity = True
                pass

            ptype = None

            # 3. get type of particles according to line color:
            #  black: solid
            #  white: snow
            #  orange: jelly
            #  blue: fluid
            figure_color = p_figure.get_color()
            if figure_color == Qt.black:
                ptype = MatterType['Plastic']
            elif figure_color == Qt.white:
                ptype = MatterType['Steel']
            elif figure_color == QColor(0xED553B):
                ptype = MatterType['Jelly']
            else:
                ptype = MatterType['Fluid']

            # p_points = p_figure.p_point_array
            if self.usingFEM:
                if isinstance(p_figure, Rect):
                    self.fem_simulation.add_object_rectangle(p_figure, ptype)
                elif isinstance(p_figure, Circle):
                    self.fem_simulation.add_object_circle(p_figure, ptype)
                else:
                    self.fem_simulation.add_object_polygon(p_figure, ptype)
            elif self.usingMPM:
                if isinstance(p_figure, Rect):
                    self.taichi_simulation.add_object_rectangle(
                        p_figure, ptype)
                elif isinstance(p_figure, Circle):
                    self.taichi_simulation.add_object_circle(p_figure, ptype)
                else:
                    self.taichi_simulation.add_object_polygon(p_figure, ptype)
                # get object shape and create object
                # if figure type is rectangle
                # if isinstance(p_figure, Rect):
                #     assert len(p_points) == 2
                #     x0 = float(p_points[0].x()) / self.window_w
                #     y0 = float(p_points[0].y()) / self.window_h
                #     x1 = float(p_points[1].x()) / self.window_w
                #     y1 = float(p_points[1].y()) / self.window_h

                #     self.taichi_simulation.add_object_rectangle([x0, y0],
                #                                                 [x1, y1],
                #                                                 figure_color,
                #                                                 800, ptype)

                # # if figure type is polygon, triangle or free-hand
                # elif isinstance(p_figure, Polygon) or isinstance(
                #         p_figure, Triangle) or isinstance(p_figure, Curve):
                #     x0 = float(p_points[0].x()) / self.window_w
                #     y0 = float(p_points[0].y()) / self.window_h
                #     x1 = float(p_points[1].x()) / self.window_w
                #     y1 = float(p_points[1].y()) / self.window_h

                #     self.taichi_simulation.add_object_polygon(
                #         p_figure, figure_color, 800, ptype)

                # # if figure type is circle
                # elif isinstance(p_figure, Circle):
                #     p_points = p_figure.p_point_array
                #     assert len(p_points) == 2
                #     x0 = float(p_points[0].x()) / self.window_w
                #     y0 = float(p_points[0].y()) / self.window_h
                #     x1 = float(p_points[1].x()) / self.window_w
                #     y1 = float(p_points[1].y()) / self.window_h

                #     self.taichi_simulation.add_object_circle([(x0 + x1) / 2,
                #                                               (y0 + y1) / 2],
                #                                              (x1 - x0) / 2,
                #                                              figure_color, 800,
                #                                              ptype)

        # insert figure_array to the end of figure_array_backup, NOTE: no need to clear figure_Array_backup here
        self.figure_array_backup.extend(self.figure_array)

        # the end, clear figure_array
        self.figure_array.clear()

    def del_objects(self):
        for figure in self.figure_array[::-1]:
            if self.point_in_polygon(figure, self.current_point):
                ind = self.figure_array.index(figure)
                self.del_figure.append(figure)
                self.figure_array.remove(figure)
                return ind

    def edit_objects_getind(self):
        for figure in self.figure_array[::-1]:
            if self.point_in_polygon(figure, self.current_point):
                ind = self.figure_array.index(figure)
                return ind

    def edit_objects(self, point_old: QPoint, point_new: QPoint):
        self.figure_array.append(self.figure_array[self.status_stack[-1][1]])
        for points in self.figure_array[-1].p_point_array:
            points.setX(points.x() + point_new.x() - point_old.x())
            points.setY(points.y() + point_new.y() - point_old.y())
            return self.status_stack[-1][1]

    def editing_simulate(self):
        QCoreApplication.processEvents()  # response to new message
        if self.usingMPM:

            self.taichi_simulation.substep()

        elif self.usingFEM:
            self.fem_simulation.init_parameter()
            self.fem_simulation.update_force()
            self.fem_simulation.advance()

            # 3. update frame, draw the particles in the window
        if self.step % int(self.frame_dt / self.dt) == 0:
            self.update()
            self.taichi_simulation.caculate_force()
            self.taichi_simulation.force_setting()
            self.isDraw = True
        self.step += 1

    def pyqtg_draw(self):
        if self.isDraw:
            self.pcmi_consistent.setData(self.x, self.y,
                                         self.taichi_simulation.force_n)

    def simulate(self):
        self.taichi_simulation.reset()
        # 1. create objects and add them to particles
        self.add_objects()

        self.step = 0
        if self.is_simulating:
            self.app = pg.mkQApp("Force Visualization")
            self.win = pg.GraphicsLayoutWidget()
            self.win.show()  ## show widget alone in its own window
            self.win.setWindowTitle('Force Visualization')
            self.view_consistent_scale = self.win.addPlot(
                0, 0, 1, 1, title="Stress of the model", enableMenu=False)
            n = self.taichi_simulation.n_part_grid + 1
            self.x = np.repeat(np.arange(0, n), n).reshape(n, n)
            self.y = np.tile(np.arange(0, n), n).reshape(n, n)
            self.x.sort(axis=0)
            self.y.sort(axis=0)
            edgecolors = None
            antialiasing = True
            cmap = pg.colormap.get('viridis')
            levels = (
                0, 5
            )  # Will be overwritten unless enableAutoLevels is set to False

            # Create image item with consistent colors and an interactive colorbar
            self.pcmi_consistent = pg.PColorMeshItem(edgecolors=edgecolors,
                                                     antialiasing=antialiasing,
                                                     colorMap=cmap,
                                                     levels=levels,
                                                     enableAutoLevels=True)
            self.view_consistent_scale.addItem(self.pcmi_consistent)
            self.bar_static = pg.ColorBarItem(
                label="stress",
                #   interactive=True,
                rounding=0.1)
            self.bar_static.setImageItem([self.pcmi_consistent])
            self.win.addItem(self.bar_static, 0, 1, 1, 1)
            self.timer = QTimer()
            self.timer.start(1)
            # self.timer.timeout.connect(self.pyqtg_draw)

        # 2. start simulation

        while True:
            self.editing_simulate()

    def reset_simulation(self):
        self.is_simulating = False
        self.figure_array.clear()
        self.taichi_simulation.particles.clear()

        self.figure_array = self.figure_array_backup
        self.figure_array_backup.clear()  # clear backup figure array here
        self.update()

    def clear_simulation(self):
        self.is_simulating = False
        self.figure_array.clear()
        self.figure_array_backup.clear()
        self.status_stack.clear()
        self.del_figure.clear()
        self.taichi_simulation.particles.clear()
        self.update()

    def undo(self):
        status = self.status_stack.pop()
        if status[0] == 'd':
            self.figure_array.insert(status[1], self.del_figure.pop())
        elif len(self.figure_array) > 0 and status[0] == 'a':
            self.figure_array.pop()
        elif len(self.figure_array) > 0 and status[0] == 'e':
            self.figure_array.insert(status[1], self.del_figure.pop())
            self.figure_array.pop()
        self.update()

    def clearFigure(self):
        self.figure_array.clear()
        self.status_stack.clear()
        self.del_figure.clear()
        self.update()

    def save_scene(self):
        pix = self.grab()  # get screen shot
        img_name = "temp.png"
        img_path = QFileDialog.getSaveFileName(
            self, "Save Scene", img_name, "Image Files (*.png *.jpg *.bmp)")
        if img_path:
            pix.save(img_path[0])
