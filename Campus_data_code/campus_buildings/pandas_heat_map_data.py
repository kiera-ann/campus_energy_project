'''Function to get Campus Building data using ArcGIS_REST_Services_API. '''

import pandas as pd
import requests
import pytz
import time

# Name of file with campus URL Data
pu_heatmap_csv_filename = "campus_building_type_data_url_rev_4_26_2021.csv"

# Eastern Timezone
new_tz = pytz.timezone('US/Eastern')


# Function to get Campus Building data
def PU_ArcGIS_REST_Services_API_data() :
    try :
        list_of_data = []  # initialize list
        df = pd.read_csv(pu_heatmap_csv_filename , sep=',')
        building_url_data = df['API URL']

        # loop through data for URL
        for i in range(0 , len(building_url_data)) :
            try :
                building_url = str(building_url_data[i])
                building_url_data_request = requests.get(building_url)

                # Create json of url response
                building_json = building_url_data_request.json()
                # Get "attributes" of "features" of json data
                building_attributes_json = building_json['features'][0]['attributes']

                BL_ID = building_attributes_json['BL_ID']  # BL_ID
                PU_R25_NAME = building_attributes_json['PU_R25_NAME']  # PU_R25_NAME
                ENERGYTIMESTAMP_raw = building_attributes_json['ENERGYTIMESTAMP']  # ENERGYTIMESTAMP

                # Returns data of type <class 'pandas._libs.tslibs.timestamps.Timestamp'>
                temp_time_var = pd.to_datetime(ENERGYTIMESTAMP_raw ,
                                               unit='ms')  # Convert Data using Pandas Timestamp unit = "ms"; data has no timezone attached

                temp_time_var_est = temp_time_var.tz_localize('US/Eastern')  # Localize to EST
                temp_time_var_utc = temp_time_var_est.tz_convert('UTC')  # Localize to UTC
                temp_time_car_utc_dt = pd.Timestamp.to_pydatetime(temp_time_var_utc)  # Return the data as an array of native Python datetime objects.
                ENERGYTIMESTAMP_dt = temp_time_car_utc_dt
                ENERGYTIMESTAMP = ENERGYTIMESTAMP_dt.strftime('%Y-%m-%dT%H:%M:%SZ')  # Need to convert datetime to string for InfluxDB Write points

                ELECTRIC_KWATT = building_attributes_json['ELECTRIC_KWATT']  # ELECTRIC_KWATT
                ELECTRIC_KWH = building_attributes_json['ELECTRIC_KWH']  # ELECTRIC_KWH
                CHW_FLOW = building_attributes_json['CHW_FLOW']  # CHW_FLOW
                CHW_TOTAL = building_attributes_json['CHW_TOTAL']  # CHW_TOTAL
                STEAM = building_attributes_json['STEAM']  # STEAM
                STEAM_TOTAL = building_attributes_json['STEAM_TOTAL']  # STEAM_TOTAL

                data_dict = { "BL_ID" : BL_ID ,
                              "PU_R25_NAME" : PU_R25_NAME ,
                              "ENERGYTIMESTAMP" : ENERGYTIMESTAMP ,
                              "ELECTRIC_KWATT" : ELECTRIC_KWATT ,
                              "ELECTRIC_KWH" : ELECTRIC_KWH ,
                              "CHW_FLOW" : CHW_FLOW ,
                              "CHW_TOTAL" : CHW_TOTAL ,
                              "STEAM" : STEAM ,
                              "STEAM_TOTAL" : STEAM_TOTAL
                              }

                list_of_data.append(data_dict)

            except :
                pass

        return list_of_data


    except :
        time.sleep(10)
        print("Failed to get data from API call.")
