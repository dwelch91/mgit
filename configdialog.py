from PySide6.QtWidgets import QDialog


class ConfigureDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('mrgit - Configure')

