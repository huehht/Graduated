import taichi as ti
import matplotlib.pyplot as plt
import numpy as np

ti.init(arch=ti.gpu)
gui = ti.GUI('FEM99')

N = 16
dt = 1e-4
dx = 1 / N
rho = 4e1
NF = 2 * N**2  # number of faces
NV = (N + 1)**2  # number of vertices
E = gui.slider('Young\'s modulus', 1e4, 1e6, step=1e4)
E.value, nu = 4e4, 0.2  # Young's modulus and Poisson's ratio
global mu, lam
mu, lam = E.value / 2 / (1 + nu), E.value * nu / (1 + nu) / (1 - 2 * nu)
ball_pos, ball_radius = ti.Vector([0.5, 0.0]), 0.16
gravity = ti.Vector([0, -40])
damping = 12.5
# damping = 20

pos = ti.Vector.field(2, float, NV)
vel = ti.Vector.field(2, float, NV)
f2v = ti.Vector.field(3, int, NF)  # ids of three vertices of each face
B = ti.Matrix.field(2, 2, float, NF)
W = ti.field(float, NF)
phi = ti.field(float, NF)  # potential energy of each face (Neo-Hookean)
U = ti.field(float, (), needs_grad=True)  # total potential energy
f = ti.Vector.field(2, float, NV)


def reload():  # Young's modulus and Poisson's ratio
    mu, lam = E.value / 2 / (1 + nu), E.value * nu / (1 + nu) / (
        1 - 2 * nu)  # Lame parameters
    return mu, lam


@ti.kernel
def update_force(mu: float, lam: float):
    for i in range(NF):
        ia, ib, ic = f2v[i]
        a, b, c = pos[ia], pos[ib], pos[ic]

        D_i = ti.Matrix.cols([a - c, b - c])
        F = D_i @ B[i]
        F_it = F.inverse().transpose()

        PF = mu * (F - F_it) + lam * ti.log(F.determinant()) * F_it
        H = -W[i] * PF @ B[i].transpose()

        fa = ti.Vector([H[0, 0], H[1, 0]])
        fb = ti.Vector([H[0, 1], H[1, 1]])
        fc = -fa - fb
        f[ia] += fa
        f[ib] += fb
        f[ic] += fc


def draw_force():
    fig, ax = plt.subplots()
    levels = np.arange(-2, 2.0, 0.005)
    x = np.linspace(-1.0, 1.0, N + 1)
    y = np.linspace(-1.0, 1.0, N + 1)
    X, Y = np.meshgrid(x, y)
    f_n = f.to_numpy()
    Z = np.zeros(NV)
    for i in range(NV):
        Z[i] = np.linalg.norm(f_n[i])
    Z = Z.reshape(N + 1, N + 1).transpose()
    cs = ax.contourf(X, Y, Z, levels=100, cmap=plt.get_cmap('Spectral'))
    cbar = fig.colorbar(cs)
    # plt.ion()
    # plt.pause(0.01)
    # plt.close()
    # plt.show()


@ti.kernel
def advance():
    for i in range(NV):
        acc = f[i] / (rho * dx**2)
        vel[i] += dt * (acc + gravity)
        vel[i] *= ti.exp(-dt * damping)
    for i in range(NV):
        # ball boundary condition:
        disp = pos[i] - ball_pos
        disp2 = disp.norm_sqr()
        if disp2 <= ball_radius**2:
            NoV = vel[i].dot(disp)
            if NoV < 0:
                vel[i] -= NoV * disp / disp2
        # rect boundary condition:
        cond = pos[i] < 0 and vel[i] < 0 or pos[i] > 1 and vel[i] > 0
        for j in ti.static(range(pos.n)):
            if cond[j]:
                vel[i][j] = 0
        pos[i] += dt * vel[i]


@ti.kernel
def draw_line():
    while True:
        gui.get_event()  # must be called before is_pressed
        if gui.is_pressed(ti.GUI.LMB, 'w'):
            mouse0_x, mouse0_y = gui.get_cursor_pos()

            mouse1_x, mouse1_y = gui.get_cursor_pos()
            print(mouse0_x, mouse0_y)
            print(mouse1_x, mouse1_y)
            print(1)
    # gui.line((mouse0_x, mouse0_y), (mouse1_x, mouse1_y),
    #          radius=1,
    #          color=0x4FB99F)


@ti.kernel
def init_pos():
    for i, j in ti.ndrange(N + 1, N + 1):
        k = i * (N + 1) + j
        pos[k] = ti.Vector([i, j]) / N * 0.25 + ti.Vector([0.5, 0.45])
        vel[k] = ti.Vector([0, 0])
    for i in range(NF):
        ia, ib, ic = f2v[i]
        a, b, c = pos[ia], pos[ib], pos[ic]
        B_i = ti.Matrix.cols([a - c, b - c])
        B[i] = B_i.inverse()
        W[i] = abs(B_i.determinant())


@ti.kernel
def init_mesh():
    for i, j in ti.ndrange(N, N):
        k = (i * N + j) * 2
        a = i * (N + 1) + j
        b = a + 1
        c = a + N + 2
        d = a + N + 1
        f2v[k + 0] = [a, b, c]
        f2v[k + 1] = [c, d, a]


@ti.kernel
def init_parameter():
    for i in f:
        f[i] = ti.Vector([0.0, 0.0])


init_mesh()
init_pos()

while gui.running:
    for e in gui.get_events():
        if e.key == gui.ESCAPE:
            gui.running = False
        elif e.key == 'r':
            mu, lam = reload()
            init_pos()
        elif e.key == 'a':
            draw_line()

    for i in range(30):
        init_parameter()
        update_force(mu, lam)
        advance()
    # draw_force()
    pos_n = pos.to_numpy()
    node_f2v = f2v.to_numpy()
    for i in range(NF):
        for j in range(3):
            a, b = node_f2v[i][j], node_f2v[i][(j + 1) % 3]
            gui.line((pos_n[a][0], pos_n[a][1]), (pos_n[b][0], pos_n[b][1]),
                     radius=1,
                     color=0x4FB99F)
    # gui.circles(pos.to_numpy(), radius=2, color=0xffaa33)
    gui.circle(ball_pos, radius=ball_radius * 512, color=0x666666)
    gui.show()