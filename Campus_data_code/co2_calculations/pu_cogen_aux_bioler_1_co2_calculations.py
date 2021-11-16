''' Function to calculate CO2 produced from Princeton Cogen Auxiliary Boiler # 1: EP.BLRS.01.i.GasFlow_dthr. Writes to InfluxDB '''

import pandas as pd
from influxdb import InfluxDBClient

# For ICETEC database
INFLUXDB_ADDRESS = '140.180.133.81'  # Personal development Mac mini IP address
INFLUXDB_USER = 'admin'
INFLUXDB_PASSWORD = 'admin'
INFLUXDB_DATABASE = 'pu_icetec_database_raw'

# For PU CO2 database
INFLUXDB_USER_PU_CO2 = 'admin'
INFLUXDB_PASSWORD_PU_CO2 = 'admin'
INFLUXDB_DATABASE_PU_CO2 = 'pu_co2_database_raw'

# For ICETEC database
influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD , None)

# For PU CO2 database
influxdb_client_PU_CO2 = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER_PU_CO2 , INFLUXDB_PASSWORD_PU_CO2 ,
                                        database=INFLUXDB_DATABASE_PU_CO2)


# Function to initialize database
def _init_influxdb_database() :
    databases = influxdb_client.get_list_database()  # check if the database is there by using the get_list_database() function of the client:
    if len(list(filter(lambda x : x['name'] == INFLUXDB_DATABASE , databases))) == 0 :
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)  # we’ll set the client to use this database


# Build query for database query of last 2 points for different Icetec paramaters
# This is for CO2 related calculations
def influxdb_query_builder_aux_bioler_1_calc() :
    # Set data_field provided to function to variable "data_field_label_str"
    data_field_label_str = str("EP.BLRS.01.i.GasFlow_dthr")
    query_p1 = 'SELECT "value" FROM "pu_icetec_database_raw"."autogen".'
    query_p2 = '"'
    query_p3 = data_field_label_str
    query_p4 = '"'
    query_p5 = " WHERE time > now() - 12h ORDER BY time DESC LIMIT 2"
    full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)  # Concatenate string
    return full_query_string


# Function to query last 2 values
def query_last_2_values_aux_bioler_1_dthr_InfluxDB() :
    # Generate Queries for Cogen auxiliary bioler # 1 dthr data; only last 2 points will be used
    cogen_aux_bioler_1_dthr_query = influxdb_query_builder_aux_bioler_1_calc()
    query_str = str(cogen_aux_bioler_1_dthr_query)  # convert query to type string
    previous_entries = influxdb_client.query(query_str)  # Query last DB entry with same type of measurement name
    previous_points = previous_entries.get_points()  # Convert to points
    dict_of_data = { }  # Initialize dictionary

    for previous_point in previous_points :  # Iterate through points
        previous_timepoint_pd = pd.to_datetime(previous_point['time'])  # Convert Timestamp to pandas timestamp object
        previous_value = previous_point['value']  # retrieves value
        previous_value_float = float(previous_value)  # convert to type float
        dict_of_data[previous_timepoint_pd] = previous_value_float  # Place timepoint: value in dictionary
    return dict_of_data


# Function to write CO2 data from Auxiliary Bioler #1 to InfluxDB
def write_pu_cogen_aux_bioler_1_co2_to_InfluxDB() :
    # DTHR is shorthand for dekatherms per hour
    dict_of_dthr_data = { }  # Initialize dictionary
    dict_of_dthr_data = query_last_2_values_aux_bioler_1_dthr_InfluxDB()  # Returns a dictionary of timestamp and values
    list_of_times = []  # Initialize list of timestamps
    list_of_values = []  # Initialize list of values

    # Iterate through dictionary of timestamp and values and append time and value in list_of_time and list_of_values
    for key , value in dict_of_dthr_data.items() :
        list_of_times.append(key)
        list_of_values.append(value)

    # Gets the time values
    last_timepoint = list_of_times[0]
    first_timepoint = list_of_times[1]

    # Calculates time elapsed
    time_difference = last_timepoint - first_timepoint

    # Calculates time elapsed in unit hours
    time_difference_hr = (time_difference).seconds / 3600.0  # finding time difference in unit hour;  # Unit hour

    # Gets the values of dthr
    last_value_dthr = list_of_values[0]
    first_value_dthr = list_of_values[1]

    # Calculate the average dthr value
    average_value_dthr = float((last_value_dthr + first_value_dthr) / 2)  # Finds the average; unit is DTHR which is shorthand for dekatherms per hour
    average_value_dthr = round(float(average_value_dthr) , 2)  # unit DTHR which is shorthand for dekatherms per hour

    # Now calculate the actual decatherms used in the time that had elapsed: decatherms per hour * time in unit hour
    amount_decatherms = float(time_difference_hr * average_value_dthr)
    amount_decatherms = round(float(amount_decatherms) , 3)  # Unit decatherms

    # One dekatherm is equal to 10 therms or one million British thermal units (Btu) or 1.055 GJ
    amount_nat_gas_btu = amount_decatherms * 1000000  # Unit Btu

    # EIA states that Natural Gas emits 117.0 pounds CO2 per million British thermal units (Btu) of energy
    # Source: https://www.eia.gov/tools/faqs/faq.php?id=73&t=11
    cogen_total_aux_bioler_1_pounds_co2 = float((amount_nat_gas_btu / 1000000) * 117)
    cogen_total_aux_bioler_1_pounds_co2 = round(float(cogen_total_aux_bioler_1_pounds_co2) , 3)  # Unit pounds CO2

    # Puts data in json body for writing to InfluxDB
    json_body = [
        {
            'measurement' : "PU Heating: Auxiliary Bioler # 1" ,
            'tags' : {
                'source_of_data' : "personal:icetec,tigerenergy" ,
                'units' : 'Pounds CO2'
            } ,
            "time" : last_timepoint ,
            'fields' : {
                'value' : cogen_total_aux_bioler_1_pounds_co2 ,
            }
        }
    ]

    # Write data to InfluxDB
    influxdb_client_PU_CO2.write_points(json_body)


# Initialize databases
_init_influxdb_database()
