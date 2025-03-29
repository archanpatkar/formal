from collections import namedtuple

# AST
app = namedtuple("app",["term1","term2"])
var = namedtuple("var",["name"])
genvar = namedtuple("genvar",["name","index"])
lam = namedtuple("lam",["var","type","term"])
pi = namedtuple("pi",["var","type","term"])
uni = namedtuple("universe",["level"])
dummy = namedtuple("dummy",["name"])

def lstr(expr):
    match expr:
        case app(term1, term2): return f"({lstr(term1)} {lstr(term2)})"
        case var(name): return f"{name}"
        case genvar(name, index): return f"{name}{index}"
        case lam(var, type, term): return f"(λ{var}:{type}.{lstr(term)})"
        case pi(var, type, term): return f"(Π{var}:{type}.{lstr(term)})"
        case uni(level): return f"Type{level}"
        case _: return expr

def refresh(term, n=0):
    n += 1
    match term:
        case str(name) | genvar(name, _): 
            return genvar(name, n)
        case dummy(_): 
            return genvar("_", n)
        
def subst(env,e):
    match e:
        case var(name) | genvar(name, _) | dummy(name):
            if name in env: return env[name]
            else: return e
        case pi(var, type, term):
            return subst_abs(env, e)
        case lam(var, type, term):
            return subst_abs(env, e)
        case app(term1, term2):
            return app(subst(env,term1), subst(env,term2))
        case uni(level): return e
        case _: return e

def subst_abs(env, e):
    pass