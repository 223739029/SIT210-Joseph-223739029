#include "arduino_secrets.h"

#include <WiFiNINA.h>
#include <Wire.h>
#include <BH1750FVI.h>

// Creates the LightSensor instance
BH1750FVI LightSensor(BH1750FVI::k_DevModeContLowRes);

bool sunlightDetected = false;

char ssid[] = SECRET_SSID;
char pass[] = SECRET_PASS;

WiFiClient client;
char HOST_NAME[] = "maker.ifttt.com";
String eventStart = "/trigger/sunlight_start/with/key/dtPpX3MO_ZNxYWdr7FhDV";
String eventStop = "/trigger/sunlight_stop/with/key/dtPpX3MO_ZNxYWdr7FhDV";

// Function to send IFTTT notification
void sendIFTTTNotification(String path) {
  if (client.connect(HOST_NAME, 80)) {
    Serial.println("Connected to server");
    client.println("GET " + path + " HTTP/1.1");
    client.println("Host: " + String(HOST_NAME));
    client.println("Connection: close");
    client.println();
  } else {
    Serial.println("Connection failed");
  }

  while (client.connected()) {
    if (client.available()) {
      char c = client.read();
      Serial.print(c);
    }
  }

  client.stop();
  Serial.println("Disconnected");
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, pass);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("Connected to WiFi");

  LightSensor.begin();
}

void loop() {
  uint16_t lux = LightSensor.GetLightIntensity();
  Serial.print("Light: ");
  Serial.println(lux);

  if (lux > 50 && !sunlightDetected) { 
    sunlightDetected = true;
    sendIFTTTNotification(eventStart);
    Serial.println("Sunlight started");
  } else if (lux <= 50 && sunlightDetected) {
    sunlightDetected = false;
    sendIFTTTNotification(eventStop);
    Serial.println("Sunlight stopped");
  }

  delay(6000); 
}