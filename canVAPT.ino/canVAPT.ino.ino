#include <SPI.h>
#include <mcp2515.h>

struct can_frame canMsg;
MCP2515 mcp2515(10); // CS pin

unsigned long lastMessageTime = 0;
bool fuzzingMode = false;
bool replayMode = false;
uint32_t replayId = 0;
uint8_t replayData[8];
uint8_t replayLen = 0;

void setup() {
  Serial.begin(115200);
  
  mcp2515.reset();
  mcp2515.setBitrate(CAN_500KBPS); // Set CAN bitrate
  mcp2515.setNormalMode();

  Serial.println("CAN Bus Initialized");
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }

  if (fuzzingMode) {
    fuzzCANBus();
    delay(100); // Delay between fuzzing messages
  }

  if (replayMode) {
    replayMessage();
    delay(100); // Delay between replay messages
  }

  if (mcp2515.readMessage(&canMsg) == MCP2515::ERROR_OK) {
    analyzeMessageTiming();
    sendMessageToSerial();
  }
}

void processCommand(String command) {
  if (command.startsWith("INJECT:")) {
    // Format: INJECT:ID,DATA
    String params = command.substring(7);
    int commaIndex = params.indexOf(',');
    if (commaIndex != -1) {
      uint32_t id = strtoul(params.substring(0, commaIndex).c_str(), NULL, 16);
      String dataStr = params.substring(commaIndex + 1);
      uint8_t data[8];
      uint8_t len = 0;
      for (int i = 0; i < dataStr.length(); i += 2) {
        if (len >= 8) break;
        data[len++] = strtoul(dataStr.substring(i, i+2).c_str(), NULL, 16);
      }
      injectMessage(id, data, len);
    }
  } else if (command == "FUZZ:ON") {
    fuzzingMode = true;
  } else if (command == "FUZZ:OFF") {
    fuzzingMode = false;
  } else if (command.startsWith("REPLAY:")) {
    // Format: REPLAY:ID,DATA
    String params = command.substring(7);
    int commaIndex = params.indexOf(',');
    if (commaIndex != -1) {
      replayId = strtoul(params.substring(0, commaIndex).c_str(), NULL, 16);
      String dataStr = params.substring(commaIndex + 1);
      replayLen = 0;
      for (int i = 0; i < dataStr.length(); i += 2) {
        if (replayLen >= 8) break;
        replayData[replayLen++] = strtoul(dataStr.substring(i, i+2).c_str(), NULL, 16);
      }
      replayMode = true;
    }
  } else if (command == "REPLAY:OFF") {
    replayMode = false;
  }
}

void injectMessage(uint32_t id, uint8_t* data, uint8_t len) {
  struct can_frame frame;
  frame.can_id = id;
  frame.can_dlc = len;
  memcpy(frame.data, data, len);
  mcp2515.sendMessage(&frame);
  Serial.println("Message injected");
}

void fuzzCANBus() {
  struct can_frame frame;
  frame.can_id = random(0x000, 0x7FF); // Random ID
  frame.can_dlc = random(0, 9); // Random length
  for(int i = 0; i < frame.can_dlc; i++) {
    frame.data[i] = random(0, 256); // Random data
  }
  mcp2515.sendMessage(&frame);
  Serial.println("Fuzzing message sent");
}

void replayMessage() {
  struct can_frame frame;
  frame.can_id = replayId;
  frame.can_dlc = replayLen;
  memcpy(frame.data, replayData, replayLen);
  mcp2515.sendMessage(&frame);
  Serial.println("Replay message sent");
}

void analyzeMessageTiming() {
  unsigned long currentTime = millis();
  unsigned long timeDiff = currentTime - lastMessageTime;
  Serial.print("Time since last message: ");
  Serial.println(timeDiff);
  lastMessageTime = currentTime;
}

void sendMessageToSerial() {
  Serial.print(canMsg.can_id, HEX);
  Serial.print(",");
  Serial.print(canMsg.can_dlc);
  for (int i = 0; i < canMsg.can_dlc; i++) {
    Serial.print(",");
    Serial.print(canMsg.data[i], HEX);
  }
  Serial.println();
}