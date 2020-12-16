from typing import Any


class SimpleCache:

    def __init__(self, max_size=100):
        self.set = set()
        self.list = []
        self.max_size = max_size

    def is_seen(self, message: Any) -> bool:
        msg_hash = hash(message["text"] + message["sent_at"])

        if msg_hash in self.set:
            return True
        else:
            self.set.add(msg_hash)
            self.list.append(msg_hash)
            if len(self.list) > self.max_size:
                discarded_hash = self.list.pop(0)
                self.set.remove(discarded_hash)

            return False
