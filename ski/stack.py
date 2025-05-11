# Refs:
# https://en.wikipedia.org/wiki/SKI_combinator_calculus
# https://github.com/ngzhian/ski
# https://yager.io/HaSKI/HaSKI.html
# https://doisinkidney.com/posts/2020-10-17-ski.html
# https://github.com/archanpatkar/kombis

from collections import namedtuple

# I = namedtuple("I",[])
# K = namedtuple("K",[])
# S = namedtuple("S",[])
I = "I"
K = "K"
S = "S"
AP = namedtuple("AP",["term1","term2"])
box = namedtuple("box",["v"])

def lstr(expr):
    match expr:
        case AP(term1, term2): return f"({lstr(term1)} {lstr(term2)})"
        case box(v): return f"[{v}]"
        case _: return expr

def step(p):
    term,stack = p
    match term, stack:
        case AP(t1, t2), st:
            return t1,[t2] + st
        case "I", [next,*st]:
            return next,st
        case "K", [x,y,*st]:
            return x,st
        case "S", [x,y,z,*st]:
            return x, [z,AP(y,z)] + st
        case box(v) as b, [next,*st]:
            return next,st
        case _, []: return None
        case "I", []: return None
        case "K", st if len(st) < 2: return None
        case "S", st if len(st) < 3: return None
        case _,_: raise ValueError(f"Unknown term {term}")

def eval(term):
    stack = []
    while out := step((term,stack)):
        term, stack = out
    if stack:
        stack = stack[::-1]
        while len(stack):
            term = AP(term, stack.pop())
    return term
    
print(lstr(eval(I)))
print(lstr(eval(AP(I, I))))
print(lstr(eval(AP(AP(K, K), I))))
print(lstr(eval(AP(AP(S, K), I))))
print(lstr(eval(AP(AP(AP(S, K), S), K))))