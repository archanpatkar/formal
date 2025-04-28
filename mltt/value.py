from dataclasses import dataclass
from syntax import variable, svar, genvar, dummy
from syntax import lam, pi, app, uni, subst, refresh
from ctx import extend, lookup_ty, lookup_value

# value 
class value: pass

@dataclass(frozen=True)
class vuni(value): 
    level: int
    def __str__(self):
        return f"vType {self.level}"

@dataclass(frozen=True)
class vpi(value):
    var: variable
    type: ...
    body: callable
    def __str__(self):
        return f"vPi {self.var}:{self.type}.{self.term}"

@dataclass(frozen=True)
class vlam(value):
    var: variable
    type: ...
    body: callable
    def __str__(self):
        return f"vLam {self.var}:{self.type}.{self.term}"

class neutral: pass

@dataclass(frozen=True)
class vneutral(value):
    n: neutral
    def __str__(self):
        return f"vNeutral {self.neutral}"

@dataclass(frozen=True)
class nsvar(neutral):
    name: str
    def __str__(self):
        return self.name

@dataclass(frozen=True)
class ngenvar(neutral):  
    name: str
    index: int
    def __str__(self):
        return f"{self.name}{self.index}"

@dataclass(frozen=True)
class ndummy(neutral):
    name: str = "_"
    def __str__(self):
        return self.name

@dataclass(frozen=True)
class napp(neutral):
    term1: neutral
    term2: value
    def __str__(self):
        return f"nApp {self.term1} {self.term2}"
    
def nvar(v):
    match v:
        case svar(name): return nsvar(name)
        case genvar(name, index): return ngenvar(name, index)
        case dummy(name): return ndummy(name)
        case _: return v

def equal(e1, e2):
    match e1, e2:
        case vneutral(n1), vneutral(n2): return equal_neutral(n1, n2)
        case vuni(i), vuni(j): return i == j
        case vlam(x, t1, e1), vlam(y, t2, e2):
            return equal_abstraction(x, t1, e1, y, t2, e2)
        case vpi(x, t1, e1), vpi(y, t2, e2):
            return equal_abstraction(x, t1, e1, y, t2, e2)
        case _, _: return False

def equal_abstraction(x, t1, e1, y, t2, e2):
    v = vneutral(nvar(refresh(x)))
    return equal(t1, t2) and equal(e1(v),e2(v))

def equal_neutral(n1, n2):
    match n1, n2:
        case nsvar(x), nsvar(y): return x == y
        case ngenvar(x, i), ngenvar(y, j):
            return x == y and i == j
        case ndummy(_), ndummy(_): return True
        case napp(e11, e12), napp(e21, e22):
            return equal_neutral(e11, e21) and equal_neutral(e12, e22)
        case _, _: return False

def eval(ctx, e):
    return _eval(ctx, {}, e)

def _eval(ctx, env, e):
    match e:
        case v if isinstance(v, (svar, genvar, dummy)):
            if v in env: return env[v]
            if v in ctx: 
                vr = lookup_value(v, ctx)
                if vr is not None: return _eval(ctx, env, vr)
                return vneutral(nvar(v))
            else: raise ValueError(f"Unknown identifier {v}")
        case uni(level): return vuni(level)
        case pi(var, type, term):
            return vpi(*eval_abstraction(ctx, env, var, type, term))
        case lam(var, type, term):
            return vlam(*eval_abstraction(ctx, env, var, type, term))
        case app(e1,e2):
            v2 = _eval(ctx, env, e2)
            match _eval(ctx, env, e1):
                case vlam(var, type, body): return body(v2)
                case vneutral(n): return vneutral(napp(n, v2))
                case v if isinstance(v, (vpi, vuni)):
                    raise ValueError(f"Function expected, got {v}")

def eval_abstraction(ctx, env, x, t, e):
    return x, _eval(ctx, env, t), lambda v: _eval(ctx, {**env, x: v}, e)

def reify(v):
    match v:
        case vneutral(n): return reify_neutral(n)
        case vuni(level): return uni(level)
        case vpi(var, type, body): return pi(*reify_abstraction(var, type, body))
        case vlam(var, type, body): return lam(*reify_abstraction(var, type, body))

def reify_neutral(n):
    match n:
        case nsvar(name): return svar(name)
        case ngenvar(name, index): return genvar(name, index)
        case ndummy(name): return dummy(name)
        case napp(term1, term2):
            return app(reify_neutral(term1), reify(term2))

def reify_abstraction(x, t, e):
    # return x, reify(t), reify(e(vneutral(x)))
    return x, reify(t), reify(e(nvar(x)))