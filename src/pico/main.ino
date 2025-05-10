#include <Arduino.h>

// 設備識別碼
const char* DEVICE_ID = "PICO:38400";

void setup() {
  // 初始化串口通訊
  Serial.begin(38400);
  while (!Serial) {
    ; // 等待串口連接
  }
  
  Serial.println("RP2040 Serial ID Server Started");
  Serial.print("Device ID: ");
  Serial.println(DEVICE_ID);
}

void loop() {
  if (Serial.available()) {
    // 讀取命令
    String command = Serial.readStringUntil('\n');
    command.trim();  // 移除空白字符
    
    // 處理 ID? 命令
    if (command == "ID?") {
      Serial.println(DEVICE_ID);
    }
  }
  
  // 短暫延遲，避免 CPU 使用率過高
  delay(10);
} 