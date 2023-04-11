#!/usr/bin/python3

import paho.mqtt.client as mqtt

from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes

import time

from datetime import date
from datetime import datetime

import os

#Dict containing list of request-response topics
topic_list = {
    'welcome':[
        'req/pref/welcomeTime',
        'pref/welcomeTime' 
    ],
    'weather':[
        'req/weather/now',
        'weather/now' 
    ],
    'ride':[
        'req/rideTime',
        'rideTime' 
    ],
    'appointment':[
        'req/appointment/range',
        'appointment/range' 
    ]
}

data = {
    'start': None,
    'date': None,
    'lastdate': None,
    'weather': None,
    'travel': None,
    'appointment': None
}
 
def on_connect(client,userdata,flags, rc):
    #Subscribe to topic to receive response-messages
    for cat in topic_list:
        client.subscribe((topic_list[cat][1], 0))
        print('Subscribed to Topic:',topic_list[cat][1])

#Diese Funktion wird aufgerufen, wenn es für ein Topic kein spezielles Callback gibt
def on_message(client, userdata, msg):
    if topic_list['welcome'][1] == msg.topic:
        data['start'] = str(msg.payload.decode("utf-8"))
        print(msg.topic+" "+str(msg.payload.decode("utf-8")))
    elif topic_list['weather'][1] == msg.topic:
        data['weather'] = str(msg.payload)
        print(msg.topic+" "+str(msg.payload))
    elif topic_list['ride'][1] == msg.topic:
        data['travel'] = str(msg.payload)
        print(msg.topic+" "+str(msg.payload))
    elif topic_list['appointment'][1] == msg.topic:
        data['appointment'] = str(msg.payload)
        print(msg.topic+" "+str(msg.payload))

def specific_callback(client, userdata, msg):
    print("Specific Topic: "+msg.topic+" "+str(msg.payload))

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
    time.sleep(5)

    #retrieve time when welcome message should be played
    client.publish(topic_list['welcome'][0])
    

    #Hier kann der eigene Code stehen. Loop oder Threads
    while True:
        c_dateTime = datetime.now()
        current_time = str(c_dateTime.time())[0:5]
        if current_time == data['start'] and data['lastdate'] != c_dateTime.date():
           data['lastdate'] = c_dateTime.date()   

           #get data for current date and time
           for topic in topic_list:
                if topic != 'welcome':
                    client.publish(topic_list[topic][0])    
           
           #tts aquired data
           str = "Guten Morgen, es ist " + data['start']
           client.publish('tts', str)
           

    #Sollte am Ende stehen, da damit die MQTT-Verbindung beendet wird
    client.loop_stop()
    client.disconnect()