## genetic package

from random import randint, choice

class Alleles:
    ## class with the list of possible alleles and their values

    ##
    ## init arguments
    ## values with a list of tuples with: (name, value, description)
    ##
    def __init__(self, values):
        self.aformat = None
        if not isinstance(values, list):
            raise ValueError("Values must be a list of tuples")
        for v in values:
            if not isinstance(v, tuple) or len(v) != 3:
                raise ValueError("Each value must be a tuple with three elements: (name, values list, description)")
            if isinstance(v[0], str) and isinstance(v[1], dict) and isinstance(v[2], str):
                if self.aformat is None:
                    self.aformat = 'dict'
                    continue
                if self.aformat == 'dict':
                    continue
                else:
                    raise ValueError("All values must be of the same type")
            if isinstance(v[0], str) and isinstance(v[1], list) and isinstance(v[2], str):
                if self.aformat is None:
                    self.aformat = 'list'
                    continue
                if self.aformat == 'list':
                    continue
                else:
                    raise ValueError("All values must be of the same type")
            else:
                raise ValueError("Tuple elements must be (str, list, str)")
        
        self.alleles = {}
        if self.aformat == 'list':
            for v in values:
                self.alleles[v[0]] = { 'name': v[0], 'value': v[1], 'description': v[2] }
        elif self.aformat == 'dict':
            for v in values:
                self.alleles[v[0]] = { 'name': v[0], 'value': list(v[1].keys()), 'description': v[2] }
                self.alleles[v[0]]['phenotype'] = v[1]
        else:
            raise ValueError("Alleles format not recognized")


    def random_value_for(self, name):
        if name not in self.alleles:
            raise ValueError(f"Allele {name} not found")
        return choice( self.alleles[name]['value'] )

    def _valid_names(self, name):
        return name in self.alleles.keys()

    def _valid_value(self, name, value):
        return value in self.alleles[name]['value']

    def __iter__(self):
        return iter(self.alleles.items())
    
    def __len__(self):
        return len(self.alleles)

class Chromosome:
    def __init__(self, alleles, values=None, mutation_rate=0.001):
        if isinstance(alleles, Alleles):
            self.alleles = alleles
        elif isinstance(alleles, list):
            self.alleles = Alleles(alleles)
        else:
            raise ValueError("Alleles must be a list or an Alleles instance")

        self.genes = {}
        if values:
            for n,v in values.items():
                if not self.alleles._valid_names(n):
                    raise ValueError(f"Allele {n} not found")
                if not self.alleles._valid_value(n, v):
                    raise ValueError(f"Value {v} not valid for allele {n}")
                self.genes[n] = v
        else:
            for a in self.alleles:
                genename = a[0]
                self.genes[genename] = self.alleles.random_value_for(genename)

    def __str__(self):
        return ' | '.join(f"{name}: {value}" for name, value in self.genes.items())

    def gene_value(self, name):
        return self.genes[name]

    def crossover(self, other):
        new_genes = {}
        for a in self.genes.keys():
            new_genes[a] = self.gene_value(a) if randint(0,1) == 0 else other.gene_value(a)
        return Chromosome(self.alleles, new_genes)
    
    def mutation(self, rate=None):
        if rate is None:
            rate = self.mutation_rate
        for a in self.genes.keys():
            if randint(0, 1) < rate:
                self.genes[a] = self.alleles.random_value_for(a)
        return self
    
    def phenotype(self, d=None):
        if d is None:
            d = {}
        
        for a in self.genes.keys():
            d[a] = self.genes[a]
        return d
