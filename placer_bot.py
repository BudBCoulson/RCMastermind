from typing import Any, Optional
from rc_rest_api import *

class PlacerBot:
    BOTNAME = "Mastermind Placer"
    BOTEMOJI = "🧞"
    STARTX_OFFSET = 5
    STARTY_OFFSET = -1

    def __init__(self, res_json):
        self.id = int(res_json["id"])
        self.pegs = set()

    @classmethod
    def get_create_req(cls, world):
        start_x = cls.STARTX_OFFSET
        start_y = world["rows"] + cls.STARTY_OFFSET
        return {"bot": {
            "name": cls.BOTNAME,
            "x": start_x,
            "y": start_y,
            "emoji": PlacerBot.BOTEMOJI,
            "can_be_mentioned": False
        }}
        
    def place_wall(self, x, y, clr, txt = None):
		jsn = {"bot_id": self.id
		       "wall": {
               "pos": {
                 "x": x,
                 "y": y
               },
               "color": clr,
               "wall_text": txt
            }}
        res = post("",jsn)
        self.pegs.add(res["id"])
		
	def erase_wall(self, idx):
		if idx in self.pegs:
			jsn = {"bot_id": self.id}
			delete(idx,jsn)
			self.pegs.remove(idx)
		
	def clear_board(self):
		for idx in self.pegs:
			self.erase_wall(idx)
		self.pegs = set()
