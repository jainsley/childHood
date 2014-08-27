#Define a function to get the nearest school
def get_closest_school(LatLng, latlngD, latlngKeys):
    from functools import partial

    #Function to calculate distance between two points
    dist = lambda coord1, coord2: (coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2

    #Find the nearest school
    closeCoord = min(latlngKeys, key=partial(dist, [LatLng['lng'], LatLng['lat']]))
    closeName = latlngD[str(closeCoord).replace(' ', '')]
	    
    return closeName

#Define function to query for the zoned or nearest school
def school_query(LatLng, school_type, age, age_grade):
    #Import packages
    from pymongo import MongoClient
    import MySQLdb as mdb
    from itertools import chain

    #Initialize output variables
    full_entry = []
    query_dbn = []
    query_results = {}
    output = []
    filterResults = []

    #Open database connections
    client = MongoClient()
    db = client.schoolDB

    schoolCon = mdb.connect('localhost','root','','censusdb')
    cursor = schoolCon.cursor()
    
    #Query school zone database
    if school_type == 'es':
        query = {'geometry':{ '$geoIntersects':{ '$geometry':
                                                {'type':'Point','coordinates':[LatLng['lng'],LatLng['lat']]}}}}
        
        #Find the appropriate elementary school zone
        for item in db.es_zones.find(query):
            query_dbn.append(item['properties']['dbn'])
            full_entry.append(item)

        if query_dbn: #Ensure the query returned data
            if query_dbn[0] == None: #If there is no entry, find the closest school and get the DoE score
                sql_query = "SELECT ATSSystemCode,title,loc FROM school_results WHERE GradesFinal LIKE %s"
                cursor.execute(sql_query, ('%' + age_grade[age] + '%',))
                latlng = list(cursor.fetchall())
                latlngD = {i[2]:[i[0],i[1]] for i in latlng}
                latlngKeys = [eval(i) for i in latlngD.keys()]
                closestSchool = get_closest_school(LatLng, latlngD, latlngKeys)
                sql_query = "SELECT DBN,SCHOOL_13,Score FROM school_score WHERE DBN = %s"
                cursor.execute(sql_query, (closestSchool[0],))
                tempResults = cursor.fetchall()
                filterResults = filter(None, tempResults)
                
            else: #If there is an entry, split multiple returned schools into separate entries
                sep_dbn = [i.strip() for i in list(query_dbn)[0].split(',')]

                #Loop over each returned school to get the DoE school
                for idx, val in enumerate(sep_dbn):
                    if val == "Unzoned" or val == None:
                        sql_query = "SELECT ATSSystemCode,title,loc FROM school_results WHERE GradesFinal LIKE %s"
                        cursor.execute(sql_query, ('%' + age_grade[age] + '%',))
                        latlng = list(cursor.fetchall())
                        latlngD = {i[2]:[i[0],i[1]] for i in latlng}
                        latlngKeys = [eval(i) for i in latlngD.keys()]
                        closestSchool = get_closest_school(LatLng, latlngD, latlngKeys)
                        sql_query = "SELECT DBN,SCHOOL_13,Score FROM school_score WHERE DBN = %s"
                        cursor.execute(sql_query, (closestSchool[0],))
                        tempResults = cursor.fetchall()
                        filterResults = filter(None, tempResults)
                    else:
                        cursor.execute("SELECT DBN,SCHOOL_13,Score FROM school_score WHERE DBN = %s", [val])
                        tempResults = cursor.fetchall()
                        filterResults = filter(None, tempResults)
            
            #Return zoned school results
            if filterResults:
                query_results['schoolName'] = filterResults[0][1]
                query_results['schoolDBN'] = filterResults[0][0]
                query_results['schoolScore'] = filterResults[0][2]
            else:
                sql_query = "SELECT ATSSystemCode,title,loc FROM school_results WHERE GradesFinal LIKE %s"
                cursor.execute(sql_query, ('%' + age_grade[age] + '%',))
                latlng = list(cursor.fetchall())
                latlngD = {i[2]:[i[0],i[1]] for i in latlng}
                latlngKeys = [eval(i) for i in latlngD.keys()]
                closestSchool = get_closest_school(LatLng, latlngD, latlngKeys)
                query_results['schoolName'] = closestSchool[1]
                query_results['schoolDBN'] = closestSchool[0]
                query_results['schoolScore'] = 'No data.'
        else:
            sql_query = "SELECT ATSSystemCode,title,loc FROM school_results WHERE GradesFinal LIKE %s"
            cursor.execute(sql_query, ('%' + age_grade[age] + '%',))
            latlng = list(cursor.fetchall())
            latlngD = {i[2]:[i[0],i[1]] for i in latlng}
            latlngKeys = [eval(i) for i in latlngD.keys()]
            closestSchool = get_closest_school(LatLng, latlngD, latlngKeys)
            query_results['schoolName'] = closestSchool[1]
            query_results['schoolDBN'] = closestSchool[0]
            query_results['schoolScore'] = 'No data.'

        if full_entry[0]['properties']['remarks'] != None:
            query_results['remarks'] = full_entry[0]['properties']['remarks']

        return query_results

    elif school_type == 'ms':
        query = {'geometry':{ '$geoIntersects':{ '$geometry':
                                                {'type':'Point','coordinates':[LatLng['lng'],LatLng['lat']]}}}}
        for item in db.ms_zones.find(query):
            query_dbn.append(item['properties']['dbn'])
            full_entry.append(item)
        
        if query_dbn:
            if query_dbn[0] == None:
                sql_query = "SELECT ATSSystemCode,title,loc FROM school_results WHERE GradesFinal LIKE %s"
                cursor.execute(sql_query, ('%' + age_grade[age] + '%',))
                latlng = list(cursor.fetchall())
                latlngD = {i[2]:[i[0],i[1]] for i in latlng}
                latlngKeys = [eval(i) for i in latlngD.keys()]
                closestSchool = get_closest_school(LatLng, latlngD, latlngKeys)
                sql_query = "SELECT DBN,SCHOOL_13,Score FROM school_score WHERE DBN = %s"
                cursor.execute(sql_query, (closestSchool[0],))
                tempResults = cursor.fetchall()
                filterResults = filter(None, tempResults)
                
            else:
                sep_dbn = [i.strip() for i in list(query_dbn)[0].split(',')]

                for idx, val in enumerate(sep_dbn):
                    if val == "Unzoned" or val == None:
                        sql_query = "SELECT ATSSystemCode,title,loc FROM school_results WHERE GradesFinal LIKE %s"
                        cursor.execute(sql_query, ('%' + age_grade[age] + '%',))
                        latlng = list(cursor.fetchall())
                        latlngD = {i[2]:[i[0],i[1]] for i in latlng}
                        latlngKeys = [eval(i) for i in latlngD.keys()]
                        closestSchool = get_closest_school(LatLng, latlngD, latlngKeys)
                        sql_query = "SELECT DBN,SCHOOL_13,Score FROM school_score WHERE DBN = %s"
                        cursor.execute(sql_query, (closestSchool[0],))
                        tempResults = cursor.fetchall()
                        filterResults = filter(None, tempResults)
                    else:
                        cursor.execute("SELECT DBN,SCHOOL_13,Score FROM school_score WHERE DBN = %s", [val])
                        tempResults = cursor.fetchall()
                        filterResults = filter(None, tempResults)
            
            if filterResults:
                query_results['schoolName'] = filterResults[0][1]
                query_results['schoolDBN'] = filterResults[0][0]
                query_results['schoolScore'] = filterResults[0][2]
            else:
                sql_query = "SELECT ATSSystemCode,title,loc FROM school_results WHERE GradesFinal LIKE %s"
                cursor.execute(sql_query, ('%' + age_grade[age] + '%',))
                latlng = list(cursor.fetchall())
                latlngD = {i[2]:[i[0],i[1]] for i in latlng}
                latlngKeys = [eval(i) for i in latlngD.keys()]
                closestSchool = get_closest_school(LatLng, latlngD, latlngKeys)
                query_results['schoolName'] = closestSchool[1]
                query_results['schoolDBN'] = closestSchool[0]
                query_results['schoolScore'] = 'No data.'
        else:
            sql_query = "SELECT ATSSystemCode,title,loc FROM school_results WHERE GradesFinal LIKE %s"
            cursor.execute(sql_query, ('%' + age_grade[age] + '%',))
            latlng = list(cursor.fetchall())
            latlngD = {i[2]:[i[0],i[1]] for i in latlng}
            latlngKeys = [eval(i) for i in latlngD.keys()]
            closestSchool = get_closest_school(LatLng, latlngD, latlngKeys)
            query_results['schoolName'] = closestSchool[1]
            query_results['schoolDBN'] = closestSchool[0]
            query_results['schoolScore'] = 'No data.'

        if full_entry[0]['properties']['remarks'] != None:
            query_results['remarks'] = full_entry[0]['properties']['remarks']

        return query_results
    
    elif school_type == 'hs':
        sql_query = "SELECT ATSSystemCode,title,loc FROM school_results WHERE GradesFinal LIKE %s"
        cursor.execute(sql_query, ('%' + age_grade[age] + '%',))
        latlng = list(cursor.fetchall())
        latlngD = {i[2]:[i[0],i[1]] for i in latlng}
        latlngKeys = [eval(i) for i in latlngD.keys()]
        closestSchool = get_closest_school(LatLng, latlngD, latlngKeys)
        sql_query = "SELECT DBN,SCHOOL_13,Score FROM school_score WHERE DBN = %s"
        cursor.execute(sql_query, (closestSchool[0],))
        tempResults = cursor.fetchall()
        filterResults = filter(None, tempResults)
                
        if filterResults:
            query_results['schoolName'] = filterResults[0][1]
            query_results['schoolDBN'] = filterResults[0][0]
            query_results['schoolScore'] = filterResults[0][2]
        else:
            sql_query = "SELECT ATSSystemCode,title,loc FROM school_results WHERE GradesFinal LIKE %s"
            cursor.execute(sql_query, ('%' + age_grade[age] + '%',))
            latlng = list(cursor.fetchall())
            latlngD = {i[2]:[i[0],i[1]] for i in latlng}
            latlngKeys = [eval(i) for i in latlngD.keys()]
            closestSchool = get_closest_school(LatLng, latlngD, latlngKeys)
            query_results['schoolName'] = closestSchool[1]
            query_results['schoolDBN'] = closestSchool[0]
            query_results['schoolScore'] = 'No data.'

        query_results['remarks'] = 'Students have a city-wide choice in the high school to attend.'

        return query_results