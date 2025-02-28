''' Function to get last 24 average hourly values for energy used in dorm room.'''

from influxdb import InfluxDBClient
import pandas as pd

# For Dorm Room Energy Sensor  Data
# For Dorm Room (DR) Energy CO2
INFLUXDB_ADDRESS = '140.180.133.81'  # Personal development Mac mini IP address
INFLUXDB_USER = 'admin'
INFLUXDB_PASSWORD = 'admin'
INFLUXDB_DATABASE = 'dormroom_energy_database_raw'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD , None)

list_of_sensor_names = ['ESP32_POWER_SENSOR: 7C:9E:BD:D7:4D:58' ,
                        'ESP32_POWER_SENSOR: 7C:9E:BD:D7:4B:AC' ,
                        'ESP32_POWER_SENSOR: 7C:9E:BD:D7:4E:88']


# Initialize database
def _init_influxdb_database() :
    databases = influxdb_client.get_list_database()  # check if the database is there by using the get_list_database() function of the client:
    if len(list(filter(lambda x : x['name'] == INFLUXDB_DATABASE , databases))) == 0 :
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)  # we’ll set the client to use this database


# Build query for database query of Dorm Room (DR) Energy
def influxdb_query_builder_dorm_energy(sensor_name) :
    # Set data_field provided to function to variable "data_field_label_str"
    data_field_label_str = str(sensor_name)
    query_p1 = 'SELECT "value" FROM "dormroom_energy_database_raw"."autogen".'
    query_p2 = '"'
    query_p3 = data_field_label_str
    query_p4 = '"'
    query_p5 = " WHERE time > now() - 24h ORDER BY time"
    full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)  # Concatenate string
    return full_query_string


# Function to query InfluxDB Dorm Room (DR) Energy data
def query_influxdb_dorm_24hr_energy_data(sensor_name) :
    new_list_of_values_24hr_wh_sum = []  # Initialize list
    query = influxdb_query_builder_dorm_energy(sensor_name)
    query_str = str(query)
    dorm_energy_df = pd.DataFrame(influxdb_client.query(query_str).get_points())

    # convert the 'time' column to datetime format
    # Source: https://www.geeksforgeeks.org/convert-the-column-type-from-string-to-datetime-format-in-pandas-dataframe/
    dorm_energy_df['time'] = pd.to_datetime(dorm_energy_df['time'])

    # Set index of dataframe to column "time"
    dorm_energy_df.set_index('time' , inplace=True)

    # Change index timezone from UTC to 'US/Eastern'
    # Source: https://stackoverflow.com/questions/22800079/converting-time-zone-pandas-dataframe
    dorm_energy_df.index = dorm_energy_df.index.tz_convert('US/Eastern')

    # Pandas Resample
    # For 24 hour graph data
    df_day_24hr_mean = dorm_energy_df.resample("H").sum()

    # Format index times as string in format '%Y-%m-%dT%H:%M:%S' e.g 2021-03-14T16:00:00 and makes a list of last 25 values
    # Source: https://www.geeksforgeeks.org/python-get-last-n-elements-from-given-list/
    # Python | Get last N elements from given list
    # list_of_times_24hr_sum = df_day_24hr_mean.index.strftime('%Y-%m-%dT%H:%M:%S').tolist()[-24 :]
    list_of_times_24hr_sum = df_day_24hr_mean.index.strftime('%Y-%m-%d %H:%M').tolist()[-24 :]

    # Makes a list of last 24 values
    list_of_values_24hr_sum_kwh = df_day_24hr_mean['value'].tolist()[-24 :]

    # For loop to convert float values to 2 significant figures
    for value in list_of_values_24hr_sum_kwh :
        value_wh = value * 1000
        value_wh = round(float(value_wh) , 3)
        new_list_of_values_24hr_wh_sum.append(value_wh)

    # to convert lists to dictionary
    # using zip()
    # Source: https://www.geeksforgeeks.org/python-convert-two-lists-into-a-dictionary/
    data_dict_dt_wh = dict(zip(list_of_times_24hr_sum , new_list_of_values_24hr_wh_sum))

    return data_dict_dt_wh


# Function to combine all sensor data and return last set of values
def dorm_daily_data_combination_u_a4() :
    list_of_dict_data = []  # Initialize list

    for name in list_of_sensor_names :
        list_of_dict_data.append(query_influxdb_dorm_24hr_energy_data(name))

    df_with_dorm_sensor_dt_wh = pd.DataFrame(list_of_dict_data)
    # Use the T attribute or the transpose() method to swap (= transpose) the rows and columns of pandas.DataFrame.
    # Neither method changes the original object, but returns a new object with the rows and columns swapped (= transposed object).
    # Source: https://note.nkmk.me/en/python-pandas-t-transpose/
    transposed_df_with_dorm_sensor_dt_wh = df_with_dorm_sensor_dt_wh.T

    # Makes a new column titled "Sum" that is the sum of all sensor values
    # Rounds sum values to 2 significant figures
    transposed_df_with_dorm_sensor_dt_wh['Sum'] = round(transposed_df_with_dorm_sensor_dt_wh.sum(axis=1) , 2)

    # Makes a new dictionary with timestamp and sum value data
    # Source: https://stackoverflow.com/questions/18012505/python-pandas-dataframe-columns-convert-to-dict-key-and-value
    daily_24hr_sum_energy = dict(zip(transposed_df_with_dorm_sensor_dt_wh.to_dict('index') , transposed_df_with_dorm_sensor_dt_wh['Sum']))

    # Data dictionary to return
    data_dict_to_return = {
        "daily_graph_energy_wh_data" : daily_24hr_sum_energy ,
        "daily_graph_data_legend" : "EPT_DateTime : Watt-Hour"
    }

    return data_dict_to_return
