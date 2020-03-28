import collections


ga_config = collections.namedtuple('Genetic_Algorigthm_Config', [
    'population_size'
])(
    population_size=200
)


class GeneticAlgorithm(object):
    def __init__(self):
        self.population_fitness = []

    def feed_fitness(self, fitness_score):
        self.population_fitness.append(fitness_score)
