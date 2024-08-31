# to run use "python -m unittest test_padding.py"
import unittest
from element import Padding, Margin  # replace 'your_module' with the actual module name


class TestMarghin(unittest.TestCase):
    def test_initial_values(self):
        margin = Margin()
        self.assertEqual(margin.top, 0)
        self.assertEqual(margin.bottom, 0)
        self.assertEqual(margin.left, 0)
        self.assertEqual(margin.right, 0)

    def test_individual_setters(self):
        margin = Margin()
        margin.top = 10
        margin.bottom = 20
        margin.left = 15
        margin.right = 25
        self.assertEqual(margin.top, 10)
        self.assertEqual(margin.bottom, 20)
        self.assertEqual(margin.left, 15)
        self.assertEqual(margin.right, 25)

    def test_composite_setters(self):
        margin = Margin()
        margin.x = 30
        self.assertEqual(margin.left, 30)
        self.assertEqual(margin.right, 30)
        self.assertEqual(margin.x, 60)

        margin.y = 40
        self.assertEqual(margin.top, 40)
        self.assertEqual(margin.bottom, 40)
        self.assertEqual(margin.y, 80)
class TestPadding(unittest.TestCase):
    def test_initial_values(self):
        padding = Padding()
        self.assertEqual(padding.top, 0)
        self.assertEqual(padding.bottom, 0)
        self.assertEqual(padding.left, 0)
        self.assertEqual(padding.right, 0)

    def test_individual_setters(self):
        padding = Padding()
        padding.top = 10
        padding.bottom = 20
        padding.left = 15
        padding.right = 25
        self.assertEqual(padding.top, 10)
        self.assertEqual(padding.bottom, 20)
        self.assertEqual(padding.left, 15)
        self.assertEqual(padding.right, 25)

    def test_composite_setters(self):
        padding = Padding()
        padding.x = 30
        self.assertEqual(padding.left, 30)
        self.assertEqual(padding.right, 30)
        self.assertEqual(padding.x, 60)

        padding.y = 40
        self.assertEqual(padding.top, 40)
        self.assertEqual(padding.bottom, 40)
        self.assertEqual(padding.y, 80)

if __name__ == '__main__':
    unittest.main()

