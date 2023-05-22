import sys
from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QApplication, QPushButton, QLineEdit, QToolBar, QAction, QSlider, QWidget
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt
# from PyQt5 import QWidget
from maincontroller import FigureType, MatterType, Minidraw_controller
from uimianwind import Ui_Minidraw
import matplotlib.pyplot as plt


class Minidraw(QMainWindow):

    def __init__(self, parent=None):
        super(Minidraw, self).__init__(parent)
        self.ui = Ui_Minidraw()
        self.ui.setupUi(self)
        self.controller = Minidraw_controller()
        self.setCentralWidget(self.controller)
        self.setWindowTitle("Simulation")  # add title
        self.setWindowIcon(
            QIcon(
                "/Users/hht/Desktop/hht_s/coding/FEMsimulate/src/resources/icon.png"
            ))  # add icon

        self.create_toolbar()
        self.create_figure_toolbar()
        self.create_simulation_toolbar()
        # self.create_snow_type_toolbar()

    def __del__(self):
        del self.ui

    def set_line_width(self, width):
        self.controller.current_line_width = width

    def set_rho(self, rho):
        pass

    def set_yms(self, yms):
        pass

    def set_prt(self, prt):
        pass

    def save_scene(self):
        self.controller.save_scene()

    # Set line colors
    def set_line_color_red(self):
        self.controller.current_line_color = Qt.red
        self.controller.current_figure_type = FigureType.Line
        self.controller.isDel = False
        self.controller.isEdit = False

    def set_line_color_blue(self):
        self.controller.current_line_color = QColor(0x87CEFA)
        self.controller.current_figure_type = FigureType.Curve
        self.controller.isDel = False
        self.controller.isEdit = False

    def set_line_color_green(self):
        self.controller.current_line_color = Qt.green
        self.controller.current_figure_type = FigureType.Curve
        self.controller.isDel = False
        self.controller.isEdit = False

    def set_line_color_orange(self):
        self.controller.current_line_color = QColor(0xED553B)
        self.controller.current_figure_type = FigureType.Curve
        self.controller.isDel = False
        self.controller.isEdit = False

    def set_line_color_black(self):
        self.controller.current_line_color = Qt.black
        self.controller.current_figure_type = FigureType.Curve
        self.controller.isDel = False
        self.controller.isEdit = False

    def set_line_color_yellow(self):
        self.controller.current_line_color = Qt.yellow
        self.controller.current_figure_type = FigureType.Curve
        self.controller.isDel = False
        self.controller.isEdit = False
        self.newWind = SettingMatrial()
        self.newWind.show()

    def set_line_color_white(self):
        self.controller.current_line_color = Qt.white
        self.controller.current_figure_type = FigureType.Curve
        self.controller.isDel = False
        self.controller.isEdit = False

    # Set figure type
    def set_figure_tool_line(self):
        self.controller.current_figure_type = FigureType.Line
        self.controller.isAdding = True
        self.controller.isDel = False
        self.controller.isEdit = False

    def set_figure_tool_rect(self):
        self.controller.current_figure_type = FigureType.Rectangle
        self.controller.isAdding = True
        self.controller.isDel = False
        self.controller.isEdit = False

    def set_figure_tool_circle(self):
        self.controller.current_figure_type = FigureType.Circle
        self.controller.isAdding = True
        self.controller.isDel = False
        self.controller.isEdit = False

    def set_figure_tool_curve(self):
        self.controller.current_figure_type = FigureType.Curve
        self.controller.isAdding = True
        self.controller.isDel = False
        self.controller.isEdit = False

    def set_figure_tool_ellipse(self):
        self.controller.current_figure_type = FigureType.Ellipse
        self.controller.isAdding = True
        self.controller.isDel = False
        self.controller.isEdit = False

    # def set_figure_tool_tri(self):
    #     self.controller.current_figure_type = FigureType.Triangle
    #     self.controller.isAdding = True

    # def set_figure_tool_poly(self):
    #     self.controller.current_figure_type = FigureType.Polygon
    #     self.controller.isAdding = True

    def set_figure_tool_del(self):
        self.controller.isAdding = False
        self.controller.isDel = True

    def set_figure_tool_edit(self):
        self.controller.isAdding = False
        self.controller.isEdit = True

    # Create toolbar
    def create_toolbar(self):
        self.slider_toolbar = self.addToolBar("slider toolbar")
        self.color_toolbar = self.addToolBar("color toolbar")

        # create slider for line width
        self.slider_line_width = QSlider(Qt.Horizontal)
        self.slider_line_width.setRange(1, 20)  # set line width range be 1-20
        self.slider_line_width.setSingleStep(
            1)  # set line width change step be 1
        self.slider_line_width.setStatusTip("线宽")

        # connect slider value change with function set_line_width
        self.slider_line_width.valueChanged.connect(self.set_line_width)
        self.slider_toolbar.addWidget(self.slider_line_width)

        # create button for color
        button_black = QAction(
            QIcon(
                "/Users/hht/Desktop/hht_s/coding/FEMsimulate/src/resources/steel.png"
            ), "Steel", self)
        button_black.triggered.connect(self.set_line_color_black)
        self.color_toolbar.addAction(button_black)

        button_white = QAction(
            QIcon(
                "/Users/hht/Desktop/hht_s/coding/FEMsimulate/src/resources/plastic.png"
            ), "Plastic", self)
        button_white.triggered.connect(self.set_line_color_white)
        self.color_toolbar.addAction(button_white)

        # button_blue = QAction(
        #     QIcon(
        #         "/Users/hht/Desktop/hht_s/coding/FEMsimulate/src/resources/fluid.png"
        #     ), "Fluid", self)
        # button_blue.triggered.connect(self.set_line_color_blue)
        # self.color_toolbar.addAction(button_blue)

        button_green = QAction(
            QIcon(
                "/Users/hht/Desktop/hht_s/coding/FEMsimulate/src/resources/hsteel.png"
            ), "high strength steel", self)
        button_green.triggered.connect(self.set_line_color_green)
        self.color_toolbar.addAction(button_green)

        button_orange = QAction(
            QIcon(
                "/Users/hht/Desktop/hht_s/coding/FEMsimulate/src/resources/jelly.png"
            ), "Jelly", self)
        button_orange.triggered.connect(self.set_line_color_orange)
        self.color_toolbar.addAction(button_orange)

        button_red = QAction(
            QIcon(
                "/Users/hht/Desktop/hht_s/coding/FEMsimulate/src/resources/velocity.png"
            ), "Draw Velocity Vector", self)
        button_red.triggered.connect(self.set_line_color_red)
        self.color_toolbar.addAction(button_red)

        button_yellow = QAction(
            QIcon(
                "/Users/hht/Desktop/hht_s/coding/FEMsimulate/src/resources/add.png"
            ), "Add Custom Material", self)
        button_yellow.triggered.connect(self.set_line_color_yellow)
        self.color_toolbar.addAction(button_yellow)

    # Create figure toolbar
    def create_figure_toolbar(self):
        self.figure_toolbar = self.addToolBar("Figure Tools")

        # button for curve
        choose_curve_act = QAction(
            QIcon(
                "/Users/hht/Desktop/hht_s/coding/FEMsimulate/src/resources/curve_icon.png"
            ), "curve tool", self)
        choose_curve_act.triggered.connect(self.set_figure_tool_curve)
        self.figure_toolbar.addAction(choose_curve_act)

        # button for circle
        choose_circle_act = QAction(
            QIcon(
                "/Users/hht/Desktop/hht_s/coding/FEMsimulate/src/resources/circle_icon.png"
            ), "circle tool", self)
        choose_circle_act.triggered.connect(self.set_figure_tool_circle)
        self.figure_toolbar.addAction(choose_circle_act)

        # button for rectangle
        choose_rect_act = QAction(
            QIcon(
                "/Users/hht/Desktop/hht_s/coding/FEMsimulate/src/resources/rect_icon.png"
            ), "rect tool", self)
        choose_rect_act.triggered.connect(self.set_figure_tool_rect)
        self.figure_toolbar.addAction(choose_rect_act)

        # button for triangle
        # choose_tri_act = QAction(QIcon("resources/tri_icon.png"),
        #                          "triangle tool", self)
        # choose_tri_act.triggered.connect(self.set_figure_tool_tri)
        # self.figure_toolbar.addAction(choose_tri_act)

        # button for polygon
        # choose_poly_act = QAction(QIcon("resources/polygon_icon.png"),
        #                           "poly tool", self)
        # choose_poly_act.triggered.connect(self.set_figure_tool_poly)
        # self.figure_toolbar.addAction(choose_poly_act)

        # button for delete
        action_del = QAction(
            QIcon(
                "/Users/hht/Desktop/hht_s/coding/FEMsimulate/src/resources/del.png"
            ), "delete element", self)
        action_del.triggered.connect(self.set_figure_tool_del)
        self.figure_toolbar.addAction(action_del)

        # button for edit
        action_edit = QAction(
            QIcon(
                "/Users/hht/Desktop/hht_s/coding/FEMsimulate/src/resources/edit.png"
            ), "edit element's position", self)
        action_edit.triggered.connect(self.set_figure_tool_edit)
        self.figure_toolbar.addAction(action_edit)

        # button for undo
        action_undo = QAction(
            QIcon(
                "/Users/hht/Desktop/hht_s/coding/FEMsimulate/src/resources/undo.png"
            ), "undo painting", self)
        action_undo.triggered.connect(self.undo)
        self.figure_toolbar.addAction(action_undo)

        # button for clear
        action_clear = QAction(
            QIcon(
                "/Users/hht/Desktop/hht_s/coding/FEMsimulate/src/resources/clear.jpg"
            ), "clear paintings", self)
        action_clear.triggered.connect(self.clear)
        self.figure_toolbar.addAction(action_clear)

    def undo(self):
        self.controller.undo()

    def clear(self):
        self.controller.clearFigure()

    # Create simulation toolbar
    def create_simulation_toolbar(self):
        self.Simulation_toolbar = self.addToolBar("simulation toolbar")
        action_simulate = QAction(
            QIcon(
                "/Users/hht/Desktop/hht_s/coding/FEMsimulate/src/resources/simulate.jpg"
            ), "start simulation", self)
        action_simulate.triggered.connect(self.start_simulation)
        self.Simulation_toolbar.addAction(action_simulate)

        action_usingFEM = QAction(
            QIcon(
                "/Users/hht/Desktop/hht_s/coding/FEMsimulate/src/resources/FEM.jpg"
            ), "using FEM simulation", self)
        action_usingFEM.triggered.connect(self.fem_simulation)
        self.Simulation_toolbar.addAction(action_usingFEM)

        action_usingMPM = QAction(
            QIcon(
                "/Users/hht/Desktop/hht_s/coding/FEMsimulate/src/resources/MPM.png"
            ), "using MPM simulation", self)
        action_usingMPM.triggered.connect(self.mpm_simulation)
        self.Simulation_toolbar.addAction(action_usingMPM)

        action_mesh_simul = QAction(
            QIcon(
                "/Users/hht/Desktop/hht_s/coding/FEMsimulate/src/resources/mesh.png"
            ), "add mesh", self)
        action_mesh_simul.triggered.connect(self.add_mesh_simu)
        self.Simulation_toolbar.addAction(action_mesh_simul)

        action_pause_simul = QAction(
            QIcon(
                "/Users/hht/Desktop/hht_s/coding/FEMsimulate/src/resources/pause.png"
            ), "pause simulation", self)
        action_pause_simul.triggered.connect(self.pause_simulation)
        self.Simulation_toolbar.addAction(action_pause_simul)

        action_save_simul = QAction(
            QIcon(
                "/Users/hht/Desktop/hht_s/coding/FEMsimulate/src/resources/save.png"
            ), "save current scene", self)
        action_save_simul.triggered.connect(self.save_scene)
        self.Simulation_toolbar.addAction(action_save_simul)

        action_reset_simul = QAction(
            QIcon(
                "/Users/hht/Desktop/hht_s/coding/FEMsimulate/src/resources/reset.png"
            ), "reset simulation", self)
        action_reset_simul.triggered.connect(self.reset_simulation)
        self.Simulation_toolbar.addAction(action_reset_simul)

        action_clear_simul = QAction(
            QIcon(
                "/Users/hht/Desktop/hht_s/coding/FEMsimulate/src/resources/clear.png"
            ), "clear simulation", self)
        action_clear_simul.triggered.connect(self.clear_simulation)
        self.Simulation_toolbar.addAction(action_clear_simul)

        # def create_snow_type_toolbar(self):
        #     self.SnowType_toolbar = self.addToolBar("snow type toolbar")
        #     choose_snow_type = [None] * 6

        #     choose_snow_type[0] = QAction(QIcon(":/resources/num1.jpg"),
        #                                   "Lower Hardening", self)
        #     choose_snow_type[0].triggered.connect(self.set_snow_type_1)
        #     self.SnowType_toolbar.addAction(choose_snow_type[0])

        #     choose_snow_type[1] = QAction(QIcon(":/resources/num2.jpg"),
        #                                   "Lower Young's", self)
        #     choose_snow_type[1].triggered.connect(self.set_snow_type_2)
        #     self.SnowType_toolbar.addAction(choose_snow_type[1])

        #     choose_snow_type[2] = QAction(QIcon(":/resources/num3.jpg"),
        #                                   "Lower Critical Compression", self)
        #     choose_snow_type[2].triggered.connect(self.set_snow_type_3)
        #     self.SnowType_toolbar.addAction(choose_snow_type[2])

        #     choose_snow_type[3] = QAction(QIcon(":/resources/num4.jpg"),
        #                                   "Reference", self)
        #     choose_snow_type[3].triggered.connect(self.set_snow_type_4)
        #     self.SnowType_toolbar.addAction(choose_snow_type[3])

        #     choose_snow_type[4] = QAction(QIcon(":/resources/num5.jpg"),
        #                                   "Lower Critical Compression & Stretch",
        #                                   self)
        #     choose_snow_type[4].triggered.connect(self.set_snow_type_5)
        #     self.SnowType_toolbar.addAction(choose_snow_type[4])

        #     choose_snow_type[5] = QAction(QIcon(":/resources/num6.jpg"),
        #                                   "Lower Critical Stretch", self)
        #     choose_snow_type[5].triggered.connect(self.set_snow_type_6)
        #     self.SnowType_toolbar.addAction(choose_snow_type[5])

        # def set_snow_type_1(self):
        #     self.controller.set_snow_type(1)

        # def set_snow_type_2(self):
        #     self.controller.set_snow_type(2)

        # def set_snow_type_3(self):
        #     self.controller.set_snow_type(3)

        # def set_snow_type_4(self):
        #     self.controller.set_snow_type(4)

        # def set_snow_type_5(self):
        #     self.controller.set_snow_type(5)

        # def set_snow_type_6(self):
        # self.controller.set_snow_type(6)

    def start_simulation(self):
        self.controller.is_simulating = True
        self.controller.simulate()

    def fem_simulation(self):
        self.controller.usingFEM = True
        self.controller.usingMPM = False

    def mpm_simulation(self):
        self.controller.usingFEM = False
        self.controller.usingMPM = True

    def add_mesh_simu(self):
        if self.add_mesh_simu:
            self.add_mesh_simu = False
            self.controller.add_mesh = False
        else:
            self.add_mesh_simu = True
            self.controller.add_mesh = True

    def pause_simulation(self):
        self.controller.is_simulating = False

    def reset_simulation(self):
        self.controller.is_simulating = False
        self.controller.reset_simulation()

    def clear_simulation(self):
        self.controller.is_simulating = False
        self.controller.clear_simulation()


class SettingMatrial(QWidget):

    def __init__(self):
        super().__init__()
        self.newWindowUI()
        self.setWindowTitle("Setting Material")

    def set_rho(self, rho):
        r = "Denisty:" + str(rho / 10)
        self.rhow.setText(r)

    def set_yms(self, yms):
        y = "Young\'s modulus:" + str(yms)
        self.ymsw.setText(y)

    def set_prt(self, prt):
        p = "Possion ratio:" + str(prt / 100)
        self.prtw.setText(p)

    def newWindowUI(self):
        self.resize(300, 300)
        self.move(200, 200)
        layout = QVBoxLayout()
        self.rhow = QLabel("Denisty:1")
        self.rho = QSlider(Qt.Horizontal)
        self.rho.setRange(10, 100)
        self.rho.setSingleStep(1)
        self.rho.setStatusTip("denisty")
        self.rho.valueChanged.connect(self.set_rho)
        self.ymsw = QLabel("Young\'s modulus:1000")
        self.yms = QSlider(Qt.Horizontal)
        self.yms.setRange(1e3, 1e5)
        self.yms.setSingleStep(1e3)
        self.yms.setStatusTip("Young\'s modulus")
        self.yms.valueChanged.connect(self.set_yms)
        self.prtw = QLabel("Possion ratio:0.1")
        self.prt = QSlider(Qt.Horizontal)
        self.prt.setRange(10, 100)
        self.prt.setSingleStep(2)
        self.prt.setStatusTip("Possion ratio")
        self.prt.valueChanged.connect(self.set_prt)
        self.btn = QPushButton("Completed Setting Material", self)
        self.btn.clicked.connect(self.close)
        layout.addWidget(self.rhow)
        layout.addWidget(self.rho)
        layout.addWidget(self.ymsw)
        layout.addWidget(self.yms)
        layout.addWidget(self.prtw)
        layout.addWidget(self.prt)
        layout.addWidget(self.btn)
        self.setLayout(layout)
