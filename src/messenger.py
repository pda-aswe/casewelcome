import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as subscribe
import paho.mqtt.publish as publish

from multiprocessing import Process, Queue

import json
import os

from data import topic_list, location, data

#requests time when welcome message should be played
#time is defined in preference in the main process
def request_welcomeTime(client):
    return __request(client,topic_list['welcome']['request'],topic_list['welcome']['response'])

#request current weather data from weather service
def request_weather(client):
    return __request(client,topic_list['weather']['request'],topic_list['weather']['response'])

#request location of common places (e.g. home, work, uni)
def request_location(client):
    return __request(client,topic_list['location']['request'],topic_list['location']['response'])

#request travel priority by which the user prefers to travel
def request_priority(client):
    return __request(client,topic_list['priority']['request'],topic_list['priority']['response'])

#request travel time, needs location and transport priority
def request_rideTime(client):
    try:
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
            
        return __request(client,topic_list['ride']['request'],topic_list['ride']['response'],message)
    except:
        return(False)

def request_appointment(client, date):
    #Get all todays appointments from start to end of day
    startTime = str(date) + 'T00:00:00+02:00'
    endTime = str(date) + 'T23:59:59+02:00'
    message = json.dumps({'start':startTime,'end':endTime})

    return __request(client,topic_list['appointment']['request'],topic_list['appointment']['response'], message)

#Request data with request-response-pattern
def __request(self,requestTopic,responseTopic, data=None):
    q = Queue()
    process = Process(target=mqttRRP, args=(q,requestTopic,responseTopic, data))
    process.start()
    process.join(timeout=3)
    process.terminate()
    print("PUBLISH ", __file__, ": Message sent to ", requestTopic, ", listen to ", responseTopic)

    if process.exitcode == 0:
        try:
            mqttData = q.get(timeout=1)
            return mqttData
        except:
            return(False)
        
#Build mqtt-reponse-request
def mqttRRP(q,requestTopic,responseTopic, data=None):
    mqtt_address = getEnvironment()
    if data is None:
        publish.single(requestTopic,hostname=mqtt_address,port=1883)
    else:
        publish.single(requestTopic,payload=data,hostname=mqtt_address,port=1883)
    mqttResponse = subscribe.simple(responseTopic,hostname=mqtt_address,port=1883).payload
    q.put(mqttResponse)

# Get docker environment
def getEnvironment():
    docker_container = os.environ.get('DOCKER_CONTAINER', False)
    if docker_container:
        mqtt_address = "broker"
    else:
        mqtt_address = "localhost"
    return mqtt_address