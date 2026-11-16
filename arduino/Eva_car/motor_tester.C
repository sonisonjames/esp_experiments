
// ESP32 + L9110S 4-channel motor driver
// Sequentially test all four TT motors

struct Motor {
  const char* name;
  int pinA;
  int pinB;
};

Motor motors[] = {
  {"Motor 1", 25, 26},
  {"Motor 2", 27, 14},
  {"Motor 3", 16, 17},
  {"Motor 4", 18, 19}
};

const int MOTOR_COUNT = 4;

const int RUN_TIME = 2000;  // 2 seconds
const int PAUSE_TIME = 1000; // 1 second

void stopMotor(Motor m) {
  digitalWrite(m.pinA, LOW);
  digitalWrite(m.pinB, LOW);
}

void forward(Motor m) {
  digitalWrite(m.pinA, HIGH);
  digitalWrite(m.pinB, LOW);
}

void reverse(Motor m) {
  digitalWrite(m.pinA, LOW);
  digitalWrite(m.pinB, HIGH);
}

void setup() {
  Serial.begin(115200);

  // Configure all motor control pins
  for (int i = 0; i < MOTOR_COUNT; i++) {
    pinMode(motors[i].pinA, OUTPUT);
    pinMode(motors[i].pinB, OUTPUT);
    stopMotor(motors[i]);
  }

  Serial.println("ESP32 4-Motor Test Started");
  delay(2000);
}

void loop() {

  for (int i = 0; i < MOTOR_COUNT; i++) {

    Motor m = motors[i];

    Serial.println("----------------------");
    Serial.print("Testing ");
    Serial.println(m.name);

    // Forward
    Serial.println("Forward...");
    forward(m);
    delay(RUN_TIME);

    stopMotor(m);
    delay(500);

    // Reverse
    Serial.println("Reverse...");
    reverse(m);
    delay(RUN_TIME);

    // Stop
    stopMotor(m);

    Serial.println("Test completed.");
    delay(PAUSE_TIME);
  }

  Serial.println("All motors tested. Restarting sequence...");
  delay(2000);
}
