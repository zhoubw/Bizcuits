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
        if "username" in session:
            user = database.get_user(session['username'])
            if "upvote" in request.form:
                _id = request.form['upvote']
                loc = database.get_location(_id)
                locations.update(loc,{'$pull':{'downvotes':user['_id']},'$push':{'upvotes':user['_id']}},upsert=False,multi=False)
                #locations.update(loc,{'$push':{'upvotes':user['_id']}},upsert=False,multi=False)
            elif "downvote" in request.form:
                _id = request.form['downvote']
                loc = database.get_location(_id)
                locations.update(loc,{'$pull':{'upvotes':user['_id']},'$push':{'downvotes':user['_id']}},upsert=False,multi=False)
                #locations.update(loc,{'$push':{'downvotes':user['_id']}},upsert=False,multi=False)

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
        user = database.get_user(session['username']);
        return render_template("front.html", session=session,users=users,locations=locs,get_timestamp=get_timestamp, get_votes=database.get_votes_pst,user=user)
    return render_template("front.html", session=session,users=users,locations=locs,get_timestamp=get_timestamp, get_votes=database.get_votes_pst)

@app.route('/account', methods=["GET", "POST"])
@login_required
def account():
    error=""
    isError=False
    success=""
    isSuccess=False
    if request.method == "POST":
        newPass = request.form['newPass']
        confirmNewPass = request.form['confirmNewPass']
        oldPass = request.form['oldPass']
        if newPass == "" or confirmNewPass == "" or oldPass == "":
            error = "Did you remember to fill out the entire form? (no)"
            isError=True
        elif newPass!= confirmNewPass:
            error = "Your passwords don't match. Please try again!"
            isError=True
        elif not database.check_login(session['username'], oldPass):
            error = "You typed in the wrong password..."
            isError=True
        else:
            success = "Okay! Your password has now been successfully changed."
            isSuccess=True
            database.set_password(session['username'], newPass)
            print newPass
    return render_template("account.html", error=error, success=success, isError=isError, isSuccess=isSuccess)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/myposts')
@login_required
def myposts():
    return render_template("myposts.html")

@app.route('/post/<postid>', methods=["GET","POST"])
def post(postid=None):
    isError = False
    error = ""
    curr_loc = database.get_location(postid)
    print curr_loc
    curr_comments = database.get_comments(postid)
    if request.method == "GET":
        if 'username' in session:
            user = database.get_user(session['username']);
            return render_template("post.html", location=curr_loc,get_timestamp=get_timestamp, comments=curr_comments, get_votes=database.get_votes_pst,postid=postid,session=session,user=user) 
        return render_template("post.html", location=curr_loc,get_timestamp=get_timestamp, comments=curr_comments, get_votes=database.get_votes_pst,postid=postid,session=session) 
    else:
        if 'username' in session:
            user=database.get_user(session['username']);
        rated()
        postid = postid
        if "content" in request.form:
            content = request.form['content']
            if content == "":
                error = "You didn't write anything!"
                isError=True
                return render_template("post.html", error=error, isError=isError, location=curr_loc, get_timestamp=get_timestamp, comments=curr_comments, get_votes=database.get_votes, postid=postid, session=session, user=user)
            elif "username" in session:
                author = session['username'] 
                user = database.get_user(author)
                database.add_comment(None, content, postid, author)
                users.update(
                user,
                    {'$push':{'comments':postid}}
                )
                #return redirect(url_for("post",postid=postid,session=session))

        #return redirect(url_for("post",postid=postid))
    return redirect(url_for("post",postid=postid,session=session, isError=isError, error=error))

@app.route('/search', methods = ['GET','POST'])
def search():
    error = ""
    isError=False
    if request.method == "POST":
        #location = request.form['query']
        #response = database.search(location)
        zipcode = request.form['zipcode']
        keywords = request.form['keyword']
        if zipcode == "":
            error = "You forgot to enter a zipcode!"
            isError=True
            return render_template("results.html", error=error, isError=isError)
        if keywords != None:
            keywords = keywords.split()
        response = database.search(keywords, zipcode)
        print '~~~~~~~~~~~~~~~~~~~~~'
        print response
        if response != []:
            sortedlocs = database.sort_votes(response)
            return render_template("results.html", session=session, users=users, locations=sortedlocs, get_timestamp=get_timestamp, get_votes=database.get_votes_pst, isError=isError)
        else:
            error = "There aren't any Bizcuits in this location yet."
            isError=True
    return render_template("results.html", error=error, isError=isError)
    
@app.route('/submit', methods= ["GET", "POST"])
@login_required
def submit():
    error = ""
    isError = False
    if request.method == "POST":
        name = request.form['locationName']
        address = request.form['streetAddress']
        zipcode = request.form['zipcode']
        desc = request.form['desc']
        if name == "" or address == "" or zipcode == ""  or desc == "":
            error = "You forgot to fill out something!"
            return render_template("submit.html", error=error, isError=True)
        postid = database.add_location(None, name, address, session['username'], zipcode, desc)
        if postid:
            #submission should work here
            user = database.get_user(session['username'])
            users.update(user,{'$push':{'bizcuits':postid}})
            return redirect(url_for('post', postid=postid))
        print "The location already exists."
        return redirect(url_for("submit"))
    elif request.method == "GET":
        return render_template("submit.html", error=error, isError=isError)

@app.route('/login', methods = ["GET", "POST"])
@nologin
def login():
    isError=False
    error=""
    if request.method == "POST":
        username = request.form['loginUsername'] #assuming SSL connection so this is okay
        password = request.form['loginPassword'] #jk SSL certs cost money
        if database.check_login(username,password):
            session['username'] = username
            return redirect(url_for('index'))
        else: #invalid
            print "invalid login"
            isError=True
            error="Wrong username or password. Please try again!"
    return render_template("login.html", error=error, isError=isError)

@app.route('/logout')
@login_required
def logout():
    session.pop('username',None)
    return redirect(url_for('index'))

@app.route('/register', methods=["GET","POST"])
@nologin
def register():
    isSuccess=False
    isError=False
    success=""
    error=""
    if request.method == "POST":
        username = request.form['registerUsername']
        password = request.form['registerPassword']
        confirmPassword = request.form['confirmPassword']
        if username=="" or password=="" or confirmPassword=="":
            isError=True
            error="You forgot to fill out some required things..."
        elif database.check_username(username):
            if not password == confirmPassword: #passwords do not match
                isError=True
                error="Passwords do not match!"
            else:
                database.register_user(username,password)
                isSuccess=True
                success="Great! You have now successfully registered, "
                success=success+username
        else:
            #username is taken
            isError=True
            error="Sorry, your username is already in use!"
    return render_template("register.html", isError=isError, isSuccess=isSuccess, success=success, error=error)

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

@app.errorhandler(404)
def error404(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.debug = True
    #print client
    #print db
    #users.remove({'username':'CleverBot'})
    app.run(port=5005)

