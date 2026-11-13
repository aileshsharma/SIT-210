#include <Wire.h>
#include <BH1750.h>
#include <DHT.h>

#define DHTPIN 2
#define DHTTYPE DHT22

#define LIGHT_LED 3
#define RED_LED 4

#define DHT_INTERVAL 2000

DHT dht(DHTPIN, DHTTYPE);
BH1750 lightMeter;

// Default thresholds
float minLux = 100.0;
float minTemp = 18.0;
float maxTemp = 32.0;
float minHumidity = 30.0;
float maxHumidity = 80.0;
float drasticLuxChange = 300.0;

float previousLux = -1;

unsigned long lastRead = 0;

// Receive threshold updates from Raspberry Pi

void readCommands() {

  if (!Serial.available()) {
    return;
  }

  String command = Serial.readStringUntil('\n');
  command.trim();

  // Check command prefix
  if (!command.startsWith("LIMITS,")) {
    Serial.println("ERROR:INVALID_COMMAND");
    return;
  }

  // Remove LIMITS,
  command.remove(0, 7);

  float values[6];

  // Extract six comma-separated values
  for (int i = 0; i < 6; i++) {

    int comma = command.indexOf(',');

    String token;

    if (i < 5) {

      if (comma == -1) {
        Serial.println("ERROR:MISSING_VALUE");
        return;
      }

      token = command.substring(0, comma);
      command.remove(0, comma + 1);

    } else {

      if (comma != -1) {
        Serial.println("ERROR:EXTRA_VALUE");
        return;
      }

      token = command;
    }

    token.trim();

    if (token.length() == 0) {
      Serial.println("ERROR:EMPTY_VALUE");
      return;
    }

    char* endPointer;
    double parsed = strtod(token.c_str(), &endPointer);

    if (endPointer == token.c_str() || *endPointer != '\0') {
      Serial.println("ERROR:INVALID_VALUE");
      return;
    }

    values[i] = parsed;
  }

  // Validate thresholds
  float l = values[0];
  float tl = values[1];
  float th = values[2];
  float hl = values[3];
  float hh = values[4];
  float delta = values[5];

  if (l < 0 ||
      tl >= th ||
      hl >= hh ||
      hl < 0 ||
      hh > 100 ||
      delta <= 0) {

    Serial.println("ERROR:INVALID_LIMITS");
    return;
  }

  // Apply new thresholds
  minLux = l;
  minTemp = tl;
  maxTemp = th;
  minHumidity = hl;
  maxHumidity = hh;
  drasticLuxChange = delta;

  Serial.println("ACK:LIMITS");
}


void setup() {

  Serial.begin(9600);
  Serial.setTimeout(100);

  Wire.begin();
  dht.begin();

  pinMode(LIGHT_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);

  digitalWrite(LIGHT_LED, LOW);
  digitalWrite(RED_LED, LOW);

  if (!lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) {
    Serial.println("{\"error\":\"BH1750 sensor not detected\"}");
  }
}

void loop() {

  readCommands();

  if (millis() - lastRead >= DHT_INTERVAL) {

    lastRead = millis();

    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    float lux = lightMeter.readLightLevel();

    if (isnan(temperature) ||
        isnan(humidity) ||
        isnan(lux) ||
        lux < 0) {

      digitalWrite(RED_LED, HIGH);

      Serial.println(
        "{\"error\":\"Sensor reading failed\"}"
      );

      return;
    }

    bool lowLight = lux < minLux;

    bool drasticChange = false;

    if (previousLux >= 0) {

      drasticChange =
        abs(lux - previousLux) > drasticLuxChange;
    }

    previousLux = lux;

    bool climateAlert =
      temperature < minTemp ||
      temperature > maxTemp ||
      humidity < minHumidity ||
      humidity > maxHumidity;

    bool alert = climateAlert || drasticChange;

    // Control LEDs
    digitalWrite(LIGHT_LED, lowLight ? HIGH : LOW);
    digitalWrite(RED_LED, alert ? HIGH : LOW);

    // Send sensor readings to Raspberry Pi
    Serial.print("{\"temperature\":");
    Serial.print(temperature, 1);

    Serial.print(",\"humidity\":");
    Serial.print(humidity, 1);

    Serial.print(",\"lux\":");
    Serial.print(lux, 1);

    Serial.print(",\"lowLight\":");
    Serial.print(lowLight ? "true" : "false");

    Serial.print(",\"drasticChange\":");
    Serial.print(drasticChange ? "true" : "false");

    Serial.print(",\"alert\":");
    Serial.print(alert ? "true" : "false");

    Serial.println("}");
  }
}