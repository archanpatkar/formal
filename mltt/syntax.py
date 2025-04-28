from itertools import count
from dataclasses import dataclass

class expr: pass
class variable(expr): pass

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
class lam(expr): 
    var: variable
    type: ...
    term: ...
    def __str__(self):
        return f"(λ{self.var}:{self.type}.{self.term})"
    
@dataclass(frozen=True)
class pi(expr): 
    var: variable
    type: ...
    term: ...
    def __str__(self):
        return f"(Π{self.var}:{self.type}.{self.term})"

@dataclass(frozen=True)
class app(expr): 
    term1: ...
    term2: ...
    def __str__(self):
        return f"({self.term1} {self.term2})"
    
@dataclass(frozen=True)
class uni(expr): 
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