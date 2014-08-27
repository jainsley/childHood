#Define a function to convert UTM coordinates to lat long coordinates

def LatLngConvert(UTMpoints):
    import utm

    points = []

    pt = utm.to_latlon([UTMpoints[1], UTMpoints[0]])
    spt = Point(pt[1], pt[0])
    points.append(spt)
    
    return points

#Define a function to convert lat long coordinates to UTM coordinates

def UTMconvert(points):
    import utm

    UTMpoints = []

    pt = [points.x, points.y]
    UTMpoints.append(utm.from_latlon(*pt))

    return UTMpoints

def get_crime_rank(LatLng, neighborhood):

    #Import packages
    from shapely.geometry import mapping, shape, Polygon, Point
    import utm
    import shapely
    import pandas as pd
    import pickle
    import scipy.stats as st
    import MySQLdb as mdb

    #Connect to mySQL database, extract locations
    crimeCon = mdb.connect('localhost','root','','censusdb')
    cursor = crimeCon.cursor()
    cursor.execute("SELECT latitude,longitude FROM crime")
    allCrimes = cursor.fetchall()

    #Convert crime locations to shapely objects
    LatLngCrime = []
    for item in allCrimes:
        LatLngCrime.append([Point(float(item[0]), float(item[1]))])

    #Convert address to shapely object, draw a 1km circle around address
    pointLatLng = Point(LatLng['lat'], LatLng['lng'])
    addressUTM = UTMconvert(pointLatLng)
    addressCircleUTM = Point(addressUTM).buffer(1000)

    addressCircle = []

    for i in list(addressCircleUTM.exterior.coords):
        cPt = utm.to_latlon(i[0], i[1], list(addressUTM)[0][2], list(addressUTM)[0][3])
        addressCircle.append(cPt)
        
    addressPoly = Polygon(addressCircle)

    #Count crimes that occured within the 1km radius
    crimeCounter = 0
    for item in LatLngCrime:
        if item[0].intersects(addressPoly):
            crimeCounter = crimeCounter + 1

    #Compare the calculated crime to the crime within the neighborhood
    cursor.execute("SELECT Mean,StdDev FROM sampledCrime WHERE Neighborhood = %s", [neighborhood])
    hoodCrimes = list(cursor.fetchall())
    if hoodCrimes:
        hoodZscore = (float(crimeCounter) - float(hoodCrimes[0][0])) / (float(hoodCrimes[0][1]) + 0.01)
    else:
        hoodZscore = "No data."

    #Compare the calculated crime to crime across NYC
    cursor.execute("SELECT Mean,StdDev FROM sampledCrime WHERE Neighborhood = 'NYC'")
    NYCcrimes = list(cursor.fetchall())
    if NYCcrimes:
        NYCZscore = (float(crimeCounter) - float(NYCcrimes[0][0])) / (float(NYCcrimes[0][1]) + 0.01)
    else:
        NYCZscore = "No data."

    #Convert z scores to percentiles
    if hoodZscore == "No data.":
        propHood = "No data."
    else:
        propHood = int(round(st.norm.cdf(hoodZscore) * 100, 0))
        if propHood > 100:
            propHood = 100

    if NYCZscore == "No data.":
        propNYC = "No data."
    else:
        propNYC = int(round(st.norm.cdf(NYCZscore) * 100, 0))
        if propNYC > 100:
            propNYC = 100

    return [propHood, propNYC]
