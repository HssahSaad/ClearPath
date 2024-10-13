// Define the L298n IO pins
#define ENB 5
#define IN1 7
#define IN2 8
#define IN3 9
#define IN4 11
#define ENA 6

void setup() {
  // Set the motor control pins as outputs
  pinMode(ENB, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENA, OUTPUT);
}

void loop() {
  // Adjust motor speeds to move straight
  analogWrite(ENA, 100);  // Speed of left motor
  analogWrite(ENB, 100);  // Speed of right motor

  // Move forward
  digitalWrite(IN1, HIGH);  // Left motor forward
  digitalWrite(IN2, LOW);   // Left motor direction
  digitalWrite(IN3, LOW);   // Right motor direction
  digitalWrite(IN4, HIGH);  // Right motor forward

  delay(2000);  // Move forward for 3 seconds

    // Stop the car
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);

  delay(30000);

  // Move forward again
  analogWrite(ENA, 100);  // Speed of left motor
  analogWrite(ENB, 100);  // Speed of right motor
  digitalWrite(IN1, HIGH);  // Left motor forward
  digitalWrite(IN2, LOW);   // Left motor direction
  digitalWrite(IN3, LOW);   // Right motor direction
  digitalWrite(IN4, HIGH);  // Right motor forward

  delay(2000);  // Move forward for another 3 seconds

  // Stop the car
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);

  // Prevent the loop from restarting (keep the car stopped)
  while (true);  // Infinite loop to keep the car stopped
}
