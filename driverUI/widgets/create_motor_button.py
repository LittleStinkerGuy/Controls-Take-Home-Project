from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QComboBox,
    QLabel,
    QLineEdit,
    QSpinBox,
    QPushButton,
    QCheckBox,
    QHBoxLayout,
)
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt, Signal


class CreateMotorButton(QWidget):
    create_motor = Signal(str, int, bool)
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        self.setAutoFillBackground(True)
        self.setObjectName("createMotorButton")
        self.setStyleSheet(
            """
            #createMotorButton {
                border-radius: 7%;
                border: .5px solid #4B4B4B;
                padding: 10px;
                
            }
            #createMotorButton > * {
                font-size: 16px;
            }
            """
        )
        self.setAttribute(Qt.WA_StyledBackground, True)

        motor_type_label = QLabel("Motor Type:")
        self.motor_type_edit = QComboBox()
        self.motor_type_edit.addItems(["Kraken", "Falcon", "SparkMax"])
        self.motor_type_edit.currentTextChanged.connect(self.on_motor_type_changed)
        can_id_label = QLabel("CAN Device ID")
        self.can_id_spin = QSpinBox()
        self.can_id_spin.setRange(1, 64)
        le = self.can_id_spin.findChild(QLineEdit)
        if le is not None:
            le.setTextMargins(5, 5, 5, 5)

        self.create_button = QPushButton("Create Motor")
        self.create_button.setStyleSheet(
            "border-radius: 7%; border: .5px solid #4B4B4B; padding: 5px;"
        )
        self.create_button.clicked.connect(self.on_create_clicked)

        abs_layout = QHBoxLayout()
        self.abs_encoder_label = QLabel("Absolute Encoder Attached")
        self.abs_encoder_checkbox = QCheckBox()
        self.abs_encoder_label.setVisible(False)
        self.abs_encoder_checkbox.setVisible(False)
        abs_layout.addWidget(self.abs_encoder_label)
        abs_layout.addWidget(self.abs_encoder_checkbox)

        layout.addWidget(motor_type_label)
        layout.addWidget(self.motor_type_edit)
        layout.addLayout(abs_layout)
        layout.addSpacing(10)
        layout.addWidget(can_id_label)
        layout.addWidget(self.can_id_spin)
        layout.addSpacing(25)
        layout.addWidget(self.create_button)

        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

    def on_motor_type_changed(self, text):
        self.abs_encoder_label.setVisible(text == "SparkMax")
        self.abs_encoder_checkbox.setVisible(text == "SparkMax")

    def on_create_clicked(self):
        motor_type = self.motor_type_edit.currentText()
        device_id = int(self.can_id_spin.value())
        encoder_attached = bool(self.abs_encoder_checkbox.isChecked())
        self.create_motor.emit(motor_type, device_id, encoder_attached)

    def set_device_id(self, device_id):
        minimum = self.can_id_spin.minimum()
        maximum = self.can_id_spin.maximum()
        clamped_value = max(minimum, min(device_id, maximum))
        was_blocked = self.can_id_spin.blockSignals(True)
        self.can_id_spin.setValue(clamped_value)
        self.can_id_spin.blockSignals(was_blocked)
