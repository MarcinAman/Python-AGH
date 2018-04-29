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
    zipped_list = zip(get_variables(expression), values.split(''))
    expression = map(lambda x: replace_mapping(zipped_list, x), expression)


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

        while len(expression) >= 2 and expression[0] == '(' and expression[-1] == ')' and self.check_expression(
                expression):
            expression = expression[1:-1]

        if expression[0] == '~':
            return self.convert_to_onp(expression[1:]) + expression[0]

        # TODO with a for or reduce
        index = self.bal(expression, '>')

        if index >= 0:
            return self.convert_to_onp(expression[:index]) + self.convert_to_onp(expression[index + 1:]) \
                   + expression[index]

        index = self.bal(expression, '|&/')

        if index >= 0:
            return self.convert_to_onp(expression[:index]) + self.convert_to_onp(expression[index + 1:]) \
                   + expression[index]

        index = self.bal(expression, '^')

        if index >= 0:
            return self.convert_to_onp(expression[:index]) + self.convert_to_onp(expression[index + 1:]) \
                   + expression[index]

        return expression


if __name__ == '__main__':
    a = Expression('')
