from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QDialog, QPushButton, QScrollArea, QLineEdit, QFrame)
from PyQt5.QtCore import (Qt, pyqtSignal, QTimer, QPropertyAnimation,
                          QEasingCurve, QRect, QPoint, QParallelAnimationGroup)
from PyQt5.QtGui import QCursor

from .ui_shared import GlassFrame, FlowLayout
from .core import Plant


class PlantCard(GlassFrame):
    clicked = pyqtSignal(object, object)

    def __init__(self, plant: Plant):
        super().__init__()
        self.plant = plant
        self.setFixedSize(198, 180)
        self.setCursor(QCursor(Qt.PointingHandCursor))

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

            # Colors: Best -> Worst
            c_best = ("#145A32", "white")
            c_good = ("#27AE60", "white")
            c_mid = ("#F1C40F", "black")
            c_low = ("#E67E22", "white")
            c_bad = ("#C0392B", "white")

            if is_o2:
                if val >= 4.0:
                    bg, fg = c_best
                elif val >= 3.0:
                    bg, fg = c_good
                elif val >= 2.0:
                    bg, fg = c_mid
                elif val >= 1.0:
                    bg, fg = c_low
                else:
                    bg, fg = c_bad
            else:
                if val >= 2.8:
                    bg, fg = c_best
                elif val >= 2.1:
                    bg, fg = c_good
                elif val >= 1.4:
                    bg, fg = c_mid
                elif val >= 0.7:
                    bg, fg = c_low
                else:
                    bg, fg = c_bad

            return f"background-color: {bg}; color: {fg}; border-radius: 4px; font-weight: bold; font-size: 10px;"

        except (ValueError, TypeError, IndexError):
            # Fallback for legacy text data
            d = str(data).lower()
            if "very high" in d:
                return "background-color: #145A32; color: white; border-radius: 4px; font-weight: bold; font-size: 10px;"
            if "high" in d:
                return "background-color: #2ECC71; color: black; border-radius: 4px; font-weight: bold; font-size: 10px;"
            elif "moderate" in d:
                return "background-color: #F1C40F; color: black; border-radius: 4px; font-weight: bold; font-size: 10px;"
            else:
                return "background-color: #E74C3C; color: white; border-radius: 4px; font-weight: bold; font-size: 10px;"

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
        self.target_width = 400
        self.target_height = 500
        self.resize(self.target_width, self.target_height)

        container = GlassFrame(self)
        layout_wrap = QVBoxLayout(self)
        layout_wrap.setContentsMargins(0, 0, 0, 0)
        layout_wrap.addWidget(container)

        container.setStyleSheet(
            ".GlassFrame { background-color: rgba(20, 30, 40, 220); border: 1px solid rgba(255,255,255,50); border-radius: 20px; }")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)

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

        name = QLabel(plant.name)
        name.setStyleSheet("font-size: 28px; font-weight: bold; color: white; margin-bottom: 5px;")

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

        layout.addLayout(header)
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
        while self.flow_layout.count():
            item = self.flow_layout.takeAt(0)
            if item is None: break
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

        for p in plants:
            card = PlantCard(p)
            card.clicked.connect(self.open_detail)
            self.flow_layout.addWidget(card)

        self.content_widget.updateGeometry()

    def open_detail(self, plant, card_widget):
        main_window = self.window()
        pos = card_widget.mapTo(main_window, QPoint(0, 0))
        start_geo = QRect(pos, card_widget.size())

        dialog = DetailModal(plant, main_window, start_geometry=start_geo)
        dialog.exec_()


class HomeTab(BaseTab):
    def __init__(self, data_manager):
        super().__init__(data_manager)
        self.search_bar.setPlaceholderText("Search top recommendations...")
        QTimer.singleShot(100, self.perform_search)

    def perform_search(self):
        text = self.search_bar.text()
        if not text:
            results = self.dm.get_top_10()
            self.status_label.setText("Top 10 Recommendations")
        else:
            results = self.dm.search(text)
            self.status_label.setText(f"Found {len(results)} matches.")
        self.populate_grid(results)


class ListTab(BaseTab):
    def __init__(self, data_manager):
        super().__init__(data_manager)
        self.search_bar.setPlaceholderText("Search library...")
        QTimer.singleShot(100, self.perform_search)

    def perform_search(self):
        text = self.search_bar.text()
        results = self.dm.search_all(text)

        # Safety limit for rendering
        MAX_ITEMS = len(results)

        if len(results) == 0: MAX_ITEMS = 0

        if len(results) > MAX_ITEMS:
            display_results = results[:MAX_ITEMS]
            self.status_label.setText(f"Displaying top {MAX_ITEMS} of {len(results)} plants. Please refine search.")
            self.populate_grid(display_results)
        else:
            self.status_label.setText(f"Found {len(results)} plants.")
            self.populate_grid(results)