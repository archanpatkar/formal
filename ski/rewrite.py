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

def eval(term):
    match term:
        case AP("I", x): return eval(x)
        case AP(AP("K", x), y): 
            return eval(x)
        case AP(AP(AP("S", x), y), z):
            return eval(AP(AP(x,z), AP(y,z)))
        case AP(t1, t2):
            r1,r2 = eval(t1), eval(t2)
            if r1 == t1 and r2 == t2:
                return AP(r1, r2)
            return eval(AP(r1, r2))
        case "S" | "K" | "I": return term
        case box(v) as b: return b
        case _: raise ValueError(f"Unknown term {term}")

print(lstr(eval(I)))
print(lstr(eval(AP(I, I))))
print(lstr(eval(AP(AP(K, K), I))))
print(lstr(eval(AP(AP(S, K), I))))
print(lstr(eval(AP(AP(AP(S, K), S), K))))