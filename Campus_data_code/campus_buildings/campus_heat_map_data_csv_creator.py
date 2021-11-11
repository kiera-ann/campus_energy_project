'''Program to generate new CSV of building URLs at Princeton. Needed since PU Facilities often update/make changes to BL_ID.'''

import requests
import datetime
import pandas as pd
import os

# Sets width of run window to view all data
desired_width = 10000
pd.set_option('display.width' , desired_width)
pd.set_option('display.max_columns' , None)
# pd.set_option('display.width', None)
pd.set_option('display.max_rows' , None)


# Function to generate ArcGIS REST Services API call
# API Page Information
# Fields:
# OBJECTID ( type: esriFieldTypeOID, alias: OBJECTID )
# BL_ID ( type: esriFieldTypeString, alias: BL_ID, length: 8 )
# PU_R25_NAME ( type: esriFieldTypeString, alias: PU_R25_NAME, length: 72 )
# MAP_NAME ( type: esriFieldTypeString, alias: MAP_NAME, length: 72 )
# ENERGYTIMESTAMP ( type: esriFieldTypeDate, alias: ENERGYTIMESTAMP, length: 8 )
# ELECTRIC_KWATT ( type: esriFieldTypeDouble, alias: ELECTRIC_KWATT )
# ELECTRIC_KWH ( type: esriFieldTypeDouble, alias: ELECTRIC_KWH )
# CHW_FLOW ( type: esriFieldTypeDouble, alias: CHW_FLOW )
# CHW_TOTAL ( type: esriFieldTypeDouble, alias: CHW_TOTAL )
# STEAM ( type: esriFieldTypeDouble, alias: STEAM )
# STEAM_TOTAL ( type: esriFieldTypeDouble, alias: STEAM_TOTAL )
# ELEC_LAPTOP ( type: esriFieldTypeDouble, alias: ELEC_LAPTOP )
# ELEC_HOUSE ( type: esriFieldTypeDouble, alias: ELEC_HOUSE )
# SHAPE ( type: esriFieldTypeGeometry, alias: SHAPE )
# USE1 ( type: esriFieldTypeString, alias: USE1, length: 32 )
# COLLEGE ( type: esriFieldTypeString, alias: COLLEGE, length: 32 )
# IMAGEPATH ( type: esriFieldTypeString, alias: IMAGEPATH, length: 45 )

def campus_building_api_generator(BL_ID_var) :
    api_url_part_1 = "https://princeton_campus_building_api_here"
    building_id = str(BL_ID_var)
    api_url_part_2 = "&outFields="
    api_url_fields_of_interest = "BL_ID,PU_R25_NAME,MAP_NAME,ENERGYTIMESTAMP,ELECTRIC_KWATT,ELECTRIC_KWH,CHW_FLOW,CHW_TOTAL,STEAM,STEAM_TOTAL,USE1," \
                                 "COLLEGE,IMAGEPATH"
    api_url_part_3 = "&returnGeometry=false&f=json"

    pu_campus_api_url_call = api_url_part_1 + building_id + api_url_part_2 + api_url_fields_of_interest + api_url_part_3
    return (pu_campus_api_url_call)


# print(campus_building_api_generator("1"))


def get_campus_url_links() :
    for i in range(1 , 1500) :
        try :
            number = str(i)
            # print(campus_building_api_generator(number))
            url = str(campus_building_api_generator(number))
            building_url_data = requests.get(str(campus_building_api_generator(number)))
            building_json_data = building_url_data.json()
            # print(building_json_data)
            building_features_attributes_data = building_json_data['features'][0]['attributes']
            # print(building_features_attributes_data)
            BL_ID = building_features_attributes_data['BL_ID']
            # print(BL_ID)
            PU_R25_NAME = building_features_attributes_data['PU_R25_NAME']
            # print(PU_R25_NAME)
            MAP_NAME = building_features_attributes_data['MAP_NAME']
            USE1 = building_features_attributes_data['USE1']
            COLLEGE = building_features_attributes_data['COLLEGE']
            # dict = {BL_ID : PU_R25_NAME}
            # print(dict)
            # data = {"BL_ID": [BL_ID], "PU_R25_NAME": [PU_R25_NAME]}
            # data = {"BL_ID": [BL_ID], "PU_R25_NAME": [PU_R25_NAME], "API URL": url}
            # data = {"BL_ID" : [BL_ID] , "PU_R25_NAME" : [PU_R25_NAME], "USE1" : [USE1], "COLLEGE": [COLLEGE]}
            data = { "BL_ID" : [BL_ID] , "PU_R25_NAME" : [PU_R25_NAME] , "MAP_NAME" : [MAP_NAME] , "USE1" : [USE1] , "COLLEGE" : [COLLEGE] ,
                     "API URL" : url }
            df = pd.DataFrame(data)
            print(df)
            #
            # # if file does not exist write header
            if not os.path.isfile(
                    'campus_building_type_data_url_rev_4_26_2021.csv') :
                df.to_csv(
                    'campus_building_type_data_url_rev_4_26_2021.csv' ,
                    index=False)
            else :  # else it exists so append without writing the header
                df.to_csv(
                    'campus_building_type_data_url_rev_4_26_2021.csv' ,
                    mode='a' , header=False , index=False)
            #
            # # campus_building_data_test.csv
            # # campus_building_data_url_test.csv
            # # campus_building_type_test.csv
        except :
            pass


print(get_campus_url_links())
