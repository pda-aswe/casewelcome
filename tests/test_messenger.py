import pytest
import time

from src import messenger
from unittest.mock import patch, ANY, MagicMock
from multiprocessing import Queue

from datetime import datetime

def test_connect():
    obj = messenger.Messenger()
    with patch.object(obj,'client') as mock_connect:
        obj.connect()
        mock_connect.connect.assert_called_with("localhost",1883,60)

def test_disconnect():
    obj = messenger.Messenger()
    with patch.object(obj,'connected',True),patch.object(obj,'client') as mock_connect:
        obj.disconnect()
        mock_connect.disconnect.assert_called()

def test_request_welcomeTime():
    obj = messenger.Messenger()
    success = obj.request_welcomeTime()
    assert success == True

def test_request_weather():
    obj = messenger.Messenger()
    success = obj.request_weather()
    assert success == True

def test_request_priority():
    obj = messenger.Messenger()
    success = obj.request_priority()
    assert success == True

def test_request_location():
    obj = messenger.Messenger()
    success = obj.request_location()
    assert success == True

def test_request_appointment():
    obj = messenger.Messenger()
    date = datetime.now().date()
    success = obj.request_appointment(date)
    assert success == True

@patch("paho.mqtt.publish.single")
@patch("paho.mqtt.subscribe.simple")
def test_mqttRRP(mock_sub,mock_pub):
    mock_sub.return_value = type('obj', (object,), {'payload' : 'asdf'})
    messenger.mqttRRP(Queue(),"test/request","test/response","asdf")
    mock_pub.assert_called_with("test/request",payload="asdf",hostname=ANY,port=ANY)
    mock_sub.assert_called_with("test/response",hostname=ANY,port=ANY)