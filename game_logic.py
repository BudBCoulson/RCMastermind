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

max_bound = int("5555",6)
color_codes = {"R": "0", "O": "1", "G": "2", "B": "3", "P": "4", "Y": "5"}

def game():
	num, numstr, numcnt = generate_code()
	print(numstr)
	
	#guess = input("Enter guess:")
	n, nstr, ncnt = process_guess(guess)
	print(nstr)
	
	ctr = 1
		
	while n != num and ctr < 10: 
		pos_correct, offpos_correct = feedback(nstr,ncnt,numstr,numcnt)

		#print("Black pegs", pos_correct)
		#print("White pegs", offpos_correct)
		
		#guess = input("Enter guess:")
		n, nstr, ncnt = process_guess(guess)
		
		ctr += 1
		
	if n == num:
		win()
	else:
		lose()

def generate_code():
	num = random.randrange(max_bound)
	numstr = numberToBase(num,6).zfill(4)
	numcnt = Counter(numstr)
	
	return num, numstr, numcnt

def process_guess(guess):
	nstr = "".join(color_codes.get(clr,"") for clr in guess).zfill(4)
	n = int(nstr,6)
	ncnt = Counter(nstr)
	
	return n, nstr, ncnt
	
def feedback(nstr,ncnt,numstr,numcnt):
	pos_correct = sum(nstr[-i-1] == numstr[-i-1] for i in range(min(len(numstr),4)))
	offpos_correct = sum(min(ncnt[s],numcnt[s]) for s in numcnt if s in ncnt) - pos_correct
	
	return pos_correct, offpos_correct
	
def win():
	print("You win!")
	
def lose():
	print("You lose.")

#game()
