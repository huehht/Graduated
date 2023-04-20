from enum import Enum
from typing import List
import taichi as ti
from PyQt5.QtCore import Qt, QPoint, QRect, QCoreApplication
from PyQt5.QtGui import QColor, QPainter, QMouseEvent, QPen, QPalette, QBrush
from PyQt5.QtWidgets import QWidget, QFileDialog

from figures import Figure, Circle, Curve, Ellipse, Line, Polygon, Rect, Triangle

n = 80  #grid resolution (cells)
window_w = 600
window_h = 600
dt = 1e-4
frame_dt = 1e-3
dx = 1 / n
inv_dx = 1 / dx
step = 0  #simulation step
velocity_ratio = 10  # speed = ratio * velocity line length
area_particle_ratio = 0.015  #num of particles = ratio * area


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


@ti.data_oriented
class Simulation:

    def __init__(self) -> None:
        quality = 1  # Use a larger value for higher-res simulations
        self.n_grid = 128 * quality
        self.dx, self.inv_dx = 1 / self.n_grid, float(self.n_grid)
        self.dt = 1e-4 / quality
        self.p_vol, self.p_rho = (self.dx * 0.5)**2, 1
        self.p_mass = self.p_vol * self.p_rho
        E, nu = 5e3, 0.2  # Young's modulus and Poisson's ratio
        self.mu_0, self.lambda_0 = E / (2 * (1 + nu)), E * nu / (
            (1 + nu) * (1 - 2 * nu))  # Lame parameters
        self.grid_v = ti.Vector.field(
            2, dtype=float,
            shape=(self.n_grid, self.n_grid))  # grid node momentum/velocity
        self.grid_m = ti.field(dtype=float,
                               shape=(self.n_grid,
                                      self.n_grid))  # grid node mass
        self.particles = []

    class particle:

        def __init__(self,
                     x,
                     v=[0, 0],
                     C=ti.Matrix.zero(float, 2, 2),
                     F=ti.Matrix([[1, 0], [0, 1]]),
                     material=MatterType.Solid,
                     Jp=1,
                     colour=Qt.red) -> None:

            self.x = x  # position
            self.v = v  # velocity
            self.C = C  # affine velocity field
            self.F = F  # deformation gradient
            self.material = material  # material id
            self.Jp = Jp  # plastic deformation
            self.colour = colour

    @ti.kernel
    def substep(self):
        for i, j in self.grid_m:
            self.grid_v[i, j] = [0, 0]
            self.grid_m[i, j] = 0
        for p in self.particles:  # Particle state update and scatter to grid (P2G)
            base = (p.x * inv_dx - 0.5).cast(int)
            fx = p.x * inv_dx - base.cast(float)
            # Quadratic kernels  [http://mpm.graphics   Eqn. 123, with x=fx, fx-1,fx-2]
            w = [0.5 * (1.5 - fx)**2, 0.75 - (fx - 1)**2, 0.5 * (fx - 0.5)**2]
            # deformation gradient update
            p.F = (ti.Matrix.identity(float, 2) + dt * p.C) @ p.F
            # Hardening coefficient: snow gets harder when compressed
            h = ti.max(0.1, ti.min(5, ti.exp(10 * (1.0 - p.Jp))))
            if material[p] == 1:  # jelly, make it softer
                h = 0.3
            mu, la = self.mu_0 * h, self.lambda_0 * h
            if material[p] == 0:  # liquid
                mu = 0.0
            U, sig, V = ti.svd(p.F)
            J = 1.0
            for d in ti.static(range(2)):
                new_sig = sig[d, d]
                if material[p] == 2:  # Snow
                    new_sig = min(max(sig[d, d], 1 - 2.5e-2),
                                  1 + 4.5e-3)  # Plasticity
                p.Jp *= sig[d, d] / new_sig
                sig[d, d] = new_sig
                J *= new_sig
            if material[p] == 0:
                # Reset deformation gradient to avoid numerical instability
                p.F = ti.Matrix.identity(float, 2) * ti.sqrt(J)
            elif material[p] == 2:
                # Reconstruct elastic deformation gradient after plasticity
                p.F = U @ sig @ V.transpose()
            stress = 2 * mu * (p.F - U @ V.transpose()) @ p.F.transpose(
            ) + ti.Matrix.identity(float, 2) * la * J * (J - 1)
            stress = (-dt * self.p_vol * 4 * inv_dx * inv_dx) * stress
            affine = stress + self.p_mass * p.C
            for i, j in ti.static(ti.ndrange(3, 3)):
                # Loop over 3x3 grid node neighborhood
                offset = ti.Vector([i, j])
                dpos = (offset.cast(float) - fx) * dx
                weight = w[i][0] * w[j][1]
                self.grid_v[base +
                            offset] += self.weight * (self.p_mass * v[p] +
                                                      affine @ dpos)
                self.grid_m[base + offset] += weight * self.p_mass
        for i, j in grid_m:
            if grid_m[i, j] > 0:  # No need for epsilon here
                # Momentum to velocity
                grid_v[i, j] = (1 / grid_m[i, j]) * grid_v[i, j]
                grid_v[i, j] += dt * gravity[None] * 30  # gravity
                dist = attractor_pos[None] - dx * ti.Vector([i, j])
                grid_v[i, j] += \
                    dist / (0.01 + dist.norm()) * attractor_strength[None] * dt * 100
                if i < 3 and grid_v[i, j][0] < 0:
                    grid_v[i, j][0] = 0  # Boundary conditions
                if i > n_grid - 3 and grid_v[i, j][0] > 0:
                    grid_v[i, j][0] = 0
                if j < 3 and grid_v[i, j][1] < 0:
                    grid_v[i, j][1] = 0
                if j > n_grid - 3 and grid_v[i, j][1] > 0:
                    grid_v[i, j][1] = 0
        for p in x:  # grid to particle (G2P)
            base = (x[p] * inv_dx - 0.5).cast(int)
            fx = x[p] * inv_dx - base.cast(float)
            w = [
                0.5 * (1.5 - fx)**2, 0.75 - (fx - 1.0)**2, 0.5 * (fx - 0.5)**2
            ]
            new_v = ti.Vector.zero(float, 2)
            new_C = ti.Matrix.zero(float, 2, 2)
            for i, j in ti.static(ti.ndrange(3, 3)):
                # loop over 3x3 grid node neighborhood
                dpos = ti.Vector([i, j]).cast(float) - fx
                g_v = grid_v[base + ti.Vector([i, j])]
                weight = w[i][0] * w[j][1]
                new_v += weight * g_v
                new_C += 4 * inv_dx * weight * g_v.outer_product(dpos)
            v[p], C[p] = new_v, new_C
            x[p] += dt * v[p]  # advection


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

    def point_in_polygon(points, pt_x, pt_y):
        nums = len(points)
        count = 0
        for i in range(nums):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % nums]
            if min(y1, y2) < pt_y <= max(y1, y2):
                x = (pt_y - y1) * (x2 - x1) / (y2 - y1) + x1
                if x <= pt_x:
                    count += 1
        return count % 2 == 1

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

    def save_scene(self):
        pix = self.grab()  # get screen shot
        img_name = "temp.png"
        img_path = QFileDialog.getSaveFileName(
            self, "Save Scene", img_name, "Image Files (*.png *.jpg *.bmp)")
        if img_path:
            pix.save(img_path[0])
