#include <Servo.h>

Servo servoB, servoS, servoE, servoWR, servoWP, servoG;

const int PIN_B  = 3;
const int PIN_S  = 5;
const int PIN_E  = 6;
const int PIN_WR = 9;
const int PIN_WP = 10;
const int PIN_G  = 11;

int curB = 90, curS = 90, curE = 90, curWR = 90, curWP = 90, curG = 120;
String line = "";

void attachAll() {
  if (!servoB.attached())  servoB.attach(PIN_B);
  if (!servoS.attached())  servoS.attach(PIN_S);
  if (!servoE.attached())  servoE.attach(PIN_E);
  if (!servoWR.attached()) servoWR.attach(PIN_WR);
  if (!servoWP.attached()) servoWP.attach(PIN_WP);
  if (!servoG.attached())  servoG.attach(PIN_G);
}

void detachAll() {
  servoB.detach();
  servoS.detach();
  servoE.detach();
  servoWR.detach();
  servoWP.detach();
  servoG.detach();
}

void writeAll() {
  servoB.write(curB);
  servoS.write(curS);
  servoE.write(curE);
  servoWR.write(curWR);
  servoWP.write(curWP);
  servoG.write(curG);
}

bool parseSixCSV(const String &s, int out[6]) {
  int last = 0;
  int idx = 0;
  for (int i = 0; i <= s.length(); i++) {
    if (i == s.length() || s[i] == ',') {
      if (idx >= 6) return false;
      String part = s.substring(last, i);
      part.trim();
      out[idx++] = constrain(part.toInt(), 0, 180);
      last = i + 1;
    }
  }
  return idx == 6;
}

void setup() {
  Serial.begin(115200);
  attachAll();
  writeAll();
  Serial.println("READY");
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      line.trim();
      if (line.length() > 0) {
        if (line == "STOP") {
          detachAll();
          Serial.println("DETACHED");
        } else {
          int vals[6];
          if (parseSixCSV(line, vals)) {
            attachAll();
            curB = vals[0];
            curS = vals[1];
            curE = vals[2];
            curWR = vals[3];
            curWP = vals[4];
            curG = vals[5];
            writeAll();
            Serial.print("OK ");
            Serial.println(line);
          } else {
            Serial.print("ERR ");
            Serial.println(line);
          }
        }
      }
      line = "";
    } else {
      line += c;
    }
  }
}
