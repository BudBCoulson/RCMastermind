import json
import logging
import requests
import sys
from time import sleep
from random import randint, choice

from actioncable.connection import Connection
from actioncable.subscription import Subscription

from settings import *
from host_bot import HostBot

# ==== REST API ================================================================

def post(id, j):
    return requests.post(BOTURL+str(id), json=j, auth=(app_id, app_secret))

def patch(id, j):
    return requests.patch(BOTURL+str(id), json=j, auth=(app_id, app_secret))

def delete(id, j=None):
    if j is None:
        return requests.delete(BOTURL+str(id), auth=(app_id, app_secret))
    else:
        return requests.delete(BOTURL+str(id), json=j, auth=(app_id, app_secret))


# ==== ACTIONCABLE =============================================================

connection = Connection(url=f"wss://recurse.rctogether.com/cable?app_id={app_id}&app_secret={app_secret}", origin='https://recurse.rctogether.com')
connection.connect()

subscription = Subscription(connection, identifier={'channel': 'ApiChannel'})

# WORLD STATE
HOST_BOT = None
world = None

def on_receive(message):
    # Initialize everything
    if message["type"] == "world":
        world = message["payload"]
        print("world received")
        init_bots(world)
    # React when host bot is mentioned
    elif message["type"] == "entity":
        payload = message['payload']
        if payload['type'] == "Avatar" and payload['message']:
            message = payload["message"]
            if HOST_BOT.id in message["mentioned_agent_ids"]:
                HOST_BOT.process_message(message)
    else:
        print("Unknown message type", message["type"])

subscription.on_receive(callback=on_receive)
subscription.create()

def init_bots(world):
    try:
        global HOST_BOT

        # Cleanup pre-existing bots
        for entity in world["entities"]:
            if entity["type"] == "Bot":
                if entity.get("name") in [HostBot.BOTNAME,PlacerBot.BOTNAME]:
                    delete(id=entity["id"])
        print("Cleaned up bots")

        # Init Host Bot
        jsn = HostBot.get_create_req(world)
        res = post(id="", j=jsn)
        HOST_BOT = HostBot(res.json())
        print(f"Initialized host bot with id {HOST_BOT.id}")
        
        # Init Placer Bot
        jsn = PlacerBot.get_create_req(world)
        res = post(id="", j=jsn)
        PLACER_BOT = PlacerBot(res.json())
        print(f"Initialized host bot with id {PLACER_BOT.id}")
        
    except:
        e = sys.exc_info()[0]
        print("Failed to POST due to ", e)

try:
    while True:
        print(subscription.state)
        sleep(1)
        pass
except KeyboardInterrupt:
    if HOST_BOT:
        delete(id=HOST_BOT.id)
