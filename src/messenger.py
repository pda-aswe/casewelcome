import paho.mqtt.client as mqtt

from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes

import json
import datetime

#Dict containing list of request-response topics
topic_list = {
    'welcome':{
        'request':'req/pref/welcomeTime',
        'response':'pref/welcomeTime' 
    },
    'location':{
        'request':'req/pref/location',
        'response':'pref/location/#',
        'root':'pref/location/'
    },
    'priority':{
        'request':'req/pref/transportPriority',
        'response':'pref/transportPriority'
    },
    'weather':{
        'request':'req/weather/now',
        'response':'weather/now' 
    },
    'ride':{
        'request':'req/rideTime',
        'response':'rideTime' 
    },
    'appointment':{
        'request':'req/appointment/range',
        'response':'appointment/range' 
    }
}

location = {
    "home": {
        "lat": None,
        "long": None,
        "publicID": None
    },
    "company": {
        "lat": None,
        "long": None,
        "publicID": None
    },
    "uni": {
        "lat": None,
        "long": None,
        "publicID": None
    }
}

data = {
    'start': None,
    'date': None,
    'lastWelcome': None,
    'weather': 'sonniger',
    'location': location,
    'priority': None,
    'travel': None,
    'event': None
}
 

#requests time when welcome message should be played
#time is defined in preference in the main process
def request_welcomeTime(client):
    print("PUBLISH ", __file__, ": Message sent to ", topic_list['welcome']['request'])
    client.publish(topic_list['welcome']['request'])

#request current weather data from weather service
#WIP
def request_weather(client):
    print("PUBLISH ", __file__, ": Message sent to ", topic_list['weather']['request'])
    client.publish(topic_list['weather']['request'])

#request location of common places (e.g. home, work, uni)
def request_location(client):
    print("PUBLISH ", __file__, ": Message sent to ", topic_list['location']['request'])
    client.publish(topic_list['location']['request'])

#request travel priority by which the user prefers to travel
def request_priority(client):
    print("PUBLISH ", __file__, ": Message sent to ", topic_list['priority']['request'])
    client.publish(topic_list['priority']['request'])

#request travel time, needs location and transport priority
def request_rideTime(client):
    message = ''
    vehicle = data['priority'][0]

    #dependend on transport option different data is required for a request
    if vehicle == 'car' or vehicle == 'pedestrian' or vehicle == 'bicycle':
        message = json.dumps({
            "from":{
                "lat":location['home']['lat'],
                "lon":location['home']['long']},
            "to":{
                "lat":location['uni']['lat'],
                "lon":location['uni']['long']},
            "transportType":vehicle
        })

    #public transport required stationid from api, henceforth fixed ids are used
    elif vehicle == 'publicTransport':
        message = json.dumps({"from":location['home']['publicID'],"to": location['uni']['publicID'],"transportType":vehicle})
            
    print("PUBLISH ", __file__, ": Message sent to ", topic_list['ride']['request'], "with message:", message)
    client.publish(topic_list['ride']['request'], message)


def request_appointment(client, date):
    startTime = str(date) + 'T00:00:00+02:00'
    endTime = str(date) + 'T23:59:59+02:00'
    message = json.dumps({'start':startTime,'end':endTime})

    print("PUBLISH ", __file__, ": Message sent to ", topic_list['appointment']['request'], "with message:", message)
    client.publish(topic_list['appointment']['request'], message)