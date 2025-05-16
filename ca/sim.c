#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

// Rule 110 - Turing complete - Cook(2004)
// https://wpmedia.wolfram.com/sites/13/2018/02/15-1-1.pdf

// Based on
// https://www.cs.emory.edu/~cheung/Courses/255/Syllabus/1-C-intro/bit-array.html
#define GetBit(A,k,size) (A[(k/(size*8))] & (1u << (k%(size*8))))
#define SetBit(A,k,size) (A[(k/(size*8))] |= (1u << (k%(size*8))))
#define ClearBit(A,k,size) (A[(k/(size*8))] &= (~(1u << (k%(size*8)))))

typedef struct {
    int* base;
    int len;
    int cap;
} bitvec;

bitvec* init_size(bitvec* v, int initial) {
    int bits = sizeof(int)*8;
    // int ceil trick
    v->cap = (initial + bits-1)/bits;
    v->len = 0;
    v->base = (int*)calloc(v->cap,sizeof(int));
    return v;
}

bitvec* new_bitvec(int size) {
    return init_size(malloc(sizeof(bitvec)), size);
}

int get(bitvec* v, int index){
    if(index < 0 || index >= v->len) return 0;
    return GetBit(v->base,index,sizeof(int)) != 0;
}

int getwrap(bitvec* v, int index){
    if(v->len == 0) return 0;
    if(index < 0)
        index = v->len + (index % v->len);
    else if(index >= v-> len) 
        index = index % v->len;
    return GetBit(v->base,index,sizeof(int)) != 0;
}

int set(bitvec* v, int index, int val) {
    if((v->cap*sizeof(int)*8) <= index) {
        int bits = sizeof(int)*8;
        int need = index+1;
        // int ceil trick
        int want = (need + bits-1)/bits;
        v->cap = want;
        v->base = (int*)realloc(v->base,sizeof(int)*v->cap);
        v->len = index;
    }
    if(val) SetBit(v->base,index,sizeof(int));
    else ClearBit(v->base,index,sizeof(int));
    if (index >= v->len) v->len = index+1;
    return val;
}

void free_bitvec(bitvec* v) {
    free(v->base);
    free(v);
}

#define BitMask(...) new_bitmask((int[]){__VA_ARGS__}, NUMARGS(__VA_ARGS__))
#define match_mask(mask,vec,offset) (apply_mask(mask,vec,offset,&op_and,&op_xnor,1) == 1)
typedef int (*reducer)(int acc, int val);
typedef int (*bitop)(int v1,int v2);

typedef struct {
    int* mask;
    int len;
} bitmask;

bitmask* new_bitmask(int* arr, int len) {
    bitmask* m = malloc(sizeof(bitmask));
    m->len = len;
    int* marr = malloc(sizeof(int)*len);
    memcpy(marr,arr,len*sizeof(int));
    m->mask = marr;
    return m;
}

int op_and(int acc, int v) { return acc & v; }
// int op_xnor(int v1,int v2) { return ~(v1 ^ v2); }
int op_xnor(int v1,int v2) { return v1 == v2; }

int apply_mask(bitmask* mask, bitvec* vec, int offset, reducer r, bitop op, int acc) {
    for(int i = 0;i < mask->len;i++) {
        int idx = offset+i;
        acc = r(acc, op(mask->mask[i],getwrap(vec,idx)));
    }
    return acc;
}

typedef struct {
    bitmask* pattern;
    int new;
} rule;

typedef struct {
    rule* rules;
    int len;
    int cap;
} ruleset;

ruleset* new_ruleset(int size){
    ruleset* rs = malloc(sizeof(ruleset));
    rs->cap = size;
    rs->len = 0;
    rs->rules = malloc(sizeof(rule)*size);
    return rs;
}

void add_rule(ruleset* rs, char* pattern, int result) {
    int len = strlen(pattern);
    int* mask = malloc(sizeof(int)*len);
    for(int i = 0;i < len;i++) mask[i] = pattern[i]=='0'? 0:1;
    if(rs->len == rs->cap) {
        rs->cap *= rs->cap;
        rs->rules = realloc(rs->rules,sizeof(rule)*rs->cap);
    }
    rs->rules[rs->len].pattern = new_bitmask(mask,len);
    rs->rules[rs->len].new = result;
    rs->len += 1;
}

void fill_state(bitvec* world, char* state) {
    int n = strlen(state);
    for(int i = 0;i < n;i++) {
        set(world,i,state[i] == '1');
    }
}

char* ca2str(bitvec* vec, char on, char off) {
    char* st = malloc(sizeof(char)*vec->len+1);
    for(int i = 0;i<vec->len;i++) {
        st[i] = get(vec,i)? on:off;
    }
    st[vec->len] = '\0';
    return st;
}

// void grow_left(bitvec* vec, int chunks) {}
// void grow_right(bitvec* vec, int chunks) {}

void sim(int iters, bitvec* world, ruleset* rs, char sym[2]) {
    int wsize = world->len;
    for(int i = 0; i < iters; i++) {
        // if(get(world,0)) grow_left(world,1);
        // if(get(world,world->len-1)) grow_right(world,1);
        // int wsize = world->len;

        bitvec* next = new_bitvec(wsize);
        next->len = wsize;

        for(int j = 0; j < world->len; j++) {
            int newbit = 0;
            for(int r = 0; r < rs->len; r++) {
                bitmask* m = rs->rules[r].pattern;
                int start = j - (m->len/2);
                if(match_mask(m,world,start)) {
                    newbit = rs->rules[r].new;
                    break;
                }
            }
            set(next,j,newbit);
        }

        char* st = ca2str(next, sym[1], sym[0]);
        puts(st);
        free(st);
        free_bitvec(world);
        world = next;
    }
    free_bitvec(world);
}

// tweet sized line allowed
#define MAX_LINE 281

int main(int argc, char *argv[]) {
    int iterations = 0;
    int wsize = 0;
    char sym[3];
    char* state;
    char line[MAX_LINE];
    ruleset* rs;
    bitvec* world;

    scanf("%d %d %2s", &iterations, &wsize, sym);

    state = malloc(sizeof(char)*wsize+1);
    scanf("%s",state);

    rs = new_ruleset(8);
    while(fgets(line, MAX_LINE, stdin)) {
        if(strncmp(line,"END",3) == 0) break;
        char pattern[MAX_LINE];
        int result;
        if(sscanf(line, "%[^,],%d", pattern, &result) == 2) {
            add_rule(rs,pattern,result);
        }
    }

    world = new_bitvec(wsize);
    fill_state(world,state);
    world->len = wsize;

    char* str = ca2str(world, sym[1], sym[0]);
    puts(str);
    free(str);

    sim(iterations, world, rs, sym);
    return 0;
}