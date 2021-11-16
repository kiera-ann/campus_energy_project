''' Function to calculate metric tons of CO2 Princeton University contributed from the PJM/PSEG grid. Writes to InfluxDB. '''
from influxdb import InfluxDBClient
import pandas as pd

# For PJM database
INFLUXDB_ADDRESS = '140.180.133.81'  # Personal development Mac mini IP address
INFLUXDB_USER = 'admin'
INFLUXDB_PASSWORD = 'admin'
INFLUXDB_DATABASE = 'pjm_database_raw'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD , database=INFLUXDB_DATABASE)

# For PU CO2 database
INFLUXDB_USER_PU_CO2 = 'admin'
INFLUXDB_PASSWORD_PU_CO2 = 'admin'
INFLUXDB_DATABASE_PU_CO2 = 'pu_co2_database_raw'

influxdb_client_PU_CO2 = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER_PU_CO2 , INFLUXDB_PASSWORD_PU_CO2 ,
                                        database=INFLUXDB_DATABASE_PU_CO2)

# For PU Energy database
INFLUXDB_USER_PU_Energy = 'admin'
INFLUXDB_PASSWORD_PU_Energy = 'admin'
INFLUXDB_DATABASE_PU_Energy = 'pu_energy_database_raw'

influxdb_client_PU_Energy = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER_PU_Energy , INFLUXDB_PASSWORD_PU_Energy ,
                                           database=INFLUXDB_DATABASE_PU_Energy)

# Query for InfluxDB calculation of Metric tons CO2 and total MW from PJM/PSEG Grid
query = 'SELECT "total_co2 (metric tons)","total_mw" FROM "pjm_database_raw"."autogen"."Power Grid Summary" WHERE time > now() - 4d ' \
        'ORDER BY time DESC LIMIT 1'

# Query for presence of calculation in InfluxDB "pu_co2_database_raw"
# Without a check, I will be overwriting values with 0.0 when subsequent calculations and DB entries are made with the same time point
query_last_co2 = 'SELECT "value" FROM "pu_co2_database_raw"."autogen"."PU Grid CO2" WHERE time > now() - 4d ORDER BY time DESC LIMIT 1'


# Build query for database query of last 2 points for power from PSEG grid; Icetec parameter: "EP.Totals.Power.i.Import_kW"
def influxdb_query_builder_energy_last_calculated() :
    # Set data_field provided to function to variable "data_field_label_str"
    data_field_label_str = str("PU Energy Data: Grid")
    query_p1 = 'SELECT "value" FROM "pu_energy_database_raw"."autogen".'
    query_p2 = '"'
    query_p3 = data_field_label_str
    query_p4 = '"'
    query_p5 = " WHERE time > now() - 2d ORDER BY time DESC LIMIT 1"
    full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)  # Concatenate string
    return full_query_string


# Function to query last 1 energy value used by campus and supplied from PJM/PSEG
def query_last_energy_value_import_InfluxDB() :
    # Generate Queries for Energy Import data; only last 1 point will be used
    energy_import_query = influxdb_query_builder_energy_last_calculated()
    query_str = str(energy_import_query)  # convert query to type string
    previous_entries = influxdb_client.query(query_str)  # Query last DB entry with same type of measurement name
    previous_points = previous_entries.get_points()  # Convert to points
    dict_of_data = { }  # Initialize dictionary

    for previous_point in previous_points :  # Iterate through points
        previous_timepoint_pd = pd.to_datetime(previous_point['time'])  # Convert Timestamp to pandas timestamp object
        previous_value = previous_point['value']  # retrieves value
        previous_value_float = float(previous_value)  # convert to type float
        dict_of_data[previous_timepoint_pd] = previous_value_float  # Place timepoint: value in dictionary
    return dict_of_data


# Function to calculate pounds of CO2 Princeton University contributed to from the PJM/PSEG grid
def write_campus_grid_co2_to_influxDB() :
    dict_of_data_dt_kWh = { }  # Initialize dictionary
    dict_of_data_dt_kWh = query_last_energy_value_import_InfluxDB()  # Returns a dictionary of timestamp and kWh value calculated
    list_of_times = []  # Initialize list of timestamps
    list_of_values = []  # Initialize list of values

    # Iterate through dictionary of timestamp and values and append time and value in list_of_time and list_of_values
    for key , value in dict_of_data_dt_kWh.items() :
        list_of_times.append(key)
        list_of_values.append(value)

    # Gets the time values
    last_timepoint = list_of_times[0]

    # Gets the last KWh calculated
    last_value_kWh = list_of_values[0]

    # kWh from Princeton grid use
    pu_grid_KWh_icetec = last_value_kWh

    # Query database for latest value of Metric tons CO2 and total MW from PJM Grid
    results = influxdb_client.query(query)
    points = results.get_points()

    # For loop to get Metric tons CO2 and total MW values from PJM data.
    # Since the data from the grid is in hourly intervals, the power values can be considered energy values since Energy is power x time,
    # where time is 1 hr
    for point in points :
        grid_total_co2_metric_tons = round(float(point['total_co2 (metric tons)']) , 5)  # float 5 decimal values
        grid_total_mwh = round(float(point['total_mw']) , 5)  # float 5 decimal values
        grid_total_kWh = 1000 * grid_total_mwh  # conversion to kilowatts units since University reports in kilowatts while grid is in megawatts

    # Formula is (pu_grid_KWh_icetec / grid_total_kWh) * grid_total_co2_metric_tons = total_co2_metric_tons from grid for campus
    campus_metric_tons_co2_grid = ((pu_grid_KWh_icetec / grid_total_kWh) * grid_total_co2_metric_tons)
    campus_metric_tons_co2_grid = round((campus_metric_tons_co2_grid) , 5)

    # For conversion to pounds CO2 from metric tons CO2
    campus_pounds_co2_grid = campus_metric_tons_co2_grid * 2204.62
    campus_pounds_co2_grid = round((campus_pounds_co2_grid) , 5)

    # JSON body for InfluxDB
    json_body = [
        {
            'measurement' : "PU CO2: Grid" ,
            'tags' : {
                'source_of_data' : "personal:icetec,tigerenergy,pjm" ,
                'units' : 'Pounds CO2'
            } ,
            "time" : last_timepoint ,
            'fields' : {
                'value' : campus_pounds_co2_grid
            }
        }
    ]

    influxdb_client_PU_CO2.write_points(json_body)  # Write to InfluxDB


# Function to initialize database
def _init_influxdb_database() :
    databases = influxdb_client.get_list_database()  # check if the database is there by using the get_list_database() function of the client:
    if len(list(filter(lambda x : x['name'] == INFLUXDB_DATABASE , databases))) == 0 :
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)  # we’ll set the client to use this database


_init_influxdb_database()  # Initialize database
