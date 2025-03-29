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
        c = 0
        for i in range(100):
            mutated_chromosome = self.chromosome.mutation(rate=1.0)
            if( mutated_chromosome.genes == original_genes ):
                c += 1
            self.assertLessEqual(c, 25, "Too many 'non' mutations")

class TestChromosomeNum(unittest.TestCase):
    def setUp(self):
        self.valid_values = [
            # action selection genes
            ('rest', [0, 5, 10], "incremental utility for rest"),
            # action params genes
            ("change_dir", [5, 25, 50, 75 ,95], "prob in % to change direction"),
        ]
        self.alleles = Alleles(self.valid_values)
        self.chromosome = Chromosome( self.alleles, {"rest": 0, "change_dir": 50} )

    def test_getvalues(self):
        self.assertEqual(self.chromosome.gene_value("rest"), 0)
        self.assertEqual(self.chromosome.gene_value("change_dir"), 50)


if __name__ == "__main__":
    unittest.main()