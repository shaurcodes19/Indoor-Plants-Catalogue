import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QStackedWidget,
                             QPushButton, QHBoxLayout, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core import DataManager
from src.ui_shared import STYLES
from src.views import HomeTab, ListTab


class FloatingNavBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 60)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 200);
                border-radius: 30px;
                border: 1px solid rgba(255, 255, 255, 150);
            }
            QPushButton {
                background: transparent;
                border: none;
                font-weight: bold;
                color: #555;
                font-size: 14px;
                border-radius: 20px;
            }
            QPushButton:checked {
                background-color: #2C3E50;
                color: white;
            }
            QPushButton:hover:!checked {
                background-color: rgba(0,0,0,10);
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(Qt.black)
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        self.btn_home = QPushButton("Home")
        self.btn_home.setCheckable(True)
        self.btn_home.setFixedSize(90, 40)

        self.btn_list = QPushButton("List")
        self.btn_list.setCheckable(True)
        self.btn_list.setFixedSize(90, 40)

        layout.addWidget(self.btn_home)
        layout.addWidget(self.btn_list)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Indoor Plants Catalogue")
        self.resize(1000, 700)

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(base_dir, "data", "plants_data_new.csv")

        if not os.path.exists(data_path):
            data_path = os.path.join(base_dir, "data", "plants.csv")

        self.dm = DataManager(data_path)
        self.setStyleSheet(STYLES)

        self.stack = QStackedWidget()
        self.home_tab = HomeTab(self.dm)
        self.list_tab = ListTab(self.dm)

        self.stack.addWidget(self.home_tab)
        self.stack.addWidget(self.list_tab)
        self.setCentralWidget(self.stack)

        self.navbar = FloatingNavBar(self)
        self.navbar.btn_home.setChecked(True)
        self.navbar.btn_home.clicked.connect(lambda: self.switch_tab(0))
        self.navbar.btn_list.clicked.connect(lambda: self.switch_tab(1))

    def switch_tab(self, index):
        if index == 0:
            self.stack.setCurrentWidget(self.home_tab)
            self.navbar.btn_home.setChecked(True)
            self.navbar.btn_list.setChecked(False)
        else:
            self.stack.setCurrentWidget(self.list_tab)
            self.navbar.btn_list.setChecked(True)
            self.navbar.btn_home.setChecked(False)

    def resizeEvent(self, event):
        nav_w = self.navbar.width()
        nav_h = self.navbar.height()

        x_pos = (self.width() - nav_w) // 2
        y_pos = self.height() - nav_h - 30

        self.navbar.move(x_pos, y_pos)
        self.navbar.raise_()
        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())