#include <Servo.h>
#include <string.h>

const byte SERVO_COUNT = 6;
const byte servoPins[SERVO_COUNT] = {3, 5, 6, 9, 10, 11};

const int buttonPin = 2;
const int ledPin = 13;

Servo servos[SERVO_COUNT];

int currentAngles[SERVO_COUNT] = {90, 45, 90, 45, 90, 37};
int targetAngles[SERVO_COUNT]  = {90, 45, 90, 45, 90, 37};

const unsigned long MOVE_INTERVAL_MS = 15;
const int STEP_SIZE = 1;

char inputBuffer[64];
byte inputIndex = 0;

unsigned long lastMoveTime = 0;
int buttonState = HIGH;
int lastButtonReading = HIGH;
unsigned long lastDebounceTime = 0;
const unsigned long DEBOUNCE_MS = 50;

void setup() {
  Serial.begin(115200);

  pinMode(ledPin, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP);
  digitalWrite(ledPin, LOW);

  for (byte i = 0; i < SERVO_COUNT; i++) {
    servos[i].attach(servoPins[i]);
    servos[i].write(currentAngles[i]);
  }

  Serial.println("READY");
}

void loop() {
  readSerialLine();
  updateServosSmoothly();
  updateButtonEvent();
}

void readSerialLine() {
  while (Serial.available() > 0) {
    char c = Serial.read();

    if (c == '\n' || c == '\r') {
      if (inputIndex > 0) {
        inputBuffer[inputIndex] = '\0';
        handleCommand(inputBuffer);
        inputIndex = 0;
      }
    } else {
      if (inputIndex < sizeof(inputBuffer) - 1) {
        inputBuffer[inputIndex++] = c;
      }
    }
  }
}

void handleCommand(char* data) {
  if (strcmp(data, "LED_HUMAN") == 0) {
    digitalWrite(ledPin, LOW);
    Serial.println("LED_HUMAN_OK");
    return;
  }

  if (strcmp(data, "LED_ROBOT") == 0) {
    digitalWrite(ledPin, HIGH);
    Serial.println("LED_ROBOT_OK");
    return;
  }

  parseAndSetTargets(data);
}

void parseAndSetTargets(char* data) {
  int values[SERVO_COUNT];
  byte count = 0;

  char* token = strtok(data, ",");

  while (token != NULL && count < SERVO_COUNT) {
    values[count] = constrain(atoi(token), 0, 180);
    count++;
    token = strtok(NULL, ",");
  }

  if (count == SERVO_COUNT) {
    for (byte i = 0; i < SERVO_COUNT; i++) {
      targetAngles[i] = values[i];
    }
    Serial.println("TARGET_SET");
  } else {
    Serial.println("ERR");
  }
}

void updateServosSmoothly() {
  unsigned long now = millis();
  if (now - lastMoveTime < MOVE_INTERVAL_MS) return;

  lastMoveTime = now;

  for (byte i = 0; i < SERVO_COUNT; i++) {
    if (currentAngles[i] < targetAngles[i]) {
      currentAngles[i] = min(currentAngles[i] + STEP_SIZE, targetAngles[i]);
      servos[i].write(currentAngles[i]);
    }
    else if (currentAngles[i] > targetAngles[i]) {
      currentAngles[i] = max(currentAngles[i] - STEP_SIZE, targetAngles[i]);
      servos[i].write(currentAngles[i]);
    }
  }
}

void updateButtonEvent() {
  int reading = digitalRead(buttonPin);
  unsigned long now = millis();

  if (reading != lastButtonReading) {
    lastDebounceTime = now;
  }

  if ((now - lastDebounceTime) >= DEBOUNCE_MS) {
    if (reading != buttonState) {
      buttonState = reading;

      if (buttonState == LOW) {
        Serial.println("BUTTON_PRESSED");
      }
    }
  }

  lastButtonReading = reading;
}
