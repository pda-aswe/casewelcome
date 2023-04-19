from src import messenger
from unittest.mock import patch, ANY, MagicMock
from multiprocessing import Queue

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

@patch("paho.mqtt.publish.single")
@patch("paho.mqtt.subscribe.simple")
def test_mqttRRP(mock_sub,mock_pub):
    mock_sub.return_value = type('obj', (object,), {'payload' : 'asdf'})
    messenger.mqttRRP(Queue(),"test/request","test/response","asdf")
    mock_pub.assert_called_with("test/request",payload="asdf",hostname=ANY,port=ANY)
    mock_sub.assert_called_with("test/response",hostname=ANY,port=ANY)