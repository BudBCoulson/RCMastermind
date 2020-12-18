import sys
from time import sleep

from actioncable.connection import Connection
from actioncable.subscription import Subscription

from host_bot import HostBot
from placer_bot import PlacerBot
from rc_rest_api import delete
from settings import app_id, app_secret

# ==== ACTIONCABLE ============================================================

connection = Connection(
    url=f"wss://recurse.rctogether.com/cable?app_id={app_id}&app_secret={app_secret}",
    origin='https://recurse.rctogether.com',
)
connection.connect()

subscription = Subscription(connection, identifier={'channel': 'ApiChannel'})

# WORLD STATE
HOST_BOT = None
WORLD = None


def on_receive(message):
    try:
        global WORLD
        # Initialize everything
        if message["type"] == "world" and not WORLD:
            WORLD = message["payload"]
            print("world received")
            init_bots(WORLD)
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
        m = sys.exc_info()[1]
        tb = sys.exc_info()[2]
        print(f"Failed to process received message due to {e}: '{m}'\n{tb}")


subscription.on_receive(callback=on_receive)
subscription.create()


def init_bots(world):
    try:
        global HOST_BOT

        # Cleanup pre-existing bots
        if HOST_BOT:
            HOST_BOT.cleanup()

        for entity in world["entities"]:
            if entity["type"] == "Bot":
                if entity.get("name") in [HostBot.BOTNAME, PlacerBot.BOTNAME]:
                    delete(id=entity["id"])
        print("Cleaned up bots")

        # Init Host Bot
        HOST_BOT = HostBot(world)
        print(f"Initialized host bot with id {HOST_BOT.id}")

        # Init Placer Bot
        # PLACER_BOT = PlacerBot(world)
        # print(f"Initialized placer bot with id {PLACER_BOT.id}")

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
        HOST_BOT.cleanup()
