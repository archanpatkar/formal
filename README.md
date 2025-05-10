<div align="center" style="background-color:white"/>
<img src="./LambdaCube.png" height="215em" width="250em"/>

### Lambda Cube

</div>

This repository contains my implementation of calculi corresponding to the [**Lambda Cube**](https://en.wikipedia.org/wiki/Lambda_cube). The older JavaScript implementations, while full-featured, relied more on eval/apply operational semantics. The present revival is based on the more traditional syntactic rewriting approach. The overall aim of this project is to deeply explore the foundational aspects of logic, computation, plt, type theory, functional programming, compilers, and formal verification.

> foundations are always under construction

* Propositional Logic
  - [DPLL SAT Solver](https://github.com/archanpatkar/vostas)
* SKI Combinator Calculus
  - [Rewrite-based normalization](https://github.com/archanpatkar/lambdacube/blob/main/ski/rewrite.py)
* (**λ**) Untyped Lambda Calculus - [Python](https://github.com/archanpatkar/lambdacube/blob/main/ulc) [JS](https://github.com/archanpatkar/ulc)
  - [α-conversion](https://github.com/archanpatkar/lambdacube/blob/main/ulc/lambda.py)
  - [de Bruijn representation](https://github.com/archanpatkar/lambdacube/blob/main/ulc/debruijn.py)
  - [Normalization by Evaluation (NbE)](https://github.com/archanpatkar/lambdacube/blob/main/ulc/nbe.py)
  - [Eval/apply operational semantics](https://github.com/archanpatkar/ulc/blob/master/src/eval.js) (old)
  - [Minimal core embedded in host language](https://github.com/archanpatkar/lambdacube/blob/main/coc/embedded/untyped.py)
* (**λ→**) Simply Typed Lambda Calculus - [JS](https://github.com/archanpatkar/styla)
  - [Church-style syntax directed type checker](https://github.com/archanpatkar/styla/blob/master/src/type.js) (old)
  - [Minimal core embedded in host language](https://github.com/archanpatkar/lambdacube/blob/main/coc/embedded/stlc.py)
* (**LLC**) Linear Lambda Calculus - [Python](https://github.com/archanpatkar/lambdacube/blob/main/llc/)
  - [Linearity-enforcing typechecker](https://github.com/archanpatkar/lambdacube/blob/main/llc/type.py)
    - de Bruijn-Peano core
    - explicit usage tracking
    - supports ⊗, ⊕, &, 1, ⊥, ⊤
* Restricted System F with Type Inference (*Hindley-Milner-Damas*) - [JS](https://github.com/archanpatkar/hml)
  - [Algorithm W](https://github.com/archanpatkar/hml/blob/master/src/type.js)
* (**λ2**) System F / Polymorphic Lambda Calculus - [JS](https://github.com/archanpatkar/systemF)
* (**Fω**) System F Omega / Higher-Order Polymorphic Lambda Calculus - [JS](https://github.com/archanpatkar/omega)
* (**MLTT**) Martin-Löf (dependent) type theory - [Python](https://github.com/archanpatkar/lambdacube/blob/main/mltt)
  - [Substitution, Type Inference](https://github.com/archanpatkar/lambdacube/blob/main/mltt/main.py)
  - [Normalization by Evaluation (NbE)](https://github.com/archanpatkar/lambdacube/blob/main/mltt/nbe.py)
* (**λC**) Calculus of constructions - 
  - [Minimal core embedded in host language](https://github.com/archanpatkar/lambdacube/blob/main/coc/embedded/dep.py)
