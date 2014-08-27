def get_neighborhood(LatLng):

    #Import packages
    from pymongo import MongoClient

    #Open database connections
    client = MongoClient()
    db = client.hoods

    #Define query to find the neighborhood
    query = {'geometry' : { '$geoIntersects':{ '$geometry':{'type':'Point', 'coordinates':[LatLng['lng'],LatLng['lat']]}}}}

    #Get the neighborhood and borough of the address
    hood = []
    for item in db.hoods.find(query):
        hood.append(item['properties']['neighborhood'])
        hood.append(item['properties']['borough'])

    return hood