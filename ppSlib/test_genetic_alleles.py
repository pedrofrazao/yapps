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

class TestAllelesV2(unittest.TestCase):
    def setUp(self):
        self.valid_values = [
            ("see_length", { "short": 0, "median": 1, "long": 3}, "see_length"),
            ("change_direction_prob", { "none": 0, "low": 0.1, "median": 0.2, "high": 0.4 }, "change dir prob."),
        ]
        self.alleles = Alleles(self.valid_values)

    def test_valid_names(self):
        self.assertTrue(self.alleles._valid_names("change_direction_prob"))
        self.assertFalse(self.alleles._valid_names("invalid"))

    def test_valid_value(self):
        self.assertTrue(self.alleles._valid_value("see_length", "long"))
        self.assertFalse(self.alleles._valid_value("see_length", "invalid"))

if __name__ == "__main__":
    unittest.main()