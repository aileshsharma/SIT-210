
#include <Wire.h>
#include <BH1750.h>
#include <DHT.h>

#define DHTPIN 12
#define DHTTYPE DHT22

#define LIGHT_LED 11
#define ALERT_LED 10

DHT dht(DHTPIN, DHTTYPE);
BH1750 lightMeter;

// Default thresholds
float minLux = 100;
float minTemp = 18;
float maxTemp = 32;
float minHumidity = 30;
float maxHumidity = 80;
float drasticLuxChange = 300;

float previousLux = -1;

bool lightAvailable = false;

unsigned long lastRead = 0;
unsigned long lastRetry = 0;

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(100);

  Wire.begin();
  dht.begin();

  pinMode(LIGHT_LED, OUTPUT);
  pinMode(ALERT_LED, OUTPUT);

  digitalWrite(LIGHT_LED, LOW);
  digitalWrite(ALERT_LED, LOW);

  // Start light sensor
  lightAvailable = lightMeter.begin();

  Serial.println("{\"system\":\"ready\"}");
}

void loop() {

  // Receive new threshold values from Raspberry Pi
  if (Serial.available()) {

    String command = Serial.readStringUntil('\n');

    if (command.startsWith("LIMITS,")) {

      command.remove(0, 7);

      float values[6];

      for (int i = 0; i < 6; i++) {

        int comma = command.indexOf(',');

        if (i < 5 && comma == -1) {
          break;
        }

        String value;

        if (i < 5) {
          value = command.substring(0, comma);
          command.remove(0, comma + 1);
        } else {
          value = command;
        }

        values[i] = value.toFloat();
      }

      if (values[1] < values[2] &&
          values[3] < values[4] &&
          values[4] <= 100 &&
          values[0] >= 0 &&
          values[5] > 0) {

        minLux = values[0];
        minTemp = values[1];
        maxTemp = values[2];
        minHumidity = values[3];
        maxHumidity = values[4];
        drasticLuxChange = values[5];

        Serial.println("ACK:LIMITS");
      } else {
        Serial.println("ERROR:INVALID_LIMITS");
      }
    }
  }

  // Read sensors every 2 seconds
  if (millis() - lastRead < 2000) {
    return;
  }

  lastRead = millis();

  // Read DHT22
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  bool dhtAvailable =
    !isnan(temperature) && !isnan(humidity);

  // Check light sensor again every 10 seconds if unavailable
  if (!lightAvailable && millis() - lastRetry >= 10000) {

    lastRetry = millis();

    lightAvailable = lightMeter.begin();
  }

  // Read BH1750 only when available
  float lux = -1;

  if (lightAvailable) {

    lux = lightMeter.readLightLevel();

    if (isnan(lux) || lux < 0) {
      lightAvailable = false;
      previousLux = -1;
    }
  }

  // Check light conditions
  bool lowLight = false;
  bool drasticChange = false;

  if (lightAvailable) {

    lowLight = lux < minLux;

    if (previousLux >= 0) {
      drasticChange =
        abs(lux - previousLux) > drasticLuxChange;
    }

    previousLux = lux;
  }

  // Check temperature and humidity
  bool climateAlert = false;

  if (dhtAvailable) {

    climateAlert =
      temperature < minTemp ||
      temperature > maxTemp ||
      humidity < minHumidity ||
      humidity > maxHumidity;
  }

  bool alert = climateAlert || drasticChange;

  // Control LEDs
  digitalWrite(
    LIGHT_LED,
    lightAvailable && lowLight ? HIGH : LOW
  );

  digitalWrite(
    ALERT_LED,
    alert ? HIGH : LOW
  );

  // Send readings to Raspberry Pi
  Serial.print("{");

  Serial.print("\"dhtAvailable\":");
  Serial.print(dhtAvailable ? "true" : "false");

  Serial.print(",\"lightAvailable\":");
  Serial.print(lightAvailable ? "true" : "false");

  Serial.print(",\"temperature\":");

  if (dhtAvailable) {
    Serial.print(temperature);
  } else {
    Serial.print("null");
  }

  Serial.print(",\"humidity\":");

  if (dhtAvailable) {
    Serial.print(humidity);
  } else {
    Serial.print("null");
  }

  Serial.print(",\"lux\":");

  if (lightAvailable) {
    Serial.print(lux);
  } else {
    Serial.print("null");
  }

  Serial.print(",\"lowLight\":");
  Serial.print(lowLight ? "true" : "false");

  Serial.print(",\"drasticChange\":");
  Serial.print(drasticChange ? "true" : "false");

  Serial.print(",\"alert\":");
  Serial.print(alert ? "true" : "false");

  Serial.println("}");
}
