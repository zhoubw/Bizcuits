from pymongo import MongoClient
from flask import Flask, render_template, request, redirect, session, url_for, escape, flash
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

import database

app = Flask(__name__)

client = MongoClient('mongodb://Citronnade:Citronnade@ds031271.mongolab.com:31271/softdev2015')
db = client['softdev2015'] #database in softdev2015
locations = db['locations'] #collection
users = db['users'] #collection

# Possible documents/collections:
# - Idea posts
# - Comment chains

app.secret_key = "c~9%1.p4IUDj2I*QYHivZ73/407E]7<f1o_5b1(QzNdr00m7Tit)[T>C;2]5"

#login/home page should be front page
#@app.route('/')
#def index():
#    return render_template("deadfront.html")

<<<<<<< HEAD
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
            pass
            return redirect(url_for("home")) # I have no idea what it is yet
        return f(*args, **kwargs)
    return inner

    

@app.route("/front", methods = ['POST'])
@app.route("/", methods = ['POST'])
def front():
    if request.method == "POST":
        query = request.form['query']
        if query == "":
            #error
            return render_template("deadfront.html") #testing
        return render_template("search_results.html", query=query)
    return render_template("deadfront.html") #testing

#this will probably be gone
=======
@app.route('/')
@app.route('/index')
def index():
    #return render_template("index.html")
    return render_template("front.html")

@app.route('/testing')
def test():
    return render_template("front1.html")

>>>>>>> origin/frontling
@app.route('/search', methods = ['POST'])
def search():
    error = ""
    if request.method == "POST":
        location = request.form['query']
        response = database.search(location)
        if response != None:
            return render_template("results.html", location=response)
        else:
            error = "Location not found."
            return render_template("results.html", error=error)
    
@app.route('/add', methods= ["GET", "POST"])
def add():
    error = ""
    if request.method == "POST":
        name = request.form['name']
        address = request.form['address']
        location = {'name': name, 'address': address}
        if locations.find_one({"name": location}) != None:
            location_id = locations.insert(location)
            return "Successfully added " + location['name'] + "!"
        else:
            return "Location already in database."
    elif request.method == "GET":
        return render_template("add.html")

@app.route('/login', methods = ["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        user = request.form['user'] #assuming SSL connection so this is okay
        password = request.form['password']
        pass_hash = generate_password_hash(password)
        #use check_password_hash(hash, password) to authenticate
    return render_template("login.html")

@app.route('/register', methods=["GET","POST"])
def register():
    return render_template("register.html")


if __name__ == "__main__":
    app.debug = True
    print client
    print db
    app.run(port=5005)

