from string import ascii_lowercase
import functools


def generate_binary(n):
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
    variables = []
    for variable in expression:
        if variable in ascii_lowercase and variable not in variables:
            variables.append(variable)

    return variables


def calculate_onp(expression, values):
    zipped_list = list(zip(get_variables(expression), list(values)))
    expression = list(map(lambda x: replace_mapping(zipped_list, x), expression))

    operators = {'^': lambda x, y: bool(x) ^ bool(y), '&': lambda x, y: bool(x) and bool(y),
                 '|': lambda x, y: bool(x) or bool(y), '/': lambda x, y: not (bool(x) and bool(y)),
                 '>': lambda x, y: not bool(x) or bool(y)}

    stack = []

    while len(expression) > 0:
        if expression[0] in ['0', '1']:
            stack.append(expression[0])
        else:
            if expression[0] == '~':
                top = not bool(stack.pop())
                stack.append(top)
            else:
                e1 = int(stack.pop())
                e2 = int(stack.pop())
                stack.append(operators[expression[0]](e1, e2))

        del expression[0]

    return stack[0]


def is_associative(tkn, associativity_type):
    if tkn == '>' and associativity_type == 'r':  # because only in case of > it matters.
        return False
    return True


class Expression:
    def __init__(self, expression):
        self.correctSigns = '~^&|/>()TF' + ascii_lowercase
        self.expression = expression.replace(' ', '')
        self.operators = {'~': (4, 1), '^': (3, 2), '&': (2, 2), '|': (2, 2), '/': (2, 2),
                          '>': (1, 2)}  # <operator> -> (priority,arguments_number)

    def check_if_brackets_are_correct(self, expression=''):
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
        if not expression:
            expression = self.expression

        return self.check_if_signs_are_correct(expression) and self.check_if_brackets_are_correct(expression)

    def bal(self, w, op):
        line = 0
        for i in range(len(w) - 1, 0, -1):
            if w[i] == ")": line -= 1
            if w[i] == "(": line += 1
            if w[i] in op and line == 0: return i
        return -1

    def convert_to_onp(self, expression=''):
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


if __name__ == '__main__':
    print(bool('1'))
    print(bool('0'))
    print(bool(1) and bool(0))
