from common import app,var,lam
from common import tokenize,parse,lstr

def fresh_var(v):
    return f"{v}'"

def free_variables(expr):
    match expr:
        case var(name): return {name}
        case app(term1, term2): return free_variables(term1) | free_variables(term2)
        case lam(name, body): return free_variables(body) - {name}

def alpha_convert(expr, old, new):
    match expr:
        case var(name):
            return var(new) if name == old else expr
        case app(term1, term2):
            t1 = alpha_convert(term1,old,new)
            t2 = alpha_convert(term2,old,new)
            return app(t1,t2)
        case lam(name, body):
            if name == old: return expr
            return lam(name,alpha_convert(body,old,new))

def substitute(expr,formal,actual):
    match expr:
        case var(name):
            return actual if name == formal else expr
        case app(term1,term2):
            return app(substitute(term1,formal,actual),substitute(term2,formal,actual))
        case lam(name,body):
            # add a case: if actual instanceof var and actual in freevars set
            if formal in free_variables(body):
                new_name = fresh_var(name)
                new_body = alpha_convert(body,name,new_name)
                return lam(new_name,substitute(new_body,formal,actual)) 
            return lam(name,substitute(body,formal,actual))

# call by name
def evaluate(expr):
    while True:
        match expr:
            case app(lam(name,body),term):
                expr = substitute(body,name,term)
            case app(term1,term2):
                t1 = evaluate(term1)
                if isinstance(t1,lam): expr = app(t1,term2)
                else: return app(t1,term2)
            case _: return expr

def repl():
    print("Lambda Calculus")
    print("Enter expressions in the format: \\x. x y or (\\x. x y) z")
    print("Type 'quit' to exit.")
    
    while True:
        user_input = input("λ> ").strip()
        if user_input.lower() == 'quit':
            break
        try:
            expr = parse(tokenize(user_input))
            print("Parsed:", lstr(expr))
            result = evaluate(expr)
            print("Evaluated:", lstr(result))
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    repl()