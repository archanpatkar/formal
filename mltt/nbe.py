# Based on:
# https://math.andrej.com/2012/11/11/how-to-implement-dependent-type-theory-ii/
# https://github.com/andrejbauer/andromeda/blob/blog-part-II/

from syntax import svar, genvar, dummy, lam, pi, app, uni, subst
from ctx import extend, lookup_ty
from value import equal as _equal, eval, reify

def normalize(ctx, e):
    return reify(eval(ctx, e))

def equal(ctx, e1, e2):
    return _equal(eval(ctx, e1), eval(ctx, e2))

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

    # Blog test 
    N = svar("N")
    ctx4 = extend({}, N, uni(0))

    z = svar("z")
    ctx4 = extend(ctx4, z, N)

    s = svar("s")
    ctx4 = extend(ctx4, s, pi(dummy("_"), N, N))  # s : N -> N

    # define three
    f = svar("f")
    x = svar("x")
    three = lam(f, pi(dummy("_"), N, N), lam(x, N, app(f, app(f, app(f, x)))))

    ctx4 = extend(ctx4, svar("three"), infer_type(ctx4, three), three)

    print(f"three : {infer_type(ctx4, three)}")

    # three (three s)
    three_app = app(svar("three"), app(svar("three"), s))
    print(f"(three (three s)) : {infer_type(ctx4, three_app)}")

    # (three (three s)) z
    three_app_z = app(three_app, z)
    print(f"(three (three s)) z normalizes to: {normalize(ctx4, three_app_z)}")