import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as subscribe
import paho.mqtt.publish as publish

from multiprocessing import Process, Queue
from datetime import datetime

import json
import os
import re

from data import Data

from singleton import SingletonMeta

class Messenger(metaclass=SingletonMeta):
    def __init__(self):      
        self.connected = False
        self.mqtt_address = ''
        self.data = Data()

        #connect to mqtt 
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def get_data(self):
        return self.data
    
    def get_mqtt_address(self):
        return self.mqtt_address

    def get_environment(self):
        docker_container = os.environ.get('DOCKER_CONTAINER', False)
        if docker_container:
            mqtt_address = "broker"
        else:
            mqtt_address = "localhost"
        return mqtt_address

    def connect(self):
        if not self.connected:
            try:
                self.mqtt_address = self.get_environment()
                self.client.connect(self.mqtt_address, 1883, 60)
                self.client.loop_start()
                self.connected = True
            except:
                return False
        return True

    def disconnect(self):
        if self.connected:
            self.connected = False
            self.client.loop_stop()
            self.client.disconnect()
        return True
    
    def _on_connect(self, client, userdata, flags, rc):
        for topic in self.data.topic_list:
            self.client.subscribe((self.data.topic_list[topic]['response'], 0))
    
    def request(self,requestTopic,responseTopic,data=None):
        q = Queue()
        process = Process(target=mqttRRP,args=(q,requestTopic,responseTopic,data))
        process.start()
        process.join(timeout=3)
        process.terminate()

    def _on_message(self,client, userdata,msg):
        print("DEBUG: ", __file__, 'Messsage from ', msg.topic, ' contains: ', str(msg.payload.decode("utf-8")))
        #welcomeTime: time welcome message should be played
        if msg.topic == self.data.topic_list['welcome']['response']:
            welcomeTime = datetime.strptime(str(msg.payload.decode("utf-8")),'%H:%M')
            self.data.data['start'] = welcomeTime.strftime('%H:%M')

        elif msg.topic == self.data.topic_list['weather']['response']:
            self.data.data['weather'] = json.loads(msg.payload.decode("utf-8"))

        #location: location data required for requesting rideTime
        elif msg.topic.__contains__(self.data.topic_list['location']['root']):
            subpath = re.sub(self.data.topic_list['location']['root'],'',msg.topic)
            place = re.sub('/.+', '', subpath)
            type = re.sub('.+/', '', subpath)

            if type == 'lat' or type == 'long':
                self.data.location[place][type] = float(msg.payload.decode("utf-8"))
            else:
                self.data.location[place][type] = str(msg.payload.decode("utf-8"))
            
        #priority: which transport option is prefered
        elif msg.topic == self.data.topic_list['priority']['response']:
            self.data.data['priority'] = json.loads(msg.payload.decode("utf-8"))

        #ride: returns time for users daily commute from home to uni/work
        elif msg.topic == self.data.topic_list['ride']['response']:
            self.data.data['travel'] = json.loads(msg.payload.decode("utf-8"))
            self.data.data['travel'] = self.data.data['travel']['travelTime']

        #appointment: appointments the user has for the day
        elif msg.topic == self.data.topic_list['appointment']['response']:
            self.data.data['event'] = json.loads(msg.payload.decode("utf-8"))
            self.data.data['event'] = self.data.data['event']['events']

        else:
            return(False)

    def publish_to_tts(self,msg):
        self.client.publish('tts',msg)

    def request_welcomeTime(self):
        return self.request(self.data.topic_list['welcome']['request'],self.data.topic_list['welcome']['response'])

    def request_weather(self):
        return self.request(self.data.topic_list['weather']['request'],self.data.topic_list['weather']['response'])

    def request_location(self):
        return self.request(self.data.topic_list['location']['request'],self.data.topic_list['location']['response'])
        #request travel priority by which the user prefers to travel
    def request_priority(self):
        return self.request(self.data.topic_list['priority']['request'],self.data.topic_list['priority']['response'])

        #request travel time, needs location and transport priority
    def request_rideTime(self):
        try:
            vehicle = self.data.data['priority'][0]

            #dependend on transport option different data is required for a request
            if vehicle == 'car' or vehicle == 'pedestrian' or vehicle == 'bicycle':
                message = json.dumps({
                    "from":{
                        "lat":self.data.location['home']['lat'],
                        "lon":self.data.location['home']['long']},
                    "to":{
                        "lat":self.data.location['uni']['lat'],
                        "lon":self.data.location['uni']['long']},
                    "transportType":vehicle
                })

            #public transport required stationid from api, henceforth fixed ids are used
            elif vehicle == 'publicTransport':
                message = json.dumps({"from":self.data.location['home']['publicID'],"to":self.data.location['uni']['publicID'],"transportType":vehicle})
                    
            return self.request(self.data.topic_list['ride']['request'],self.data.topic_list['ride']['response'],message)
        except:
            return(False)

    def request_appointment(self,date):
        #Get all todays appointments from start to end of day
        startTime = str(date) + 'T00:00:00+02:00'
        endTime = str(date) + 'T23:59:59+02:00'
        message = json.dumps({'start':startTime,'end':endTime})

        return self.request(self.data.topic_list['appointment']['request'],self.data.topic_list['appointment']['response'], message)



def mqttRRP(q,requestTopic,responseTopic,data=None):
    docker_container = os.environ.get('DOCKER_CONTAINER', False)
    if docker_container:
        mqtt_address = "broker"
    else:
        mqtt_address = "localhost"

    if data is None:
        publish.single(requestTopic,hostname=mqtt_address,port=1883)
    else:
        publish.single(requestTopic,payload=data,hostname=mqtt_address,port=1883)
    mqttResponse = subscribe.simple(responseTopic,hostname=mqtt_address,port=1883).payload
    q.put(mqttResponse)