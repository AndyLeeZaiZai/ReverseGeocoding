import json
import googlemaps
import pandas as pd
import numpy as np
import openpyxl
from datetime import datetime
from pprint import pprint
#pprint(result) can print the result in a more pretty way


def re_geocoding(lat, lon):
    gmaps = googlemaps.Client(key='AIzaSyCGwr54FPosQvvW2YPYONUtAgdMA6scE2M')
    result = gmaps.reverse_geocode((float(lat)/10000000, float(lon)/10000000), result_type = 'street_address')
    result_location = {}
    address_components = []

    for loop in result:
        address_components = loop.get("address_components")
        break
    for loop_1 in address_components:
        result_location[loop_1.get("types")[0]] = loop_1.get("long_name")

    return result_location


json_file = open('LocationHistory.json')
json_string = json_file.read()
json_data = json.loads(json_string)

locations = json_data["locations"]

result_table = pd.DataFrame()

for location in locations:
    UTC_time = datetime.fromtimestamp(
              int(location.get("timestampMs"))/1000
              ).strftime("%Y-%m-%dT%H:%M:%SZ")
    location_detail = re_geocoding(location.get("latitudeE7"), location.get("longitudeE7"))
    if (location_detail != {} and location_detail.has_key('postal_code')):
        result_table = result_table.append({'route': location_detail["route"],
                                            'street_number': location_detail["street_number"],
                                            'postal_code': location_detail["postal_code"],
                                            'administrative_area_level_2': location_detail["administrative_area_level_2"],
                                            'administrative_area_level_1': location_detail["administrative_area_level_1"],
                                            'time': UTC_time},
                                            ignore_index=True)
result_table = result_table[['route', 'street_number', 'postal_code', 'administrative_area_level_2', 'administrative_area_level_1', 'time']]

#result_table.to_csv('regeo.csv', sep=' ')
writer = pd.ExcelWriter('re_geo_output.xlsx')
result_table.to_excel(writer,'Sheet1')
writer.save()
