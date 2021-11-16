# ''' Function to request power sensor data from ESP32 devices. '''
# Import modules
import paho.mqtt.client as mqtt
import time
from datetime import datetime
import sys

# MQTT Credentials
MQTT_ADDRESS = '140.180.133.113'  # Mac Pro Server 2 IP
BROKER_PORT = 1883
MQTT_USER = 'guest'
MQTT_PASSWORD = 'guest'

# Topics of interest
# MQTT_RPi_SENSORS_TOPIC = 'dormhud/rpi/sensors'
MQTT_ESP32_POWER_SENSORS_REQUEST_TOPIC = 'dormhud/esp32/request_power'


# publish callback function
def on_publish(client , userdata , result) :
    time_now = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')  # For simple debugging or logging
    print(time_now)  # For simple debugging or logging
    print("Data request was published with message")
    pass


# create client object and connect
client = mqtt.Client()
client.username_pw_set("guest" , password='guest')
client.connect(MQTT_ADDRESS , BROKER_PORT , 45)

# assign publish callback function
client.on_publish = on_publish


# Main Function to publish requests for power sensor data
def mqtt_esp32_power_request() :
    # publish messages
    while True :
        try :
            msg = "sensor_data_requested"
            ret = client.publish(MQTT_ESP32_POWER_SENSORS_REQUEST_TOPIC , msg)
            print(msg)
            time.sleep(40)
            print()

        # Handles KeyboardInterrupt exception
        except KeyboardInterrupt :
            sys.exit()  # quit

        # Handles other issues
        except :
            time_now_except = datetime.now()  # For simple debugging or logging
            print(time_now_except)  # For simple debugging00 or logging
            print("Failed to Power Data Request...")
            print("Will try again soon...")
            time.sleep(10)
            print()
            continue


def main() :
    mqtt_esp32_power_request()


if __name__ == '__main__' :
    print('MQTT Power Sensor Data Request')
    main()
