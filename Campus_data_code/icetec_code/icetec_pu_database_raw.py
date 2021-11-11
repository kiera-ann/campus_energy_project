# encoding=utf8
import sys
import time
from datetime import datetime
# from Campus_data_code.pu_icetec_data_function import get_icetec_pu_data_function  # Uses icetec time which is not UTC

# Uses properly converted UTC time
from Campus_data_code.icetec_code.pu_icetec_data_function_utc import get_icetec_pu_data_function

# Calculates CO2 from Cogen Turbines
from Campus_data_code.co2_calculations.cogen_turbine_co2_calculations import write_cogen_turbine_co2_to_InfluxDB

# Calculates Energy from Cogen Turbines
from Campus_data_code.campus_energy_calculations.pu_cogen_turbine_energy_calculations import write_cogen_turbine_energy_to_InfluxDB

# Calculates Energy from PJM/PSEG
from Campus_data_code.campus_energy_calculations.pu_grid_energy_calculations import write_campus_grid_energy_to_influxDB

# Calculates CO2 from PJM/PSEG
from PJM_code.general_pjm_code.pjm_query_database_co2_calc import write_campus_grid_co2_to_influxDB

# Calculates Energy from Solar.WindsorPV
from Campus_data_code.campus_energy_calculations.pu_solar_WindsorPV_energy_calculations import write_Solar_WindsorPV_energy_to_InfluxDB

# Function to calculate fraction of energy from different sources
from Campus_data_code.campus_energy_calculations.campus_energy_percent import campus_energy_source_division

# Calculates CO2 from Cogen Supplementary fired Duct Burner
from Campus_data_code.co2_calculations.cogen_duct_burner_co2_calculations import write_pu_cogen_duct_burner_co2_to_InfluxDB

# Calculates Energy from Cogen MicroTurbines
from Campus_data_code.cogen_generated_energy.cogen_microturbine.pu_cogen_microturbine_energy_calculations import write_cogen_microturbine_energy_to_InfluxDB

# Calculates CO2 from Cogen Auxiliary Boiler # 1
from Campus_data_code.co2_calculations.pu_cogen_aux_bioler_1_co2_calculations import write_pu_cogen_aux_bioler_1_co2_to_InfluxDB

# Calculates CO2 from Cogen Auxiliary Boiler # 2
from Campus_data_code.co2_calculations.pu_cogen_aux_bioler_2_co2_calculations import write_pu_cogen_aux_bioler_2_co2_to_InfluxDB

# Calculates Pounds of Steam produced in Princeton's Cogen Facility
from Campus_data_code.co2_calculations.campus_heat_calculations.pu_cogen_heat_calculations import write_cogen_total_steam_to_InfluxDB

# Function to calculate most recent total kiloWatts per hour for Princeton's Campus
from Campus_data_code.campus_energy_calculations.pu_campus_energy_calculations import write_recent_total_campus_energy_to_InfluxDB

# Calculates Total CO2 for Princeton Campus
from Campus_data_code.co2_calculations.pu_campus_co2_calculations import write_recent_total_campus_co2_to_InfluxDB

# Calculates Total Energy CO2 for Princeton Campus
from Campus_data_code.co2_calculations.pu_campus_energy_co2_calculations import write_recent_total_campus_energy_co2_to_InfluxDB

# Calculates Total Heat CO2 for Princeton Campus
from Campus_data_code.co2_calculations.campus_heat_calculations.pu_campus_heat_co2_calculations import write_recent_total_campus_heat_co2_to_InfluxDB

# Calculates the most recent energy emission data to InfluxDB
from Campus_data_code.co2_calculations.campus_heat_calculations.pu_campus_energy_emission_rate_calculations import write_recent_energy_emission_rate_to_InfluxDB

# Import InfluxDB Module
from influxdb import InfluxDBClient

INFLUXDB_ADDRESS = '140.180.133.81'  # Personal development Mac mini IP address
INFLUXDB_USER = 'admin'
INFLUXDB_PASSWORD = 'admin'
INFLUXDB_DATABASE = 'pu_icetec_database_raw'

# http://localhost:8086

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS , 8086 , INFLUXDB_USER , INFLUXDB_PASSWORD , None)


def _init_influxdb_database() :
    databases = influxdb_client.get_list_database()  # check if the database is there by using the get_list_database() function of the client:
    if len(list(filter(lambda x : x['name'] == INFLUXDB_DATABASE , databases))) == 0 :
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)  # we’ll set the client to use this database


def icetec_parse_function_api() :
    while True :
        try :
            print()
            time_now = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')  # For simple debugging or logging
            print(time_now)  # For simple debugging or logging

            list_of_newly_written_data = []  # initialize list; this is the list of data points that are new and now written into InfluxDB
            delta_energy = False  # Tag to determine if tally of energy has to be updated; initially set to False
            delta_co2 = False  # Tag to determine if tally of CO2 has to be updated; initially set to False
            delta_heat_co2 = False  # Tag to determine if tally of CO2 for heat has to be updated; initially set to False
            delta_energy_co2 = False  # Tag to determine if tally of CO2 for energy has to be updated; initially set to False
            # delta_heat = False  # Unsure of use yet

            list_of_data = get_icetec_pu_data_function()
            # print(list_of_data)   # For simple debugging or logging

            # Send to function to calculate fraction/percent of energy from different sources
            campus_energy_source_division(list_of_data)

            print("Icetec Data Parsed")     # Debugging print statement

            # Loop through elements in list_of_data received from Icetec API call
            for i in range(0 , len(list_of_data)) :
                if (list_of_data[i]["data_field_label"] == "EP.Totals.Power.i.Solar_kW") \
                        or (list_of_data[i]["data_field_label"] == "EP.Power.Solar.WindsorPV.pm8600.kW") \
                        or (list_of_data[i]["data_field_label"] == "EP.Power.Solar.FrickPV.Main.Total_kW"):
                # if list_of_data[i]["data_field_label"] == "EP.Power.Solar.WindsorPV.Ion7550.i.Total_kW" :  # Old API
                    is_renewable_var = True
                else :
                    is_renewable_var = False

                json_body = [
                    {
                        'measurement' : list_of_data[i]["data_field_label"] ,
                        'tags' : {
                            'source_of_data' : "icetec_tigerenergy_api" ,
                            'units' : list_of_data[i]["units"] ,
                            'is_renewable' : is_renewable_var ,
                        } ,
                        "time" : list_of_data[i]["timestamp"] ,
                        # "time" : "2020-09-30T17:00:00Z" ,
                        'fields' : {
                            'value' : list_of_data[i]["value"] ,
                        }
                    }
                ]

                try:
                    # Done to extract item from the list
                    data_set = json_body[0]
                    data_set.items()

                    # Build query for database entry
                    # This check is to avoid writing a value to database if there is no need since value is already written
                    query_p1 = 'SELECT "value" FROM "pu_icetec_database_raw"."autogen".'
                    query_p2 = '"'
                    query_p3 = list_of_data[i]["data_field_label"]
                    query_p4 = '"'
                    query_p5 = " WHERE time > now() - 1m ORDER BY time DESC LIMIT 1"
                    full_query_string = str(query_p1 + query_p2 + query_p3 + query_p4 + query_p5)
                    # print(full_query_string)    # Debugging print statement

                    previous_db_entry = influxdb_client.query(full_query_string)  # Query last DB entry with same type of measurement name
                    previous_points = previous_db_entry.get_points()  # Convert to points

                    for previous_point in previous_points :  # Iterate through points
                        previous_timepoint = previous_point['time']  # sets the variable "previous_timepoint" to whatever the last timepoint value is
                        # print(previous_timepoint)    # Debugging print statement
                        # print(type(previous_point))  # Seems to be dictionary type
                        previous_point_str = str(previous_timepoint)  # Convert timepoint value to type string

                    # Pass if previous_point_str == latest_timepoint_str evaluates to True
                    # This means a value with the same timestamp is already in the database and we do not want to overwrite it with a new value
                    if previous_point_str == list_of_data[i]["timestamp"] :
                        print("Data for " + str(list_of_data[i]["data_field_label"]) +
                              " already exists for this timepoint so program will not write to InfluxDB.")
                        pass

                    else :
                        # Write to new data to InfluxDB
                        influxdb_client.write_points(json_body)

                        # Appends list with name of data sets that are new for later post processing
                        list_of_newly_written_data.append(data_set["measurement"])
                        print(json_body)

                except :
                    # In the event code has been down for some time, there will be a large gap time data or missing data completely
                    # So there is a need to write data to influxDB
                    influxdb_client.write_points(json_body)
                    # print("Data not written in a while so will only write to InfluxDB alone.")      # Debugging print statement
                    print(json_body)  # Debugging print statement

            # Functions to calculate CO2 and Energy Data and input into InfluxDB
            # print(list_of_newly_written_data)  # Debugging print statement
            # Calculates CO2 from Cogen Turbine and writes that data to InfluxDB
            if "EP.Cogen.Turbine.FUEL.i.GasFlow_dthr" in list_of_newly_written_data :
                write_cogen_turbine_co2_to_InfluxDB()
                delta_co2 = True  # There was a change to CO2 so a new tally of campus CO2 needs to be calculated
                delta_energy_co2 = True

            # Calculates Energy from Cogen Turbine and writes that data to InfluxDB
            if "EP.Cogen.Turbine.Power.ION.Total_kW" in list_of_newly_written_data :
                write_cogen_turbine_energy_to_InfluxDB()
                delta_energy = True  # There was a change to energy so a new tally of campus energy needs to be calculated


            # Calculates Energy from PSEG Grid and writes that data to InfluxDB
            if "EP.Totals.Power.i.Import_kW" in list_of_newly_written_data :
                write_campus_grid_energy_to_influxDB()
                delta_energy = True  # There was a change to energy so a new tally of campus energy needs to be calculated

                # Calculates CO2 from PSEG Grid and writes that data to InfluxDB
                write_campus_grid_co2_to_influxDB()
                delta_co2 = True  # There was a change to CO2 so a new tally of campus CO2 needs to be calculated
                delta_energy_co2 = True

            # Calculates Energy from Solar.WindsorPV and writes that data to InfluxDB
            # if "EP.Totals.Power.i.Solar_kW" in list_of_newly_written_data :  # Solar API
            if "EP.Totals.Power.i.Solar_kW" in list_of_newly_written_data :
                write_Solar_WindsorPV_energy_to_InfluxDB()  # old solar API name
                delta_energy = True  # There was a change to energy so a new tally of campus energy needs to be calculated

            # Calculates Energy from Cogen Microturbine and writes that data to InfluxDB
            if "EP.Totals.Power.i.MicroTurb_kW" in list_of_newly_written_data :
                write_cogen_microturbine_energy_to_InfluxDB()
                delta_energy = True  # There was a change to energy so a new tally of campus energy needs to be calculated

            # Calculates CO2 from Cogen Supplementary fired Duct Burner and writes that data to InfluxDB
            if "EP.Cogen.DB.i.Gas_dthr" in list_of_newly_written_data :
                write_pu_cogen_duct_burner_co2_to_InfluxDB()
                delta_co2 = True  # There was a change to CO2 so a new tally of campus CO2 needs to be calculated
                delta_heat_co2 = True

            # Calculates CO2 from Cogen Auxiliary Bioler # 1 and writes that data to InfluxDB
            if "EP.BLRS.01.i.GasFlow_dthr" in list_of_newly_written_data :
                write_pu_cogen_aux_bioler_1_co2_to_InfluxDB()
                delta_co2 = True  # There was a change to CO2 so a new tally of campus CO2 needs to be calculated
                delta_heat_co2 = True

            # Calculates CO2 from Cogen Auxiliary Bioler # 2 and writes that data to InfluxDB
            if "EP.BLRS.02.i.GasFlow_dthr" in list_of_newly_written_data :
                write_pu_cogen_aux_bioler_2_co2_to_InfluxDB()
                delta_co2 = True  # There was a change to CO2 so a new tally of campus CO2 needs to be calculated
                delta_heat_co2 = True

            # Calculates Pounds of Steam produced on Campus for all heating and writes that data to InfluxDB
            if "EP.Totals.Steam.i.Campus_pph" in list_of_newly_written_data :
                write_cogen_total_steam_to_InfluxDB()
                # delta_heat = True  # There was a change to the pounds of steam produced so a new tally of campus steam needs to be calculated

            # Determine if either delta_energy or delta_co2 is True and if so, perform some new tallies so building level data is compared to new data
            if delta_energy == True :
                # print("delta_energy == True")       # Debugging print statement
                write_recent_total_campus_energy_to_InfluxDB()

            # Calculates new Total Campus CO2 if value of delta_co2 is True
            if delta_co2 == True :
                # print("delta_co2 = True")       # Debugging print statement
                write_recent_total_campus_co2_to_InfluxDB()

            # Calculates new Total Energy CO2 if value of delta_co2 is True
            # Also calculates new energy use emissions (pounds CO2/KWH)
            if delta_energy_co2 == True :
                # print("delta_energy_co2 == True")       # Debugging print statement
                write_recent_total_campus_energy_co2_to_InfluxDB()
                # Calculates new energy use emissions (pounds CO2/KWH)
                write_recent_energy_emission_rate_to_InfluxDB()

            # Calculates new Total Heat CO2 if value of delta_co2 is True
            if delta_heat_co2 == True :
                # print("delta_heat_co2 == True")     # Debugging print statement
                write_recent_total_campus_heat_co2_to_InfluxDB()

            time.sleep(20)
            # print()

        # Handles KeyboardInterrupt exception
        except KeyboardInterrupt :
            # quit
            sys.exit()

        # Handles other issues with getting data from Icetec API
        except :
            print()
            time_now_except = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')  # For simple debugging or logging
            print(time_now_except)  # For simple debugging00 or logging
            print("Failed to collect Icetec data...")
            print("Will try again soon...")
            time.sleep(20)
            print()

            continue


def main() :
    _init_influxdb_database()
    icetec_parse_function_api()


if __name__ == '__main__' :
    print('Icetec Data to InfluxDB')
    main()

# print(icetec_parse_function_api())
