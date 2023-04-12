#!/usr/bin/python3

import paho.mqtt.client as mqtt

import time
import json

from datetime import date
from datetime import datetime

import os
import re

import messenger

def on_connect(client,userdata,flags, rc):
    #Subscribe to topic to receive response-messages
    for topic in messenger.topic_list:
        client.subscribe((messenger.topic_list[topic]['response'], 0))
        print('Subscribed to Topic:', messenger.topic_list[topic]['response'])

#Diese Funktion wird aufgerufen, wenn es für ein Topic kein spezielles Callback gibt
def on_message(client, userdata, msg):
    print("Topic", msg.topic, " Payload:", str(msg.payload.decode("utf-8"))),

    #welcomeTime: time welcome message should be played
    if messenger.topic_list['welcome']['response'] == msg.topic:
        messenger.data['start'] = str(msg.payload.decode("utf-8"))

    #location: location data required for requesting rideTime
    elif msg.topic.__contains__(messenger.topic_list['location']['root']):
        #get location and type of data from topic path to access the location dictionary
        subpath = re.sub(messenger.topic_list['location']['root'],'',msg.topic)
        loc_place = re.sub('/.+', '', subpath)
        loc_data = re.sub('.+/', '', subpath)

        #check whether data has to be saved as a float or string
        if loc_data == 'lat' or loc_data == 'long':
            messenger.location[loc_place][loc_data] = float(msg.payload.decode("utf-8"))
        else:
            messenger.location[loc_place][loc_data] = str(msg.payload.decode("utf-8"))
        
    #priority: which transport option is prefered
    elif msg.topic == messenger.topic_list['priority']['response']:
        messenger.data['priority'] = json.loads(msg.payload.decode("utf-8"))

    #ride: returns time for users daily commute from home to uni/work
    elif msg.topic == messenger.topic_list['ride']['response']:
        print("Topic", msg.topic, " Payload:", str(msg.payload.decode("utf-8"))),

def specific_callback(client, userdata, msg):
    print("Specific Topic: "+ msg.topic+" "+str(msg.payload))

def function2Test():
    return True

if __name__ == "__main__": # pragma: no cover      
    #connect to mqtt 
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    #configer and connect docker-container with mqttt
    docker_container = os.environ.get('DOCKER_CONTAINER', False)
    if docker_container:
        mqtt_address = "broker"
    else:
        mqtt_address = "localhost"
    client.connect(mqtt_address,1883,60)
    client.loop_start()
    time.sleep(2)

    #retrieve time when welcome message should be played
    messenger.request_welcomeTime(client)   

    #Hier kann der eigene Code stehen. Loop oder Threads
    while True:
        #get current date and time each loop
        c_dateTime = datetime.now()
        #retrieve hour and time to compare
        current_time = str(c_dateTime.time())[0:5]
        #check if currentTime is welcomeTime and if welcomeMessage was already played 
        if current_time == messenger.data['start'] and messenger.data['lastdate'] != c_dateTime.date():
            #update last date welcomeTime is played to prevent second excecution
            messenger.data['lastdate'] = c_dateTime.date()   

            #get required data for welcome message 
            #messenger.request_weather(client)      #weather: WIP
            messenger.request_priority(client)      #transport priority
            messenger.request_location(client)      #location
            messenger.request_appointment(client)   #todays appointments: WIP

            #empty loop waits until priority and location are filled with data
            #otherwise it may happen that request is send before data of priority and location are aquired
            while messenger.data['priority'] == None and None not in messenger.data['location'].values():
                ()
            messenger.request_rideTime(client)      #ride time from home to uni
           
            #build tts message and publish message to tts
            tts = "Guten Morgen, es ist " + messenger.data['start']
            client.publish('tts', str)

        #wait some time before polling again
        time.sleep(30)

    #Sollte am Ende stehen, da damit die MQTT-Verbindung beendet wird
    client.loop_stop()
    client.disconnect()