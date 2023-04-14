from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from figures import Figure


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # 设置主窗口的标题
        self.setWindowTitle("Figure Drawer")

        # 设置中央 widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 垂直布局
        self.v_layout = QVBoxLayout()
        self.central_widget.setLayout(self.v_layout)

        # 创建画布
        self.canvas = Canvas()
        self.v_layout.addWidget(self.canvas)

        # 水平布局 - 操作按钮
        self.button_layout = QHBoxLayout()
        self.v_layout.addLayout(self.button_layout)

        # 画线按钮
        self.line_button = QPushButton("Line")
        self.line_button.clicked.connect(self.canvas.draw_line)
        self.button_layout.addWidget(self.line_button)

        # 画矩形按钮
        self.rect_button = QPushButton("Rectangle")
        self.rect_button.clicked.connect(self.canvas.draw_rect)
        self.button_layout.addWidget(self.rect_button)

        # 清空按钮
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.canvas.clear)
        self.button_layout.addWidget(self.clear_button)


class Canvas(QWidget):

    def __init__(self):
        super().__init__()
        self.current_figure = None  # 设置 current_figure 的默认值
        # 多边形列表
        self.figures = []

        # 鼠标按下的起始点
        self.start_point = None

        # 设置画布背景色为白色
        self.setAutoFillBackground(True)
        self.setStyleSheet("background-color: white;")

    def mousePressEvent(self, event):
        self.start_point = event.pos()

    def mouseReleaseEvent(self, event):
        end_point = event.pos()

        # 添加已画好的图形到列表中
        if self.current_figure is not None:
            self.current_figure.add_point(end_point)
            self.figures.append(self.current_figure)

        self.current_figure = None
        self.start_point = None

        self.update()  # 重绘画布

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen()
        for fig in self.figures:
            pen.setWidth(fig.get_width())
            pen.setColor(fig.get_color())
            painter.setPen(pen)
            fig.draw(painter)

        if self.current_figure is not None:
            pen.setWidth(self.current_figure.get_width())
            pen.setColor(self.current_figure.get_color())
            painter.setPen(pen)
            self.current_figure.draw_dynamic(painter, self.start_point)

    def draw_line(self):
        self.current_figure = Figure(self.start_point)
        self.current_figure.set_width(3)
        self.current_figure.set_color(QColor(255, 0, 0))

    def draw_rect(self):
        self.current_figure = Figure(self.start_point)
        self.current_figure.set_width(2)
        self.current_figure.set_color(QColor(0, 255, 0))

    def clear(self):
        self.figures.clear()
        self.current_figure = None
        self.update()


if __name__ == "__main__":
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec_()
