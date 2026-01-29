import unittest
from script import add

class TestAddFunction(unittest.TestCase):
    def test_add_float(self):
        self.assertEqual(add(1, 2.5), 3.5)  # This should pass

if __name__ == '__main__':
    unittest.main()
