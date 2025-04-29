from collections import namedtuple
from lark import Lark, Transformer, UnexpectedToken

# future impl. todo
# let bindings
# memoized laziness/call by need: cell = namedtuple("cell",["v"])
# number & bool literals
# if else

# AST
# expressions
app = namedtuple("app",["term1","term2"])
var = namedtuple("var",["name"])
lam = namedtuple("lam",["name","term"])
let = namedtuple("let", ["name", "defn", "body"])
letrec = namedtuple("letrec", ["name", "defn", "body"])

# top level
defn = namedtuple("defn", ["name", "expr"])
recdefn = namedtuple("recdefn", ["name", "expr"])
expr = namedtuple("expr", ["expr"])

def lstr(e):
    match e:
        case app(term1, term2): 
            return f"({lstr(term1)} {lstr(term2)})"
        case var(name): 
            return f"{name}"
        case lam(name, term): 
            return f"(λ{name}.{lstr(term)})"
        case let(name, df, body):
            return f"(let {name} = {lstr(df)} in {lstr(body)})"
        case letrec(name, df, body):
            return f"(let rec {name} = {lstr(df)} in {lstr(body)})"
        case defn(name, ex):
            return f"(def {name} = {lstr(ex)})"
        case recdefn(name, ex):
            return f"(recdef {name} = {lstr(ex)})"
        case expr(ex):
            return f"(expr {lstr(ex)})"
        case _: 
            return str(e)
        
def curry(params, body):
    for p in reversed(params):
        body = lam(p, body)
    return body
        
class ASTBuilder(Transformer):
    def start(self, items):
        return items
    
    def param_list(self, items):
        return [str(t) for t in items]

    def expr(self, item):
        (e,) = item
        return expr(e)

    def top_let(self, items):
        name, params, expr = items
        return defn(name, curry(params, expr))

    def top_letrec(self, items):
        name, params, expr = items
        return recdefn(name, curry(params, expr))

    def lam(self, items):
        *params, body = items
        for param in reversed(params):
            body = lam(param, body)
        return body

    def let(self, items):
        name, params, defn_, body = items
        return let(name, curry(params, defn_), body)

    def letrec(self, items):
        name, params, defn_, body = items
        return letrec(name, curry(params, defn_), body)

    def app_chain(self, items):
        # fold left associatively
        e = items[0]
        for item in items[1:]:
            e = app(e, item)
        return e

    def var(self, items):
        (t,) = items
        return var(str(t))

    def group(self, items):
        (e,) = items
        return e

with open("grammar.lark") as f:
    grammar = f.read()

parser = Lark(grammar, parser="lalr", transformer=ASTBuilder())

def parse(source):
    try:
        return parser.parse(source)
    except UnexpectedToken as e:
        print(f"\nSyntax Error at line {e.line}, column {e.column}: unexpected token '{e.token}'")
        lines = source.splitlines()
        if e.line <= len(lines):
            print(lines[e.line - 1])
            print(" " * (e.column - 1) + "^")
        raise e