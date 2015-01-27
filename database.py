from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

client = MongoClient('mongodb://Citronnade:Citronnade@ds031271.mongolab.com:31271/softdev2015')
db = client['softdev2015']
locations = db['locations']
comments = db['comments']
users = db['users'] #collection
# db = client.test_database
# Possible documents:
# - Idea posts
# - Comment chains

#app.secret_key = "c~9%1.p4IUDj2I*QYHivZ73/407E]7<f1o_5b1(QzNdr00m7Tit)[T>C;2]5"

#def search(query):
#    response = locations.find({"address": query})
#    if(response == None):
#        return None
#    return list(response) #array instead of cursor

def search(keywords, zipcode): #keywords is array or single word?
    response_zip = locations.find({"zipcode": zipcode})
    if response_zip == None:
        return None
    response_zip = list(response_zip) #create array
    print '~~~~~~~~~~~~~~~~~~~~~~~'
    print keywords
    print '~~~~~~~~~~~~~~~~~~~~~'
    print response_zip
    if not keywords: #find everything in a given zipcode.
        return response_zip
    culled_response = [] #sets aren't really working
    added_responses = [] #so we now have a set for added locations.
    enum_locs = list(enumerate(response_zip))
    #this gives something like [(0, loc1), (1, loc2)]
    for keyword in keywords:
        keyword = keyword.lower()
        for loc in enum_locs:
            if keyword in loc[1]['desc'].lower() or keyword in loc[1]['name'].lower():
                if loc[0] not in added_responses:
                    culled_response.append(loc[1])
                    added_responses.append(loc[0])
                
    return culled_response
                
            
    

#checks if the username is available
#returns true if available
def check_username(username):
    if users.find_one({'username':username}) != None:
        return False # username already exists
    return True # available, does not exist yet

# registers a user. Returns the user_id
def register_user(username, password):
    user = {"username":username, "password":generate_password_hash(password),
            "rates": [], "bizcuits": []}
    user_id = users.insert(user)
    print "Succesfully registered."
    return user_id

# checks if the username and password logs in
def check_login(username, password):
    user = get_user(username)
    if user == None:
        return False
    if check_password_hash(user['password'], password):
        print "password to be checked: " + password
        print "current password hash: " + user['password']
        return True
    return False

def get_user(username):
    user = users.find_one({"username":username})
    return user

def get_password(username): #returns a hash
    user = get_user(username)
    return user["password"]

def set_password(username, password):
    user = get_user(username)
    print "user's _id: " + str(user["_id"])
    print "before: " + user["password"]
    user["password"] = generate_password_hash(password)
    print "after: " + user["password"]
    users.save(user)
    #users.update({"_id": user["_id"]}, {"set":{"password":user["password"]}})
    #users.find_and_modify({"username":username},{"password":user["password"]}) 
    print users.find_one({"username":username})
    print users.find_one({"username":username, "password":user["password"]})

def get_users():
    usrs = users.find()
    return list(usrs)
def add_location(location=None, name=None, address=None, author=None, zipcode=None, desc=None):
    if (name==None) or (address==None) or (author==None) or (zipcode==None) or (desc==None):
        print "Missing fields, failed."
        return False
    #votes = {"up": 1, "down": 0} #vote dict
    upvotes = []
    downvotes = []
    location = {"address": address, "zipcode": zipcode, "name": name,
                "author": author, "desc": desc, "upvotes": upvotes, "downvotes":downvotes
    }    
    #if locations.find_one({"address": address, "zipcode": zipcode}) == None:
    location_id = locations.insert(location)
    print "Successfully added " + location['name'] + "!"
    return location_id

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
    post_comments = reversed(list(post_comments))
    return post_comments #array instead of cursor
