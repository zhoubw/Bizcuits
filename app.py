from pymongo import MongoClient
from flask import Flask, render_template, request, redirect, session, url_for, escape, flash
from datetime import datetime

import database

app = Flask(__name__)

client = MongoClient('mongodb://Citronnade:Citronnade@ds031271.mongolab.com:31271/softdev2015')
db = client['softdev2015']
locations = db['locations']

# db = client.test_database
# Possible documents:
# - Idea posts
# - Comment chains

app.secret_key = "c~9%1.p4IUDj2I*QYHivZ73/407E]7<f1o_5b1(QzNdr00m7Tit)[T>C;2]5"


@app.route('/')
def index():
    return render_template("index.html")

@app.route("/front")
#@app.route("/")
def front():
    return render_template("front.html")

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

if __name__ == "__main__":
    app.debug = True
    print client
    print db
    app.run(port=5005)

