''' Makes Request for Power Sensor Data on topic 'dormhud/esp32/request_power' from ESP32.
Written for MQTT Broker 2018 Mac Mini i3 Server. '''

# Import modules
import paho.mqtt.client as mqtt
import time
from datetime import datetime
import sys

# MQTT Credentials
MQTT_ADDRESS = '140.180.133.81'  # IP of the MQTT broker 2018 Mac Mini i3 Server
MQTT_PORT = 1883
MQTT_USER = 'admin'
MQTT_PASSWORD = 'admin'

# Topics of interest
MQTT_ESP32_POWER_SENSORS_REQUEST_TOPIC = 'dormhud/esp32/request_power'

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

# Main Function to publish requests for power sensor data
def mqtt_esp32_power_request() :
    # Publish messages
    while True :
        try :
            msg = "sensor_data_requested"
            ret = client.publish(MQTT_ESP32_POWER_SENSORS_REQUEST_TOPIC , msg)
            print(msg)
            time.sleep(20)
            print()

        # Handles KeyboardInterrupt exception
        except KeyboardInterrupt :
            # quit
            sys.exit()

        # Handles other issues
        except :
            time_now_except = datetime.now()  # For simple debugging or logging
            print(time_now_except)  # For simple debugging00 or logging
            print("Failed to Power Data Request...")
            print("Will try again soon...")
            time.sleep(10)
            print()
            continue

# Main Function
def main() :
    mqtt_esp32_power_request()


if __name__ == '__main__' :
    print('MQTT Power Sensor Data Request')
    main()
