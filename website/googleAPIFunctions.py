#!/usr/bin/env python

# coding: utf-8

#Import packages
import urllib
import json
import re

#Read the Google API key stored in a file
with open ("googleAPIkey", "r") as myfile:
    googleAPIKey=myfile.readlines()

def googleDirections(origin,destination,mode):
    """This function takes an origin, a destination, and a mode of transportation
    and returns a result of a Google directions query as a json dict."""
    baseURL = 'https://maps.googleapis.com/maps/api/directions/json?'
    walkingURL = baseURL + 'origin=' + origin + '&destination=' + destination + '&mode=' + mode
    directions = json.loads(urllib.urlopen(walkingURL).read())
    return directions

#Example usage
#d = googleDirections('35 E 21st St, New York, NY', '308 Hemlock St, Brooklyn, NY', 'walking')

def getDirectionsDistance(dirJSON):
    """This function takes the json output of a googleDirections function call and
    parses it to output the reported walking distance as a float."""
    dist_string = dirJSON['routes'][0]['legs'][0]['distance']['text']
    non_decimal = re.compile(r'[^\d.]+')
    dist_float = float(non_decimal.sub('', dist_string))
    return dist_float

#Example usage
#d_distance = getDirectionsDistance(d)

def googleNearbyPlacesByKeyword(apiKey, location, radius, keyword):
    """This function takes an API key, a location, a radius, and a keyword
    and returns a result of a Google nearby places query as a json dict."""
    baseURL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
    nearbyURL = baseURL + 'key=' + apiKey + '&location=' + location + '&radius=' + radius + '&keyword=' + keyword
    nearby = json.loads(urllib.urlopen(nearbyURL).read())
    return nearby

#Example usage
#e = googleNearbyPlacesByKeyword(googleAPIKey[0],'40.6823507,-73.8708103', '2000', 'playground')

def getNearbyLatLong(nearbyJSON):
    """This function takes the json output of a googleNearbyPlacesByKeyword function call and
    parses it to output the latitude and longitude of the nearest location."""
    latlong = e['results'][0]['geometry']['location']
    return latlong

#Example usage
#nearLatLng = getNearbyLatLong(e)

def googleGeocoding(address):
    """This function takes an address and returns the latitude and longitude from the Google geocoding API."""
    baseURL = 'http://maps.googleapis.com/maps/api/geocode/json?'
    geocodeURL = baseURL + 'address=' + address + '&components=administrative_area:NY|country:US'
    geocode = json.loads(urllib.urlopen(geocodeURL).read())
    return geocode

#Example usage
#f = googleGeocoding('308 Hemlock St, Brooklyn, NY')

def getGeocodeLatLong(geocodeJSON):
    """This function takes the json output of a googleGeocoding function call and
    parses it to output the latitude and longitude"""
    latlong = geocodeJSON['results'][0]['geometry']['location']
    return latlong

#Example usage
#addressLatLong getGeocodeLatLong(f)