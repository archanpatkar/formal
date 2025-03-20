import json

# Based on:
# https://tiarkrompf.github.io/notes/?/dependent-types/aside1

nVars = -1
def fresh():
    global nVars
    nVars += 1
    return f"x{nVars}"

def struct(expr):
    match expr:
        case tuple(e): return tuple(map(struct, e))
        case _ if callable(expr):
            name = fresh()
            return ("=>", name, struct(expr(name)))
        case _: return expr

def stringize(expr):
    global nVars
    save = nVars
    try: return json.dumps(struct(expr))
    except: nVars = save

def fun(x): return x
def app(x,y):
    if callable(x): return x(y)
    return (x, y)

test = ("fun", lambda x: ("app", ("fun",lambda y:y),x))
print(struct(test))
print(stringize(test))

# test = fun(lambda x: app(fun(lambda y: y),x))
# print(stringize(test))

# test = fun(lambda x: app(x,fun(lambda y: y)))
# print(stringize(test))