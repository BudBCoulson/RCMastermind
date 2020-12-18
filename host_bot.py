import re
from typing import NamedTuple

from rc_rest_api import post, patch, delete
from placer_bot import PlacerBot
from game_logic import Game
from message_cache import SimpleCache
from time import time


class PlayerInfo(NamedTuple):
    person_name: str
    user_id: int


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
        self.player = None

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

                caller_info = PlayerInfo(
                    person_name=payload["person_name"],
                    user_id=payload["user_id"],
                )

                if msg.find("help") != -1:
                    self._send_message(self.HELP_TEXT, caller_info)
                elif msg == "start game":
                    self._start_game(caller_info)
                elif msg == "clean up":
                    self._reset(caller_info)
                elif msg == "demo":
                    self._demo(caller_info)
                elif msg == "hint":
                    self._hint(caller_info)
                elif self.game:
                    guess = msg.strip()
                    self._guess(caller_info, guess.upper())
                else:
                    self._send_message("I don't understand you", caller_info)
            else:
                print(f"[Host Bot {self.id}]: Got a message but failed to parse it")

    def cleanup(self):
        while self.placers:
            pbot = self.placers.pop()
            pbot.clear()
            pbot.vanish()
        delete(id=self.id)

    def _start_game(self, caller_info):
        if self._cannot_end_current_game(caller_info):
            self._send_message("Another game is already in progress", caller_info)
        else:
            self._send_message("Please wait while I cleanup...", caller_info)
            self._reset(caller_info)

            self.player = caller_info
            self._send_message(f"Started a game for you, {caller_info.person_name}. I've chosen my code.")

            self.game = Game()
            self.turn = -1
            self.gametime = time()

            pbot = PlacerBot(self.start_x-4, self.start_y+2)
            self.placers.append(pbot)
            pbot.write_secret()

    def _cannot_end_current_game(self, caller_info):
        return (
            self.player and self.player.user_id not in [caller_info.user_id, self.id]
            and self.game and time() - self.gametime <= 180
        )

    def _reset(self, caller_info):
        if self._cannot_end_current_game(caller_info):
            self._send_message("Cannot reset someone else's game while it's in progress", caller_info)
        else:
            self._send_message("Resetting everything...", caller_info)
            while self.placers:
                pbot = self.placers.pop()
                pbot.clear()
                pbot.vanish()
            self.player = None
            self.game = None
            self.turn = -1
            self.gametime = None

    def _demo(self, caller_info):
        if self._cannot_end_current_game(caller_info):
            self._send_message("Another game is already in progress", caller_info)
        else:
            self._send_message("Please wait while I cleanup...", caller_info)
            self._reset(caller_info)

            self.player = PlayerInfo(
                person_name=self.BOTNAME,
                user_id=self.id,
            )

            self._send_message("Started a demo game. I've chosen my code.")

            self.game = Game()
            self.turn = -1
            self.gametime = time()

            pbot = PlacerBot(self.start_x-4, self.start_y+2)
            self.placers.append(pbot)
            pbot.write_secret()

            while self.game:
                guess = self.game.get_guess_code()
                self._guess(self.player, guess)

    def _hint(self, caller_info):
        if not self.player:
            self._send_message("No game in progress", caller_info)
        elif self.game and self.player.user_id != caller_info.user_id:
            self._send_message("Only the current player can request a hint", caller_info)
        else:
            self._send_message(f"I would suggest choosing {self.game.get_guess_code()}")

    def _guess(self, caller_info, guess_text):
        print(caller_info.person_name, guess_text)
        if not self.player:
            self._send_message("No game in progress", caller_info)
        elif self.player.user_id != caller_info.user_id:
            self._send_message("Cannot participate in someone else's game", caller_info)
        elif not self.game:
            self._send_message("Game is already over!")
        elif len(guess_text) != 4 or not all(ch in {"R", "O", "G", "B", "P", "Y"} for ch in guess_text):
            self._send_message(
                f"{guess_text} is not a valid guess, {caller_info.person_name}. Please enter a string of four colors."
            )
        else:
            self.turn += 1
            self._send_message(f"Guessed: {guess_text}", caller_info)

            pbot = PlacerBot(self.start_x-4, self.start_y+13-self.turn)
            self.placers.append(pbot)
            pbot.write_code(guess_text)

            pos_c, off_c = self.game.process_guess(guess_text)

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
        true_code = self.game.get_true_code()
        if win:
            self._send_message(f"{self.player.person_name} wins!")
        else:
            self._send_message(f"Sorry, you've run out of guesses. My code was {true_code}", self.player)

        pbot = self.placers[0]
        pbot.clear()
        pbot.write_code(true_code)

        msg = "Congratulations!" if win else "Better luck next time."
        for pbot in self.placers:
            pbot.message(msg)

        self.game = None
        self.turn = -1
        self.gametime = None

    def _send_message(self, text, caller_info=None):
        msg_text = text
        if caller_info:
            msg_text = f"@**{caller_info.person_name}** {text}"
        msg_req = {
            "bot": {"message": msg_text}
        }
        patch(id=self.id, j=msg_req)
        print(f"[Host Bot {self.id}]: Sent message with '{msg_text}'")
