import requests
import pandas as pd  # For handling timestamps
from PJM_code.general_pjm_code.pjmapiurlgenerator import pjm_api_call  # Personal module import
from PJM_code.general_pjm_code.PJM_NJ_CO2_calculator import PJM_NJ_CO2_per_MWh


# Request PJM JSON Data from API
# Returns JSON Data
def getpjmjsondata() :
    pjm_data = requests.get(pjm_api_call())
    pjm_data_json = pjm_data.json()
    pjm_data_json_items = pjm_data_json['items']
    return pjm_data_json_items


def pjm_parse_data_function() :
    list_of_data = []  # List of energy sources from PJM
    data_dict = { }
    summary_data_dict = { }
    total_mw = 0.0  # Total MW
    total_mw_renewable = 0.0  # Total Renewable MW
    total_percent_renewable = 0.0
    total_mw_nonrenewable = 0.0  # Total Non-Renewable MW
    total_percent_nonrenewable = 0.0
    total_co2 = 0.0

    # Makes a new request for PJM JSON Data using function 'getpjmjsondata()'
    energy_source_data_only = getpjmjsondata()

    # Code to get most recent set of 11 energy points
    last_count_from_api_data = len(energy_source_data_only)  # gets the greater number
    counts_needed_from_api_data = 11  # Number of energy points expected for a given time
    first_count_needed_from_api_data = last_count_from_api_data \
                                       - counts_needed_from_api_data  # Finds the difference of the greater number and the number expected

    # For loop to go through that data obtained from API request ***NOT USED ANYMORE BUT KEEPING FOR FUTURE USE***
    # Python does have a built-in reversed function. If you wrap range() inside reversed(), then you can print the integers in reverse order.
    for i in range(first_count_needed_from_api_data , last_count_from_api_data) :
        # Date time related code
        datetime_beginning_utc_raw = [item['datetime_beginning_utc'] for item in energy_source_data_only][i]
        temp_time_var = pd.to_datetime(datetime_beginning_utc_raw)
        temp_time_var_utc = temp_time_var.tz_localize('UTC')  # Localize to UTC
        temp_time_car_utc_dt = pd.Timestamp.to_pydatetime(temp_time_var_utc)  # Return the data as an array of native Python datetime objects.
        ENERGYTIMESTAMP_dt = temp_time_car_utc_dt
        datetime_beginning_utc = ENERGYTIMESTAMP_dt.strftime('%Y-%m-%dT%H:%M:%SZ')  # Convert to datetime string format
        fuel_type = [item['fuel_type'] for item in energy_source_data_only][i]
        fuel_type_lower = str(fuel_type).lower()
        fuel_percentage_of_total_as_received = [item['fuel_percentage_of_total'] for item in energy_source_data_only][i]
        fuel_percentage_of_total = (float(fuel_percentage_of_total_as_received) * 100)
        mw = [item['mw'] for item in energy_source_data_only][i]
        is_renewable = [item['is_renewable'] for item in energy_source_data_only][i]

        # Include CO2 log for each fuel type from MW produced
        CO2_dict = PJM_NJ_CO2_per_MWh()
        if fuel_type_lower in CO2_dict :
            data_dict = { "fuel_type" : fuel_type_lower ,
                          "is_renewable" : is_renewable ,
                          "datetime_beginning_utc" : datetime_beginning_utc ,
                          "mw" : mw ,
                          "fuel_percentage_of_total" : fuel_percentage_of_total ,
                          "CO2 metric tons" : round(float(mw * CO2_dict[fuel_type_lower]) , 1) }  # Calculate CO2 intensity of fuel

        else :
            data_dict = { "fuel_type" : fuel_type_lower ,
                          "is_renewable" : is_renewable ,
                          "datetime_beginning_utc" : datetime_beginning_utc ,
                          "mw" : mw ,
                          "fuel_percentage_of_total" : fuel_percentage_of_total ,
                          "CO2 metric tons" : 0.0 }  # Sets CO2 intensity to 0.0 for non-carbon producing fuels

        list_of_data.append(data_dict)

        if is_renewable == True :
            total_mw_renewable = total_mw_renewable + mw

        else :
            total_mw_nonrenewable = total_mw_nonrenewable + mw

        # Sums up the total MW for Percent Renewable/Non-renewable calculations
        total_mw = total_mw + mw

        # Calculate percents - more accurate than using PJM values
        total_percent_renewable = (total_mw_renewable / total_mw) * 100
        total_percent_nonrenewable = (total_mw_nonrenewable / total_mw) * 100

        # Rounds the float values to 1 decimal point
        total_percent_renewable = round(total_percent_renewable , 1)  # round to 1 decimal point
        total_percent_nonrenewable = round(total_percent_nonrenewable , 1)  # round to 1 decimal point

        for key , value in data_dict.items() :
            if key == "CO2 metric tons" :
                total_co2 = total_co2 + value

        # Data for Ted Borer at Princeton University
        # Determine/record metric ton CO2/MWH for each hour slot
        # Power Grid Hourly Emission Efficiency
        emission_efficiency = float(total_co2 / total_mw)
        emission_efficiency = round(emission_efficiency , 8)

        # Summary dictionary of data
        summary_data_dict = { "datetime_beginning_utc" : datetime_beginning_utc ,
                              "total_mw" : total_mw ,
                              "total_mw_renewable" : total_mw_renewable ,
                              "total_percent_renewable" : total_percent_renewable ,
                              "total_mw_nonrenewable" : total_mw_nonrenewable ,
                              "total_percent_nonrenewable" : total_percent_nonrenewable ,
                              "total_co2 (metric tons)" : total_co2 ,
                              "emission_efficiency" : emission_efficiency }

    return list_of_data , summary_data_dict
