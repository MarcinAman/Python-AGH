import unittest
import RWL


class CheckingValues(unittest.TestCase):
    def test_brackets(self):
        xd = RWL.Expression('')
        self.assertEqual(xd.check_if_brackets_are_correct(), True)
        xd.expression = '()'
        self.assertEqual(xd.check_if_brackets_are_correct(), True)
        xd.expression = '(expr(exp(a)(a)))'
        self.assertEqual(xd.check_if_brackets_are_correct(), True)
        xd.expression = '(()()'
        self.assertEqual(xd.check_if_brackets_are_correct(), False)
        xd.expression = ')))((('
        self.assertEqual(xd.check_if_brackets_are_correct(), False)
        self.assertEqual(xd.check_if_brackets_are_correct('ab)|~(b&c&~'),False)

    def test_signs(self):
        xd = RWL.Expression('')
        self.assertEqual(xd.check_if_signs_are_correct(), True)
        xd.expression = '((T|F)&(a>b))'
        self.assertEqual(xd.check_if_signs_are_correct(), True)
        xd.expression = '((T|F)&(a<b))'
        self.assertEqual(xd.check_if_signs_are_correct(), False)

        # and the part when expression has correct chars but in incorrect order:

        xd.expression = 'TF'
        self.assertEqual(xd.check_if_signs_are_correct(), False)

        xd.expression = '((T|F)&(a b))'
        self.assertEqual(xd.check_if_signs_are_correct(), False)

    def test_onp(self):
        dummy_object = RWL.Expression('')
        self.assertEqual(dummy_object.convert_to_onp('~a'), 'a~')
        self.assertEqual(dummy_object.convert_to_onp('(a&b)>(c&d)'), 'ab&cd&>')
        self.assertEqual(dummy_object.convert_to_onp('(a&~b)>(c&d)'), 'ab~&cd&>')
        self.assertEqual(dummy_object.convert_to_onp('a&~(b&x)>c&d'), 'abx&~&cd&>')
        self.assertEqual(dummy_object.convert_to_onp('~(a&b)|~(b&c)'), 'ab&~bc&~|')

    def test_calculate_onp(self):
        some_object = RWL.Expression('')
        self.assertEqual(RWL.calculate_onp(some_object.convert_to_onp('a&b&c&d|e|p'), '111100'), True)
        self.assertEqual(RWL.calculate_onp(some_object.convert_to_onp('a&b&c&d|e|p'), '101100'), False)
        self.assertEqual(RWL.calculate_onp(some_object.convert_to_onp('~(a&b)|~(b&c)'), '010'), True)


if __name__ == '__main__':
    unittest.main()
