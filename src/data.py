from datetime import datetime

from singleton import SingletonMeta

class Data(metaclass=SingletonMeta):
    def __init__(self):
        self.topic_list = {
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

        self.location = {
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

        self.data = {
            'start': None,
            'date': None,
            'lastWelcome': None,
            'weather': None,
            'location': self.location,
            'priority': None,
            'travel': 0,
            'event': []
        }

        self.data['lastWelcome'] = datetime(1970, 1, 1)

    def prep_weather_data(self):
        return ('In ' + self.data['weather']['location'] + \
                ' wird das Wetter heute ' + self.data['weather']['description'] + '.' + \
                ' Heute wird eine Temperatur von ' + str(self.data['weather']['temperature']) + \
                ' Grad Celcius erwarted mit einer Feuchtigkeit von ' + str(self.data['weather']['humidity']) + \
                ' Prozent. ')

    def prep_travel_data(self):
        if self.data['travel']:
            return 'Deine vorraussichtliche Reisezeit beträgt ' + str(int(self.data['travel']/60)) + ' Minuten. '
        else:
            return 'Es konnte keine Prognose zur heutigen Reisezeit ermittelt werden. '

    def prep_event_data(self):
        if self.data['event'] is not []:    
            msg = 'Heute stehen folgende Termine an: '
            for event in self.data['event']:
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