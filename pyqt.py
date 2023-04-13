import sys, math, sip

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from uiDemo11 import Ui_MainWindow  # 导入 uiDemo9.py 中的 Ui_MainWindow 界面类


class MyMainWindow(QMainWindow,
                   Ui_MainWindow):  # 继承 QMainWindow 类和 Ui_MainWindow 界面类

    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)  # 初始化父类
        self.setupUi(self)  # 继承 Ui_MainWindow 界面类

    def click_pushButton_01(self):  # 点击 pushButton_01 触发
        self.lineEdit.setText("1. 几何变换")
        self.plainTextEdit.appendPlainText("1.1 图像平移")
        self.stackedWidget.setCurrentIndex(0)  # 打开 stackedWidget > page_0
        return

    def click_pushButton_02(self):  # 点击 pushButton_02 触发
        self.lineEdit.setText("1. 几何变换")
        self.plainTextEdit.appendPlainText("1.2 图像缩放")
        self.stackedWidget.setCurrentIndex(0)  # 打开 stackedWidget > page_0
        self.label_1.setPixmap(QtGui.QPixmap("../image/fractal02.png"))
        return

    def click_pushButton_03(self):  # 点击 pushButton_03 触发
        self.lineEdit.setText("1. 几何变换")
        self.plainTextEdit.appendPlainText("1.3 图像转置缩放")
        self.label_1.setPixmap(QtGui.QPixmap("../image/fractal03.png"))
        return

    def click_pushButton_04(self):  # 点击 pushButton_04 触发
        self.lineEdit.setText("1. 几何变换")
        self.plainTextEdit.appendPlainText("1.4 图像旋转")
        self.label_1.setPixmap(QtGui.QPixmap("../image/fractal04.png"))
        return

    def click_pushButton_05(self):  # 点击 pushButton_05 触发
        self.lineEdit.setText("2. 图像增强")
        self.plainTextEdit.appendPlainText("2.1 灰度变换")
        self.stackedWidget.setCurrentIndex(1)  # 打开 stackedWidget > page_1
        self.label_2.setPixmap(QtGui.QPixmap("../image/fractal01.png"))
        self.label_2.setScaledContents(True)  # 图片自适应 QLabel 区域大小
        return

    def click_pushButton_06(self):  # 点击 pushButton_06 触发
        self.plainTextEdit.appendPlainText("2.2 直方图修正")
        self.label_3.setPixmap(QtGui.QPixmap("../image/fractal02.png"))
        return

    def click_pushButton_07(self):  # 点击 pushButton_07 触发
        self.plainTextEdit.appendPlainText("2.3 图像平滑")
        self.label_2.setPixmap(QtGui.QPixmap("../image/fractal03.png"))
        return

    def click_pushButton_08(self):  # 点击 pushButton_08 触发
        self.plainTextEdit.appendPlainText("2.4 图像锐化")
        self.label_3.setPixmap(QtGui.QPixmap("../image/fractal04.png"))
        return

    def click_pushButton_09(self):  # 点击 pushButton_09 触发
        self.lineEdit.setText("3. 频域处理")
        self.plainTextEdit.appendPlainText("3.1 傅立叶变换")
        self.stackedWidget.setCurrentIndex(2)  # 打开 stackedWidget > page_2
        self.label_4.setPixmap(QtGui.QPixmap("../image/fractal01.png"))
        self.label_5.setPixmap(QtGui.QPixmap("../image/fractal02.png"))
        self.label_6.setPixmap(QtGui.QPixmap("../image/fractal03.png"))
        self.label_7.setPixmap(QtGui.QPixmap("../image/fractal04.png"))
        return

    def click_pushButton_10(self):  # 点击 pushButton_10 触发
        self.plainTextEdit.appendPlainText("3.2 离散余弦")
        self.label_5.setPixmap(QtGui.QPixmap(""))
        self.label_6.setPixmap(QtGui.QPixmap(""))
        self.label_7.setPixmap(QtGui.QPixmap(""))
        return

    def trigger_actHelp(self):  # 动作 actHelp 触发
        QMessageBox.about(self, "About",
                          """数字图像处理工具箱 v1.0\nCopyright YouCans, XUPT 2021""")
        return


if __name__ == '__main__':

    app = QApplication(sys.argv)  # 在 QApplication 方法中使用，创建应用程序对象
    myWin = MyMainWindow()  # 实例化 MyMainWindow 类，创建主窗口
    myWin.show()  # 在桌面显示控件 myWin
    sys.exit(app.exec_())  # 结束进程，退出程序
