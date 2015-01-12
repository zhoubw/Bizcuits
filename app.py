from pymongo import MongoClient
from flask import Flask, render_template, request, redirect, session, url_for, escape, flash
from datetime import datetime

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

@app.route('/search', methods = ['POST'])
def search():
    error = ""
    if request.method == "POST":
        location = request.form['location']
        response = locations.find_one({"name": location})
        if response != None:
            return render_template("results.html", location=response)
        else:
            error = "Location not found."
            return render_template("results.html", error=error)
    return "HELP WHAT DO AHHHHHHHHHHH"
    
@app.route('/add', methods= ["GET", "POST"])
def add():
    error = ""
    if request.method == "POST":
        name = request.form['name']
        address = request.form['address']
        try:
            location = {'name': name, 'address': address}
            location_id = locations.insert(location)
            return "Successfully added " + location.name + "!"
        except:
            return "Location already in database."
    elif request.method == "GET":
        return render_template("add.html")

if __name__ == "__main__":
    app.debug = True
    print client
    print db
    app.run(port=5005)

