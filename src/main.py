import sys
from mainwind import Minidraw
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    wind = Minidraw()
    wind.show()
    sys.exit(app.exec_())
