import json

# Based on:
# https://tiarkrompf.github.io/notes/?/dependent-types/aside3

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

def forall0(aty,f): return ("forall", aty, f)

def is_forall(t): return isinstance(t, tuple) and t[0] == "forall"

def typed(e,t): 
    o = lambda a: app(o,a)
    o.untyped = e
    o.type = t
    return o

def is_typed(e):
    return e.untyped and e.type

def untyped(e):
    assert is_typed(e), f"no type: {e}"
    return (e.untyped,e.type)

def printt(e):
    tm,ty = untyped(e)
    print("term:", stringize(tm))
    print("type:", stringize(ty))

def forall(aty,f):
    lty,rty = untyped(aty)
    assert rty == "Type" or rty == "Kind", f"illegal argument type/kind: {rty}"
    res,ty = untyped(f(typed("x?",lty)))
    return typed(forall0(lty,lambda x: untyped(f(typed(x,lty)))[0]),ty)

def constant(tm,ty):
    tyt, tyk = untyped(ty)
    assert tyk == "Type" or tyk == "Kind", f"illegal type/kind: {tyk}"
    return typed(tm,tyt)

def fun(aty,f):
    lty,rty = untyped(aty)
    assert rty == "Type" or rty == "Kind", f"illegal argument type/kind: {rty}"
    return typed(
        fun0(lambda x: untyped(f(typed(x,lty)))[0]),
        forall0(lty,lambda x: untyped(f(typed(x,lty)))[1])
    )

def app(f,a):
    f1,fty = untyped(f)
    a1,aty = untyped(a)
    assert is_forall(fty), f"not a function type: {fty}"
    _,lty,frty = fty
    assert aty == lty, f"illegal argument type: {aty} != {lty}"
    res = app0(f1,a1)
    rty = frty(a1)
    return typed(res,rty)

Type = typed("Type","Kind")

# id = fun(Type, lambda t: t)
# printt(id)

# poly_id = fun(Type, lambda t: fun(t, lambda x: x))
# printt(poly_id)

N = constant("N",Type)
z = constant("z",N)
s = constant("s", forall(N,lambda x: N))

three = s(s(s(z)))
printt(three)