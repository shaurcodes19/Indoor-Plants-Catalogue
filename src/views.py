import os
from enum import global_enum

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QDialog, QPushButton, QScrollArea, QLineEdit, QFrame)
from PyQt5.QtCore import (Qt, pyqtSignal, QTimer, QPropertyAnimation,
                          QEasingCurve, QRect, QPoint, QParallelAnimationGroup)
from PyQt5.QtGui import QCursor, QPixmap
from PyQt5.QtGui import QCursor, QColor

from .ui_shared import GlassFrame, FlowLayout
from .core import Plant


def get_plant_image(plant_id):
    """
    Robust helper to find plant images.
    Checks relative to the script location (src/../assets) and current working directory.
    """
    # 1. Determine the directory where this file (views.py) lives
    current_file_dir = os.path.dirname(os.path.abspath(__file__))

    # 2. Determine project root (assuming views.py is in src/)
    project_root = os.path.dirname(current_file_dir)

    # 3. Define potential paths to the 'assets' folder
    candidate_dirs = [
        os.path.join(project_root, 'assets'),  # Project root assets (best practice)
        os.path.join(current_file_dir, 'assets'),  # Assets inside src
        os.path.join(os.getcwd(), 'assets'),  # Assets in current working dir
        'assets'  # Relative fallback
    ]

    # 4. Search for the image
    extensions = ['.png', '.jpg', '.jpeg']

    for folder in candidate_dirs:
        if os.path.isdir(folder):
            for ext in extensions:
                full_path = os.path.join(folder, f"{plant_id}{ext}")
                if os.path.exists(full_path):
                    return full_path
    return None


class PlantCard(GlassFrame):
    clicked = pyqtSignal(object, object)

    def __init__(self, plant: Plant):
        super().__init__()
        self.plant = plant
        self.setFixedSize(198, 180)
        self.setCursor(QCursor(Qt.PointingHandCursor))

        # Disable shadow for performance with large datasets
        self.setGraphicsEffect(None)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        self.name_label = QLabel(plant.name)
        self.name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")

        self.sci_label = QLabel(plant.scientific_name)
        self.sci_label.setStyleSheet("font-size: 12px; font-style: italic; color: #ddd;")

        try:
            stars = int(round(self.plant.rating))
        except (ValueError, TypeError):
            stars = 0

        rating_text = "★" * stars + "☆" * (5 - stars)
        self.rating_label = QLabel(f"{rating_text} ({self.plant.rating})")
        self.rating_label.setStyleSheet("color: #FFD700; font-size: 14px;")

        tags_layout = QHBoxLayout()

        o2_tag = QLabel("O₂")
        o2_tag.setToolTip(f"O₂ Release: {plant.o2_data} ml/day")
        o2_tag.setStyleSheet(self._get_tag_style(plant.o2_data, is_o2=True))
        o2_tag.setFixedSize(30, 20)
        o2_tag.setAlignment(Qt.AlignCenter)
        tags_layout.addWidget(o2_tag)

        tags_layout.addSpacing(5)
        co2_tag = QLabel("CO₂")
        co2_tag.setToolTip(f"CO₂ Absorption: {plant.co2_data} mg/day")
        co2_tag.setStyleSheet(self._get_tag_style(plant.co2_data, is_o2=False))
        co2_tag.setFixedSize(30, 20)
        co2_tag.setAlignment(Qt.AlignCenter)
        tags_layout.addWidget(co2_tag)

        tags_layout.addStretch()

        layout.addWidget(self.name_label)
        layout.addWidget(self.sci_label)
        layout.addSpacing(5)
        layout.addWidget(self.rating_label)
        layout.addStretch()
        layout.addLayout(tags_layout)

    def _get_tag_style(self, data, is_o2=True):
        try:
            clean_str = str(data).split()[0]
            val = float(clean_str)

            c_best, c_good, c_mid, c_low, c_bad = ("#145A32", "#27AE60", "#F1C40F", "#E67E22", "#C0392B")

            if is_o2:
                col = c_best if val >= 4.0 else c_good if val >= 3.0 else c_mid if val >= 2.0 else c_low if val >= 1.0 else c_bad
            else:
                col = c_best if val >= 2.8 else c_good if val >= 2.1 else c_mid if val >= 1.4 else c_low if val >= 0.7 else c_bad

            text_col = "black" if col == "#F1C40F" else "white"
            return f"background-color: {col}; color: {text_col}; border-radius: 4px; font-weight: bold; font-size: 10px;"
        except (ValueError, TypeError, IndexError):
            d = str(data).lower()
            if "very high" in d: return "background-color: #145A32; color: white; border-radius: 4px;"
            if "high" in d:
                return "background-color: #2ECC71; color: black; border-radius: 4px;"
            elif "moderate" in d:
                return "background-color: #F1C40F; color: black; border-radius: 4px;"
            else:
                return "background-color: #E74C3C; color: white; border-radius: 4px;"

    def mousePressEvent(self, event):
        self.clicked.emit(self.plant, self)

    def enterEvent(self, event):
        self.setStyleSheet(
            ".GlassFrame { background-color: rgba(255, 255, 255, 50); border: 1px solid rgba(255, 255, 255, 100); border-radius: 16px; }")
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(
            ".GlassFrame { background-color: rgba(255, 255, 255, 30); border: 1px solid rgba(255, 255, 255, 60); border-radius: 16px; }")
        super().leaveEvent(event)

class DetailModal(QDialog):
    def __init__(self, plant: Plant, parent=None, start_geometry=None):

        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.start_geometry = start_geometry
        self.target_width = 450
        self.target_height = 600
        self.resize(self.target_width, self.target_height)

        container = GlassFrame(self)
        layout_wrap = QVBoxLayout(self)
        layout_wrap.setContentsMargins(0, 0, 0, 0)
        layout_wrap.addWidget(container)

        container.setStyleSheet(
            ".GlassFrame { background-color: rgba(20, 30, 40, 230); border: 1px solid rgba(255,255,255,50); border-radius: 20px; }")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)

        # Header with Close Button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.close_animated)
        close_btn.setStyleSheet("""
            QPushButton { background: transparent; color: white; font-size: 24px; border: none; }
            QPushButton:hover { color: #ff6b6b; }
        """)

        header = QHBoxLayout()
        header.addStretch()
        header.addWidget(close_btn)
        layout.addLayout(header)

        # Image for Modal
        img_label = QLabel()
        img_label.setFixedSize(390, 220)
        img_label.setAlignment(Qt.AlignCenter)
        img_label.setStyleSheet("background-color: rgba(0,0,0,0.3); border-radius: 10px;")

        # Load Image logic for Modal
        img_path = get_plant_image(plant.id)

        if img_path:
            pix = QPixmap(img_path)
            if not pix.isNull():
                scaled = pix.scaled(img_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                img_label.setPixmap(scaled)

        layout.addWidget(img_label, alignment=Qt.AlignCenter)
        layout.addSpacing(15)

        # Text Info
        name = QLabel(plant.name)
        name.setStyleSheet("font-size: 28px; font-weight: bold; color: white; margin-bottom: 5px;")
        name.setWordWrap(True)

        sci = QLabel(plant.scientific_name)
        sci.setStyleSheet("font-size: 16px; font-style: italic; color: #aaa; margin-bottom: 15px;")

        desc = QLabel(plant.description)
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 14px; color: #ddd; line-height: 1.4;")

        stats_box = QFrame()
        stats_box.setStyleSheet("background-color: rgba(255,255,255,10); border-radius: 10px; padding: 10px;")
        stats_layout = QVBoxLayout(stats_box)

        def make_stat(label, value):
            lbl = QLabel(f"<b>{label}:</b> {value}")
            lbl.setStyleSheet("color: #eee; font-size: 13px;")
            return lbl

        stats_layout.addWidget(make_stat("O₂ Release", f"{plant.o2_data} ml/day"))
        stats_layout.addWidget(make_stat("CO₂ Absorb", f"{plant.co2_data} mg/day"))
        stats_layout.addWidget(make_stat("Rating", f"{plant.rating}/5"))

        layout.addWidget(name)
        layout.addWidget(sci)
        layout.addWidget(stats_box)
        layout.addSpacing(15)
        layout.addWidget(desc)
        layout.addStretch()

    def showEvent(self, event):
        if self.start_geometry:
            self.animate_open()
        super().showEvent(event)

    def animate_open(self):
        parent_rect = self.parent().rect()
        end_x = (parent_rect.width() - self.target_width) // 2
        end_y = (parent_rect.height() - self.target_height) // 2
        end_rect = QRect(end_x, end_y, self.target_width, self.target_height)

        self.setGeometry(self.start_geometry)

        self.anim_group = QParallelAnimationGroup(self)

        geo_anim = QPropertyAnimation(self, b"geometry")
        geo_anim.setDuration(350)
        geo_anim.setStartValue(self.start_geometry)
        geo_anim.setEndValue(end_rect)
        geo_anim.setEasingCurve(QEasingCurve.OutExpo)

        op_anim = QPropertyAnimation(self, b"windowOpacity")
        op_anim.setDuration(250)
        op_anim.setStartValue(0.0)
        op_anim.setEndValue(1.0)

        self.anim_group.addAnimation(geo_anim)
        self.anim_group.addAnimation(op_anim)
        self.anim_group.start()

    def close_animated(self):
        if self.start_geometry:
            self.anim_group = QParallelAnimationGroup(self)

            geo_anim = QPropertyAnimation(self, b"geometry")
            geo_anim.setDuration(250)
            geo_anim.setStartValue(self.geometry())
            geo_anim.setEndValue(self.start_geometry)
            geo_anim.setEasingCurve(QEasingCurve.InQuad)

            op_anim = QPropertyAnimation(self, b"windowOpacity")
            op_anim.setDuration(200)
            op_anim.setStartValue(1.0)
            op_anim.setEndValue(0.0)

            self.anim_group.addAnimation(geo_anim)
            self.anim_group.addAnimation(op_anim)
            self.anim_group.finished.connect(self.accept)
            self.anim_group.start()
        else:
            self.accept()


class BaseTab(QWidget):
    def __init__(self, data_manager):
        super().__init__()
        self.dm = data_manager
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 80)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search plants...")
        self.search_bar.textChanged.connect(self.on_search_changed)
        self.layout.addWidget(self.search_bar)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #ddd; font-size: 12px; margin-left: 5px; font-style: italic;")
        self.layout.addWidget(self.status_label)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.content_widget = QWidget()

        self.flow_layout = FlowLayout(self.content_widget)

        self.scroll.setWidget(self.content_widget)
        self.layout.addWidget(self.scroll)

        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(150)
        self.search_timer.timeout.connect(self.perform_search)

    def on_search_changed(self):
        self.search_timer.start()

    def perform_search(self):
        raise NotImplementedError

    def populate_grid(self, plants):
        self._clear_layout()

        for p in plants:
            card = PlantCard(p)
            card.clicked.connect(self.open_detail)
            self.flow_layout.addWidget(card)

        self.content_widget.updateGeometry()
        self.status_label.setText(f"Found {len(plants)} plants.")

    def _clear_layout(self):
        if self.content_widget.layout():
            layout = self.content_widget.layout()
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().setParent(None)
                    item.widget().deleteLater()

    def open_detail(self, plant, card_widget):
        main_window = self.window()
        pos = card_widget.mapTo(main_window, QPoint(0, 0))
        start_geo = QRect(pos, card_widget.size())
        dialog = DetailModal(plant, main_window, start_geometry=start_geo)
        dialog.exec_()


class HomeTab(BaseTab):
    def __init__(self, data_manager):
        super().__init__(data_manager)

        self.setObjectName("HomeTab")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setStyleSheet("""
            #HomeTab {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #093637, stop:1 #44a08d);
            }
        """)

        self.search_bar.setPlaceholderText("Search top recommendations...")

        QWidget().setLayout(self.flow_layout)
        self.list_layout = QVBoxLayout(self.content_widget)
        self.list_layout.setAlignment(Qt.AlignTop)
        self.list_layout.setSpacing(10)

        QTimer.singleShot(100, self.perform_search)

    def perform_search(self):
        text = self.search_bar.text()
        if not text:
            results = self.dm.get_top_10()
            self.status_label.setText("Top 10 Leaderboard")
        else:
            results = self.dm.search(text)
            self.status_label.setText(f"Found {len(results)} matches.")

        self.populate_leaderboard(results)

    def populate_leaderboard(self, plants):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
                item.widget().deleteLater()

        for idx, p in enumerate(plants):
            row = RankedPlantRow(p, rank=idx + 1)
            row.clicked.connect(self.open_detail)
            self.list_layout.addWidget(row)

        self.content_widget.updateGeometry()

    def populate_grid(self, plants):
        self.populate_leaderboard(plants)


class ListTab(BaseTab):
    def __init__(self, data_manager):
        super().__init__(data_manager)
        self.search_bar.setPlaceholderText("Search library...")
        QTimer.singleShot(100, self.perform_search)

    def perform_search(self):
        text = self.search_bar.text()
        results = self.dm.search_all(text)
        self.populate_grid(results)