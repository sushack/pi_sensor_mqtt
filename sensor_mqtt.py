#!/usr/bin/env python

import mosquitto
import os
import time
import json

broker = "api.xively.com"
port = 1883
endpoint = os.environ['MQTT_ENDPOINT']
api_key = os.environ['MQTT_API_KEY']

mypid = os.getpid()
client_uniq = "sensor_mqtt_"+str(mypid)
mqttc = mosquitto.Mosquitto(client_uniq)
mqttc.username_pw_set(api_key)
mqttc.connect(broker, port, 60, True)
     
def publish(reading):
    global mqttc;
    data = { 
        'version':'1.0.0', 
        'datastreams': [ 
            {
                "id" : "sensor1",
                "datapoints": [
                    {
                        "at": time.ctime(),
                        "value": reading
                    }
                 ]
            }
        ]
    }
    mqttc.publish(endpoint, json.dumps(data))
    
while mqttc.loop() == 0:
    publish(27)
    print "message published"
    time.sleep(0.5)
    pass
    

def cleanup():
    print "Ending and cleaning up"
    mqttc.disconnect()