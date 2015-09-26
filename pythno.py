from pyparsing import *
import re


def Syntax():
    operator = oneOf('+ - / * define print')
    op = Suppress(Literal('('))
    cp = Suppress(Literal(')'))
    int_lit = Word(nums)
    var = Word(alphas)
    expr = Forward()
    atom = int_lit | var | Group(op + expr + cp)
    expr << operator + atom + atom
    ####
    #  expr = operator + integer_literal + integer_literal
    rule = op + expr + cp| var
    return rule

good_strings = (
    '(+ 1 2)',
    '(- 1 2)',
    '(- 1 (/ 1 2))',
    '(define 1 2)',
    '(+ 1 2) (+ 1 2)',
)
bad_strings = (
    '(+ 1 2',
    '+ 1 2)',
    '+ 1 a)',
    '(+ 1n2 2)',
    )
test_strings = good_strings +bad_strings


def parse(s):
    return Syntax().parseString(s).asList()


global_env = {
    '+': lambda x, y: float(x) + float(y),
    '-': lambda x, y: float(x) - float(y),
    '/': lambda x, y: float(x) / float(y),
    '*': lambda x, y: float(x) * float(y),
}

def peval(s):
    parsed = parse(s)
    result = eval_(parsed)
    return result

def atomize(i):
    try:
        return int(i)
    except:
        try:
            return float(i)
        except:
            return i

# http://norvig.com/lispy.html
def eval_(s, env=global_env):
    s = atomize(s)
    if isinstance(s, int) or isinstance(s, float):
        return s
    elif not isinstance(s, list):
        return env[s]
    elif s[0] == 'define':
        _, var, exp = s
        env[var] = eval_(exp, env)
    elif s[0] == 'print':
        _, exp = s
        return eval_(exp, env)
    else:
        proc = eval_(s[0], env)
        return proc(eval_(s[1], env), eval_(s[2], env))

def parse_fix(s, prefix=''):
    if len(prefix) > 8:
        raw_input()
    print prefix + 'parsing', s
    try:
        parsed = Syntax().parseString(s)
        return parsed
    except ParseException as e:
        expected = re.match('Expected (.*)', e.msg).group(1)
        cats = '(W|Re):\((.*)\)'
        if re.match(cats, expected):
            t, chars = re.match(cats, expected).groups()
            chars = chars.strip("'")
            chars = chars.strip("[]")
            expected = chars[0]
            if t == 'W':
                expected = expected + ' '
        else:
            expected = expected.strip('"')

        if e.loc == 0  or e.loc == len(s):
            # Add char
            s = s[:e.loc] + expected + s[e.loc:]
        else:
            # Replace char
             s = s[:e.loc] + expected + s[min(e.loc+1, len(s)):]
        # Also try removing char
        print prefix + 'Exception is', e, e.loc
        # print e.loc, e.line, expected
        return parse_fix(s, prefix=prefix + ' ' * 4)

for s in test_strings:
    print parse_fix(s)

for s in good_strings:
    print s, peval(s)
