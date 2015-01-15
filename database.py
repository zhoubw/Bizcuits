from pymongo import MongoClient

client = MongoClient('mongodb://Citronnade:Citronnade@ds031271.mongolab.com:31271/softdev2015')
db = client['softdev2015']
locations = db['locations']

# db = client.test_database
# Possible documents:
# - Idea posts
# - Comment chains

#app.secret_key = "c~9%1.p4IUDj2I*QYHivZ73/407E]7<f1o_5b1(QzNdr00m7Tit)[T>C;2]5"

def search(query):
    response = locations.find_one({"name": query})
    return response

def add(location):
    #uhm. can you loop through a dict and check that everything is good?
    if locations.find_one({"name": location}) != None:
        location_id = locations.insert(location)
        #return "Successfully added " + location['name'] + "!"
        return True
    else:
        #return "Location already in database."
        return False

