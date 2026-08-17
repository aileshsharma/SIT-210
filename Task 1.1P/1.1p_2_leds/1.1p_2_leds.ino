const int PORCH_LED = 11;
const int HALLWAY_LED = 10;
const int BUTTON = 9;

void setup()
{
  pinMode(PORCH_LED, OUTPUT);
  pinMode(HALLWAY_LED, OUTPUT);
  pinMode(BUTTON, INPUT_PULLUP);

  digitalWrite(PORCH_LED, LOW);
  digitalWrite(HALLWAY_LED, LOW);
}

void loop()
{
  if (digitalRead(BUTTON) == LOW)
  {
    // Turn both lights ON
    digitalWrite(PORCH_LED, HIGH);
    digitalWrite(HALLWAY_LED, HIGH);

    // Porch stays ON for 30 seconds
    delay(30000);
    digitalWrite(PORCH_LED, LOW);

    // Hallway stays ON for another 30 seconds
    delay(30000);
    digitalWrite(HALLWAY_LED, LOW);

    // Wait for button to be released
    while (digitalRead(BUTTON) == LOW)
    {
      delay(10);
    }
  }
}