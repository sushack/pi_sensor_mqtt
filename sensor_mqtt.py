#!/usr/bin/env python

import mosquitto
import serial
import os
import time
from datetime import datetime, date
import json
import random
import yaml

last_published = 0

# Load config
stream = open("config.yml", 'r')
config = yaml.load(stream)

mypid = os.getpid()
client_uniq = "sensor_mqtt_"+str(mypid)
mqttc = mosquitto.Mosquitto(client_uniq)
mqttc.username_pw_set(config['mqtt']['username'])
mqttc.connect(config['mqtt']['broker'], config['mqtt']['port'], 60, True)

serialFromWireless = serial.Serial(config['serial']['port'])
serialFromWireless.flushInput()

def mqtt_topic(sensor, reading_type):
    try:
        return config['mqtt']['topic_override']
    except KeyError:
        return '/oxflood/'+config['uuid']+'/'+sensor+'/'+reading_type

def publish(sensor, reading_type, reading):
    try:
        sensor_config = config['sensors'][sensor][reading_type]
    except KeyError:
        print("unknown sensor or reading type: " + sensor + " " + reading_type)
    else:
        if sensor_config:
            now = datetime.now().isoformat()
            data = { 
                'version':'1.0.0', 
                'datastreams': [ 
                    {
                        "id" : sensor+'_'+reading_type,
                        "datapoints": [
                            {
                                "at": now,
                                "value": sensor_config['base']-reading,
                                "units": sensor_config["units"]
                            }
                        ]
                    },
                    {
                        "id" : sensor+'_'+reading_type+'_threshold',
                        "datapoints": [
                            {
                                "at": now,
                                "value": sensor_config['threshold']
                            }
                        ]
                    }
                ],
                "location": {
                    "lat": sensor_config['latitude'],
                    "lon": sensor_config['longitude']
                }
            }
            print(json.dumps(data))
            mqttc.publish(mqtt_topic(sensor, reading_type), json.dumps(data))
            print("message published: " + sensor + " " + reading_type)
    
while mqttc.loop() == 0:
    serialFromWireless.flushInput()
    serialFromWireless.flushOutput()
    serialFromWireless.flush()
    if serialFromWireless.read() == b'a': #look for start of data package
        rawinput = serialFromWireless.read(11).decode("utf-8") #'a' plus rest of message = 12 bytes
        # chop up raw data input
        sensor = rawinput[0:2]
        river = rawinput[2:6]
        number = rawinput[6:]
        number = number.rsplit('-')[0] #remove trailing dashes
        if last_published < time.time() - 10:
            publish(sensor,river,float(number))
            last_published = time.time()
    pass

def cleanup():
    print("Ending and cleaning up")
    serialFromWireless.close()
    mqttc.disconnect()
