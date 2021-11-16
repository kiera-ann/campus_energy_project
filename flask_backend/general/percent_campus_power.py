'''Code to generate percent of campus Power Composition for front end'''
from influxdb import InfluxDBClient

INFLUXDB_ADDRESS = '140.180.133.81'  # Personal development Mac mini IP address
INFLUXDB_USER = 'admin'
INFLUXDB_PASSWORD = 'admin'
INFLUXDB_DATABASE = 'pu_campus_power_composition_raw'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD , None)

data_field_labels_of_interest = ["EP.Totals.Power.i.Import_kW" , "EP.Totals.Power.i.Solar_kW" ,
                                 "EP.Cogen.Turbine.Power.ION.Total_kW"]


# Build query string
def influxdb_query_builder(data_field_label) :
    # Set data_field provided to function to variable "data_field_label_str"
    data_field_label_str = str(data_field_label)
    query_p1 = 'SELECT "value_percent" FROM "pu_campus_power_composition_raw"."autogen".'
    query_p2 = '"'
    query_p3 = data_field_label_str
    query_p4 = '"'
    query_p5 = " WHERE time > now() - 12h ORDER BY time DESC LIMIT 1"
    full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)  # Concatenate string
    return full_query_string


# Function that gets Campus Power Composition in Real Time
def get_campus_power_composition() :
    data_dict = { }  # Initialize dictionary
    new_data_dict = { }  # Initialize dictionary
    return_data_dict = { }  # Initialize dictionary

    for data_field in data_field_labels_of_interest :
        query = influxdb_query_builder(data_field)
        query_str = str(query)
        previous_entries = influxdb_client.query(query_str)  # Query last DB entry with same type of measurement name
        previous_points = previous_entries.get_points()  # Convert to points
        for previous_point in previous_points :  # Iterate through points
            field_percent = previous_point['value_percent']
            field_percent = round(float(field_percent))
            data_dict[data_field] = field_percent

    new_data_dict['solar'] = data_dict['EP.Totals.Power.i.Solar_kW']
    new_data_dict['grid'] = data_dict['EP.Totals.Power.i.Import_kW']
    new_data_dict['campus_power_plant'] = data_dict['EP.Cogen.Turbine.Power.ION.Total_kW']
    new_data_dict['unit_name'] = "percent"
    new_data_dict['unit_symbol'] = "%"

    return_data_dict['campus_power_composition'] = new_data_dict
    return return_data_dict
