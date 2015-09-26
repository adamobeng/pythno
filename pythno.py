from pyparsing import *
import re


def Syntax():
    operator = oneOf('+ - / *')
    op = Suppress(Literal('('))
    cp = Suppress(Literal(')'))
    int_lit = Word(nums)
    expr = Forward()
    atom = int_lit | Group(op + expr + cp)
    expr << Group(operator + atom + atom)
    ####
    #  expr = operator + integer_literal + integer_literal
    rule = op + expr + cp
    return rule

test_strings = (
    '(+ 1 2)',
    '(- 1 2)',
    '(- 1 (+ 1 2))',
    '(+ 1 2',
    '+ 1 2)',
    '+ 1 a)',
    '(+ 1n2 2)',
)


def parse(s):
    return Syntax().parseString(s).asList()


def add_to_locals(x, y):
    locals_[x] = y

OPERATORS = {
    '+': lambda x, y: int(x) + int(y),
    '-': lambda x, y: int(x) - int(y),
    '/': lambda x, y: int(x) / int(y),
    '*': lambda x, y: int(x) * int(y),
    'define': add_to_locals,
}


def peval(s):
    parsed = parse(s)
    result = eval_(parsed)
    return result


def eval_(s, locals_={}):
    if isinstance(s, str):
        result = s
    elif isinstance(s, list) and len(s) == 1:
        result = eval_(s[0])
    else:
        op, one, two = s
        result = OPERATORS[op](eval_(one), eval_(two))
    return result


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
        # Also try removing char
        print prefix + 'Exception is', e, e.loc
        # print e.loc, e.line, expected
        return parse_fix(s, prefix=prefix + ' ' * 4)
for s in test_strings:
    print parse_fix(s)
