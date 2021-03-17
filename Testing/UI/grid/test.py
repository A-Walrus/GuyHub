import sys
from PyQt5 import QtWidgets


class IndicSelectWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(IndicSelectWindow, self).__init__(parent=parent)
        self.resize(500, 400)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.scrollArea = QtWidgets.QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.gridLayout = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.layout.addWidget(self.scrollArea)

        for i in range(5):
            for j in range(5):
            	widget=QtWidgets.QPushButton()
                self.gridLayout.addWidget(widget, i, j)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = IndicSelectWindow()
    w.show()
    sys.exit(app.exec_())