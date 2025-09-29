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
from PySide6.QtCore import Qt, Signal, QTimer

from typing import Optional

# Attempt to import the NT client. If not available at import time, we allow
# passing an already-constructed client into the widget.
try:
    from test import MotorNTClient  # adjust module name if needed
except Exception:  # pragma: no cover
    MotorNTClient = None  # type: ignore


class MotorDisplay(QWidget):
    close_requested = Signal(object)

    def __init__(
        self, MotorType, DeviceID, encoderAttached, nt_client: Optional[object] = None
    ):
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

        # ---------------- NT client + polling setup ----------------
        self._nt = nt_client
        # Create a default client connected to localhost if none was provided
        if self._nt is None and MotorNTClient is not None:
            self._nt = MotorNTClient()
        if getattr(self, "_nt", None) is not None:
            try:
                self._nt.start()
            except Exception:
                # If start fails, we still keep the UI functional without data
                pass

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

        # Wire UI actions
        self.desired_speed_send.clicked.connect(self._send_desired_speed)
        self.reset_position_send.clicked.connect(self._send_reset_position)
        self.stop_button.clicked.connect(self._on_stop_clicked)
        self.reset_button.clicked.connect(self._on_reset_clicked)

        # Periodic polling of NetworkTables for live stats
        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(200)  # ms
        self._poll_timer.timeout.connect(self._update_from_nt)
        self._poll_timer.start()

        # Add the three layouts to the main layout
        layout.addLayout(header_layout)
        layout.addWidget(header_divider)
        layout.addLayout(middle_layout)
        layout.addWidget(middle_divider)
        layout.addLayout(footer_layout)

        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Track latched command booleans so we can clear them on the next command
        self._stop_latched = False
        self._reset_latched = False

    def _on_close_clicked(self):
        try:
            if hasattr(self, "_poll_timer"):
                self._poll_timer.stop()
        except Exception:
            pass
        self.close_requested.emit(self)

    def _update_from_nt(self):
        """Fetch latest motor stats from NT and update labels."""
        if not getattr(self, "_nt", None):
            return
        try:
            data = self._nt.get_motor_data(int(self.device_id))
        except Exception:
            print("hello")
            return

        # Format and update UI labels
        try:
            self.voltage_value.setText(f"{data.busVoltage:.1f} V")
            self.current_value.setText(f"{data.outputCurrent:.1f} A")
            self.temp_value.setText(f"{data.temperature:.1f} °C")
            self.velocity_value.setText(f"{data.velocity:.0f} rpm")
            # setSpeed expected in [-1, 1] from stats; show as percentage
            self.setspeed_value.setText(f"{data.setSpeed * 100:.0f} %")
            self.position_value.setText(f"{data.position:.2f} rotations")
        except Exception:
            print("oh no")
            pass

    def _set_cmd_bool(self, key: str, value: bool) -> bool:
        """Attempt to set a boolean command topic directly via the client's publishers.
        Returns True on success, False otherwise.
        """
        if not getattr(self, "_nt", None):
            return False
        try:
            pubs = self._nt._ensure_cmd_pubs(
                int(self.device_id)
            )  # uses client internals
            pubs[key].set(bool(value))
            return True
        except Exception:
            return False

    def _send_desired_speed(self):
        """Read percent from input ([-100, 100]) and command NT in [-1, 1].
        Also clears a previously latched 'stop' boolean as requested.
        """
        if not getattr(self, "_nt", None):
            return
        text = self.desired_speed_input.text().strip()
        if not text:
            return
        try:
            pct = float(text)
        except ValueError:
            return
        # Clamp to [-100, 100] then scale to [-1, 1]
        pct = max(-100.0, min(100.0, pct))

        # If stop was latched True, clear it now (set back to False)
        if self._stop_latched:
            if self._set_cmd_bool("stop", False):
                self._stop_latched = False

        try:
            self._nt.set_speed(int(self.device_id), pct / 100.0)
        except Exception:
            pass

    def _send_reset_position(self):
        """Read target position (rotations) and command NT absolute position.
        Also clears a previously latched 'reset' boolean as requested.
        """
        if not getattr(self, "_nt", None):
            return
        text = self.reset_position_input.text().strip()
        if not text:
            return
        try:
            rotations = float(text)
        except ValueError:
            return

        # If reset was latched True, clear it now (set back to False)
        if self._reset_latched:
            if self._set_cmd_bool("reset", False):
                self._reset_latched = False

        try:
            self._nt.set_position(int(self.device_id), rotations)
        except Exception:
            pass

    def _on_stop_clicked(self):
        # Latch stop to True; it will be cleared on next desired speed command
        if self._set_cmd_bool("stop", True):
            self._stop_latched = True

    def _on_reset_clicked(self):
        # Latch reset to True; it will be cleared on next position command
        if self._set_cmd_bool("reset", True):
            self._reset_latched = True

    def closeEvent(self, event):
        # Stop polling when the widget closes; do not stop the shared NT client
        try:
            if hasattr(self, "_poll_timer"):
                self._poll_timer.stop()
        except Exception:
            pass
        super().closeEvent(event)
