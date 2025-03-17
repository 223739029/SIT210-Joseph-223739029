#include "arduino_secrets.h"
//Add Libraries
#include "DHT.h"
#include <ThingSpeak.h>
#include <WiFiNINA.h>
#include "thingProperties.h"

#define DHTPIN 2 
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

// Used WiFi credentials from Sketch Secrets file
const char* ssid = SECRET_SSID;
const char* password = SECRET_OPTIONAL_PASS;

// ThingSpeak credentials from account on website
unsigned long myChannelNumber = 2880560;
const char* myWriteAPIKey = "FLZKOB4X6SIE9V15";

WiFiClient client;

void setup() {
  Serial.begin(9600);
  delay(1500); 

  // Initializes DHT11 sensor
  dht.begin();
  
  Serial.println(F("Initializing WiFi...")); //Confirms through serial monitor
  
  // Connects to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  
  Serial.println("\nConnected to WiFi"); //Confirms through serial monitor

  // Initializes connection to ThingSpeak
  ThingSpeak.begin(client);
  
  // Initializes IoT Cloud properties
  initProperties();
  ArduinoCloud.begin(ArduinoIoTPreferredConnection);
  
  setDebugMessageLevel(2);
  ArduinoCloud.printDebugInfo();
}

void loop() {
  ArduinoCloud.update(); // Updates IoT Cloud connection

  // Reads DHT11 sensor data
  float humidity = dht.readHumidity();
  float tempC = dht.readTemperature();
  float tempF = dht.readTemperature(true);

  // Check if any reads failed and display fail messageS
  if (isnan(humidity) || isnan(tempC)) {
    Serial.println(F("Failed to read from DHT sensor!")); //Confirms through serial monitor
    return;
  }


  // Print readings
  Serial.print(F("Humidity: ")); Serial.print(humidity); Serial.print(F("%  ")); //Confirms through serial monitor
  Serial.print(F("Temperature: ")); Serial.print(tempC); Serial.print(F("°C ")); //Confirms through serial monitor


  // Sends data to ThingSpeak
  ThingSpeak.setField(1, tempC);
  ThingSpeak.setField(2, humidity);
  ThingSpeak.writeFields(myChannelNumber, myWriteAPIKey);

  Serial.println("Data sent to ThingSpeak!"); //Confirms through serial monitor

  // Set Wait 60 seconds before next update
  delay(60000);
}


