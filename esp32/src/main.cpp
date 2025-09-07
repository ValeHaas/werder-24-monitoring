#include <Arduino.h>
// ...existing code...
#include <WiFi.h>
#include <HTTPClient.h>
// #include "HT_st7735.h"

#define WATER_SENSOR_PIN 19 // ESP32 pin GPIO19 connected to water sensor's pin
#define LED_PIN 2           // ESP32 pin GPIO2 connected to onboard LED

#define WIFI_SSID "GP7 VLH"                // replace with your WiFi SSID
#define WIFI_PASSWORD "WerDasLiestIstDoof" // replace with your WiFi password
#define AUTH_TOKEN "lkjbandcQWEfc3"        // Token for authenticating requests

// HT_st7735 st7735;

int current_water_state; // current state of water sensor
int prev_water_state;    // previous state of water sensor
bool water_alarm;        // Alarm is triggered
HTTPClient http;         // Create an HTTPClient object

void setup()
{
  Serial.begin(9600);

  // delay(1000);
  // st7735.st7735_init();

  // st7735.st7735_fill_screen(ST7735_BLACK);
  // st7735.st7735_write_str(0, 0, " Wassersensor");

  pinMode(WATER_SENSOR_PIN, INPUT_PULLUP);             // set ESP32 pin to input pull-up mode
  current_water_state = digitalRead(WATER_SENSOR_PIN); // read state
  water_alarm = (water_alarm || current_water_state == LOW);

  // Wifi connection
  Serial.print("Connecting to WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" connected!");
  // st7735.st7735_write_str(0, 60, "Verbunden mit" + (String)WIFI_SSID);

  // Notify API of startup
  if (WiFi.status() == WL_CONNECTED)
  {
    http.begin("https://werder-24.de/monitoring/ug/rohrbruch/startup?auth_token=" + (String)AUTH_TOKEN);
    int httpResponseCode = http.GET();
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    http.end();
  }

  // Notify initial state
  if ((prev_water_state == HIGH && current_water_state == LOW))
  {
    Serial.println("Start: Water leakage is detected!");
    // st7735.st7735_write_str(0, 20, "!!! Wasseraustritt detektiert !!!");
  }
  else
  {
    Serial.println("Start: No water leakage.");
    // st7735.st7735_write_str(0, 20, "Kein Wasseraustritt detektiert");
  }
}

void loop()
{
  prev_water_state = current_water_state;              // save the last state
  current_water_state = digitalRead(WATER_SENSOR_PIN); // read new state

  if ((prev_water_state == HIGH && current_water_state == LOW))
  {
    water_alarm = true;
    Serial.println("Water leakage is detected!");
    // st7735.st7735_write_str(0, 20, "!!! Wasseraustritt detektiert !!!");″
    // Send HTTP request to API endpoint
    if (WiFi.status() == WL_CONNECTED)
    {
      http.begin("https://werder-24.de/monitoring/ug/rohrbruch/alarm?auth_token=" + (String)AUTH_TOKEN);
      int httpResponseCode = http.GET();
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
      http.end();
    }
    else
    {
      Serial.println("WiFi not connected, cannot send alarm!");
    }
  }

  if (water_alarm) // blink
  {
    Serial.println("Alarm triggered, reset to end it.");
    digitalWrite(LED_PIN, HIGH); // turn the LED on
    delay(100);                  // wait for 100 milliseconds
    digitalWrite(LED_PIN, LOW);  // turn the LED off by making the voltage LOW
  }
  delay(150); // wait for 100 milliseconds
}