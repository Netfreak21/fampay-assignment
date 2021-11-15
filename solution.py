# your code goes here
import requests
import threading
from pymongo import MongoClient
from flask import Flask
from flask import jsonify,request
import json
import re

nPerPage = 10

def connect_mongo():
    client = MongoClient('localhost', 27017)
    return client

client = connect_mongo()

app = Flask(__name__)
@app.route('/api/v1/getList/',methods=['GET'])
def getList():
    pageNumber = request.args['pageNumber']
    pageNumber = int(pageNumber)
    responseList = []
    for entry in client['youtube_database'].youtubeTable.find().skip((pageNumber-1)*nPerPage).limit(nPerPage):
       responseList.append(str(entry))    
    return str(responseList)

@app.route('/api/v1/searchList',methods=['GET'])
def searchList():
    pageNumber = request.args['pageNumber']
    pageNumber = int(pageNumber)
    query = request.args['query']
    responseList = []
    regex = re.compile(query,re.IGNORECASE)
    for entry in client['youtube_database'].youtubeTable.find({"$or": [{"title": regex}, {"description": regex}]}).skip((pageNumber-1)*nPerPage).limit(nPerPage):
       responseList.append(str(entry))    
    return str(responseList)


class Data :
    def _init_(publishTime,title,description,thDefault,thMedium,thHigh):
        self.publishTime = publishTime
        self.title = title
        self.description = description
        self.thDefault = thDefault
        self.thMedium = thMedium
        self.thHigh = thHigh
    
def insertToMongo(entry,client):
    client['youtube_database'].youtubeTable.insert_one(entry.__dict__)
    print(client['youtube_database'].youtubeTable.find_one({'title': entry.title}))
    
n = 4
def f(f_stop,client):
    # do something here ...
    response = requests.get('https://youtube.googleapis.com/youtube/v3/search?key=AIzaSyBaa3yxBprIXotlsR5-Nca9B69peZ43gus&q=subhanallah&part=snippet&order=date')
    response = response.json()
    for x in response["items"]:
        y = Data()
        y.publishTime = x["snippet"]['publishTime']
        y.title = x["snippet"]['title']
        y.description = x["snippet"]['description']
        y.thDefault = x["snippet"]['thumbnails']['default']
        y.thMedium = x["snippet"]['thumbnails']['medium']
        y.thHigh = x["snippet"]['thumbnails']['high']
        insertToMongo(y,client)
        print(y.publishTime)
    
    for i in range(4) :
        response = requests.get('https://youtube.googleapis.com/youtube/v3/search?key=AIzaSyBaa3yxBprIXotlsR5-Nca9B69peZ43gus&q=subhanallah&part=snippet&order=date&pageToken='+response['nextPageToken'])
        response = response.json()
        for x in response["items"]:
            y = Data()
            y.publishTime = x["snippet"]['publishTime']
            y.title = x["snippet"]['title']
            y.description = x["snippet"]['description']
            y.thDefault = x["snippet"]['thumbnails']['default']
            y.thMedium = x["snippet"]['thumbnails']['medium']
            y.thHigh = x["snippet"]['thumbnails']['high']
            insertToMongo(y,client)

    if not f_stop.is_set():
        # call f() again in 10 seconds
        threading.Timer(60, f, [f_stop,client]).start()
        
app.run(debug = True)
f_stop = threading.Event()

# start calling f now and every 60 sec thereafter
f(f_stop,client)

# stop the thread when needed
#f_stop.set()