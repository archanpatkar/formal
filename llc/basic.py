# Based on:
# https://oleg.fi/gists/posts/2018-07-12-llc-in-agda.html

from collections import namedtuple

# Terms
vapp = namedtuple("app",["term1","term2"])
vvar = namedtuple("var",["v","name"])
vlam = namedtuple("lam",["type","body"])
vtensI = namedtuple("tensI",["term1","term2"])
vtensE = namedtuple("tensE",["pair","body"])

# Types
atomic = namedtuple("atomic", ["n"]) # Atomic Type
arrow = namedtuple("arrow", ["term1","term2"]) # Linear Implication
tensor = namedtuple("tensor", ["term1","term2"]) # Linear Tensor

one = namedtuple("one", []) # One
none = namedtuple("zero", []) # Zero
# tons = namedtuple("tons", []) # Tons !

# Explicit Peano De Bruijn
vz = namedtuple("zero", []) # Zero
vs = namedtuple("succ", ["term"]) # Successor

err = namedtuple("err", ["msg"]) # Error

def lookup(ctx,usage,v):
    match v, ctx, usage:
        case vz(), [t,*ctail], [one(), *utail]:
            return (t,[none()]+utail)
        case vs(term), [t,*ctail], [u,*utail]:
            result = lookup(ctail, utail, term)
            if isinstance(result, err): return result
            ty,updated = result
            return (ty, [u]+updated)
        case _, _, _:
            return err(f"Type error: Variable not found in context or invalid usage {v}")

def type_lambda(ctx, usage, lam):
    type = lam.type
    body = lam.body
    new_ctx = [type]+ctx
    new_usage = [one()]+usage
    match type_check(body, new_ctx, new_usage):
        case (rety, [u, *rest]):
            match u:
                case none():
                    return (arrow(type, rety), rest)
                case err(msg) as e: return e
                case _: 
                    return err(f"Not consistent with linearity: {u}")
        case err(msg) as e: return e
        case _:
            return err(f"Type error in lambda body: {body}")

def type_app(ctx, usage, ap):
    term1 = ap.term1
    term2 = ap.term2
    match type_check(term1, ctx, usage):
        case (arrow(type1, type2), usage1):
            match type_check(term2, ctx, usage1):
                case (arg, usage2) if arg == type1:
                    return (type2, usage2)
                case err(msg) as e: return e
                case _ as t:
                    return err(f"Type does not match: {term2}")
        case err(msg) as e: return e
        case _:
            return err(f"Expected function: {term1}")

def type_tensI(ctx, usage, ti):
    term1 = ti.term1
    term2 = ti.term2
    match type_check(term1, ctx, usage):
        case (type1, usage_a):
            match type_check(term2, ctx, usage_a):
                case (type2, usage_b):
                    return (tensor(type1, type2), usage_b)
                case err(msg) as e: return e
                case _:
                    return err(f"Type error in tensor introduction: {term2}")
        case err(msg) as e: return e
        case _:
            return err(f"Type error in tensor introduction: {term1}")

def type_tensE(ctx, usage, te):
    pair = te.pair
    body = te.body
    match type_check(pair, ctx, usage):
        case (tensor(type1, type2), usage_a):
            new_ctx = [type1,type2]+ctx
            new_usage = [one(),one()]+usage_a
            match type_check(body, new_ctx, new_usage):
                case (c_ty, [none(), none(), *usage_b]):
                    return (c_ty, usage_b)
                case err(msg) as e: return e
                case _:
                    return err(f"Type error in tensor elimination: {body}")
        case err(msg) as e: return e
        case _:
            return err(f"Type error in tensor elimination: {pair}")

def type_check(t,ctx,usage):
    match t:
        case vvar(v,_):
            return lookup(ctx, usage, v)
        case vlam(_, _) as l: 
            return type_lambda(ctx, usage, l)
        case vapp(term1, term2) as ap:
            return type_app(ctx, usage, ap)
        case vtensI(term1, term2) as ti:
            return type_tensI(ctx, usage, ti)
        case vtensE(pair, body) as te:
            return type_tensE(ctx, usage, te)
        case err(msg) as e: return e
        case _:
            return err(f"Unknown term: {t}")

peano = lambda n: vz() if n == 0 else vs(peano(n - 1))
V = lambda n: vvar(peano(n), f"v{n}")

# basic functionality test
# ustack = lambda n: [one() for i in range(n)]
# cstack = lambda t,n: [t for i in range(n)]
# vstack = lambda n: [V(i) for i in range(n)]

# ctx = cstack(a(0),5)
# usage = ustack(5)
# vv = vstack(5)

# print(vv)
# print(usage)
# print(ctx)

# ty,usage = lookup(ctx, usage, V(0).v)
# print(ty)
# print(usage)

# ty,usage = lookup(ctx, usage, V(1).v)
# print(ty)
# print(usage)


def tstr(ty):
    match ty:
        case atomic(n):
            return f"A{n}"
        case arrow(t1, t2):
            left = tstr(t1)
            right = tstr(t2)
            if isinstance(t1, arrow):
                left = f"({left})"
            return f"{left} ⊸ {right}"
        case tensor(t1, t2):
            return f"({tstr(t1)} ⊗ {tstr(t2)})"
        case _:
            return str(ty)
        
def vstr(e):
    match e:
        case vvar(_, name):
            return name
        case vlam(ty, body):
            return f"(λ:{tstr(ty)}. {vstr(body)})"
        case vapp(f, x):
            left  = vstr(f)
            right = vstr(x)
            return f"({left} {right})"
        case vtensI(t1, t2):
            return f"({vstr(t1)} ⊗ {vstr(t2)})"
        case vtensE(pair, body):
            return f"(let (x,y) = {vstr(pair)} in {vstr(body)})"
        case _:
            return str(e)


closed_term = lambda t: type_check(t, [], [])

print(vstr(vlam(atomic(0), vapp(V(0), V(0)))))
print(tstr(closed_term(vlam(atomic(0), V(0)))[0]))

dup = vlam(arrow(atomic(0), arrow(atomic(0),atomic(1))), vlam(atomic(0), vapp(vapp(V(1), V(0)), V(0))))
print(vstr(dup))
print(closed_term(dup))

print(vstr(vlam(atomic(0), vapp(V(0), V(0)))))
print(tstr(closed_term(vlam(atomic(0), vapp(V(0), V(0))))))

curry = vlam(
    arrow(tensor(atomic(0),atomic(1)), atomic(2)),           
    vlam(atomic(0),                                
      vlam(atomic(1),                             
        vapp(                               
          V(2),                              
          vtensI(V(1), V(0))                
        )
      )
    )
)
print(vstr(curry))
print(tstr(closed_term(curry)[0]))

uncurry = vlam(
    arrow(atomic(0), arrow(atomic(1), atomic(2))),
    vlam(
      tensor(atomic(0),atomic(1)),                    
      vtensE(
        V(0),                                
        vapp(                                
          vapp(V(3), V(0)),                
          V(1)                            
        )
      )
    )
)
print(vstr(uncurry))
print(tstr(closed_term(uncurry)[0]))