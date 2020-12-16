from typing import Any, Optional
from time import sleep
import re

from rc_rest_api import *
from placer_bot import PlacerBot
from game_logic import Game

class HostBot:
    BOTNAME = "Mastermind Host"
    BOTEMOJI = "🧙"
    STARTX_OFFSET = 5
    STARTY_OFFSET = -15

    HELP_TEXT = """
Welcome to the Mastermind corner of virtual RC!
The Host Bot understands the following messages (case is ignored):

'start game' - Starts the game for the user

'guess <your guess>' - Processes the user's guess (as a string of four colors, represented by the letters "ROGBPY")

'end game' - Ends the game for the user

'<...>help<...>' - Shows this message

WARNING: Under Construction!!
The game is currently in development and therefore very buggy.
"""

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
        self.current_player_name = None
        self.current_user_id = None
        self.note_id = None
        
        self.placer = None
        self.game = None
        self.turn = -1

    def process_message(self, payload):
        text = payload["message"]["text"]
        match = re.fullmatch("@\*\*[^|*]+\*\*(.*)", text)
        if match and len(match.groups()) == 1:
            msg = match.group(1).lower().strip()
            print(f"[Host Bot {self.id}]: Got a message: {msg}")

            # TODO(polarfoxgirl): Deal with duplicated messages!

            if msg.find("help") != -1:
                self._update_note(self.HELP_TEXT)
            elif msg == "start game":
                self._start_game(payload["person_name"], payload["user_id"])
            elif msg == "end game":
                self._end_game(payload["user_id"])
            elif msg.find("guess") != -1:
                guess = msg[len("guess"):].strip()
                self._guess(payload["user_id"], guess.upper())
            else:
                self._update_note(f"{payload['person_name']}, I don't understand you")
        else:
            print(f"[Host Bot {self.id}]: Got a message but failed to parse it")

    def cleanup(self):
        if self.note_id:
            delete(id=self.note_id, j={"bot_id": self.id}, url=NOTEURL)
        if self.placer:
            self.placer.vanish()
        delete(id=self.id)

    def _start_game(self, person_name, user_id):
        if self.current_user_id:
            self._update_note("Another game is already in progress!")
        else:
            self.current_user_id = user_id
            self.current_player_name = person_name
            self._update_note(f"Started a game for {person_name}")
            
            self.placer = PlacerBot()
            self.game = Game()
            self.turn = -1
    
    # TODO(bud): Add timer to end abandoned games
    #            Allow other users to end completed games
    def _end_game(self, user_id):
        if not self.current_user_id:
            self._update_note("No game in progress!")
        elif self.current_user_id != user_id:
            self._update_note("Cannot end someone else's game")
        else:
            self._update_note(f"Ended a game for {self.current_player_name}")
            self.current_user_id = None
            self.current_player_name = None
            
            self.placer.clear_board()
            self.placer.vanish()
            self.game = None
            self.turn = -1

    def _guess(self, user_id, guess_text):
        if not self.current_user_id:
            self._update_note("No game in progress!")
        elif self.current_user_id != user_id:
            self._update_note("Cannot participate in someone else's game")
        else:
            self.turn += 1
            self._update_note(f"{self.current_player_name} guessed: {guess_text}")
            self.placer.write_code(guess_text,self.turn)
            pos_c, off_c = self.game.process_guess(guess_text)
            self.placer.write_keys(pos_c, off_c, self.turn)
            if pos_c == 4:
                self._win()
                return
            if self.turn == 9:
                self._lose()
                return
    
    # TODO(bud): add more effects here (fireworks emojis?)            
    def _win(self):
        self._update_note(f"{self.current_player_name} wins!")
        
    def _lose(self):
        true_code = self.game.secrets[-1]
        self._update_note(f"Sorry, {self.current_player_name}, you've run out of guesses. My code was {true_code}")
        self.placer.write_code(true_code, 11)
            
    def _update_note(self, text):
        print("Started updating note")
        note_req = {
            "bot_id": self.id,
            "note": {"note_text": text}
        }

        if self.note_id:
            patch(id=self.note_id, j=note_req, url=NOTEURL)
        else:
            res = post(id="", j=note_req, url=NOTEURL)
            self.note_id = res.json()["id"]
        print(f"[Host Bot {self.id}]: Updated note {self.note_id} with '{text}'")
