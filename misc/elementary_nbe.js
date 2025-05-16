// NBE for bags & bundle game
// https://okmij.org/ftp/tagless-final/NBE.html

const bag = (n) => [...Array(n)].map(_=>"#");
const bundle = (l, r) => Object({"l": l, "r": r});
const empty = bag(0);

function isValid(b) {
    if (Array.isArray(b)) {
        return b.reduce((acc, v) => (v == "#") + acc, 0) == b.length;
    }
    return b?.l && b?.r && isValid(b.l) && isValid(b.r);
}

function str(b) {
    if(Array.isArray(b)) return `[${b.join("")}]`;    
    if((b?.l || b?.l == 0) && (b?.r || b?.r == 0)) return `(${str(b.l)}, ${str(b.r)})`;
    return b;
}

// Nat01S
function eval(b) {
    if(Array.isArray(b)) return b.length;
    if(b?.l && b?.r) return eval(b.l) + eval(b.r);
    return b;
}

function reify(b) {
    return Number.isInteger(b)? bag(b): b;
}

function check(term) {
    console.log("input   :", str(term));
    console.log("isValid :", isValid(term));
    const val = eval(term);
    console.log("eval    :", val);
    const norm = reify(val);
    console.log("norm    :", str(norm));
    console.log("eval(norm):", eval(norm));
    console.log("---");
};

check(empty); // []
check(bag(3)); // [###]
check(bundle(bag(1), bag(2))); // ([#],[##])
check(bundle(bag(1), bundle(bag(1), bag(1)))); // ([#],([#],[#]))
check(bundle(bundle(bag(0),bag(2)),empty)); // (([],[##]),[])
check(bundle(bundle(bag(1),bag(1)), bundle(bag(1), bag(1)))); // (([#],[#]), ([#],[#]))
check(bundle(bundle(bag(1),bag(1)), bundle(bag(1), bag(2)))); // (([#],[#]), ([#],[##]))