import paho.mqtt.client as mqtt

from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes

import json

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
    'weather': None,
    'location': location,
    'priority': None,
    'travel': None,
    'appointment': None
}
 

#requests time when welcome message should be played
#time is defined in preference in the main process
def request_welcomeTime(client):
    client.publish(topic_list['welcome']['request'])

#request current weather data from weather service
#WIP
def request_weather(client):
    client.publish(topic_list['weather']['request'])
    pass

#request location of common places (e.g. home, work, uni)
def request_location(client):
    client.publish(topic_list['location']['request'])
    pass

#request travel priority by which the user prefers to travel
def request_priority(client):
    client.publish(topic_list['priority']['request'])
    pass

def request_rideTime(client):
    message = ''
    vehicle = data['priority'][0]

    #dependend on transport option different data is required for a request
    if vehicle == 'car' or vehicle == 'walk' or vehicle == 'bicycle':
        message = str({
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
        message = str({"from":location['home']['publicID'],"to": location['uni']['publicID'],"transportType":vehicle})
            
    print("DEBUG ", __file__, ": ", message)
    client.publish(topic_list['ride']['request'], json.dumps(message, indent=3))


def request_appointment():
    pass