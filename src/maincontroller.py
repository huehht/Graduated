from enum import Enum
import math
import taichi as ti
from PyQt5.QtCore import Qt, QPoint, QPointF, QRect, QCoreApplication
from PyQt5.QtGui import QColor, QPainter, QPolygonF, QMouseEvent, QPen, QPalette, QBrush, QLinearGradient
from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from figures import Figure, Circle, Curve, Ellipse, Line, Polygon, Rect, Triangle
import simulation
from scanline import CScanLine
import copy
from scipy.ndimage.filters import gaussian_filter

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


MatterType = dict(NoType=0, Fluid=1, Jelly=2, Steel=3, Plastic=4, HSteel=5)


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
        self.window_w = 900
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
        self.endEdit = False

        self.add_mesh = False
        self.is_drawing_polygon = False
        self.is_simulating = False
        self.fem_simulation = simulation.FEM(self.window_w, self.window_h)
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
            radius = abs(figure.start_x - figure.end_x) / 2
            center_x = (figure.start_x + figure.end_x) / 2
            center_y = figure.start_y + radius
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
            # print(self.current_point)
            if self.isEdit:
                ind = self.edit_objects_getind()
                if ind is not None:
                    self.status_stack.append(['e', ind])
                    # pass
                else:
                    self.endEdit = False
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

        if self.isEdit and self.endEdit:
            self.edit_objects(self.current_point, event.pos())
            self.current_point = event.pos()
        elif self.draw_status:
            self.current_point = event.pos()
            # self.p_current_figure.draw_dynamic(self.get_painter(),
            #                                    self.current_point)
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        # print(event.pos())
        self.draw_status = False
        if self.isDel:
            ind = self.del_objects()
            if ind is not None:
                self.status_stack.append(['d', ind])
                self.isDel = False
        elif self.isEdit and self.endEdit:
            self.edit_objects(self.current_point, event.pos())
            self.current_point = event.pos()
            # self.del_figure.append(self.figure_array.pop(ind))
            self.isEdit = False
        elif self.p_current_figure and self.isAdding:
            self.current_point = event.pos()
            self.p_current_figure.set_width(self.current_line_width)
            self.p_current_figure.set_color(self.current_line_color)
            self.p_current_figure.add_point(self.current_point)
            if self.current_figure_type != FigureType.Polygon:
                self.figure_array.append(self.p_current_figure)
                self.p_current_figure = None
        self.endEdit = True
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
            fc_n = self.fem_simulation.force_n.to_numpy()
            max_f = np.linalg.norm(fc_n)
            fc_n = fc_n / max(max_f, 1e-4)
            for i in range(self.fem_simulation.NF):
                for j in range(3):
                    a, b = node_f2v[i][j], node_f2v[i][(j + 1) % 3]
                    if matr_n[a] == MatterType['NoType'] or matr_n[
                            b] == MatterType['NoType']:
                        break
                    elif matr_n[a] == MatterType['Fluid']:
                        color = Qt.blue
                    elif matr_n[a] == MatterType['Jelly']:
                        color = QColor(0xED553B)
                    elif matr_n[a] == MatterType['Plastic']:
                        color = Qt.black
                    elif matr_n[a] == MatterType['HSteel']:
                        color = Qt.green
                    elif matr_n[a] == MatterType['Steel']:
                        color = Qt.white
                    # if self.add_mesh:
                    if True:
                        painter.setPen(QPen(color, 1))
                        painter.setBrush(QBrush(color))
                        painter.drawLine(pos_n[a][0] * self.window_w,
                                         pos_n[a][1] * self.window_h,
                                         pos_n[b][0] * self.window_w,
                                         pos_n[b][1] * self.window_h)
                # print(self.add_mesh)
                # if not self.add_mesh:
                if False:
                    a, b, c = node_f2v[i][0], node_f2v[i][1], node_f2v[i][2]
                    if matr_n[a] == MatterType['NoType'] or matr_n[
                            b] == MatterType['NoType'] or matr_n[
                                c] == MatterType['NoType']:
                        break
                    grad = QLinearGradient(pos_n[a][0] * self.window_w,
                                           pos_n[a][1] * self.window_h,
                                           pos_n[c][0] * self.window_w,
                                           pos_n[c][1] * self.window_h)
                    # colors = [(0, 0, 0), (8, 69, 99), (57, 174, 156),
                    #           (222, 251, 123), (239, 255, 190),
                    #           (255, 255, 255)]
                    colorx = [0, 8, 57, 222, 239, 255]
                    colory = [0, 69, 174, 251, 255, 255]
                    colorz = [0, 99, 156, 123, 190, 255]
                    x = [0, 0.2, 0.4, 0.6, 0.8, 1]
                    tempcolorax = np.interp(fc_n[a], x, colorx)
                    tempcoloray = np.interp(fc_n[a], x, colory)
                    tempcoloraz = np.interp(fc_n[a], x, colorz)
                    tempcolorcx = np.interp(fc_n[c], x, colorx)
                    tempcolorcy = np.interp(fc_n[c], x, colory)
                    tempcolorcz = np.interp(fc_n[c], x, colorz)
                    # print(tempcolorax, tempcoloray, tempcoloraz)
                    # print(tempcolorcx, tempcolorcy, tempcolorcz)
                    grad.setColorAt(
                        0, QColor(tempcolorax, tempcoloray, tempcoloraz))
                    # grad.setColorAt(0.2, QColor(8, 69, 99))
                    # grad.setColorAt(0.4, QColor(57, 174, 156))
                    # grad.setColorAt(0.6, QColor(222, 251, 123))
                    # grad.setColorAt(0.8, QColor(239, 255, 190))
                    grad.setColorAt(
                        1, QColor(tempcolorcx, tempcolorcy, tempcolorcz))
                    painter.setBrush(QBrush(grad))
                    painter.drawPolygon(
                        QPolygonF([
                            QPointF(pos_n[a][0] * self.window_w,
                                    pos_n[a][1] * self.window_h),
                            QPointF(pos_n[b][0] * self.window_w,
                                    pos_n[b][1] * self.window_h),
                            QPointF(pos_n[c][0] * self.window_w,
                                    pos_n[c][1] * self.window_h)
                        ]))

    def setting_4sets(self):
        top = 0
        bottom = self.window_h
        left = self.window_w
        right = 0
        for i in range(len(self.figure_array)):
            p_figure = self.figure_array[i]
            if isinstance(p_figure, Line):
                continue
            if isinstance(p_figure, Rect):
                top = max(p_figure.start_y, p_figure.end_y, top)
                bottom = min(p_figure.start_y, p_figure.end_y, bottom)
                left = min(p_figure.start_x, p_figure.end_x, left)
                right = max(p_figure.start_x, p_figure.end_x, right)
            elif isinstance(p_figure, Circle):
                top = max(p_figure.start_y, p_figure.end_y, top)
                bottom = min(p_figure.start_y, p_figure.end_y, bottom)
                left = min(p_figure.start_x, p_figure.end_x, left)
                right = max(p_figure.start_x, p_figure.end_x, right)
            else:
                csl = CScanLine(p_figure)
                top = max(csl.top, top)
                bottom = min(csl.bottom, bottom)
                left = min(csl.left, left)
                right = max(csl.right, right)
        self.fem_simulation.init_pos(top, bottom, left, right)

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
                v_x = p_next_figure.get_line_vector().x()
                v_y = p_next_figure.get_line_vector().y()

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
                vel_ratio = 10
                if isinstance(p_figure, Rect):
                    if has_init_velocity:
                        self.fem_simulation.add_object_rectangle(
                            p_figure, ptype, v_x / vel_ratio, v_y / vel_ratio)
                    else:
                        self.fem_simulation.add_object_rectangle(
                            p_figure, ptype)
                elif isinstance(p_figure, Circle):
                    if has_init_velocity:
                        self.fem_simulation.add_object_circle(
                            p_figure, ptype, v_x / vel_ratio, v_y / vel_ratio)
                    else:
                        self.fem_simulation.add_object_circle(p_figure, ptype)
                else:
                    if has_init_velocity:
                        self.fem_simulation.add_object_polygon(
                            p_figure, ptype, v_x / vel_ratio, v_y / vel_ratio)
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
        # print(self.current_point)
        # print(self.status_stack)
        for figure in self.figure_array[::-1]:
            if self.point_in_polygon(figure, self.current_point):
                ind = self.figure_array.index(figure)
                self.del_figure.append(figure)
                # print(self.del_figure)
                self.figure_array.remove(figure)
                return ind

    def edit_objects_getind(self):
        # print(self.current_point)
        for figure in self.figure_array[::-1]:
            if self.point_in_polygon(figure, self.current_point):
                ind = self.figure_array.index(figure)
                if isinstance(figure, Rect):
                    self.del_figure.append(Rect(QPoint(), orig=figure))
                elif isinstance(figure, Curve):
                    self.del_figure.append(Curve(QPoint(), orig=figure))
                elif isinstance(figure, Circle):
                    self.del_figure.append(Circle(QPoint(), orig=figure))
                # print(self.del_figure)
                self.figure_array.append(self.figure_array[ind])
                self.figure_array.pop(ind)
                return ind

    def edit_objects(self, point_old: QPoint, point_new: QPoint):
        # print(self.status_stack)
        # self.figure_array.append(self.figure_array[self.status_stack[-1][1]])
        for points in self.figure_array[-1].p_point_array:
            points.setX(points.x() + point_new.x() - point_old.x())
            points.setY(points.y() + point_new.y() - point_old.y())

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
            if self.usingMPM:
                self.taichi_simulation.caculate_force()
                self.taichi_simulation.force_setting()
            elif self.usingFEM:
                self.fem_simulation.caculate_f()
            self.isDraw = True
        self.step += 1

    def pyqtg_draw(self):
        if self.isDraw:
            if self.usingMPM:
                z = self.taichi_simulation.force_n
            elif self.usingFEM:
                z = self.fem_simulation.force_n.to_numpy().reshape(
                    self.fem_simulation.N + 1, self.fem_simulation.N + 1)
                z = np.flip(z, 1)
                z = gaussian_filter(z, sigma=1)
                # print(z)
            self.pcmi_consistent.setData(self.x, self.y, z)

    def simulate(self):
        self.taichi_simulation.reset()
        # 1. create objects and add them to particles
        self.setting_4sets()
        self.add_objects()

        self.step = 0
        if self.is_simulating:
            self.app = pg.mkQApp("Force Visualization")
            self.win = pg.GraphicsLayoutWidget()
            self.win.show()  ## show widget alone in its own window
            self.win.setWindowTitle('Force Visualization')
            self.view_consistent_scale = self.win.addPlot(
                0, 0, 1, 1, title="Stress of the model", enableMenu=False)
            if self.usingMPM:
                n = self.taichi_simulation.n_part_grid + 1
            elif self.usingFEM:
                n = self.fem_simulation.N + 2
            self.x = np.repeat(np.arange(0, n), n).reshape(n, n)
            self.y = np.tile(np.arange(0, n), n).reshape(n, n)
            self.x.sort(axis=0)
            self.y.sort(axis=0)
            edgecolors = None
            antialiasing = True
            # cmap = pg.colormap.get('viridis')
            levels = (
                0, 5
            )  # Will be overwritten unless enableAutoLevels is set to False
            colors = [(0, 0, 0), (8, 69, 99), (57, 174, 156), (222, 251, 123),
                      (239, 255, 190), (255, 255, 255)]
            cmap = pg.ColorMap(pos=np.linspace(0.0, 1, 6), color=colors)
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
            self.timer.timeout.connect(self.pyqtg_draw)

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
        if self.status_stack:
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
