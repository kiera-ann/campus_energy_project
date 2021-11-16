'''Module to request Campus Building Data Parameters and write data into InfluxDB. '''

import time
from influxdb import InfluxDBClient
from datetime import datetime
import sys

# Custom Module
from Campus_data_code.campus_buildings.pandas_heat_map_data import PU_ArcGIS_REST_Services_API_data

# Module to Calculate Energy kilowatts per hour for all Campus Buildings
from Campus_data_code.campus_buildings.pu_building_energy_calculations import write_campus_building_energy_to_InfluxDB

# Module to Calculate Building Energy CO2 for all Campus Buildings
from Campus_data_code.co2_calculations.pu_building_energy_co2_calculations import write_recent_building_energy_co2_to_InfluxDB

# Module to Calculate Pounds of Steam for all Campus Buildings
from Campus_data_code.campus_buildings.pu_building_steam_calculations import write_campus_building_steam_to_InfluxDB

# Module to Calculate Heat CO2 for all Campus Buildings
from Campus_data_code.co2_calculations.campus_heat_calculations.pu_building_heat_co2_calculations import write_recent_building_heat_co2_to_InfluxDB

# For PU Campus Building database
INFLUXDB_ADDRESS = '140.180.133.81'  # Personal development Mac mini IP address
INFLUXDB_USER = 'admin'
INFLUXDB_PASSWORD = 'admin'
INFLUXDB_DATABASE = 'pu_arcgis_database_raw'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD , None)


# Initialize database
def _init_influxdb_database() :
    databases = influxdb_client.get_list_database()  # check if the database is there by using the get_list_database() function of the client:
    if len(list(filter(lambda x : x['name'] == INFLUXDB_DATABASE , databases))) == 0 :
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)  # we’ll set the client to use this database


# Function to parse building data into InfluxDB
def PU_ArcGIS_REST_Services_API_parse_to_database() :
    while True :
        try :
            print()
            time_now = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')  # For simple debugging or logging
            print(time_now)  # For simple debugging or logging

            list_of_newly_written_building_data = []  # initialize list; this is the list of data points that are new and now written into InfluxDB
            list_of_data = PU_ArcGIS_REST_Services_API_data()

            for i in range(0 , len(list_of_data)) :
                json_body = [
                    {
                        'measurement' : list_of_data[i]["PU_R25_NAME"] ,
                        'tags' : {
                            'source_of_data ' : "PU_ArcGIS_REST_Services_API" } ,
                        "time" : list_of_data[i]["ENERGYTIMESTAMP"] ,
                        'fields' : {
                            "BL_ID" : list_of_data[i]["BL_ID"] ,
                            "PU_R25_NAME" : list_of_data[i]["PU_R25_NAME"] ,
                            "ENERGYTIMESTAMP" : list_of_data[i]["ENERGYTIMESTAMP"] ,
                            "ELECTRIC_KWATT" : list_of_data[i]["ELECTRIC_KWATT"] ,
                            "ELECTRIC_KWH" : list_of_data[i]["ELECTRIC_KWH"] ,
                            "CHW_FLOW" : list_of_data[i]["CHW_FLOW"] ,
                            "CHW_TOTAL" : list_of_data[i]["CHW_TOTAL"] ,
                            "STEAM" : list_of_data[i]["STEAM"] ,
                            "STEAM_TOTAL" : list_of_data[i]["STEAM_TOTAL"]
                        }
                    }
                ]

                try :
                    # Code to check database to see if data already exists for this timepoint. If so, program will not write to InfluxDB
                    # Build query for database entry
                    # This check is to avoid writing a value to database if there is no need since value is already written
                    query_p1 = 'SELECT "ELECTRIC_KWH" FROM "pu_arcgis_database_raw"."autogen".'
                    query_p2 = '"'
                    query_p3 = list_of_data[i]["PU_R25_NAME"]
                    query_p4 = '"'
                    query_p5 = " WHERE time > now() - 5m ORDER BY time DESC LIMIT 1"
                    full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)
                    previous_db_entry = influxdb_client.query(full_query_string)  # Query last DB entry with same type of measurement name
                    previous_points = previous_db_entry.get_points()  # Convert to points

                    for previous_point in previous_points :  # Iterate through points
                        previous_timepoint = previous_point['time']  # sets the variable "previous_timepoint" to whatever the last timepoint value is
                        previous_point_str = str(previous_timepoint)  # Convert timepoint value to type string

                    # Pass if previous_point_str == latest_timepoint_str evaluates to True
                    # This means a value with the same timestamp is already in the database and we do not want to overwrite it with a new value
                    if previous_point_str == list_of_data[i]["ENERGYTIMESTAMP"] :
                        print("Data for " + str(list_of_data[i]["PU_R25_NAME"]) +
                              " already exists for this timepoint so program will not write to InfluxDB.")
                        pass

                    else :
                        influxdb_client.write_points(json_body)  # Write to new data to InfluxDB

                        # Appends list with name of data sets that are new for later post processing
                        list_of_newly_written_building_data.append(list_of_data[i]["PU_R25_NAME"])
                        print(json_body)  # Debugging print statement

                # Handles KeyboardInterrupt exception
                except KeyboardInterrupt :
                    sys.exit()  # quit

                except :
                    # In the event code has been down for some time, there will be a large gap time data or missing data completely
                    # So there is a need to write data to influxDB
                    influxdb_client.write_points(json_body)
                    print(json_body)  # Debugging print statement

            print(list_of_newly_written_building_data)  # Debugging print statement
            try :
                for building in list_of_newly_written_building_data :
                    # Energy Related Building Calculations
                    write_campus_building_energy_to_InfluxDB(building)  # Calculates Building Energy Use
                    write_recent_building_energy_co2_to_InfluxDB(building)  # Calculates Building CO2 related to Energy Use

                    # Heat Related Building Calculations
                    write_campus_building_steam_to_InfluxDB(building)  # Calculates Building Steam Use
                    write_recent_building_heat_co2_to_InfluxDB(building)  # Calculates Heat CO2 related to Energy Use

            # Handles KeyboardInterrupt exception
            except KeyboardInterrupt :
                sys.exit()  # quit

            except :
                print("passed")
                pass
            time.sleep(30)

        # Handles KeyboardInterrupt exception
        except KeyboardInterrupt :
            sys.exit()  # quit

        # Handles other issues with getting data from Princeton ArcGIS_REST_Services_API
        except :
            print()
            time_now_except = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')  # For simple debugging or logging
            print(time_now_except)  # For simple debugging or logging
            print("Failed to get data from PU_ArcGIS_REST_Services.")
            print("Will try again soon...")
            time.sleep(30)
            print()
            continue


def main() :
    _init_influxdb_database()  # Initialize database
    PU_ArcGIS_REST_Services_API_parse_to_database()  # Function to parse building data into InfluxDB


if __name__ == '__main__' :
    print('PU_ArcGIS_REST_Services Data to InfluxDB')
    main()
