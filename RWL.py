from string import ascii_lowercase
import functools
from itertools import combinations


def generate_binary(n):
    """
    Function returns generator with binary sequences of a set length

    :param n: length of a binary sequence
    :return: generator with binary sequence
    """
    if n == 0:
        yield ""
    else:
        for c in generate_binary(n - 1):
            yield "0" + c
            yield "1" + c


def find_value(zipped_list, x):
    for a, b in zipped_list:
        if a == x:
            return b
    return -1


def replace_mapping(zipped_list, x):
    if x == 'T':
        return 1
    elif x == 'F':
        return 0
    elif x in (ascii_lowercase + 'TF'):
        return find_value(zipped_list, x)
    else:
        return x


def get_variables(expression):
    """
    Functions filters the expression for variables and returns them
    As a variable we mean any lower case character

    :param expression: expression to search in
    :return: list with variables from expression
    """
    variables = []
    for variable in expression:
        if variable in ascii_lowercase and variable not in variables:
            variables.append(variable)

    return variables


def calculate_onp(expression, values):
    """
    Function calculates a value of an expression in reverse polish notation
    :param expression: Expression in RPN given as a string.
    :param values: binary sequence with values to be put in coresponding positions. Also string
    :return: Bool value of an expression
    Warning: function will only work on correct RNP expression and will not return any warnings in case of errors
    """

    zipped_list = list(zip(get_variables(expression), list(values)))
    expression = list(map(lambda x: replace_mapping(zipped_list, x), expression))

    operators = {'^': lambda x, y: bool(x) ^ bool(y), '&': lambda x, y: bool(x) and bool(y),
                 '|': lambda x, y: bool(x) or bool(y), '/': lambda x, y: not (bool(x) and bool(y)),
                 '>': lambda x, y: not bool(x) or bool(y)}

    stack = []

    while len(expression) > 0:
        if expression[0] in ['0', '1']:
            stack.append(int(expression[0]))
        else:
            if expression[0] == '~':
                top = not bool(stack.pop())
                stack.append(top)
            else:
                e1 = int(stack.pop())
                e2 = int(stack.pop())
                stack.append(operators[expression[0]](e2, e1))

        del expression[0]

    return stack[0]


def is_associative(tkn, associativity_type):
    if tkn == '>' and associativity_type == 'r':  # because only in case of > it matters.
        return False
    return True


def concat(s1, s2):
    """
    Helper function to reduce expressions
    :param s1: Sthing we can iterate over with binary sequence and '_'
    :param s2: Sthing we can iterate over with binary sequence and '_'
    :return: Merged version of input, when certain bits are different this place is being replaced by '_'
    """
    w = ""
    lz = 0
    for z1, z2 in zip(s1, s2):
        if z1 == z2:
            w += z1
        else:
            lz += 1
            w += "_"

    if lz == 1:
        return w

    return False


def reduce_(s):
    """
    Main reduce function
    :param s: Set with values
    :return: reduced set
    """
    result = set()
    b2 = False

    for e1 in s:
        b1 = False
        for e2 in s:
            v = concat(e1, e2)
            if v:
                result.add(v)
                b1 = b2 = True

        if not b1:
            result.add(e1)
    if b2:
        return reduce_(result)

    return result


def expression_to_string(s):
    """
    Helper function to change a reduced set to human-readable form
    :param s: Set with values
    :return: String made from input in pattern: (expression)|(expression)|(expression) or T (if expression is tautology)
    """
    result2 = ""
    for e1 in s:
        result = ""
        for i in range(0, len(e1)):
            if e1[i] == '_':
                continue
            if e1[i] == '0':
                result += '~'
            result += ascii_lowercase[i] + "&"

        result2 += '(' + result[:-1] + ')|'

    if result2 == '()|':
        return 'T'

    return result2[:-1]


def trim_expression(expression):
    """
    Basic expression trimming
    :param expression: takes an expression which in most cases matches a pattern: (expression) and trims brackets
    :return: expression with trimmed brackets
    """
    e = Expression('')
    while len(expression) > 2 and expression[0] == '(' and expression[-1] == ')' and e.check_expression(expression):
        expression = expression[1:-1]

    return expression


def reduce_tuple(expression):
    """
    Function reduces a tuple of string expressions
    :param expression: tuple containing expressions. We assume that they do not contain '|'
    since in this case they are a product of QuineMcCluskey algorithm
    :return: String containing reduced expression or the input one if further reduction was not successful
    """
    expression_list = list(expression)
    variables = get_variables(str.join('|', expression_list))
    binary_generator = generate_binary(len(variables))
    incorrect_binaries = []
    some_expression = Expression('')
    onp_expression = some_expression.convert_to_onp(str.join('|', expression_list))
    onp_xor = some_expression.convert_to_onp(functools.reduce(lambda x, y: x + '^' + y, variables))

    while True:
        try:
            x = binary_generator.__next__()
            if calculate_onp(onp_expression, x) != calculate_onp(onp_xor, x):
                incorrect_binaries.append(x)
        except:
            break

    if len(incorrect_binaries) > 0:
        return str.join('|', expression_list)

    return '(' + functools.reduce(lambda x, y: x + '^' + y, variables) + ')'


def reduce_xor(expression):
    """
    Specific function to reduce xor expressions. It generates combinations of k elements in len(variables)
    where k is in range from 2 to len(variables). It checks whether it is not the same as var1 xor var2 xor var3 etc
    :param expression: String expression to be reduced. We assume that it matches a pattern: (expr1)|(expr2)|(expr3) ...
    :return: reduced expression in string form or input one if further reduction was not possible
    """
    expressions_list = expression.split('|')
    n = len(expressions_list)
    for a in range(2, n + 1):
        for expr in combinations(expressions_list, a):  # i feel really bad for this
            reduced_sub_expression = reduce_tuple(expr)
            prev_expression = str.join('|', expr)
            if len(reduced_sub_expression) < len(prev_expression):
                for var in list(expr):
                    del expressions_list[expressions_list.index(var)]
                expressions_list.append(reduced_sub_expression)
                return reduce_xor(functools.reduce(lambda x, y: '|' + x + y + '|', expressions_list))

    return expression


def reduce_brackets(expression):
    """
    Function that reduces unessesary brackets. It eliminates situations where between two | there is a expression that doesnt need them
    example:
    (expr1)|(a)|(expr2) will be evaluated to: (expr1)|a|(expr2)
    :param expression: string expression in form (expr1)|(expr2)|(expr3)
    :return: reduced expression
    """
    expression_list = expression.split('|')
    if len(expression_list) == 1:
        return trim_expression(expression_list[0])

    reduced_expressions = []
    for some in expression_list:
        if len(some) <= 4:
            # we are sure that there will be 2 brackets + we want 1 variable (or variable + negation)
            reduced_expressions.append(trim_expression(some))
        else:
            reduced_expressions.append(some)

    return str.join('|', reduced_expressions)


def reduce_logical_expression(expression):
    """
    Main function that is responsible for driving program.
    It calls functions to check if expression is correct and then reduces expression
    :param expression: String expression to be reduced
    :return: reduced expression or ERROR if it is not correct
    """
    expression_object = Expression(expression)

    if not expression_object.check_expression():
        return 'ERROR'

    expression_in_general_form = expression_object.generate_general_form()
    expression_with_xor = reduce_brackets(reduce_xor(expression_in_general_form))

    if len(expression_with_xor) < len(expression):
        return expression_with_xor

    e = reduce_brackets(expression_in_general_form)

    if len(e) < len(expression):
        return e

    return reduce_brackets(expression)


class Expression:
    """
    Class designed to handle most of expression operations.
    It contains map with bindings:
    <operator> -> (priority,arguments_number)

    Also string with correct signs and expression itself
    """
    def __init__(self, expression):
        self.general_form = ''
        self.correctSigns = '~^&|/>()TF' + ascii_lowercase
        self.expression = expression.replace(' ', '')
        self.operators = {'~': (4, 1), '^': (3, 2), '&': (2, 2), '|': (2, 2), '/': (2, 2),
                          '>': (1, 2)}  # <operator> -> (priority,arguments_number)

    def check_if_brackets_are_correct(self, expression=''):
        """
        Helper function to determine whether brackets are placed correctly
        :param expression: expression in String form
        :return: Bool result of brackets checking
        """
        if not expression:
            expression = self.expression
        brackets = 0
        for a in expression:
            if a == '(':
                brackets += 1
            elif a == ')':
                brackets -= 1
                if brackets < 0:
                    return False

        if brackets == 0:
            return True
        return False

    def check_if_signs_are_correct(self, expression=''):
        """
        Simple filter function that checks if expression contains correct signs and is semantically correct
        :param expression: String expression to be checked
        :return: Bool result
        """
        if not expression:
            expression = self.expression

        if not expression:
            return True

        if [x for x in expression if x not in self.correctSigns]:
            return False

        state = True
        for single in expression:
            if state:
                if single in self.operators and self.operators[single][1] == 1 or single in ['(', ')']:  # we want ~
                    # we ignore brackets since they are already checked
                    continue
                elif single in (ascii_lowercase + 'TF'):
                    state = False
                else:
                    return False
            else:
                if single in self.operators and self.operators[single][1] == 2:  # everything else than ~
                    state = True
                elif single in ['(', ')']:
                    continue
                else:
                    return False

        return not state

    def check_expression(self, expression=''):
        """
        Higher level interface for checking expression
        It calls methods to determine whether expression is correct semantically, in terms of brackets and signs
        :param expression: String expression to check
        :return: Bool result
        """
        if not expression:
            expression = self.expression

        return self.check_if_signs_are_correct(expression) and self.check_if_brackets_are_correct(expression)

    def convert_to_onp(self, expression=''):
        """
        Function converts an infix expression to RPN
        Warning: it doesnt check whether this expression is correct
        :param expression: Infix expression
        :return: RPN expression
        """
        if not expression:
            expression = self.expression

        stack = []
        onp = []

        for tkn in expression:
            if tkn in self.operators:
                while len(stack) > 0 and stack[-1] in self.operators:
                    if (is_associative(tkn, 'l') and (self.operators[tkn][0] - self.operators[stack[-1]][0]) <= 0) \
                            or (
                            is_associative(tkn, 'r') and (self.operators[tkn][0] - self.operators[stack[-1]][0]) < 0):
                        onp.append(stack.pop())
                        continue
                    break
                stack.append(tkn)
            elif tkn == '(':
                stack.append(tkn)
            elif tkn == ')':
                while len(stack) > 0 and stack[-1] != '(':
                    onp.append(stack.pop())
                stack.pop()
            else:
                onp.append(tkn)

        while len(stack) > 0:
            onp.append(stack.pop())

        return functools.reduce(lambda x, y: x + y, onp)

    def generate_general_form(self, expression=''):
        """
        Function generates general form from infix expression
        It uses QuineMcCluskey algorithm

        Result matches a pattern: (expression1)|(expression2)|(expression3)...
        :param expression: Infix expression as a String
        :return: String infix expression evaluated using QuineMcCluskey
        """
        if not expression:
            expression = self.expression

        n = len(get_variables(expression))
        correct_binaries = []
        generator = generate_binary(n)
        current_expression = self.convert_to_onp(expression)

        while True:
            try:
                x = generator.__next__()
                if calculate_onp(current_expression, x):
                    correct_binaries.append(x)
            except:
                break

        set2 = reduce_(correct_binaries)
        self.general_form = expression_to_string(set2)

        return self.general_form


if __name__ == '__main__':
    x = None

    while not x:
        x = input('')
        if x:
            print(reduce_logical_expression(x))
        else:
            break
