'''Module to Calculate Pounds of Steam for all Campus Buildings. Write data into InfluxDB. '''

import time
from influxdb import InfluxDBClient
from datetime import datetime
import sys
import pandas as pd

# For PU Campus Building database
INFLUXDB_ADDRESS = '140.180.133.81'  # Personal development Mac mini IP address
INFLUXDB_USER = 'admin'
INFLUXDB_PASSWORD = 'admin'
INFLUXDB_DATABASE = 'pu_arcgis_database_raw'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD , None)

# For PU Campus Building Heat
INFLUXDB_ADDRESS = '140.180.133.81'  # Personal development Mac mini IP address
INFLUXDB_USER_general = 'admin'
INFLUXDB_PASSWORD_general = 'admin'
INFLUXDB_DATABASE_Building_Heat = 'pu_arcgis_heat_database_raw'


influxdb_client_building_heat = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER_general , INFLUXDB_PASSWORD_general ,
                                                 database=INFLUXDB_DATABASE_Building_Heat)


# Initialize database
def _init_influxdb_database() :
    databases = influxdb_client.get_list_database()  # check if the database is there by using the get_list_database() function of the client:
    if len(list(filter(lambda x : x['name'] == INFLUXDB_DATABASE , databases))) == 0 :
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)  # we’ll set the client to use this database


# Build query for database query of last 2 points for steam from Princeton Building Data
def influxdb_query_builder_building_steam_pph(PU_R25_NAME) :
    # Set data_field provided to function to variable "data_field_label_str"
    data_field_label_str = str(PU_R25_NAME)
    query_p1 = 'SELECT "STEAM" FROM "pu_arcgis_database_raw"."autogen".'
    query_p2 = '"'
    query_p3 = data_field_label_str
    query_p4 = '"'
    query_p5 = " WHERE time > now() - 12h ORDER BY time DESC LIMIT 2"

    # Concatenate string
    full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)

    # print(full_query_string)    # Debugging print statement
    return full_query_string


# Debugging function
# print(influxdb_query_builder_building_steam_pph('Nassau Hall')) # Debugging print statement

# Function to query last 2 values
def query_last_2_values_building_steam_InfluxDB(PU_R25_NAME) :
    # Generate Queries for Steam from Princeton Building Data
    building_steam_query = influxdb_query_builder_building_steam_pph(PU_R25_NAME)
    # print(building_steam_query)   # Debugging print statement

    query_str = str(building_steam_query)  # convert query to type string
    previous_entries = influxdb_client.query(query_str)  # Query last DB entry with same type of measurement name
    previous_points = previous_entries.get_points()  # Convert to points

    dict_of_data = { }  # Initialize dictionary

    for previous_point in previous_points :  # Iterate through points

        previous_timepoint_pd = pd.to_datetime(previous_point['time'])  # Convert Timestamp to pandas timestamp object
        # print(previous_timepoint_pd)  # Debugging print statement

        previous_value = previous_point['STEAM']  # retrieves value
        previous_value_float = float(previous_value)  # convert to type float
        # print(previous_value_float)  # Debugging print statement

        dict_of_data[previous_timepoint_pd] = previous_value_float  # Place timepoint: value in dictionary
    # print(dict_of_data)  # Debugging print statement
    return dict_of_data


# Debugging function
# print(query_last_2_values_building_steam_InfluxDB('Nassau Hall')) # Debugging print statement


# Function to calculate Steam in pounds from Princeton Building Data; Write data to InfluxDB
def write_campus_building_steam_to_InfluxDB(PU_R25_NAME) :
    building_name = str(PU_R25_NAME)
    dict_of_data_dt_pph = { }  # Initialize dictionary

    # Returns a dictionary of timestamp and pph values
    dict_of_data_dt_pph = query_last_2_values_building_steam_InfluxDB(PU_R25_NAME)
    # print(dict_of_data_dt_pph)  # Debugging print statement

    list_of_times = []  # Initialize list of timestamps
    list_of_values = []  # Initialize list of values

    # Iterate through dictionary of timestamp and values and append time and value in list_of_time and list_of_values
    for key , value in dict_of_data_dt_pph.items() :
        list_of_times.append(key)
        list_of_values.append(value)

    # print(list_of_times)   # Debugging print statement
    # print(list_of_values)   # Debugging print statement

    # Gets the time values
    last_timepoint = list_of_times[0]
    first_timepoint = list_of_times[1]

    # Calculates time elapsed
    time_difference = last_timepoint - first_timepoint

    # Calculates time elapsed in unit hours
    time_difference_hr = (time_difference).seconds / 3600.0  # finding time difference in unit hour;  # Unit hour
    # print(time_difference_hr)  # Unit hour   # Debugging print statement

    # Gets the values of pph from Building Data
    last_value_pph = list_of_values[0]
    first_value_pph = list_of_values[1]

    # Calculates average from the last two steam values
    average_building_steam_pph = float((last_value_pph + first_value_pph) / 2)
    average_building_steam_pph = round(float(average_building_steam_pph) , 4)

    # Finds Pounds of Steam
    # For my calculations, I am calculating pounds per hour steam by the time in unit hour to obtain pounds of steam for the building
    building_steam_pounds = average_building_steam_pph * time_difference_hr
    building_steam_pounds = round(float(building_steam_pounds) , 4)
    # print(building_steam_pounds)

    # Puts data in json body for writing to InfluxDB
    json_body = [
        {
            'measurement' : building_name ,
            'tags' : {
                'source_of_data' : "PU_ArcGIS_REST_Services_API" ,
                'units' : 'Pounds' ,
            } ,
            "time" : last_timepoint ,
            # "time" : "2020-09-30T17:00:00Z" ,
            'fields' : {
                'value' : building_steam_pounds ,
            }
        }
    ]

    # Write data to InfluxDB
    influxdb_client_building_heat.write_points(json_body)
    # print(json_body)  # Debugging print statement


# Debugging function
# print(write_campus_building_steam_to_InfluxDB('Nassau Hall'))  # Debugging print statement

# Initialize databases
_init_influxdb_database()
