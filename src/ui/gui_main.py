from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
                                     QPushButton, QTabWidget, QComboBox, QFormLayout, QGroupBox, QFileDialog,
                                     QTextEdit, QHBoxLayout, QListWidget)
import sys
import json
import os
import serial
import serial.tools.list_ports
from PyQt5.QtCore import QTimer

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

        # 創建載入按鈕
        btn_layout = QHBoxLayout()
        self.load_all_button = QPushButton("載入所有設定")
        self.load_all_button.clicked.connect(self.load_all_configs)
        btn_layout.addWidget(self.load_all_button)

        self.load_rp2040_button = QPushButton("載入 RP2040 設定")
        self.load_rp2040_button.clicked.connect(lambda: self.load_single_config('rp2040'))
        btn_layout.addWidget(self.load_rp2040_button)

        self.load_pmu_button = QPushButton("載入 PMU 設定")
        self.load_pmu_button.clicked.connect(lambda: self.load_single_config('pmu'))
        btn_layout.addWidget(self.load_pmu_button)

        self.load_dio_button = QPushButton("載入 DIO 設定")
        self.load_dio_button.clicked.connect(lambda: self.load_single_config('dio'))
        btn_layout.addWidget(self.load_dio_button)

        self.load_relay_button = QPushButton("載入 Relay 設定")
        self.load_relay_button.clicked.connect(lambda: self.load_single_config('relay'))
        btn_layout.addWidget(self.load_relay_button)

        self.layout.addLayout(btn_layout)

        # 創建分頁視窗
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # 創建各硬體設定頁面
        self.rp2040_panel = RP2040SetupPanel()
        self.pmu_panel = PMUSetupPanel()
        self.dio_panel = DIOSetupPanel()
        self.relay_panel = RelaySetupPanel()

        # 添加各頁面到分頁視窗
        self.tabs.addTab(self.rp2040_panel, "RP2040")
        self.tabs.addTab(self.pmu_panel, "PMU")
        self.tabs.addTab(self.dio_panel, "數位 I/O")
        self.tabs.addTab(self.relay_panel, "Relay")

        # 創建儲存按鈕
        save_btn_layout = QHBoxLayout()
        self.save_all_button = QPushButton("儲存所有設定")
        self.save_all_button.clicked.connect(self.save_all_configs)
        save_btn_layout.addWidget(self.save_all_button)

        self.save_rp2040_button = QPushButton("儲存 RP2040 設定")
        self.save_rp2040_button.clicked.connect(lambda: self.save_single_config('rp2040'))
        save_btn_layout.addWidget(self.save_rp2040_button)

        self.save_pmu_button = QPushButton("儲存 PMU 設定")
        self.save_pmu_button.clicked.connect(lambda: self.save_single_config('pmu'))
        save_btn_layout.addWidget(self.save_pmu_button)

        self.save_dio_button = QPushButton("儲存 DIO 設定")
        self.save_dio_button.clicked.connect(lambda: self.save_single_config('dio'))
        save_btn_layout.addWidget(self.save_dio_button)

        self.save_relay_button = QPushButton("儲存 Relay 設定")
        self.save_relay_button.clicked.connect(lambda: self.save_single_config('relay'))
        save_btn_layout.addWidget(self.save_relay_button)

        self.layout.addLayout(save_btn_layout)

    def load_all_configs(self):
        dir_path = QFileDialog.getExistingDirectory(self, "選擇硬體設定資料夾", os.getcwd())
        if not dir_path:
            return

        # 載入所有設定檔
        for filename in os.listdir(dir_path):
            if filename.endswith('.json'):
                self.load_config_file(os.path.join(dir_path, filename))

    def load_single_config(self, hw_type):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            f"選擇 {hw_type.upper()} 設定檔",
            os.getcwd(),
            f"JSON Files (*.json)"
        )
        if file_path:
            self.load_config_file(file_path)

    def load_config_file(self, file_path):
        try:
            with open(file_path, 'r') as f:
                config = json.load(f)
            
            # 根據檔案名稱決定要更新哪個面板
            filename = os.path.basename(file_path).lower()
            if 'rp2040' in filename:
                self.rp2040_panel.update_config(config)
            elif 'pmu' in filename:
                self.pmu_panel.update_config(config)
            elif 'dio' in filename:
                self.dio_panel.update_config(config)
            elif 'relay' in filename:
                self.relay_panel.update_config(config)
        except Exception as e:
            print(f"Error loading config file {file_path}: {str(e)}")

    def save_all_configs(self):
        dir_path = QFileDialog.getExistingDirectory(self, "選擇儲存資料夾", os.getcwd())
        if not dir_path:
            return

        # 儲存所有設定
        configs = {
            'rp2040': self.rp2040_panel.get_config(),
            'pmu': self.pmu_panel.get_config(),
            'dio': self.dio_panel.get_config(),
            'relay': self.relay_panel.get_config()
        }

        for hw_type, config in configs.items():
            file_path = os.path.join(dir_path, f"{hw_type}_config.json")
            with open(file_path, 'w') as f:
                json.dump(config, f, indent=2)

    def save_single_config(self, hw_type):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"儲存 {hw_type.upper()} 設定",
            f"{hw_type}_config.json",
            "JSON Files (*.json)"
        )
        if file_path:
            config = getattr(self, f"{hw_type}_panel").get_config()
            with open(file_path, 'w') as f:
                json.dump(config, f, indent=2)

class RP2040SetupPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QFormLayout()
        self.setLayout(self.layout)
        self.alias_inputs = {}

    def update_config(self, config):
        # 清除現有設定
        while self.layout.rowCount():
            self.layout.removeRow(0)
        self.alias_inputs.clear()

        # 設定 I2C
        if 'i2c_host' in config:
            for i, i2c in enumerate(config['i2c_host']):
                key = f"I2C{i}"
                cb = QComboBox()
                cb.addItems([f"Pin {pin}" for pin in i2c['pins']])
                self.layout.addRow(f"別名 {key}", cb)
                self.alias_inputs[key] = cb

        # 設定 PWM
        if 'pwm' in config:
            for i, pwm_pin in enumerate(config['pwm']):
                key = f"PWM{i}"
                cb = QComboBox()
                cb.addItem(f"Pin {pwm_pin}")
                self.layout.addRow(f"別名 {key}", cb)
                self.alias_inputs[key] = cb

    def get_config(self):
        config = {'i2c_host': [], 'pwm': []}
        for key, cb in self.alias_inputs.items():
            if key.startswith('I2C'):
                idx = int(key[3:])
                while len(config['i2c_host']) <= idx:
                    config['i2c_host'].append({'pins': []})
                pin = int(cb.currentText().replace("Pin ", ""))
                config['i2c_host'][idx]['pins'].append(pin)
            elif key.startswith('PWM'):
                pin = int(cb.currentText().replace("Pin ", ""))
                config['pwm'].append(pin)
        return config

class PMUSetupPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QFormLayout()
        self.setLayout(self.layout)
        self.config_inputs = {}

    def update_config(self, config):
        # 清除現有設定
        while self.layout.rowCount():
            self.layout.removeRow(0)
        self.config_inputs.clear()

        # 添加 PMU 設定項目
        for key, value in config.items():
            input_field = QComboBox()
            input_field.addItems([str(v) for v in value])
            self.layout.addRow(key, input_field)
            self.config_inputs[key] = input_field

    def get_config(self):
        return {key: [int(input_field.currentText())] for key, input_field in self.config_inputs.items()}

class DIOSetupPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QFormLayout()
        self.setLayout(self.layout)
        self.config_inputs = {}

    def update_config(self, config):
        # 清除現有設定
        while self.layout.rowCount():
            self.layout.removeRow(0)
        self.config_inputs.clear()

        # 添加 DIO 設定項目
        for key, value in config.items():
            input_field = QComboBox()
            input_field.addItems([str(v) for v in value])
            self.layout.addRow(key, input_field)
            self.config_inputs[key] = input_field

    def get_config(self):
        return {key: [int(input_field.currentText())] for key, input_field in self.config_inputs.items()}

class RelaySetupPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QFormLayout()
        self.setLayout(self.layout)
        self.config_inputs = {}

    def update_config(self, config):
        # 清除現有設定
        while self.layout.rowCount():
            self.layout.removeRow(0)
        self.config_inputs.clear()

        # 添加 Relay 設定項目
        for key, value in config.items():
            input_field = QComboBox()
            input_field.addItems([str(v) for v in value])
            self.layout.addRow(key, input_field)
            self.config_inputs[key] = input_field

    def get_config(self):
        return {key: [int(input_field.currentText())] for key, input_field in self.config_inputs.items()}

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

class SerialPortPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # 創建掃描按鈕
        self.scan_button = QPushButton("掃描 Serial Ports")
        self.scan_button.clicked.connect(self.scan_ports)
        self.layout.addWidget(self.scan_button)
        
        # 創建狀態標籤
        self.status_label = QLabel("狀態：等待掃描...")
        self.layout.addWidget(self.status_label)
        
        # 創建顯示列表
        self.port_list = QListWidget()
        self.layout.addWidget(QLabel("已連接的 RP2040 設備："))
        self.layout.addWidget(self.port_list)

    def scan_ports(self):
        self.port_list.clear()
        self.status_label.setText("狀態：掃描中...")
        QApplication.processEvents()
        
        ports = serial.tools.list_ports.comports()
        found_devices = False
        
        if not ports:
            self.status_label.setText("狀態：無串口設備連接")
            self.port_list.addItem("無設備連接")
            return
            
        for port in ports:
            try:
                ser = serial.Serial(port.device, 115200, timeout=1)
                ser.write(b'ID?\n')
                response = ser.readline().decode().strip()
                if response.startswith('RP2040_'):
                    self.port_list.addItem(f"{port.device} - {response}")
                    found_devices = True
                ser.close()
            except:
                continue
                
        if not found_devices:
            self.status_label.setText("狀態：未找到 RP2040 設備")
            self.port_list.addItem("無 RP2040 設備連接")
        else:
            self.status_label.setText("狀態：掃描完成")

class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ATE 系統 UI 原型")
        self.setGeometry(200, 200, 800, 500)

        tabs = QTabWidget()
        tabs.addTab(SerialPortPanel(), "Serial Ports")
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
