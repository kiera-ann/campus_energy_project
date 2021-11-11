'''Module to Calculate Energy CO2 for all Campus Buildings. Write data into InfluxDB. '''

import time
from influxdb import InfluxDBClient
from datetime import datetime
import sys
import pandas as pd

# For PU Campus Building database
INFLUXDB_ADDRESS = '140.180.133.81'  # Personal development Mac mini IP address
INFLUXDB_USER = 'admin'
INFLUXDB_PASSWORD = 'admin'
INFLUXDB_DATABASE = 'pu_arcgis_energy_database_raw'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD , None)

# For PU Campus Total Energy Data
INFLUXDB_DATABASE_total_campus = 'pu_energy_database_raw'

influxdb_client_campus = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD ,
                                        database=INFLUXDB_DATABASE_total_campus)

# For PU Campus Total CO2 Data
INFLUXDB_DATABASE_total_campus_CO2 = 'pu_co2_database_raw'

influxdb_client_energy_CO2 = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD ,
                                            database=INFLUXDB_DATABASE_total_campus_CO2)

# For PU Campus Building Energy CO2 - Writing final building Energy CO2 to this database
INFLUXDB_DATABASE_Building_Energy_CO2 = 'pu_arcgis_energy_co2_database_raw'

influxdb_client_building_energy_CO2 = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD ,
                                            database=INFLUXDB_DATABASE_Building_Energy_CO2)


# Initialize database
def _init_influxdb_database() :
    databases = influxdb_client.get_list_database()  # check if the database is there by using the get_list_database() function of the client:
    if len(list(filter(lambda x : x['name'] == INFLUXDB_DATABASE , databases))) == 0 :
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)  # we’ll set the client to use this database


# Build query for database query of last 1 point for power from Princeton Building Data
def influxdb_query_builder_building_energy_kWh(PU_R25_NAME) :
    # Set data_field provided to function to variable "data_field_label_str"
    data_field_label_str = str(PU_R25_NAME)
    query_p1 = 'SELECT "value" FROM "pu_arcgis_energy_database_raw"."autogen".'
    query_p2 = '"'
    query_p3 = data_field_label_str
    query_p4 = '"'
    query_p5 = " WHERE time > now() - 12h ORDER BY time DESC LIMIT 1"

    # Concatenate string
    full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)

    # print(full_query_string)    # Debugging print statement
    return full_query_string


# # Debugging function
# print(influxdb_query_builder_building_energy_kWh('Nassau Hall'))  # Debugging print statement


# Function to query building energy database and return a dictionary with query data
def query_database_building(PU_R25_NAME) :
    # Function to generate a list of queries to be made to the database and store list in variable "list_of_queries"
    building_energy_query = influxdb_query_builder_building_energy_kWh(PU_R25_NAME)
    # print(building_energy_query)    # Debugging print statement

    query_str = str(building_energy_query)  # convert query to type string
    previous_entries = influxdb_client.query(query_str)  # Query last DB entry with same type of measurement name
    previous_points = previous_entries.get_points()  # Convert to points

    dict_of_data = { }  # Initialize dictionary

    for previous_point in previous_points :  # Iterate through points

        previous_timepoint_pd = pd.to_datetime(previous_point['time'])  # Convert Timestamp to pandas timestamp object
        # print(previous_timepoint_pd)  # Debugging print statement

        previous_value = previous_point['value']  # retrieves value
        previous_value_float = float(previous_value)  # convert to type float
        # print(previous_value_float)  # Debugging print statement

        dict_of_data[previous_timepoint_pd] = previous_value_float  # Place timepoint: value in dictionary
    # print(dict_of_data)  # Debugging print statement

    return dict_of_data


# # Debugging function
# print(query_database_building('Nassau Hall'))  # Debugging print statement


# Build query for database query of last 1 point for power from Princeton Total Campus Data
def influxdb_query_builder_campus_energy_kWh() :
    # Set data_field provided to function to variable "data_field_label_str"
    data_field_label_str = str("PU Energy Data: Total")
    query_p1 = 'SELECT "value" FROM "pu_energy_database_raw"."autogen".'
    query_p2 = '"'
    query_p3 = data_field_label_str
    query_p4 = '"'
    query_p5 = " WHERE time > now() - 12h ORDER BY time DESC LIMIT 1"

    # Concatenate string
    full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)

    # print(full_query_string)    # Debugging print statement
    return full_query_string


# # Debugging function
# print(influxdb_query_builder_campus_energy_kWh())  # Debugging print statement


# Function to query Total Campus energy database and return a dictionary with query data
def query_database_campus() :
    # Function to generate a list of queries to be made to the database and store list in variable "list_of_queries"
    total_campus_energy_query = influxdb_query_builder_campus_energy_kWh()
    # print(total_campus_energy_query)    # Debugging print statement

    query_str = str(total_campus_energy_query)  # convert query to type string
    previous_entries = influxdb_client.query(query_str)  # Query last DB entry with same type of measurement name
    previous_points = previous_entries.get_points()  # Convert to points

    dict_of_data = { }  # Initialize dictionary

    for previous_point in previous_points :  # Iterate through points

        previous_timepoint_pd = pd.to_datetime(previous_point['time'])  # Convert Timestamp to pandas timestamp object
        # print(previous_timepoint_pd)  # Debugging print statement

        previous_value = previous_point['value']  # retrieves value
        previous_value_float = float(previous_value)  # convert to type float
        # print(previous_value_float)  # Debugging print statement

        dict_of_data[previous_timepoint_pd] = previous_value_float  # Place timepoint: value in dictionary
    # print(dict_of_data)  # Debugging print statement

    return dict_of_data


# # Debugging function
# print(query_database_campus())  # Debugging print statement


# Build query for database query of last 1 point for Princeton Total Campus Energy CO2 Data
def influxdb_query_builder_campus_energy_co2() :
    # Set data_field provided to function to variable "data_field_label_str"
    data_field_label_str = str("PU CO2 Data: Energy")
    query_p1 = 'SELECT "value" FROM "pu_co2_database_raw"."autogen".'
    query_p2 = '"'
    query_p3 = data_field_label_str
    query_p4 = '"'
    query_p5 = " WHERE time > now() - 12h ORDER BY time DESC LIMIT 1"

    # Concatenate string
    full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)

    # print(full_query_string)    # Debugging print statement
    return full_query_string


# # Debugging function
# print(influxdb_query_builder_campus_energy_co2())  # Debugging print statement


# Function to query Princeton Total Campus Energy CO2 Data from database and return a dictionary with query data
def query_database_campus_energy_co2() :
    # Function to generate a list of queries to be made to the database and store list in variable "list_of_queries"
    building_energy_co2_query = influxdb_query_builder_campus_energy_co2()
    # print(building_energy_co2_query)    # Debugging print statement

    query_str = str(building_energy_co2_query)  # convert query to type string
    previous_entries = influxdb_client.query(query_str)  # Query last DB entry with same type of measurement name
    previous_points = previous_entries.get_points()  # Convert to points

    dict_of_data = { }  # Initialize dictionary

    for previous_point in previous_points :  # Iterate through points

        previous_timepoint_pd = pd.to_datetime(previous_point['time'])  # Convert Timestamp to pandas timestamp object
        # print(previous_timepoint_pd)  # Debugging print statement

        previous_value = previous_point['value']  # retrieves value
        previous_value_float = float(previous_value)  # convert to type float
        # print(previous_value_float)  # Debugging print statement

        dict_of_data[previous_timepoint_pd] = previous_value_float  # Place timepoint: value in dictionary
    # print(dict_of_data)  # Debugging print statement

    return dict_of_data


# # Debugging function
# print(query_database_campus_energy_co2())  # Debugging print statement


# Function to calculate most recent tally of Energy CO2 for each Princeton's Campus Building and write data to InfluxDB
def write_recent_building_energy_co2_to_InfluxDB(PU_R25_NAME) :
    building_name = str(PU_R25_NAME)
    # List of times to eventually use latest time stamp
    list_of_times = []  # Initialize list
    # Building Energy Data
    building_energy_data_dict = query_database_building(PU_R25_NAME)  # returns a dictionary with query data

    # For loop to get timestamp and values and append time and value in list_of_time and list_of_values
    for key , value in building_energy_data_dict.items() :
        building_energy_time = key
        building_energy_value = float(value)

    # print(building_energy_time)  # Debugging print statement
    # print(building_energy_value)  # Debugging print statement

    # Adds time stamp to list_of_times for finding latest timestamp
    list_of_times.append(building_energy_time)

    # Total Campus Energy Data
    total_campus_energy_dict = query_database_campus()  # returns a dictionary with query data

    # For loop to get timestamp and values and append time and value in list_of_time and list_of_values
    for key , value in total_campus_energy_dict.items() :
        total_campus_energy_time = key
        total_campus_energy_value = float(value)

    # print(total_campus_energy_time)  # Debugging print statement
    # print(total_campus_energy_value)  # Debugging print statement

    # Adds time stamp to list_of_times for finding latest timestamp
    list_of_times.append(total_campus_energy_time)

    # Total Campus Energy CO2 Data
    total_campus_energy_co2_dict = query_database_campus_energy_co2()  # returns a dictionary with query data

    # For loop to get timestamp and values and append time and value in list_of_time and list_of_values
    for key , value in total_campus_energy_co2_dict.items() :
        total_campus_energy_co2_time = key
        total_campus_energy_co2_value = float(value)

    # print(total_campus_energy_co2_time)  # Debugging print statement
    # print(total_campus_energy_co2_value)  # Debugging print statement

    # Adds time stamp to list_of_times for finding latest timestamp
    list_of_times.append(total_campus_energy_co2_time)

    # print(list_of_times)  # Debugging print statement

    # Date times are comparable; so you can use max(datetimes_list) and min(datetimes_list)
    # Source: https://stackoverflow.com/questions/3922644/find-oldest-youngest-datetime-object-in-a-list
    latest_timestamp = max(list_of_times)
    # print(latest_timestamp)  # Debugging print statement

    # Formula for Calculating building level energy CO2
    # (Building Energy/Campus Total Energy) * Campus Energy CO2
    building_energy_co2 = float((building_energy_value / total_campus_energy_value) * total_campus_energy_co2_value)
    building_energy_co2 = round(building_energy_co2 , 3)

    # print(building_energy_co2)  # Debugging print statement

    # Puts data in json body for writing to InfluxDB
    json_body = [
        {
            'measurement' : building_name ,
            'tags' : {
                'source_of_data' : "icetec_tigerenergy_api" ,
                'units' : 'Pounds CO2'
            } ,
            "time" : latest_timestamp ,
            # "time" : "2020-09-30T17:00:00Z" ,
            'fields' : {
                'value' : building_energy_co2 ,
            }
        }
    ]

    # Write data to InfluxDB
    influxdb_client_building_energy_CO2.write_points(json_body)
    # print(building_name + " Energy CO2")  # Debugging print statement
    # print(json_body) # Debugging print statement


# Debugging function
# print(write_recent_building_energy_co2_to_InfluxDB('Nassau Hall'))  # Debugging print statement

# Initialize databases
_init_influxdb_database()
