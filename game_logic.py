import random
from collections import Counter

def numberToBase(n, b):
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(str(n % b))
        n //= b
    return ''.join(digits[::-1])

max_bound = int('5555',6)
num = random.randrange(max_bound)
numstr = numberToBase(num,6).zfill(4)
numcnt = Counter(numstr)
print(num,numstr,numcnt)
  
nstr = input("Guess the passcode:").zfill(4)
n = int(nstr,6)
ncnt = Counter(nstr)
   
if (n == num):   
    print("Great! You guessed the number in just one try! You're a Mastermind!") 
else: 
    ctr = 0  

    while (n != num):   
        ctr += 1
        
        pos_correct = sum(nstr[-i-1] == numstr[-i-1] for i in range(min(len(numstr),4)))
        offpos_correct = sum(min(ncnt[s],numcnt[s]) for s in numcnt if s in ncnt) - pos_correct

        print("Black pegs", pos_correct)
        print("White pegs", offpos_correct)
        nstr = input("Enter your next choice of numbers: ").zfill(4)
        n = int(nstr,6)
        ncnt= Counter(nstr)

    print("You've become a Mastermind!") 
    print("It took you only", ctr, "tries.") 
