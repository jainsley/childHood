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
from collections import Counter
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

#Load the randomHood dictionary back from the pickle file. This file contains 100 randomly generated points within each of the 266 NYC neighborhoods.
randomHood = pickle.load(open("NYC_neighborhood_random_points.p", "rb"))

#Initialize a counter to monitor progress
progress = 1

#Test case of a 7 year old.
inputAge = '7'

#Initialize list of calculated scores
childHoodScores = []

#For each neighboorhood
for neighborhood in randomHood.keys():

    #For the first 11 coordinates in each neighborhood
    for coords in randomHood[neighborhood][0:11]:

        #Convert from a shapely object to dictionary
        addressLatLng = {'lat' : coords.y, 'lng' : coords.x}

        #Get the neighborhood and borough for the address
        hood = gh.get_neighborhood(addressLatLng)

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

        #print output #Print output for debugging

        #Count how many times each entry appears in the ouput
        entryCount = Counter()
        for entry in [output['school']['schoolScore'], output['crimeNYC'], output['censusNYC'], output['traffic']]:
            entryCount[entry] += 1
	    #print entryCount #Print output for debugging
	
        #If 'No data.' appears more than once, the output score is not calculated.
        if 'No data.' in dict(entryCount).keys():
            if dict(entryCount)['No data.'] > 1:
                output['NYCscore'] = 'Insufficient data for this address.'
        else:
            if output['school']['schoolScore'] == 'No data.':
                output['NYCscore'] = round((0.5 * (100 - output['crimeNYC'])) + (0.3 * output['censusNYC']) + (0.2 * (100 - output['traffic'])))
            elif output['traffic'] == 'No data.':
                output['NYCscore'] = round((0.5 * float(output['school']['schoolScore'])) + (0.3 * (100 - output['crimeNYC'])) + (0.2 * output['censusNYC']))
            else:
                #output['hoodScore'] = round((0.4 * float(output['school']['schoolScore'])) + (0.3 * (100 - output['crimeNeighborhood'])) + (0.2 * output['censusNeighborhood']) + (0.1 * (100 - output['traffic'])))
                output['NYCscore'] = round((0.4 * float(output['school']['schoolScore'])) + (0.3 * (100 - output['crimeNYC'])) + (0.2 * output['censusNYC']) + (0.1 * (100 - output['traffic'])))

        outputJSON = json.dumps(output).encode('utf8')
        childHoodScores.append(outputJSON)
        #print progress #Print how many data points have been analyzed for monitoring progress
        #print addressLatLng #Print location Lat/Lng for debugging
        progress = progress + 1
	
        with open("test.txt", "a") as myfile:
            myfile.write(outputJSON)

pickle.dump(childHoodScores, open("NYC_childHood_scores.p", "wb"))