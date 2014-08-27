#Define a function to convert lat long coordinates to UTM coordinates

def UTMconvert(points):
    import utm

    UTMpoints = []

    pt = [points.x, points.y]
    UTMpoints.append(utm.from_latlon(*pt))

    return UTMpoints

#Define a function to convert UTM coordinates to lat long coordinates

def LatLngConvert(UTMpoints):
    import utm

    points = []

    pt = utm.to_latlon([UTMpoints[1], UTMpoints[0]])
    spt = Point(pt[1], pt[0])
    points.append(spt)
    
    return points

#Define a function to get all traffic data surrounding an area

def findTraffic(LatLng):
    #Import packages
    from shapely.geometry import mapping, shape, Polygon, Point
    import shapely.geometry
    import MySQLdb as mdb
    import scipy.stats as st
    import utm

    #Import functions for Google API
    import googleAPIFunctions as gf

    #Open a connection to MySQL database
    censusCon = mdb.connect('localhost','root','','censusdb')
    cursor = censusCon.cursor()

    #Get traffic data z_score and the line shape representing the monitored street intersections from database
    cursor.execute("SELECT z_score,line FROM traffic")
    trafficZscores = list(cursor.fetchall())

    #Convert the input coordinated to a shapely Point object
    pointLatLng = Point(LatLng['lat'], LatLng['lng'])

    #Convert the Point coordinates to UTM, define a 1km circle around the point
    addressUTM = UTMconvert(pointLatLng)
    addressCircleUTM = Point(addressUTM).buffer(1000) #Chose 1km as that's a likely distance to walk.

    #Initialize list for circle coordinates
    addressCircle = []

    #Convert the UTM coordinates back to Lat/Lng
    for i in list(addressCircleUTM.exterior.coords):
        cPt = utm.to_latlon(i[0], i[1], list(addressUTM)[0][2], list(addressUTM)[0][3])
        addressCircle.append(cPt)
    
    #Store the results as a shapely polygon
    addressPoly = Polygon(addressCircle)

    #Initialize list of nearby traffic monitoring zones
    nearbyTraffic = []

    #Get the z scores of each traffic intersection that intersects with the circle
    for idx, var in enumerate(trafficZscores):
        if var[1] != None:
            line = shapely.geometry.LineString(eval(trafficZscores[idx][1]))
            if line.intersects(addressPoly):
                nearbyTraffic.append(var)
    
    #Sum the z scores    
    zSum = 0
    for i in nearbyTraffic:
        zSum = zSum + i[0]

    #Return the mean z score converted to percentile score. If there is no traffic data, return 'No data.'
    if len(nearbyTraffic) > 0:
        zMean = zSum / len(nearbyTraffic)

        trafficPer = int(round(st.norm.cdf(zMean) * 100, 0))

        return(trafficPer)
    
    else:
        return 'No data.'
