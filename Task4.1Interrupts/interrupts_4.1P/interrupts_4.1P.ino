#include <Wire.h>
#include <BH1750.h>

const int PIR_PIN = 9;
const int BUTTON_PIN = 10;

const int LED1_PIN = 12;
const int LED2_PIN = 11;

const float DARK_THRESHOLD = 50.0;

const unsigned long LED1_TIME = 30000;
const unsigned long LED2_TIME = 60000;

const unsigned long PIR_COOLDOWN = 2000;
const unsigned long BUTTON_COOLDOWN = 500;

BH1750 lightMeter;

volatile bool motionEvent = false;
volatile bool buttonEvent = false;

volatile unsigned long pirTime = 0;
volatile unsigned long buttonTime = 0;

bool lightOneRunning = false;
bool lightTwoRunning = false;

unsigned long lightOneStarted = 0;
unsigned long lightTwoStarted = 0;


// PIR interrupt
void detectMotion() {

  unsigned long timeNow = millis();

  if (timeNow - pirTime >= PIR_COOLDOWN) {
    motionEvent = true;
    pirTime = timeNow;
  }
}


// Button interrupt
void buttonPressed() {

  unsigned long timeNow = millis();

  if (timeNow - buttonTime >= BUTTON_COOLDOWN) {
    buttonEvent = true;
    buttonTime = timeNow;
  }
}


// Switch both lights ON
void switchLightsOn() {

  digitalWrite(LED1_PIN, HIGH);
  digitalWrite(LED2_PIN, HIGH);

  lightOneRunning = true;
  lightTwoRunning = true;

  lightOneStarted = millis();
  lightTwoStarted = millis();
}


void setup() {

  Serial.begin(9600);

  pinMode(PIR_PIN, INPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  pinMode(LED1_PIN, OUTPUT);
  pinMode(LED2_PIN, OUTPUT);

  digitalWrite(LED1_PIN, LOW);
  digitalWrite(LED2_PIN, LOW);

  Wire.begin();

  if (lightMeter.begin()) {
    Serial.println("BH1750 started.");
  } else {
    Serial.println("BH1750 not detected.");
  }


  // PIR interrupt
  attachInterrupt(
    digitalPinToInterrupt(PIR_PIN),
    detectMotion,
    RISING
  );


  // Button interrupt
  attachInterrupt(
    digitalPinToInterrupt(BUTTON_PIN),
    buttonPressed,
    FALLING
  );


  Serial.println("System ready.");
}


void loop() {

  // PIR event
  if (motionEvent) {

    motionEvent = false;

    float lightValue = lightMeter.readLightLevel();

    Serial.println("Motion detected.");

    Serial.print("Current light: ");
    Serial.print(lightValue);
    Serial.println(" lux");


    if (lightValue < DARK_THRESHOLD) {

      Serial.println("Darkness detected.");

      switchLightsOn();

      Serial.println("Lights switched ON by motion.");

    } else {

      Serial.println("Enough light is available.");
      Serial.println("Lights remain OFF.");
    }
  }


  // Button event
  if (buttonEvent) {

    buttonEvent = false;

    Serial.println("Button pressed.");

    switchLightsOn();

    Serial.println("Lights switched ON by button.");
  }


  // LED1 timer
  if (lightOneRunning &&
      millis() - lightOneStarted >= LED1_TIME) {

    digitalWrite(LED1_PIN, LOW);
    lightOneRunning = false;

    Serial.println("First LED switched OFF after 30 seconds.");
  }


  // LED2 timer
  if (lightTwoRunning &&
      millis() - lightTwoStarted >= LED2_TIME) {

    digitalWrite(LED2_PIN, LOW);
    lightTwoRunning = false;

    Serial.println("Second LED switched OFF after 60 seconds.");
  }

  delay(50);
}
