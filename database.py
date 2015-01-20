from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('mongodb://Citronnade:Citronnade@ds031271.mongolab.com:31271/softdev2015')
db = client['softdev2015']
locations = db['locations']
comments = db['comments']

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

def get_location(uid):
    loc = locations.find_one({ "_id": ObjectId(uid) })
    return loc

def get_locations():
    locs = locations.find()
    return locs

def add_comment(comment=None, content=None, uid=None, author=None): #for transitional purposes until we move dict generation out of app and into database
    if comment == None:
        if content == None || uid == None || author == None:
            return False
        else:
            comment = {'postid': uid, 'content': content, 'author': author}
    if get_location(postid) == None:
        return False #location not found
    else:
        comment_id = comments.insert(comment)
        return True

def get_comment(commentid=None):
    if commentid == None:
        #no comment sent
        return False
    else:
        comment = comments.find_one({"_id": commentid})
        if commment == None:
            return False
        return comment

def get_comments(postid):
    post = get_location(uid)
    if post == None:
        return False
    post_comments = comments.find('postid': postid)
    return post_comments
