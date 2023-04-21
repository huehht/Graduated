import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QToolBar, QAction, QSlider
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt
from maincontroller import FigureType, MatterType, Minidraw_controller


class Minidraw(QMainWindow):

    def __init__(self, parent=None):
        super(Minidraw, self).__init__(parent)
        self.ui = Ui_Minidraw()
        self.ui.setupUi(self)
        self.controller = Minidraw_controller()
        self.setCentralWidget(self.controller)
        self.setWindowTitle("Qtaichi")  # add title
        self.setWindowIcon(QIcon(":/resources/icon.png"))  # add icon

        self.create_toolbar()
        self.create_figure_toolbar()
        self.create_simulation_toolbar()
        self.create_snow_type_toolbar()

    def __del__(self):
        del self.ui

    def set_line_width(self, width):
        self.controller.current_line_width = width

    def save_scene(self):
        self.controller.save_scene()

    # Set line colors
    def set_line_color_red(self):
        self.controller.current_line_color = Qt.red
        self.controller.current_figure_type = FigureType.Line

    def set_line_color_blue(self):
        self.controller.current_line_color = QColor(0x87CEFA)
        self.controller.current_figure_type = FigureType.Curve

    def set_line_color_green(self):
        self.controller.current_line_color = Qt.green

    def set_line_color_orange(self):
        self.controller.current_line_color = QColor(0xED553B)
        self.controller.current_figure_type = FigureType.Curve

    def set_line_color_black(self):
        self.controller.current_line_color = Qt.black
        self.controller.current_figure_type = FigureType.Curve

    def set_line_color_yellow(self):
        self.controller.current_line_color = Qt.yellow

    def set_line_color_white(self):
        self.controller.current_line_color = Qt.white
        self.controller.current_figure_type = FigureType.Curve

    # Set figure type
    def set_figure_tool_line(self):
        self.controller.current_figure_type = FigureType.Line
        self.controller.isAdding = True

    def set_figure_tool_rect(self):
        self.controller.current_figure_type = FigureType.Rectangle
        self.controller.isAdding = True

    def set_figure_tool_circle(self):
        self.controller.current_figure_type = FigureType.Circle
        self.controller.isAdding = True

    def set_figure_tool_curve(self):
        self.controller.current_figure_type = FigureType.Curve
        self.controller.isAdding = True

    def set_figure_tool_ellipse(self):
        self.controller.current_figure_type = FigureType.Ellipse
        self.controller.isAdding = True

    def set_figure_tool_tri(self):
        self.controller.current_figure_type = FigureType.Triangle
        self.controller.isAdding = True

    def set_figure_tool_poly(self):
        self.controller.current_figure_type = FigureType.Polygon
        self.controller.isAdding = True

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
        button_black = QAction(QIcon(":/resources/solid.png"), "Solid", self)
        button_black.triggered.connect(self.set_line_color_black)
        self.color_toolbar.addAction(button_black)

        button_white = QAction(QIcon(":/resources/snow.png"), "Snow", self)
        button_white.triggered.connect(self.set_line_color_white)
        self.color_toolbar.addAction(button_white)

        button_blue = QAction(QIcon(":/resources/fluid.png"), "Fluid", self)
        button_blue.triggered.connect(self.set_line_color_blue)
        self.color_toolbar.addAction(button_blue)

        button_orange = QAction(QIcon(":/resources/jelly.png"), "Jelly", self)
        button_orange.triggered.connect(self.set_line_color_orange)
        self.color_toolbar.addAction(button_orange)

        button_red = QAction(QIcon(":/resources/velocity.png"),
                             "Draw Velocity Vector", self)
        button_red.triggered.connect(self.set_line_color_red)
        self.color_toolbar.addAction(button_red)

    # Create figure toolbar
    def create_figure_toolbar(self):
        self.figure_toolbar = self.addToolBar("Figure Tools")

        # button for curve
        choose_curve_act = QAction(QIcon(":/resources/curve_icon.png"),
                                   "curve tool", self)
        choose_curve_act.triggered.connect(self.set_figure_tool_curve)
        self.figure_toolbar.addAction(choose_curve_act)

        # button for circle
        choose_circle_act = QAction(QIcon(":/resources/circle_icon.png"),
                                    "circle tool", self)
        choose_circle_act.triggered.connect(self.set_figure_tool_circle)
        self.figure_toolbar.addAction(choose_circle_act)

        # button for rectangle
        choose_rect_act = QAction(QIcon(":/resources/rect_icon.png"),
                                  "rect tool", self)
        choose_rect_act.triggered.connect(self.set_figure_tool_rect)
        self.figure_toolbar.addAction(choose_rect_act)

        # button for triangle
        choose_tri_act = QAction(QIcon(":/resources/tri_icon.png"),
                                 "triangle tool", self)
        choose_tri_act.triggered.connect(self.set_figure_tool_tri)
        self.figure_toolbar.addAction(choose_tri_act)

        # button for polygon
        choose_poly_act = QAction(QIcon(":/resources/polygon_icon.png"),
                                  "poly tool", self)
        choose_poly_act.triggered.connect(self.set_figure_tool_poly)
        self.figure_toolbar.addAction(choose_poly_act)

        # button for delete
        action_del = QAction(QIcon(":/resources/del.png"), "delete element",
                             self)
        action_del.triggered.connect(self.set_figure_tool_del)
        self.figure_toolbar.addAction(action_del)

        # button for edit
        action_edit = QAction(QIcon(":/resources/edit.png"),
                              "edit element's position", self)
        action_edit.triggered.connect(self.set_figure_tool_edit)
        self.figure_toolbar.addAction(action_edit)

        # button for undo
        action_undo = QAction(QIcon(":/resources/undo.png"), "undo painting",
                              self)
        action_undo.triggered.connect(self.undo)
        self.figure_toolbar.addAction(action_undo)

        # button for clear
        action_clear = QAction(QIcon(":/resources/clear.jpg"),
                               "clear paintings", self)
        action_clear.triggered.connect(self.clear)
        self.figure_toolbar.addAction(action_clear)

    def undo(self):
        self.controller.undo()

    def clear(self):
        self.controller.clearFigure()

    # Create simulation toolbar
    def create_simulation_toolbar(self):
        self.Simulation_toolbar = self.addToolBar("simulation toolbar")
        action_simulate = QAction(QIcon(":/resources/simulate.jpg"),
                                  "start simulation", self)
        action_simulate.triggered.connect(self.start_simulation)
        self.Simulation_toolbar.addAction(action_simulate)

        action_pause_simul = QAction(QIcon(":/resources/pause.png"),
                                     "pause simulation", self)
        action_pause_simul.triggered.connect(self.pause_simulation)
        self.Simulation_toolbar.addAction(action_pause_simul)

        action_save_simul = QAction(QIcon(":/resources/save.png"),
                                    "save current scene", self)
        action_save_simul.triggered.connect(self.save_scene)
        self.Simulation_toolbar.addAction(action_save_simul)

        action_reset_simul = QAction(QIcon(":/resources/reset.png"),
                                     "reset simulation", self)
        action_reset_simul.triggered.connect(self.reset_simulation)
        self.Simulation_toolbar.addAction(action_reset_simul)

        action_clear_simul = QAction(QIcon(":/resources/clear.png"),
                                     "clear simulation", self)
        action_clear_simul.triggered.connect(self.clear_simulation)
        self.Simulation_toolbar.addAction(action_clear_simul)

    def create_snow_type_toolbar(self):
        self.SnowType_toolbar = self.addToolBar("snow type toolbar")
        choose_snow_type = [None] * 6

        choose_snow_type[0] = QAction(QIcon(":/resources/num1.jpg"),
                                      "Lower Hardening", self)
        choose_snow_type[0].triggered.connect(self.set_snow_type_1)
        self.SnowType_toolbar.addAction(choose_snow_type[0])

        choose_snow_type[1] = QAction(QIcon(":/resources/num2.jpg"),
                                      "Lower Young's", self)
        choose_snow_type[1].triggered.connect(self.set_snow_type_2)
        self.SnowType_toolbar.addAction(choose_snow_type[1])

        choose_snow_type[2] = QAction(QIcon(":/resources/num3.jpg"),
                                      "Lower Critical Compression", self)
        choose_snow_type[2].triggered.connect(self.set_snow_type_3)
        self.SnowType_toolbar.addAction(choose_snow_type[2])

        choose_snow_type[3] = QAction(QIcon(":/resources/num4.jpg"),
                                      "Reference", self)
        choose_snow_type[3].triggered.connect(self.set_snow_type_4)
        self.SnowType_toolbar.addAction(choose_snow_type[3])

        choose_snow_type[4] = QAction(QIcon(":/resources/num5.jpg"),
                                      "Lower Critical Compression & Stretch",
                                      self)
        choose_snow_type[4].triggered.connect(self.set_snow_type_5)
        self.SnowType_toolbar.addAction(choose_snow_type[4])

        choose_snow_type[5] = QAction(QIcon(":/resources/num6.jpg"),
                                      "Lower Critical Stretch", self)
        choose_snow_type[5].triggered.connect(self.set_snow_type_6)
        self.SnowType_toolbar.addAction(choose_snow_type[5])

    def set_snow_type_1(self):
        self.controller.set_snow_type(1)

    def set_snow_type_2(self):
        self.controller.set_snow_type(2)

    def set_snow_type_3(self):
        self.controller.set_snow_type(3)

    def set_snow_type_4(self):
        self.controller.set_snow_type(4)

    def set_snow_type_5(self):
        self.controller.set_snow_type(5)

    def set_snow_type_6(self):
        self.controller.set_snow_type(6)

    def start_simulation(self):
        self.controller.is_simulating = True
        self.controller.simulate()

    def pause_simulation(self):
        self.controller.is_simulating = False

    def reset_simulation(self):
        self.controller.is_simulating = False
        self.controller.reset_simulation()

    def clear_simulation(self):
        self.controller.is_simulating = False
        self.controller.clear_simulation()
