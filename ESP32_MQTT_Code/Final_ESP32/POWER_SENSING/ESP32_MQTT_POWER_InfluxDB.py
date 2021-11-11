# Use this to test MQTTInfluxDBBridge.py

import paho.mqtt.client as mqtt
import pandas as pd
import sys
import time
from influxdb import InfluxDBClient

# Function to calculate kiloWatts per hour from Dorm Power Sensors
from Campus_data_code.dorm_level_calculations.dorm_room_energy_calculations import write_DR_energy_to_InfluxDB

# Function to Calculate Dorm Room Level Energy CO2
from Campus_data_code.dorm_level_calculations.dorm_room_energy_co2_calculations import write_recent_dr_energy_co2_to_InfluxDB

# convert dictionary string to dictionary
# using json.loads()
import json

MQTT_ADDRESS = '140.180.133.113'
MQTT_USER = 'guest'
MQTT_PASSWORD = 'guest'
MQTT_ESP32_POWER_SENSORS_TOPIC = 'dormhud/esp32/power'

# InfluxDB on CHAOS RPi
INFLUXDB_ADDRESS = '140.180.133.81'  # Personal development Mac mini IP address
INFLUXDB_USER = 'admin'
INFLUXDB_PASSWORD = 'admin'
INFLUXDB_DATABASE = 'dormroom_power_database_raw'

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
    client.subscribe(MQTT_ESP32_POWER_SENSORS_TOPIC)


def on_disconnect(client , userdata , rc) :
    print("client disconnected ok \n")


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
        LOCATION_NUMBER = message_dict["LOCATION"]

        # Determines how to interpret data based on the Sensor ID
        # Creates JSON data and Put data in InfluxDB
        if SENSOR_ID == "Modern Device Current Sensor" :
            ANALOG_VALUE = message_dict["ANALOG_Value"]
            VOLTAGE_VALUE = message_dict["VOLTAGE"]
            VOLTAGE_UNITS = message_dict["VOLTAGE_UNITS"]
            POWER_VALUE = message_dict["POWER"]
            POWER_UNITS = message_dict["POWER_UNITS"]
            LOCATION = (str("Main Dorm Area" + ": SOCKET ADDRESS " + DEVICE_MAC_ID))
            MEASUREMENT_NAME = (str("ESP32_POWER_SENSOR: " + DEVICE_MAC_ID))

        # Convert Data to JSON format for InfluxDB entry
        DEVICE_json_body = [
            {
                "measurement" : MEASUREMENT_NAME ,
                "tags" : {
                    'DEVICE_NAME' : DEVICE_NAME ,
                    'DEVICE_MAC_ID' : DEVICE_MAC_ID ,
                    'SENSOR_ID' : SENSOR_ID ,
                    'location' : LOCATION ,
                    'location_number' : LOCATION_NUMBER ,
                } ,
                "time" : SENSOR_TIMESTAMP ,
                "fields" : {
                    "ANALOG_VALUE" : ANALOG_VALUE ,
                    "VOLTAGE_VALUE" : VOLTAGE_VALUE ,
                    "VOLTAGE_UNITS" : VOLTAGE_UNITS ,
                    "POWER_VALUE" : POWER_VALUE ,
                    "POWER_UNITS" : POWER_UNITS ,
                }
            }
        ]

        # Send to function to write RAW Power json data to InfluxDB,
        # calculate energy and Energy CO2 and write that date to InfluxDB
        dorm_room_energy_InfluxDB(DEVICE_json_body)

    except :
        pass


# Function to write RAW Power json data to InfluxDB, calculate energy and Energy CO2 and write that date to InfluxDB
def dorm_room_energy_InfluxDB(json_body) :
    influxdb_client.write_points(json_body)
    print(json_body)  # Debugging print statement

    # Done to extract item from the list
    data_set = json_body[0]
    data_set.items()
    measurement_name = str(data_set["measurement"])
    # print(measurement_name)

    # Function to request energy calculations
    write_DR_energy_to_InfluxDB(measurement_name)

    # Function to request energy CO2 calculations
    write_recent_dr_energy_co2_to_InfluxDB(measurement_name)


def on_message(client , userdata , msg) :
    """The callback for when a PUBLISH message is received from the server."""
    try :
        message_payload_to_JSON(msg)
        # client.disconnect()
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
            mqtt_client.on_disconnect = on_disconnect
            mqtt_client.loop_forever()

        # Handles KeyboardInterrupt exception
        except KeyboardInterrupt :
            # quit
            sys.exit()

        # Handles other issues
        except :
            time.sleep(5)
            continue


if __name__ == '__main__' :
    print('ESP32 POWER SENSING MQTT to InfluxDB Server')
    main()
