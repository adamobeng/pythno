#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from pyparsing import *
import traceback
import re
import difflib
from colorama import Fore, Back, Style, init
import ast
import operator as pyoperator
import subprocess
import os.path
import sys

def cowsay(text):
    if os.path.exists('python.cow'):
        return '\n\n' + subprocess.check_output(('cowsay', '-f', os.getcwd() + '/python.cow', '"%s"' % text))
    else:
        return '\n\n' + subprocess.check_output(('cowsay', '"%s"' % text))


def Syntax():
    binary_operator = oneOf('+ - / * max min')
    define = Literal('define') 
    unary_operator = Literal('print') | Literal('cow')
    op = Suppress(Literal('('))
    cp = Suppress(Literal(')'))
    int_lit = Word(nums)
    var = Word(alphas)
    expr = Forward()
    atom = int_lit | var | Group(expr)
    expr <<  op + (unary_operator + atom | binary_operator + atom + atom | define + var + atom) + cp
    return expr

good_strings = '''(cow 1)
    (+ 1 2)
    (- 1 2)
    (- 1 (/ 1 2))
    (+ a 2)
    (print a)
    (cow a)
    (define a 2)'''.split('\n')

bad_strings = [
    '(+ 1 2',
    '(+ 1 )',
    '(+ 1n2 2)',
    '(define 2 n)',
]
test_strings = good_strings + bad_strings

def parse(s):
    return Syntax().parseString(s).asList()


global_env = {
    '+':  pyoperator.add,
    '-':  pyoperator.sub,
    '/':  pyoperator.div,
    '*':  pyoperator.mul,
    'max':  max,
    'min':  min,
    'cow': cowsay,
    'print': str,
}


def peval(s):
    parsed = parse(s)
    result = eval_(parsed)
    return result


def atomize(i):
    try:
        return float(i)
    except:
        return i

# http://norvig.com/lispy.html


def eval_(s, env=global_env):
    try:
        s = atomize(s)
        if isinstance(s, int) or isinstance(s, float):
            return s
        elif not isinstance(s, list):
            if s in env:
                return env[s]
            else:
                # Undeclared variable
                existing_variables = [k for k, v in env.iteritems() 
                        if (isinstance(v, int) or isinstance(k, float))]
                if len(existing_variables) == 0:
                    env[s] = 0
                    print Fore.RED, 'Creating new variable "%s=0"' % s, Fore.RESET
                    return 0
                else:
                    matches = difflib.get_close_matches(s, existing_variables, n=1, cutoff=0.6)
                    if len(matches) == 0:
                        env[s] = 0 
                        print Fore.RED, 'Creating new variable "%s=0"' % s, Fore.RESET
                        return 0
                    else:
                        n = matches[0]
                        print Fore.RED, 'Replacing variable "%s" with exisitng variable "%s" ' % (s, n), Fore.RESET
                        return env[n]
        elif s[0] == 'define':
            _, var, exp = s
            val = eval_(exp, env)
            env[var] = val
            return val
        else:
            proc = eval_(s[0], env)
            args = [eval_(i, env) for i in s[1:]]
            try:
                result = proc(*args)
            except ZeroDivisionError:
                print Fore.RED, 'Dividing by zero yields infinity', Fore.RESET
                return sys.maxint
            return result
    except:
        print traceback.format_exc()
        raise Exception()


def parse_fix(s, prefix=''):
    if len(prefix) > 8:
        raw_input()
    try:
        parsed = Syntax().parseString(s).asList()
        #print 'with no error!'
        return parsed
    except ParseException as e:
        print prefix + 'parsing', s,
        expected = re.match('Expected (.*)', e.msg).group(1)
        cats = '(W|Re):\((.*)\)'
        if re.match(cats, expected):
            t, chars = re.match(cats, expected).groups()
            if t=='Re':
                chars = chars.strip("'")
                if re.match('[.*]', chars):
                    chars = chars.strip("[]")
                    chars = list(chars)
                elif '|' in chars:
                    chars = chars.replace('\\\\', '')
                    chars = chars.split('|')
            #print 'chars', chars
            expected = chars[0]
            if t == 'W':
                expected = expected + ' '
        else:
            expected = expected.strip('"')
        if e.loc == 0 or e.loc == len(s):
            # Add char
            s = s[:e.loc] + expected + s[e.loc:]
        else:
            # Replace char
            s = s[:e.loc] + expected + s[min(e.loc + 1, len(s)):]
        # Also try removing char, replacing word
        #print prefix + 'Exception is', e, e.loc
        print 'to "%s"' % (Fore.CYAN + s + Fore.RESET,)
        # print e.loc, e.line, expected
        return parse_fix(s, prefix=prefix + ' ' * 4)


def repl():
    while True:
        try:
            in_ = raw_input('🐍 > ')
            if in_.strip() == '': 
                continue
            elif in_ == '%env':
                for k, v in global_env.iteritems():
                    print ' | '.join(map(str, (k.ljust(16) , str(v).ljust(32), type(v))))
                continue
            result = eval_(parse_fix(in_))
            print Fore.GREEN , result , Fore.RESET
        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    init()
    repl()

for s in good_strings:
    print s
    #p = parse_fix(s)
    p = parse(s)
    #print p
    r = eval_(p)
    print 'RESULT', Fore.GREEN , r , Fore.RESET
