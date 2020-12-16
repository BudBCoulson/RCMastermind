from typing import Any, Optional

from rc_rest_api import *

class PlacerBot:
    BOTNAME = "Mastermind Placer"
    BOTEMOJI = "🧞"
    STARTX_OFFSET = 5
    STARTY_OFFSET = -2

    def __init__(self, world):
        self.start_x = self.STARTX_OFFSET
        self.start_y = world["rows"] + self.STARTY_OFFSET
        req = {"bot": {
            "name": self.BOTNAME,
            "x": self.start_x,
            "y": self.start_y,
            "emoji": self.BOTEMOJI,
            "direction": "left",
            "can_be_mentioned": False
        }}
        res = post(id="", j=req)
        
        self.id = int(res.json()["id"])
        self.pegs = set()
  
    def place_wall(self, x, y, clr):
        self.move_to(x+1,y)
        jsn = {"bot_id": self.id,
               "wall": {
                 "pos": {
                   "x": x,
                   "y": y
                  },
               "color": clr
        }}
        res = post("", jsn, WALLURL)
        print(res.json())
        self.pegs.add(res.json()["id"])
        
    def erase_wall(self, idx):
        j = {"bot_id": self.id}
        if idx in self.pegs:
            delete(idx, j, WALLURL)
            
    def move_to(self, x, y):
        jsn = {"bot":{"x": x, "y": y}}
        res = patch(self.id, jsn)
        
    def clear_board(self):
        print(self.pegs)
        for idx in self.pegs:
            self.erase_wall(idx)
        self.pegs = set()
        
        self.move_to(self.start_x, self.start_y)
