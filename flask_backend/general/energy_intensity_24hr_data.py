''' Function to get last 24 average hourly values for energy intensity of Princeton University.'''
from influxdb import InfluxDBClient
import pandas as pd

# For PU Energy emissions (pounds CO2/KWH) database
INFLUXDB_ADDRESS = '140.180.133.81'  # Personal development Mac mini IP address
INFLUXDB_USER = 'admin'
INFLUXDB_PASSWORD = 'admin'
INFLUXDB_DATABASE = 'pu_energy_emissions_raw'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD , None)


# Initialize database
def _init_influxdb_database() :
    databases = influxdb_client.get_list_database()  # check if the database is there by using the get_list_database() function of the client:
    if len(list(filter(lambda x : x['name'] == INFLUXDB_DATABASE , databases))) == 0 :
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)  # we’ll set the client to use this database


# Build query for database query of Dorm Room (DR) Energy CO2
# Query last 26 hours in descending order
def influxdb_query_builder_campus_energy_intensity() :
    # Set data_field provided to function to variable "data_field_label_str"
    data_field_label_str = str('PU Energy Emission Rate')
    query_p1 = 'SELECT "value" FROM "pu_energy_emissions_raw"."autogen".'
    query_p2 = '"'
    query_p3 = data_field_label_str
    query_p4 = '"'
    query_p5 = " WHERE time > now() - 24h ORDER BY time DESC"
    full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)    # Concatenate string
    return full_query_string


# Function to query InfluxDB PU Energy emissions (pounds CO2/KWH) database 'pu_energy_emissions_raw'
def query_influxdb_campus_energy_emission_intensity() :
    new_list_of_values = []  # Initialize list
    query = influxdb_query_builder_campus_energy_intensity()
    query_str = str(query)
    campus_CO2_KWH_df = pd.DataFrame(influxdb_client.query(query_str).get_points())

    # convert the 'time' column to datetime format
    # Source: https://www.geeksforgeeks.org/convert-the-column-type-from-string-to-datetime-format-in-pandas-dataframe/
    campus_CO2_KWH_df['time'] = pd.to_datetime(campus_CO2_KWH_df['time'])

    # Set index of dataframe to column "time"
    campus_CO2_KWH_df.set_index('time' , inplace=True)

    # Change index timezone from UTC to 'US/Eastern'
    # Source: https://stackoverflow.com/questions/22800079/converting-time-zone-pandas-dataframe
    campus_CO2_KWH_df.index = campus_CO2_KWH_df.index.tz_convert('US/Eastern')

    # Pandas Resample
    # Source: https://towardsdatascience.com/using-the-pandas-resample-function-a231144194c4

    # Calculations for the current day
    df_day = campus_CO2_KWH_df.resample("H").mean()

    # Format index times as string in format '%Y-%m-%dT%H:%M:%S' e.g 2021-03-14T16:00:00 and makes a list
    # list_of_times = df_day.index.strftime('%Y-%m-%dT%H:%M:%S').tolist()[-24 :]
    list_of_times = df_day.index.strftime('%Y-%m-%d %H:%M').tolist()[-24 :]

    # Makes a list of the values
    list_of_values = df_day['value'].tolist()[-24 :]

    # For loop to convert float values to 2 significant figures
    for value in list_of_values :
        value = round(float(value) , 2)
        new_list_of_values.append(value)

    # to convert lists to dictionary
    # using zip()
    # Source: https://www.geeksforgeeks.org/python-convert-two-lists-into-a-dictionary/
    data_dict_dt_lbsco2_mwh = dict(zip(list_of_times , new_list_of_values))

    # Data dictionary to return
    data_dict_to_return = {
        "campus_energy_intensity" : data_dict_dt_lbsco2_mwh ,
        "units" : "lbs CO2/Wh" ,
        "daily_graph_data_legend" : "EPT_DateTime : lbs CO2/Wh"
    }

    return data_dict_to_return
