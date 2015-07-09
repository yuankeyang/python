# -*- Mode: Python -*-

# We're using dictionaries as sets.
# mostly works, unfort. can't use dicts for set-of-sets...
def make_set (l=()):
    r = {}
    for x in l:
        r[x] = None
    return r

# Set: {<item>:None, ...}
def set_union (a, b):
    r = a.copy()
    r.update (b)
    return r

def set_difference (a, b):
    r = a.copy()
    for x in b.keys():
        if r.has_key (x):
            del r[x]
    return r

def nary_to_binary (exp):
    if type(exp) == type(''):
        if len(exp) > 1:
            return nary_to_binary ((CONCAT,) + tuple(map (None, exp)))
        else:
            return exp
    else:
        op = exp[0]
        args = map (nary_to_binary, exp[1:])
        if len(args) < 3:
            return (op,) + tuple(args)
        else:
            return (op, args[0], nary_to_binary ((op,) + tuple(args[1:])))

# this is so they print out pretty
class operator:
    def __init__ (self, s):
        self.s = s
    def __repr__ (self):
        return self.s

# operators
CONCAT = operator('+')
STAR = operator('*')
OR = operator('|')
# XXX pretty easy to make other operators, like 'PLUS'

# (ab|ba)*
# (star (or (concat "a" "b") (concat "b" "a")))

r1 = '(ab|ba)*'
r2 = '(\r\n.\r\n)|(\n.\n)|(\r.\r)'

# XXX write a parser, too...
def pprint_regexp (exp):
    if type(exp) == type(''):
        return exp
    else:
        op = exp[0]
        args = map (pprint_regexp, exp[1:])
        if op is CONCAT:
            return ''.join (args)
        elif op is STAR:
            return '(' + args[0] + ')*'
        elif op is OR:
            return '(' + '|'.join (args) + ')'
        else:
            raise ValueError, 'Unknown operator "%s"' % op

# ab
# (ab)
# (ab)*
# a|b
# (a|b)*

def is_special (ch):
    return ch in "()*|"

def maybe_concat (exp, sub):
    if exp is None:
        return sub
    else:
        return (CONCAT, exp, sub)

def parse_regexp (s, pos=0):
    exp = None
    while 1:
        if pos >= len(s):
            return exp, pos
        else:
            ch = s[pos]
            if ch == '(':
                sub, pos = parse_regexp (s, pos+1)
                exp = maybe_concat (exp, sub)
            elif ch == ')':
                return exp, pos
            elif ch == '*':
                return (STAR, exp), pos
            elif ch == '|':
                sub, pos = parse_regexp (s, pos+1)
                exp = (OR, exp, sub)
            elif ch == '\\':
                # literal character
                pos += 1
                exp = maybe_concat (exp, s[pos])
            else:
                exp = maybe_concat (exp, ch)
            pos += 1

class regexp_to_nfa_converter:

    def __init__ (self):
        self.counter = 0

    def next_state (self):
        result = self.counter
        self.counter += 1
        return result

    # ((<from>, (<char>, <to>), ...), <start>, <end>)

    def walk_exp (self, m):
        "walk a tree-regexp creating an NFA"
        if type(m) == type(''):
            # XXX assumes single character
            s = self.next_state()
            e = self.next_state()
            return [(s, (m, e))], s, e
        else:
            op = m[0]
            if op is CONCAT:
                (a_trans, a_start, a_end) = self.walk_exp (m[1])
                (b_trans, b_start, b_end) = self.walk_exp (m[2])
                # one new transition
                trans =  a_trans + b_trans + [(a_end, (None, b_start))]
                return trans, a_start, b_end
            elif op is STAR:
                e_trans, e_start, e_end = self.walk_exp (m[1])
                new_start = self.next_state()
                new_end   = self.next_state()
                # four new transitions
                trans = e_trans + [
                    (e_end,	(None, e_start)),
                    (new_start,	(None, e_start)),
                    (e_end,	(None, new_end)),
                    (new_start, (None, new_end))
                    ]
                return trans, new_start, new_end
            elif op is OR:
                (a_trans, a_start, a_end) = self.walk_exp (m[1])
                (b_trans, b_start, b_end) = self.walk_exp (m[2])
                new_start = self.next_state()
                new_end   = self.next_state()
                # four new transitions
                trans = a_trans + b_trans + [
                    (new_start,	(None, a_start)),
                    (new_start,	(None, b_start)),
                    (a_end,	(None, new_end)),
                    (b_end,	(None, new_end))
                    ]
                return trans, new_start, new_end
            else:
                raise ValueError, "unknown operator '%s'" % repr(op)

    def coalesce_nfa (self, m):
        "group transitions by <from-state>"
        r = [[] for x in range (self.counter)]
        #r = map (lambda x: [], range(self.counter))
        tl, start, end = m
        tl.sort()
        for start, trans in tl:
            r[start].append (trans)
        return r, start, end

    def go (self, exp):
        return self.coalesce_nfa (self.walk_exp (exp))

#def regexp_to_nfa (exp):
#    return regexp_to_nfa_converter().go (nary_to_binary (exp))

def regexp_to_nfa (exp):
    parsed, ignore = parse_regexp (exp)
    # I'm pretty sure nary_to_binary isn't needed because of parse_regexp
    return regexp_to_nfa_converter().go (parsed)

class nfa_dfa_converter:

    def __init__ (self, nfa, start, end):
        self.nfa = nfa
        self.start = start
        self.end = end
        self.initial = self.epsilon_closure (start)
        self.states = [self.initial]
        self.dfa = []

    def moves (self, state, symbol):
        "all from <state> with <symbol>"
        r = {}
        for sym, to_state in self.nfa[state]:
            if sym == symbol:
                r[to_state] = None
        return r

    def non_epsilon_moves (self, state):
        r = {}
        for sym, to_state in self.nfa[state]:
            if sym is not None:
                r[sym] = None
        return r

    def epsilon_closure (self, state):
        return self._epsilon_closure (state, make_set([state]))

    def _epsilon_closure (self, state, visited):
        epsilon_moves = self.moves (state, None)
        adjoined = set_union (visited, epsilon_moves)
        if len(visited) == len(adjoined):
            return visited
        else:
            r = {}
            for s in set_difference (adjoined, visited).keys():
                r = set_union (r, self._epsilon_closure (s, adjoined))
            return r

    def symbol_closure (self, state, symbol):
        one = self.epsilon_closure (state)
        two = make_set()
        for s in one.keys():
            two = set_union (two, self.moves (s, symbol))
        r = make_set()
        for s in two.keys():
            r = set_union (r, self.epsilon_closure (s))
        return r

    def set_symbol_closure (self, set, symbol):
        r = make_set()
        for s in set.keys():
            r = set_union (r, self.symbol_closure (s, symbol))
        return r

    def set_non_epsilon_moves (self, set):
        r = make_set()
        for s in set.keys():
            r = set_union (r, self.non_epsilon_moves (s))
        return r

    def find_end_states (self):
        "find those members of <state_set> that contain <end_state>"
        state_sets = self.states
        end_state = self.end
        r = []
        for i in range(len(state_sets)):
            set = state_sets[i]
            if set.has_key (end_state):
                r.append (i)
        return r

    def walk (self, index, set):
        symbols = self.set_non_epsilon_moves (set)
        for sym in symbols.keys():
            closure = self.set_symbol_closure (set, sym)
            # have we seen this superstate yet?
            if closure in self.states:
                self.dfa.append ((index, sym, self.states.index (closure)))
            else:
                # it's a new superstate
                new_index = len(self.states)
                self.states.append (closure)
                # so walk it
                self.walk (new_index, closure)
                self.dfa.append ((index, sym, new_index))

    def go (self):
        self.walk (0, self.initial)
        self.dfa.sort()
        return self.dfa, self.find_end_states()

    def minimize (self):
        final = make_set (self.find_end_states())
        t = {}
        for fs, ch, ts in self.dfa:
            t2 = t.get (fs, {})
            t2[ch] = ts
            t[fs] = t2
            
        # make sure final states exist
        for f in final.keys():
            if not t.has_key (f):
                t[f] = {}

        # partition
        non_final = set_difference (make_set (t.keys()), final)
        part = [final.keys(), non_final.keys()]
        last_size = len(part)

        # churn
        while 1:
            # build state->set_index map
            m = {}
            for i in range(len(part)):
                for s in part[i]:
                    m[s] = i
            #
            s = {}
            crib = {}
            for fs, trans in t.items():
                s2 = {}
                for ch, ts in trans.items():
                    part_num = m[ts]
                    s2[(ch,part_num)] = None
                s2 = s2.keys()
                s2.sort()
                s[tuple(s2)] = None
                crib[fs] = tuple(s2)
            # s now holds new partitions, convert to list-of-state form
            s = s.keys()
            s.sort()
            crib = reverse_map (crib)
            new_part = map (lambda x,c=crib: c[x], s)
            # keep partitioning until there's no progress
            if len(new_part) == len(part):
                break
            else:
                part = new_part

        # <part> now holds our final paritioning of DFA states.
        # collapse those that are equivalent

        # we sort the new partition so that state zero (initial) is in front...
        for p in part:
            p.sort()
        part.sort()

        # make old_state->new_state map
        m = {}
        for i in range(len(part)):
            for s in part[i]:
                m[s] = i
        
        # translate dfa
        old_dfa = t
        new_dfa = []
        for i in range(len(part)):
            # pick the first of the equiv set
            equiv = part[i][0]
            old_trans = old_dfa[equiv]
            new_trans = []
            for (ch, ts) in old_trans.items():
                new_trans.append ((ch, m[ts]))
            new_dfa.append (new_trans)
        # translate final states
        new_finals = {}
        for f in final.keys():
            new_finals[m[f]] = None

        # ugh, what a bitch that was!
        return new_dfa, new_finals.keys()

def reverse_map (d):
    r = {}
    for key, value in d.items():
        l = r.get (value, [])
        l.append (key)
        r[value] = l
    return r

def nfa_to_dfa (m, s, e):
    c = nfa_dfa_converter(m, s, e)
    c.go()
    return c.minimize()

def regexp_to_dfa (exp):
    m, s, e = regexp_to_nfa (exp)
    return nfa_to_dfa (m, s, e)

def build_dfa_tables (dfa, finals, ignore_case=1):
    nstates = len(dfa)
    table = range(nstates)
    for i in range(nstates):
        t = 256 * [-1]
        moves = dfa[i]
        for ch, ts in moves:
            t[ord(ch)] = ts
            if ignore_case:
                t[ord(ch.lower())] = ts
        table[i] = t
    finals_table = [0] * nstates
    for f in finals:
        finals_table[f] = 1
    return table, finals_table

class machine:

    def __init__ (self, dfa, finals, ignore_case=1):
        self.dfa = dfa
        self.state_table, self.finals_table = build_dfa_tables (dfa, finals, ignore_case)
        self.state = 0

    def feed (self, data):
        result = []
        in_machine = None
        last_entry = None
        for i in range(len(data)):
            ch = data[i]
            where_to = self.state_table[self.state][ord(ch)]
            if where_to == -1:
                # non-accepting version of state zero
                self.state = 0
                in_machine = None
                last_entry = None
            else:
                if in_machine is None:
                    in_machine = 1
                    last_entry = i
                self.state = where_to
                if self.finals_table[self.state]:
                    result.append ((i, last_entry))
        return result, last_entry

def regexp_machine_1 (exp, ignore_case=1):
    dfa, finals = regexp_to_dfa (exp)
    m = machine (dfa, finals, ignore_case)
    return m

def regexp_machine (exp, ignore_case=1):
    import dfa
    fa, finals = regexp_to_dfa (exp)
    state_table, finals_table = build_dfa_tables (fa, finals, ignore_case)
    m = dfa.dfa (state_table, finals_table)
    return m
