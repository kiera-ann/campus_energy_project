''' Function to calculate most recent energy use emissions (pounds CO2/KWH) for Princeton's Campus Energy and store data in InfluxDB. '''
import pandas as pd

# Import InfluxDB Module
from influxdb import InfluxDBClient

# For PU Energy database
INFLUXDB_ADDRESS = '140.180.133.81'  # Personal development Mac mini IP address
INFLUXDB_USER = 'admin'
INFLUXDB_PASSWORD = 'admin'
INFLUXDB_DATABASE_co2 = 'pu_co2_database_raw'

influxdb_client_co2 = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD ,
                                     database=INFLUXDB_DATABASE_co2)

# For PU Energy database
INFLUXDB_DATABASE_energy = 'pu_energy_database_raw'

influxdb_client_energy = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD ,
                                        database=INFLUXDB_DATABASE_energy)

# For PU Energy emissions (pounds CO2/KWH) database
INFLUXDB_DATABASE = 'pu_energy_emissions_raw'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD ,
                                 database=INFLUXDB_DATABASE)


# Initialize databases
def _init_influxdb_database() :
    databases = influxdb_client.get_list_database()  # check if the database is there by using the get_list_database() function of the client:
    if len(list(filter(lambda x : x['name'] == INFLUXDB_DATABASE , databases))) == 0 :
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)  # we’ll set the client to use this database


# Build query for database query of last 1 point for Energy CO2 from Princeton: 'PU CO2 Data: Energy'
def influxdb_query_builder_energy_co2_lbs() :
    # Set data_field provided to function to variable "data_field_label_str"
    data_field_label_str = str('PU CO2 Data: Energy')
    query_p1 = 'SELECT "value" FROM "pu_co2_database_raw"."autogen".'
    query_p2 = '"'
    query_p3 = data_field_label_str
    query_p4 = '"'
    query_p5 = " WHERE time > now() - 12h ORDER BY time DESC LIMIT 1"

    # Concatenate string
    full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)

    # print(full_query_string)    # Debugging print statement
    return full_query_string


# Debugging function
# print(influxdb_query_builder_energy_co2_lbs())  # Debugging print statement


# Build query for database query of last 1 points for power from Princeton Energy Calculations: "PU Energy Data: Total"
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


# Debugging function
# print(influxdb_query_builder_campus_energy_kWh())  # Debugging print statement

# Function to query InfluxDb and return 2 dictionaries in a list
def query_InfluxDB_data() :
    # List of data to return
    list_of_data = []  # Initialize list
    # Dictionary for Campus Energy CO2 data
    campus_energy_co2_dict = { }  # Initialize dictionary
    # Dictionary for Campus Energy data
    campus_energy_dict = { }  # Initialize dictionary

    # 'PU CO2 Data: Energy' Query
    campus_energy_co2_query_str = influxdb_query_builder_energy_co2_lbs()
    campus_energy_co2_query_str = str(campus_energy_co2_query_str)  # Convert to type string
    # print(campus_energy_co2_query_str)    # Debugging print statement

    # 'PU Energy Data: Total' Query
    campus_energy_used_query_str = influxdb_query_builder_campus_energy_kWh()
    campus_energy_used_query_str = str(campus_energy_used_query_str)  # Convert to type string
    # print(campus_energy_used_query_str)    # Debugging print statement

    # Query 'PU CO2 Data: Energy' data
    previous_entries_co2 = influxdb_client_co2.query(campus_energy_co2_query_str)  # Query last DB entry with same type of measurement name
    previous_points_co2 = previous_entries_co2.get_points()  # Convert to points
    for previous_point_co2 in previous_points_co2 :  # Iterate through points

        previous_timepoint_co2_pd = pd.to_datetime(previous_point_co2['time'])  # Convert Timestamp to pandas timestamp object
        # print(previous_timepoint_co2_pd)  # Debugging print statement

        previous_value_co2 = previous_point_co2['value']  # retrieves value
        previous_value_co2_float = float(previous_value_co2)  # convert to type float
        # print(previous_value_co2_float) # Debugging print statement

    campus_energy_co2_dict[previous_timepoint_co2_pd] = previous_value_co2_float
    data_dict_co2 = {
        'PU CO2 Data: Energy lbs CO2' : campus_energy_co2_dict
    }
    # print(campus_energy_co2_dict)   # Debugging print statement
    # print(data_dict_co2)    # Debugging print statement
    list_of_data.append(data_dict_co2)

    # Query 'PU Energy Data: Total' data
    previous_entries_energy = influxdb_client_energy.query(campus_energy_used_query_str)  # Query last DB entry with same type of measurement name
    previous_points_energy = previous_entries_energy.get_points()  # Convert to points
    for previous_point_energy in previous_points_energy :  # Iterate through points

        previous_timepoint_energy_pd = pd.to_datetime(previous_point_energy['time'])  # Convert Timestamp to pandas timestamp object
        # print(previous_timepoint_energy_pd)  # Debugging print statement

        previous_value_energy = previous_point_energy['value']  # retrieves value
        previous_value_energy_float = float(previous_value_energy)  # convert to type float
        # print(previous_value_energy_float) # Debugging print statement

    campus_energy_dict[previous_timepoint_energy_pd] = previous_value_energy_float
    data_dict_energy = {
        'PU Energy Data: Total KWH' : campus_energy_dict
    }
    # print(campus_energy_dict)   # Debugging print statement
    # print(data_dict_energy)  # Debugging print statement
    list_of_data.append(data_dict_energy)

    # print(list_of_data) # Debugging print statement
    return list_of_data


# Debugging function
# print(query_InfluxDB_data())    # Debugging print statement

# Function to calculate the most recent energy emission data to InfluxDB
def write_recent_energy_emission_rate_to_InfluxDB() :
    list_of_data = []  # Initialize list

    list_of_times = []  # Initialize list of timestamps
    list_of_values = []  # Initialize list of values

    # Stores measurement name as key and its data value as value
    data_dict = { }  # Initialize dictionary

    # Gets data from Function 'query_InfluxDB_data()'
    list_of_data = query_InfluxDB_data()
    # print(list_of_data)

    for dictionary in list_of_data :
        # Iterate through dictionary of timestamp and values and append time and value in list_of_time and list_of_values
        for key , value in dictionary.items() :
            # print(key)  # Debugging print statement
            # print(value)    # Debugging print statement

            for timestamp , data_value in value.items() :
                # print(timestamp)    # Debugging print statement
                list_of_times.append(timestamp)
                # print(data_value)   # Debugging print statement
                data_dict[key] = data_value

    # print(data_dict)    # Debugging print statement
    # print(list_of_times)    # Debugging print statement

    # Date times are comparable; so you can use max(datetimes_list) and min(datetimes_list)
    # Source: https://stackoverflow.com/questions/3922644/find-oldest-youngest-datetime-object-in-a-list
    # I will use the latest timestamp as the overall timestamp to apply to the data to be input into InfluxDB
    latest_timestamp = max(list_of_times)
    # print(latest_timestamp)   # Debugging print statement

    # Extract CO2 value
    co2_emissions_lbs = data_dict['PU CO2 Data: Energy lbs CO2']
    # print(co2_emissions_lbs)  # Debugging print statement
    # Extract Energy value
    energy_value_kwh = data_dict['PU Energy Data: Total KWH']
    # print(energy_value_kwh)  # Debugging print statement

    # Formula to calculate energy emission rate
    # CO2 Emission (unit pounds) / Energy (unit KWH)
    energy_emission_rate_value = co2_emissions_lbs / energy_value_kwh
    # print(energy_emission_rate_value)       # Debugging print statement
    energy_emission_rate_value = round(float(energy_emission_rate_value), 8)
    # print(energy_emission_rate_value)  # Debugging print statement

    # Puts data in json body for writing to InfluxDB
    json_body = [
        {
            'measurement' : "PU Energy Emission Rate" ,
            'tags' : {
                'source_of_data' : "icetec_tigerenergy_api" ,
                'units' : 'Pounds CO2/KWH'
            } ,
            "time" : latest_timestamp ,
            'fields' : {
                'value' : energy_emission_rate_value ,
            }
        }
    ]

    # Write data to InfluxDB
    influxdb_client.write_points(json_body)
    # print("PU Energy Emission Rate")  # Debugging print statement
    # print(json_body) # Debugging print statement


# Debugging function
# print(write_recent_energy_emission_rate_to_InfluxDB())  # Debugging print statement

# Initialize databases
_init_influxdb_database()
