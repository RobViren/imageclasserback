# [START app]
import logging

# [START imports]
from flask import Flask, render_template, jsonify, request, Response
from google.appengine.api import users
from google.appengine.ext import ndb
from flask_cors import CORS

import json, datetime
# [END imports]

class Image(ndb.Model):
    name = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    data = ndb.JsonProperty(repeated=True)

# [START create_app]
app = Flask(__name__)
CORS(app)
# [END create_app]

API_KEY = 'totallyanapikey'

@app.after_request
def apply_caching(response):
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1"
    response.headers["Strict-Transport-Security"] =  "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"

    return response

@app.route('/hello', methods=['GET'])
def hello():
    resp = Response("Hello")
    resp.status_code = 200
    return resp


@app.route('/api/v1/image', methods=['POST'])
def image_post():
    key = request.headers.get('API_KEY')
    if key == API_KEY:
        print "woop"
        if (request.is_json):
            print "woop"
            try:
                jdata = request.get_json()
                jdata['name']
            except:
                resp = Response('Must Include Image Name')
                resp.status_code = 400
                return resp
        else:
            resp = Response('Invalid JSON')
            resp.status_code = 400
            return resp

        qry = Image.query(Image.name == jdata['name'])
        res = qry.get()
        if(res):
            resp = Response('Name Allready Used')
            resp.status_code = 400
            return resp
        else:
            image = Image()
            image.name = jdata['name']
            image.put()
            resp = Response('OK')
            resp.status_code = 200
            return resp
    else :
        resp = Response('Invalid Key')
        resp.status_code = 400
        return resp

@app.route('/api/v1/image', methods=['GET'])
def images_get():
    key = request.headers.get('API_KEY')
    limit = request.args.get('limit')

    if key == API_KEY:
        qry = Image.query()
        if limit:
            res = qry.fetch(limit, keys_only=False)
        else :
            res = qry.fetch(100, keys_only=False)
        rows = [row.to_dict() for row in res]
        resp = jsonify(rows)
        resp.status_code = 200
        return resp
    else :
        resp = Response('Invalid Key')
        resp.status_code = 400
        return resp

@app.route('/api/v1/image/names', methods=['GET'])
def names_get():
    limit = request.args.get('limit')

    qry = Image.query()
    if limit:
        res = qry.fetch(limit, keys_only=False)
    else :
        res = qry.fetch(100, keys_only=False)
    rows = [row.to_dict() for row in res]
    names = []
    for val in rows:
        names.append(val['name'])
    resp = jsonify(names)
    resp.status_code = 200
    return resp


@app.route('/api/v1/image', methods=['PUT'])
def image_put():
    if (request.is_json):
        jdata = request.get_json()
        try:
            jdata['data']
            jdata['name']
        except:
            resp = Response('Must Include Name and Data')
            resp.status_code = 400
            return resp

        qry = Image.query(Image.name == jdata['name'])
        res = qry.get()
        if(res):
            res.data.append(jdata['data'])
            res.put()
        else:
            resp = Response('Image Name Does Not Exist')
            resp.status_code = 400
            return resp

    else:
        resp = Response('Must Be JSON Format. Check Headers')
        resp.status_code = 400
        return resp

    resp = Response('OK')
    resp.status_code = 200
    return resp

@app.route('/api/v1/image', methods=['DELETE'])
def image_delete():
    name = request.args.get('name')
    if name:
        qry = Image.query(Image.name == name)
        res = qry.get()
        print res
        if(res):
            try:
                res.key.delete()
            except:
                resp = Response('Cannot Delete')
                resp.status_code = 400
                return resp
                
            resp = Response('OK')
            resp.status_code = 200
            return resp

        else:
            resp = Response('Image Name Does Not Exist')
            resp.status_code = 400
            return resp
    else:
        resp = Response('Must include name')
        resp.status_code = 400
        return resp
