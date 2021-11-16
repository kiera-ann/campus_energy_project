from influxdb import InfluxDBClient
import time
import sys
from datetime import datetime
from PJM_code.general_pjm_code.pjm_data_parse import pjm_parse_data_function

INFLUXDB_ADDRESS = '140.180.133.81'  # Personal development Mac mini IP address
INFLUXDB_USER = 'admin'
INFLUXDB_PASSWORD = 'admin'
INFLUXDB_DATABASE = 'pjm_database_raw'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD , None)


def _init_influxdb_database() :
    databases = influxdb_client.get_list_database()  # check if the database is there by using the get_list_database() function of the client:
    if len(list(filter(lambda x : x['name'] == INFLUXDB_DATABASE , databases))) == 0 :
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)  # we’ll set the client to use this database


def pjm_parse_function_api() :
    while True :
        try :
            print()
            time_now = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')  # For simple debugging or logging
            print(time_now)  # For simple debugging or logging
            list_of_data , summary_data_dict = pjm_parse_data_function()
            for i in range(0 , len(list_of_data)) :
                json_body = [
                    {
                        'measurement' : list_of_data[i]["fuel_type"] ,
                        'tags' : {
                            'is_renewable' : list_of_data[i]["is_renewable"] ,
                            'source_of_data' : "pjm_personal_api"
                        } ,
                        "time" : list_of_data[i]["datetime_beginning_utc"] ,
                        'fields' : {
                            'value_mw' : list_of_data[i]["mw"] ,
                            'value_mw_pct' : list_of_data[i]["fuel_percentage_of_total"] ,
                            'CO2 metric tons' : list_of_data[i]["CO2 metric tons"]
                        }
                    }
                ]
                try :
                    # Code to check database to see if data already exists for this timepoint. If so, program will not write to InfluxDB
                    # Build query for database entry
                    # This check is to avoid writing a value to database if there is no need since value is already written
                    query_p1 = 'SELECT "value_mw" FROM "pjm_database_raw"."autogen".'
                    query_p2 = '"'
                    query_p3 = list_of_data[i]["fuel_type"]
                    query_p4 = '"'
                    query_p5 = " WHERE time > now() - 12h ORDER BY time DESC LIMIT 1"
                    full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)
                    previous_db_entry = influxdb_client.query(full_query_string)  # Query last DB entry with same type of measurement name
                    previous_points = previous_db_entry.get_points()  # Convert to points

                    for previous_point in previous_points :  # Iterate through points
                        previous_timepoint = previous_point['time']  # sets the variable "previous_timepoint" to whatever the last timepoint value is
                        previous_point_str = str(previous_timepoint)  # Convert timepoint value to type string

                    # Pass if previous_point_str == latest_timepoint_str evaluates to True
                    # This means a value with the same timestamp is already in the database and we do not want to overwrite it with a new value
                    if previous_point_str == list_of_data[i]["datetime_beginning_utc"] :
                        print("Data for " + str(list_of_data[i]["fuel_type"]) +
                              " already exists for this timepoint so program will not write to InfluxDB.")
                        pass

                    else :
                        influxdb_client.write_points(json_body)  # Write new data to InfluxDB
                        print(json_body)

                except :
                    influxdb_client.write_points(json_body)
                    print(json_body)

            json_body_2 = [
                {
                    'measurement' : "Power Grid Summary" ,
                    'tags' : {
                        'source_of_data' : "pjm_personal_api"
                    } ,
                    "time" : summary_data_dict["datetime_beginning_utc"] ,
                    'fields' : {
                        'total_mw' : summary_data_dict["total_mw"] ,
                        'total_mw_renewable' : summary_data_dict["total_mw_renewable"] ,
                        'total_percent_renewable' : summary_data_dict["total_percent_renewable"] ,
                        'total_mw_nonrenewable' : summary_data_dict["total_mw_nonrenewable"] ,
                        'total_percent_nonrenewable' : summary_data_dict["total_percent_nonrenewable"] ,
                        'total_co2 (metric tons)' : summary_data_dict["total_co2 (metric tons)"] ,
                        'emission_efficiency' : summary_data_dict["emission_efficiency"]
                    }
                }
            ]

            try :
                # Code to check database to see if data already exists for this timepoint. If so, program will not write to InfluxDB
                # Build query for database entry
                # This check is to avoid writing a value to database if there is no need since value is already written
                query_p1 = 'SELECT "total_mw" FROM "pjm_database_raw"."autogen".'
                query_p2 = '"'
                query_p3 = "Power Grid Summary"
                query_p4 = '"'
                query_p5 = " WHERE time > now() - 12h ORDER BY time DESC LIMIT 1"
                full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)
                previous_db_entry = influxdb_client.query(full_query_string)  # Query last DB entry with same type of measurement name
                previous_points = previous_db_entry.get_points()  # Convert to points

                for previous_point in previous_points :  # Iterate through points
                    previous_timepoint = previous_point['time']  # sets the variable "previous_timepoint" to whatever the last timepoint value is
                    previous_point_str = str(previous_timepoint)  # Convert timepoint value to type string

                # Pass if previous_point_str == latest_timepoint_str evaluates to True
                # This means a value with the same timestamp is already in the database and we do not want to overwrite it with a new value
                if previous_point_str == summary_data_dict["datetime_beginning_utc"] :
                    print("Data for " + str("Power Grid Summary") +
                          " already exists for this timepoint so program will not write to InfluxDB.")
                    pass

                else :
                    influxdb_client.write_points(json_body_2)  # Write new data to InfluxDB
                    print(json_body_2)
            except :
                influxdb_client.write_points(json_body_2)
                print(json_body_2)

            time.sleep(120)  # CHeck every 2 minutes for an update

        # Handles KeyboardInterrupt exception
        except KeyboardInterrupt :
            sys.exit()  # quit

        # Handles other issues with getting data from PJM API
        except :
            print()
            time_now_except = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')  # For simple debugging or logging
            print(time_now_except)  # For simple debugging or logging
            print("Failed to get data from PJM API.")
            print("Will try again soon...")
            time.sleep(120)
            print()
            continue


def main() :
    _init_influxdb_database()
    pjm_parse_function_api()


if __name__ == '__main__' :
    print('PJM Data to InfluxDB')
    main()
