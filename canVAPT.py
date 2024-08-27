import sys
import serial
import time
import serial.tools.list_ports
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
                               QTextEdit, QFileDialog, QComboBox, QHBoxLayout, QLabel,
                               QLineEdit, QGridLayout, QDialog, QTableWidget, QTableWidgetItem,
                               QHeaderView)
from PySide6.QtCore import QTimer, Qt, QEvent
from PySide6.QtGui import QColor, QTextCursor
import pyqtgraph as pg


class PacketDetailDialog(QDialog):
    def __init__(self, can_id, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Packet Detail - ID: {can_id}")
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()

        table = QTableWidget(7, 2)
        table.setHorizontalHeaderLabels(["Field", "Value"])
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        fields = [
            ("SOF", "1"),
            ("ID", can_id),
            ("Control", data[:1]),  # Assuming first byte is control
            ("Data", data[2:]),  # Assuming rest is data
            ("CRC", "Calculated CRC"),  # You'd need to implement CRC calculation
            ("ACK", "1"),  # Assuming ACK is always 1 in this context
            ("EOF", "1")
        ]

        for i, (field, value) in enumerate(fields):
            table.setItem(i, 0, QTableWidgetItem(field))
            table.setItem(i, 1, QTableWidgetItem(value))

        layout.addWidget(table)
        self.setLayout(layout)


class CANMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CANBJECTOR")
        self.setGeometry(100, 100, 1000, 800)

        main_layout = QVBoxLayout()

        # Settings bar
        settings_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        self.update_port_list()
        settings_layout.addWidget(QLabel("COM Port:"))
        settings_layout.addWidget(self.port_combo)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.toggle_connection)
        settings_layout.addWidget(self.connect_button)

        settings_layout.addStretch()
        main_layout.addLayout(settings_layout)

        # Control Panel
        control_layout = QGridLayout()
        self.inject_id = QLineEdit()
        self.inject_data = QLineEdit()
        inject_button = QPushButton("Inject Message")
        inject_button.clicked.connect(self.inject_message)
        control_layout.addWidget(QLabel("Inject ID (hex):"), 0, 0)
        control_layout.addWidget(self.inject_id, 0, 1)
        control_layout.addWidget(QLabel("Inject Data (hex):"), 0, 2)
        control_layout.addWidget(self.inject_data, 0, 3)
        control_layout.addWidget(inject_button, 0, 4)

        self.fuzz_button = QPushButton("Start Fuzzing")
        self.fuzz_button.clicked.connect(self.toggle_fuzzing)
        control_layout.addWidget(self.fuzz_button, 1, 0, 1, 2)

        self.replay_id = QLineEdit()
        self.replay_button = QPushButton("Start Replay")
        self.replay_button.clicked.connect(self.toggle_replay)
        control_layout.addWidget(QLabel("Replay ID (hex):"), 1, 2)
        control_layout.addWidget(self.replay_id, 1, 3)
        control_layout.addWidget(self.replay_button, 1, 4)

        main_layout.addLayout(control_layout)

        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by ID or data...")
        self.search_input.textChanged.connect(self.filter_packets)
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)

        # Message Display
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.installEventFilter(self)
        main_layout.addWidget(self.text_edit)

        # Graph
        self.graph = pg.PlotWidget()
        self.graph.setBackground('w')
        self.graph.setLabel('left', 'Message Count')
        self.graph.setLabel('bottom', 'CAN ID')
        main_layout.addWidget(self.graph)

        save_button = QPushButton("Save Packets")
        save_button.clicked.connect(self.save_packets)
        main_layout.addWidget(save_button)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.ser = None
        self.packets = {}
        self.last_update = {}
        self.message_counts = {}

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_packets)

        self.graph_timer = QTimer(self)
        self.graph_timer.timeout.connect(self.update_graph)
        self.graph_timer.start(1000)  # Update graph every second

    def eventFilter(self, obj, event):
        if obj == self.text_edit and event.type() == QEvent.MouseButtonDblClick:
            cursor = self.text_edit.textCursor()
            cursor.select(QTextCursor.LineUnderCursor)
            line = cursor.selectedText()
            parts = line.split(':')
            if len(parts) == 2:
                can_id = parts[0].strip()
                data = parts[1].strip()
                dialog = PacketDetailDialog(can_id, data, self)
                dialog.exec()
            return True
        return super().eventFilter(obj, event)

    def filter_packets(self):
        search_text = self.search_input.text().lower()
        self.text_edit.clear()
        for can_id, data in self.packets.items():
            if search_text in can_id.lower() or search_text in data.lower():
                self.text_edit.append(f'{can_id}: {data}')

    def update_port_list(self):
        self.port_combo.clear()
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo.addItems(ports)

    def toggle_connection(self):
        if self.ser:
            self.disconnect_serial()
        else:
            self.connect_serial()

    def connect_serial(self):
        port = self.port_combo.currentText()
        try:
            self.ser = serial.Serial(port, 115200)
            self.timer.start(10)  # Update every 10ms
            self.text_edit.append(f"Connected to {port}")
            self.connect_button.setText("Disconnect")
            self.port_combo.setEnabled(False)
        except serial.SerialException as e:
            self.text_edit.append(f"Error connecting to {port}: {str(e)}")

    def disconnect_serial(self):
        if self.ser:
            self.ser.close()
            self.ser = None
            self.timer.stop()
            self.text_edit.append("Disconnected from serial port.")
            self.connect_button.setText("Connect")
            self.port_combo.setEnabled(True)

    def update_packets(self):
        if self.ser and self.ser.in_waiting:
            line = self.ser.readline().decode().strip()
            parts = line.split(',')
            if len(parts) >= 2:
                can_id = parts[0]
                data = ','.join(parts[1:])
                current_time = time.time()

                if can_id in self.packets:
                    elapsed = current_time - self.last_update[can_id]
                    if elapsed > 60:
                        color = QColor(255, 0, 0)  # Red
                    elif elapsed > 10:
                        color = QColor(255, 255, 255)  # White
                    else:
                        color = QColor(0, 255, 0)  # Green
                else:
                    color = QColor(0, 255, 0)  # Green

                self.packets[can_id] = data
                self.last_update[can_id] = current_time
                self.message_counts[can_id] = self.message_counts.get(can_id, 0) + 1

                self.text_edit.setTextColor(color)
                self.text_edit.append(f'{can_id}: {data}')
                self.text_edit.setTextColor(QColor(0, 0, 0))  # Reset to black
                self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())

    def save_packets(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Packets", "", "Text Files (*.txt)")
        if file_name:
            with open(file_name, 'w') as f:
                for can_id, data in self.packets.items():
                    f.write(f"{can_id}: {data}\n")

    def inject_message(self):
        if not self.ser:
            self.text_edit.append("Not connected to serial port.")
            return
        can_id = self.inject_id.text()
        data = self.inject_data.text()
        command = f"INJECT:{can_id},{data}\n"
        self.ser.write(command.encode())
        self.text_edit.append(f"Injected message: {can_id}, {data}")

    def toggle_fuzzing(self):
        if not self.ser:
            self.text_edit.append("Not connected to serial port.")
            return
        if self.fuzz_button.text() == "Start Fuzzing":
            self.ser.write(b"FUZZ:ON\n")
            self.fuzz_button.setText("Stop Fuzzing")
            self.text_edit.append("Started fuzzing")
        else:
            self.ser.write(b"FUZZ:OFF\n")
            self.fuzz_button.setText("Start Fuzzing")
            self.text_edit.append("Stopped fuzzing")

    def toggle_replay(self):
        if not self.ser:
            self.text_edit.append("Not connected to serial port.")
            return
        if self.replay_button.text() == "Start Replay":
            replay_id = self.replay_id.text()
            if replay_id in self.packets:
                command = f"REPLAY:{replay_id},{self.packets[replay_id]}\n"
                self.ser.write(command.encode())
                self.replay_button.setText("Stop Replay")
                self.text_edit.append(f"Started replaying messages for ID: {replay_id}")
            else:
                self.text_edit.append(f"No messages captured for ID: {replay_id}")
        else:
            self.ser.write(b"REPLAY:OFF\n")
            self.replay_button.setText("Start Replay")
            self.text_edit.append("Stopped replaying messages")

    def update_graph(self):
        self.graph.clear()
        x = list(self.message_counts.keys())
        y = list(self.message_counts.values())
        self.graph.plot(x, y, pen=None, symbol='o')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CANMonitor()
    window.show()
    sys.exit(app.exec())