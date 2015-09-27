op = Suppress(Literal('('))
cp = Suppress(Literal(')'))

integer_literal = Word(nums)
expr = Forward()
operand = Or(integer_literal, expr)
expr << op + Literal('+') + operand + operand + cp
rule = OneOrMore(expr)

binary_expression = binary_operator + Or(pexpr, integer_literal) + Or(pexpr, integer_literal)
expr = binary_expression
pexpr << op + expr + cp
rule = OneOrMore(pexpr)

