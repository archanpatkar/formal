# Based on:
# https://oleg.fi/gists/posts/2018-07-12-llc-in-agda.html
# https://www.cs.cmu.edu/~fp/courses/linear/handouts/linlam.pdf
from collections import namedtuple

# Base
vapp = namedtuple("app",["term1","term2"])
vvar = namedtuple("var",["v","name"])
vlam = namedtuple("lam",["type","body","v"])

# Multiplicative
vtensI = namedtuple("tensI",["term1","term2"])
vtensE = namedtuple("tensE",["pair","body","v1","v2"])
voneI = namedtuple("one", [])
voneE = namedtuple("let1",["term","body"])

# Additive
vwithI = namedtuple("withI",["term1","term2"])
vwithE0 = namedtuple("fst",["pair"])
vwithE1 = namedtuple("snd",["pair"])
vunit = namedtuple("unit", [])
vabort = namedtuple("abort",["term","type"])
vinl = namedtuple("inl",["type","term"])
vinr = namedtuple("inr",["type","term"])
vmatch = namedtuple("match",["term","case1","case2","v1","v2"])

# Types
atomic = namedtuple("atomic", ["n"]) # Atomic Type()
arrow = namedtuple("arrow", ["term1","term2"]) # Linear Implication
tensor = namedtuple("tensor", ["term1","term2"]) # Linear Tensor
munit = namedtuple("one", []) # One
pair = namedtuple("pair", ["term1","term2"]) # Linear Pair
aunit = namedtuple("tee", []) # ⊤
azero = namedtuple("zero", []) # ⊥
sum = namedtuple("sum", ["term1","term2"]) # Linear Sum

# Usage
one = namedtuple("one", []) # One
none = namedtuple("zero", []) # Zero
tons = namedtuple("tons", []) # Tons for !

# Explicit Peano De Bruijn
vz = namedtuple("zero", []) # Zero
vs = namedtuple("succ", ["term"]) # Successor

err = namedtuple("err", ["msg"]) # Error

def lookup(ctx,usage,v):
    match v, ctx, usage:
        case vz(), [t,*ctail], [one(), *utail]:
            if isinstance(t, aunit):
                return err("cannot use variable of type ⊤")
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

    if isinstance(type, aunit):
        return err("no binding on ⊤")

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
                case (aunit(), _): return err("cannot apply argument of type ⊤")
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
        case (type1, usage1):
            match type_check(term2, ctx, usage1):
                case (type2, usage2):
                    return (tensor(type1, type2), usage2)
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
        case (tensor(type1, type2), usage1):
            new_ctx = [type1,type2]+ctx
            new_usage = [one(),one()]+usage1
            match type_check(body, new_ctx, new_usage):
                case (c_ty, [none(), none(), *usage2]):
                    return (c_ty, usage2)
                case err(msg) as e: return e
                case _:
                    return err(f"Type error in tensor elimination: {body}")
        case err(msg) as e: return e
        case _:
            return err(f"Type error in tensor elimination: {pair}")

def type_voneI(ctx, usage, o):
    return (munit(), usage)

def type_voneE(ctx, usage, o):
    term = o.term
    body = o.body
    match type_check(term, ctx, usage):
        case (munit(), usage):
            return type_check(body, ctx, usage)
        case err(msg) as e: return e
        case _:
            return err(f"Type error in multipicative unit elimination: {term}")

def type_vunit(ctx, usage, u):
    return (aunit(), usage)

def type_withI(ctx, usage, wi):
    term1 = wi.term1
    term2 = wi.term2
    match type_check(term1, ctx, usage):
        case (type1, usage1):
            match type_check(term2, ctx, usage1):
                case (type2, usage2):
                    return (pair(type1, type2), usage2)
                case err(msg) as e: return e
                case _:
                    return err(f"Type error in additive pair introduction: {term2}")
        case err(msg) as e: return e
        case _:
            return err(f"Type error in additive pair introduction: {term1}")

def type_withE0(ctx, usage, we0):
    p = we0.pair
    match type_check(p, ctx, usage):
        case (pair(type1, type2), usage):
            return (type1, usage)
        case err(msg) as e: return e
        case _:
            return err(f"Type error in additive pair elimination fst: {pair}")

def type_withE1(ctx, usage, we1):
    p = we1.pair
    match type_check(p, ctx, usage):
        case (pair(type1, type2), usage):
            return (type2, usage)
        case err(msg) as e: return e
        case _:
            return err(f"Type error in additive pair elimination snd: {pair}")

def type_abort(ctx, usage, ab):
    term = ab.term
    type = ab.type
    match type_check(term, ctx, usage):
        case (azero(), usage1):
            return (type, usage1)
        case err(msg) as e: return e
        case _:
            return err("Abort requires argument of type 0 or ⊥")
        
def type_inl(ctx, usage, inl):
    term = inl.term
    type = inl.type
    match type_check(term, ctx, usage):
        case (type1, usage1) if type1 == type.term1:
            return (sum(type1, type.term2), usage1)
        case err(msg) as e: return e
        case _:
            return err(f"Type error in additive injection left: {term}")

def type_inr(ctx, usage, inr):
    term = inr.term
    type = inr.type
    match type_check(term, ctx, usage):
        case (type2, usage1) if type2 == type.term2:
            return (sum(type.term1, type2), usage1)
        case err(msg) as e: return e
        case _:
            return err(f"Type error in additive injection right: {term}")

def type_check(t,ctx,usage):
    match t:
        case vvar(v, _):
            return lookup(ctx, usage, v)
        case vlam(ty, _, _) as l: 
            if isinstance(ty, aunit):
                return err("lambda abstraction over ⊤ is not allowed")
            return type_lambda(ctx, usage, l)
        case vapp(_, _) as ap:
            # add unit check
            return type_app(ctx, usage, ap)
        case vtensI(_, _) as ti:
            return type_tensI(ctx, usage, ti)
        case vtensE(_, _, _, _) as te:
            return type_tensE(ctx, usage, te)
        case voneI() as o: 
            return type_voneI(ctx, usage, o)
        case voneE(_, _) as o:
            return type_voneE(ctx, usage, o)
        case vwithI(_, _) as wi:
            return type_withI(ctx, usage, wi)
        case vwithE0(_) as we0:
            return type_withE0(ctx, usage, we0)
        case vwithE1(_) as we1:
            return type_withE1(ctx, usage, we1)
        case vunit() as u:
            return type_vunit(ctx, usage, u)
        case vabort(_, _) as ab:
            return type_abort(ctx, usage, ab)
        case vinl(_,_) as inl:
            return type_inl(ctx, usage, inl)
        case vinr(_,_) as inr:
            return type_inr(ctx, usage, inr)
        case vmatch(_, _, _, _, _) as m:
            pass
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
        case pair(t1, t2):
            return f"({tstr(t1)} & {tstr(t2)})"
        case sum(t1, t2):
            return f"({tstr(t1)} ⊕ {tstr(t2)})"
        case munit():
            return "1"
        case aunit():
            return "⊤"
        case azero():
            return "⊥"
        case _:
            return str(ty)
        
def vstr(e):
    match e:
        case vvar(_, name):
            return name
        case vlam(ty, body, v):
            return f"(λ:{tstr(ty)}. {vstr(body)})"
        case vapp(f, x):
            left  = vstr(f)
            right = vstr(x)
            return f"({left} {right})"
        case vtensI(t1, t2):
            return f"({vstr(t1)} ⊗ {vstr(t2)})"
        case vtensE(pair, body):
            return f"(let (1,0) = {vstr(pair)} in {vstr(body)})"
        case voneI():
            return "1"
        case voneE(unit, body):
            return f"(let () = {vstr(unit)} in {vstr(body)})"
        case vwithI(t1, t2):
            return f"({vstr(t1)}, {vstr(t2)})"
        case vwithE0(pair):
            return f"(fst {vstr(pair)})"
        case vwithE1(pair):
            return f"(snd {vstr(pair)})"
        case vunit():
            return "()"
        case vabort(term, type):
            return f"(abort {vstr(term)} as {tstr(type)})"
        case vinl(term, sumty):
            return f"(inl {tstr(sumty)} {vstr(term)})"
        case vinr(term, sumty):
            return f"(inr {tstr(sumty)} {vstr(term)})"
        case vmatch(term, case1, case2):
            return f"(match {vstr(term)} with inl 1 => {vstr(case1)} | inr 0 => {vstr(case2)})"
        case _:
            return str(e)
        
def reify(e):
    match e:
        case vvar(_, name):
            return name
        case vlam(ty, body, v):
            return f"(λ {v}:{tstr(ty)}. {vstr(body)})"
        case vapp(f, x):
            return f"({vstr(f)} {vstr(x)})"
        case vtensI(t1, t2):
            return f"({vstr(t1)} ⊗ {vstr(t2)})"
        case vtensE(pair, body, v1, v2):
            return f"(let ({v1},{v2}) = {vstr(pair)} in {vstr(body)})"
        case voneI():
            return "1"
        case voneE(unit, body):
            return f"(let () = {vstr(unit)} in {vstr(body)})"
        case vwithI(t1, t2):
            return f"({vstr(t1)}, {vstr(t2)})"
        case vwithE0(pair):
            return f"(fst {vstr(pair)})"
        case vwithE1(pair):
            return f"(snd {vstr(pair)})"
        case vunit():
            return "()"
        case vabort(term, ty):
            return f"(abort {vstr(term)} as {tstr(ty)})"
        case vinl(term, sumty):
            return f"(inl {vstr(term)} as {tstr(sumty)})"
        case vinr(term, sumty):
            return f"(inr {vstr(term)} as {tstr(sumty)})"
        case vmatch(term, case1, case2, v1, v2):
            return f"(match {vstr(term)} with inl {v1} => {vstr(case1)} | inr {v2} => {vstr(case2)})"
        case _:
            return str(e)


closed_term = lambda t: type_check(t, [], [])

print(vstr(vlam(atomic(0), vapp(V(0), V(0)), "x")))
print(tstr(closed_term(vlam(atomic(0), V(0), "x"))[0]))

dup = vlam(
    arrow(atomic(0), arrow(atomic(0), atomic(1))),
    vlam(atomic(0), vapp(vapp(V(1), V(0)), V(0)), "x"),
    "f"
)
print(reify(dup))
print(vstr(dup))
print(tstr(closed_term(dup)[0]))

print(vstr(vlam(atomic(0), vapp(V(0), V(0)), "x")))
print(tstr(closed_term(vlam(atomic(0), vapp(V(0), V(0)), "x"))[0]))

curry = vlam(
    arrow(tensor(atomic(0), atomic(1)), atomic(2)),
    vlam(atomic(0),
         vlam(atomic(1),
              vapp(V(2), vtensI(V(1), V(0))),
              "y"),
         "x"),
    "f"
)
print(reify(curry))
print(vstr(curry))
print(tstr(closed_term(curry)[0]))

uncurry = vlam(
    arrow(atomic(0), arrow(atomic(1), atomic(2))),
    vlam(
        tensor(atomic(0), atomic(1)),
        vtensE(
            V(0),
            vapp(
                vapp(V(3), V(0)),
                V(1)
            ),
            "x", "y"
        ),
        "p"
    ),
    "f"
)
print(reify(uncurry))
print(vstr(uncurry))
print(tstr(closed_term(uncurry)[0]))

mul_unit = vlam(
    munit(),
    voneE(
        V(0),
        vlam(atomic(0), V(0), "x")
    ),
    "u"
)
print(reify(mul_unit))
print(vstr(mul_unit))
print(tstr(closed_term(mul_unit)[0]))

ft = vlam(
    pair(atomic(0), atomic(1)),
    vwithE0(V(0)),
    "p"
)
print(reify(ft))
print(vstr(ft))
print(tstr(closed_term(ft)[0]))

st = vlam(
    pair(atomic(0), atomic(1)),
    vwithE1(V(0)),
    "p"
)
print(reify(st))
print(vstr(st))
print(tstr(closed_term(st)[0]))

pintro = vlam(
    atomic(0),
    vlam(
        atomic(1),
        vwithI(V(1), V(0)),
        "y"
    ),
    "x"
)
print(reify(pintro))
print(vstr(pintro))
print(tstr(closed_term(pintro)[0]))

cp = vwithI(
    vlam(atomic(0), V(0), "x"),
    vlam(atomic(1), V(0), "y")
)
print(reify(cp))
print(vstr(cp))
print(tstr(closed_term(cp)[0]))

u = vlam(
    aunit(),
    V(0),
    "u"
)
print(reify(u))
print(vstr(u))
print(tstr(closed_term(u)[0]))

abterm = vlam(
    azero(),
    vabort(V(0), atomic(0)),
    "x"
)
print(reify(abterm))
print(vstr(abterm))
print(tstr(closed_term(abterm)[0]))

# closed_term = lambda t: type_check(t, [], [])

# print(vstr(vlam(atomic(0), vapp(V(0), V(0)))))
# print(tstr(closed_term(vlam(atomic(0), V(0)))[0]))

# dup = vlam(arrow(atomic(0), arrow(atomic(0),atomic(1))), vlam(atomic(0), vapp(vapp(V(1), V(0)), V(0))))
# print(vstr(dup))
# print(closed_term(dup))

# print(vstr(vlam(atomic(0), vapp(V(0), V(0)))))
# print(tstr(closed_term(vlam(atomic(0), vapp(V(0), V(0))))))

# curry = vlam(
#     arrow(tensor(atomic(0),atomic(1)), atomic(2)),           
#     vlam(atomic(0),                                
#       vlam(atomic(1),                             
#         vapp(                               
#           V(2),                              
#           vtensI(V(1), V(0))                
#         )
#       )
#     )
# )
# print(vstr(curry))
# print(tstr(closed_term(curry)[0]))

# uncurry = vlam(
#     arrow(atomic(0), arrow(atomic(1), atomic(2))),
#     vlam(
#       tensor(atomic(0),atomic(1)),                    
#       vtensE(
#         V(0),                                
#         vapp(                                
#           vapp(V(3), V(0)),                
#           V(1)                            
#         )
#       )
#     )
# )
# print(vstr(uncurry))
# print(tstr(closed_term(uncurry)[0]))

# mul_unit = vlam(
#     munit(),
#     voneE(
#         V(0), 
#         vlam(atomic(0), V(0))
#     )
# )
# print(vstr(mul_unit))
# print(tstr(closed_term(mul_unit)[0]))


# # \x: A&B. fst x
# # \x: A&B. snd x

# ft = vlam(
#     pair(atomic(0), atomic(1)),
#     vwithE0(V(0))
# )
# print(vstr(ft))
# print(tstr(closed_term(ft)[0]))

# st = vlam(
#     pair(atomic(0), atomic(1)),
#     vwithE1(V(0))
# )
# print(vstr(st))
# print(tstr(closed_term(st)[0]))

# pintro = vlam(
#     atomic(0),
#     vlam(
#         atomic(1),
#         vwithI(V(1), V(0))
#     )
# )
# print(vstr(pintro))
# print(tstr(closed_term(pintro)[0]))

# cp = vwithI(
#     vlam(atomic(0), V(0)),
#     vlam(atomic(1), V(0))
# )
# print(vstr(cp))
# print(tstr(closed_term(cp)[0]))

# u = vlam(
#     aunit(),
#     V(0)
# )
# print(vstr(u))
# print(tstr(closed_term(u)[0]))

# abterm = vlam(
#     azero(),
#     vabort(V(0), atomic(0))
# )

# print(vstr(abterm))
# print(tstr(closed_term(abterm)[0]))