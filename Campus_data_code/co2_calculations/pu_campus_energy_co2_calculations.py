''' Function to calculate most recent total pounds of CO2 for Princeton's Campus Energy and store data in InfluxDB. '''
import pandas as pd

# Import InfluxDB Module
from influxdb import InfluxDBClient

# For PU Energy CO2 database
INFLUXDB_ADDRESS = '140.180.133.81'  # Personal development Mac mini IP address
INFLUXDB_USER = 'admin'
INFLUXDB_PASSWORD = 'admin'
INFLUXDB_DATABASE = 'pu_co2_database_raw'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD ,
                                 database=INFLUXDB_DATABASE)

# List of measurements of relevance to Campus CO2 for Energy
measurement_names_for_energy_co2 = ["PU Electricity Turbine CO2" , "PU CO2: Grid"]


# Initialize databases
def _init_influxdb_database() :
    databases = influxdb_client.get_list_database()  # check if the database is there by using the get_list_database() function of the client:
    if len(list(filter(lambda x : x['name'] == INFLUXDB_DATABASE , databases))) == 0 :
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)  # we’ll set the client to use this database


# Build query for database query of last 1 point for CO2 from Princeton
def influxdb_query_builder_energy_co2_lbs(meaurement_name) :
    # Set data_field provided to function to variable "data_field_label_str"
    data_field_label_str = str(meaurement_name)
    query_p1 = 'SELECT "value" FROM "pu_co2_database_raw"."autogen".'
    query_p2 = '"'
    query_p3 = data_field_label_str
    query_p4 = '"'
    query_p5 = " WHERE time > now() - 12h ORDER BY time DESC LIMIT 1"
    full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)  # Concatenate string
    return full_query_string


# Function to generate a list of queries for total co2 data related to energy use
def generate_list_of_queries() :
    list_of_queries = []  # Initialize list
    for name in measurement_names_for_energy_co2 :
        list_of_queries.append(influxdb_query_builder_energy_co2_lbs(name))
    return list_of_queries


# Function to query database and return a list of dictionaries with query data
def query_database() :
    # Function to generate a list of queries to be made to the database and store list in variable "list_of_queries"
    list_of_queries = generate_list_of_queries()
    list_of_dict = []  # Initialize list
    count = 1  # Used to make unique dictionary variable names

    # Iterate through list of queries "list_of_queries"; Name or type of energy source is not recorded since it is not of value
    for query in list_of_queries :
        query_str = str(query)  # convert query to type string
        previous_entries = influxdb_client.query(query_str)  # Query last DB entry with same type of measurement name
        previous_points = previous_entries.get_points()  # Convert to points

        for previous_point in previous_points :  # Iterate through points
            previous_timepoint_pd = pd.to_datetime(previous_point['time'])  # Convert Timestamp to pandas timestamp object
            previous_value = previous_point['value']  # retrieves value
            previous_value_float = float(previous_value)  # convert to type float

            # Create unique dictionary names
            dictionary_name = "dict_of_data_" + str(count)
            dictionary_name = { }  # Initialize varibale as a dictionary
            dictionary_name[previous_timepoint_pd] = previous_value_float  # Place timepoint: value in dictionary
            count = count + 1  # Increment counter to create a new dictionary variable name on iterating for loop
            list_of_dict.append(dictionary_name)  # Append to list of dictionaries
    return list_of_dict


# Function to calculate most recent tally of Energy CO2 Princeton's Campus is responsible for and write data to InfluxDB
def write_recent_total_campus_energy_co2_to_InfluxDB() :
    list_of_dict = []  # Initialize list
    list_of_dict = query_database()  # returns a list of dictionaries with query data
    list_of_times = []  # Initialize list of timestamps
    list_of_values = []  # Initialize list of values

    for dictionary in list_of_dict :
        # Iterate through dictionary of timestamp and values and append time and value in list_of_time and list_of_values
        for key , value in dictionary.items() :
            list_of_times.append(key)
            list_of_values.append(float(value))

    # Finds sum using sum() function in Python
    # Source: https://www.geeksforgeeks.org/sum-function-python/
    sum_campus_energy_co2 = sum(list_of_values)
    sum_campus_energy_co2 = round(float(sum_campus_energy_co2) , 3)

    # Date times are comparable; so you can use max(datetimes_list) and min(datetimes_list)
    # Source: https://stackoverflow.com/questions/3922644/find-oldest-youngest-datetime-object-in-a-list
    # I will use the latest timestamp as the overall timestamp to apply to the data to be input into InfluxDB
    latest_timestamp = max(list_of_times)

    # Puts data in json body for writing to InfluxDB
    json_body = [
        {
            'measurement' : "PU CO2 Data: Energy" ,
            'tags' : {
                'source_of_data' : "icetec_tigerenergy_api" ,
                'units' : 'Pounds CO2'
            } ,
            "time" : latest_timestamp ,
            'fields' : {
                'value' : sum_campus_energy_co2 ,
            }
        }
    ]

    # Write data to InfluxDB
    influxdb_client.write_points(json_body)


# Initialize databases
_init_influxdb_database()
