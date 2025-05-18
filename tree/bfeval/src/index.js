const {tagged, sum} = require("styp");

const t = sum("tree", {
    leaf: [],
    stem: ['x'],
    fork: ['l', 'r']
});

function str(term) {
    return term.cata({
        leaf: () => "△",
        stem: ({x})  => `(△ ${str(x)})`,
        fork: ({l, r}) => `(△ ${str(l)} ${str(r)})`
    });
}

function apply(a,b) {
    return a.cata({
        leaf: () => t.stem(b),
        stem: ({x}) => t.fork(x, b),
        fork: ({l, r}) => l.cata({
            leaf: () => r,
            stem: ({x}) => apply(apply(x,b),apply(r,b)),
            fork: ({l:a1, r:a2}) => b.cata({
                leaf: () => a1,
                stem: ({x: u}) => apply(a2,u),
                fork: ({l:u, r:v}) => apply(apply(r, u), v)
            })
        })
    });
}

let _false = t.leaf;
console.log("false: ",str(_false));
let _true = t.stem(t.leaf);
console.log("true: ",str(_true));
let _not = t.fork(t.fork(_true, t.fork(t.leaf,_false)),t.leaf);
console.log("not: ",str(_not));

let term = apply(_not, _false);
console.log(str(term));
term = apply(_not, _true);
console.log(str(term));