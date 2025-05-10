from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
                                     QPushButton, QTabWidget, QComboBox, QFormLayout, QGroupBox, QFileDialog,
                                     QTextEdit, QHBoxLayout, QListWidget, QFrame, QScrollArea, QDesktopWidget)
import sys
import json
import os
import serial
import serial.tools.list_ports
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QColor, QPalette

# VS Code 深色主題顏色
VSCODE_COLORS = {
    'background': '#1e1e1e',  # 主背景色
    'foreground': '#d4d4d4',  # 主要文字顏色
    'widget_background': '#252526',  # 控件背景色
    'button_background': '#0e639c',  # 按鈕背景色
    'button_hover': '#1177bb',  # 按鈕懸停色
    'button_pressed': '#0d5a8e',  # 按鈕按下色
    'border': '#3c3c3c',  # 邊框顏色
    'selection': '#264f78',  # 選中項顏色
    'group_background': '#2d2d2d',  # 分組背景色
    'status_background': '#007acc',  # 狀態欄背景色
    'error': '#f48771',  # 錯誤文字顏色
    'success': '#6a9955',  # 成功文字顏色
}

def apply_vscode_style(app):
    """應用 VS Code 深色主題到整個應用程序"""
    # 設置全局調色板
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(VSCODE_COLORS['background']))
    palette.setColor(QPalette.WindowText, QColor(VSCODE_COLORS['foreground']))
    palette.setColor(QPalette.Base, QColor(VSCODE_COLORS['widget_background']))
    palette.setColor(QPalette.AlternateBase, QColor(VSCODE_COLORS['widget_background']))
    palette.setColor(QPalette.ToolTipBase, QColor(VSCODE_COLORS['widget_background']))
    palette.setColor(QPalette.ToolTipText, QColor(VSCODE_COLORS['foreground']))
    palette.setColor(QPalette.Text, QColor(VSCODE_COLORS['foreground']))
    palette.setColor(QPalette.Button, QColor(VSCODE_COLORS['button_background']))
    palette.setColor(QPalette.ButtonText, QColor(VSCODE_COLORS['foreground']))
    palette.setColor(QPalette.BrightText, QColor(VSCODE_COLORS['error']))
    palette.setColor(QPalette.Link, QColor(VSCODE_COLORS['button_background']))
    palette.setColor(QPalette.Highlight, QColor(VSCODE_COLORS['selection']))
    palette.setColor(QPalette.HighlightedText, QColor(VSCODE_COLORS['foreground']))
    
    app.setPalette(palette)
    
    # 設置全局樣式表
    app.setStyleSheet(f"""
        QWidget {{
            background-color: {VSCODE_COLORS['background']};
            color: {VSCODE_COLORS['foreground']};
        }}
        
        QTabWidget::pane {{
            border: 1px solid {VSCODE_COLORS['border']};
            background-color: {VSCODE_COLORS['background']};
        }}
        
        QTabBar::tab {{
            background-color: {VSCODE_COLORS['widget_background']};
            color: {VSCODE_COLORS['foreground']};
            border: 1px solid {VSCODE_COLORS['border']};
            padding: 8px 12px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {VSCODE_COLORS['background']};
            border-bottom: 2px solid {VSCODE_COLORS['button_background']};
        }}
        
        QTabBar::tab:hover {{
            background-color: {VSCODE_COLORS['selection']};
        }}
        
        QPushButton {{
            background-color: {VSCODE_COLORS['button_background']};
            color: {VSCODE_COLORS['foreground']};
            border: none;
            padding: 5px 15px;
            border-radius: 3px;
        }}
        
        QPushButton:hover {{
            background-color: {VSCODE_COLORS['button_hover']};
        }}
        
        QPushButton:pressed {{
            background-color: {VSCODE_COLORS['button_pressed']};
        }}
        
        QPushButton:disabled {{
            background-color: {VSCODE_COLORS['border']};
            color: #666666;
        }}
        
        QGroupBox {{
            background-color: {VSCODE_COLORS['group_background']};
            border: 1px solid {VSCODE_COLORS['border']};
            border-radius: 3px;
            margin-top: 1em;
            padding-top: 10px;
        }}
        
        QGroupBox::title {{
            color: {VSCODE_COLORS['foreground']};
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px;
        }}
        
        QLabel {{
            color: {VSCODE_COLORS['foreground']};
        }}
        
        QTextEdit {{
            background-color: {VSCODE_COLORS['widget_background']};
            color: {VSCODE_COLORS['foreground']};
            border: 1px solid {VSCODE_COLORS['border']};
            border-radius: 3px;
            padding: 5px;
        }}
        
        QScrollArea {{
            border: 1px solid {VSCODE_COLORS['border']};
            background-color: {VSCODE_COLORS['background']};
        }}
        
        QScrollBar:vertical {{
            background-color: {VSCODE_COLORS['background']};
            width: 12px;
            margin: 0;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {VSCODE_COLORS['border']};
            min-height: 20px;
            border-radius: 6px;
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}
    """)

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

class DeviceGroup(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # 標題
        title_layout = QHBoxLayout()
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {VSCODE_COLORS['foreground']};
                font-weight: bold;
                font-size: 14px;
            }}
        """)
        title_layout.addWidget(self.title_label)
        self.layout.addLayout(title_layout)
        
        # 設備列表容器
        self.devices_container = QWidget()
        self.devices_layout = QVBoxLayout()
        self.devices_container.setLayout(self.devices_layout)
        
        # 創建滾動區域
        scroll = QScrollArea()
        scroll.setWidget(self.devices_container)
        scroll.setWidgetResizable(True)
        self.layout.addWidget(scroll)
        
        # 創建預設的設備槽位
        self.device_slots = []
        self.create_default_slots()
        
    def create_default_slots(self):
        """創建預設的設備槽位"""
        for i in range(10):
            slot = self.create_device_slot(f"Slot {i+1}")
            self.device_slots.append(slot)
            self.devices_layout.addWidget(slot)
            
    def create_device_slot(self, slot_name):
        """創建一個設備槽位"""
        device_widget = QFrame()
        device_widget.setStyleSheet(f"""
            QFrame {{
                background-color: {VSCODE_COLORS['widget_background']};
                border: 1px solid {VSCODE_COLORS['border']};
                border-radius: 3px;
                margin: 2px;
                padding: 5px;
            }}
        """)
        device_layout = QHBoxLayout()
        device_layout.setSpacing(10)
        device_widget.setLayout(device_layout)
        
        # 狀態指示燈（預設紅色）
        status_light = QLabel()
        status_light.setObjectName("status_light")  # 設置對象名稱
        status_light.setFixedSize(12, 12)
        status_light.setStyleSheet("""
            QLabel {
                background-color: #e74c3c;
                border-radius: 6px;
                border: 1px solid #c0392b;
            }
        """)
        device_layout.addWidget(status_light)
        
        # 槽位名稱
        slot_label = QLabel(slot_name)
        slot_label.setObjectName("slot_label")  # 設置對象名稱
        slot_label.setStyleSheet(f"""
            QLabel {{
                color: {VSCODE_COLORS['foreground']};
                min-width: 150px;
            }}
        """)
        device_layout.addWidget(slot_label)
        
        # 分隔線
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet(f"background-color: {VSCODE_COLORS['border']};")
        device_layout.addWidget(separator)
        
        # 設備信息（預設為空）
        device_info = QLabel("Waiting for device...")
        device_info.setObjectName("device_info")  # 設置對象名稱
        device_info.setStyleSheet(f"""
            QLabel {{
                color: {VSCODE_COLORS['foreground']};
                min-width: 200px;
            }}
        """)
        device_layout.addWidget(device_info)
        
        # 添加彈性空間
        device_layout.addStretch()
        
        return device_widget
        
    def add_device(self, port, response, baud_rate):
        """添加設備到第一個可用的槽位"""
        # 解析設備 ID
        device_id = response.replace('PICO:', '')
        device_parts = device_id.split('_')
        device_name = device_parts[0]  # 功能名稱
        device_number = device_parts[1] if len(device_parts) > 1 else "1"  # 設備編號
        
        # 找到第一個可用的槽位
        for slot in self.device_slots:
            # 使用對象名稱查找設備信息標籤
            device_info = slot.findChild(QLabel, "device_info")
            if device_info and device_info.text() == "Waiting for device...":
                # 更新狀態指示燈為綠色
                status_light = slot.findChild(QLabel, "status_light")
                if status_light:
                    status_light.setStyleSheet("""
                        QLabel {
                            background-color: #2ecc71;
                            border-radius: 6px;
                            border: 1px solid #27ae60;
                        }
                    """)
                
                # 更新設備信息
                device_info.setText(f"PORT: {port} ({baud_rate} baud) | Device: {device_name} | Number: {device_number}")
                break
                
    def clear_devices(self):
        """重置所有設備槽位"""
        for slot in self.device_slots:
            # 重置狀態指示燈為紅色
            status_light = slot.findChild(QLabel, "status_light")
            if status_light:
                status_light.setStyleSheet("""
                    QLabel {
                        background-color: #e74c3c;
                        border-radius: 6px;
                        border: 1px solid #c0392b;
                    }
                """)
            
            # 重置設備信息
            device_info = slot.findChild(QLabel, "device_info")
            if device_info:
                device_info.setText("Waiting for device...")

class SerialScanner(QThread):
    device_found = pyqtSignal(str, str, int)  # port, response, baud_rate
    scan_finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    debug_message = pyqtSignal(str)  # 新增 debug 訊息信號
    
    def __init__(self):
        super().__init__()
        self.is_running = True
        self.target_ports = []
        self.baud_rates = [9600, 19200, 38400, 57600, 115200]  # 常用波特率列表
        
    def set_ports_and_baud(self, ports, baud_rate):
        """設置要掃描的端口列表"""
        self.target_ports = ports
        
    def run(self):
        self.debug_message.emit("開始掃描串口...")
        
        if not self.target_ports:
            self.error_occurred.emit("未選擇端口")
            self.scan_finished.emit()
            return
            
        for port in self.target_ports:
            if not self.is_running:
                break
                
            self.debug_message.emit(f"正在掃描串口: {port}")
            
            # 對每個端口嘗試不同的波特率
            for baud_rate in self.baud_rates:
                if not self.is_running:
                    break
                    
                try:
                    self.debug_message.emit(f"嘗試波特率: {baud_rate}")
                    
                    # 設置串口參數
                    ser = serial.Serial(
                        port=port,
                        baudrate=baud_rate,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        timeout=0.5,  # 縮短超時時間以加快掃描速度
                        write_timeout=0.5
                    )
                    
                    # 清空緩衝區
                    ser.reset_input_buffer()
                    ser.reset_output_buffer()
                    
                    self.debug_message.emit(f"發送 ID? 命令到 {port}")
                    ser.write(b'ID?\n')
                    ser.flush()
                    
                    self.debug_message.emit("等待回應...")
                    response = ser.readline().decode().strip()
                    self.debug_message.emit(f"收到回應: {response}")
                    
                    # 檢查是否為 PICO 設備
                    if response.startswith('PICO:'):
                        self.debug_message.emit(f"找到設備: {port} - {response} (波特率: {baud_rate})")
                        self.device_found.emit(port, response, baud_rate)
                        break  # 找到設備後跳出波特率循環
                        
                except serial.SerialTimeoutException:
                    self.debug_message.emit(f"串口 {port} 在波特率 {baud_rate} 下超時")
                except serial.SerialException as e:
                    self.debug_message.emit(f"串口錯誤: {str(e)}")
                except Exception as e:
                    self.debug_message.emit(f"其他錯誤: {str(e)}")
                finally:
                    try:
                        if 'ser' in locals() and ser.is_open:
                            ser.close()
                    except:
                        pass
                    
        self.debug_message.emit("掃描完成")
        self.scan_finished.emit()
        
    def stop(self):
        self.is_running = False

class SerialPortPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # 創建頂部控制區域
        top_layout = QHBoxLayout()
        
        # 掃描按鈕
        self.scan_button = QPushButton("掃描")
        self.scan_button.setFixedWidth(80)
        self.scan_button.clicked.connect(self.scan_all_ports)
        top_layout.addWidget(self.scan_button)
        
        # 狀態顯示區域
        self.status_label = QLabel("狀態：等待掃描...")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                padding: 5px;
                background-color: {VSCODE_COLORS['status_background']};
                color: white;
                border-radius: 3px;
                border: 1px solid {VSCODE_COLORS['border']};
            }}
        """)
        top_layout.addWidget(self.status_label)
        top_layout.addStretch()
        
        self.layout.addLayout(top_layout)
        
        # 創建設備分組
        devices_layout = QHBoxLayout()
        
        # I2C 設備組
        self.i2c_group = DeviceGroup("I2C 設備")
        devices_layout.addWidget(self.i2c_group)
        
        # PWM 設備組
        self.pwm_group = DeviceGroup("PWM 設備")
        devices_layout.addWidget(self.pwm_group)
        
        # ADC 設備組
        self.adc_group = DeviceGroup("ADC 設備")
        devices_layout.addWidget(self.adc_group)
        
        self.layout.addLayout(devices_layout)
        
        # 創建終端機訊息區域
        terminal_group = QGroupBox("終端機訊息")
        terminal_layout = QVBoxLayout()
        
        # 終端機訊息顯示區域
        self.terminal_text = QTextEdit()
        self.terminal_text.setReadOnly(True)
        self.terminal_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {VSCODE_COLORS['widget_background']};
                color: {VSCODE_COLORS['foreground']};
                font-family: Consolas, Monaco, monospace;
                font-size: 12px;
                padding: 5px;
                border: 1px solid {VSCODE_COLORS['border']};
                border-radius: 3px;
            }}
        """)
        terminal_layout.addWidget(self.terminal_text)
        
        # 清除按鈕
        clear_button = QPushButton("清除訊息")
        clear_button.clicked.connect(self.clear_terminal)
        terminal_layout.addWidget(clear_button)
        
        terminal_group.setLayout(terminal_layout)
        self.layout.addWidget(terminal_group)
        
        # 創建掃描器
        self.scanner = None

    def clear_terminal(self):
        """清除終端機訊息"""
        self.terminal_text.clear()

    def scan_all_ports(self):
        """掃描所有可用端口"""
        # 清空所有設備組
        self.i2c_group.clear_devices()
        self.pwm_group.clear_devices()
        self.adc_group.clear_devices()
        
        self.status_label.setText("狀態：正在掃描串口...")
        self.scan_button.setEnabled(False)
        
        # 如果已經有掃描器在運行，先停止它
        if self.scanner and self.scanner.isRunning():
            self.scanner.stop()
            self.scanner.wait()
            
        # 創建新的掃描器
        self.scanner = SerialScanner()
        self.scanner.device_found.connect(self.on_device_found)
        self.scanner.scan_finished.connect(self.on_scan_finished)
        self.scanner.error_occurred.connect(self.on_error)
        self.scanner.debug_message.connect(self.on_debug_message)
        
        # 獲取所有可用端口（除了 COM4）
        ports = [port.device for port in serial.tools.list_ports.comports() if port.device != "COM4"]
        
        # 設置要掃描的端口
        self.scanner.set_ports_and_baud(ports, None)  # 不再需要傳入波特率
        self.scanner.start()
        
    def on_debug_message(self, message):
        """處理 debug 訊息"""
        self.terminal_text.append(message)
        # 自動滾動到底部
        self.terminal_text.verticalScrollBar().setValue(
            self.terminal_text.verticalScrollBar().maximum()
        )
        
    def on_device_found(self, port, response, baud_rate):
        # 更新狀態顯示
        self.status_label.setText(f"狀態：在 {port} 發現設備 {response}")
        
        # 根據設備類型添加到相應的組
        if "I2C" in response:
            self.i2c_group.add_device(port, response, baud_rate)
        elif "PWM" in response:
            self.pwm_group.add_device(port, response, baud_rate)
        elif "ADC" in response:
            self.adc_group.add_device(port, response, baud_rate)
        
    def on_scan_finished(self):
        self.status_label.setText("狀態：掃描完成")
        self.scan_button.setEnabled(True)
        
    def on_error(self, error_msg):
        self.status_label.setText(f"狀態：{error_msg}")
        self.scan_button.setEnabled(True)

class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ATE 系統 UI 原型")
        
        # 獲取螢幕尺寸
        screen = QDesktopWidget().screenGeometry()
        # 設置視窗大小為螢幕的 90%
        window_width = int(screen.width() * 0.9)
        window_height = int(screen.height() * 0.9)
        # 計算視窗位置使其居中
        x = (screen.width() - window_width) // 2
        y = (screen.height() - window_height) // 2
        # 設置視窗大小和位置
        self.setGeometry(x, y, window_width, window_height)
        
        # 設置視窗標誌
        self.setWindowFlags(Qt.Window)
        
        # 創建分頁視窗
        self.tabs = QTabWidget()
        self.tabs.addTab(SerialPortPanel(), "Serial Ports")
        self.tabs.addTab(ScriptEditorPanel(), "測試腳本")
        self.tabs.addTab(PMUPanel(), "PMU")
        self.tabs.addTab(DigitalIOPanel(), "數位 I/O")
        self.tabs.addTab(RelayPanel(), "Relay")
        self.tabs.addTab(HardwareSetupPanel(), "硬體設定")
        
        # 設置分頁視窗的樣式
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {VSCODE_COLORS['border']};
                background-color: {VSCODE_COLORS['background']};
            }}
            
            QTabBar::tab {{
                background-color: {VSCODE_COLORS['widget_background']};
                color: {VSCODE_COLORS['foreground']};
                border: 1px solid {VSCODE_COLORS['border']};
                padding: 8px 12px;
                margin-right: 2px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {VSCODE_COLORS['background']};
                border-bottom: 2px solid {VSCODE_COLORS['button_background']};
            }}
            
            QTabBar::tab:hover {{
                background-color: {VSCODE_COLORS['selection']};
            }}
        """)
        
        self.setCentralWidget(self.tabs)
        
        # 顯示視窗
        self.show()
        
        # 延遲一下再最大化視窗，這樣可以確保所有控件都已經正確加載
        QTimer.singleShot(100, self.showMaximized)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_vscode_style(app)  # 應用 VS Code 深色主題
    window = MainUI()
    sys.exit(app.exec_())
