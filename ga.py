import collections
import random


ga_config = collections.namedtuple('Genetic_Algorigthm_Config', [
    'population_size'
])(
    population_size=10
)


class GeneticAlgorithm(object):
    def __init__(self):
        self.population_fitness = []

    def feed_fitness(self, fitness_score):
        self.population_fitness.append(fitness_score)

    def __reset_generation(self, generation):
        for single in generation:
            single.reset()

    def __swap_bias(self, a, b):
        tmp = a.nn.bias
        a.nn.bias = b.nn.bias
        b.nn.bias = tmp

    def __crossover(self, a, b):
        a = a.duplicate()
        b = b.duplicate()

        self.__swap_bias(a, b)
        return a, b

    def get_the_next_generation(self, current_generation):
        next_gen = []

        sorted_cars = sorted(current_generation, key=lambda c: c.fitness, reverse=True)

        # Get the best four
        next_gen.extend(sorted_cars[:4])
        self.__reset_generation(next_gen)

        """offsprings = []

        first, second = sorted_cars[:2]
        first, second = self.__crossover(first, second)
        offsprings.append(first if random.random() > 0.5 else second)

        for i in xrange(3):
            first, second = random.choice(sorted_cars), random.choice(sorted_cars)
            first, second = self.__crossover(first, second)
            offsprings.append(first if random.random() > 0.5 else second)

        for i in xrange(2):
            offsprings.append(random.choice(sorted_cars))

        for offspring in offsprings:
            if random.random() > 0.5:
                offspring.nn.bias = offspring.nn.bias * ((1 + random.random() - 0.5) * 3 + (random.random() - 0.5))

        next_gen.extend(offsprings)"""

        return next_gen
