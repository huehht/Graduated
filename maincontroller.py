from enum import Enum
import math
import taichi as ti
from PyQt5.QtCore import Qt, QPoint, QRect, QCoreApplication
from PyQt5.QtGui import QColor, QPainter, QMouseEvent, QPen, QPalette, QBrush
from PyQt5.QtWidgets import QWidget, QFileDialog

from figures import Figure, Circle, Curve, Ellipse, Line, Polygon, Rect, Triangle
from scanline import CScanLine


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


class MatterType(Enum):
    Fluid = 0
    Jelly = 1
    Snow = 2
    Solid = 3


@ti.data_oriented
class Simulation:

    @ti.kernel
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
        self.area_particle_ratio = 0.015
        # num of particles = ratio * area
        self.gravity = ti.Vector.field(2, dtype=float, shape=())
        self.gravity[None] = [0, -1]

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
            base = (p.x * self.inv_dx - 0.5).cast(int)
            fx = p.x * self.inv_dx - base.cast(float)
            # Quadratic kernels  [http://mpm.graphics   Eqn. 123, with x=fx, fx-1,fx-2]
            w = [0.5 * (1.5 - fx)**2, 0.75 - (fx - 1)**2, 0.5 * (fx - 0.5)**2]
            # deformation gradient update
            p.F = (ti.Matrix.identity(float, 2) + self.dt * p.C) @ p.F
            # Hardening coefficient: snow gets harder when compressed
            h = ti.max(0.1, ti.min(5, ti.exp(10 * (1.0 - p.Jp))))
            if p.material == 1:  # jelly, make it softer
                h = 0.3
            mu, la = self.mu_0 * h, self.lambda_0 * h
            if p.material == 0:  # liquid
                mu = 0.0
            U, sig, V = ti.svd(p.F)
            J = 1.0
            for d in ti.static(range(2)):
                new_sig = sig[d, d]
                if p.material == 2:  # Snow
                    new_sig = min(max(sig[d, d], 1 - 2.5e-2),
                                  1 + 4.5e-3)  # Plasticity
                p.Jp *= sig[d, d] / new_sig
                sig[d, d] = new_sig
                J *= new_sig
            if p.material == 0:
                # Reset deformation gradient to avoid numerical instability
                p.F = ti.Matrix.identity(float, 2) * ti.sqrt(J)
            elif p.material == 2:
                # Reconstruct elastic deformation gradient after plasticity
                p.F = U @ sig @ V.transpose()
            stress = 2 * mu * (p.F - U @ V.transpose()) @ p.F.transpose(
            ) + ti.Matrix.identity(float, 2) * la * J * (J - 1)
            stress = (-self.dt * self.p_vol * 4 * self.inv_dx *
                      self.inv_dx) * stress
            affine = stress + self.p_mass * p.C
            for i, j in ti.static(ti.ndrange(3, 3)):
                # Loop over 3x3 grid node neighborhood
                offset = ti.Vector([i, j])
                dpos = (offset.cast(float) - fx) * self.dx
                weight = w[i][0] * w[j][1]
                self.grid_v[base +
                            offset] += self.weight * (self.p_mass * p.v +
                                                      affine @ dpos)
                self.grid_m[base + offset] += weight * self.p_mass
        for i, j in self.grid_m:
            if self.grid_m[i, j] > 0:  # No need for epsilon here
                # Momentum to velocity
                self.grid_v[i, j] = (1 / self.grid_m[i, j]) * self.grid_v[i, j]
                self.grid_v[i,
                            j] += self.dt * self.gravity[None] * 30  # gravity
                if i < 3 and self.grid_v[i, j][0] < 0:
                    self.grid_v[i, j][0] = 0  # Boundary conditions
                if i > self.n_grid - 3 and self.grid_v[i, j][0] > 0:
                    self.grid_v[i, j][0] = 0
                if j < 3 and self.grid_v[i, j][1] < 0:
                    self.grid_v[i, j][1] = 0
                if j > self.n_grid - 3 and self.grid_v[i, j][1] > 0:
                    self.grid_v[i, j][1] = 0
        for p in self.particles:  # grid to particle (G2P)
            base = (p.x * self.inv_dx - 0.5).cast(int)
            fx = p.x * self.inv_dx - base.cast(float)
            w = [
                0.5 * (1.5 - fx)**2, 0.75 - (fx - 1.0)**2, 0.5 * (fx - 0.5)**2
            ]
            new_v = ti.Vector.zero(float, 2)
            new_C = ti.Matrix.zero(float, 2, 2)
            for i, j in ti.static(ti.ndrange(3, 3)):
                # loop over 3x3 grid node neighborhood
                dpos = ti.Vector([i, j]).cast(float) - fx
                g_v = self.grid_v[base + ti.Vector([i, j])]
                weight = w[i][0] * w[j][1]
                new_v += weight * g_v
                new_C += 4 * self.inv_dx * weight * g_v.outer_product(dpos)
            p.v, p.C = new_v, new_C
            p.x += self.dt * p.v  # advection

    # Add circle object in scene

    @ti.kernel
    def add_object_circle(self,
                          center,
                          radius,
                          color,
                          num=500,
                          t=MatterType.Solid,
                          velocity=(0.0, 0.0)):
        i = 0
        area = math.pi * (radius * radius) * self.window_w * self.window_h
        num = area * self.area_particle_ratio if area * self.area_particle_ratio > num else num
        while i < num:
            pos = [((ti.random() * 2) - 1) * radius,
                   ((ti.random() * 2) - 1) * radius]
            if pos[0] * pos[0] + pos[1] * pos[1] < radius * radius:
                self.particles.append(
                    self.Particle(x=[pos[0] + center[0], pos[1] + center[1]],
                                  v=velocity,
                                  colour=color,
                                  material=t))
                i += 1

    # Add rectangle object in scene
    @ti.kernel
    def add_object_rectangle(self,
                             v1,
                             v2,
                             color,
                             num=500,
                             t=MatterType.Solid,
                             velocity=(0.0, 0.0)):
        box_min = [min(v1[0], v2[0]), min(v1[1], v2[1])]
        box_max = [max(v1[0], v2[0]), max(v1[1], v2[1])]
        i = 0
        area = (box_max[0] - box_min[0]) * self.window_w * (
            box_max[1] - box_min[1]) * self.window_h
        num = area * self.area_particle_ratio if area * self.area_particle_ratio > num else num
        while i < num:
            pos = [
                ti.random() * (box_max[0] - box_min[0]) + box_min[0],
                ti.random() * (box_max[1] - box_min[1]) + box_min[1]
            ]
            self.particles.append(self.Particle(pos, velocity, color, t))
            i += 1

    # Add polygon & free-hand object in scene
    @ti.kernel
    def add_object_polygon(self,
                           polygon,
                           color,
                           num=500,
                           t='Snow',
                           velocity=(0.0, 0.0)):
        scanline = CScanLine(polygon)  # use scanline method here
        i = 0
        area = scanline.GetRectArea()
        num = area * self.area_particle_ratio if area * self.area_particle_ratio > num else num
        while i < num:
            pos = [ti.random(), ti.random()]
            x0 = pos[0] * self.window_w
            y0 = pos[1] * self.window_h
            if y0 <= scanline.top and y0 >= scanline.bottom and x0 >= scanline.left and x0 <= scanline.right:
                if scanline.mat_inside.get((int(x0), int(y0))):
                    self.particles.append(
                        self.Particle(pos, velocity, color, t))
                    i += 1


class FEM:

    def __init__(self) -> None:
        self.N = 40
        self.dt = 1e-4
        self.dx = 1 / self.N
        self.rho = 4e1
        self.NF = 2 * self.N**2  # number of faces
        self.NV = (self.N + 1)**2  # number of vertices
        self.E, self.nu = 4e4, 0.2  # Young's modulus and Poisson's ratio
        self.mu, self.lam = self.E / 2 / (1 + self.nu), self.E * self.nu / (
            1 + self.nu) / (1 - 2 * self.nu)
        self.gravity = ti.Vector([0, -10])
        self.damping = 12.5
        # self.damping = 20

        self.pos = ti.Vector.field(2, float, self.NV)
        self.vel = ti.Vector.field(2, float, self.NV)
        self.f2v = ti.Vector.field(
            3, int, self.NF)  # ids of three vertices of each face
        self.B = ti.Matrix.field(2, 2, float, self.NF)
        self.W = ti.field(float, self.NF)
        self.phi = ti.field(
            float, self.NF)  # potential energy of each face (Neo-Hookean)
        self.U = ti.field(float, (), needs_grad=True)  # total potential energy
        self.f = ti.Vector.field(2, float, self.NV)

    @ti.kernel
    def update_force(self):
        for i in range(self.NF):
            ia, ib, ic = self.f2v[i]
            a, b, c = self.pos[ia], self.pos[ib], self.pos[ic]

            D_i = ti.Matrix.cols([a - c, b - c])
            F = D_i @ self.B[i]
            F_it = F.inverse().transpose()

            PF = self.mu * (F - F_it) + self.lam * ti.log(
                F.determinant()) * F_it
            H = -self.W[i] * PF @ self.B[i].transpose()

            fa = ti.Vector([H[0, 0], H[1, 0]])
            fb = ti.Vector([H[0, 1], H[1, 1]])
            fc = -fa - fb
            self.f[ia] += fa
            self.f[ib] += fb
            self.f[ic] += fc


class Minidraw_controller(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # self.ui = Ui_Minidraw_controller()
        # self.ui.setupUi(self)

        self.draw_status = False
        self.current_point = None
        self.usingFEM = False

        self.current_line_color = Qt.white
        self.current_line_width = 7
        self.current_figure_type = FigureType.Curve

        self.figure_array = []
        self.figure_array_backup = []
        self.del_figure = []
        self.status_stack = []

        self.p_current_figure = None
        self.isAdding = True
        self.isEdit = False
        self.isDel = False

        self.is_drawing_polygon = False
        self.is_simulating = False
        self.taichi_simulation = Simulation()

    def point_in_polygon(figure, point: QPoint):
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

        if self.isEdit:
            self.edit_objects(self.current_point, event.pos())
            self.current_point = event.pos()
        elif self.draw_status:
            self.current_point = event.pos()
            self.p_current_figure.draw_dynamic(self.get_painter(),
                                               self.current_point)
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
            if self.is_drawing_polygon:
                self.is_drawing_polygon = False
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

                self.taichi_simulation.add_object_rectangle([x0, y0], [x1, y1],
                                                            figure_color, 800,
                                                            ptype)

            # if figure type is polygon, triangle or free-hand
            elif isinstance(p_figure, Polygon) or isinstance(
                    p_figure, Triangle) or isinstance(p_figure, Curve):
                x0 = float(p_points[0].x()) / self.window_w
                y0 = float(p_points[0].y()) / self.window_h
                x1 = float(p_points[1].x()) / self.window_w
                y1 = float(p_points[1].y()) / self.window_h

                self.taichi_simulation.add_object_polygon(
                    p_figure, figure_color, 800, ptype)

            # if figure type is circle
            elif isinstance(p_figure, Circle):
                p_points = p_figure.p_point_array
                assert len(p_points) == 2
                x0 = float(p_points[0].x()) / self.window_w
                y0 = float(p_points[0].y()) / self.window_h
                x1 = float(p_points[1].x()) / self.window_w
                y1 = float(p_points[1].y()) / self.window_h

                self.taichi_simulation.add_object_circle([(x0 + x1) / 2,
                                                          (y0 + y1) / 2],
                                                         (x1 - x0) / 2,
                                                         figure_color, 800,
                                                         ptype)

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

    def simulate(self):
        # 1. create objects and add them to particles
        self.add_objects()

        # 2. start simulation
        step = 0
        while True:
            QCoreApplication.processEvents()  # response to new message
            if not self.is_simulating:
                break
            self.taichi_simulation.substep()

            # 3. update frame, draw the particles in the window
            if step % int(self.frame_dt / self.dt) == 0:
                self.update()
            step += 1

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
