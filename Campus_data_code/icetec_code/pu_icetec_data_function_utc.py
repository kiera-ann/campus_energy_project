''' Function to parse Icetec data from Icetec API. Returns list of all fields in "cov" parameter in  API response. '''

import requests
import pandas as pd


# Function to get icetec data from Icetec API
def get_icetec_pu_data_function() :
    list_of_data = []  # initialize list
    pu_icetec_tigerenergy_data = requests.get("https://icetec_api_here")

    # Create json of url response
    pu_icetec_tigerenergy_data_json = pu_icetec_tigerenergy_data.json()
    # print(pu_icetec_tigerenergy_data_json)

    # Get first data in "cov" of json data; Just for testing purposes
    # pu_icetec_tigerenergy_data_cov_json = pu_icetec_tigerenergy_data_json['cov'][0]
    # print(pu_icetec_tigerenergy_data_cov_json)

    # Get data in "cov" of json data
    for i in range(len(pu_icetec_tigerenergy_data_json['cov'])) :
        # Get i number in list of cov data and assign to variable "pu_icetec_tigerenergy_data_cov_json"
        pu_icetec_tigerenergy_data_cov_json = pu_icetec_tigerenergy_data_json['cov'][i]

        # Extract relevanty information from "pu_icetec_tigerenergy_data_cov_json"
        units = pu_icetec_tigerenergy_data_cov_json['eng']
        data_field_label = pu_icetec_tigerenergy_data_cov_json['path']
        timestamp_string_raw = pu_icetec_tigerenergy_data_cov_json['tstamp']
        temp_time_var = pd.to_datetime(timestamp_string_raw)  # Icetec gives timestamp in EST so I need to convert to UTC
        # print(temp_time_var)
        # temp_time_var_est = temp_time_var.tz_localize('US/Eastern')  # Localize to EST
        temp_time_var_utc = temp_time_var.tz_convert('UTC')  # Convert to UTC
        temp_time_car_utc_dt = pd.Timestamp.to_pydatetime(temp_time_var_utc)  # Return the data as an array of native Python datetime objects.
        ENERGYTIMESTAMP_dt = temp_time_car_utc_dt
        timestamp_string = ENERGYTIMESTAMP_dt.strftime('%Y-%m-%dT%H:%M:%SZ')  # Convert to datetime string format
        # print(timestamp_string)

        data_value = float(pu_icetec_tigerenergy_data_cov_json['value'])

        summary_data_dict = { "data_field_label" : data_field_label ,
                              "units" : units ,
                              "timestamp" : timestamp_string ,
                              "value" : data_value }

        list_of_data.append(summary_data_dict)

    return (list_of_data)


# get_icetect_pu_data_function()
# print(get_icetec_pu_data_function())
# print(len(get_icetec_pu_data_function()))
