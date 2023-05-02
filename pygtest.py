"""
Demonstrates very basic use of PColorMeshItem
"""

import time

import numpy as np

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore


def plot():
    app = pg.mkQApp("PColorMesh Example")

    ## Create window with GraphicsView widget
    win = pg.GraphicsLayoutWidget()
    win.show()  ## show widget alone in its own window
    win.setWindowTitle('pyqtgraph example: pColorMeshItem')
    view_consistent_scale = win.addPlot(0,
                                        0,
                                        1,
                                        1,
                                        title="Consistent colorscheme",
                                        enableMenu=False)

    ## Create data

    # To enhance the non-grid meshing, we randomize the polygon vertices per and
    # certain amount
    randomness = 5

    # x and y being the vertices of the polygons, they share the same shape
    # However the shape can be different in both dimension
    xn = 50  # nb points along x
    yn = 40  # nb points along y

    x = np.repeat(np.arange(0, xn), yn).reshape(xn, yn)\
        + np.random.random((xn, yn))*randomness
    y = np.tile(np.arange(0, yn), xn).reshape(xn, yn)\
        + np.random.random((xn, yn))*randomness
    x.sort(axis=0)
    y.sort(axis=0)

    # z being the color of the polygons its shape must be decreased by one in each dimension
    z = np.exp(-(x * xn)**2 / 1000)[:-1, :-1]

    ## Create autoscaling image item
    edgecolors = None
    antialiasing = False
    cmap = pg.colormap.get('viridis')
    levels = (-2, 2
              )  # Will be overwritten unless enableAutoLevels is set to False

    # Create image item with consistent colors and an interactive colorbar
    pcmi_consistent = pg.PColorMeshItem(edgecolors=edgecolors,
                                        antialiasing=antialiasing,
                                        colorMap=cmap,
                                        levels=levels,
                                        enableAutoLevels=False)
    view_consistent_scale.addItem(pcmi_consistent)

    # Add colorbar
    bar_static = pg.ColorBarItem(label="Z value [arbitrary unit]",
                                 interactive=True,
                                 rounding=0.1)
    bar_static.setImageItem([pcmi_consistent])
    win.addItem(bar_static, 0, 1, 1, 1)

    # Add timing label to the autoscaling view
    textitem = pg.TextItem(anchor=(1, 0))

    textitem.setPos(0, 10)

    timer = QtCore.QTimer()
    timer.setSingleShot(True)
    pcmi_consistent.setData(x, y, z)
    pg.exec()
    # not using QTimer.singleShot() because of persistence on PyQt. see PR #1605


# def updateData():
#     global i
#     global textpos

#     ## Display the new data se
#     pcmi_consistent.setData(new_x, new_y, new_z)
#     t2 = time.perf_counter()

#     i += wave_speed

#     textitem.setText(f'{(t2 - t1)*1000:.1f} ms')

#     # cap update rate at fps
#     delay = max(1000 / fps - (t2 - t0), 0)
#     timer.start(int(delay))

# timer.timeout.connect(updateData)
# updateData()

if __name__ == '__main__':
    plot()
    print(1)