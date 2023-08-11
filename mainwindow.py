import os
from json import loads
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtGui import Qt, QFont, QAction, QIcon, QCursor
from PySide6.QtWidgets import (
    QMainWindow, QSplitter, QTreeWidget, QTreeWidgetItem, QComboBox, QPushButton, QToolBar, QStyle, QApplication
)
from pygit2 import GIT_BRANCH_ALL, GIT_BRANCH_LOCAL

from configdialog import ConfigureDialog
from git import discover_repo
from logwidget import LogWidget

__version__ = '0.0.1'


class RepoTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, parent, name, repo, log):
        super().__init__(parent)

        #print(self.parent)
        self.name = name
        self.repo = repo
        self.log = log
        status = self.repo.status(untracked_files='no')
        mod_files = len(status) > 0
        self.cur_branch = repo.head.shorthand

        self.setText(0, name)
        self.setText(1, self.cur_branch)

        self.branch_combo = QComboBox()
        branches = [b.decode() for b in self.repo.raw_listall_branches(GIT_BRANCH_LOCAL)]
        self.branch_combo.addItems(branches)
        self.branch_combo.setCurrentText(self.cur_branch)
        self.branch_combo.currentIndexChanged.connect(self.checkout_branch)
        self.treeWidget().setItemWidget(self, 2, self.branch_combo)

        self.setText(3, str(len(status)))
        self.setTextAlignment(3, Qt.AlignRight)

        # self.stash_button = QPushButton("Stash")
        # self.treeWidget().setItemWidget(self, 4, self.stash_button)

        if mod_files:
            bold_font = QFont()
            bold_font.setPointSize(12)
            bold_font.setBold(True)
            self.setFont(0, bold_font)
            self.setFont(1, bold_font)
            self.setFont(3, bold_font)
            self.branch_combo.setEnabled(False)
            # self.stash_button.setEnabled(True)
        else:
            # self.stash_button.setEnabled(False)
            self.branch_combo.setEnabled(True)


    def checkout_branch(self, index: int):
        current_branch = self.repo.lookup_branch(self.cur_branch)
        print(current_branch)
        checkout_branch = self.branch_combo.itemText(index)
        checkout_branch_ref = self.repo.lookup_branch(checkout_branch)
        self.log.info(f"{self.name}: Checking out branch {checkout_branch}...")
        self.repo.checkout(checkout_branch_ref)
        print(self.repo.head.shorthand)
        self.cur_branch = checkout_branch


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log = LogWidget()
        self.log.info(f"mrgit {__version__}")
        self.log.info("© 2023 Don Welch <dwelch91@gmail.com>")

        self.setWindowTitle(f"mrgit")

        self.toolbar = QToolBar("mrgit")
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        refresh_action = QAction(QIcon('assets/refresh.png'), "Refresh", self)
        refresh_action.triggered.connect(self.refresh_tree)
        self.toolbar.addAction(refresh_action)

        config_action = QAction(QIcon('assets/config.png'), "Configure...", self)
        config_action.triggered.connect(self.configure)
        self.toolbar.addAction(config_action)

        self.repo_roots = [Path('/home/dwelch/git'), Path('/home/dwelch/ze')]

        self.addToolBar(self.toolbar)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(4)
        self.tree.setColumnWidth(0, 400)
        self.tree.setColumnWidth(1, 300)
        self.tree.setColumnWidth(2, 300)
        self.tree.setColumnWidth(3, 80)
        # self.tree.setColumnWidth(4, 50)
        self.tree.setHeaderLabels(['repository', 'current branch', 'checkout branch', 'mod. files', 'stash'])
        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.addWidget(self.tree)
        self.splitter.addWidget(self.log)
        self.setCentralWidget(self.splitter)

        self.config_dir = Path.home() / '.config' / 'mrgit'
        self.config_file = self.config_dir / 'config.json'

        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True)

        self.log.info(f"Configuration file: {self.config_file}")

        QTimer.singleShot(0, self.refresh_tree)


    def configure(self):
        if self.config_file.exists():
            with open(self.config_file, 'rb') as f:
                config = loads(f.read())

        dlg = ConfigureDialog()
        if dlg.exec():
            # ...
            self.refresh_tree()


    def refresh_tree(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        try:
            self.tree.clear()
            for index, r in enumerate(self.repo_roots):
                item = QTreeWidgetItem([r.as_posix()])
                self.tree.insertTopLevelItem(index, item)
                for p in r.iterdir():
                    if p.is_dir():
                        repo = discover_repo(p)
                        if repo.path is not None:
                            repo_name = p.parts[-1]
                            child = RepoTreeWidgetItem(item, repo_name, repo, self.log)
                            item.addChild(child)

        finally:
            QApplication.restoreOverrideCursor()