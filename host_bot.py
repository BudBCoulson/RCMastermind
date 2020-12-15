from typing import Any, Optional
import re

from rc_rest_api import *

class HostBot:
    BOTNAME = "Mastermind Host"
    BOTEMOJI = "🧙"
    STARTX_OFFSET = 11
    STARTY_OFFSET = -13

    def __init__(self, world):
        start_x = self.STARTX_OFFSET
        start_y = world["rows"] + self.STARTY_OFFSET
        req = {"bot": {
            "name": self.BOTNAME,
            "x": start_x,
            "y": start_y,
            "emoji": self.BOTEMOJI,
            "can_be_mentioned": True
        }}
        res = post(id="", j=req)

        self.id = int(res.json()["id"])
        self.current_player = None
        self.current_game = None
        

    def process_message(self, payload):
        text = payload["message"]["text"]
        match = re.fullmatch("@\*\*[^|*]+\*\*(.*)", text)
        if match and len(match.groups()) == 1:
            msg = match.group(1).lower()
            print(f"[Host Bot {self.id}]: Got a message: {msg}")

            if msg.find("help"):
                self._show_help(payload["person_name"], payload["user_id"])
        else:
            print(f"[Host Bot {self.id}]: Got a message but failed to parse it")

    def _show_help(self, person_name, user_id):
        res = patch(self.id, j={"bot": {"message": {"text": "Helpful message here"}}})
        print(f"[Host Bot {self.id}]: Got a patch response: {res}")
