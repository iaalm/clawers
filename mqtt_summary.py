#!/usr/bin/python3

"""
use mqtt for a summary of these clawer
"""

import paho.mqtt.client as mqtt
import curses
tab = []
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(True)
stdscr.clear()
stdscr.refresh()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    #print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$summary/#")
    #client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global tab
    #print(msg.topic+" "+str(msg.payload))
    if msg.topic in tab:
        i = tab.index(msg.topic)
    else:
        i = len(tab)
        tab.append(msg.topic)
    stdscr.addstr( i, 0, '%s:%s'%(msg.topic, msg.payload.decode('utf-8')))
    stdscr.refresh()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("127.0.0.1", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
