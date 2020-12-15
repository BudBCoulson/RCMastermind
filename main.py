import json
import logging
import sys
from time import sleep
from random import randint, choice

from actioncable.connection import Connection
from actioncable.subscription import Subscription

from host_bot import HostBot
from rc_rest_api import delete
from settings import *
from placer_bot import PlacerBot

# ==== ACTIONCABLE =============================================================

connection = Connection(url=f"wss://recurse.rctogether.com/cable?app_id={app_id}&app_secret={app_secret}", origin='https://recurse.rctogether.com')
connection.connect()

subscription = Subscription(connection, identifier={'channel': 'ApiChannel'})

# WORLD STATE
HOST_BOT = None
world = None

def on_receive(message):
    try:
        # Initialize everything
        if message["type"] == "world":
            world = message["payload"]
            print("world received")
            init_bots(world)
        # React when host bot is mentioned
        elif message["type"] == "entity":
            payload = message['payload']
            if payload['type'] == "Avatar" and payload['message']:
                if HOST_BOT.id in payload["message"]["mentioned_agent_ids"]:
                    HOST_BOT.process_message(payload)
        else:
            print("Unknown message type", message["type"])
    except:
        e = sys.exc_info()[0]
        print("Failed to process received message due to ", e)

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
        HOST_BOT = HostBot(world)
        print(f"Initialized host bot with id {HOST_BOT.id}")
        
        # Init Placer Bot
        jsn = PlacerBot.get_create_req(world)
        res = post(id="", j=jsn)
        PLACER_BOT = PlacerBot(res.json())
        print(f"Initialized host bot with id {PLACER_BOT.id}")
        
    except:
        e = sys.exc_info()[0]
        print("Failed to init due to ", e)

try:
    while True:
        print(subscription.state)
        sleep(1)
        pass
except KeyboardInterrupt:
    if HOST_BOT:
        delete(id=HOST_BOT.id)
