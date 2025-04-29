# Based on:
# https://davidchristiansen.dk/tutorials/nbe/
# (untyped part only)

from collections import namedtuple
from common import app,var,lam, let, letrec, defn, recdefn, expr
from common import parse, lstr

CLOS = namedtuple("clos", ["env","var","body"])
N_var = namedtuple("nvar", ["name"])
N_ap = namedtuple("nap", ["rator","rand"])

extend = lambda p, x, value=None: {**p, x: value}

add_star = lambda v: f"{v}*"
freshen = lambda used,v: freshen(used,add_star(v)) if v in used else v

def eval(p, e):
    match e:
        case lam(name, body):
            return CLOS(p, name, body)
        case var(name):
            if name in p: return p[name]
            else: 
                # raise ValueError(f"Unknown variable {name}")
                return N_var(name)
        case app(rator, rand):
            return apply(eval(p, rator), eval(p, rand))

def apply(fun, arg):
    match fun: 
        case CLOS(p, var, body):
           return eval(extend(p, var, arg), body)
        case N_var(_) | N_ap(_, _):
            return N_ap(fun,arg)

def reify(used,v):
    match v:
        case N_var(name): 
            return var(name)
        case N_ap(rator, rand): 
            return app(reify(used,rator), reify(used,rand))
        case CLOS(p, name, body):
            y = freshen(used,name)
            ny = N_var(y)
            nb = reify(extend(used,y), eval(extend(p,name,ny), body))
            return lam(y, nb)

def norm(p, e):
    return reify({}, eval(p, e))

def desugar(env, e):
    match e:
        case var(name):
            return env.get(name, e)
        case app(term1, term2):
            return app(desugar(env, term1), desugar(env, term2))
        case lam(name, body):
            new_env = extend(env, name, var(name)) if name in env else env
            return lam(name, desugar(new_env, body))
        case let(name, df, body):
            return app(
                desugar(env,lam(name, body)), 
                desugar(env, df)
            )
        case letrec(name, df, body):
            # desugar with fix
            fixed = app(var('fix'), lam(name, df))
            return app(
                desugar(env,lam(name, body)), 
                fixed
            )
        case defn(name, expr_):
            expr_d = desugar(env, expr_)
            env[name] = expr_d
            return None
        case recdefn(name, expr_):
            fixed = app(var('fix'), desugar(env,lam(name, expr_)))
            env[name] = fixed
            return None
        case expr(inner_expr):
            return desugar(env, inner_expr)
        case _: return e

def repl():
    print("Lambda Calculus (NBE)")
    print("Enter expressions in the format: \\x. x y or (\\x. x y) z")
    print("Type 'quit' to exit.")
    
    env = {}
    env["fix"] = lam("f", app(
        lam("x", app(var("f"), app(var("x"), var("x")))),
        lam("x", app(var("f"), app(var("x"), var("x"))))
    ))

    while True:
        try:
            user_input = input("λ> ").strip()
            if user_input.lower() == 'quit':
                break
            parsed = parse(user_input)
            print("Parsed:", lstr(parsed))
            result = desugar(env, parsed)
            if result is not None:
                normed = norm({}, result)
                print("Normalized:", lstr(normed))
            else: print("Definition added.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    repl()

# \x. \y. y
# ((\x.x) (\x.x))
# x
# let id = \x. x
# id id
# let const = \x y. x in (const id)