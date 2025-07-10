
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

// ---- WiFi & MQTT ----
const char* ssid = "Your_Wifi_SSID";

const char* password = "Your_Wifi_Password";
const char* mqtt_server = "127.0.0.1"; // Relace with Suscriber_Server_IP

// MQTT credentials
const char* mqtt_user = "espuser1";    // <-- Replace with your MQTT username
const char* mqtt_pass = "espuserpass";    // <-- Replace with your MQTT password

// ---- Sensor Settings ----
#define DHTPIN 5
#define PIRPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// ---- Optional: Ultrasonic Sensor (commented) ----
// #define TRIGPIN D6
// #define ECHOPIN D7

bool motionDetected = false;

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect("ESP8266Client", mqtt_user, mqtt_pass)) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      delay(2000);
    }
  }
}

void setup() {
  pinMode(PIRPIN, INPUT);
  // pinMode(TRIGPIN, OUTPUT);  // For ultrasonic sensor
  // pinMode(ECHOPIN, INPUT);   // For ultrasonic sensor
  Serial.begin(115200);
  dht.begin();
  setup_wifi();
  client.setServer(mqtt_server, 1883);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  float temp = dht.readTemperature();
  float hum = dht.readHumidity();
  motionDetected = digitalRead(PIRPIN);

  if (isnan(temp) || isnan(hum)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  String payload = "{";
  payload += "\"temperature\":" + String(temp, 2) + ",";
  payload += "\"humidity\":" + String(hum, 2) + ",";
  payload += "\"motion\":" + String(motionDetected ? "true" : "false");

  // ---- Ultrasonic Sensor Reading (commented out) ----
  /*
  digitalWrite(TRIGPIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIGPIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIGPIN, LOW);
  long duration = pulseIn(ECHOPIN, HIGH);
  float distance = duration * 0.034 / 2;
  payload += ",\"distance\":" + String(distance, 2);
  */

  payload += "}";

  client.publish("sensors/esp1/data", payload.c_str());
  Serial.println("Published: " + payload);

  delay(1500);
}
