#!/usr/bin/env python

import mosquitto
import serial
import os
import time
import json
import random
import yaml

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
            data = { 
                'version':'1.0.0', 
                'datastreams': [ 
                    {
                        "id" : sensor+'_'+reading_type,
                        "datapoints": [
                            {
                                "at": time.ctime(),
                                "value": reading
                            }
                        ]
                    }
                ],
                "location": {
                    "lat": sensor_config['latitude'],
                    "lon": sensor_config['longitude']
                }
            }
            mqttc.publish(mqtt_topic(sensor, reading_type), json.dumps(data))
            print("message published: " + sensor + " " + reading_type)
    
while mqttc.loop() == 0:
    rawinput = serialFromWireless.readline()
    rawinput = rawinput.strip().decode("utf-8")
    sensor = rawinput[1:3]
    river = rawinput[3:7]
    number = rawinput[7:]
    number = number.rsplit('-')[0]
    publish(sensor,river,number)
    pass

def cleanup():
    print("Ending and cleaning up")
    serialFromWireless.close()
    mqttc.disconnect()