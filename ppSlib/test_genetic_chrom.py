import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import unittest
from ppSlib.genetic import Alleles, Chromosome

# filepath: /home/pedro/develop/gui_tests/ppSlib/test_genetic.py
debug = lambda x: print(f">> {str(x)}") if( os.environ.get('DEBUG', False) ) else None


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

    # def test_str(self):
    #     chromosome_str = str(self.chromosome)
    #     debug( f"chrom: {str(self.chromosome)}" )
    #     self.assertIn("color", chromosome_str)
    #     self.assertIn("size", chromosome_str)
    #     self.assertIn("sex", chromosome_str)

    def test_crossover(self):
        other_chromosome = Chromosome( self.alleles, {"color": "red", "size": "small", "sex": "female"} )
        new_chromosome = self.chromosome.crossover(other_chromosome)
        debug( f"self: {str(self.chromosome)}" )
        debug( f"other: {str(other_chromosome)}" )
        debug( f"new: {str(new_chromosome)}" )

        self.assertEqual(self.alleles, new_chromosome.alleles)
        self.assertEqual(len(self.chromosome.alleles),3)
        self.assertEqual(len(new_chromosome.alleles),3)
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

class TestChromosomeRandom(unittest.TestCase):
    def setUp(self):
        self.valid_values = [
            # action selection genes
            ('rest', [0, 5, 10], "incremental utility for rest"),
            # action params genes
            ("change_dir", [5, 25, 50, 75 ,95], "prob in % to change direction"),
        ]
        self.alleles = Alleles(self.valid_values)
        self.chromosome = Chromosome( self.alleles )
        debug( f"{self._testMethodName}: {str(self.chromosome)}" )

    def test_getvalues(self):
        self.assertIn(self.chromosome.gene_value("rest"), self.valid_values[0][1])
        self.assertIn(self.chromosome.gene_value("change_dir"), self.valid_values[1][1])


class TestChromosomeOnDict(unittest.TestCase):
    def setUp(self):
        self.dict = {
            "rest": 0,
            "change_direction_prob": 5,
            "direction": 5,
            "energy": 100,
        }

        alleles=[
            ('rest', [0, 5, 10], "incremental utility for rest"),
            ("change_direction_prob", [5, 25, 50, 75 ,95], "prob in % to change direction"),
        ]
        self.alleles = alleles
        self.chromosome = Chromosome( alleles, {"rest": 0, "change_direction_prob": 50} )
        debug( f"{self._testMethodName}: {str(self.chromosome)}" )

    def test_apply_chrom_on_dict(self):
        self.chromosome.phenotype(self.dict)
        # Check if the dictionary has been updated correctly
        self.assertEqual(self.dict["rest"], 0)
        self.assertEqual(self.dict["change_direction_prob"], 50)
        self.assertEqual(self.dict["direction"], 5)
        self.assertEqual(self.dict["energy"], 100)
    
    def test_apply_chrom_without_dict(self):
        d = self.chromosome.phenotype()
        self.assertEqual(d["rest"], 0)
        self.assertEqual(d["change_direction_prob"], 50)
        self.assertNotIn("direction", d)
        self.assertNotIn("energy", d)

    def test_gen_chrom_without_values(self):
        chrom = Chromosome( self.alleles )
        debug( f"{self._testMethodName}: {str(chrom)}" )
        self.assertIn(self.chromosome.gene_value("rest"), [0, 5, 10])
        self.assertIn(self.chromosome.gene_value("change_direction_prob"), [5, 25, 50, 75 ,95])


class TestChromosomeBig(unittest.TestCase):
    def setUp(self):

        alleles=[
            # ('rest', [0, 5, 10], "incremental utility for rest"),
            # ("change_direction_prob", [5, 25, 50, 75 ,95], "prob in % to change direction"),
            ("gene1", [ i for i in range(1000) ], "gene1"),
            ("gene2", [ i for i in range(1000) ], "gene2"),
            ("gene3", [ i for i in range(1000) ], "gene3"),
            ("gene4", [ i for i in range(1000) ], "gene4"),
            ("gene5", [ i for i in range(1000) ], "gene5"),
            ("gene6", [ i for i in range(1000) ], "gene6"),
            ("gene7", [ i for i in range(1000) ], "gene7"),
            ("gene8", [ i for i in range(1000) ], "gene8"),
            ("gene9", [ i for i in range(1000) ], "gene9"),
            ("gene10", [ i for i in range(1000) ], "gene10"),
            ("gene11", [ i for i in range(1000) ], "gene11"),
            ("gene12", [ i for i in range(1000) ], "gene12"),
            ("gene13", [ i for i in range(1000) ], "gene13"),
            ("gene14", [ i for i in range(1000) ], "gene14"),
            ("gene15", [ i for i in range(1000) ], "gene15"),
            ("gene16", [ i for i in range(1000) ], "gene16"),
            ("gene17", [ i for i in range(1000) ], "gene17"),
            ("gene18", [ i for i in range(1000) ], "gene18"),
            ("gene19", [ i for i in range(1000) ], "gene19"),
            ("gene20", [ i for i in range(1000) ], "gene20"),
            ("gene21", [ i for i in range(1000) ], "gene21"),
            ("gene22", [ i for i in range(1000) ], "gene22"),
            ("gene23", [ i for i in range(1000) ], "gene23"),
            ("gene24", [ i for i in range(1000) ], "gene24"),
            ("gene25", [ i for i in range(1000) ], "gene25"),
            ("gene26", [ i for i in range(1000) ], "gene26"),
            ("gene27", [ i for i in range(1000) ], "gene27"),
            ("gene28", [ i for i in range(1000) ], "gene28"),
            ("gene29", [ i for i in range(1000) ], "gene29"),
        ]
        self.alleles = alleles

    def test_sex_cross_1(self):
        chromosome1 = Chromosome( self.alleles )
        chromosome2 = Chromosome( self.alleles )
        new_chromosome = chromosome1.sexual_reproduction(chromosome2)
        debug( f"\n>> chromosome1:       {str(chromosome1)}" )
        debug( f"chromosome2:       {str(chromosome2)}" )
        debug( f"new_chromosome:    {str(new_chromosome)}" )

        cross_counter,_ = Chromosome._approx_crossover_count(chromosome1,chromosome2,new_chromosome)
        # can be 1 or 2 because the selected chromosome can be the 2nd created (based on the chromosome2)
        self.assertIn(cross_counter, [1,2], "Invalid crossover count")
    
    def test_sex_cross_n(self):
        chromosome1 = Chromosome( self.alleles )
        chromosome2 = Chromosome( self.alleles )

        for n in range(2,5):
            new_chromosome = chromosome1.sexual_reproduction(chromosome2, num_cross_points=n )
            debug( f"\n>> chromosome1:       {str(chromosome1)}" )
            debug( f"chromosome2:       {str(chromosome2)}" )
            debug( f"new_chromosome:    {str(new_chromosome)}" )

            (cross_counter,mutation_counter) = Chromosome._approx_crossover_count(chromosome1,chromosome2,new_chromosome)
            # can be n or n+1 because the selected chromosome can be the 2nd created (based on the chromosome2)
            self.assertGreaterEqual(cross_counter, n-1, "Invalid crossover count")
            self.assertLessEqual(cross_counter, n+1, "Invalid crossover count")
            self.assertEqual(mutation_counter, 0, "Invalid mutation count")

    def test_sex_cross_1_mut_01(self):
        chromosome1 = Chromosome( self.alleles )
        chromosome2 = Chromosome( self.alleles )

        n=1
        new_chromosome = chromosome1.sexual_reproduction(chromosome2, num_cross_points=n, mutation_rate=0.1 )
        debug( f"\n>> chromosome1:       {str(chromosome1)}" )
        debug( f"chromosome2:       {str(chromosome2)}" )
        debug( f"new_chromosome:    {str(new_chromosome)}" )

        (cross_counter,mutation_counter) = Chromosome._approx_crossover_count(chromosome1,chromosome2,new_chromosome)
        # can be n or n+1 because the selected chromosome can be the 2nd created (based on the chromosome2)
        self.assertIn(cross_counter, [n,n+1], "Invalid crossover count")
        self.assertGreaterEqual(mutation_counter, 1, "Invalid mutation count")

    # def chross1(self):
    #     self.chromosome.phenotype(self.dict)
    #     # Check if the dictionary has been updated correctly
    #     self.assertEqual(self.dict["rest"], 0)
    #     self.assertEqual(self.dict["change_direction_prob"], 50)
    #     self.assertEqual(self.dict["direction"], 5)
    #     self.assertEqual(self.dict["energy"], 100)
    
    # def test_apply_chrom_without_dict(self):
    #     d = self.chromosome.phenotype()
    #     self.assertEqual(d["rest"], 0)
    #     self.assertEqual(d["change_direction_prob"], 50)
    #     self.assertNotIn("direction", d)
    #     self.assertNotIn("energy", d)

if __name__ == "__main__":
    unittest.main()