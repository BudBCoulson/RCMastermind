import random
from collections import Counter

def numberToBase(n, b):
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(str(n % b))
        n //= b
    return "".join(digits[::-1])

class Game:
    MAX_BOUND = int("5555",6)
    COLOR_CODES = {"R": "0", "O": "1", "G": "2", "B": "3", "P": "4", "Y": "5"}
    CODE_COLORS = {val: key for key, val in COLOR_CODES.items()}
    
    def __init__(self):
        self.secrets = self._generate_code()
        
        print(f"Game: init with code data {self.secrets}")
    
    def _generate_code(self):
        num = random.randrange(self.MAX_BOUND)
        numstr = numberToBase(num,6).zfill(4)
        numcnt = Counter(numstr)
        clrstr = "".join(self.CODE_COLORS[d] for d in numstr)
        
        print("Game: generated secrets")
        
        return numstr, numcnt, clrstr
        
    def process_guess(self, guess):
        nstr = "".join(self.COLOR_CODES.get(clr,"") for clr in guess).zfill(4)
        ncnt = Counter(nstr)
        numstr, numcnt, _ = self.secrets
        pos_correct = sum(nstr[-i-1] == numstr[-i-1] for i in range(min(len(numstr),4)))
        offpos_correct = sum(min(ncnt[s],numcnt[s]) for s in numcnt if s in ncnt) - pos_correct
        
        print(f"Game: processed guess {guess} with results {pos_correct}, {offpos_correct}")
        
        return pos_correct, offpos_correct
