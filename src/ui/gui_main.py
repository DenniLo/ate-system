from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
                                     QPushButton, QTabWidget, QComboBox, QFormLayout, QGroupBox, QFileDialog,
                                     QTextEdit, QHBoxLayout)
import sys
import json
import os

# 全域硬體設定資料
hardware_config = {}
pinmap = {}

# 讀取硬體設定檔
def load_hardware_config(file_path):
    global hardware_config
    with open(file_path, 'r') as f:
        hardware_config = json.load(f)

# 儲存 pinmap 對應
def save_pinmap(file_path):
    with open(file_path, 'w') as f:
        json.dump(pinmap, f, indent=2)

class HardwareSetupPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.form = QFormLayout()
        self.alias_inputs = {}

        self.load_button = QPushButton("載入硬體設定檔")
        self.load_button.clicked.connect(self.load_config)
        self.layout.addWidget(self.load_button)

        self.group = QGroupBox("Pin Alias 對應設定")
        self.group.setLayout(self.form)
        self.layout.addWidget(self.group)

        self.save_button = QPushButton("儲存對應檔 (pinmap.json)")
        self.save_button.clicked.connect(self.save_pinmap_file)
        self.layout.addWidget(self.save_button)

    def load_config(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "選擇 hardware_config.json", os.getcwd(), "JSON Files (*.json)")
        if not file_path:
            return

        load_hardware_config(file_path)
        self.form_widgets_clear()

        # 解析 RP2040 I2C HOST 與 PWM
        if 'rp2040' in hardware_config:
            if 'i2c_host' in hardware_config['rp2040']:
                for i, i2c in enumerate(hardware_config['rp2040']['i2c_host']):
                    key = f"I2C{i}"
                    cb = QComboBox()
                    cb.addItems([f"Pin {pin}" for pin in i2c['pins']])
                    self.form.addRow(f"別名 {key}", cb)
                    self.alias_inputs[key] = cb

            if 'pwm' in hardware_config['rp2040']:
                for i, pwm_pin in enumerate(hardware_config['rp2040']['pwm']):
                    key = f"PWM{i}"
                    cb = QComboBox()
                    cb.addItem(f"Pin {pwm_pin}")
                    self.form.addRow(f"別名 {key}", cb)
                    self.alias_inputs[key] = cb

    def form_widgets_clear(self):
        while self.form.rowCount():
            self.form.removeRow(0)
        self.alias_inputs.clear()

    def save_pinmap_file(self):
        for key, cb in self.alias_inputs.items():
            sel = cb.currentText().replace("Pin ", "")
            pinmap[key] = int(sel)
        save_pinmap("pinmap.json")

class PMUPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("PMU 控制面板"))
        layout.addWidget(QPushButton("啟動量測"))
        self.setLayout(layout)

class DigitalIOPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("數位 IO 控制面板"))
        layout.addWidget(QPushButton("執行 Pattern"))
        self.setLayout(layout)

class RelayPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Relay 控制面板"))
        layout.addWidget(QPushButton("切換繼電器"))
        self.setLayout(layout)

class ScriptEditorPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.editor = QTextEdit()
        self.editor.setPlaceholderText("輸入 ATE 測試腳本，例如:\nI2C_W(0x80, 0x2A)\nFV(VIN, 10V, 10mA)\nMV(COMP, AV12)")

        self.save_button = QPushButton("儲存腳本")
        self.save_button.clicked.connect(self.save_script)

        self.load_button = QPushButton("載入腳本")
        self.load_button.clicked.connect(self.load_script)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.load_button)
        btn_layout.addWidget(self.save_button)

        self.layout.addWidget(QLabel("ATE 測試腳本編輯器"))
        self.layout.addWidget(self.editor)
        self.layout.addLayout(btn_layout)

    def save_script(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "儲存腳本", "script.ate", "ATE Script (*.ate)")
        if file_path:
            with open(file_path, 'w') as f:
                f.write(self.editor.toPlainText())

    def load_script(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "載入腳本", os.getcwd(), "ATE Script (*.ate)")
        if file_path:
            with open(file_path, 'r') as f:
                self.editor.setPlainText(f.read())

class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ATE 系統 UI 原型")
        self.setGeometry(200, 200, 800, 500)

        tabs = QTabWidget()
        tabs.addTab(ScriptEditorPanel(), "測試腳本")
        tabs.addTab(PMUPanel(), "PMU")
        tabs.addTab(DigitalIOPanel(), "數位 I/O")
        tabs.addTab(RelayPanel(), "Relay")
        tabs.addTab(HardwareSetupPanel(), "硬體設定")

        self.setCentralWidget(tabs)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainUI()
    window.show()
    sys.exit(app.exec_())
