# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import datetime
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))
    if req.get("result").get("action") == "trainStatus":
        res = processRequest(req)
    if req.get("result").get("action") == "trainRoute":
        res = processRoute(req)
    if req.get("result").get("action") == "stationCode":
        res = processCode(req)
    if req.get("result").get("action") == "trainArrival":
        res = processArrival(req)
    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def processCode(req):
    if req.get("result").get("action") != "stationCode":
        return {}
#     baseurl = "https://api.railwayapi.com/v2/name-to-code/station/"
#     remain = "/apikey/e5hkcdzqsj"
    baseurl = "https://api.railwayapi.com/v2/suggest-station/name/"
    remain = "/apikey/e5hkcdzqsj"
    yql_query = makeQueryForPlace(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + yql_query + remain
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResult3(data)
    return res

def processArrival(req):
    if req.get("result").get("action") != "trainArrival":
        return {}
    baseurl = "https://api.railwayapi.com/v2/arrivals/station/"
    remain = "/hours/4/apikey/0v40s8kpt1"
    yql_query = makeYqlQueryArrival(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + yql_query + remain
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResult5(data)
    return res


def processRoute(req):
    if req.get("result").get("action") != "trainRoute":
        return {}
    baseurl = "https://api.railwayapi.com/v2/route/train/"
    remain = "/apikey/e5hkcdzqsj"
    yql_query = makeYqlQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + yql_query + remain
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResult2(data)
    return res


def processRequest(req):
    if req.get("result").get("action") != "trainStatus":
        return {}
    baseurl = "https://api.railwayapi.com/v2/live/train/" 
    i = datetime.datetime.now()
    day = i.day 
    month = i.month 
    year = i.year
    today = "10-04-2018"
    remain = "/date/"+today+"/apikey/e5hkcdzqsj/"
    yql_query = makeYqlQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + yql_query + remain
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResult1(data)
    return res


def makeWebhookResult1(data):

    speech = data.get('position')
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "webhook-dm"
    }
def makeWebhookResult2(data):

#     speech = data.get('position')
    speech = ""
    for routes in data['route']:
        speech =  speech +routes['station']['name'] + " -> "
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "webhook-dm"
    }

def makeWebhookResult3(data):

    speech = ""
    for station in data['stations']:
        speech =  speech + station['name'] +"  -  "+ station['code'] + "\n"
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "webhook-dm"
    }


def makeWebhookResult5(data):
    
    speech = ""
    for code in data['trains']:
        speech =  speech + code['name'] +"is with scheduled arrival of "+ 
        code['scharr'] +" and scheduled departure of "+ code['schdep'] +
        "with delayed departure of train as"+ code['delaydep']
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "webhook-dm"
    }

def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    trainnum = parameters.get("Train")
    if trainnum is None:
        return None
    return trainnum

def makeYqlQueryArrival(req):
    result = req.get("result")
    parameters = result.get("parameters")
    traincode = parameters.get("Station_code_letters")
    if traincode is None:
        return None
    return traincode

def makeQueryForPlace(req):
    result = req.get("result")
    parameters = result.get("parameters")
    trainnum = parameters.get("geo-city")
    if trainnum:
        return trainnum
    trainnum2 = parameters.get("place") 
    if trainnum2:
        return trainnum2
    return {}

def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Today the weather in " + location.get('city') + ": " + condition.get('text') + \
             ", And the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')

