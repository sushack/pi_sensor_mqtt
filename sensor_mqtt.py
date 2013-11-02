#!/usr/bin/env python

import mosquitto
import os
import time
import json
import random
import yaml

# Load config
stream = open("config.yml", 'r')
config = yaml.load(stream)

endpoint = os.environ['MQTT_ENDPOINT']

mypid = os.getpid()
client_uniq = "sensor_mqtt_"+str(mypid)
mqttc = mosquitto.Mosquitto(client_uniq)
mqttc.username_pw_set(config['mqtt']['username'])
mqttc.connect(config['mqtt']['broker'], config['mqtt']['port'], 60, True)



def publish(sensor, reading_type, reading):
    sensor_config = config['sensors'][sensor][reading_type]
    if sensor_config:
        data = { 
            'version':'1.0.0', 
            'datastreams': [ 
                {
                    "id" : sensor_config['publish_id'],
                    "datapoints": [
                        {
                            "at": time.ctime(),
                            "value": reading
                        }
                     ]
                }
            ]
        }
        mqttc.publish(sensor_config['mqtt_endpoint'], json.dumps(data))
    
while mqttc.loop() == 0:
    publish("R1", "RIVR", random.randrange(0,255))
    print "message published"
    time.sleep(1)
    pass
    

def cleanup():
    print "Ending and cleaning up"
    mqttc.disconnect()