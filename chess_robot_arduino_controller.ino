#include <Servo.h>

// =============================================
// Chess Robot Arduino Controller
// متوافق مع ملف HTML: chess_robot_dashboard_multipage.html
// الأوامر المستلمة من الـ Web Serial:
// B90  -> Base
// S120 -> Shoulder
// E75  -> Elbow
// W90  -> Wrist Rotation
// P60  -> Wrist Pitch
// G40  -> Gripper
// كل أمر ينتهي بسطر جديد \n
// منافذ السيرفو (مطابقة للترتيب المتفق عليه)
// Base          -> D3
// Shoulder      -> D5
// Elbow         -> D6
// WristRotation -> D10
// WristPitch    -> D11
// Gripper       -> D9
// =============================================

Servo baseServo;
Servo shoulderServo;
Servo elbowServo;
Servo wristRotServo;
Servo wristPitchServo;
Servo gripperServo;

const byte PIN_BASE        = 3;
const byte PIN_SHOULDER    = 5;
const byte PIN_ELBOW       = 6;
const byte PIN_WRIST_ROT   = 10;
const byte PIN_WRIST_PITCH = 11;
const byte PIN_GRIPPER     = 9;

// زوايا البداية - خليتها مطابقة للواجهة تقريباً
int currentBase       = 90;
int currentShoulder   = 140;
int currentElbow      = 140;
int currentWristRot   = 90;
int currentWristPitch = 50;
int currentGripper    = 30;

// حدود الحماية - عدلها بعد التجربة حسب ذراعك الحقيقي
const int MIN_BASE        = 0;
const int MAX_BASE        = 180;
const int MIN_SHOULDER    = 0;
const int MAX_SHOULDER    = 180;
const int MIN_ELBOW       = 0;
const int MAX_ELBOW       = 180;
const int MIN_WRIST_ROT   = 0;
const int MAX_WRIST_ROT   = 180;
const int MIN_WRIST_PITCH = 0;
const int MAX_WRIST_PITCH = 180;
const int MIN_GRIPPER     = 10;   // مهم: مو 90 حتى ينغلق من الـ HTML
const int MAX_GRIPPER     = 80;

const int SERVO_STEP_DELAY = 8;  // سرعة الحركة الناعمة
String inputLine = "";

void moveServoSmooth(Servo &servo, int &currentAngle, int targetAngle) {
  targetAngle = constrain(targetAngle, 0, 180);

  if (targetAngle > currentAngle) {
    for (int pos = currentAngle; pos <= targetAngle; pos++) {
      servo.write(pos);
      delay(SERVO_STEP_DELAY);
    }
  } else if (targetAngle < currentAngle) {
    for (int pos = currentAngle; pos >= targetAngle; pos--) {
      servo.write(pos);
      delay(SERVO_STEP_DELAY);
    }
  } else {
    servo.write(targetAngle);
  }

  currentAngle = targetAngle;
}

bool parseCommand(const String &cmd, char &joint, int &angle) {
  if (cmd.length() < 2) return false;

  joint = toupper(cmd.charAt(0));
  String anglePart = cmd.substring(1);
  anglePart.trim();

  if (anglePart.length() == 0) return false;

  for (unsigned int i = 0; i < anglePart.length(); i++) {
    if (!isDigit(anglePart.charAt(i)) && !(i == 0 && anglePart.charAt(i) == '-')) {
      return false;
    }
  }

  angle = anglePart.toInt();
  return true;
}

void handleJointCommand(char joint, int angle) {
  switch (joint) {
    case 'B':
      angle = constrain(angle, MIN_BASE, MAX_BASE);
      moveServoSmooth(baseServo, currentBase, angle);
      Serial.print("OK B ");
      Serial.println(angle);
      break;

    case 'S':
      angle = constrain(angle, MIN_SHOULDER, MAX_SHOULDER);
      moveServoSmooth(shoulderServo, currentShoulder, angle);
      Serial.print("OK S ");
      Serial.println(angle);
      break;

    case 'E':
      angle = constrain(angle, MIN_ELBOW, MAX_ELBOW);
      moveServoSmooth(elbowServo, currentElbow, angle);
      Serial.print("OK E ");
      Serial.println(angle);
      break;

    case 'W':
      angle = constrain(angle, MIN_WRIST_ROT, MAX_WRIST_ROT);
      moveServoSmooth(wristRotServo, currentWristRot, angle);
      Serial.print("OK W ");
      Serial.println(angle);
      break;

    case 'P':
      angle = constrain(angle, MIN_WRIST_PITCH, MAX_WRIST_PITCH);
      moveServoSmooth(wristPitchServo, currentWristPitch, angle);
      Serial.print("OK P ");
      Serial.println(angle);
      break;

    case 'G':
      angle = constrain(angle, MIN_GRIPPER, MAX_GRIPPER);
      moveServoSmooth(gripperServo, currentGripper, angle);
      Serial.print("OK G ");
      Serial.println(angle);
      break;

    default:
      Serial.print("ERR Unknown joint: ");
      Serial.println(joint);
      break;
  }
}

void attachAllServos() {
  baseServo.attach(PIN_BASE);
  shoulderServo.attach(PIN_SHOULDER);
  elbowServo.attach(PIN_ELBOW);
  wristRotServo.attach(PIN_WRIST_ROT);
  wristPitchServo.attach(PIN_WRIST_PITCH);
  gripperServo.attach(PIN_GRIPPER);
}

void moveToStartupPose() {
  baseServo.write(currentBase);
  shoulderServo.write(currentShoulder);
  elbowServo.write(currentElbow);
  wristRotServo.write(currentWristRot);
  wristPitchServo.write(currentWristPitch);
  gripperServo.write(currentGripper);
}

void printHelp() {
  Serial.println("Chess Robot Ready");
  Serial.println("Commands:");
  Serial.println("B90   Base");
  Serial.println("S120  Shoulder");
  Serial.println("E75   Elbow");
  Serial.println("W90   Wrist Rotation");
  Serial.println("P60   Wrist Pitch");
  Serial.println("G40   Gripper");
}

void setup() {
  Serial.begin(9600);
  inputLine.reserve(24);

  attachAllServos();
  delay(400);
  moveToStartupPose();
  delay(800);

  printHelp();
}

void loop() {
  while (Serial.available() > 0) {
    char c = Serial.read();

    if (c == '\r') {
      continue;
    }

    if (c == '\n') {
      inputLine.trim();

      if (inputLine.length() > 0) {
        char joint;
        int angle;

        if (parseCommand(inputLine, joint, angle)) {
          handleJointCommand(joint, angle);
        } else {
          Serial.print("ERR Bad command: ");
          Serial.println(inputLine);
        }
      }

      inputLine = "";
    } else {
      inputLine += c;
      if (inputLine.length() > 20) {
        inputLine = "";
        Serial.println("ERR Command too long");
      }
    }
  }
}
