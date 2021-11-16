''' Subscribes Environmental Sensor Data topic and parses data to InfluxDB.'''

import sys
import paho.mqtt.client as mqtt
import pandas as pd
from influxdb import InfluxDBClient
import time

# convert dictionary string to dictionary
# using json.loads()
import json

MQTT_ADDRESS = "140.180.133.81"  # IP of the MQTT broker 2018 Mac Mini i3 Server
MQTT_USER = 'admin'
MQTT_PASSWORD = 'admin'
MQTT_ESP32_SENSORS_TOPIC = 'dormhud/esp32/enviro_sensors'

# InfluxDB on 2018 Mac Mini i3 Server
INFLUXDB_ADDRESS = '140.180.133.81'  # Personal development Mac mini IP address
INFLUXDB_USER = 'admin'
INFLUXDB_PASSWORD = 'admin'
INFLUXDB_DATABASE = 'environment_sensor_raw_db'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD , None)


# Function to attach UTC Timestamp to sensor data
def timestamp_data() :
    time_now_utc = pd.Timestamp.now(tz='UTC')
    datetime_now_utc = pd.Timestamp.to_pydatetime(time_now_utc)  # Return the data as an array of native Python datetime objects.
    sensor_TIMESTAMP_dt = datetime_now_utc
    SENSOR_TIMESTAMP_str = sensor_TIMESTAMP_dt.strftime('%Y-%m-%dT%H:%M:%SZ')  # Need to convert datetime to string for InfluxDB Write points
    return SENSOR_TIMESTAMP_str


def on_connect(client , userdata , flags , rc) :
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_ESP32_SENSORS_TOPIC)


# Function to send payload to InfluxDB
def message_payload_to_JSON(msg) :
    try :
        # Convert Payload to string
        msg.payload = msg.payload.decode("utf-8")
        message_payload_str = str(msg.payload)

        # using json.loads()
        # convert dictionary string to dictionary
        message_dict = json.loads(message_payload_str)
        SENSOR_TIMESTAMP = timestamp_data()

        DEVICE_MAC_ID = message_dict["DEVICE_MAC_ID"]
        DEVICE_NAME = message_dict["DEVICE_NAME"]
        SENSOR_ID = message_dict["SENSOR_ID"]

        # Determines how to interpret data based on the Sensor ID
        # Creates JSON data and Put data in InfluxDB
        if SENSOR_ID == "Adafruit Bosch BME280" :
            TEMPERATURE_VALUE = message_dict["TEMPERATURE"]
            TEMPERATURE_UNITS = message_dict["TEMPERATURE_UNITS"]
            RELATIVE_HUMIDITY_VALUE = message_dict["HUMIDITY"]
            RELATIVE_HUMIDITY_UNITS = message_dict["HUMIDITY_UNITS"]

            # Convert Data to JSON format for InfluxDB entry
            json_body = [
                {
                    'measurement' : DEVICE_NAME ,
                    'tags' : {
                        'SENSOR_ID' : SENSOR_ID ,
                        'DEVICE_NAME' : DEVICE_NAME ,
                        'DEVICE_MAC_ID' : DEVICE_MAC_ID
                    } ,
                    'time' : SENSOR_TIMESTAMP ,
                    'fields' : {
                        't_value' : TEMPERATURE_VALUE ,
                        't_units' : TEMPERATURE_UNITS ,
                        'rh_value' : RELATIVE_HUMIDITY_VALUE ,
                        'rh_units' : RELATIVE_HUMIDITY_UNITS ,
                    }
                }
            ]

            influxdb_client.write_points(json_body)
            print(json_body)



        # Determines how to interpret data based on the Sensor ID
        # Creates JSON data and Put data in InfluxDB
        elif SENSOR_ID == "Adafruit TSL2591" :
            INFRARED_LIGHT_VALUE = message_dict["Infrared Light"]
            FULL_LIGHT_VALUE = message_dict["Full Light"]
            VISIBLE_LIGHT_VALUE = message_dict["Visible Light"]
            LUX_LIGHT_VALUE = message_dict["Lux Light"]
            LOCATION = "Main Dorm Area"

            # Convert Data to JSON format for InfluxDB entry
            json_body = [
                {
                    'measurement' : DEVICE_NAME ,
                    'tags' : {
                        'SENSOR_ID' : SENSOR_ID ,
                        'location' : LOCATION ,
                        'DEVICE_NAME' : DEVICE_NAME ,
                        'DEVICE_MAC_ID' : DEVICE_MAC_ID
                    } ,
                    'time' : SENSOR_TIMESTAMP ,
                    'fields' : {
                        'ir_value' : INFRARED_LIGHT_VALUE ,
                        'full_light_value' : FULL_LIGHT_VALUE ,
                        'vis_light_value' : VISIBLE_LIGHT_VALUE ,
                        'lux_light_value' : LUX_LIGHT_VALUE ,
                    }
                }
            ]

            influxdb_client.write_points(json_body)
            print(json_body)

        # Determines how to interpret data based on the Sensor ID
        # Creates JSON data and Put data in InfluxDB
        elif SENSOR_ID == "Sensirion SCD30 Sensor" :
            CO2_VALUE = message_dict["CO2"]
            CO2_UNITS = message_dict["CO2_UNITS"]
            TEMPERATURE_VALUE = message_dict["TEMPERATURE"]
            TEMPERATURE_UNITS = message_dict["TEMPERATURE_UNITS"]
            RELATIVE_HUMIDITY_VALUE = message_dict["HUMIDITY"]
            RELATIVE_HUMIDITY_UNITS = message_dict["HUMIDITY_UNITS"]
            LOCATION = "Main Dorm Area"

            # Convert Data to JSON format for InfluxDB entry
            json_body = [
                {
                    'measurement' : DEVICE_NAME ,
                    'tags' : {
                        'SENSOR_ID' : SENSOR_ID ,
                        'location' : LOCATION ,
                        'DEVICE_NAME' : DEVICE_NAME ,
                        'DEVICE_MAC_ID' : DEVICE_MAC_ID
                    } ,
                    'time' : SENSOR_TIMESTAMP ,
                    'fields' : {
                        'co2_value' : CO2_VALUE ,
                        'co2_units' : CO2_UNITS ,
                        't_value' : TEMPERATURE_VALUE ,
                        't_units' : TEMPERATURE_UNITS ,
                        'rh_value' : RELATIVE_HUMIDITY_VALUE ,
                        'rh_units' : RELATIVE_HUMIDITY_UNITS ,
                    }
                }
            ]

            influxdb_client.write_points(json_body)
            print(json_body)

        print()

    except :
        pass


def on_message(client , userdata , msg) :
    """The callback for when a PUBLISH message is received from the server."""
    try :
        # Sends payload to Function 'message_payload_to_JSON()' to transfer payload to InfluxDB
        message_payload_to_JSON(msg)
    except :
        pass


# The function _init_influxdb_database() initializes the InfluxDB database.
# If the database does not exist, it will be created through the function.
def _init_influxdb_database() :
    databases = influxdb_client.get_list_database()
    if len(list(filter(lambda x : x['name'] == INFLUXDB_DATABASE , databases))) == 0 :
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)


def main() :
    # Initializes the InfluxDB database
    _init_influxdb_database()

    while True :
        try :
            # Initializes the MQTT
            mqtt_client = mqtt.Client()
            mqtt_client.username_pw_set(MQTT_USER , MQTT_PASSWORD)
            mqtt_client.on_connect = on_connect
            mqtt_client.on_message = on_message
            mqtt_client.connect(MQTT_ADDRESS , 1883)
            mqtt_client.loop_forever()

        # Handles KeyboardInterrupt exception
        except KeyboardInterrupt :
            sys.exit()  # quit

        # Handles other exceptions
        except :
            time.sleep(10)  # Delay for 10 seconds
            continue  # Try again


if __name__ == '__main__' :
    print('ESP32 ENVIRONMENT SENSING MQTT to InfluxDB Server')
    main()
