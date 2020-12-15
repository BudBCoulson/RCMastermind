from typing import Any, Optional


class PlacerBot:
    BOTNAME = "Mastermind Placer"
    BOTEMOJI = "🧞"
    STARTX_OFFSET = 5
    STARTY_OFFSET = -1

    def __init__(self, res_json):
        self.id = int(res_json["id"])

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
