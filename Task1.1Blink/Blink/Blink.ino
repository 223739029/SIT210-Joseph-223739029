// Define LED pin for Nano 33 IoT
const int ledPin = LED_BUILTIN;

// Function to blink dot (1 Unit of time)
void dot() {
  digitalWrite(ledPin, HIGH);
  delay(250);
  digitalWrite(ledPin, LOW);
  delay(250);
}

// Function to blink dash (3 units of time)
void dash() {
  digitalWrite(ledPin, HIGH);
  delay(750);
  digitalWrite(ledPin, LOW);
  delay(250);
}

void setup() {
  pinMode(ledPin, OUTPUT);
}

void loop() {
  //J
  dot();
  dash();
  dash();
  dash();
  //O
  dash();
  dash();
  dash();
  //S
  dot();
  dot();
  dot();
  //E
  dot();
  //P
  dot();
  dash();
  dash();
  dot();
  //H
  dot();
  dot();
  dot();
  dot();
}

