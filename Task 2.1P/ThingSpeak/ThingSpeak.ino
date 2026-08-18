#include <WiFiNINA.h>
#include <ThingSpeak.h>
#include <DHT.h>
#include <BH1750.h>
#include <Wire.h>

// ---------- Wi-Fi ----------
#define SECRET_SSID "._."
#define SECRET_PASS "siuuu7777"

// ---------- ThingSpeak ----------
#define SECRET_CH_ID 3459593
#define SECRET_WRITE_APIKEY "V17UJRKDOXFE7T97"

// ---------- DHT22 ----------
#define DHTPIN 12
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

// ---------- BH1750 ----------
BH1750 lightMeter;

// ---------- Wi-Fi ----------
WiFiClient client;

void setup()
{
  Serial.begin(9600);

  dht.begin();

  Wire.begin();
  lightMeter.begin();

  Serial.println("Connecting to Wi-Fi...");

  while (WiFi.begin(SECRET_SSID, SECRET_PASS) != WL_CONNECTED)
  {
    delay(5000);
    Serial.println("Trying again...");
  }

  Serial.println("Wi-Fi connected.");

  ThingSpeak.begin(client);
}

void loop()
{
  // Read DHT22
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  // Read BH1750
  float light = lightMeter.readLightLevel();

  // Display readings
  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" °C");

  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.println(" %");

  Serial.print("Light: ");
  Serial.print(light);
  Serial.println(" lux");

  // Send data to ThingSpeak
  ThingSpeak.setField(1, temperature);
  ThingSpeak.setField(2, humidity);
  ThingSpeak.setField(3, light);

  int response = ThingSpeak.writeFields(SECRET_CH_ID, SECRET_WRITE_APIKEY);

  if (response == 200)
  {
    Serial.println("Data sent to ThingSpeak successfully.");
  }
  else
  {
    Serial.print("ThingSpeak error: ");
    Serial.println(response);
  }

  Serial.println("-------------------------");

  // Wait 30 seconds
  delay(30000);
}