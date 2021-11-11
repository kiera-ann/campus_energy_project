''' Function to calculate kiloWatts per hour from Dorm Power Sensors '''
import pandas as pd
from influxdb import InfluxDBClient

# INFLUXDB Dorm RAW Power Data
INFLUXDB_ADDRESS = '140.180.133.81'  # Personal development Mac mini IP address
INFLUXDB_USER = 'admin'
INFLUXDB_PASSWORD = 'admin'
INFLUXDB_DATABASE = 'dormroom_power_database_raw'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD , None)

# For computed Dorm room (DR) Energy Database
INFLUXDB_USER_DR_Energy = 'admin'
INFLUXDB_PASSWORD_DR_Energy = 'admin'
INFLUXDB_DATABASE_DR_Energy = 'dormroom_energy_database_raw'

influxdb_client_DR_Energy = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER_DR_Energy , INFLUXDB_PASSWORD_DR_Energy ,
                                           database=INFLUXDB_DATABASE_DR_Energy)


# Initialize databases
def _init_influxdb_database() :
    databases = influxdb_client.get_list_database()  # check if the database is there by using the get_list_database() function of the client:
    if len(list(filter(lambda x : x['name'] == INFLUXDB_DATABASE , databases))) == 0 :
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)  # we’ll set the client to use this database


# Build query for database query of last 2 points for power from sensor
def influxdb_query_builder_DR_Power_W(sensor_data_stream_id) :
    # Set data_field provided to function to variable "data_field_label_str"
    data_field_label_str = str(sensor_data_stream_id)
    query_p1 = 'SELECT "POWER_VALUE" FROM "dormroom_power_database_raw"."autogen".'
    query_p2 = '"'
    query_p3 = data_field_label_str
    query_p4 = '"'
    query_p5 = " WHERE time > now() - 12h ORDER BY time DESC LIMIT 2"

    # Concatenate string
    full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)

    # print(full_query_string)    # Debugging print statement
    return full_query_string


# Debugging function
# print(influxdb_query_builder_DR_Power_W()) # Debugging print statement


# Function to query last 2 values
def query_last_2_values_DR_Power_InfluxDB(sensor_data_stream_id) :
    # Ensure measurement data name is type string
    sensor_data_stream_id = str(sensor_data_stream_id)
    # Generate Queries for Dorm Room Power Data; only last 2 points will be used
    dorm_room_power_query = influxdb_query_builder_DR_Power_W(sensor_data_stream_id)
    # print(dorm_room_power_query)   # Debugging print statement

    query_str = str(dorm_room_power_query)  # convert query to type string
    previous_entries = influxdb_client.query(query_str)  # Query last DB entry with same type of measurement name
    previous_points = previous_entries.get_points()  # Convert to points

    dict_of_data = { }  # Initialize dictionary

    for previous_point in previous_points :  # Iterate through points

        previous_timepoint_pd = pd.to_datetime(previous_point['time'])  # Convert Timestamp to pandas timestamp object
        # print(previous_timepoint_pd)  # Debugging print statement

        previous_value = previous_point['POWER_VALUE']  # retrieves value
        previous_value_float = float(previous_value)  # convert to type float
        # print(previous_value_float)  # Debugging print statement

        dict_of_data[previous_timepoint_pd] = previous_value_float  # Place timepoint: value in dictionary
    # print(dict_of_data)  # Debugging print statement
    return dict_of_data


# Debugging function
# print(query_last_2_values_DR_Power_InfluxDB('ESP32_POWER_SENSOR: AC:67:B2:05:39:88')) # Debugging print statement


# Function to calculate kiloWatts per hour from Dorm Room Sensors
def write_DR_energy_to_InfluxDB(measurement_name) :
    # Ensure measurement data name is type string
    sensor_data_stream_id = str(measurement_name)
    dict_of_data_dt_W = { }  # Initialize dictionary

    dict_of_data_dt_W = query_last_2_values_DR_Power_InfluxDB(sensor_data_stream_id)  # Returns a dictionary of timestamp and kW values
    # print(dict_of_data_dt_W)  # Debugging print statement

    list_of_times = []  # Initialize list of timestamps
    list_of_values = []  # Initialize list of values

    # Iterate through dictionary of timestamp and values and append time and value in list_of_time and list_of_values
    for key , value in dict_of_data_dt_W.items() :
        list_of_times.append(key)
        list_of_values.append(value)

    # print(list_of_times)  # Debugging print statement
    # print(list_of_values)  # Debugging print statement

    # Gets the time values
    last_timepoint = list_of_times[0]
    first_timepoint = list_of_times[1]

    # Calculates time elapsed
    time_difference = last_timepoint - first_timepoint
    # print(time_difference)    # Debugging print statement
    # print((time_difference).seconds)  # Debugging print statement

    # Check to perform energy calculations ONLY if difference between time is less than that specified (180 seconds or 3 minutes)
    # This allows calculations to ignore large gaps which could be caused by unplugging power monitoring devices

    if ((time_difference).seconds) <= 180 :
        # Calculates time elapsed in unit hours
        time_difference_hr = (time_difference).seconds / 3600.0  # finding time difference in unit hour;  # Unit hour
        # print(time_difference_hr)  # Unit hour   # Debugging print statement

        # Gets the values of W from Power sensors and convert to kW
        last_value_W = list_of_values[0]
        last_value_kW = (float(last_value_W / 1000))
        first_value_W = list_of_values[1]
        first_value_kW = (float(first_value_W / 1000))

        # Calculates average from the last two power values
        average_power_dr_sensor_kW = float((last_value_kW + first_value_kW) / 2)
        average_power_dr_sensor_kW = round(float(average_power_dr_sensor_kW) , 4)

        # Finds kW per hour
        # Energy is simply power times time. For instance, the most common unit of energy in the US is the kilowatt hour, or kWh.
        # One kWh is equal to using 1000 watts, or 1 kW continuously for one hour. As such, a kWh is born.
        kW_per_hour = average_power_dr_sensor_kW * time_difference_hr
        # print(kW_per_hour)

        # Puts data in json body for writing to InfluxDB
        json_body = [
            {
                'measurement' : sensor_data_stream_id ,
                'tags' : {
                    'source_of_data' : "ESP32_sensors" ,
                    'units' : 'kW_per_hour' ,
                } ,
                "time" : last_timepoint ,
                'fields' : {
                    'value' : kW_per_hour ,
                }
            }
        ]

        # Write data to InfluxDB
        influxdb_client_DR_Energy.write_points(json_body)
        # print("kiloWatts per hour from Dorm Room Sensors")  # Debugging print statement
        # print(json_body)  # Debugging print statement
        return ("passed")

    else:
        return ("failed")


# Debugging function
# print(write_DR_energy_to_InfluxDB("ESP32_POWER_SENSOR: 7C:9E:BD:D7:4D:44"))  # Debugging print statement

# Initialize databases
_init_influxdb_database()
