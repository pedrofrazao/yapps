import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import unittest
from ppSlib.genetic import Alleles, Chromosome

# filepath: /home/pedro/develop/gui_tests/ppSlib/test_genetic.py


class TestAlleles(unittest.TestCase):
    def setUp(self):
        self.valid_values = [
            ("color", ["red", "green", "blue"], "Color of the object"),
            ("size", ["small", "medium", "large"], "Size of the object")
        ]
        self.alleles = Alleles(self.valid_values)

    def test_random_value_for_valid(self):
        value = self.alleles.random_value_for("color")
        self.assertIn(value, ["red", "green", "blue"])

    def test_random_value_for_invalid(self):
        with self.assertRaises(ValueError):
            self.alleles.random_value_for("invalid")

class TestChromosome(unittest.TestCase):
    def setUp(self):
        self.valid_values = [
            ("color", ["red", "green", "blue"], "Color of the object"),
            ("size", ["small", "medium", "large"], "Size of the object"),
            ("sex", ["female", "male"], "Sex of the object")
        ]
        self.alleles = Alleles(self.valid_values)
        self.chromosome = Chromosome( self.alleles, {"color": "red", "size": "small", "sex": "male"} )

    def test_init(self):
        self.assertEqual(len(self.chromosome.genes), 3)
        self.assertIn(self.chromosome.genes["color"], ["red", "green", "blue"])
        self.assertIn(self.chromosome.genes["size"], ["small", "medium", "large"])
        self.assertIn(self.chromosome.genes["sex"], ["female","male"])

    def test_str(self):
        chromosome_str = str(self.chromosome)
        self.assertIn("color", chromosome_str)
        self.assertIn("size", chromosome_str)
        self.assertIn("sex", chromosome_str)

    def test_crossover(self):
        other_chromosome = Chromosome( self.alleles, {"color": "red", "size": "small", "sex": "female"} )
        new_chromosome = self.chromosome.crossover(other_chromosome)
        self.assertEqual(len(new_chromosome.genes), 3)
        self.assertIn(new_chromosome.genes["color"], ["red"])
        self.assertIn(new_chromosome.genes["size"], ["small"])
        self.assertIn(new_chromosome.genes['sex'], ["female","male"])

    def test_mutation(self):
        original_genes = self.chromosome.genes.copy()
        mutated_chromosome = self.chromosome.mutation(rate=1.0)
        self.assertNotEqual(mutated_chromosome.genes, original_genes)

if __name__ == "__main__":
    unittest.main()