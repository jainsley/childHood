#Import packages
import sys, getopt, pymongo
import MySQLdb as mdb
from pymongo import MongoClient

#Import functions for Google API
import googleAPIFunctions as gf

#Define a dictionary matching age with grade
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

#Function to find the nearest school
def get_closest_school(LatLng, latlngD, latlngKeys):
    from functools import partial

    #Function to calculate distance between two points
    dist = lambda coord1, coord2: (coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2

    #Find the nearest high school
    closeCoord = min(latlngKeys, key=partial(dist, [LatLng['lng'], LatLng['lat']]))
    closeName = latlngD[str(closeCoord).replace(' ', '')]
    
    return closeName

#Define function to query for school based on age
def school_query(LatLng, school_type, age):
    #Initialize output variables
    full_entry = []
    query_dbn = []
    query_results = []
    
    #Query school zone database
    if school_type == 'es':
        query = {'geometry':{ '$geoIntersects':{ '$geometry':
                                                {'type':'Point','coordinates':[LatLng['lng'],LatLng['lat']]}}}}
        for item in db.es_zones.find(query):
            query_dbn.append(item['properties']['dbn'])
            full_entry.append(item)
        
        if query_dbn[0] == None:
            query_results.append(full_entry[0]['properties']['remarks'])
            
        else:
            sep_dbn = [i.strip() for i in list(query_dbn)[0].split(',')]

            for idx, val in enumerate(sep_dbn):
                if val == "Unzoned" or val == None:
                    sql_query = "SELECT title,loc FROM school_results WHERE GradesFinal LIKE %s"
                    cursor.execute(sql_query, ('%' + age_grade[age] + '%',))
                    latlng = list(cursor.fetchall())
                    latlngD = {i[1]:i[0] for i in latlng}
                    latlngKeys = [eval(i) for i in latlngD.keys()]
                    query_results.append(full_entry[idx]['properties']['remarks'])
                    query_results.append(get_closest_school(LatLng, latlngD, latlngKeys))
                else:
                    cursor.execute("SELECT title FROM school_results WHERE ATSSystemCode = %s", [val])
                    query_results.append(cursor.fetchall())

                if full_entry[0]['properties']['remarks'] != None:
                    query_results.append(full_entry[0]['properties']['remarks'])
            
        return query_results

    elif school_type == 'ms':
        query = {'geometry':{ '$geoIntersects':{ '$geometry':
                                                {'type':'Point','coordinates':[LatLng['lng'],LatLng['lat']]}}}}
        for item in db.ms_zones.find(query):
            query_dbn.append(item['properties']['dbn'])
            full_entry.append(item)
        
        if query_dbn[0] == None:
            query_results.append(full_entry[0]['properties']['remarks'])
        
        else:
            sep_dbn = [i.strip() for i in list(query_dbn)[0].split(',')]

            for idx, val in enumerate(sep_dbn):
                if val == "Unzoned" or val == None:
                    sql_query = "SELECT title,loc FROM school_results WHERE GradesFinal LIKE %s"
                    cursor.execute(sql_query, ('%' + age_grade[age] + '%',))
                    latlng = list(cursor.fetchall())
                    latlngD = {i[1]:i[0] for i in latlng}
                    latlngKeys = [eval(i) for i in latlngD.keys()]
                    query_results.append(full_entry[idx]['properties']['remarks'])
                    query_results.append(get_closest_school(LatLng, latlngD, latlngKeys))
                else:
                    cursor.execute("SELECT title FROM school_results WHERE ATSSystemCode = %s", [val])
                    query_results.append(cursor.fetchall())

            if full_entry[0]['properties']['remarks'] != None:
                query_results.append(full_entry[0]['properties']['remarks'])  
            
        return query_results
    
    elif school_type == 'hs':
        sql_query = "SELECT title,loc FROM school_results WHERE GradesFinal LIKE %s"
        cursor.execute(sql_query, ('%' + age_grade[age] + '%',))
        latlng = list(cursor.fetchall())
        latlngD = {i[1]:i[0] for i in latlng}
        latlngKeys = [eval(i) for i in latlngD.keys()]
        query_results.append('Students have a city-wide choice in the high school to attend.')
        query_results.append(get_closest_school(LatLng, latlngD, latlngKeys))
        
        return query_results

#Run query
#address = '308 hemlock st brooklyn, ny'
#address = '121 saratoga ave brooklyn NY'
#address = '1030 86th St Brooklyn, NY'
address = '353 Broadway Brooklyn, NY'

#Get latitude and longitude for input address
addressLatLng = gf.getGeocodeLatLong(gf.googleGeocoding(address))

inputAge = '17'
schoolType = ''

try:
    age_grade[inputAge]
except KeyError:
    sys.exit("Not an appropriate age.")

if age_grade[inputAge] in ['09','10','11','12']:
    schoolType = 'hs'
elif age_grade[inputAge] in ['06','07','08']:
    schoolType = 'ms'
elif age_grade[inputAge] in ['PK','0K','01','02','03','04','05',]:
    schoolType = 'es'

#Open database connections
client = MongoClient()
db = client.schoolDB

schoolCon = mdb.connect('localhost','','','censusdb')
cursor = schoolCon.cursor()

school_query(addressLatLng, schoolType, inputAge)


full_entry = []
query_dbn = []
query_results = []

query = {'geometry':{ '$geoIntersects':{ '$geometry':{'type':'Point','coordinates':[addressLatLng['lng'],addressLatLng['lat']]}}}}
for item in db.ms_zones.find(query):
    query_dbn.append(item['properties']['dbn'])
    full_entry.append(item)

if query_dbn[0] == None:
    query_results.append(full_entry[0]['properties']['remarks'])
    
else:    
    sep_dbn = [i.strip() for i in list(query_dbn)[0].split(',')]

    for idx, val in enumerate(sep_dbn):
        if val == "Unzoned" or val == None:
            sql_query = "SELECT title,loc FROM school_results WHERE GradesFinal LIKE %s"
            cursor.execute(sql_query, ('%' + age_grade[age] + '%',))
            latlng = list(cursor.fetchall())
            latlngD = {i[1]:i[0] for i in latlng}
            latlngKeys = [eval(i) for i in latlngD.keys()]
            query_results.append(full_entry[idx]['properties']['remarks'])
            query_results.append(get_closest_school(LatLng, latlngD, latlngKeys))

        else:
            cursor.execute("SELECT title FROM school_results WHERE ATSSystemCode = %s", [val])
            query_results.append(cursor.fetchall())

    if full_entry[0]['properties']['remarks'] != None:
        query_results.append(full_entry[0]['properties']['remarks'])


print query_results
#print query_dbn
#print full_entry