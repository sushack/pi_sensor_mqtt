pi_sensor_mqtt
==============

Reads sensor data from serial wireless sensors and publishes to an MQTT broker.

Set up with

    workon pi_sensor_mqtt
    pip install -r requirements.txt
    
Copy config.example.yml to config.yml and add details for your various sensors and MQTT broker.

Then run:

    ./sensor_mqtt.py