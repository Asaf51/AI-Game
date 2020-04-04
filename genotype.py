import abc

import nn


class Genotype(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, neural_network=None):
        self.fitness = 0
        self.alive = True

        if neural_network is not None:
            self.nn = neural_network
        else:
            self.nn = nn.NeuralNetwork()

    def kill(self):
        self.alive = False

    @abc.abstractmethod
    def evaluate(self):
        """
        Evaluate fitness for the genotype
        """
        pass

    @abc.abstractmethod
    def duplicate(self):
        """
        Duplicate the genotype in order to make a new on
        """
        pass

    def reset(self):
        self.fitness = 0
        self.alive = True
