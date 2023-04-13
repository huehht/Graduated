from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1080, 768)
        MainWindow.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap("C:/Users/David/.designer/image/youcans.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(150, 0, 20, 680))
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.stackedWidget.setGeometry(QtCore.QRect(170, 0, 900, 680))
        self.stackedWidget.setObjectName("stackedWidget")
        self.page_0 = QtWidgets.QWidget()
        self.page_0.setObjectName("page_0")
        self.label_1 = QtWidgets.QLabel(self.page_0)
        self.label_1.setGeometry(QtCore.QRect(50, 0, 800, 600))
        self.label_1.setText("")
        self.label_1.setPixmap(QtGui.QPixmap("../image/iconJpeg.png"))
        self.label_1.setAlignment(QtCore.Qt.AlignCenter)
        self.label_1.setObjectName("label_1")
        self.stackedWidget.addWidget(self.page_0)
        self.page_1 = QtWidgets.QWidget()
        self.page_1.setObjectName("page_1")
        self.label_2 = QtWidgets.QLabel(self.page_1)
        self.label_2.setGeometry(QtCore.QRect(20, 20, 400, 300))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap("../image/iconPng.png"))
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.page_1)
        self.label_3.setGeometry(QtCore.QRect(450, 20, 400, 300))
        self.label_3.setText("")
        self.label_3.setPixmap(QtGui.QPixmap("../image/iconPng.png"))
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.formLayoutWidget = QtWidgets.QWidget(self.page_1)
        self.formLayoutWidget.setGeometry(QtCore.QRect(90, 430, 271, 131))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout_1 = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout_1.setContentsMargins(0, 0, 0, 0)
        self.formLayout_1.setObjectName("formLayout_1")
        self.label_11 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_11.setMinimumSize(QtCore.QSize(100, 35))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.formLayout_1.setWidget(0, QtWidgets.QFormLayout.LabelRole,
                                    self.label_11)
        self.spinBox = QtWidgets.QSpinBox(self.formLayoutWidget)
        self.spinBox.setMinimumSize(QtCore.QSize(0, 35))
        self.spinBox.setObjectName("spinBox")
        self.formLayout_1.setWidget(0, QtWidgets.QFormLayout.FieldRole,
                                    self.spinBox)
        self.label_12 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_12.setMinimumSize(QtCore.QSize(100, 35))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        self.formLayout_1.setWidget(1, QtWidgets.QFormLayout.LabelRole,
                                    self.label_12)
        self.spinBox_2 = QtWidgets.QSpinBox(self.formLayoutWidget)
        self.spinBox_2.setMinimumSize(QtCore.QSize(0, 35))
        self.spinBox_2.setObjectName("spinBox_2")
        self.formLayout_1.setWidget(1, QtWidgets.QFormLayout.FieldRole,
                                    self.spinBox_2)
        self.label_13 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_13.setMinimumSize(QtCore.QSize(100, 35))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        self.label_13.setFont(font)
        self.label_13.setObjectName("label_13")
        self.formLayout_1.setWidget(2, QtWidgets.QFormLayout.LabelRole,
                                    self.label_13)
        self.spinBox_3 = QtWidgets.QSpinBox(self.formLayoutWidget)
        self.spinBox_3.setMinimumSize(QtCore.QSize(0, 35))
        self.spinBox_3.setObjectName("spinBox_3")
        self.formLayout_1.setWidget(2, QtWidgets.QFormLayout.FieldRole,
                                    self.spinBox_3)
        self.formLayoutWidget_2 = QtWidgets.QWidget(self.page_1)
        self.formLayoutWidget_2.setGeometry(QtCore.QRect(470, 430, 271, 131))
        self.formLayoutWidget_2.setObjectName("formLayoutWidget_2")
        self.formLayout_2 = QtWidgets.QFormLayout(self.formLayoutWidget_2)
        self.formLayout_2.setContentsMargins(0, 0, 0, 0)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_14 = QtWidgets.QLabel(self.formLayoutWidget_2)
        self.label_14.setMinimumSize(QtCore.QSize(100, 35))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        self.label_14.setFont(font)
        self.label_14.setObjectName("label_14")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole,
                                    self.label_14)
        self.spinBox_4 = QtWidgets.QSpinBox(self.formLayoutWidget_2)
        self.spinBox_4.setMinimumSize(QtCore.QSize(0, 35))
        self.spinBox_4.setObjectName("spinBox_4")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole,
                                    self.spinBox_4)
        self.label_15 = QtWidgets.QLabel(self.formLayoutWidget_2)
        self.label_15.setMinimumSize(QtCore.QSize(100, 35))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        self.label_15.setFont(font)
        self.label_15.setObjectName("label_15")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole,
                                    self.label_15)
        self.spinBox_5 = QtWidgets.QSpinBox(self.formLayoutWidget_2)
        self.spinBox_5.setMinimumSize(QtCore.QSize(0, 35))
        self.spinBox_5.setObjectName("spinBox_5")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole,
                                    self.spinBox_5)
        self.label_16 = QtWidgets.QLabel(self.formLayoutWidget_2)
        self.label_16.setMinimumSize(QtCore.QSize(100, 35))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        self.label_16.setFont(font)
        self.label_16.setObjectName("label_16")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole,
                                    self.label_16)
        self.spinBox_6 = QtWidgets.QSpinBox(self.formLayoutWidget_2)
        self.spinBox_6.setMinimumSize(QtCore.QSize(0, 35))
        self.spinBox_6.setObjectName("spinBox_6")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole,
                                    self.spinBox_6)
        self.stackedWidget.addWidget(self.page_1)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.label_4 = QtWidgets.QLabel(self.page_2)
        self.label_4.setGeometry(QtCore.QRect(20, 20, 400, 300))
        self.label_4.setText("")
        self.label_4.setPixmap(QtGui.QPixmap("../image/iconPng.png"))
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.page_2)
        self.label_5.setGeometry(QtCore.QRect(450, 20, 400, 300))
        self.label_5.setText("")
        self.label_5.setPixmap(QtGui.QPixmap("../image/iconPng.png"))
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.page_2)
        self.label_6.setGeometry(QtCore.QRect(20, 350, 400, 300))
        self.label_6.setText("")
        self.label_6.setPixmap(QtGui.QPixmap("../image/iconPng.png"))
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.page_2)
        self.label_7.setGeometry(QtCore.QRect(450, 350, 400, 300))
        self.label_7.setText("")
        self.label_7.setPixmap(QtGui.QPixmap("../image/iconPng.png"))
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.stackedWidget.addWidget(self.page_2)
        self.toolBox = QtWidgets.QToolBox(self.centralwidget)
        self.toolBox.setGeometry(QtCore.QRect(10, 10, 141, 351))
        self.toolBox.setMinimumSize(QtCore.QSize(0, 351))
        self.toolBox.setStyleSheet("font: 10pt \"Arial\";")
        self.toolBox.setLineWidth(8)
        self.toolBox.setObjectName("toolBox")
        self.page_T1 = QtWidgets.QWidget()
        self.page_T1.setGeometry(QtCore.QRect(0, 0, 141, 171))
        self.page_T1.setMinimumSize(QtCore.QSize(0, 30))
        self.page_T1.setObjectName("page_T1")
        self.verticalLayoutWidget_4 = QtWidgets.QWidget(self.page_T1)
        self.verticalLayoutWidget_4.setGeometry(QtCore.QRect(0, 0, 131, 140))
        self.verticalLayoutWidget_4.setObjectName("verticalLayoutWidget_4")
        self.layout_T1 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_4)
        self.layout_T1.setContentsMargins(0, 0, 0, 0)
        self.layout_T1.setObjectName("layout_T1")
        self.pushButton_01 = QtWidgets.QPushButton(self.verticalLayoutWidget_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.pushButton_01.sizePolicy().hasHeightForWidth())
        self.pushButton_01.setSizePolicy(sizePolicy)
        self.pushButton_01.setMinimumSize(QtCore.QSize(60, 25))
        self.pushButton_01.setMaximumSize(QtCore.QSize(160, 60))
        self.pushButton_01.setObjectName("pushButton_01")
        self.layout_T1.addWidget(self.pushButton_01)
        self.pushButton_02 = QtWidgets.QPushButton(self.verticalLayoutWidget_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.pushButton_02.sizePolicy().hasHeightForWidth())
        self.pushButton_02.setSizePolicy(sizePolicy)
        self.pushButton_02.setMinimumSize(QtCore.QSize(60, 25))
        self.pushButton_02.setMaximumSize(QtCore.QSize(160, 60))
        self.pushButton_02.setObjectName("pushButton_02")
        self.layout_T1.addWidget(self.pushButton_02)
        self.pushButton_03 = QtWidgets.QPushButton(self.verticalLayoutWidget_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.pushButton_03.sizePolicy().hasHeightForWidth())
        self.pushButton_03.setSizePolicy(sizePolicy)
        self.pushButton_03.setMinimumSize(QtCore.QSize(60, 25))
        self.pushButton_03.setMaximumSize(QtCore.QSize(160, 60))
        self.pushButton_03.setObjectName("pushButton_03")
        self.layout_T1.addWidget(self.pushButton_03)
        self.pushButton_04 = QtWidgets.QPushButton(self.verticalLayoutWidget_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.pushButton_04.sizePolicy().hasHeightForWidth())
        self.pushButton_04.setSizePolicy(sizePolicy)
        self.pushButton_04.setMinimumSize(QtCore.QSize(60, 25))
        self.pushButton_04.setMaximumSize(QtCore.QSize(160, 60))
        self.pushButton_04.setObjectName("pushButton_04")
        self.layout_T1.addWidget(self.pushButton_04)
        self.toolBox.addItem(self.page_T1, "")
        self.page_T2 = QtWidgets.QWidget()
        self.page_T2.setGeometry(QtCore.QRect(0, 0, 141, 131))
        self.page_T2.setObjectName("page_T2")
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.page_T2)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(0, 0, 131, 140))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.layout_T2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.layout_T2.setContentsMargins(0, 0, 0, 0)
        self.layout_T2.setObjectName("layout_T2")
        self.pushButton_05 = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.pushButton_05.sizePolicy().hasHeightForWidth())
        self.pushButton_05.setSizePolicy(sizePolicy)
        self.pushButton_05.setMinimumSize(QtCore.QSize(60, 25))
        self.pushButton_05.setMaximumSize(QtCore.QSize(160, 60))
        self.pushButton_05.setObjectName("pushButton_05")
        self.layout_T2.addWidget(self.pushButton_05)
        self.pushButton_06 = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.pushButton_06.sizePolicy().hasHeightForWidth())
        self.pushButton_06.setSizePolicy(sizePolicy)
        self.pushButton_06.setMinimumSize(QtCore.QSize(60, 25))
        self.pushButton_06.setMaximumSize(QtCore.QSize(160, 60))
        self.pushButton_06.setObjectName("pushButton_06")
        self.layout_T2.addWidget(self.pushButton_06)
        self.pushButton_08 = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.pushButton_08.sizePolicy().hasHeightForWidth())
        self.pushButton_08.setSizePolicy(sizePolicy)
        self.pushButton_08.setMinimumSize(QtCore.QSize(60, 25))
        self.pushButton_08.setMaximumSize(QtCore.QSize(160, 60))
        self.pushButton_08.setObjectName("pushButton_08")
        self.layout_T2.addWidget(self.pushButton_08)
        self.pushButton_07 = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.pushButton_07.sizePolicy().hasHeightForWidth())
        self.pushButton_07.setSizePolicy(sizePolicy)
        self.pushButton_07.setMinimumSize(QtCore.QSize(60, 25))
        self.pushButton_07.setMaximumSize(QtCore.QSize(160, 60))
        self.pushButton_07.setObjectName("pushButton_07")
        self.layout_T2.addWidget(self.pushButton_07)
        self.toolBox.addItem(self.page_T2, "")
        self.page_T3 = QtWidgets.QWidget()
        self.page_T3.setGeometry(QtCore.QRect(0, 0, 141, 171))
        self.page_T3.setObjectName("page_T3")
        self.verticalLayoutWidget_5 = QtWidgets.QWidget(self.page_T3)
        self.verticalLayoutWidget_5.setGeometry(QtCore.QRect(0, 0, 131, 100))
        self.verticalLayoutWidget_5.setObjectName("verticalLayoutWidget_5")
        self.layout_T3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_5)
        self.layout_T3.setContentsMargins(0, 0, 0, 0)
        self.layout_T3.setObjectName("layout_T3")
        self.pushButton_09 = QtWidgets.QPushButton(self.verticalLayoutWidget_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.pushButton_09.sizePolicy().hasHeightForWidth())
        self.pushButton_09.setSizePolicy(sizePolicy)
        self.pushButton_09.setMinimumSize(QtCore.QSize(60, 25))
        self.pushButton_09.setMaximumSize(QtCore.QSize(160, 60))
        self.pushButton_09.setObjectName("pushButton_09")
        self.layout_T3.addWidget(self.pushButton_09)
        self.pushButton_10 = QtWidgets.QPushButton(self.verticalLayoutWidget_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.pushButton_10.sizePolicy().hasHeightForWidth())
        self.pushButton_10.setSizePolicy(sizePolicy)
        self.pushButton_10.setMinimumSize(QtCore.QSize(60, 25))
        self.pushButton_10.setMaximumSize(QtCore.QSize(160, 60))
        self.pushButton_10.setObjectName("pushButton_10")
        self.layout_T3.addWidget(self.pushButton_10)
        self.pushButton_11 = QtWidgets.QPushButton(self.verticalLayoutWidget_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.pushButton_11.sizePolicy().hasHeightForWidth())
        self.pushButton_11.setSizePolicy(sizePolicy)
        self.pushButton_11.setMinimumSize(QtCore.QSize(60, 25))
        self.pushButton_11.setMaximumSize(QtCore.QSize(160, 60))
        self.pushButton_11.setObjectName("pushButton_11")
        self.layout_T3.addWidget(self.pushButton_11)
        # self.pushButton_12 = QtWidgets.QPushButton(self.verticalLayoutWidget_5)
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
        #                                    QtWidgets.QSizePolicy.Fixed)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(
        #     self.pushButton_12.sizePolicy().hasHeightForWidth())
        # self.pushButton_12.setSizePolicy(sizePolicy)
        # self.pushButton_12.setMinimumSize(QtCore.QSize(60, 25))
        # self.pushButton_12.setMaximumSize(QtCore.QSize(160, 60))
        # self.pushButton_12.setObjectName("pushButton_12")
        # self.layout_T3.addWidget(self.pushButton_12)
        self.toolBox.addItem(self.page_T3, "")
        self.page_T4 = QtWidgets.QWidget()
        self.page_T4.setGeometry(QtCore.QRect(0, 0, 141, 171))
        self.page_T4.setObjectName("page_T4")
        self.verticalLayoutWidget_6 = QtWidgets.QWidget(self.page_T4)
        self.verticalLayoutWidget_6.setGeometry(QtCore.QRect(0, 0, 131, 71))
        self.verticalLayoutWidget_6.setObjectName("verticalLayoutWidget_6")
        self.layout_T4 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_6)
        self.layout_T4.setContentsMargins(0, 0, 0, 0)
        self.layout_T4.setObjectName("layout_T4")
        self.pushButton_13 = QtWidgets.QPushButton(self.verticalLayoutWidget_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.pushButton_13.sizePolicy().hasHeightForWidth())
        self.pushButton_13.setSizePolicy(sizePolicy)
        self.pushButton_13.setMinimumSize(QtCore.QSize(60, 25))
        self.pushButton_13.setMaximumSize(QtCore.QSize(160, 60))
        self.pushButton_13.setObjectName("pushButton_13")
        self.layout_T4.addWidget(self.pushButton_13)
        self.pushButton_14 = QtWidgets.QPushButton(self.verticalLayoutWidget_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.pushButton_14.sizePolicy().hasHeightForWidth())
        self.pushButton_14.setSizePolicy(sizePolicy)
        self.pushButton_14.setMinimumSize(QtCore.QSize(60, 25))
        self.pushButton_14.setMaximumSize(QtCore.QSize(160, 60))
        self.pushButton_14.setObjectName("pushButton_14")
        self.layout_T4.addWidget(self.pushButton_14)
        # self.pushButton_15 = QtWidgets.QPushButton(self.verticalLayoutWidget_6)
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
        #                                    QtWidgets.QSizePolicy.Fixed)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(
        #     self.pushButton_15.sizePolicy().hasHeightForWidth())
        # self.pushButton_15.setSizePolicy(sizePolicy)
        # self.pushButton_15.setMinimumSize(QtCore.QSize(60, 25))
        # self.pushButton_15.setMaximumSize(QtCore.QSize(160, 60))
        # self.pushButton_15.setObjectName("pushButton_15")
        # self.layout_T4.addWidget(self.pushButton_15)
        self.toolBox.addItem(self.page_T4, "")
        # self.page_T5 = QtWidgets.QWidget()
        # self.page_T5.setGeometry(QtCore.QRect(0, 0, 141, 171))
        # self.page_T5.setObjectName("page_T5")
        # self.toolBox.addItem(self.page_T5, "")
        self.page_T7 = QtWidgets.QWidget()
        self.page_T7.setGeometry(QtCore.QRect(0, 0, 141, 171))
        self.page_T7.setObjectName("page_T7")
        self.toolBox.addItem(self.page_T7, "")
        # self.verticalLayoutWidget_3 = QtWidgets.QWidget(self.centralwidget)
        # self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(
        #     10, 380, 141, 291))
        # self.verticalLayoutWidget_3.setObjectName("verticalLayoutWidget_3")
        # self.leftFrame_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_3)
        # self.leftFrame_2.setContentsMargins(0, 0, 0, 0)
        # self.leftFrame_2.setObjectName("leftFrame_2")
        # self.lineEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget_3)
        # self.lineEdit.setMinimumSize(QtCore.QSize(0, 30))
        # self.lineEdit.setObjectName("lineEdit")
        # self.leftFrame_2.addWidget(self.lineEdit)
        # self.plainTextEdit = QtWidgets.QPlainTextEdit(
        #     self.verticalLayoutWidget_3)
        # self.plainTextEdit.setObjectName("plainTextEdit")
        # self.leftFrame_2.addWidget(self.plainTextEdit)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1080, 23))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuQuit = QtWidgets.QMenu(self.menubar)
        self.menuQuit.setObjectName("menuQuit")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionOpen = QtWidgets.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("../image/iconOpen.png"),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOpen.setIcon(icon1)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave = QtWidgets.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("../image/iconSave.png"),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave.setIcon(icon2)
        self.actionSave.setObjectName("actionSave")
        self.actionClose = QtWidgets.QAction(MainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("../image/iconClose.png"),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionClose.setIcon(icon3)
        self.actionClose.setObjectName("actionClose")
        self.actionQuit = QtWidgets.QAction(MainWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("../image/iconQuit.png"),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionQuit.setIcon(icon4)
        self.actionQuit.setObjectName("actionQuit")
        self.actionSetup = QtWidgets.QAction(MainWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("../image/iconSetup.png"),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSetup.setIcon(icon5)
        self.actionSetup.setObjectName("actionSetup")
        self.actionHelp = QtWidgets.QAction(MainWindow)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("../image/iconHelp.png"),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionHelp.setIcon(icon6)
        self.actionHelp.setObjectName("actionHelp")
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionClose)
        self.menuQuit.addAction(self.actionQuit)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuQuit.menuAction())
        self.toolBar.addAction(self.actionOpen)
        self.toolBar.addAction(self.actionClose)
        self.toolBar.addAction(self.actionSave)
        self.toolBar.addAction(self.actionSetup)
        self.toolBar.addAction(self.actionHelp)
        self.toolBar.addAction(self.actionQuit)

        self.retranslateUi(MainWindow)
        self.stackedWidget.setCurrentIndex(0)
        self.toolBox.setCurrentIndex(0)
        self.actionQuit.triggered.connect(MainWindow.close)
        self.actionHelp.triggered.connect(MainWindow.trigger_actHelp)
        self.pushButton_01.clicked.connect(MainWindow.click_pushButton_01)
        self.pushButton_02.clicked.connect(MainWindow.click_pushButton_02)
        self.pushButton_03.clicked.connect(MainWindow.click_pushButton_03)
        self.pushButton_04.clicked.connect(MainWindow.click_pushButton_04)
        self.pushButton_05.clicked.connect(MainWindow.click_pushButton_05)
        self.pushButton_06.clicked.connect(MainWindow.click_pushButton_06)
        self.pushButton_07.clicked.connect(MainWindow.click_pushButton_07)
        self.pushButton_08.clicked.connect(MainWindow.click_pushButton_08)
        self.pushButton_09.clicked.connect(MainWindow.click_pushButton_09)
        self.pushButton_10.clicked.connect(MainWindow.click_pushButton_10)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "图形图像处理"))
        self.label_11.setText(_translate("MainWindow", "曝光："))
        self.label_12.setText(_translate("MainWindow", "亮度："))
        self.label_13.setText(_translate("MainWindow", "对比度："))
        self.label_14.setText(_translate("MainWindow", "锐化："))
        self.label_15.setText(_translate("MainWindow", "模糊："))
        self.label_16.setText(_translate("MainWindow", "杂点："))
        self.pushButton_01.setText(_translate("MainWindow", "绘制矩形"))
        self.pushButton_02.setText(_translate("MainWindow", "绘制圆形"))
        self.pushButton_03.setText(_translate("MainWindow", "绘制多边形"))
        self.pushButton_04.setText(_translate("MainWindow", "删除选择部分"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_T1),
                                 _translate("MainWindow", "1. 基础模型建立"))
        self.pushButton_05.setText(_translate("MainWindow", "导入模型"))
        self.pushButton_06.setText(_translate("MainWindow", "导出模型"))
        self.pushButton_08.setText(_translate("MainWindow", "材料设置"))
        self.pushButton_07.setText(_translate("MainWindow", "切换为3D模型"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_T2),
                                 _translate("MainWindow", "2. 模型具体设置"))
        self.pushButton_09.setText(_translate("MainWindow", "静态应力分析"))
        self.pushButton_10.setText(_translate("MainWindow", "施加荷载分析"))
        self.pushButton_11.setText(_translate("MainWindow", "空气动力模拟"))
        # self.pushButton_12.setText(_translate("MainWindow", "小波变换"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_T3),
                                 _translate("MainWindow", "3. 分析与模拟"))
        self.pushButton_13.setText(_translate("MainWindow", "结果展示"))
        self.pushButton_14.setText(_translate("MainWindow", "动画展示与导出"))
        # self.pushButton_15.setText(_translate("MainWindow", "空气动力模拟"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_T4),
                                 _translate("MainWindow", "4. 结果展示与动画导出"))
        # self.toolBox.setItemText(self.toolBox.indexOf(self.page_T5),
        #                          _translate("MainWindow", "5. 图像压缩"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_T7),
                                 _translate("MainWindow", "返回"))
        self.menuFile.setTitle(_translate("MainWindow", "文件"))
        self.menuQuit.setTitle(_translate("MainWindow", "退出"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.actionOpen.setText(_translate("MainWindow", "打开"))
        self.actionSave.setText(_translate("MainWindow", "保存"))
        self.actionClose.setText(_translate("MainWindow", "关闭"))
        self.actionQuit.setText(_translate("MainWindow", "退出"))
        self.actionSetup.setText(_translate("MainWindow", "设置"))
        self.actionHelp.setText(_translate("MainWindow", "帮助"))
