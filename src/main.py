#!/usr/bin/python3
import time

from datetime import datetime, timedelta

import messenger

if __name__ == "__main__": # pragma: no cover
    mqttConnection = messenger.Messenger()
    if not mqttConnection.connect():
        print('no mqtt broker running')
        quit()

    mqttConnection.request_welcomeTime()
    while True:
        #get current date and time
        now = datetime.utcnow()
        
        #below line only for testing purposes
        now = now.replace(day=18)
        
        currentTime = now.strftime('%H:%M')

        #for multiple repetisions:
        if currentTime != mqttConnection.get_data().data['start']:
        #check if currentTime is welcomeTime and if welcomeMessage was already played 
        #if currentTime == data['start'] and data['lastWelcome'] != now.date():
            #update last date welcomeTime is played to prevent second excecution
            mqttConnection.get_data().data['lastWelcome'] = now.date()   

            #get required data for welcome message 
            mqttConnection.request_weather()                      
            mqttConnection.request_priority()                        
            mqttConnection.request_location()                         
            mqttConnection.request_appointment(now.date())          

            #wait till required date is initialized
            start_time = time.time()
            passed = 0.0
            while  mqttConnection.get_data().data['priority'] is None or passed > 3.0:
                end_time = time.time()
                passed = end_time - start_time
                pass 

            #if priority data is still none, skip rideTime request
            if  mqttConnection.get_data().data['priority'] is not None:
                mqttConnection.request_rideTime()    

            #wait a bit for message to come in 
            time.sleep(3)

            #prepare data
            msg_weather = mqttConnection.get_data().prep_weather_data()
            msg_travel  = mqttConnection.get_data().prep_travel_data()
            msg_event   = mqttConnection.get_data().prep_event_data()

            #build tts message and publish message to tts
            tts = "Guten Morgen, es ist " + \
                currentTime + ". " + \
                msg_weather + \
                msg_travel + \
                msg_event + \
                "Das war alles. Ich wünsche dir noch einen schönen Tag."
            
            #skipMsg = 'Guten Morgen, es ist ' + currentTime + ' In Stuttgart wird das Wetter heute Überwiegend bewölkt. Heute wird eine Temperatur von 12.33 Grad Celcius erwarted mit einer Feuchtigkeit von 72 Prozent. Deine vorraussichtliche Reisezeit beträgt 20 Minuten. Heute stehen folgende Termine an: Von 23:00 bis 00:00 hast du ein Termin für asdf. Das war alles. Ich wünsche dir noch einen schönen Tag.'
            print("OUTPUT ", __file__, ": ", tts)
            mqttConnection.publish_to_tts(tts)
        
        #wait some time before polling again
        time.sleep(15)
    mqttConnection.disconnect()