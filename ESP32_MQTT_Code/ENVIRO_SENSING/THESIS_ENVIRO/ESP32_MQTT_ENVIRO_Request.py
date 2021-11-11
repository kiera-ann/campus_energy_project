''' Makes Request for Environmental Sensor Data on topic 'dormhud/esp32/request_enviro' from ESP32.
Written for MQTT Broker 2018 Mac Mini i3 Server. '''

import sys
import paho.mqtt.client as mqtt
import time
from datetime import datetime

# MQTT Credentials
MQTT_ADDRESS = '140.180.133.81'  # IP of the MQTT broker 2018 Mac Mini i3 Server
MQTT_PORT = 1883
MQTT_USER = 'admin'
MQTT_PASSWORD = 'admin'
MQTT_ESP32_ENVIRONMENT_SENSORS_REQUEST_TOPIC = 'dormhud/esp32/request_enviro'


# Publish callback function
def on_publish(client , userdata , result) :
    time_now = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')  # For simple debugging or logging
    print(time_now)  # For simple debugging or logging
    print("Data request was published with message")
    pass


# Create client object and connect
client = mqtt.Client()
client.username_pw_set(MQTT_USER , password=MQTT_PASSWORD)
client.connect(MQTT_ADDRESS , MQTT_PORT , 45)

# Assign publish callback function
client.on_publish = on_publish


# Function to Request MQTT ENVIRO data from deployed ESP32 MCUs
def mqtt_enviro_request_data() :
    while True :
        try :
            # Message for data request
            msg = "sensor_data_requested"
            ret = client.publish(MQTT_ESP32_ENVIRONMENT_SENSORS_REQUEST_TOPIC , msg)
            print(msg)

            # Delay for 40 seconds
            time.sleep(40)

            print()

        # Handles KeyboardInterrupt exception
        except KeyboardInterrupt :
            # quit
            sys.exit()

        # Handles other exceptions
        except :
            # Delay for 10 seconds
            time.sleep(10)

            # Try again
            continue


# Main Function
def main() :
    mqtt_enviro_request_data()


if __name__ == '__main__' :
    print('MQTT ESP32 ENVIRONMENT SENSING Request')
    main()
