"""
Demonstrates very basic use of PColorMeshItem
"""

import time

import numpy as np
import sys
from PyQt5.QtWidgets import QApplication, QWidget
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from PyQt5.QtCore import QTimer, QDateTime


class plots:

    def __init__(self):
        self.pl()
        # pg.exec()s

    def pl(self):
        self.app = pg.mkQApp("PColorMesh Example")

        ## Create window with GraphicsView widget
        self.win = pg.GraphicsLayoutWidget()
        self.win.show()  ## show widget alone in its own window
        self.win.setWindowTitle('pyqtgraph example: pColorMeshItem')
        self.view_consistent_scale = self.win.addPlot(
            0, 0, 1, 1, title="Consistent colorscheme", enableMenu=False)

        ## Create data

        # To enhance the non-grid meshing, we randomize the polygon vertices per and
        # certain amount
        randomness = 5

        # x and y being the vertices of the polygons, they share the same shape
        # However the shape can be different in both dimension
        self.xn = 50  # nb points along x
        yn = 40  # nb points along y

        self.x = np.repeat(np.arange(0, self.xn), yn).reshape(self.xn, yn)\
            + np.random.random((self.xn, yn))*randomness
        self.y = np.tile(np.arange(0, yn), self.xn).reshape(self.xn, yn)\
            + np.random.random((self.xn, yn))*randomness
        self.x.sort(axis=0)
        self.y.sort(axis=0)
        # z being the color of the polygons its shape must be decreased by one in each dimension
        self.z = np.exp(-(self.x * self.xn)**2 / 1000)[:-1, :-1]

        ## Create autoscaling image item
        edgecolors = None
        antialiasing = True
        cmap = pg.colormap.get('viridis')
        levels = (
            -2, 2
        )  # Will be overwritten unless enableAutoLevels is set to False

        # Create image item with consistent colors and an interactive colorbar
        self.pcmi_consistent = pg.PColorMeshItem(edgecolors=edgecolors,
                                                 antialiasing=antialiasing,
                                                 colorMap=cmap,
                                                 levels=levels,
                                                 enableAutoLevels=False)
        self.view_consistent_scale.addItem(self.pcmi_consistent)

        # Add colorbar
        self.bar_static = pg.ColorBarItem(label="Z value [arbitrary unit]",
                                          interactive=True,
                                          rounding=0.2)
        self.bar_static.setImageItem([self.pcmi_consistent])
        self.win.addItem(self.bar_static, 0, 1, 1, 1)

        # Add timing label to the autoscaling view
        # self.textitem = pg.TextItem(anchor=(1, 0))

        # self.textitem.setPos(0, 10)
        self.timer = QTimer()
        # self.timer.setSingleShot(True)
        self.timer.start(100)
        self.timer.timeout.connect(self.updated)
        # self.updated()
        # timer.timeout.connect(updateData)
        # updateData()
        # not using QTimer.singleShot() because of persistence on PyQt. see PR #1605

    def updated(self):
        self.z = np.exp(-(self.x * self.xn)**2 / (np.random.random() + 1) /
                        10)[:-1, :-1]
        print(self.x)
        print(self.z)
        self.pcmi_consistent.setData(self.x, self.y, self.z)

    #     ## Display the new data se
    #     self.pcmi_consistent.setData(new_x, new_y, new_z)
    #     t2 = time.perf_counter()

    #     i += wave_speed

    #     textitem.setText(f'{(t2 - t1)*1000:.1f} ms')

    #     # cap update rate at fps
    #     delay = max(1000 / fps - (t2 - t0), 0)
    #     timer.start(int(delay))


if __name__ == '__main__':

    app = QApplication(sys.argv)
    p = plots()
    # w = QWidget()
    # w.resize(250, 150)
    # w.move(300, 300)
    # w.setWindowTitle('Simple')
    # w.show()
    # pg.exec()
    sys.exit(app.exec_())