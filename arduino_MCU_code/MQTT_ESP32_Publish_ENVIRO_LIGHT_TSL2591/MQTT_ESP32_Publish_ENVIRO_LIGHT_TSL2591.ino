// Program written by and Property of Kiera Robinson.
// Program Details: MQTT Program to that publishes sensor data (IR/Visible/Full/Lux Light) from Adafruit TSL2591 High Dynamic Range Digital Light Sensor
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

// The Adafruit TSL2591 High Dynamic Range Digital Light Sensor (IR/Visible/Full/Lux Light)
// Product Page: https://www.adafruit.com/product/1980
// PRODUCT ID: 1980
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include "Adafruit_TSL2591.h"

// The Adafruit TSL2591 High Dynamic Range Digital Light Sensor (IR/Visible/Full/Lux Light)
Adafruit_TSL2591 tsl = Adafruit_TSL2591(2591); // pass in a number for the sensor identifier (for your use later)

// Princeton Servicenet Wireless Network credentials
const char* ssid = "internet";
const char* password =  "";


// MQTT Server Credentials
// Credentials for Mac Pro Server 2
//const char* mqttServer = "140.180.133.113"; // IP of the MQTT broker Mac Pro Server 2
const char* mqttServer = "140.180.133.81"; // IP of the MQTT broker 2018 Mac Mini i3 Server
const int mqttPort = 1883; // 1883 is the listener port for the Broker
const char* mqttUser = "admin"; // MQTT username
const char* mqttPassword = "admin"; // MQTT password

//const char* sensor_pub_topic = "dormhud/esp32/enviro_light_sensors"; // MQTT topic to publish environment light sensor data for debugging
const char* sensor_pub_topic = "dormhud/esp32/enviro_sensors"; // MQTT topic to publish all environment sensor data

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

    // Brief LED Light  to Notify of Success
    digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
    delay(300);                       // wait for 3/10 of a second
    digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW

    // Section copied from example code from Adafruit TSL2591 Sensor "void advancedRead(void)" function
    // More advanced data read example. Read 32 bits with top 16 bits IR, bottom 16 bits full spectrum
    // That way you can do whatever math and comparisons you want!
    uint32_t lum = tsl.getFullLuminosity();
    uint16_t ir, full;
    ir = lum >> 16;
    full = lum & 0xFFFF;

    //    // Added in since it does not appear to calculate values for visible and store in a variable
    //    float visible = full - ir;
    //    float lux = (tsl.calculateLux(full, ir), 6);

    // Prints out Light Data from Adafruit TSL2591 Sensor
    Serial.println("Gathering data from Adafruit TSL2591 Sensor...");
    Serial.print(F("IR: ")); Serial.print(ir);  Serial.print(F("  "));
    Serial.print(F("Full: ")); Serial.print(full); Serial.print(F("  "));
    //    Serial.print(F("Visible: ")); Serial.print(visible); Serial.print(F("  "));
    //    Serial.print(F("Lux: ")); Serial.println(lux);

    Serial.print(F("Visible: ")); Serial.print(full - ir); Serial.print(F("  "));
    Serial.print(F("Lux: ")); Serial.println(tsl.calculateLux(full, ir), 6);

    // Added in since it does not appear to calculate values for visible and store in a variable
    // Lux seems to work better when calculated without the 6 part at the end
    float visible = full - ir;
    float lux = tsl.calculateLux(full, ir);
    // Serial.print(F("Calculated Lux: ")); Serial.println(lux);    // Added in for debugging of Lux

    // Infrared Light Variable (Int)
    char charInfrared[] = "00.00";

    // Full spectrum (IR + visible) Light Variable (Int)
    char charFull[] = "00.00";

    // Visible Light Variable (Int)
    char charVisible[] = "00.00";

    // Lux Light Variable (Float with 2 decimal figures)
    char charLux[] = "00.00";

    // Converts Float to String
    // dtostrf(FLOAT,WIDTH,PRECSISION,BUFFER);
    // WIDTH is the number of characters to use in the output.
    // PRECISION is the number of characters after the decimal point.
    // BUFFER is where the write the characters to.
    dtostrf(ir, 4, 0, charInfrared);
    dtostrf(full, 4, 0, charFull);
    dtostrf(visible, 4, 0, charVisible);
    dtostrf(lux, 6, 2, charLux);

    // Encodes data in JSON Format
    // Sourced from guide at: https://techtutorialsx.com/2017/04/29/esp32-sending-json-messages-over-mqtt/
    // Requires a class from ArduinoJson 5 NOT version 6. For example, use version 5.13.5
    // See guide for this error: https://arduinojson.org/v6/error/jsonbuffer-is-a-class-from-arduinojson-5/
    StaticJsonBuffer<300> JSONbuffer;
    JsonObject& JSONencoder = JSONbuffer.createObject();
    JSONencoder["DEVICE_NAME"] = "ESP32_Personal_TSL2591";
    JSONencoder["DEVICE_MAC_ID"] = WiFi.macAddress();
    JSONencoder["SENSOR_ID"] = "Adafruit TSL2591";
    JSONencoder["Infrared Light"] = charInfrared;
    JSONencoder["Full Light"] = charFull;
    JSONencoder["Visible Light"] = charVisible;
    JSONencoder["Lux Light"] = charLux;
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
  else {
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


/**************************************************************************/
/*
    Displays some basic information on this sensor from the unified
    sensor API sensor_t type (see Adafruit_Sensor for more information)
*/
/**************************************************************************/
void displaySensorDetails(void)
{
  sensor_t sensor;
  tsl.getSensor(&sensor);
  Serial.println(F("------------------------------------"));
  Serial.print  (F("Sensor:       ")); Serial.println(sensor.name);
  Serial.print  (F("Driver Ver:   ")); Serial.println(sensor.version);
  Serial.print  (F("Unique ID:    ")); Serial.println(sensor.sensor_id);
  Serial.print  (F("Max Value:    ")); Serial.print(sensor.max_value); Serial.println(F(" lux"));
  Serial.print  (F("Min Value:    ")); Serial.print(sensor.min_value); Serial.println(F(" lux"));
  Serial.print  (F("Resolution:   ")); Serial.print(sensor.resolution, 4); Serial.println(F(" lux"));
  Serial.println(F("------------------------------------"));
  Serial.println(F(""));
}



/**************************************************************************/
/*
    Configures the gain and integration time for the TSL2591
*/
/**************************************************************************/
void configureSensor(void)
{
  // You can change the gain on the fly, to adapt to brighter/dimmer light situations
  //tsl.setGain(TSL2591_GAIN_LOW);    // 1x gain (bright light)
  tsl.setGain(TSL2591_GAIN_MED);      // 25x gain
  //tsl.setGain(TSL2591_GAIN_HIGH);   // 428x gain

  // Changing the integration time gives you a longer time over which to sense light
  // longer timelines are slower, but are good in very low light situtations!
  //tsl.setTiming(TSL2591_INTEGRATIONTIME_100MS);  // shortest integration time (bright light)
  // tsl.setTiming(TSL2591_INTEGRATIONTIME_200MS);
  tsl.setTiming(TSL2591_INTEGRATIONTIME_300MS);
  // tsl.setTiming(TSL2591_INTEGRATIONTIME_400MS);
  // tsl.setTiming(TSL2591_INTEGRATIONTIME_500MS);
  // tsl.setTiming(TSL2591_INTEGRATIONTIME_600MS);  // longest integration time (dim light)

  /* Display the gain and integration time for reference sake */
  Serial.println(F("------------------------------------"));
  Serial.print  (F("Gain:         "));
  tsl2591Gain_t gain = tsl.getGain();
  switch (gain)
  {
    case TSL2591_GAIN_LOW:
      Serial.println(F("1x (Low)"));
      break;
    case TSL2591_GAIN_MED:
      Serial.println(F("25x (Medium)"));
      break;
    case TSL2591_GAIN_HIGH:
      Serial.println(F("428x (High)"));
      break;
    case TSL2591_GAIN_MAX:
      Serial.println(F("9876x (Max)"));
      break;
  }
  Serial.print  (F("Timing:       "));
  Serial.print((tsl.getTiming() + 1) * 100, DEC);
  Serial.println(F(" ms"));
  Serial.println(F("------------------------------------"));
  Serial.println(F(""));
}



void setup() {
  // initialize digital pin LED_BUILTIN as an output LED Light
  pinMode(LED_BUILTIN, OUTPUT);

  //  Serial.begin(9600);
  Serial.begin(115200);

  // Start WiFi and OTA Function
  setup_wifi_OTA();

  // Starting Adafruit TSL2591 Sensor
  Serial.println(F("Establishing connection to Adafruit TSL2591 Sensor..."));

  //  Establish connection to Adafruit TSL2591 Sensor
  while (!tsl.begin()) {
    delay(100);
  }

  //  Only printed if connection to sensor is successful
  Serial.println(F("Connected to Adafruit TSL2591 sensor."));

  /* Display some basic information on this sensor */
  Serial.println(F("Basic Information on Adafruit TSL2591 Sensor."));
  displaySensorDetails();

  /* Configure the sensor */
  Serial.println(F("Configuring Adafruit TSL2591 Sensor..."));
  configureSensor();

  // Establishing connection to MQTT Server only if connection to Adafruit TSL2591 Sensor is established
  Serial.println("Establishing connection to MQTT Server...");
  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);

  // Starts this program block if MQTT Server connection is successful
  while (!client.connected()) 
  {
    // Unique name for Client or else MQTT will not be able to handle multiple messages with on_message function
    // MAC ADDRESS will be used as Client Name since it is unique
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


// OTA related code block for remotely deploying code
void setup_wifi_OTA() {

  // Delay 1 second
  delay(1000);

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
    if (client.connect((char*) clientName.c_str(), mqttUser, mqttPassword) ) {
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
