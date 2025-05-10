from machine import UART
import time

# 初始化 UART
# 使用 UART0，TX=GP0, RX=GP1
uart = UART(0, baudrate=38400, tx=0, rx=1)

# 設備識別碼
DEVICE_ID = "PICO:38400"

def main():
    print("PICO Serial ID Server Started")
    print(f"Device ID: {DEVICE_ID}")
    
    while True:
        if uart.any():  # 檢查是否有數據可讀
            try:
                # 讀取命令
                command = uart.readline().decode().strip()
                print(f"Received command: {command}")
                
                # 處理 ID? 命令
                if command == "ID?":
                    print(f"Sending response: {DEVICE_ID}")
                    uart.write(f"{DEVICE_ID}\n".encode())
                    uart.flush()
                    
            except Exception as e:
                print(f"Error: {str(e)}")
                
        time.sleep(0.1)  # 短暫延遲，避免 CPU 使用率過高

if __name__ == "__main__":
    main() 