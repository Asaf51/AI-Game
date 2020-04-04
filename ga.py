import random

from config import ga_config, nn_config


class GeneticAlgorithm(object):
    def __init__(self):
        pass

    def __sort_population_by_fitness(self, generation):
        return sorted(generation, key=lambda c: c.evaluate(), reverse=True)

    def selection(self, population):
        """
        Get the `self.selection_count` best population to the next level
        """
        selection = population[:ga_config.selection_amount]
        for gen in selection:
            gen.reset()

        return selection

    def crossover(self, parent1, parent2):
        offspring1 = parent1.duplicate()
        offspring2 = parent2.duplicate()

        for i in xrange(nn_config.input_layer_size):
            for j in xrange(nn_config.hidden_layer_size):
                if random.random() < ga_config.crossover_swap_probability:
                    new_offspring1_value = parent2.nn.get_input_weight(i, j)
                    new_offspring2_value = parent1.nn.get_input_weight(i, j)
                else:
                    new_offspring1_value = parent1.nn.get_input_weight(i, j)
                    new_offspring2_value = parent2.nn.get_input_weight(i, j)

                offspring1.nn.change_input_weight(i, j, new_offspring1_value)
                offspring2.nn.change_input_weight(i, j, new_offspring2_value)

        for i in xrange(nn_config.hidden_layer_size):
            for j in xrange(nn_config.output_layer_size):
                if random.random() < ga_config.crossover_swap_probability:
                    new_offspring1_value = parent2.nn.get_hidden_weight(i, j)
                    new_offspring2_value = parent1.nn.get_hidden_weight(i, j)
                else:
                    new_offspring1_value = parent1.nn.get_hidden_weight(i, j)
                    new_offspring2_value = parent2.nn.get_hidden_weight(i, j)

                offspring1.nn.change_hidden_weight(i, j, new_offspring1_value)
                offspring2.nn.change_hidden_weight(i, j, new_offspring2_value)

        return offspring1, offspring2

    def mutate(self, gen):
        mut_amount = ga_config.mutation_amout
        for i in xrange(nn_config.input_layer_size):
            for j in xrange(nn_config.hidden_layer_size):
                if random.random() < ga_config.mutation_probability:
                    gen.nn.change_input_weight(
                        i, j, gen.nn.get_input_weight(i, j) + (random.random() * (mut_amount * 2) - mut_amount))

        for i in xrange(nn_config.hidden_layer_size):
            for j in xrange(nn_config.output_layer_size):
                if random.random() < ga_config.mutation_probability:
                    gen.nn.change_hidden_weight(
                        i, j, gen.nn.get_hidden_weight(i, j) + (random.random() * (mut_amount * 2) - mut_amount))

    def __need_new_child(self, next_gen):
        return len(next_gen) < ga_config.population_size

    def get_the_next_generation(self, current_generation):
        next_gen = []
        sorted_population = self.__sort_population_by_fitness(current_generation)

        for gen in sorted_population:
            print gen.fitness,
        print

        next_gen.extend(self.selection(sorted_population))

        while self.__need_new_child(next_gen):
            offspring1, offspring2 = self.crossover(next_gen[0], next_gen[1])
            next_gen.append(offspring1)

            if self.__need_new_child(next_gen):
                next_gen.append(offspring2)

        for gen in next_gen:
            if random.random() < ga_config.precent_of_mutations:
                self.mutate(gen)

        return next_gen
