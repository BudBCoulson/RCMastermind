import re

from rc_rest_api import post, patch, delete
from placer_bot import PlacerBot
from game_logic import Game
from message_cache import SimpleCache
from time import time

class HostBot:
    BOTNAME = "Mastermind Host"
    BOTEMOJI = "🧙"
    STARTX_OFFSET = 9
    STARTY_OFFSET = -15

    HELP_TEXT = """
Welcome! See the note in the top left corner of the Mastermind space for instructions.
"""

    def __init__(self, world):
        self.start_x = self.STARTX_OFFSET
        self.start_y = world["rows"] + self.STARTY_OFFSET
        req = {"bot": {
            "name": self.BOTNAME,
            "x": self.start_x,
            "y": self.start_y,
            "emoji": self.BOTEMOJI,
            "can_be_mentioned": True
        }}
        res = post(id="", j=req)

        self.id = int(res.json()["id"])
        self.current_player_name = None
        self.current_user_id = None

        self.placers = []
        self.game = None
        self.turn = -1
        self.gametime = None

        self.msg_cache = SimpleCache()

    def process_message(self, payload):
        if self.msg_cache.is_seen(payload["message"]):
            print(f"[Host Bot {self.id}]: Ignoring message since it's a duplicate")
        else:
            text = payload["message"]["text"]
            match = re.fullmatch(r"@\*\*[^|*]+\*\*(.*)", text)
            if match and len(match.groups()) == 1:
                msg = match.group(1).lower().strip()
                print(f"[Host Bot {self.id}]: Got a message: {msg}")

                if msg.find("help") != -1:
                    self._send_message(self.HELP_TEXT, payload['person_name'])
                elif msg == "start game":
                    self._start_game(payload["person_name"], payload["user_id"])
                elif msg == "end game":
                    self._end_game(payload['person_name'], payload["user_id"])
                elif msg == "demo":
                    self._demo(payload['person_name'], payload["user_id"])
                elif msg == "hint":
                    self._hint(payload['person_name'], payload["user_id"])
                elif self.game:
                    guess = msg.strip()
                    self._guess(payload['person_name'], payload["user_id"], guess.upper())
                else:
                    self._send_message("I don't understand you", payload['person_name'])
            else:
                print(f"[Host Bot {self.id}]: Got a message but failed to parse it")

    def cleanup(self):
        while self.placers:
            pbot = self.placers.pop()
            pbot.clear()
            pbot.vanish()
        delete(id=self.id)

    def _start_game(self, person_name, user_id):
        if self.game and time() - self.gametime <= 180:
            self._send_message("Another game is already in progress", person_name)
        else:
            if self.game:
                self._send_message("Please wait while I cleanup...", person_name)
                self._end_game(self.current_player_name, self.current_user_id)

            self.current_user_id = user_id
            self.current_player_name = person_name
            self._send_message(f"Started a game for you, {person_name}. I've chosen my code.")

            self.game = Game()
            self.turn = -1
            self.gametime = time()
            
            pbot = PlacerBot(self.start_x-4, self.start_y+2)
            self.placers.append(pbot)
            pbot.write_secret()

    def _end_game(self, person_name, user_id):
        if not self.current_user_id:
            self._send_message("No game in progress", person_name)
        elif self.game and self.current_user_id != user_id:
            self._send_message("Cannot end someone else's game", person_name)
        else:
            self._send_message(f"Ended a game for {self.current_player_name}", person_name)
            self.current_user_id = None
            self.current_player_name = None

            while self.placers:
                pbot = self.placers.pop()
                pbot.clear()
                pbot.vanish()
            self.game = None
            self.turn = -1
            self.gametime = None

    def _demo(self, person_name, user_id):
        if self.game and time() - self.gametime <= 180:
            self._send_message("Another game is already in progress", person_name)
        else:
            if self.game:
                self._send_message("Please wait while I cleanup...", person_name)
                self._end_game(self.current_player_name, self.current_user_id)

            self.current_user_id = self.id
            self.current_player_name = self.BOTNAME
            self._send_message("Started a demo game. I've chosen my code.")

            self.game = Game()
            self.turn = -1
            self.gametime = time()
            
            pbot = PlacerBot(self.start_x-4, self.start_y+2)
            self.placers.append(pbot)
            pbot.write_secret()
            
            while self.game:
                guess = self.game.get_guess_code()
                self._guess(guess_text=guess)

    def _hint(self, person_name, user_id):
        if not self.current_user_id:
            self._send_message("No game in progress", person_name)
        elif self.game and self.current_user_id != user_id:
            self._send_message("Only the current player can request a hint", person_name)
        else:
            self._send_message(f"I would suggest choosing {self.game.get_guess_code()}")

    def _guess(self, person_name=self.current_player_name, user_id=self.current_player_id, guess_text):
        if not self.current_user_id:
            self._send_message("No game in progress", person_name)
        elif self.current_user_id != user_id:
            self._send_message("Cannot participate in someone else's game", person_name)
        elif not self.game:
            self._send_message("Game is already over!")
        elif len(guess_text) != 4 or not all(ch in {"R","O","G","B","P","Y"} for ch in guess_text):
            self._send_message(f"{guess_text} is not a valid guess, {person_name}. Please enter a string of four colors.")
        else:
            self.turn += 1
            self._send_message(f"You guessed: {guess_text}", person_name)

            pbot = PlacerBot(self.start_x-4, self.start_y+13-self.turn)
            self.placers.append(pbot)
            pbot.write_code(guess_text)

            pos_c, off_c = self.game.process_guess(guess=guess_text)
            
            pbot = PlacerBot(self.start_x-1, self.start_y+13-self.turn)
            self.placers.append(pbot)
            pbot.write_keys(pos_c, off_c)

            self.gametime = time()

            if pos_c == 4:
                self._gameover(True)
                return
            if self.turn == 9:
                self._gameover(False)
                return

    def _gameover(self, win):
        true_code = self.game.secrets[-1]
        if win:
            self._send_message(f"{self.current_player_name} wins!")
        else:
            self._send_message(f"Sorry, you've run out of guesses. My code was {true_code}", self.current_player_name)

        pbot = self.placers[0]
        pbot.clear()
        pbot.write_code(true_code)

        msg = "Congratulations!" if win else "Better luck next time."
        for pbot in self.placers:
            pbot.message(msg)

        self.game = None
        self.turn = -1
        self.gametime = None

    def _send_message(self, text, person_name=None):
        msg_text = text
        if person_name:
            msg_text = f"@**{person_name}** {text}"
        msg_req = {
            "bot": {"message": msg_text}
        }
        patch(id=self.id, j=msg_req)
        print(f"[Host Bot {self.id}]: Sent message with '{msg_text}'")
