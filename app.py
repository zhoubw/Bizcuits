from pymongo import MongoClient
from flask import Flask, render_template, request, redirect, session, url_for, escape, flash
from datetime import datetime

app = Flask(__name__)

client = MongoClient()

# db = client.test_database
# Possible documents:
# - Idea posts
# - Comment chains

app.secret_key = "c~9%1.p4IUDj2I*QYHivZ73/407E]7<f1o_5b1(QzNdr00m7Tit)[T>C;2]5"

if __name__ == "__main__":
    app.debug = True
    app.run(port=5005)
