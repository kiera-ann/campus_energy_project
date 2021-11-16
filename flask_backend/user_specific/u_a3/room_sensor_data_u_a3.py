''' Function to get Room Environment Data from Sensors.'''

from influxdb import InfluxDBClient
import pendulum

INFLUXDB_ADDRESS = '140.180.133.81'  # Personal development Mac mini IP address
INFLUXDB_USER = 'admin'
INFLUXDB_PASSWORD = 'admin'
INFLUXDB_DATABASE = 'environment_sensor_raw_db'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD , None)

sensor_name = "ESP32_ENVIRO_3"


# Initialize database
def _init_influxdb_database() :
    databases = influxdb_client.get_list_database()  # check if the database is there by using the get_list_database() function of the client:
    if len(list(filter(lambda x : x['name'] == INFLUXDB_DATABASE , databases))) == 0 :
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)  # we’ll set the client to use this database


# Build query for database query of Dorm Room Enviro Sensor Data - Temperature Data
def influxdb_query_builder_dorm_enviro_t_value() :
    # Set data_field provided to function to variable "data_field_label_str"
    data_field_label_str = str(sensor_name)
    query_p1 = 'SELECT "t_value" FROM "environment_sensor_raw_db"."autogen".'
    query_p2 = '"'
    query_p3 = data_field_label_str
    query_p4 = '"'
    query_p5 = " WHERE time > now() - 12h ORDER BY time DESC LIMIT 1"
    full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)  # Concatenate string
    return full_query_string


# Build query for database query of Dorm Room Enviro Sensor Data - Relative Humidity Data
def influxdb_query_builder_dorm_enviro_rh_value() :
    # Set data_field provided to function to variable "data_field_label_str"
    data_field_label_str = str(sensor_name)
    query_p1 = 'SELECT "rh_value" FROM "environment_sensor_raw_db"."autogen".'
    query_p2 = '"'
    query_p3 = data_field_label_str
    query_p4 = '"'
    query_p5 = " WHERE time > now() - 12h ORDER BY time DESC LIMIT 1"
    full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)  # Concatenate string
    return full_query_string


def query_influxdb_sensor_enviro_data() :
    t_value_query = str(influxdb_query_builder_dorm_enviro_t_value())  # Query string for Temperature Data
    rh_value_query = str(influxdb_query_builder_dorm_enviro_rh_value())  # Query string for Relative Humidity Data
    enviro_dict = { }  # Initialize Dictionary

    # For Temperature Data
    previous_db_entry_t_value = influxdb_client.query(t_value_query)  # Query last DB entry with same type of measurement name
    previous_points_t_value = previous_db_entry_t_value.get_points()  # Convert to points

    for previous_point_t_value in previous_points_t_value :  # Iterate through points
        previous_t_value = previous_point_t_value['t_value']  # retrieves value
        previous_t_value_float = float(previous_t_value)  # convert to type float

    # For Relative Humidity Data
    previous_db_entry_rh_value = influxdb_client.query(rh_value_query)  # Query last DB entry with same type of measurement name
    previous_points_rh_value = previous_db_entry_rh_value.get_points()  # Convert to points

    for previous_point_rh_value in previous_points_rh_value :  # Iterate through points
        previous_rh_value = previous_point_rh_value['rh_value']  # retrieves value
        previous_rh_value_float = float(previous_rh_value)  # convert to type float

    enviro_dict = {
        "temperature" : previous_t_value_float ,
        "humidity_value" : previous_rh_value_float ,
    }
    return enviro_dict


# get_sensor_data_u_a1
def get_sensor_data_u_a3() :
    data_dict = { }  # Initialize Dictionary
    building_name = 'Baker Hall'
    room_number = 'S204'
    full_room_location = 'Baker Hall - ROOM S204'
    enviro_dict = query_influxdb_sensor_enviro_data()
    celsius_temperature_value = float(enviro_dict['temperature'])
    temperature_value = round((celsius_temperature_value * 1.8) + 32)  # Convert Celsius To Fahrenheit
    temperature_units = "Fahrenheit"
    temperature_units_symbol = " °F"
    humidity_value = round(float(enviro_dict['humidity_value']))
    humidity_units = "percent"
    humidity_units_symbol = " %"
    time_now_pendulum = pendulum.now('UTC')
    time_now_pendulum_string = time_now_pendulum.strftime('%Y-%m-%dT%H:%M:%S%z')

    # Add a colon to timezone offset when using datetime.strftime
    # Source: https://gist.github.com/mattstibbs/a283f55a124d2de1b1d732daaac1f7f8
    # Add a colon separator to the offset segment
    sensor_timestamp_utc = "{0}:{1}".format(
        time_now_pendulum_string[:-2] ,
        time_now_pendulum_string[-2 :]
    )

    # Build Dictionary
    data_dict = { 'room_building_info' :
        {
            'building_name' : building_name ,
            'room_number' : room_number ,
            'full_room_location' : full_room_location ,
            'temperature_value' : temperature_value ,
            'temperature_units' : temperature_units ,
            'temperature_units_symbol' : temperature_units_symbol ,
            'humidity_value' : humidity_value ,
            'humidity_units' : humidity_units ,
            'humidity_units_symbol' : humidity_units_symbol ,
            'sensor_timestamp_utc' : sensor_timestamp_utc ,
        }
    }

    return data_dict

