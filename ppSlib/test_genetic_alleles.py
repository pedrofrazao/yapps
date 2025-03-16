import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import unittest
from ppSlib.genetic import Alleles

class TestAlleles(unittest.TestCase):
    def setUp(self):
        self.valid_values = [
            ("color", ["red", "green", "blue"], "Color of the object"),
            ("size", ["small", "medium", "large"], "Size of the object")
        ]
        self.alleles = Alleles(self.valid_values)

    def test_init_valid(self):
        self.assertEqual(len(self.alleles.alleles), 2)
        self.assertIn("color", self.alleles.alleles)
        self.assertIn("size", self.alleles.alleles)

    def test_init_invalid_not_list(self):
        with self.assertRaises(ValueError):
            Alleles("not a list")

    def test_init_invalid_not_tuples(self):
        with self.assertRaises(ValueError):
            Alleles([("color", ["red", "green", "blue"], "Color of the object"), "invalid tuple"])

    def test_init_invalid_tuple_elements(self):
        with self.assertRaises(ValueError):
            Alleles([("color", "not a list", "Color of the object")])

    def test_random_value_for_valid(self):
        value = self.alleles.random_value_for("color")
        self.assertIn(value, ["red", "green", "blue"])

    def test_random_value_for_invalid(self):
        with self.assertRaises(ValueError):
            self.alleles.random_value_for("invalid")

if __name__ == "__main__":
    unittest.main()