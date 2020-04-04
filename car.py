import random
import pygame
import copy

import genotype
from config import config


class Car(genotype.Genotype):
    def __init__(self, neural_network=None, color=None):
        super(Car, self).__init__(neural_network)

        if color is not None:
            self.color = color
        else:
            self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        self.rect = None
        self.rays = []
        self.__create_rect()

    def __create_rect(self):
        self.rect = pygame.Rect((
            (config.screen_x - config.car_size) / 2,
            (config.screen_y - config.car_size) / 2),
            (config.car_size, config.car_size))

    def move_forward(self):
        self.rect = self.rect.move(0, -config.player_movement_speed)
        self.fitness += config.player_movement_speed

    def move_backward(self, speed):
        self.rect = self.rect.move(0, speed)

    def move_left(self):
        self.rect = self.rect.move(-config.player_movement_speed, 0)

    def move_right(self):
        self.rect = self.rect.move(config.player_movement_speed, 0)

    def reset(self):
        super(Car, self).reset()
        self.__create_rect()
        self.rays = []

    def evaluate(self):
        return self.fitness

    def duplicate(self):
        return Car(copy.deepcopy(self.nn))
