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

def start_game():
	num = random.randrange(max_bound)
	numstr = numberToBase(num,6).zfill(4)
	numcnt = Counter(numstr)
	  
	n, nstr, ncnt = get_guess()
	   
	if (n == num):   
		print("Great! You guessed the number in just one try! You're a Mastermind!") 
		
	else: 
		ctr = 0  

		while (n != num):   
			ctr += 1
			
			pos_correct, offpos_correct = feedback(nstr,ncnt,numstr,numcnt)

			print("Black pegs", pos_correct)
			print("White pegs", offpos_correct)
			
			n, nstr, ncnt = get_guess()

		print("You've become a Mastermind!") 
		print("It took you only", ctr, "tries.") 

def get_guess():
	nstr = input("Guess the passcode:").zfill(4)
	n = int(nstr,6)
	ncnt = Counter(nstr)
	
	return n, nstr, ncnt
	
def feedback(nstr,ncnt,numstr,numcnt):
	pos_correct = sum(nstr[-i-1] == numstr[-i-1] for i in range(min(len(numstr),4)))
	offpos_correct = sum(min(ncnt[s],numcnt[s]) for s in numcnt if s in ncnt) - pos_correct
	
	return pos_correct, offpos_correct
	
start_game()
