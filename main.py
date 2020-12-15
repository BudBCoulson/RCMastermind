import json
import logging
import requests
from time import sleep
from random import randint, choice

from actioncable.connection import Connection
from actioncable.subscription import Subscription

from settings import *

# ==== REST API ================================================================

def post(id, j):
    print("POST: ", j)
    return requests.post(BOTURL+id, json=j, auth=(app_id, app_secret))

def patch(id, j):
    return requests.patch(BOTURL+id, json=j, auth=(app_id, app_secret))

def delete(id, j=None):
    if j is None:
        return requests.delete(BOTURL+id, auth=(app_id, app_secret))
    else:
        return requests.delete(BOTURL+id, json=j, auth=(app_id, app_secret))


# ==== ACTIONCABLE =============================================================

#logging.basicConfig(level=logging.DEBUG)

connection = Connection(url=f"wss://recurse.rctogether.com/cable?app_id={app_id}&app_secret={app_secret}", origin='https://recurse.rctogether.com')
connection.connect()

subscription = Subscription(connection, identifier={'channel': 'ApiChannel'})

# WORLD STATE
HOST_BOTID = None

HOST_STARTX = 16
HOST_STARTY = 16

world = None

def on_receive(message):
    global HOST_STARTX, HOST_STARTY

    # Initialize everything
    if message["type"] == "world":
        world = message["payload"]
        print("world received")
        for entity in world["entities"]:
            # Cleanup pre-existing bots
            if entity["type"] == "Bot":
                if entity.get("name") == HOST_BOTNAME:
                    delete(id=str(entity["id"]))

        HOST_STARTX = HOST_STARTX_OFFSET
        HOST_STARTY = world["rows"] + HOST_STARTY_OFFSET
        init()
    # React when host bot is mentioned
    elif message["type"] == "entity":
        payload = message['payload']
        if payload['type'] == "Avatar" and payload['message']:
            message = payload["message"]
            if int(HOST_BOTID) in message["mentioned_agent_ids"]:
                print(f"[{HOST_BOTID}]Got message for the bot {message}")
    else:
        print("Unknown message type", message["type"])

subscription.on_receive(callback=on_receive)
subscription.create()

def init():
    global HOST_BOTID
    print("Running init")
    req = post(id="", j={"bot":{"name":HOST_BOTNAME, "x":HOST_STARTX, "y":HOST_STARTY, "emoji":HOST_BOTEMOJI, "can_be_mentioned":True}})
    print("Got response from POST")
    bot = req.json()
    HOST_BOTID = str(bot["id"])
    print(f"Initialized host bot with id {HOST_BOTID}")

try:
    while True:
        print(subscription.state)
        sleep(1)
        pass
except KeyboardInterrupt:
    if HOST_BOTID:
        delete(HOST_BOTID)