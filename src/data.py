
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

#Dict containing list of locations
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

#Dict containing data
data = {
    'start': None,
    'date': None,
    'lastWelcome': None,
    'weather': None,
    'location': location,
    'priority': None,
    'travel': 0,
    'event': []
}
