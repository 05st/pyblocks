# shared.py contains data that should be shared among modules and helpful functions

# dictionary for levels, contains the text and expected value for goal variable
# the second half of the levels are quite hard to solve in pyblocks, but possible
LEVEL_DATA = {
    1: ("Set 'goal' to the result of 5 + 5 * 5", 30),
    2: ("Set 'goal' to be the smallest prime factor of 12345678", 2),
    3: ("Set 'goal' to be the sum of all odd numbers under 100", 2500),
    4: ("Find the sum of all the multiples of 3 or 5 below 1000.", 233168),
    5: ("Each new term in the Fibonacci sequence is generated by adding the previous two terms. Start with 1, 2, 3, 5 and so on. Find the sum of the even fibonacci numbers less than 4,000,000.", 4613732),
    6: ("The first prime numbers are 2, 3, 5, _. What is the 10 001st prime number?", 104743),
    7: ("The Collatz sequence is created with the following rules: n/2 if n is even, otherwise 3*n+1. For example, starting with 13: 13 -> 40 -> 20 -> 10. Find the starting number with the longest sequence under 1,000,000.", 837799),
    8: ("Start on the top left of a 20x20 grid lattice. If you can only move down or to the right, how many paths to the bottom left are there?", 137846528820),
    9: ("Two numbers are amicable if the sum of the PROPER divisors of number A is equal to number B, and vice versa. A cannot equal B. Find the sum of all amicable numbers under 1000.", 31626),
    10: ("Congratulations! You've completed all of the levels.", None),
}

# blocks that will appear on the insert menu
INSERT_OPTIONS = [
    "StartBlock",
    "NumBlock", "TextBlock", "TrueBlock", "FalseBlock",
    "PrintBlock", "RetBlock",
    "AddBlock", "SubBlock", "MulBlock", "DivBlock", "ModBlock",
    "EqBlock", "NEqBlock", "GrBlock", "LsBlock",
    "NotBlock", "RndBlock", "FlrBlock", "CelBlock",
    "IncBlock", "DecBlock",
    "VarBlock", "SetBlock",
    # "FuncBlock", "CallBlock",
    "IfBlock", "WhileBlock", "ForBlock",
]

# checks collision between rectangle and point
def check_collision(pos, size, point):
    rx, ry = pos
    px, py = point
    w, h = size
    return (px > rx and px < rx + w) and (py > ry and py < ry + h)

# returns a list of strings that are all less than 70 characters (which is about 600 pixels in the font)
def wrap_text(text):
    words = text.split()
    ret = []

    curr = ""
    for word in words:
        if len(curr) + len(word) >= 70 or word == "[BREAK]":
            ret.append(curr)
            curr = "" if word == "[BREAK]" else word
        else:
            curr += f" {word}"
    ret.append(curr)
    return ret

# clamps num into min/max
def clamp(n, mi, ma):
    return min(ma, max(mi, n))

