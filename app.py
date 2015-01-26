from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask, render_template, request, redirect, session, url_for, escape, flash
from datetime import datetime
import pytz
from tzlocal import get_localzone
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

import database

app = Flask(__name__)

#mongo stuff
client = MongoClient('mongodb://Citronnade:Citronnade@ds031271.mongolab.com:31271/softdev2015')
db = client['softdev2015'] #database in softdev2015
locations = db['locations'] #collection
comments = db['comments'] #collection
users = db['users'] #collection

app.secret_key = "c~9%1.p4IUDj2I*QYHivZ73/407E]7<f1o_5b1(QzNdr00m7Tit)[T>C;2]5"

#timezone stuff
tz = get_localzone()

def get_timestamp(loc_id):
    date = ObjectId(loc_id).generation_time
    date = date.astimezone(tz)
    date = date.strftime("%b %d, %Y at %I:%M %p")
    return date


#for pages that require login
def login_required(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if "username" in session:
            return f(*args, **kwargs)
        return redirect(url_for("login")) #maybe need this to be sth else
    return inner

#for pages that cannot use login
def nologin(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if "username" in session:
            flash(session['username'] + " is logged in!")
            return redirect(url_for("index")) # I have no idea what it is yet
        return f(*args, **kwargs)
    return inner

def rated():
    if request.method == "POST":
        user = database.get_user(session['username'])
        if "upvote" in request.form:
            _id = request.form['upvote']
            if 'rates' in user:
                if _id in user['rates']:
                    return #yeah this can be better
            loc = database.get_location(_id)
            locations.update(
            #{ '_id':ObjectId(request.form['upvote'])},
                loc,
                {'$inc':{'votes.up':1}},
                upsert=False,
                multi=False)
            users.update(
                user,
                {'$push':{'rates':_id}}
            )
        elif "downvote" in request.form:
            _id = request.form['downvote']
            if 'rates' in user:
                if _id in user['rates']:
                    return
            loc = database.get_location(_id)
            locations.update(
                #{ '_id':ObjectId(request.form['upvote'])},
                loc,
                {'$inc':{'votes.down':1}},
                upsert=False,
                multi=False)
            users.update(
                user,
                {'$push':{'rates':_id}})

@app.route('/', methods=['GET','POST'])
#@app.route('/index')
#@app.route('/home')
def index():
    rated()
    #return render_template("index.html")
    locs = database.get_locations()
    #print 'before: ' + str(locs)
    locs = database.sort_votes(locs)
    #print 'after: ' + str(locs)
    #usrs = database.get_users()
    #print not locations.find_one({'_id':ObjectId('54b01a4b839b007864cfa565')}) in users.find_one({'username':session['username']})['rates']
    if 'username' in session:
        rates = users.find_one({'username':session['username']})['rates']
        rates_str = [str(x) for x in rates]
        return render_template("front.html", session=session,users=users,locations=locs,get_timestamp=get_timestamp, get_votes=database.get_votes,rates=rates_str)
    return render_template("front.html", session=session,users=users,locations=locs,get_timestamp=get_timestamp, get_votes=database.get_votes)

@app.route('/account')
def account():
    return render_template("account.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/post/<postid>', methods=["GET","POST"])
def post(postid=None):
    curr_loc = database.get_location(postid)
    print curr_loc
    curr_comments = database.get_comments(postid)
    if request.method == "GET":
        if 'username' in session:
            rates = users.find_one({'username':session['username']})['rates']
            rates_str = [str(x) for x in rates]
            return render_template("post.html", location=curr_loc,get_timestamp=get_timestamp, comments=curr_comments, get_votes=database.get_votes,postid=postid,session=session,rates=rates_str) 
        return render_template("post.html", location=curr_loc,get_timestamp=get_timestamp, comments=curr_comments, get_votes=database.get_votes,postid=postid,session=session) 
    else:
        rated()
        postid = postid
        if "content" in request.form:
            content = request.form['content']
            if "username" in session:
                author = session['username'] 
                user = database.get_user(author)
                database.add_comment(None, content, postid, author)
                users.update(
                user,
                    {'$push':{'comments':postid}}
                )
                #return redirect(url_for("post",postid=postid,session=session))

        #return redirect(url_for("post",postid=postid))
        return redirect(url_for("post",postid=postid,session=session))

@app.route('/search', methods = ['GET','POST'])
def search():
    rated()
    error = ""
    if request.method == "POST":
        #location = request.form['query']
        #response = database.search(location)
        zipcode = request.form['zipcode']
        keywords = request.form['keyword']
        if zipcode == "":
            return render_template("400.html")
        if keywords != None:
            keywords = keywords.split()
        response = database.search(keywords, zipcode)
        print '~~~~~~~~~~~~~~~~~~~~~'
        print response
        if response != None:
            sortedlocs = database.sort_votes(response)
            if 'username' in session:
                rates = users.find_one({'username':session['username']})['rates']
                rates_str = [str(x) for x in rates]
                return render_template("results.html", locations=sortedlocs, session=session, users=users, get_timestamp=get_timestamp, get_votes=database.get_votes, rates=rates_str)
            return render_templates("results.html", session=session, users=users, locations=sortedlocs, get_timestamp=get_timestamp, get_votes=database.get_votes)
        else:
            error = "Location not found."
            return render_template("results.html", error=error)
    
@app.route('/submit', methods= ["GET", "POST"])
def submit():
    error = ""
    if request.method == "POST":
        name = request.form['locationName']
        address = request.form['streetAddress']
        zipcode = request.form['zipcode']
        desc = request.form['desc']
        postid = database.add_location(None, name, address, session['username'], zipcode, desc)  
        if postid:
            return redirect(url_for('post', postid=postid))
        print "The location already exists."
        return redirect(url_for("submit"))
    elif request.method == "GET":
        return render_template("submit.html")

@app.route('/login', methods = ["GET", "POST"])
@nologin
def login():
    error = ""
    if request.method == "POST":
        username = request.form['loginUsername'] #assuming SSL connection so this is okay
        password = request.form['loginPassword']
        #pass_hash = generate_password_hash(password) #wtf do I do with this
        #use check_password_hash(hash, password) to authenticate
        if database.check_login(username,password):
            session['username'] = username
            return redirect(url_for('index'))
        else: #invalid
            #message for invalid user/pass combo
            print "invalid login"
            
    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    session.pop('username',None)
    return redirect(url_for('index'))

@app.route('/register', methods=["GET","POST"])
@nologin
def register():
    if request.method == "POST":
        username = request.form['registerUsername']
        password = request.form['registerPassword']
        confirmPassword = request.form['confirmPassword']
        if database.check_username(username):
            if not password == confirmPassword: #passwords do not match
                print "passwords do not match"
                pass #need some kind of message
            else:
                database.register_user(username,password)
        else:
            #username is taken
            flash(username + " is taken!")
            #need some kind of message
            pass
    return render_template("register.html")

@app.route('/control',methods=["GET","POST"])
def control():
    if request.method == 'POST':
        if 'clear-users' in request.form:
            users.remove()
        elif 'delete-user' in request.form:
            _id = request.form['delete-user']
            users.remove({'_id':ObjectId(_id)})
        elif 'delete-location' in request.form:
            print "OK=================================="
            _id = request.form['delete-location']
            print _id
            print locations.remove({'_id':ObjectId(_id)})

    locationsf = locations.find()
    usersf = users.find()
    return render_template("control.html",session=session,locations=locationsf,users=usersf)
        
    locationsf = locations.find()
    usersf = users.find()
    #return render_template("control.html",session=session,locations=locations,users=users)
    return render_template("control.html",session=session,locations=locationsf,users=usersf)

@app.errorhandler(400)
def error400(e):
    return render_template('400.html'), 400

if __name__ == "__main__":
    app.debug = True
    #print client
    #print db
    #users.remove({'username':'CleverBot'})
    app.run(port=5005)

