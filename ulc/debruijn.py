from collections import namedtuple
from common import app,var,lam
from common import tokenize,parse

# de Bruijn representation
bvar = namedtuple("bvar", ["index","name"])
dlam = namedtuple("lam", ["term","name"])

def lstr(expr):
    match expr:
        case app(term1, term2): return f"({lstr(term1)} {lstr(term2)})"
        case var(name): return f"{name}"
        case lam(name, term): return f"(λ{name}.{lstr(term)})"
        case bvar(index,_): return f"{index}"
        case dlam(term,_): return f"(λ.{lstr(term)})"
        case _: return expr

def de_bruijn(expr, ctx=None):
    if ctx == None: ctx = []
    match expr:
        case app(term1, term2):
            return app(de_bruijn(term1,ctx),de_bruijn(term2,ctx))
        case var(name): 
            if name in ctx:
                return bvar(ctx.index(name),name)
            return expr
        case lam(name, term):
            return dlam(de_bruijn(term,[name]+ctx),name)

def restore_names(expr):
    match expr:
        case app(term1, term2):
            return app(restore_names(term1), restore_names(term2))
        case dlam(term,n):
            return lam(n, restore_names(term))
        case bvar(_,name): return var(name)
        case var(_): return expr

def shift(term,offset,level=0):
    match term:
        case bvar(index,n):
            if index >= level:
                # free var
                return bvar(index+offset,n)
            return term
        case app(term1,term2):
            return app(shift(term1,offset,level),shift(term2,offset,level))
        case dlam(term,n):
            return dlam(shift(term,offset,level+1),n)
        case var(_): return term

def substitute(body,actual,level=0):
    match body:
        case bvar(index,n):
            if index == level: return shift(actual,level) 
            elif index > level: return bvar(index-1,n)
            return body
        case app(term1,term2):
            return app(substitute(term1,actual,level),substitute(term2,actual,level))
        case dlam(term,n):
            return dlam(substitute(term,actual,level+1),n)
        case var(_): return body

def evaluate(expr):
    match expr:
        case app(dlam(body,n),term):
            return evaluate(substitute(body,term))
        case app(term1,term2):
            t1 = evaluate(term1)
            if isinstance(t1,dlam): 
                return evaluate(app(t1,term2))
            return app(t1,evaluate(term2))
        case dlam(body,n):
            # this requires shifting.
            # otherwise i guess it is not necessary.
            return dlam(evaluate(body),n)
        case _: return expr

def repl():
    print("Lambda Calculus (De Bruijn)")
    print("Enter expressions in the format: \\x. x y or (\\x. x y) z")
    print("Type 'quit' to exit.")
    
    while True:
        user_input = input("λ> ").strip()
        if user_input.lower() == 'quit':
            break
        try:
            expr = parse(tokenize(user_input))
            print("Parsed:", lstr(expr))
            expr = de_bruijn(expr)
            print("de Bruijn:",lstr(expr))
            result = evaluate(expr)
            print("Evaluated:", lstr(result))
            print("Restored:",lstr(restore_names(result)))
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    repl()

# tested for de bruijn indexing correctness
# λx. x - (λ.0)
# λx. λy. x - (λ.(λ.1))
# (λx. x y) z - (λx. x y) z
# λx. λy. λz. x z (y z) - (λ.(λ.(λ.(2 0 (1 0)))))
# (λx. λy. x (y x)) (λz. z) - ((λ.(λ.(1 (0 1)))) (λ.0))
# λx. (λy. y (x z)) (λw. x w) - (λ.((λ.(0 (1 z))) (λ.(1 0))))
# (λx. λy. x (y x)) (λz. z) (λw. w a) - ((λ.(λ.(1 (0 1)))) (λ.0) (λ.(0 a)))
# x y z - (x y z)
# λa. λb. λc. λd. λe. a (b (c (d e))) - (λ.(λ.(λ.(λ.(λ.(4 (3 (2 (1 0)))))))))
# (λx. x x) (λy. y (λz. y z)) - ((λ.(0 0)) (λ.(0 (λ.(1 0)))))

# tested for shifting.
# \x.\y.\z. (\i. \j. i) (\k. x y z)
# (\x.\y.\z. (\i. \j. i) (\k. x y z)) (\q.q) (\t.t) v
# (\x.\y.\z. (\i. \j. i) (\k. x y z)) (\q.q) (\t.t) a b c
# (\x.\y.\z. (\i. \j. i) (\k. x y z)) a b c d e f
# (\x y z. (\i j. i) (\k. x y z)) a b c d e