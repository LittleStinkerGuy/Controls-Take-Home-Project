from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QLabel,
    QLineEdit,
    QSpinBox,
    QPushButton,
    QFrame,
)
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt, Signal


class MotorDisplay(QWidget):
    close_requested = Signal(object)

    def __init__(self, MotorType, DeviceID, encoderAttached):
        super().__init__()

        layout = QVBoxLayout(self)
        self.device_id = DeviceID
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

        # Create header, middle, and footer layouts
        header_layout = QVBoxLayout()
        header_top_row = QHBoxLayout()
        header_top_row.addStretch()
        self.close_button = QPushButton("X")
        self.close_button.setFixedSize(20, 20)
        self.close_button.setStyleSheet("border-radius: 5px;")
        self.close_button.clicked.connect(self._on_close_clicked)
        header_top_row.addWidget(self.close_button)
        header_layout.addLayout(header_top_row)
        middle_layout = QVBoxLayout()
        footer_layout = QVBoxLayout()

        header_divider = QFrame()
        header_divider.setFrameShape(QFrame.HLine)
        header_divider.setFrameShadow(QFrame.Sunken)

        middle_divider = QFrame()
        middle_divider.setFrameShape(QFrame.HLine)
        middle_divider.setFrameShadow(QFrame.Sunken)

        # Header layout: add labels for initializer inputs
        self.motor_type_label = QLabel(f"Motor Type: {MotorType}")
        self.motor_type_label.setStyleSheet("font-weight: bold;")
        self.device_id_label = QLabel(f"Device ID: {DeviceID}")
        self.device_id_label.setStyleSheet("font-weight: bold;")
        self.encoder_attached_label = QLabel(f"Encoder Attached: {encoderAttached}")
        self.encoder_attached_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(self.motor_type_label)
        header_layout.addWidget(self.device_id_label)
        header_layout.addWidget(self.encoder_attached_label)

        # Middle layout: metric labels and value labels
        voltage_row = QHBoxLayout()
        voltage_label = QLabel("Voltage:")
        self.voltage_value = QLabel("0.0 V")
        voltage_row.addWidget(voltage_label)
        voltage_row.addWidget(self.voltage_value)
        middle_layout.addLayout(voltage_row)

        current_row = QHBoxLayout()
        current_label = QLabel("Current:")
        self.current_value = QLabel("0.0 A")
        current_row.addWidget(current_label)
        current_row.addWidget(self.current_value)
        middle_layout.addLayout(current_row)

        temp_row = QHBoxLayout()
        temp_label = QLabel("Temp:")
        self.temp_value = QLabel("0.0 °C")
        temp_row.addWidget(temp_label)
        temp_row.addWidget(self.temp_value)
        middle_layout.addLayout(temp_row)

        setspeed_row = QHBoxLayout()
        setspeed_label = QLabel("Set Speed (%):")
        self.setspeed_value = QLabel("0 %")
        setspeed_row.addWidget(setspeed_label)
        setspeed_row.addWidget(self.setspeed_value)
        middle_layout.addLayout(setspeed_row)

        velocity_row = QHBoxLayout()
        velocity_label = QLabel("Velocity (rpm):")
        self.velocity_value = QLabel("0 rpm")
        velocity_row.addWidget(velocity_label)
        velocity_row.addWidget(self.velocity_value)
        middle_layout.addLayout(velocity_row)

        position_row = QHBoxLayout()
        position_label = QLabel("Position (rotations):")
        self.position_value = QLabel("0.0 rotations")
        position_row.addWidget(position_label)
        position_row.addWidget(self.position_value)
        middle_layout.addLayout(position_row)

        # Footer layout: input fields with labels
        desired_speed_label = QLabel("Desired Speed (%):")
        self.desired_speed_input = QLineEdit()
        self.desired_speed_input.setPlaceholderText("0–100 %")
        footer_layout.addWidget(desired_speed_label)
        desired_speed_input_row = QHBoxLayout()
        self.desired_speed_input.setStyleSheet("padding: 5px;")
        desired_speed_input_row.addWidget(self.desired_speed_input)
        self.desired_speed_send = QPushButton("Send")
        desired_speed_input_row.addWidget(self.desired_speed_send)
        footer_layout.addLayout(desired_speed_input_row)

        reset_position_label = QLabel("Reset Position (rotations):")
        self.reset_position_input = QLineEdit()
        self.reset_position_input.setPlaceholderText("0.0 rotations")
        footer_layout.addWidget(reset_position_label)
        reset_position_input_row = QHBoxLayout()
        self.reset_position_input.setStyleSheet("padding: 5px;")
        reset_position_input_row.addWidget(self.reset_position_input)
        self.reset_position_send = QPushButton("Send")
        reset_position_input_row.addWidget(self.reset_position_send)
        footer_layout.addLayout(reset_position_input_row)

        control_buttons_row = QHBoxLayout()
        self.reset_button = QPushButton("Reset")
        self.stop_button = QPushButton("Stop")
        control_buttons_row.addWidget(self.reset_button)
        control_buttons_row.addWidget(self.stop_button)
        footer_layout.addLayout(control_buttons_row)

        # Add the three layouts to the main layout
        layout.addLayout(header_layout)
        layout.addWidget(header_divider)
        layout.addLayout(middle_layout)
        layout.addWidget(middle_divider)
        layout.addLayout(footer_layout)

        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    def _on_close_clicked(self):
        self.close_requested.emit(self)
