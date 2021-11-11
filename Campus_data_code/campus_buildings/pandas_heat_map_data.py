'''Function to get Campus Building data using ArcGIS_REST_Services_API. '''

import pandas as pd
import requests
import pytz
import time

# Name of file with campus URL Data
# pu_heatmap_csv_filename = "campus_building_type_data_url_final_2.csv"
# pu_heatmap_csv_filename = "campus_building_type_data_url_2.csv"
pu_heatmap_csv_filename = "campus_building_type_data_url_rev_4_26_2021.csv"

new_tz = pytz.timezone('US/Eastern')


# Function to get Campus Building data
def PU_ArcGIS_REST_Services_API_data() :
    try:
        list_of_data = []  # initialize list
        df = pd.read_csv(pu_heatmap_csv_filename , sep=',')

        building_url_data = df['API URL']
        # print(len(building_url_data))
        # print(building_url_data[0])

        # loop through data for URL
        for i in range(0 , len(building_url_data)) :
            try:
                building_url = str(building_url_data[i])
                # print(building_url)
                building_url_data_request = requests.get(building_url)

                # Create json of url response
                building_json = building_url_data_request.json()

                # Get "attributes" of "features" of json data
                building_attributes_json = building_json['features'][0]['attributes']
                # print(building_attributes_json)

                # BL_ID
                BL_ID = building_attributes_json['BL_ID']
                # print(BL_ID)

                # PU_R25_NAME
                PU_R25_NAME = building_attributes_json['PU_R25_NAME']
                # print(PU_R25_NAME)

                # ENERGYTIMESTAMP
                ENERGYTIMESTAMP_raw = building_attributes_json['ENERGYTIMESTAMP']
                # print(ENERGYTIMESTAMP_raw) # No longer needed if using Pandas Timestamp with unit = "ms"

                # Returns data of type <class 'pandas._libs.tslibs.timestamps.Timestamp'>
                temp_time_var = pd.to_datetime(ENERGYTIMESTAMP_raw ,
                                               unit='ms')  # Convert Data using Pandas Timestamp unit = "ms"; data has no timezone attached
                # print("temp_time_var")
                # print(temp_time_var.tzinfo)  # Return time zone info
                # print(temp_time_var.tz) # Return time zone info
                # print(temp_time_var.tz_localize('UTC'))

                temp_time_var_est = temp_time_var.tz_localize('US/Eastern')  # Localize to EST
                # print(temp_time_var_est)
                # print(temp_time_var.tz)
                temp_time_var_utc = temp_time_var_est.tz_convert('UTC')  # Localize to UTC
                # print(temp_time_var_utc)

                temp_time_car_utc_dt = pd.Timestamp.to_pydatetime(temp_time_var_utc)  # Return the data as an array of native Python datetime objects.
                # print(temp_time_car_utc_dt)

                # ENERGYTIMESTAMP_corrected = int(ENERGYTIMESTAMP_raw / 1000)  # No longer needed if using Pandas Timestamp with unit = "ms"
                # print(ENERGYTIMESTAMP_corrected)
                # ENERGYTIMESTAMP = datetime.fromtimestamp(ENERGYTIMESTAMP_corrected).strftime('%Y-%m-%dT%H:%M:%SZ')
                # print(ENERGYTIMESTAMP)

                ENERGYTIMESTAMP_dt = temp_time_car_utc_dt
                # print(ENERGYTIMESTAMP)
                # print(type(ENERGYTIMESTAMP))
                ENERGYTIMESTAMP = ENERGYTIMESTAMP_dt.strftime('%Y-%m-%dT%H:%M:%SZ')  # Need to convert datetime to string for InfluxDB Write points
                # print(ENERGYTIMESTAMP)
                # print(type(ENERGYTIMESTAMP))

                # ELECTRIC_KWATT
                ELECTRIC_KWATT = building_attributes_json['ELECTRIC_KWATT']
                # print(ELECTRIC_KWATT)

                # ELECTRIC_KWH
                ELECTRIC_KWH = building_attributes_json['ELECTRIC_KWH']
                # print(ELECTRIC_KWH)

                # CHW_FLOW
                CHW_FLOW = building_attributes_json['CHW_FLOW']
                # print(CHW_FLOW)

                # CHW_TOTAL
                CHW_TOTAL = building_attributes_json['CHW_TOTAL']
                # print(CHW_TOTAL)

                # STEAM
                STEAM = building_attributes_json['STEAM']
                # print(STEAM)

                # STEAM_TOTAL
                STEAM_TOTAL = building_attributes_json['STEAM_TOTAL']
                # print(STEAM_TOTAL)

                # # IMAGEPATH No need for this resource
                # IMAGEPATH = building_attributes_json['IMAGEPATH']
                # print(IMAGEPATH)
                # "IMAGEPATH" : IMAGEPATH

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
                # print(data_dict)      # Debugging print statement

                list_of_data.append(data_dict)

            except:
                pass

        return list_of_data


    except :
        time.sleep(10)
        print("Failed to get data from API call.")

# Function debugging
# print(PU_ArcGIS_REST_Services_API_data())
# print(len(PU_ArcGIS_REST_Services_API_data()))
