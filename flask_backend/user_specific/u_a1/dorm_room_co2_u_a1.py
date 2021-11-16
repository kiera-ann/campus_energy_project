''' Function to get sum of Dorm Room CO2 from InfluxDB. '''

from influxdb import InfluxDBClient
import pandas as pd

# For Dorm Room Energy Sensor  Data
# For Dorm Room (DR) Energy CO2
INFLUXDB_ADDRESS = '140.180.133.81'  # Personal development Mac mini IP address
INFLUXDB_USER = 'admin'
INFLUXDB_PASSWORD = 'admin'
INFLUXDB_DATABASE = 'dormroom_energy_co2_database_raw'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD , None)

list_of_sensor_names = ['ESP32_POWER_SENSOR: 7C:9E:BD:D8:C4:9C']


# Initialize database
def _init_influxdb_database() :
    databases = influxdb_client.get_list_database()  # check if the database is there by using the get_list_database() function of the client:
    if len(list(filter(lambda x : x['name'] == INFLUXDB_DATABASE , databases))) == 0 :
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)  # we’ll set the client to use this database


# Build query for database query of Dorm Room (DR) Energy CO2
def influxdb_query_builder_dorm_co2(sensor_name) :
    # Set data_field provided to function to variable "data_field_label_str"
    data_field_label_str = str(sensor_name)
    query_p1 = 'SELECT "value" FROM "dormroom_energy_co2_database_raw"."autogen".'
    query_p2 = '"'
    query_p3 = data_field_label_str
    query_p4 = '"'
    query_p5 = " WHERE time > now() - 15d ORDER BY time"
    full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)    # Concatenate string
    return full_query_string


# Function to query InfluxDB Dorm Room (DR) Energy CO2 data
def query_influxdb_dorm_co2_data_u_a1() :
    # Initialize Variable
    total_co2_today = 0.0
    total_co2_yesterday = 0.0
    total_co2_week = 0.0
    # total_co2_month = 0.0
    return_data_dict = { }  # Initialize dictionary

    # Each loop is done for a sensor's data
    for name in list_of_sensor_names :
        try :
            query = influxdb_query_builder_dorm_co2(name)
            query_str = str(query)
            dorm_co2_df = pd.DataFrame(influxdb_client.query(query_str).get_points())

            # convert the 'time' column to datetime format
            # Source: https://www.geeksforgeeks.org/convert-the-column-type-from-string-to-datetime-format-in-pandas-dataframe/
            dorm_co2_df['time'] = pd.to_datetime(dorm_co2_df['time'])

            # Set index of dataframe to column "time"
            dorm_co2_df.set_index('time' , inplace=True)

            # Change index timezone from UTC to 'US/Eastern'
            # Source: https://stackoverflow.com/questions/22800079/converting-time-zone-pandas-dataframe
            dorm_co2_df.index = dorm_co2_df.index.tz_convert('US/Eastern')

            # Pandas Resample
            # Source: https://towardsdatascience.com/using-the-pandas-resample-function-a231144194c4

            # Calculations for the current day
            df_day = dorm_co2_df.resample("D").sum()
            dorm_co2_last_day = df_day.index.tolist()[-1]  # Date Today (Last day)
            dorm_co2_last_day_value = round(float(df_day['value'].tolist()[-1]) , 3)  # C02 Today (Last day)
            total_co2_today = total_co2_today + dorm_co2_last_day_value

            # Calculations for the previous day
            dorm_co2_previous_day_value = round(float(df_day['value'].tolist()[-2]) , 3)  # C02 Yesterday (Previous day)
            total_co2_yesterday = total_co2_yesterday + dorm_co2_previous_day_value

            # Calculations for the week
            df_week = dorm_co2_df.resample("W").sum()
            dorm_co2_last_week = df_week.index.tolist()[0]
            dorm_co2_last_week_value = round(float(df_week['value'].tolist()[-1]) , 3)
            total_co2_week = total_co2_week + dorm_co2_last_week_value

            # # Round values to 1 significant figure
            total_co2_today = round(total_co2_today , 1)
            total_co2_yesterday = round(total_co2_yesterday , 1)
            total_co2_week = round(total_co2_week , 1)

        except :
            pass

        data_dict = {
            'energy_report_co2' : {
                'total_co2_today' : total_co2_today ,
                'total_co2_yesterday' : total_co2_yesterday ,
                'total_co2_week' : total_co2_week ,
                'unit_name' : "pound" ,
                'unit_symbol' : 'lb'
            }
        }
    return data_dict
