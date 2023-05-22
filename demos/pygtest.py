from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QPainterPath
from PyQt5.QtCore import Qt, QPoint
import sys


class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.point1 = QPoint()
        self.point2 = QPoint()
        self.point3 = QPoint()
        self.dic = {
            1: self.point1,
            2: self.point2,
            3: self.point3
        }  #记录三个坐标,分别是起点,控制点,终点
        self.count = 0
        self.initUI()
        print(self.dic[1])

    def initUI(self):
        self.setGeometry(300, 300, 380, 250)
        self.setWindowTitle('Bézier curve')
        self.show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawBezierCurve(qp)  #绘制贝塞尔曲线
        qp.end()

    def drawBezierCurve(self, qp):
        path = QPainterPath()
        path.moveTo(self.dic[1])
        path.cubicTo(self.dic[1], self.dic[2],
                     self.dic[3])  #绘制贝塞尔曲线需要提供三个点,起点,控制点和终点
        qp.drawPath(path)

    def mousePressEvent(self, event):  # 重写鼠标按下事件
        if event.button() == Qt.LeftButton:
            self.count += 1
            self.dic[self.count] = event.pos()  #获取当前点击的坐标
            if self.count == 3:
                self.count = 0
                self.update()  #触发绘制事件用update函数


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())