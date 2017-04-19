import json
import googlemaps
import pandas as pd
import numpy as np
import openpyxl
from datetime import datetime
from pprint import pprint
#pprint(result) can print the result in a more pretty way


def re_geocoding(lat, lon):
    """Fetches the address of a location using Google reverse geocoding API.

    Input the latitude and longitude of a location. Return a dictionary including
    the address components such as route, street number, postal code, country etc.
    Note: the lat and lon variable shoould be interger, which means both of these
    two variables are ----E7 types.

    Args:
        lat: an integer number represents the latitude of a location.
        lon: an integer number represents the longitude of a location.

    Returns:
        A dictionary that contains the following address components:
            'route',
            'street_number',
            'postal_code',
            'administrative_area_level_2',
            'administrative_area_level_1' ,
            'country'.
    """

    # Set the appliaction key and call the reverse_geocode API
    gmaps = googlemaps.Client(key='AIzaSyCGwr54FPosQvvW2YPYONUtAgdMA6scE2M')
    result = gmaps.reverse_geocode((float(lat)/10000000, float(lon)/10000000),
                                   result_type = 'street_address')

    # Initailization of variables
    result_location = {}    # Dictionaty
    address_components = []    # List

    for loop in result:
        address_components = loop.get("address_components")
        break
    for loop_1 in address_components:
        result_location[loop_1.get("types")[0]] = loop_1.get("long_name")

    return result_location

# Input the json file downloaded from Google Takeout
# URL: https://takeout.google.com/settings/takeout/custom
json_file = open('LocationHistory.json')
json_string = json_file.read()
json_data = json.loads(json_string)
locations = json_data["locations"]

# Initailization the  variable of result
result_table = pd.DataFrame() # Pandas data frame

for location in locations:
    # Extract UTC time from timestampMs
    UTC_time = datetime.fromtimestamp(
              int(location.get("timestampMs"))/1000
              ).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Get the address dictionary using the latitude and longitude value and
    # re_geocoding(lat, lon) function defined above
    location_detail = re_geocoding(location.get("latitudeE7"), location.get("longitudeE7"))

    # Filter empty location and useless entries which have missing postcode
    if (location_detail != {} and location_detail.has_key('postal_code')):
        result_table = result_table.append({
            'route': location_detail["route"],
            'street_number': location_detail["street_number"],
            'postal_code': location_detail["postal_code"],
            'administrative_area_level_2': location_detail["administrative_area_level_2"],
            'administrative_area_level_1': location_detail["administrative_area_level_1"],
            'country': location_detail["country"],
            'time': UTC_time},
            ignore_index=True)

# Re-order the column of the relust data frame
result_table = result_table[[
    'route',
    'street_number',
    'postal_code',
    'administrative_area_level_2',
    'administrative_area_level_1',
    'country',
    'time']]

# Write the result into a excel file, if you would like to write it into csv file,
# use result_table.to_csv('regeo.csv', sep=' ') instead
writer = pd.ExcelWriter('re_geo_output.xlsx')
result_table.to_excel(writer,'Sheet1')
writer.save()
