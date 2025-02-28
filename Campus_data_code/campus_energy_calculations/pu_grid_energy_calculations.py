# encoding=utf8

''' Function to calculate kiloWatts per hour from Princeton Grid import use : EP.Totals.Power.i.Import_kW '''

import pandas as pd
from influxdb import InfluxDBClient

INFLUXDB_ADDRESS = '140.180.133.81'  # Personal development Mac mini IP address
INFLUXDB_USER = 'admin'
INFLUXDB_PASSWORD = 'admin'
INFLUXDB_DATABASE = 'pu_icetec_database_raw'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD , None)

# For PU Energy database
INFLUXDB_USER_PU_Energy = 'admin'
INFLUXDB_PASSWORD_PU_Energy = 'admin'
INFLUXDB_DATABASE_PU_Energy = 'pu_energy_database_raw'

influxdb_client_PU_Energy = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER_PU_Energy , INFLUXDB_PASSWORD_PU_Energy ,
                                           database=INFLUXDB_DATABASE_PU_Energy)


# Initialize databases
def _init_influxdb_database() :
    databases = influxdb_client.get_list_database()  # check if the database is there by using the get_list_database() function of the client:
    if len(list(filter(lambda x : x['name'] == INFLUXDB_DATABASE , databases))) == 0 :
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)  # we’ll set the client to use this database


# Build query for database query of last 2 points for power from PSEG grid; Icetec parameter: "EP.Totals.Power.i.Import_kW"
def influxdb_query_builder_power_import() :
    # Set data_field provided to function to variable "data_field_label_str"
    data_field_label_str = str("EP.Totals.Power.i.Import_kW")
    query_p1 = 'SELECT "value" FROM "pu_icetec_database_raw"."autogen".'
    query_p2 = '"'
    query_p3 = data_field_label_str
    query_p4 = '"'
    query_p5 = " WHERE time > now() - 12h ORDER BY time DESC LIMIT 2"
    full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)   # Concatenate string
    return full_query_string


# Function to query last 2 values
def query_last_2_values_power_import_InfluxDB() :
    # Generate Queries for Power Import data; only last 2 points will be used
    power_import_query = influxdb_query_builder_power_import()
    query_str = str(power_import_query)  # convert query to type string
    previous_entries = influxdb_client.query(query_str)  # Query last DB entry with same type of measurement name
    previous_points = previous_entries.get_points()  # Convert to points
    dict_of_data = { }  # Initialize dictionary

    for previous_point in previous_points :  # Iterate through points
        previous_timepoint_pd = pd.to_datetime(previous_point['time'])  # Convert Timestamp to pandas timestamp object
        previous_value = previous_point['value']  # retrieves value
        previous_value_float = float(previous_value)  # convert to type float
        dict_of_data[previous_timepoint_pd] = previous_value_float  # Place timepoint: value in dictionary
    return dict_of_data


# Function to calculate kiloWatts per hour from Princeton Grid import and write to InfluxDB: EP.Totals.Power.i.Import_kW
def write_campus_grid_energy_to_influxDB() :
    dict_of_data_dt_kW = { }  # Initialize dictionary
    dict_of_data_dt_kW = query_last_2_values_power_import_InfluxDB()  # Returns a dictionary of timestamp and kW values from EP.Totals.Power.i.Import_kW
    list_of_times = []  # Initialize list of timestamps
    list_of_values = []  # Initialize list of values

    # Iterate through dictionary of timestamp and values and append time and value in list_of_time and list_of_values
    for key , value in dict_of_data_dt_kW.items() :
        list_of_times.append(key)
        list_of_values.append(value)

    # Gets the time values
    last_timepoint = list_of_times[0]
    first_timepoint = list_of_times[1]

    # Calculates time elapsed
    time_difference = last_timepoint - first_timepoint

    # Calculates time elapsed in unit hours
    time_difference_hr = (time_difference).seconds / 3600.0  # finding time difference in unit hour;  # Unit hour

    # Gets the values of kW from EP.Totals.Power.i.Import_kW
    last_value_kW = list_of_values[0]
    first_value_kW = list_of_values[1]

    # Calculates average from the last two power values
    average_power_draw_pjm_kW = float((last_value_kW + first_value_kW) / 2)
    average_power_draw_pjm_kW = round(float(average_power_draw_pjm_kW) , 4)

    # Finds kW per hour
    # Energy is simply power times time. For instance, the most common unit of energy in the US is the kilowatt hour, or kWh.
    # One kWh is equal to using 1000 watts, or 1 kW continuously for one hour. As such, a kWh is born.
    kW_per_hour = average_power_draw_pjm_kW * time_difference_hr

    # Puts data in json body for writing to InfluxDB
    json_body = [
        {
            'measurement' : "PU Energy Data: Grid" ,
            'tags' : {
                'source_of_data' : "icetec_tigerenergy_api" ,
                'units' : 'kW_per_hour'
            } ,
            "time" : last_timepoint ,
            'fields' : {
                'value' : kW_per_hour ,
            }
        }
    ]

    # Write data to InfluxDB
    influxdb_client_PU_Energy.write_points(json_body)


# Initialize databases
_init_influxdb_database()
