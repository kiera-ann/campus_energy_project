''' Function to calculate kiloWatts per hour from Princeton Cogen MicroTurbines: EP.Totals.Power.i.MicroTurb_kW. Add data to InfluxDB '''
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


# Build query for database query of last 2 points for power from Princeton Cogen MicroTurbines; Icetec parameter: "EP.Totals.Power.i.MicroTurb_kW"
def influxdb_query_builder_cogen_microturbine_kW() :
    # Set data_field provided to function to variable "data_field_label_str"
    data_field_label_str = str("EP.Totals.Power.i.MicroTurb_kW")
    query_p1 = 'SELECT "value" FROM "pu_icetec_database_raw"."autogen".'
    query_p2 = '"'
    query_p3 = data_field_label_str
    query_p4 = '"'
    query_p5 = " WHERE time > now() - 12h ORDER BY time DESC LIMIT 2"
    full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)  # Concatenate string
    return full_query_string


# Function to query last 2 values
def query_last_2_values_cogen_microturbine_InfluxDB() :
    # Generate Queries for Cogen Turbine data; only last 2 points will be used
    cogen_microturbine_query = influxdb_query_builder_cogen_microturbine_kW()
    query_str = str(cogen_microturbine_query)  # convert query to type string
    previous_entries = influxdb_client.query(query_str)  # Query last DB entry with same type of measurement name
    previous_points = previous_entries.get_points()  # Convert to points
    dict_of_data = { }  # Initialize dictionary

    for previous_point in previous_points :  # Iterate through points
        previous_timepoint_pd = pd.to_datetime(previous_point['time'])  # Convert Timestamp to pandas timestamp object
        previous_value = previous_point['value']  # retrieves value
        previous_value_float = float(previous_value)  # convert to type float
        dict_of_data[previous_timepoint_pd] = previous_value_float  # Place timepoint: value in dictionary
    return dict_of_data


# Function to calculate kiloWatts per hour from Princeton Cogen MicroTurbine; Icetec parameter: "EP.Totals.Power.i.MicroTurb_kW"
def write_cogen_microturbine_energy_to_InfluxDB() :
    dict_of_data_dt_kW = { }  # Initialize dictionary

    # Returns a dictionary of timestamp and kW values from EP.Totals.Power.i.MicroTurb_kW
    dict_of_data_dt_kW = query_last_2_values_cogen_microturbine_InfluxDB()
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

    # Gets the values of kW from EP.Totals.Power.i.MicroTurb_kW
    last_value_kW = list_of_values[0]
    first_value_kW = list_of_values[1]

    # Calculates average from the last two power values
    average_power_cogen_microturbine_kW = float((last_value_kW + first_value_kW) / 2)
    average_power_cogen_microturbine_kW = round(float(average_power_cogen_microturbine_kW) , 4)

    # Finds kW per hour
    # Energy is simply power times time. For instance, the most common unit of energy in the US is the kilowatt hour, or kWh.
    # One kWh is equal to using 1000 watts, or 1 kW continuously for one hour. As such, a kWh is born.
    kW_per_hour = average_power_cogen_microturbine_kW * time_difference_hr

    # Puts data in json body for writing to InfluxDB
    json_body = [
        {
            'measurement' : "PU Energy Data: Cogen MicroTurbine" ,
            'tags' : {
                'source_of_data' : "icetec_tigerenergy_api" ,
                'units' : 'kW_per_hour' ,
                'is_renewable' : False ,
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
