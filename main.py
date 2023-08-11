import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from mainwindow import MainWindow


def main() -> int:
    app = QApplication([])
    app.setStyle('Material')
    font = QFont()
    font.setPointSize(12)
    app.setFont(font)
    widget = MainWindow()
    widget.resize(1440, 1024)
    widget.show()
    #app.processEvents()
    #latest_thread = LatestThread()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
