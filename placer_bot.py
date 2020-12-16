from typing import Any, Optional
from rc_rest_api import *

class PlacerBot:
    BOTNAME = "Mastermind Placer"
    BOTEMOJI = "🧞"
    STARTX_OFFSET = 5
    STARTY_OFFSET = -1

    def __init__(self, world):
        start_x = cls.STARTX_OFFSET
        start_y = world["rows"] + cls.STARTY_OFFSET
        req = {"bot": {
            "name": self.BOTNAME,
            "x": start_x,
            "y": start_y,
            "emoji": self.BOTEMOJI,
            "can_be_mentioned": False
        }}
        res = post(id="", j=req)
        
        self.id = int(res.json()["id"])
        self.pegs = set()

        
    def place_wall(self, x, y, clr, txt = None):
        jsn = {"wall": {
                "pos": {
                "x": x,
                "y": y
            },
            "color": clr,
            "wall_text": txt
        }}
        res = post("", jsn, WALLURL)
        self.pegs.add(res["id"])
        
    def erase_wall(self, idx):
        j = {"bot_id": self.id}
        if idx in self.pegs:
            delete(idx, j, WALLURL)
            self.pegs.remove(idx)
        
    def clear_board(self):
        for idx in self.pegs:
            self.erase_wall(idx)
        self.pegs = set()
