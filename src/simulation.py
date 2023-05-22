from enum import Enum
import math
import taichi as ti
import numpy as np
import random
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from PyQt5.QtCore import Qt, QPoint, QRect, QCoreApplication
from PyQt5.QtGui import QColor, QPainter, QMouseEvent, QPen, QPalette, QBrush
from PyQt5.QtWidgets import QWidget, QFileDialog
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from figures import Figure, Circle, Curve, Ellipse, Line, Polygon, Rect, Triangle
from scanline import CScanLine

ti.init(arch=ti.gpu)  # Try to run on GPU


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


@ti.data_oriented
class Simulations:

    # @ti.kernel
    def __init__(self, w, h) -> None:
        quality = 1  # Use a larger value for higher-res simulations
        self.n_grid = 128 * quality
        self.n_part_grid = 8 * quality
        self.n_particles = 8 * 8 * 50 * quality**2
        self.grid_particle_ratio = 50
        self.dx, self.inv_dx = 1 / self.n_grid, float(self.n_grid)
        # self.n_p2gs = self.n_particles / self.grid_particle_ratio
        self.n_p2gs = 8 * 8 * quality**2
        self.dt = 1e-4 / quality
        self.p_vol, self.p_rho = (self.dx * 0.5)**2, 1
        self.p_mass = self.p_vol * self.p_rho
        E, nu = 5e3, 0.2  # Young's modulus and Poisson's ratio
        self.mu_0 = ti.field(ti.f32, shape=())
        self.lambda_0 = ti.field(ti.f32, shape=())
        self.mu_0[None], self.lambda_0[None] = E / (2 * (1 + nu)), E * nu / (
            (1 + nu) * (1 - 2 * nu))  # Lame parameters
        self.grid_v = ti.Vector.field(
            2, dtype=float,
            shape=(self.n_grid, self.n_grid))  # grid node momentum/velocity
        self.grid_m = ti.field(dtype=float,
                               shape=(self.n_grid,
                                      self.n_grid))  # grid node mass
        # self.particles = []
        # self.area_particle_ratio = 0.015
        # num of particles = ratio * area
        self.gravity = ti.Vector.field(2, dtype=float, shape=())
        self.gravity[None] = [0, 1]
        self.window_w = w
        self.window_h = h
        self.x = ti.Vector.field(2,
                                 dtype=float,
                                 shape=self.n_particles,
                                 needs_grad=True)  # position
        self.v = ti.Vector.field(2,
                                 dtype=float,
                                 shape=self.n_particles,
                                 needs_grad=True)  # velocity
        self.accl = ti.Vector.field(2, dtype=float, shape=self.n_particles)
        self.z = ti.Vector.field(2, dtype=float, shape=self.n_p2gs)
        self.force_z = ti.field(dtype=float, shape=self.n_p2gs)
        # self.stress = ti.Vector.field(2,
        #                               2,
        #                               dtype=float,
        #                               shape=self.n_particles)  # stress
        self.C = ti.Matrix.field(
            2, 2, dtype=float, shape=self.n_particles)  # affine velocity field
        self.F = ti.Matrix.field(
            2, 2, dtype=float, shape=self.n_particles)  # deformation gradient
        self.material = ti.field(dtype=int,
                                 shape=self.n_particles)  # material id
        self.Jp = ti.field(dtype=float,
                           shape=self.n_particles)  # plastic deformation

    @ti.kernel
    def reset(self):
        group_size = self.grid_particle_ratio
        for i in range(self.n_particles):
            self.x[i] = [
                ti.random() / self.n_part_grid +
                ((i // group_size) % self.n_part_grid) / self.n_part_grid,
                ti.random() / self.n_part_grid +
                ((i // group_size) // self.n_part_grid) / self.n_part_grid
            ]
            # self.material[i] = MatterType['NoType']
            self.material[i] = MatterType['Fluid']
            self.v[i] = [0, 0]
            self.F[i] = ti.Matrix([[1, 0], [0, 1]])
            self.Jp[i] = 1
            self.C[i] = ti.Matrix.zero(float, 2, 2)
            self.accl[i] = [0, 0]

    @ti.func
    def reset_mu_lam(self, E: ti.f32, nu: ti.f32):
        # self.mu_0, self.lambda_0 = E / (2 * (1 + nu)), E * nu / (
        #     (1 + nu) * (1 - 2 * nu))  # Lame parameters
        self.mu_0[None] = 1
        self.lambda_0[None] = 1

    @ti.kernel
    def substep(self):
        for i, j in self.grid_m:
            self.grid_v[i, j] = [0, 0]
            self.grid_m[i, j] = 0
        for p in self.x:  # Particle state update and scatter to grid (P2G)
            base = (self.x[p] * self.inv_dx - 0.5).cast(int)
            fx = self.x[p] * self.inv_dx - base.cast(float)
            # Quadratic kernels  [http://mpm.graphics   Eqn. 123, with x=fx, fx-1,fx-2]
            w = [0.5 * (1.5 - fx)**2, 0.75 - (fx - 1)**2, 0.5 * (fx - 0.5)**2]
            # deformation gradient update
            self.F[p] = (ti.Matrix.identity(float, 2) +
                         self.dt * self.C[p]) @ self.F[p]
            # Hardening coefficient: snow gets harder when compressed
            h = ti.max(0.1, ti.min(5, ti.exp(10 * (1.0 - self.Jp[p]))))
            if self.material[p] == 3:
                self.reset_mu_lam(5e3, 0.2)
                # E, nu = 2e4, 0.3  # Young's modulus and Poisson's ratio
                # self.mu_0, self.lambda_0 = E / (2 * (1 + nu)), E * nu / (
                #     (1 + nu) * (1 - 2 * nu))  # Lame parameters
            elif self.material[p] == 4:
                self.reset_mu_lam(7e2, 0.4)
                # E, nu = 7e2, 0.4  # Young's modulus and Poisson's ratio
                # self.mu_0, self.lambda_0 = E / (2 * (1 + nu)), E * nu / (
                #     (1 + nu) * (1 - 2 * nu))  # Lame parameters
            elif self.material[p] == 2:  # jelly, make it softer
                h = 0.3
            mu, la = self.mu_0[None] * h, self.lambda_0[None] * h
            if self.material[p] == 1:  # liquid
                mu = 0.0
            U, sig, V = ti.svd(self.F[p])
            J = 1.0
            for d in ti.static(range(2)):
                new_sig = sig[d, d]
                self.Jp[p] *= sig[d, d] / new_sig
                sig[d, d] = new_sig
                J *= new_sig
            if self.material[p] == 1:
                # Reset deformation gradient to avoid numerical instability
                self.F[p] = ti.Matrix.identity(float, 2) * ti.sqrt(J)
            stress = 2 * mu * (self.F[p] - U @ V.transpose()
                               ) @ self.F[p].transpose() + ti.Matrix.identity(
                                   float, 2) * la * J * (J - 1)
            stress = (-self.dt * self.p_vol * 4 * self.inv_dx *
                      self.inv_dx) * stress
            affine = stress + self.p_mass * self.C[p]
            for i, j in ti.static(ti.ndrange(3, 3)):
                # Loop over 3x3 grid node neighborhood
                offset = ti.Vector([i, j])
                dpos = (offset.cast(float) - fx) * self.dx
                weight = w[i][0] * w[j][1]
                self.grid_v[base +
                            offset] += weight * (self.p_mass * self.v[p] +
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
        for p in self.x:  # grid to particle (G2P)
            base = (self.x[p] * self.inv_dx - 0.5).cast(int)
            fx = self.x[p] * self.inv_dx - base.cast(float)
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
            self.accl[p] = self.v[p] - new_v
            self.v[p], self.C[p] = new_v, new_C
            self.x[p] += self.dt * self.v[p]  # advection

    # @ti.func
    def point_in_rect(self, figure: ti.template(), pt_x: float,
                      pt_y: float) -> bool:
        return pt_x <= ti.max(figure.start_x, figure.end_x) and pt_x >= ti.min(
            figure.start_x, figure.end_x) and pt_y <= ti.max(
                figure.start_y, figure.end_y) and pt_y >= ti.min(
                    figure.start_y, figure.end_y)

    # @ti.func
    def point_in_circle(self, figure: ti.template(), pt_x: float,
                        pt_y: float) -> bool:
        radius = abs(figure.start_x - figure.end_x)
        center_x = (figure.start_x + figure.end_x) / 2
        center_y = (figure.start_y + figure.end_y) / 2
        # print(pt_x, pt_y)
        return radius**2 >= (center_x - pt_x)**2 + (center_y - pt_y)**2

    # @ti.func
    def point_in_poly(self, figure, pt_x, pt_y):
        # points = figure.p_point_array
        nums = len(figure.p_point_array)
        count = 0
        for i in range(nums):
            x1, y1 = figure.p_point_array[i].x(), figure.p_point_array[i].y()
            x2, y2 = figure.p_point_array[
                (i + 1) % nums].x(), figure.p_point_array[(i + 1) % nums].y()
            if ti.min(y1, y2) < pt_y <= ti.max(y1, y2):
                x = (pt_y - y1) * (x2 - x1) / (y2 - y1) + x1
                if x <= pt_x:
                    count += 1
        return count % 2 == 1

    def point_in_polygon(self, figure: ti.template(), pt_x, pt_y):
        # pt_x = point[0]
        # pt_y = point[1]
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

    @ti.kernel
    def caculate_force(self):
        for i in range(self.n_particles / self.grid_particle_ratio):
            self.z[i] = [0, 0]
            for j in range(self.grid_particle_ratio):
                if self.material[i + j] == MatterType['NoType']:
                    break
                self.z[i] = self.z[i] + self.accl[i + j]
            self.force_z[i] = self.z[i].norm() / self.grid_particle_ratio

    def force_setting(self):
        self.force_n = self.force_z.to_numpy().reshape(
            self.n_part_grid, self.n_part_grid).transpose()
        # self.force_n = self.force_n.reshape(self.n_grid,
        #                                     self.n_grid).transpose()

    # def draw_force(self):
    #     setting_x = np.linspace(-1.0, 1.0, self.n_grid)
    #     setting_y = np.linspace(-1.0, 1.0, self.n_grid)
    #     self.caculate_force()
    #     force_n = self.force_z.to_numpy()
    #     force_n = force_n.reshape(self.n_grid, self.n_grid).transpose()
    #     plt.contourf(setting_x,
    #                  setting_y,
    #                  force_n,
    #                  levels=100,
    #                  cmap=plt.get_cmap('Spectral'))

    # @ti.data_oriented
    # class particle:

    #     # @ti.kernel
    #     def __init__(
    #             self,
    #             x,
    #             v=[0, 0],
    #             #  C=ti.Matrix.zero(float, 2, 2),
    #             #  F=ti.Matrix([[1, 0], [0, 1]]),
    #             material=MatterType['Plastic'],
    #             Jp=1,
    #             color=Qt.red) -> None:

    #         self.x = x  # position
    #         self.v = v  # velocity
    #         self.material = material  # material id
    #         self.Jp = Jp  # plastic deformation
    #         self.c = color
    #         self.C = ti.Matrix([[0, 0], [0, 0]])  # affine velocity field
    #         self.F = ti.Matrix([[1, 0], [0, 1]])  # deformation gradient
    #         # self.setting()

    #     # @ti.kernel
    #     # def setting(self):
    #     #     self.C = ti.Matrix.zero(float, 2, 2)  # affine velocity field
    #     #     self.F = ti.Matrix([[1, 0], [0, 1]])  # deformation gradient

    # @ti.kernel
    # def subpars(self, p: ti.template()):
    #     # p.x.from_numpy(p.x)
    #     # temp = ti.Matrix(p.x)
    #     base = (p.x * self.inv_dx - 0.5).cast(int)
    #     fx = p.x * self.inv_dx - base.cast(float)
    #     # Quadratic kernels  [http://mpm.graphics   Eqn. 123, with x=fx, fx-1,fx-2]
    #     w = [0.5 * (1.5 - fx)**2, 0.75 - (fx - 1)**2, 0.5 * (fx - 0.5)**2]

    #     # deformation gradient update
    #     p.F = (ti.Matrix.identity(float, 2) + self.dt * p.C) @ p.F
    #     # Hardening coefficient: snow gets harder when compressed
    #     h = ti.max(0.1, ti.min(5, ti.exp(10 * (1.0 - p.Jp))))
    #     if p.material == 3:
    #         E, nu = 2e4, 0.3  # Young's modulus and Poisson's ratio
    #         self.mu_0, self.lambda_0 = E / (2 * (1 + nu)), E * nu / (
    #             (1 + nu) * (1 - 2 * nu))  # Lame parameters
    #     elif p.material == 4:
    #         E, nu = 7e2, 0.4  # Young's modulus and Poisson's ratio
    #         self.mu_0, self.lambda_0 = E / (2 * (1 + nu)), E * nu / (
    #             (1 + nu) * (1 - 2 * nu))  # Lame parameters
    #     elif p.material == 2:  # jelly, make it softer
    #         h = 0.3
    #     mu, la = self.mu_0 * h, self.lambda_0 * h
    #     if p.material == 1:  # liquid
    #         mu = 0.0
    #     U, sig, V = ti.svd(p.F)
    #     J = 1.0
    #     for d in ti.static(range(2)):
    #         new_sig = sig[d, d]
    #         p.Jp *= sig[d, d] / new_sig
    #         sig[d, d] = new_sig
    #         J *= new_sig
    #     if p.material == 1:
    #         # Reset deformation gradient to avoid numerical instability
    #         p.F = ti.Matrix.identity(float, 2) * ti.sqrt(J)
    #     stress = 2 * mu * (p.F - U @ V.transpose()) @ p.F.transpose(
    #     ) + ti.Matrix.identity(float, 2) * la * J * (J - 1)
    #     stress = (-self.dt * self.p_vol * 4 * self.inv_dx *
    #               self.inv_dx) * stress
    #     affine = stress + self.p_mass * p.C
    #     for i, j in ti.static(ti.ndrange(3, 3)):
    #         # Loop over 3x3 grid node neighborhood
    #         offset = ti.Vector([i, j])
    #         dpos = (offset.cast(float) - fx) * self.dx
    #         weight = w[i][0] * w[j][1]
    #         self.grid_v[base + offset] += self.weight * (self.p_mass * p.v +
    #                                                      affine @ dpos)
    #         self.grid_m[base + offset] += weight * self.p_mass

    # @ti.kernel
    # def g2p(self, p: ti.template()):
    #     # temp = ti.Matrix(p.x)
    #     base = (p.x * self.inv_dx - 0.5).cast(int)
    #     fx = p.x * self.inv_dx - base.cast(float)
    #     w = [0.5 * (1.5 - fx)**2, 0.75 - (fx - 1.0)**2, 0.5 * (fx - 0.5)**2]
    #     new_v = ti.Vector.zero(float, 2)
    #     new_C = ti.Matrix.zero(float, 2, 2)
    #     for i, j in ti.static(ti.ndrange(3, 3)):
    #         # loop over 3x3 grid node neighborhood
    #         dpos = ti.Vector([i, j]).cast(float) - fx
    #         g_v = self.grid_v[base + ti.Vector([i, j])]
    #         weight = w[i][0] * w[j][1]
    #         new_v += weight * g_v
    #         new_C += 4 * self.inv_dx * weight * g_v.outer_product(dpos)
    #     p.v, p.C = new_v, new_C
    #     p.x += self.dt * p.v  # advection

    # # @ti.kernel
    # # def prit(self, p: ti.template()):
    # #     print(p.x, p.v, p.c)

    # @ti.kernel
    # def gridtest(self):
    #     for i, j in self.grid_m:
    #         if self.grid_m[i, j] > 0:  # No need for epsilon here
    #             # Momentum to velocity
    #             self.grid_v[i, j] = (1 / self.grid_m[i, j]) * self.grid_v[i, j]
    #             self.grid_v[i,
    #                         j] += self.dt * self.gravity[None] * 30  # gravity
    #             if i < 3 and self.grid_v[i, j][0] < 0:
    #                 self.grid_v[i, j][0] = 0  # Boundary conditions
    #             if i > self.n_grid - 3 and self.grid_v[i, j][0] > 0:
    #                 self.grid_v[i, j][0] = 0
    #             if j < 3 and self.grid_v[i, j][1] < 0:
    #                 self.grid_v[i, j][1] = 0
    #             if j > self.n_grid - 3 and self.grid_v[i, j][1] > 0:
    #                 self.grid_v[i, j][1] = 0

    # @ti.kernel
    # def gridinit(self):
    #     for i, j in self.grid_m:
    #         self.grid_v[i, j] = [0, 0]
    #         self.grid_m[i, j] = 0

    # def substep(self):
    #     self.gridinit()
    #     for p in self.particles:
    #         print(p.F)
    #         self.subpars(p)
    #     self.gridtest()
    #     for p in self.particles:  # grid to particle (G2P)
    #         self.g2p(p)

    # @ti.kernel
    # def ran(self) -> ti.f32:
    #     return ti.random()

    # Add circle object in scene
    @ti.kernel
    def add_object_figure(self, figure: ti.template(), t: int):
        for k in range(self.n_particles):
            if isinstance(figure, Rect):
                if self.point_in_rect(figure, self.x[k][0] * self.window_w,
                                      self.x[k][1] * self.window_h):
                    self.material[k] = t
                    # self.v[k] = velocity
            elif isinstance(figure, Circle):
                if self.point_in_circle(figure, self.x[k][0] * self.window_w,
                                        self.x[k][1] * self.window_h):
                    self.material[k] = t
            else:
                if self.point_in_poly(figure, self.x[k][0] * self.window_w,
                                      self.x[k][1] * self.window_h):
                    self.material[k] = t

    # @ti.kernel
    def add_object_circle(self, figure: ti.template(), t: int):
        for k in range(self.n_particles):
            if self.point_in_circle(figure, self.x[k][0] * self.window_w,
                                    self.x[k][1] * self.window_h):
                self.material[k] = t

    # Add rectangle object in scene

    def add_object_rectangle(self, figure: ti.template(), t: int):
        for k in range(self.n_particles):
            if self.point_in_rect(figure, self.x[k][0] * self.window_w,
                                  self.x[k][1] * self.window_h):
                self.material[k] = t

    # Add polygon & free-hand object in scene
    # @ti.kernel
    def add_object_polygon(self, figure: ti.template(), t: int):
        for k in range(self.n_particles):
            if self.point_in_poly(figure, self.x[k][0] * self.window_w,
                                  self.x[k][1] * self.window_h):
                self.material[k] = t


@ti.data_oriented
class FEM:

    # @ti.kernel
    def __init__(self, w, h) -> None:
        self.window_w = w
        self.window_h = h
        self.N = 32
        self.dt = 1e-4
        self.dx = 1 / self.N
        self.rho = 4e1
        self.NF = 2 * self.N**2  # number of faces
        self.NV = (self.N + 1)**2  # number of vertices
        E, nu = 4e4, 0.2  # Young's modulus and Poisson's ratio
        self.mu, self.lam = E / 2 / (1 + nu), E * nu / (1 + nu) / (1 - 2 * nu)
        self.gravity = ti.Vector([0, 10])
        self.damping = 12.5
        # self.damping = 20

        self.pos = ti.Vector.field(2, float, self.NV)
        self.vel = ti.Vector.field(2, float, self.NV)
        self.matr = ti.field(int, self.NV)
        self.f2v = ti.Vector.field(
            3, int, self.NF)  # ids of three vertices of each face
        self.B = ti.Matrix.field(2, 2, float, self.NF)
        self.W = ti.field(float, self.NF)
        self.phi = ti.field(
            float, self.NF)  # potential energy of each face (Neo-Hookean)
        self.U = ti.field(float, (), needs_grad=True)  # total potential energy
        self.f = ti.Vector.field(2, float, self.NV)
        self.force_n = ti.field(float, self.NV)
        self.init_mesh()
        # self.init_pos()

    # @ti.func
    def resetMaterial(self, material):
        if material == MatterType['Jelly']:
            self.lam = self.lam * 0.3
        elif material == MatterType['Plastic']:
            E, nu = 5e3, 0.4
            self.mu, self.lam = E / 2 / (1 + nu), E * nu / (1 + nu) / (1 -
                                                                       2 * nu)
        elif material == MatterType['Steel'] or material == MatterType[
                'HSteel']:
            E, nu = 1e5, 0.3
            self.mu, self.lam = E / 2 / (1 + nu), E * nu / (1 + nu) / (1 -
                                                                       2 * nu)

    @ti.kernel
    def update_force(self):
        for i in range(self.NF):
            ia, ib, ic = self.f2v[i]
            if self.matr[ia] != MatterType['NoType'] and self.matr[
                    ib] != MatterType['NoType'] and self.matr[
                        ic] != MatterType['NoType']:
                a, b, c = self.pos[ia], self.pos[ib], self.pos[ic]
                self.resetMaterial(self.matr[ia])
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

    @ti.kernel
    def caculate_f(self):
        for i in range(self.NV):
            self.force_n[i] = self.f[i].norm()

    @ti.kernel
    def advance(self):
        for i in range(self.NV):
            acc = self.f[i] / (self.rho * self.dx**2)
            self.vel[i] += self.dt * (acc + self.gravity)
            self.vel[i] *= ti.exp(-self.dt * self.damping)
        for i in range(self.NV):
            # rect boundary condition:
            cond = self.pos[i] < 0.04 and self.vel[i] < 0 or self.pos[
                i] > 0.92 and self.vel[i] > 0
            for j in ti.static(range(self.pos.n)):
                if cond[j]:
                    self.vel[i][j] = 0
            self.pos[i] += self.dt * self.vel[i]

    # @ti.kernel
    def point_in_polygon(figure, point):
        pt_x = point[0]
        pt_y = point[1]
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

    # @ti.func
    def point_in_rect(self, figure: ti.template(), pt_x: float,
                      pt_y: float) -> bool:
        return pt_x <= ti.max(figure.start_x, figure.end_x) and pt_x >= ti.min(
            figure.start_x, figure.end_x) and pt_y <= ti.max(
                figure.start_y, figure.end_y) and pt_y >= ti.min(
                    figure.start_y, figure.end_y)

    # @ti.func
    def point_in_circle(self, figure: ti.template(), pt_x: float,
                        pt_y: float) -> bool:
        radius = abs(figure.start_x - figure.end_x)
        center_x = (figure.start_x + figure.end_x) / 2
        center_y = (figure.start_y + figure.end_y) / 2
        # print(pt_x, pt_y)
        return radius**2 >= (center_x - pt_x)**2 + (center_y - pt_y)**2

    # @ti.func
    def point_in_poly(self, figure, pt_x, pt_y):
        # points = figure.p_point_array
        nums = len(figure.p_point_array)
        count = 0
        for i in range(nums):
            x1, y1 = figure.p_point_array[i].x(), figure.p_point_array[i].y()
            x2, y2 = figure.p_point_array[
                (i + 1) % nums].x(), figure.p_point_array[(i + 1) % nums].y()
            if ti.min(y1, y2) < pt_y <= ti.max(y1, y2):
                x = (pt_y - y1) * (x2 - x1) / (y2 - y1) + x1
                if x <= pt_x:
                    count += 1
        return count % 2 == 1

    @ti.kernel
    def init_pos(self, top: int, bottom: int, left: int, right: int):
        hit = (top - bottom) / self.window_h
        wid = (right - left) / self.window_w
        # print(self.window_h, self.window_w)
        # print(top - bottom, hit, hit * self.window_h)
        for i, j in ti.ndrange(self.N + 1, self.N + 1):
            k = i * (self.N + 1) + j
            self.pos[k] = ti.Vector([i * wid, j * hit]) / self.N + ti.Vector(
                [left / self.window_w, bottom / self.window_h])
            self.vel[k] = ti.Vector([0, 0])
            self.matr[k] = MatterType['NoType']
        for i in range(self.NF):
            ia, ib, ic = self.f2v[i]
            a, b, c = self.pos[ia], self.pos[ib], self.pos[ic]
            B_i = ti.Matrix.cols([a - c, b - c])
            self.B[i] = B_i.inverse()
            self.W[i] = abs(B_i.determinant())

    @ti.kernel
    def init_mesh(self):
        for i, j in ti.ndrange(self.N, self.N):
            k = (i * self.N + j) * 2
            a = i * (self.N + 1) + j
            b = a + 1
            c = a + self.N + 2
            d = a + self.N + 1
            self.f2v[k + 0] = [a, b, c]
            self.f2v[k + 1] = [c, d, a]

    @ti.kernel
    def init_parameter(self):
        for i in self.f:
            self.f[i] = ti.Vector([0.0, 0.0])

    def add_object_figure(self,
                          figure,
                          t=MatterType['Plastic'],
                          velocity=(0.0, 0.0)):
        for k in range(self.NV):
            if self.point_in_polygon(figure, self.pos[k]):
                self.matr[k] = t
                self.vel[k] = velocity

    def add_object_circle(self, figure: ti.template(), t: int, vx=0, vy=0):
        for k in range(self.NV):
            if self.point_in_circle(figure, self.pos[k][0] * self.window_w,
                                    self.pos[k][1] * self.window_h):
                self.matr[k] = t
                self.vel[k] = (vx, vy)

    # Add rectangle object in scene

    def add_object_rectangle(self, figure: ti.template(), t: int, vx=0, vy=0):
        for k in range(self.NV):
            if self.point_in_rect(figure, self.pos[k][0] * self.window_w,
                                  self.pos[k][1] * self.window_h):
                self.matr[k] = t
                self.vel[k] = (vx, vy)

    # Add polygon & free-hand object in scene
    # @ti.kernel
    def add_object_polygon(self, figure: ti.template(), t: int, vx=0, vy=0):
        for k in range(self.NV):
            if self.point_in_poly(figure, self.pos[k][0] * self.window_w,
                                  self.pos[k][1] * self.window_h):
                self.matr[k] = t
                self.vel[k] = (vx, vy)
