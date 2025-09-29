import sys


from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QFrame,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt
from widgets import create_motor_button
from widgets import motor_display


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Motor Test Bench")
        self.resize(1145, 720)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title_label = QLabel("Motor Test Bench")
        title_label.setStyleSheet("font-weight: bold; font-size: 32px;")
        title_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(title_label)
        horizontal_line = QFrame()
        horizontal_line.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(horizontal_line)

        self.master_motor_layout = QHBoxLayout()
        self.motor_layout = QHBoxLayout()
        self.master_motor_layout.addLayout(self.motor_layout)
        layout.addLayout(self.master_motor_layout, 1)

        self.create_control = create_motor_button.CreateMotorButton()
        self.master_motor_layout.addWidget(self.create_control, 1)
        self.displayCount = 0
        self.used_ids = set()
        self.stretchSize = 3
        self.create_control.create_motor.connect(self.add_motor_display)
        self._update_layout_state()

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def _remove_trailing_stretch(self):
        count = self.master_motor_layout.count()
        if count > 0:
            item = self.master_motor_layout.itemAt(count - 1)
            if item is not None and item.spacerItem() is not None:
                self.master_motor_layout.takeAt(count - 1)

    def _apply_stretch(self):
        self._remove_trailing_stretch()
        if getattr(self, "stretchSize", 0) > 0:
            self.master_motor_layout.addStretch(self.stretchSize)

    def _calculate_stretch_size(self):
        max_stretch_slots = 3
        occupied_slots = min(self.displayCount, max_stretch_slots)
        return max(0, max_stretch_slots - occupied_slots)

    def _update_layout_state(self):
        self.stretchSize = self._calculate_stretch_size()
        self._apply_stretch()
        next_id = self._next_available_device_id(
            self.create_control.can_id_spin.minimum()
        )
        has_capacity = self.displayCount < 4

        if has_capacity:
            self.create_control.show()
        else:
            self.create_control.hide()

        self.create_control.setEnabled(has_capacity and next_id is not None)
        if next_id is not None:
            self.create_control.set_device_id(next_id)

    def add_motor_display(self, motor_type, device_id, encoder_attached):
        unique_id = self._next_available_device_id(device_id)
        if unique_id is None:
            return

        self._remove_trailing_stretch()
        widget = motor_display.MotorDisplay(motor_type, unique_id, encoder_attached)
        widget.close_requested.connect(self.remove_motor_display)
        self.used_ids.add(unique_id)
        self.displayCount += 1
        self.motor_layout.addWidget(widget, 1)
        self._update_layout_state()

    def remove_motor_display(self, widget):
        index = self.motor_layout.indexOf(widget)
        if index != -1:
            item = self.motor_layout.takeAt(index)
            removed_widget = item.widget() if item is not None else None
            if removed_widget is not None:
                if hasattr(removed_widget, "device_id"):
                    self.used_ids.discard(removed_widget.device_id)
                removed_widget.deleteLater()
            self.displayCount = max(0, self.displayCount - 1)
            self._update_layout_state()

    def _next_available_device_id(self, start):
        minimum = self.create_control.can_id_spin.minimum()
        maximum = self.create_control.can_id_spin.maximum()
        candidate = max(start, minimum)
        while candidate <= maximum:
            if candidate not in self.used_ids:
                return candidate
            candidate += 1
        return None


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
