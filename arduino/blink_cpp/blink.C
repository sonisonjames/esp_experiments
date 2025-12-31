class MyLED {
  int pin;
public:
  MyLED(int p) : pin(p) { pinMode(pin, OUTPUT); }
  void blink() { digitalWrite(pin, HIGH); delay(200); digitalWrite(pin, LOW); }
};

MyLED led(2);  // Global instance

void setup() {  // REQUIRED
  // Initialization here if needed
}

void loop() {   // REQUIRED
  led.blink();
  delay(1000);
}
