import pandas as pd
from influxdb import InfluxDBClient

# For PU Campus Building Energy CO2 - Writing final building Energy CO2 to this database
INFLUXDB_ADDRESS = '140.180.133.81'  # Personal development Mac mini IP address
INFLUXDB_USER = 'admin'
INFLUXDB_PASSWORD = 'admin'
INFLUXDB_DATABASE = 'pu_arcgis_energy_co2_database_raw'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD ,
                                 database=INFLUXDB_DATABASE)


# Initialize database
def _init_influxdb_database() :
    databases = influxdb_client.get_list_database()  # check if the database is there by using the get_list_database() function of the client:
    if len(list(filter(lambda x : x['name'] == INFLUXDB_DATABASE , databases))) == 0 :
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)  # we’ll set the client to use this database


def list_of_campus_buildings() :
    # Name of file with campus URL Data
    pu_heatmap_csv_filename = "campus_building_type_data_url_final.csv"

    # Read CSV file and convert to pandas object
    df = pd.read_csv(pu_heatmap_csv_filename , sep=',')

    # Convert Pandas column to list
    # Source: https://datatofish.com/convert-pandas-dataframe-to-list/
    building_PU_R25_NAME = df['PU_R25_NAME'].tolist()
    return building_PU_R25_NAME


# Build query for database
def influxdb_query_builder(PU_R25_NAME) :
    # Set data_field provided to function to variable "data_field_label_str"
    data_field_label_str = str(PU_R25_NAME)
    query_p1 = 'SELECT "value" FROM "pu_arcgis_energy_co2_database_raw"."autogen".'
    query_p2 = '"'
    query_p3 = data_field_label_str
    query_p4 = '"'
    query_p5 = " WHERE time > now() - 40d ORDER BY time"
    full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)  # Concatenate string
    return full_query_string


# Function to query InfluxDB building data energy CO2 data
def query_influxdb_energy_co2_data(PU_R25_NAME) :
    building_energy_co2_query = influxdb_query_builder(PU_R25_NAME)
    query_str = str(building_energy_co2_query)  # convert query to type string
    buidling_energy_co2_df = pd.DataFrame(influxdb_client.query(query_str).get_points())

    # convert the 'time' column to datetime format
    # Source: https://www.geeksforgeeks.org/convert-the-column-type-from-string-to-datetime-format-in-pandas-dataframe/
    buidling_energy_co2_df['time'] = pd.to_datetime(buidling_energy_co2_df['time'])
    # print(buidling_energy_co2_df)  # Debugging print statement

    # Set index of dataframe to column "time"
    buidling_energy_co2_df.set_index('time' , inplace=True)

    # Change index timezone from UTC to 'US/Eastern'
    # Source: https://stackoverflow.com/questions/22800079/converting-time-zone-pandas-dataframe
    buidling_energy_co2_df.index = buidling_energy_co2_df.index.tz_convert('US/Eastern')

    # Pandas Resample
    # Source: https://towardsdatascience.com/using-the-pandas-resample-function-a231144194c4
    df_day = buidling_energy_co2_df.resample("D").sum()

    # Not the best way since it does not account for difference in Eastern Standard Time (EST) & Eastern Daylight Time (EDT)
    # Still left for note taking/new learning approach
    # Offset of '+5H' to adjust for difference in timezone since time is recorded in UTC but we need to convert to US/Eastern
    # df_day = building_energy_co2_df.resample("D", offset = '+5H').sum()

    building_energy_co2_last_day = df_day.index.tolist()[-1]
    print("building_energy_co2_last_day")  # Debugging print statement
    print(building_energy_co2_last_day)  # Debugging print statement
    building_energy_co2_last_day_value = round(float(df_day['value'].tolist()[-1]) , 3)
    print("building_energy_co2_last_day_value")  # Debugging print statement
    print(building_energy_co2_last_day_value)  # Debugging print statement
    print()

    df_week = buidling_energy_co2_df.resample("W").sum()
    building_energy_co2_last_week = df_week.index.tolist()[-1]
    print("building_energy_co2_last_week")  # Debugging print statement
    print(building_energy_co2_last_week)  # Debugging print statement
    building_energy_co2_last_week_value = round(float(df_week['value'].tolist()[-1]) , 3)
    print("building_energy_co2_last_week_value")  # Debugging print statement
    print(building_energy_co2_last_week_value)  # Debugging print statement
    print()

    df_month = buidling_energy_co2_df.resample("M").sum()
    building_energy_co2_last_month = df_month.index.tolist()[-1]
    print("building_energy_co2_last_month")  # Debugging print statement
    print(building_energy_co2_last_month)  # Debugging print statement
    building_energy_co2_last_month_value = round(float(df_month['value'].tolist()[-1]) , 3)
    print("building_energy_co2_last_month_value")  # Debugging print statement
    print(building_energy_co2_last_month_value)  # Debugging print statement
