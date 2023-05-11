from PyQt5 import *
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys


class saveGui(QDialog):
    def __init__(self):
        super(saveGui, self).__init__()
        loadUi('saveGui.ui', self)
        self.setWindowTitle('Saving Video')
        self.setWindowIcon(QIcon('img/save_icon.png'))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = saveGui()
    window.show()
    sys.exit(app.exec_())
