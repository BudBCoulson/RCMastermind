import random
from collections import Counter, defaultdict

def numberToBase(n, b):
    if n == 0:
        return ""
    digits = []
    while n:
        digits.append(str(n % b))
        n //= b
    return "".join(digits[::-1])

NUM_COLORS = 6
CODE_LEN = 4   
MAX_BOUND = NUM_COLORS**CODE_LEN - 1
COLOR_CODES = {"R": "0", "O": "1", "G": "2", "B": "3", "P": "4", "Y": "5"}
CODE_COLORS = {val: key for key, val in COLOR_CODES.items()}

class Game:
    
    def __init__(self):
        self.code = self._generate_code()
        
        self.possible = set(range(MAX_BOUND))
        self.combos = set(range(MAX_BOUND))
        self.guess = 7
        
        print(f"Game: init with color code {self._codeforms(self.code)[-1]}")

    def _generate_code(self):
        num = random.randrange(MAX_BOUND)
        return num

    def _codeforms(self, num):
        numstr = numberToBase(num,NUM_COLORS).zfill(CODE_LEN)
        numcnt = Counter(numstr)
        clrstr = "".join(CODE_COLORS[d] for d in numstr)
        
        # print(f"Game: created codeforms {numstr, numcnt, clrstr}")
        
        return numstr, numcnt, clrstr

    def _clr_to_num(self, clrcode):
        return int("".join(COLOR_CODES.get(clr,"") for clr in clrcode),NUM_COLORS)

    def process_guess(self, guess, code=-1, human=True):
        if type(guess) == str:    
            nstr = "".join(COLOR_CODES.get(clr,"") for clr in guess).zfill(CODE_LEN)
            ncnt = Counter(nstr)
            self.guess = int(nstr, NUM_COLORS)
        else:
            nstr, ncnt, _ = self._codeforms(guess)
            
        if code < 0:
            code = self.code
        numstr, numcnt, _ = self._codeforms(code)
        
        pos_correct = sum(nstr[-i-1] == numstr[-i-1] for i in range(min(len(numstr),CODE_LEN)))
        offpos_correct = sum(min(ncnt[s],numcnt[s]) for s in numcnt if s in ncnt) - pos_correct
        
        if human:
            self._update_guesser(pos_correct, offpos_correct)
            print(f"Game: processed guess {guess} with results {pos_correct}, {offpos_correct}")
        
        return pos_correct, offpos_correct

    def get_guess_code(self):
        return self._codeforms(self.guess)[-1]
        
    def get_true_code(self):
        return self._codeforms(self.code)[-1]

    def _update_guesser(self, pos_c, off_c):
        self.possible.discard(self.guess)
        self.combos.discard(self.guess)
        
        self._prune(pos_c, off_c)
        self.guess = -1
        self._minimax()
        
        print("Game: updated guesser")

    def _prune(self, pos_c, off_c):
        newposs = set()
        for cd in self.possible:
            if (pos_c, off_c) == self.process_guess(self.guess, cd, False):
                newposs.add(cd)
        self.possible = newposs
        
        print("Game: pruned remaining possibilities")

    def _minimax(self):
        scores = {}
        
        for gs in self.combos:
            score_counts = defaultdict(int)
            for cd in self.possible:
                keypegs = self.process_guess(gs, cd, False)
                score_counts[keypegs] += 1
            scores[gs] = max(score_counts.values()) if score_counts else float('inf')

        minmax = min(scores.values())
        next_guesses = {gs for gs in scores if scores[gs] == minmax}
        
        for ng in next_guesses:
            if ng in self.possible:
                self.guess = ng
        
        if self.guess < 0:        
            self.guess = next_guesses.pop()
            
        print(f"Game: ran minimax, updating guess to {self._codeforms(self.guess)[-1]}")
