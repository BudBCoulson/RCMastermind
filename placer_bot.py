from typing import Any, Optional

from rc_rest_api import *

class PlacerBot:
    BOTNAME = "Mastermind Placer"
    BOTEMOJI = "🧞"
    START_X = 5
    START_Y = 108
    COLOR_NAMES = {"R": "pink", "O": "orange", "G": "green", "B": "blue", "P": "purple", "Y": "yellow"}

    def __init__(self):
        req = {"bot": {
            "name": self.BOTNAME,
            "x": self.START_X,
            "y": self.START_Y,
            "emoji": self.BOTEMOJI,
            "direction": "left",
            "can_be_mentioned": False
        }}
        res = post(id="", j=req)
        
        self.id = int(res.json()["id"])
        self.pegs = []
        
        print("PlacerBot: init")
  
    def _place_wall(self, x, y, clr = "gray", txt = " "):
        self._move_to(x+1,y)
        jsn = {"bot_id": self.id,
               "wall": {
                 "pos": {
                   "x": x,
                   "y": y
                  },
               "color": clr,
               "wall_text": txt
        }}
        res = post("", jsn, WALLURL)
        self.pegs.append((x,y,res.json()["id"]))
        
        print("PlacerBot: made wall with params", x, y, clr, txt)
        
    def _erase_wall(self, x, y, idx):
        j = {"bot_id": self.id}
        if (x,y,idx) in self.pegs:
            self._move_to(x+1,y)
            delete(idx, j, WALLURL)
        
        print("PlacerBot: erased wall at", x, y)
            
    def _move_to(self, x, y):
        jsn = {"bot":{"x": x, "y": y}}
        res = patch(self.id, jsn)
        
        print("PlacerBot: moved to", x, y)
        
    def _orient(self, direct):
        jsn = {"bot":{"direction": direct}}
        res = patch(self.id, jsn)
        
        print("PlacerBot: changed orientation to", direct)
        
    def write_code(self, colors, turn):
        for i in range(4):
            self._place_wall(self.START_X-4+i, self.START_Y+turn, clr = self.COLOR_NAMES[colors[i]])
        
        print("PlacerBot: wrote code", colors, "at turn #", turn)
            
    def write_keys(self, pos_c, off_c, turn):
        self._place_wall(self.START_X+1, self.START_Y+turn, clr = 'pink', txt = str(pos_c))
        self._place_wall(self.START_X+2, self.START_Y+turn, clr = 'gray', txt = str(off_c))
        self._orient('up')
        self._move_to(self.START_X+2, self.START_Y+turn+1)
        self._orient('left')
        
        print("PlacerBot: wrote keys", pos_c, off_c, "at turn #", turn) 
                 
    def clear_board(self):
        while self.pegs:
            x, y, idx = self.pegs.pop()
            self._erase_wall(x,y,idx)
            
        print("PlacerBot: board reset")
            
    def vanish(self):
        delete(self.id)
        
        print("PlacerBot: goodbye")
