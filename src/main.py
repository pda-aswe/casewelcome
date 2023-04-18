#!/usr/bin/python3

import paho.mqtt.client as mqtt

import time
import json

from datetime import datetime

import re

from data import topic_list, location, data
from messenger import *

def on_connect(client,userdata,flags, rc):
    #Subscribe to topic to receive response-messages
    for topic in topic_list:
        client.subscribe((topic_list[topic]['response'], 0))

#Diese Funktion wird aufgerufen, wenn es für ein Topic kein spezielles Callback gibt
def on_message(client, userdata, msg):
    print("MESSAGE ", __file__, ": ", "Topic", msg.topic, " Payload:", str(msg.payload.decode("utf-8"))),

    #welcomeTime: time welcome message should be played
    if topic_list['welcome']['response'] == msg.topic:
        welcomeTime = datetime.strptime(str(msg.payload.decode("utf-8")),'%H:%M')
        data['start'] = welcomeTime.strftime('%H:%M')

    elif msg.topic == topic_list['weather']['response']:
        print("Weather: ", str(msg.payload.decode("utf-8")))
        data['weather'] = json.loads(msg.payload.decode("utf-8"))

    #location: location data required for requesting rideTime
    elif msg.topic.__contains__(topic_list['location']['root']):
        #get location and type of data from topic path to access the location dictionary
        subpath = re.sub(topic_list['location']['root'],'',msg.topic)
        place = re.sub('/.+', '', subpath)
        type = re.sub('.+/', '', subpath)

        #check whether data has to be saved as a float or string
        if type == 'lat' or type == 'long':
            location[place][type] = float(msg.payload.decode("utf-8"))
        else:
            location[place][type] = str(msg.payload.decode("utf-8"))
        
    #priority: which transport option is prefered
    elif msg.topic == topic_list['priority']['response']:
        data['priority'] = json.loads(msg.payload.decode("utf-8"))

    #ride: returns time for users daily commute from home to uni/work
    elif msg.topic == topic_list['ride']['response']:
        data['travel'] = json.loads(msg.payload.decode("utf-8"))
        #Cut out everything except travelTime 
        data['travel'] = data['travel']['travelTime']

    #appointment: appointments the user has for the day
    elif msg.topic == topic_list['appointment']['response']:
        data['event'] = json.loads(msg.payload.decode("utf-8"))
        #Cut out everything except events
        data['event'] = data['event']['events']

def function2Test():
    return True

def prep_weather_data():
    return ('In ' + data['weather']['location'] + \
            ' wird das Wetter heute ' + data['weather']['description'] + '.' + \
            ' Heute wird eine Temperatur von ' + str(data['weather']['temperature']) + \
            ' Grad Celcius erwarted mit einer Feuchtigkeit von ' + str(data['weather']['humidity']) + \
            ' Prozent. ')

def prep_travel_data():
    if data['travel']:
        return 'Deine vorraussichtliche Reisezeit beträgt ' + str(int(data['travel']/60)) + ' Minuten. '
    else:
        return 'Es konnte keine Prognose zur heutigen Reisezeit ermittelt werden. '

def prep_event_data():
    if data['event'] is not []:    
        msg = 'Heute stehen folgende Termine an: '
        print("Event :", data['event'])
        for event in data['event']:
            #start of event
            start = datetime.strptime(event['start'], '%Y-%m-%dT%H:%M:%S%z')
            msg += 'Von ' + str(start.strftime('%H:%M')) + ' '

            #end of event
            end = datetime.strptime(event['end'], '%Y-%m-%dT%H:%M:%S%z')
            msg += 'bis ' + str(end.strftime('%H:%M')) + ' '

            #event location
            if event['location'] != '':
                msg += 'in ' + event['location'] + ' '

            #event summary
            msg += 'hast du ein Termin für ' + event['summary']
            msg +='. '

        return msg
    else:
        return 'Es stehen für heute keine Termine an.'


if __name__ == "__main__": # pragma: no cover      
    #connect to mqtt 
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    #configer and connect docker-container with mqttt
    mqtt_address = getEnvironment()
    client.connect(mqtt_address,1883,60)
    client.loop_start()
    time.sleep(2)

    #when should message be played
    request_welcomeTime(client)   
    #initialize for loop comparison
    data['lastWelcome'] = datetime(1970, 1, 1)

    while True:
        #get current date and time
        now = datetime.now()
        
        #below line only for testing purposes
        now = now.replace(day=18)
        
        currentTime = now.strftime('%H:%M')

        #for multiple repetisions:
        if currentTime != data['start']:
        #check if currentTime is welcomeTime and if welcomeMessage was already played 
        #if currentTime == data['start'] and data['lastWelcome'] != now.date():
            #update last date welcomeTime is played to prevent second excecution
            data['lastWelcome'] = now.date()   

            #get required data for welcome message 
            request_weather(client)                      
            request_priority(client)                        
            request_location(client)                         
            request_appointment(client, now.date())          

            #wait till required date is initialized
            start_time = time.time()
            passed = 0.0
            while data['priority'] is None or passed > 3.0:
                end_time = time.time()
                passed = end_time - start_time
                pass 

            #if priority data is still none, skip rideTime request
            if data['priority'] is not None:
                request_rideTime(client)    

            #wait a bit for message to come in 
            time.sleep(3)

            #prepare data
            msg_weather = prep_weather_data()
            msg_travel  = prep_travel_data()
            msg_event   = prep_event_data()

            #build tts message and publish message to tts
            tts = "Guten Morgen, es ist " + \
                currentTime + ". " + \
                msg_weather + \
                msg_travel + \
                msg_event + \
                "Das war alles. Ich wünsche dir noch einen schönen Tag."
            
            print("OUTPUT ", __file__, ": ", tts)
            client.publish('tts', tts)

        #wait some time before polling again
        time.sleep(15)

    #Sollte am Ende stehen, da damit die MQTT-Verbindung beendet wird
    client.loop_stop()
    client.disconnect()