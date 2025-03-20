import json

# Based on:
# https://tiarkrompf.github.io/notes/?/dependent-types/aside2

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

def fun0(x): return x
def app0(x,y):
    if callable(x): return x(y)
    return (x, y)

def is_funtype(t):
    return isinstance(t, tuple) and t[0] == "->"

def is_basetype(t):
    return isinstance(t, str)

def is_type(t):
    return is_funtype(t) or is_basetype(t)

def funtype(x,y):
    assert is_type(x), f"illegal type: {x}"
    assert is_type(y), f"illegal type: {y}"
    return ("->", x, y)

def typed(e,t): return ("typed", e, t)

def is_typed(e):
    return isinstance(e, tuple) and e[0] == "typed"

def untyped(e):
    assert is_typed(e), f"no type: {e}"
    return e[1:]

def printt(e):
    tm,ty = untyped(e)
    print("term:", stringize(tm))
    print("type:", stringize(ty))

def constant(tm,ty):
    assert is_type(ty), f"illegal type: {ty}"
    return typed(tm,ty)

def app(f,a):
    f1,fty = untyped(f)
    a1,aty = untyped(a)
    assert is_funtype(fty), f"not a function type: {fty}"
    assert fty[1] == aty, f"illegal argument type: {aty}"
    _,lty,rty = fty
    assert aty == lty, f"illegal argument type: {aty} != {lty}"
    return typed(app0(f1,a1),rty)

def fun(aty,f):
    assert is_type(aty), f"illegal argument type: {aty}"
    return typed(
        fun0(lambda x: untyped(f(typed(x,aty)))[0]),
        funtype(aty,untyped(f(typed("x?",aty)))[1])
    )

id = fun("Int", lambda x: x)
printt(id)

eta = fun(funtype("Int","Int"), lambda f: fun("Int", lambda x: app(f,x)))
printt(eta)

test = app(app(eta,id),typed(2,"Int"))
printt(test)