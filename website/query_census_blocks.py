def get_census_blocks(LatLng, school_type, hood, borough):

    #Import packages
    from pymongo import MongoClient
    import pandas as pd
    import MySQLdb as mdb
    import scipy.stats as st
    import math

    import googleAPIFunctions as gf

    #Set up mongoDB connection
    client = MongoClient()
    db = client.censusDB

    query = {'geometry' : { '$geoIntersects':{ '$geometry':{'type':'Point', 'coordinates':[LatLng['lng'],LatLng['lat']]}}}}

    query_zone = []
    for item in db.censusBlocks.find(query):
        query_zone.append(item['properties']['ct2010'])

    #Open connection to mysql database
    censusCon = mdb.connect('localhost','root','','censusdb')
    cursor = censusCon.cursor()

    selCol = ['Tot_Population', 'F_Under_5', 'F_5_to_9', 'F_10_to_14', 'F_15_to_17',
          'M_Under_5', 'M_5_to_9', 'M_10_to_14', 'M_15_to_17']
    
    if query_zone:
        sql_query = "SELECT Tot_Population,F_Under_5,F_5_to_9,F_10_to_14,F_15_to_17,M_Under_5,M_5_to_9,M_10_to_14,M_15_to_17 FROM census_data WHERE GEOid2 LIKE %s"
        cursor.execute(sql_query, ('%' + query_zone[0] + '%',))
        zonePop = list(cursor.fetchall())
        zonePopDf = pd.DataFrame(zonePop, columns=selCol)

        if school_type == 'hs':
            dfIndex = ['Tot_Population', 'F_10_to_14', 'F_15_to_17', 'M_10_to_14', 'M_15_to_17']
        elif school_type == 'ms':
            dfIndex = ['Tot_Population', 'F_10_to_14', 'M_10_to_14']
        elif school_type == 'es':
            dfIndex = ['Tot_Population', 'F_Under_5', 'F_5_to_9', 'M_Under_5', 'M_5_to_9']

        selDf = zonePopDf.loc[:,dfIndex]

        def propKids(ser):
            if ser.loc['Tot_Population'] > 0:
                ratio = float(ser[1:].sum()) / float(ser.loc['Tot_Population'])
                return ratio

        meanProp = selDf.apply(propKids, 1).mean()

        #Query the census kid population sampled location database
        sql_query = "SELECT AgeRange,mean,std FROM censusAgg WHERE Neighborhood = %s AND Borough = %s"
        cursor.execute(sql_query, (hood, borough))
        hoodMeanStd = list(cursor.fetchall())

        output = []
        if hoodMeanStd:
            if hoodMeanStd[0][1] != None or hoodMeanStd[1][1] != None or hoodMeanStd[2][1] != None:

                kidPopNYC = {'LessThanNine' : [0.115852, 0.030868], 'TenToFourteen' : [0.054890, 0.018394], 'TenToSeventeen' : [0.090276, 0.028859]}

                if school_type == 'es':
                    if hoodMeanStd[0][1] != None and hoodMeanStd[0][2] != None:
                        hoodZscore = (meanProp - float(hoodMeanStd[0][1])) / (float(hoodMeanStd[0][2]) + 0.01)
                        NYCZscore = (meanProp - kidPopNYC['LessThanNine'][0]) / (kidPopNYC['LessThanNine'][1] + 0.01)
                    else:
                        hoodZscore = []
                        NYCZscore = []
                        output = ['No data.', 'No data.']
                elif school_type == 'ms':
                    if hoodMeanStd[1][1] != None and hoodMeanStd[1][2] != None:
                        hoodZscore = (meanProp - float(hoodMeanStd[1][1])) / (float(hoodMeanStd[1][2]) + 0.01)
                        NYCZscore = (meanProp - kidPopNYC['TenToFourteen'][0]) / (kidPopNYC['TenToFourteen'][1] + 0.01)
                    else:
                        hoodZscore = []
                        NYCZscore = []
                        output = ['No data.', 'No data.']
                elif school_type == 'hs':
                    if hoodMeanStd[2][1] != None and hoodMeanStd[2][2] != None:
                        hoodZscore = (meanProp - float(hoodMeanStd[2][1])) / (float(hoodMeanStd[2][2]) + 0.01)
                    NYCZscore = (meanProp - kidPopNYC['TenToSeventeen'][0]) / (kidPopNYC['TenToSeventeen'][1] + 0.01)
                else:
                    hoodZscore = []
                    NYCZscore = []
                    output = ['No data.', 'No data.']

                if hoodZscore:
                    propHoodtemp = st.norm.cdf(hoodZscore) * 100
                    if math.isnan(propHoodtemp):
                        propHood = 0
                    else:
                        propHood = int(round(propHoodtemp, 0))
                    if propHood > 100:
                        propHood = 100
                    output.append(propHood)

                if NYCZscore:
                    propNYCtemp = st.norm.cdf(NYCZscore) * 100
                    if math.isnan(propNYCtemp):
                        propNYC = 0
                    else:
                        propNYC = int(round(propNYCtemp, 0))
                    if propNYC > 100:
                        propNYC = 100
                    output.append(propNYC)

            else:
                output = ['No data.', 'No data.']
        else:
            output = ['No data.', 'No data.']
    else:
        output = ['No data.', 'No data.']

    return output