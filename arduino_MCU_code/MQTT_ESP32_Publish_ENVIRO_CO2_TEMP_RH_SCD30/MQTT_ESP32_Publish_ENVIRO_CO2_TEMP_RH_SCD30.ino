// Program written by and Property of Kiera Robinson
// Program Details: MQTT Program to that publishes sensor data (CO₂, Temperature, and Relative Humidity) from SparkFun Electronic Sensirion SCD30 Sensor
// Program Revision: 2020.12.26
// 2020.12.24 : Debugging: 2 LED FLashes means success. 3 LED flashes mean failure.
// 2020.12.26 : Added reconnection functions for both WiFi and MQTT; Added OTA Function; Rearranged connection to WiFi since it is needed regardless
//              of connection to sensor
// 2021.01.28 : Made code revisions in an attempt to address ESP32 lack of response with time.
// 2021.04.24 : Made code revisions to change MQTT broker adrress to be 2018 Mac Mini i3 Server


// For JSON data encoding when publishing payload
#include <ArduinoJson.h>

// MQTT Library
#include <PubSubClient.h>

//WiFI Library
#include <WiFi.h>
#include <WiFiAP.h>
#include <WiFiMulti.h>
#include <WiFiUdp.h>
#include <WiFiScan.h>
#include <ETH.h>
#include <WiFiClient.h>
#include <WiFiSTA.h>
#include <WiFiServer.h>
#include <WiFiType.h>
#include <WiFiGeneric.h>

// For OTA Update Function
#include <WebServer.h>
#include <ESPmDNS.h>
#include <Update.h>

// The Sensirion SCD30 Sensor: CO2, Humidity & Temperature Sensor Library
// Product Page: https://www.sparkfun.com/products/15112
// PRODUCT ID: SEN-15112
// Click here to get the library: http://librarymanager/All#SparkFun_SCD30
#include <Wire.h>
#include "SparkFun_SCD30_Arduino_Library.h"

// Sensirion SCD30 Sensor: CO2, Humidity & Temperature Sensor
SCD30 airSensor;

// Princeton Servicenet Wireless Network credentials
const char* ssid = "internet";
const char* password =  "";


// MQTT Server Credentials
// Credentials for Mac Pro Server 2
//const char* mqttServer = "140.180.133.113"; // IP of the MQTT broker Mac Pro Server 2
const char* mqttServer = "140.180.133.81"; // IP of the MQTT broker 2018 Mac Mini i3 Server
const int mqttPort = 1883; // 1883 is the listener port for the Broker
const char* mqttUser = "admin"; // MQTT username
const char* mqttPassword = "admin" // MQTT password


const char* sensor_pub_topic = "dormhud/esp32/enviro_sensors"; // MQTT topic to publish environment sensor data

// Initialise the WiFi and MQTT Client objects
WiFiClient espClient;
PubSubClient client(espClient);

// For OTA Code
const char* host = "ESP32";

// For OTA Webpage
WebServer server(80);

/*
   Login page
*/

const char* loginIndex =
  "<form name='loginForm'>"
  "<table width='20%' bgcolor='A09F9F' align='center'>"
  "<tr>"
  "<td colspan=2>"
  "<center><font size=4><b>ESP32 Login Page</b></font></center>"
  "<br>"
  "</td>"
  "<br>"
  "<br>"
  "</tr>"
  "<td>Username:</td>"
  "<td><input type='text' size=25 name='userid'><br></td>"
  "</tr>"
  "<br>"
  "<br>"
  "<tr>"
  "<td>Password:</td>"
  "<td><input type='Password' size=25 name='pwd'><br></td>"
  "<br>"
  "<br>"
  "</tr>"
  "<tr>"
  "<td><input type='submit' onclick='check(this.form)' value='Login'></td>"
  "</tr>"
  "</table>"
  "</form>"
  "<script>"
  "function check(form)"
  "{"
  "if(form.userid.value=='admin' && form.pwd.value=='admin')"
  "{"
  "window.open('/serverIndex')"
  "}"
  "else"
  "{"
  " alert('Error Password or Username')/*displays error message*/"
  "}"
  "}"
  "</script>";

/*
   Server Index Page
*/

const char* serverIndex =
  "<script src='https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js'></script>"
  "<form method='POST' action='#' enctype='multipart/form-data' id='upload_form'>"
  "<input type='file' name='update'>"
  "<input type='submit' value='Update'>"
  "</form>"
  "<div id='prg'>progress: 0%</div>"
  "<script>"
  "$('form').submit(function(e){"
  "e.preventDefault();"
  "var form = $('#upload_form')[0];"
  "var data = new FormData(form);"
  " $.ajax({"
  "url: '/update',"
  "type: 'POST',"
  "data: data,"
  "contentType: false,"
  "processData:false,"
  "xhr: function() {"
  "var xhr = new window.XMLHttpRequest();"
  "xhr.upload.addEventListener('progress', function(evt) {"
  "if (evt.lengthComputable) {"
  "var per = evt.loaded / evt.total;"
  "$('#prg').html('progress: ' + Math.round(per*100) + '%');"
  "}"
  "}, false);"
  "return xhr;"
  "},"
  "success:function(d, s) {"
  "console.log('success!')"
  "},"
  "error: function (a, b, c) {"
  "}"
  "});"
  "});"
  "</script>";





// Function on receipt of message
void callback(char* topic, byte* payload, unsigned int length) {

  Serial.print("Message has been received in MQTT topic: ");
  Serial.println(topic);

  Serial.print("Message is: ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }

  Serial.println();
  Serial.println("Authenticating Message...");

  // Compares payload string to safe word and only publishes if there is a match
  // Found at: https://arduino.stackexchange.com/questions/55024/how-to-convert-byte-payload-to-string
  if (!strncmp((char *)payload, "sensor_data_requested", length))
  {

    Serial.println("Message Authenticated.");

    //    Wire.begin();
    //    airSensor.begin();
    //    delay(50);

    // Checks if data is available from Sensirion SCD30 Sensor
    while (!airSensor.dataAvailable()) {
      delay(1000);
    }


    // Notice to alert that data is available from Sensirion SCD30 Sensor
    Serial.println("Data available from Sensirion SCD30 Sensor.");

    // Brief LED Light  to Notify of Success
    digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
    delay(300);                       // wait for 3/10 of a second
    digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW

    // Prints out CO2, Temperature, and Relative Humidity from Sensirion SCD30 Sensor
    float CO2 = airSensor.getCO2();
    float temperature = airSensor.getTemperature();
    float humidity = airSensor.getHumidity();
    Serial.println("Gathering data from Sensirion SCD30 Sensor...");
    Serial.print("CO2 (ppm): "); Serial.print(CO2); Serial.print("\t\t");
    Serial.print("Temperature (C): "); Serial.print(temperature); Serial.print("\t\t");
    Serial.print("Humidity(%): "); Serial.println(humidity);

    // CO2 Variable
    char charCO2[] = "00.00";
    // Temperature Variable
    char charTemperature[] = "00.00";
    // Humidity Variable
    char charHumidity[] = "00.00";

    // Converts Float to String
    // dtostrf(FLOAT,WIDTH,PRECSISION,BUFFER);
    // WIDTH is the number of characters to use in the output.
    // PRECISION is the number of characters after the decimal point.
    // BUFFER is where the write the characters to.
    dtostrf(CO2, 4, 0, charCO2);
    dtostrf(temperature, 4, 2, charTemperature);
    dtostrf(humidity, 4, 2, charHumidity);

    // Encodes data in JSON Format
    // Sourced from guide at: https://techtutorialsx.com/2017/04/29/esp32-sending-json-messages-over-mqtt/
    // Requires a class from ArduinoJson 5 NOT version 6. For example, use version 5.13.5
    // See guide for this error: https://arduinojson.org/v6/error/jsonbuffer-is-a-class-from-arduinojson-5/
    StaticJsonBuffer<300> JSONbuffer;
    JsonObject& JSONencoder = JSONbuffer.createObject();
    JSONencoder["DEVICE_NAME"] = "ESP32_Personal_SCD30";
    JSONencoder["DEVICE_MAC_ID"] = WiFi.macAddress();
    JSONencoder["SENSOR_ID"] = "Sensirion SCD30 Sensor";
    JSONencoder["CO2"] = charCO2;
    JSONencoder["CO2_UNITS"] = "PPM";
    JSONencoder["TEMPERATURE"] = charTemperature;
    JSONencoder["TEMPERATURE_UNITS"] = "CELSIUS";
    JSONencoder["HUMIDITY"] = charHumidity;
    JSONencoder["HUMIDITY_UNITS"] = "%";
    char JSONmessageBuffer[300];
    JSONencoder.printTo(JSONmessageBuffer, sizeof(JSONmessageBuffer));
    Serial.println("Publishing requested sensor data to MQTT Server...");
    Serial.println(JSONmessageBuffer);
    client.publish(sensor_pub_topic, JSONmessageBuffer);  // Test publish
    Serial.println("Data Published.");
    Serial.println("Transmission terminated.");
    Serial.println("-----------------------");

    // Longer Light LED to Notify of Completion
    digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
    delay(1000);                       // wait for a second
    digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW

    Serial.println();
  }
  else
  {
    Serial.println("Message not Authenticated.");
    Serial.println("-----------------------");

    // Long Triple Light LED to Notify of Failure
    digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
    delay(1000);                       // wait for a second
    digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
    delay(1000);                       // wait for a second    // Light LED to Notify of Success
    digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
    delay(1000);                       // wait for a second
    digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
    delay(1000);                       // wait for a second
    digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
    delay(1000);                       // wait for a second
    digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW

    Serial.println();
  }
}

void setup() {
  // initialize digital pin LED_BUILTIN as an output LED Light
  pinMode(LED_BUILTIN, OUTPUT);

  //   Serial.begin(9600);
  Serial.begin(115200);

  // Start WiFi and OTA Function
  setup_wifi_OTA();

  // Starting Sensirion SCD30 Sensor
  Serial.println(F("Establishing connection to Sensirion SCD30 Sensor..."));

  // Needed for use of Sensirion SCD30 Sensor
  Wire.begin();

  //  Establish connection to Sensirion SCD30 Sensor
  while (!airSensor.begin()) {
    delay(100);
  }

  Serial.println(F("Connected to Sensirion SCD30 Sensor."));

  // Establishing connection to MQTT Server only if connection to Sensirion SCD30 Sensor is established
  Serial.println("Establishing connection to MQTT Server...");
  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);

  // Starts this program block if MQTT Server connection is successful
  while (!client.connected())
  {

    // Unique name for Client or else MQTT will not be able to handle multiple messages with on_message function
    // MAC ADDRESS will be used as Client Name
    String clientName = WiFi.macAddress();
    if (client.connect((char*) clientName.c_str(), mqttUser, mqttPassword) )
    {
      Serial.print("Connection established to MQTT Server ");
      Serial.print("with Client Name: "); Serial.println(clientName);

      // MQTT Topic for Environmental Sensing
      client.subscribe("dormhud/esp32/request_enviro");
    }
    else
    {
      // Notice if connection to MQTT server fails. Prints state. Tries to establish a connection with MQTT Server again.
      Serial.print("Connection failed to establish with state: ");
      Serial.println(client.state());
      delay(2000);
    }
  }
}





void setup_wifi_OTA() {

  // Delay 1 second
  delay(1000);

  // Attempt connection to WiFi
  Serial.print("Establishing connection to WiFi Network ");
  Serial.print(ssid); Serial.println(".");


  // If no WiFi connection established, it will try again
  while (WiFi.begin(ssid, password) != WL_CONNECTED) {
    Serial.println("No WiFi Connection established.");
    Serial.print("Attempting to establish connection to WiFi network: ");
    Serial.print(ssid); Serial.println(".");
    delay(500);
  }

  // WiFi Connection established notice.
  Serial.print("Connection established to WiFi Network: ");
  Serial.print(ssid); Serial.println(".");

  // Print IP address of ESP32 device
  Serial.print("IP address: "); Serial.print(WiFi.localIP()); Serial.println(".");

  // Included code for OTA update
  /*use mdns for host name resolution*/
  while (!MDNS.begin(host)) { //http://esp32.local
    Serial.println("Error setting up MDNS responder!");
    delay(1000);
  }


  Serial.println("mDNS Responder Started.");
  /*return index page which is stored in serverIndex */
  server.on("/", HTTP_GET, []() {
    server.sendHeader("Connection", "close");
    server.send(200, "text/html", loginIndex);
  });
  server.on("/serverIndex", HTTP_GET, []() {
    server.sendHeader("Connection", "close");
    server.send(200, "text/html", serverIndex);
  });
  /*handling uploading firmware file */
  server.on("/update", HTTP_POST, []() {
    server.sendHeader("Connection", "close");
    server.send(200, "text/plain", (Update.hasError()) ? "FAIL" : "OK");
    ESP.restart();
  }, []() {
    HTTPUpload& upload = server.upload();
    if (upload.status == UPLOAD_FILE_START) {
      Serial.printf("Update: %s\n", upload.filename.c_str());
      if (!Update.begin(UPDATE_SIZE_UNKNOWN)) { //start with max available size
        Update.printError(Serial);
      }
    } else if (upload.status == UPLOAD_FILE_WRITE) {
      /* flashing firmware to ESP*/
      if (Update.write(upload.buf, upload.currentSize) != upload.currentSize) {
        Update.printError(Serial);
      }
    } else if (upload.status == UPLOAD_FILE_END) {
      if (Update.end(true)) { //true to set the size to the current progress
        Serial.printf("Update Success: %u\nRebooting...\n", upload.totalSize);
      } else {
        Update.printError(Serial);
      }
    }
  });
  server.begin();
}



// This loop is to re-establish lost connection to MQTT Server
void reconnect_mqtt() {

  // Loop until we're reconnected to MQTT Server
  while ((!client.connected()) && (WiFi.status() == WL_CONNECTED)) {

    // Establishing connection to MQTT Server
    Serial.println("Establishing connection to MQTT Server...");
    client.setServer(mqttServer, mqttPort);
    client.setCallback(callback);

    // Unique name for Client or else MQTT will not be able to handle multiple messages with on_message function
    // MAC ADDRESS will be used as Client Name
    String clientName = WiFi.macAddress();
    if (client.connect((char*) clientName.c_str()), mqttUser, mqttPassword ) {
      Serial.print("Connection re-established to MQTT Server ");
      Serial.print("with Client Name: "); Serial.println(clientName);

      // Resubscribe to MQTT Topic for Environmental Sensing
      client.subscribe("dormhud/esp32/request_enviro");
    }
    else
    {
      // Print failed re-connection state
      Serial.print("Connection failed to establish with state: ");
      Serial.print(client.state());
      Serial.println("Will try to re-establish connection to MQTT Server in 5 seconds");

      // Wait 5 seconds before retrying to re-establish lost connection to MQTT Server
      delay(5000);
    }
  }
}



// Function to re-establish lost WiFi Connection
void reconnect_wifi() {

  // Delay 1 second
  delay(1000);

  // Attempt re-connection to WiFi
  Serial.print("Attempting to re-establishing connection to WiFi Network: ");
  Serial.print(ssid); Serial.println(".");

  while (WiFi.begin(ssid, password) != WL_CONNECTED) {
    Serial.print("No WiFi Connection could be re-established to ");
    Serial.print(ssid); Serial.println(".");
    Serial.println("Will attempt to re-establish connection again...");
    delay(1000);  // Delay 1 second
  }

  // WiFi Connection established notice.
  Serial.println("Connection established to WiFi Network!");

  // Print IP address of ESP32 device
  Serial.print("IP address: "); Serial.print(WiFi.localIP()); Serial.println(".");
}



void loop() {

  //  If WiFi connection is lost, retry to re-establish WiFi connection
  if (WiFi.status() != WL_CONNECTED)
  {
    reconnect_wifi();
  }

  server.handleClient();
  delay(1);

  //  Tries to reconnect to MQTT Server if disconnected
  if (!client.connected()) {
    reconnect_mqtt();
  }
  if (client.connected()) {
    // Loops MQTT subscription to callback
    client.loop();
  }
}
