''' Function to calculate Pounds of Steam produced in Princeton's Cogen Facility: EP.Totals.Steam.i.Production_pph. Adds the data to InfluxDB. '''
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


# Build query for database query of last 2 points of Pounds per hour Steam produced at Princeton's Cogen Facility
# Icetec parameter: "EP.Totals.Steam.i.Production_pph"
def influxdb_query_builder_cogen_total_steam_pph() :
    # Set data_field provided to function to variable "data_field_label_str"
    data_field_label_str = str("EP.Totals.Steam.i.Production_pph")
    query_p1 = 'SELECT "value" FROM "pu_icetec_database_raw"."autogen".'
    query_p2 = '"'
    query_p3 = data_field_label_str
    query_p4 = '"'
    query_p5 = " WHERE time > now() - 12h ORDER BY time DESC LIMIT 2"
    full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)  # Concatenate string
    return full_query_string


# Function to query last 2 values
def query_last_2_values_cogen_total_steam_InfluxDB() :
    # Generate Queries for Cogen Turbine data; only last 2 points will be used
    cogen_total_steam_query = influxdb_query_builder_cogen_total_steam_pph()
    query_str = str(cogen_total_steam_query)  # convert query to type string
    previous_entries = influxdb_client.query(query_str)  # Query last DB entry with same type of measurement name
    previous_points = previous_entries.get_points()  # Convert to points
    dict_of_data = { }  # Initialize dictionary

    for previous_point in previous_points :  # Iterate through points
        previous_timepoint_pd = pd.to_datetime(previous_point['time'])  # Convert Timestamp to pandas timestamp object
        previous_value = previous_point['value']  # retrieves value
        previous_value_float = float(previous_value)  # convert to type float
        dict_of_data[previous_timepoint_pd] = previous_value_float  # Place timepoint: value in dictionary
    return dict_of_data


# Function to calculate Pounds of steam from Princeton Cogen Facility; Icetec parameter: "EP.Totals.Steam.i.Production_pph"
def write_cogen_total_steam_to_InfluxDB() :
    dict_of_data_dt_pph = { }  # Initialize dictionary

    # Returns a dictionary of timestamp and pph values from "EP.Totals.Steam.i.Production_pph"
    dict_of_data_dt_pph = query_last_2_values_cogen_total_steam_InfluxDB()
    list_of_times = []  # Initialize list of timestamps
    list_of_values = []  # Initialize list of values

    # Iterate through dictionary of timestamp and values and append time and value in list_of_time and list_of_values
    for key , value in dict_of_data_dt_pph.items() :
        list_of_times.append(key)
        list_of_values.append(value)

    # Gets the time values
    last_timepoint = list_of_times[0]
    first_timepoint = list_of_times[1]

    # Calculates time elapsed
    time_difference = last_timepoint - first_timepoint

    # Calculates time elapsed in unit hours
    time_difference_hr = (time_difference).seconds / 3600.0  # finding time difference in unit hour;  # Unit hour

    # Gets the values of kW from EP.Cogen.Turbine.Power.ION.Total_kW
    last_value_pph = list_of_values[0]
    first_value_pph = list_of_values[1]

    # Calculates average from the last two steam pph values
    average_cogen_total_steam_pph = float((last_value_pph + first_value_pph) / 2)
    average_cogen_total_steam_pph = round(float(average_cogen_total_steam_pph) , 4)

    # Finds Pounds of Steam produced in that interval of time_difference_hr
    pounds_steam_produced = average_cogen_total_steam_pph * time_difference_hr

    # Puts data in json body for writing to InfluxDB
    json_body = [
        {
            'measurement' : "PU Steam Data: Total Production" ,
            'tags' : {
                'source_of_data' : "icetec_tigerenergy_api" ,
                'units' : 'Pounds'
            } ,
            "time" : last_timepoint ,
            'fields' : {
                'value' : pounds_steam_produced ,
            }
        }
    ]

    # Write data to InfluxDB
    influxdb_client_PU_Energy.write_points(json_body)


# Initialize databases
_init_influxdb_database()
