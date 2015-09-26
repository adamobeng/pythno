from pyparsing import *
import re

op = Suppress(Literal('('))
cp = Suppress(Literal(')'))

integer_literal = Word(nums)
expr = Forward()
operand = Or(integer_literal, expr)
expr << op + Literal('+') + operand + operand + cp
rule = OneOrMore(expr)

integer_literal = Word(nums)
binary_operator = Or([Literal('+'), Literal('-'), Literal('/'), Literal('*')])
binary_expression = binary_operator + integer_literal + integer_literal
expr = binary_expression
pexpr = op + expr + cp
rule = OneOrMore(pexpr)


test_strings = (
    '(+ 1 2)',
    '(- 1 2)',
    '(+ 1 2',
    '+ 1 2)',
    '+ 1 a)',
)

def parse(s):
    return rule.parseString(s)

OPERATORS = {
        '+' : lambda x, y: int(x)+int(y),
        '-' : lambda x, y: int(x)-int(y),
        '/' : lambda x, y: int(x)/int(y),
        '*' : lambda x, y: int(x)*int(y),
}
def peval(s):
    parsed = parse(s)
    op, one, two = parsed
    result = OPERATORS[op](one, two)
    return result
peval(test_strings[1])

def parse_fix(s):
    print 'parsing', s
    try:
        parsed = rule.parseString(s)
        return parsed
    except ParseException as e:
        # https://github.com/greghaskins/pyparsing/blob/ae9863266c3d75664187d82931226c50b7bba5c2/src/pyparsing.py
        expected = re.match('Expected (.*)', e.msg).group(1)
        expected = expected.strip('"')
        if expected == 'W:(0123...)':
            expected = ' 0 '
        s = s + ' '
        s = s[:e.loc] + expected + s[e.loc:]
        print 'Exception is', e, e.loc
        #print e.loc, e.line, expected
        return parse_fix(s)
for s in test_strings:
    print s, parse_fix(s)
