''' Function to determine fraction of campus power from different sources: PJM Grid, Solar Field, Cogen Turbine, Microturbine '''

import sys
import time
from datetime import datetime
from influxdb import InfluxDBClient

# Uses properly converted UTC time
from Campus_data_code.icetec_code.pu_icetec_data_function_utc import get_icetec_pu_data_function

INFLUXDB_ADDRESS = '140.180.133.81'  # Personal development Mac mini IP address
INFLUXDB_USER = 'admin'
INFLUXDB_PASSWORD = 'admin'
INFLUXDB_DATABASE = 'pu_campus_power_composition_raw'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD , None)


# Initialize database
def _init_influxdb_database() :
    databases = influxdb_client.get_list_database()  # check if the database is there by using the get_list_database() function of the client:
    if len(list(filter(lambda x : x['name'] == INFLUXDB_DATABASE , databases))) == 0 :
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)  # we’ll set the client to use this database


# Sources of energy of interest
data_field_labels_of_interest = ["EP.Totals.Power.i.Site_kW" , "EP.Totals.Power.i.Import_kW" , "EP.Totals.Power.i.Solar_kW" ,
                                 "EP.Cogen.Turbine.Power.ION.Total_kW" , "EP.Totals.Power.i.MicroTurb_kW"]


# Function to create json_body for InfluxDB writing of data
def json_body_creater_percent(data_field_label , timestamp , total_power_kW , power_percent) :
    # Determines if power source is renewable or not
    if data_field_label == "EP.Totals.Power.i.Solar_kW" :
        is_renewable_var = True
    else :
        is_renewable_var = False

    # Creates json_body with inputted data
    json_body = [
        {
            'measurement' : data_field_label ,
            'tags' : {
                'source_of_data' : "icetec_tigerenergy_api" ,
                'units' : 'percent' ,
                'is_renewable' : is_renewable_var ,
            } ,
            "time" : timestamp ,
            'fields' : {
                'value_percent' : power_percent ,
                'value_kW' : total_power_kW
            }
        }
    ]
    return json_body


# Build query for database entry
# This check is to avoid writing a value to database if there is no need since value is already written
def influxdb_query_builder(data_field_label) :
    # Set data_field provided to function to variable "data_field_label_str"
    data_field_label_str = str(data_field_label)
    query_p1 = 'SELECT "value_percent" FROM "pu_co2_database_raw"."autogen".'
    query_p2 = '"'
    query_p3 = data_field_label_str
    query_p4 = '"'
    query_p5 = " WHERE time > now() - 12h ORDER BY time DESC LIMIT 1"

    # Concatenate string
    full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)
    return full_query_string


# Function to ensure that the percent value returned from the grid is not more than 100% or less than 0%
def value_percent_checker(value) :
    value = float(value)
    if value > 100 :
        value = 100.0
    elif value < 0 :
        value = 0.0
    else :
        value = value
    return float(value)


# Determines percent of campus power from different energy sources
def campus_energy_source_division(list_of_data) :
    # Initialize list
    icetec_list_data = []
    energy_sources_for_campus = []

    icetec_list_data = list_of_data

    # Loop through elements in list_of_data received from Icetec API call
    for i in range(0 , len(list_of_data)) :
        if list_of_data[i]["data_field_label"] in data_field_labels_of_interest :
            energy_sources_for_campus.append(list_of_data[i])

    # For loop to loop through energy sources for the campus and extract kW value for each of the 5 campus energy sources
    for i in range(0 , len(energy_sources_for_campus)) :

        # EP.Totals.Power.i.Site_kW
        if energy_sources_for_campus[i]["data_field_label"] == "EP.Totals.Power.i.Site_kW" :
            total_power_of_campus_kW = energy_sources_for_campus[i]['value']
            total_power_of_campus_timestamp = energy_sources_for_campus[i]['timestamp']

        # EP.Totals.Power.i.Import_kW
        elif energy_sources_for_campus[i]["data_field_label"] == "EP.Totals.Power.i.Import_kW" :
            total_grid_power_kW = energy_sources_for_campus[i]['value']
            total_grid_power_timestamp = energy_sources_for_campus[i]['timestamp']

        # EP.Totals.Power.i.Solar_kW
        elif energy_sources_for_campus[i]["data_field_label"] == "EP.Totals.Power.i.Solar_kW" :
            total_solar_power_kW = energy_sources_for_campus[i]['value']
            total_solar_power_timestamp = energy_sources_for_campus[i]['timestamp']

        # EP.Cogen.Turbine.Power.ION.Total_kW
        elif energy_sources_for_campus[i]["data_field_label"] == "EP.Cogen.Turbine.Power.ION.Total_kW" :
            total_turbine_power_kW = energy_sources_for_campus[i]['value']
            total_turbine_power_timestamp = energy_sources_for_campus[i]['timestamp']

        # EP.Totals.Power.i.MicroTurb_kW
        elif energy_sources_for_campus[i]["data_field_label"] == "EP.Totals.Power.i.MicroTurb_kW" :
            total_micro_turbine_power_kW = energy_sources_for_campus[i]['value']
            total_micro_turbine_power_timestamp = energy_sources_for_campus[i]['timestamp']

    # PJM Grid Percent
    grid_power_percent = round((float(total_grid_power_kW / total_power_of_campus_kW) * 100) , 2)
    grid_power_percent = value_percent_checker(grid_power_percent)

    # Solar Power Percent
    solar_power_percent = round((float(total_solar_power_kW / total_power_of_campus_kW) * 100) , 2)
    solar_power_percent = value_percent_checker(solar_power_percent)

    # Turbine Power Percent
    turbine_power_percent = round((float(total_turbine_power_kW / total_power_of_campus_kW) * 100) , 2)
    turbine_power_percent = value_percent_checker(turbine_power_percent)

    # Micro Turbine Power Percent
    micro_turbine_power_percent = round((float(total_micro_turbine_power_kW / total_power_of_campus_kW) * 100) , 2)
    micro_turbine_power_percent = value_percent_checker(micro_turbine_power_percent)

    # Total Power as a percent (should be 100% but comes up to a little more/less sometimes)
    total_power_percent = grid_power_percent + solar_power_percent + turbine_power_percent + micro_turbine_power_percent
    # print(total_power_percent)  # Debugging print statement

    # Use function json_body_creater_percent(data_field_label , timestamp , total_power_kW , power_percent) to create JSON_body for writing to InfluxDB
    # EP.Totals.Power.i.Site_kW
    total_campus_power_json_body = json_body_creater_percent("EP.Totals.Power.i.Site_kW" , total_power_of_campus_timestamp ,
                                                             total_power_of_campus_kW , total_power_percent)

    # EP.Totals.Power.i.Import_kW
    total_grid_import_campus_power_json_body = json_body_creater_percent("EP.Totals.Power.i.Import_kW" , total_grid_power_timestamp ,
                                                                         total_grid_power_kW , grid_power_percent)

    # EP.Power.Solar.WindsorPV.Ion7550.i.Total_kW
    windsor_solar_power_json_body_json_body = json_body_creater_percent("EP.Totals.Power.i.Solar_kW" , total_solar_power_timestamp ,
                                                                        total_solar_power_kW , solar_power_percent)

    # EP.Cogen.Turbine.Power.ION.Total_kW
    cogen_turbine_power_json_body = json_body_creater_percent("EP.Cogen.Turbine.Power.ION.Total_kW" , total_turbine_power_timestamp ,
                                                              total_turbine_power_kW , turbine_power_percent)

    # EP.Totals.Power.i.MicroTurb_kW
    cogen_microturbine_power_json_body = json_body_creater_percent("EP.Totals.Power.i.MicroTurb_kW" , total_micro_turbine_power_timestamp ,
                                                                   total_micro_turbine_power_kW , micro_turbine_power_percent)

    list_to_write_influxDB = [total_campus_power_json_body , total_grid_import_campus_power_json_body , windsor_solar_power_json_body_json_body ,
                              cogen_turbine_power_json_body , cogen_microturbine_power_json_body]

    print("Division of Campus Energy Sources")  # Debugging print statement

    # For loop to write to InfluxDB, sends each item as a list
    for i in range(0 , len(list_to_write_influxDB)) :
        campus_data_to_influxdb(list_to_write_influxDB[i])

    # Separates the prints of "Division of Campus Energy Sources" from Icetec Parse Prints
    print()


# Function to write new data to InfluxDB
def campus_data_to_influxdb(json_body) :
    try :
        # Done to extract item from the list
        data_set = json_body[0]
        data_set.items()

        # Gets measurement name
        measurement = data_set["measurement"]

        # Converts measurement name to type string
        measurement_str = str(measurement)

        # Builds query string with function "influxdb_query_builder(data_field_label)"
        query = influxdb_query_builder(measurement_str)

        previous_db_entry = influxdb_client.query(query)  # Query last DB entry with same type of measurement name
        previous_points = previous_db_entry.get_points()  # Convert to points

        for previous_point in previous_points :  # Iterate through points
            previous_timepoint = previous_point['time']  # sets the variable "previous_timepoint" to whatever the last timepoint value is
            previous_timepoint_str = str(previous_timepoint)  # Convert timepoint value to type string

        # Pass if previous_point_str == latest_timepoint_str evaluates to True
        # This means a value is already there adn we do not want to overwrite it with a new value which is likely to be 0.0
        if previous_timepoint_str == data_set["time"] :
            print("Data for " + measurement_str +
                  " already exists for this timepoint so program will not write to InfluxDB.")
            pass

        else :
            influxdb_client.write_points(json_body)  # Write to InfluxDB
            print(json_body)  # Debugging print statement

    # Should only be executed if Database is new and empty
    except :
        influxdb_client.write_points(json_body)
        print(json_body)


# Initialize database
_init_influxdb_database()
