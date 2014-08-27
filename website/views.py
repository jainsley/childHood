from flask import Flask
app = Flask(__name__)

#Import packages, functions
import googleAPIFunctions as gf
import traffic_shapely_functions as tsf
import get_schools as gs
import query_census_blocks as qcb
import get_hood as gh
import get_crime as gc
import scoreColors as sc

import pickle
import json
from flask import jsonify
from flask import Flask
from flask import render_template
from flask import request
import re
import shapely.geometry
import scipy.stats as st
import sys, getopt, pymongo
import MySQLdb as mdb
from pymongo import MongoClient
import pandas as pd

#Define an age/grade dictionary
age_grade = {'4':'PK',
             '5':'0K',
             '6':'01',
             '7':'02',
             '8':'03',
             '9':'04',
             '10':'05',
             '11':'06',
             '12':'07',
             '13':'08',
             '14':'09',
             '15':'10',
             '16':'11',
             '17':'12'}

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/', methods=['POST'])
def address_post():
    #Get latitude and longitude for input address
    inputAddress = request.form['address']
    inputAge = request.form['age']

    #Check for a valid age
    if not str(inputAge) in age_grade.keys():
        raise InvalidUsage("Choose an age from 4 to 17.")

    #Get the latitiute and longitude for the address
    addressLatLng = gf.getGeocodeLatLong(gf.googleGeocoding(inputAddress))

    #Check for a valid address
    if not 'lat' in addressLatLng.keys():
        raise InvalidUsage("Please enter a valid address in NYC.")

    #Get the neighborhood and borough for the address
    hood = gh.get_neighborhood(addressLatLng)

    #Check for a valid NYC address
    if not hood:
        raise InvalidUsage("Please enter a valid address in NYC.")

    #Initialize output
    output = {}

    #Add address coordinates, borough, and neighborhood to output
    output['addressCoord'] = addressLatLng
    output['neighborhood'] = hood[0]
    output['borough'] = hood[1]

    #Get the zoned or nearest school for the address
    schoolType = ''

    if age_grade[inputAge] in ['09','10','11','12']:
        schoolType = 'hs'
    elif age_grade[inputAge] in ['06','07','08']:
        schoolType = 'ms'
    elif age_grade[inputAge] in ['PK','0K','01','02','03','04','05',]:
        schoolType = 'es'

    school = gs.school_query(addressLatLng, schoolType, inputAge, age_grade)

    output['school'] = school

    #Get the nearest traffic data for the address
    traffic = tsf.findTraffic(addressLatLng)

    output['traffic'] = traffic
    output['trafficColor'] = sc.valueColor(traffic, 'bad')

    #Get the census data for the nearest census blocks
    censusKids = qcb.get_census_blocks(addressLatLng, schoolType, output['neighborhood'], output['borough'])

    output['censusNeighborhood'] = censusKids[0]
    output['censusNeighborhoodColor'] = sc.valueColor(censusKids[0], 'good')
    output['censusNYC'] = censusKids[1]
    output['censusNYCColor'] = sc.valueColor(censusKids[1], 'good')

    #Get the crime data for the address
    crime = gc.get_crime_rank(addressLatLng, output['neighborhood'])

    output['crimeNeighborhood'] = crime[0]
    output['crimeNeighborhoodColor'] = sc.valueColor(crime[0], 'bad')
    output['crimeNYC'] = crime[1]
    output['crimeNYCColor'] = sc.valueColor(crime[1], 'bad')

    if output['school']['schoolScore'] == 'No data.':
        output['hoodScore'] = round((0.5 * (100 - output['crimeNeighborhood'])) + (0.3 * output['censusNeighborhood']) + (0.2 * (100 - output['traffic'])))
        output['NYCscore'] = round((0.5 * (100 - output['crimeNYC'])) + (0.3 * output['censusNYC']) + (0.2 * (100 - output['traffic'])))
    else:    
        output['hoodScore'] = round((0.4 * float(output['school']['schoolScore'])) + (0.3 * (100 - output['crimeNeighborhood'])) + (0.2 * output['censusNeighborhood']) + (0.1 * (100 - output['traffic'])))
        output['NYCscore'] = round((0.4 * float(output['school']['schoolScore'])) + (0.3 * (100 - output['crimeNYC'])) + (0.2 * output['censusNYC']) + (0.1 * (100 - output['traffic'])))

    #return jsonify(**output)

    outputJSON = json.dumps(output).encode('utf8')
    return render_template('results.html', outputJSON=outputJSON)

class InvalidUsage(Exception):
    """Class for handling excpetions"""
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv
    
@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = error.to_dict()
    message = response.get('message', '')
    return render_template('error.html', message = message)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', message = "Page Not Found (404).")

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', message = "An unexpected error has occurred (500).")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
