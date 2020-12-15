from typing import Any, Optional


class HostBot:
    BOTNAME = "Mastermind Host"
    BOTEMOJI = "🧙"
    STARTX_OFFSET = 11
    STARTY_OFFSET = -13

    def __init__(self, res_json):
        self.id = int(res_json["id"])
        self.current_player = None
        self.current_game = None

    @classmethod
    def get_create_req(cls, world):
        start_x = cls.STARTX_OFFSET
        start_y = world["rows"] + cls.STARTY_OFFSET
        return {"bot": {
            "name": cls.BOTNAME,
            "x": start_x,
            "y": start_y,
            "emoji": HostBot.BOTEMOJI,
            "can_be_mentioned": True
        }}

    def process_message(self, message_json):
        print(f"[Host Bot {self.id}]: Got message for the bot {message_json}")