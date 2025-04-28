def lookup_ty(x, ctx):
    return ctx[x][0]

def lookup_value(x, ctx):
    return ctx[x][1]

def extend(ctx, x, ty, value=None):
    # if x in ctx:
    #     raise ValueError(f"Variable {x} already exists in context")
    return {**ctx, x: (ty, value)}