from collections import namedtuple
import re

# future impl. todo
# let bindings
# memoized laziness/call by need: cell = namedtuple("cell",["v"])
# number & bool literals
# if else

# AST
app = namedtuple("app",["term1","term2"])
var = namedtuple("var",["name"])
lam = namedtuple("lam",["name","term"])

def lstr(expr):
    match expr:
        case app(term1, term2): return f"({lstr(term1)} {lstr(term2)})"
        case var(name): return f"{name}"
        case lam(name, term): return f"(λ{name}.{lstr(term)})"
        case _: return expr

def tokenize(s):
    return re.findall(r'[()λ\\.]|\w+', s)

def parse(tokens):
    def expr():
        if not tokens:
            raise SyntaxError("Unexpected end of input")
        
        token = tokens.pop(0)
        
        if token == '(':
            e = application()
            if not tokens or tokens.pop(0) != ')':
                raise SyntaxError("Mismatched parentheses")
            return e
        elif token in ['λ', '\\']:
            if not tokens:
                raise SyntaxError("Incomplete lambda expression")
            return lamb()
        else:
            return var(token)
    
    def lamb():
        params = []
        while tokens and tokens[0] not in ['.']:
            params.append(tokens.pop(0))
        if not tokens or tokens.pop(0) != '.':
            raise SyntaxError("Expected '.' after lambda variable(s)")
        body = application()
        for param in reversed(params):
            body = lam(param, body)
        return body

    def application():
        e = expr()
        while tokens and tokens[0] != ')':
            e = app(e, expr())
        return e

    result = application()
    if tokens:
        raise SyntaxError("Unexpected tokens after expression")
    return result