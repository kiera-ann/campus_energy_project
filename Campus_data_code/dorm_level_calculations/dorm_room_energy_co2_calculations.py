'''Module to Calculate Dorm Room Level Energy CO2. Write data into InfluxDB. '''

from influxdb import InfluxDBClient
import pandas as pd

# For Dorm Room Energy Sensor  Data
INFLUXDB_ADDRESS = '140.180.133.81'  # Personal development Mac mini IP address
INFLUXDB_USER = 'admin'
INFLUXDB_PASSWORD = 'admin'
INFLUXDB_DATABASE = 'dormroom_energy_database_raw'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD , None)

# For PU Campus Total Energy Data
INFLUXDB_DATABASE_total_campus = 'pu_energy_database_raw'

influxdb_client_campus = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD ,
                                        database=INFLUXDB_DATABASE_total_campus)

# For PU Campus Total CO2 Data; will only use 'PU CO2 Data: Energy'
INFLUXDB_DATABASE_total_campus_CO2 = 'pu_co2_database_raw'

influxdb_client_energy_CO2 = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD ,
                                            database=INFLUXDB_DATABASE_total_campus_CO2)

# For Dorm Room (DR) Energy CO2 - Writing final Energy CO2 to this database
INFLUXDB_DATABASE_DR_Energy_CO2 = 'dormroom_energy_co2_database_raw'

influxdb_client_DR_energy_CO2 = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD ,
                                               database=INFLUXDB_DATABASE_DR_Energy_CO2)


# Initialize database
def _init_influxdb_database() :
    databases = influxdb_client.get_list_database()  # check if the database is there by using the get_list_database() function of the client:
    if len(list(filter(lambda x : x['name'] == INFLUXDB_DATABASE , databases))) == 0 :
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)  # we’ll set the client to use this database


# Build query for database query of last 1 point for power from Dorm Room (DR) Energy Sensor Data
def influxdb_query_builder_dr_energy_kWh(sensor_data_stream_id) :
    # Set data_field provided to function to variable "data_field_label_str"
    data_field_label_str = str(sensor_data_stream_id)
    query_p1 = 'SELECT "value" FROM "dormroom_energy_database_raw"."autogen".'
    query_p2 = '"'
    query_p3 = data_field_label_str
    query_p4 = '"'
    query_p5 = " WHERE time > now() - 12h ORDER BY time DESC LIMIT 1"
    full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)  # Concatenate string
    return full_query_string


# Function to query building energy database and return a dictionary with query data
def query_database_dr_energy(sensor_data_stream_id) :
    # Function to generate a list of queries to be made to the database and store list in variable "list_of_queries"
    dorm_room_energy_query = influxdb_query_builder_dr_energy_kWh(sensor_data_stream_id)
    query_str = str(dorm_room_energy_query)  # convert query to type string
    previous_entries = influxdb_client.query(query_str)  # Query last DB entry with same type of measurement name
    previous_points = previous_entries.get_points()  # Convert to points
    dict_of_data = { }  # Initialize dictionary

    for previous_point in previous_points :  # Iterate through points
        previous_timepoint_pd = pd.to_datetime(previous_point['time'])  # Convert Timestamp to pandas timestamp object
        previous_value = previous_point['value']  # retrieves value
        previous_value_float = float(previous_value)  # convert to type float
        dict_of_data[previous_timepoint_pd] = previous_value_float  # Place timepoint: value in dictionary
    return dict_of_data


# Build query for database query of last 1 point for power from Princeton Total Campus Data
def influxdb_query_builder_campus_energy_kWh() :
    # Set data_field provided to function to variable "data_field_label_str"
    data_field_label_str = str("PU Energy Data: Total")
    query_p1 = 'SELECT "value" FROM "pu_energy_database_raw"."autogen".'
    query_p2 = '"'
    query_p3 = data_field_label_str
    query_p4 = '"'
    query_p5 = " WHERE time > now() - 12h ORDER BY time DESC LIMIT 1"
    full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)  # Concatenate string
    return full_query_string


# Function to query Total Campus energy database and return a dictionary with query data
def query_database_campus() :
    # Function to generate a list of queries to be made to the database and store list in variable "list_of_queries"
    total_campus_energy_query = influxdb_query_builder_campus_energy_kWh()
    query_str = str(total_campus_energy_query)  # convert query to type string
    previous_entries = influxdb_client.query(query_str)  # Query last DB entry with same type of measurement name
    previous_points = previous_entries.get_points()  # Convert to points
    dict_of_data = { }  # Initialize dictionary

    for previous_point in previous_points :  # Iterate through points
        previous_timepoint_pd = pd.to_datetime(previous_point['time'])  # Convert Timestamp to pandas timestamp object
        previous_value = previous_point['value']  # retrieves value
        previous_value_float = float(previous_value)  # convert to type float
        dict_of_data[previous_timepoint_pd] = previous_value_float  # Place timepoint: value in dictionary
    return dict_of_data


# Build query for database query of last 1 point for Princeton Total Campus Energy CO2 Data
def influxdb_query_builder_campus_energy_co2() :
    # Set data_field provided to function to variable "data_field_label_str"
    data_field_label_str = str("PU CO2 Data: Energy")
    query_p1 = 'SELECT "value" FROM "pu_co2_database_raw"."autogen".'
    query_p2 = '"'
    query_p3 = data_field_label_str
    query_p4 = '"'
    query_p5 = " WHERE time > now() - 12h ORDER BY time DESC LIMIT 1"
    full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)  # Concatenate string
    return full_query_string


# Function to query Princeton Total Campus Energy CO2 Data from database and return a dictionary with query data
def query_database_campus_energy_co2() :
    # Function to generate a list of queries to be made to the database and store list in variable "list_of_queries"
    building_energy_co2_query = influxdb_query_builder_campus_energy_co2()
    query_str = str(building_energy_co2_query)  # convert query to type string
    previous_entries = influxdb_client.query(query_str)  # Query last DB entry with same type of measurement name
    previous_points = previous_entries.get_points()  # Convert to points
    dict_of_data = { }  # Initialize dictionary

    for previous_point in previous_points :  # Iterate through points
        previous_timepoint_pd = pd.to_datetime(previous_point['time'])  # Convert Timestamp to pandas timestamp object
        previous_value = previous_point['value']  # retrieves value
        previous_value_float = float(previous_value)  # convert to type float
        dict_of_data[previous_timepoint_pd] = previous_value_float  # Place timepoint: value in dictionary
    return dict_of_data


# Function to calculate most recent tally of Energy CO2 for each Dorm Room Sensor and write data to InfluxDB
def write_recent_dr_energy_co2_to_InfluxDB(measurement_name) :
    # Ensure measurement data name is type string
    sensor_data_stream_id = str(measurement_name)

    # List of times to eventually use latest time stamp
    list_of_times = []  # Initialize list

    # Dorm Room Energy Data
    dorm_energy_data_dict = query_database_dr_energy(sensor_data_stream_id)  # returns a dictionary with query data

    # For loop to get timestamp and values and append time and value in list_of_time and list_of_values
    for key , value in dorm_energy_data_dict.items() :
        esp32_sensor_energy_time = key
        esp32_sensor_energy_value = float(value)

    # Adds time stamp to list_of_times for finding latest timestamp
    list_of_times.append(esp32_sensor_energy_time)

    # Total Campus Energy Data
    total_campus_energy_dict = query_database_campus()  # returns a dictionary with query data

    # For loop to get timestamp and values and append time and value in list_of_time and list_of_values
    for key , value in total_campus_energy_dict.items() :
        total_campus_energy_time = key
        total_campus_energy_value = float(value)

    # Adds time stamp to list_of_times for finding latest timestamp
    list_of_times.append(total_campus_energy_time)

    # Total Campus Energy CO2 Data
    total_campus_energy_co2_dict = query_database_campus_energy_co2()  # returns a dictionary with query data

    # For loop to get timestamp and values and append time and value in total_campus_energy_co2_time and total_campus_energy_co2_value
    for key , value in total_campus_energy_co2_dict.items() :
        total_campus_energy_co2_time = key
        total_campus_energy_co2_value = float(value)

    # Adds time stamp to list_of_times for finding latest timestamp
    list_of_times.append(total_campus_energy_co2_time)

    # Date times are comparable; so you can use max(datetimes_list) and min(datetimes_list)
    # Source: https://stackoverflow.com/questions/3922644/find-oldest-youngest-datetime-object-in-a-list
    latest_timestamp = max(list_of_times)

    # Formula for Calculating Power Sensor Energy CO2
    # (esp32_sensor_energy_value/Campus Total Energy) * Campus Energy CO2
    esp32_sensor_energy_co2 = float((esp32_sensor_energy_value / total_campus_energy_value) * total_campus_energy_co2_value)
    esp32_sensor_energy_co2 = round(esp32_sensor_energy_co2 , 7)

    # Puts data in json body for writing to InfluxDB
    json_body = [
        {
            'measurement' : measurement_name ,
            'tags' : {
                'source_of_data' : "icetec, tigerenergy, personal api" ,
                'units' : 'Pounds CO2'
            } ,
            "time" : latest_timestamp ,
            'fields' : {
                'value' : esp32_sensor_energy_co2 ,
            }
        }
    ]

    # Write data to InfluxDB
    influxdb_client_DR_energy_CO2.write_points(json_body)


# Initialize databases
_init_influxdb_database()
