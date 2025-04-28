from itertools import count
from dataclasses import dataclass
from typing import Union

# https://math.andrej.com/2012/11/08/how-to-implement-dependent-type-theory-i/
# https://github.com/andrejbauer/andromeda/tree/blog-part-I

class variable: pass

@dataclass(frozen=True)
class svar(variable): 
    name: str
    def __str__(self):
        return self.name

@dataclass(frozen=True)
class genvar(variable): 
    name: str
    index: int
    def __str__(self):
        return f"{self.name}{self.index}"

@dataclass(frozen=True)
class dummy(variable): 
    name: str = "_"
    def __str__(self):
        return self.name

@dataclass(frozen=True)
class lam: 
    var: variable
    type: ...
    term: ...
    def __str__(self):
        return f"(λ{self.var}:{self.type}.{self.term})"
    
@dataclass(frozen=True)
class pi: 
    var: variable
    type: ...
    term: ...
    def __str__(self):
        return f"(Π{self.var}:{self.type}.{self.term})"

@dataclass(frozen=True)
class app: 
    term1: ...
    term2: ...
    def __str__(self):
        return f"({self.term1} {self.term2})"
    
@dataclass(frozen=True)
class uni: 
    level: int
    def __str__(self):
        return f"Type{self.level}"
    
# expr = Union[var, genvar, dummy, uni, app, lam, pi]

_fresh = count(0)
def refresh(term):
    c = next(_fresh)
    match term:
        case svar(name) | genvar(name, _) | dummy(name): 
            return genvar(name, c)
        
def subst(env,e):
    match e:
        case v if isinstance(v, (svar, genvar, dummy)):
            return env.get(v, v)
        case lam(v, type, term)| pi(v, type, term):
            return subst_abs(env, e)
        case app(term1, term2):
            return app(subst(env,term1), subst(env,term2))
        case uni(_): return e
        case _: return e

def subst_abs(env, e):
    xdash = refresh(e.var)
    env = {**env, e.var: xdash}
    match e:
        case pi(var, type, term):
            return pi(xdash, subst(env,type), subst(env,term))
        case lam(var, type, term):
            return lam(xdash, subst(env,type), subst(env,term))
        case _: 
            raise ValueError(f"Invalid term: {e}") 

def lookup_ty(x, ctx):
    return ctx[x][0]

def lookup_value(x, ctx):
    return ctx[x][1]

def extend(ctx, x, ty, value=None):
    # if x in ctx:
    #     raise ValueError(f"Variable {x} already exists in context")
    return {**ctx, x: (ty, value)}

def infer_universe(ctx, t):
    u = infer_type(ctx, t)
    match normalize(ctx, u):
        case uni(level): return level
        case _:
            raise ValueError(f"Type Expected, got {u}")

def infer_pi(ctx, e):
    t = infer_type(ctx, e)
    match normalize(ctx, t):
        case pi(x, s, t):
            return x, s, t
        case _:
            raise ValueError(f"Pi function expected, got {t}")

def check_equal(ctx, e1, e2):
    if not equal(ctx, e1, e2):
        raise ValueError(f"Expressions are not equal: {e1} != {e2}")

def infer_type(ctx, e):
    match e:
        case v if isinstance(v, (svar, genvar, dummy)):
            if v in ctx: return lookup_ty(v, ctx)
            else: raise ValueError(f"Unknown identifier {v}")
        case uni(level):
            return uni(level + 1)
        case pi(var, type, term):
            k1 = infer_universe(ctx, type)
            k2 = infer_universe(extend(ctx,var,type), term)
            return uni(max(k1, k2))
        case lam(var, type, term):
            _ = infer_universe(ctx, type)
            te = infer_type(extend(ctx,var,type), term)
            return pi(var, type, te)
        case app(e1,e2):
            x, s, t = infer_pi(ctx,e1)
            te = infer_type(ctx, e2)
            check_equal(ctx, s, te)
            return subst({x: e2}, t)
  
def normalize(ctx, e):
    match e:
        case v if isinstance(v, (svar, genvar, dummy)):
            if v in ctx: 
                vr = lookup_value(v, ctx)
                if vr is not None: return normalize(ctx, vr)
                return v
            else: raise ValueError(f"Unknown identifier {v}")
        case app(e1,e2):
            e2 = normalize(ctx, e2)
            match normalize(ctx, e1):
                case lam(var, _, term):
                    return normalize(ctx, subst({var: e2}, term))
                case e1:
                    return app(e1, e2)
        case uni(level): return uni(level)
        case pi(var, type, term):
            return pi(*normalize_abstraction(ctx, var, type, term))
        case lam(var, type, term):
            return lam(*normalize_abstraction(ctx, var, type, term))

def normalize_abstraction(ctx, x, t, e):
    t = normalize(ctx, t)
    return x, t, normalize(extend(ctx,x,t), e)

def equal(ctx, e1, e2):
    e1 = normalize(ctx, e1)
    e2 = normalize(ctx, e2)
    return _equal(e1, e2)

def _equal(e1, e2):
    match e1, e2:
        case svar(x), svar(y): return x == y
        case genvar(x, i), genvar(y, j):
            return x == y and i == j
        case dummy(), dummy(): return True
        case uni(i), uni(j): return i == j
        case app(e11, e12), app(e21, e22):
            return _equal(e11, e21) and _equal(e12, e22)
        case lam(x, t1, e1), lam(y, t2, e2):
            return equal_abstraction(x, t1, e1, y, t2, e2)
        case pi(x, t1, e1), pi(y, t2, e2):
            return equal_abstraction(x, t1, e1, y, t2, e2)
        case _: return False

def equal_abstraction(x, t1, e1, y, t2, e2):
    return _equal(t1,t2) and _equal(e1, subst({y:x},e2))



if __name__ == "__main__":
    # expr = lam(var("x"), var("A"), app(var("x"), var("x")))
    # print(subst({}, expr))
    
    A = svar("A")
    ctx = extend({}, A, uni(0))

    # λx:A. x
    id = lam(svar("x"), A, svar("x"))
    print(f"id: {infer_type(ctx, id)}")  # should be Πx:A. A

    # λx:A. λy:A. x
    const = lam(svar("x"), A, lam(svar("y"), A, svar("x")))
    print(f"const: {infer_type(ctx, const)}")  # should be Πx:A. Πy:A. A

    # (id x)
    ctx2 = extend(ctx, svar("x"), A)
    app1 = infer_type(ctx2, app(id, svar("x")))
    print(f"(id x): {app1}")  # should be A

    # full test
    # (λx:A.x) y
    app2 = app(lam(svar("x"), A, svar("x")), svar("y"))  
    ctx3 = extend(ctx, svar("y"), A)
    normed = normalize(ctx3, app2)
    print(f"Normalizing (id y) -> {normed}")  # should be y