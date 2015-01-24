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
    response = locations.find({"address": query})
    if(response == None):
        return None
    return list(response) #array instead of cursor

def add(location=None, name=None, address=None, author=None, zipcode=None, desc=None):
    if (name==None) or (address==None) or (author==None) or (zipcode==None) or (desc==None):
        return False
    votes = {"up": 1, "down": 0} #vote dict
    location = {"address": address, "zipcode": zipcode, "name": name,
                "author": author, "desc": desc, "votes": votes
    }    

    if locations.find_one({"address": address, "zipcode": zipcode}) != None:
        location_id = locations.insert(location)
        #return "Successfully added " + location['name'] + "!"
        return True
    else:
        #return "Location already in database."
        return False

def get_location(postid):
    loc = locations.find_one({ "_id": ObjectId(postid) })
    return loc

def get_locations():
    locs = locations.find()
    return list(locs)  #array instead of cursor

def sort_votes(post): #sorts either comments or posts by votes
    try:
        #print 'VOTES: '
        print get_votes(post[0]['votes'])
        #print "Sorted votes."
        return sorted(post, key= lambda v: get_votes(v['votes']), reverse=True) #throws an error
    except:
        print "Failure."
        return post

def get_votes(votes):
    try:
        return votes["up"] - votes["down"]
    except:
        return 0

def add_comment(comment=None, content=None, postid=None, author=None): #for transitional purposes until we move dict generation out of app and into database
    if comment == None:
        if (content == None) or (postid == None) or (author == None):
            return False
        else:
            votes = {"up": 1, "down": 0} #vote dict
            comment = {'postid': postid, 'content': content, 'author': author,
                       'votes': votes}
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
    post = get_location(postid)
    if post == None:
        return False
    post_comments = comments.find({'postid': postid})
    return list(post_comments) #array instead of cursor
