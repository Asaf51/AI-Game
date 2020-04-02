import pygame
import collections
import random
import math
import time

import nn
import ga

config = collections.namedtuple('Configuration', [
    'screen_x',
    'screen_y',
    'car_size',
    'car_color',
    'bg_color',
    'camera_speed',
    'fps',
    'player_movement_speed',
    'bg_objects_color',
    'margin_between_bg_objects',
    'bg_object_size',
    'number_of_obstacles',
    'min_obstacle_len',
    'obstacle_width',
    'obstacle_color',
    'field_of_view',
    'number_of_rays',
    'ray_color',
    'player'  # 0 - NN, 1 - Real player
])(
    screen_x=500,
    screen_y=500,
    car_size=25,
    car_color=(255, 255, 255),
    bg_color=(0, 0, 0),
    camera_speed=2,
    fps=120,
    player_movement_speed=3,
    bg_objects_color=(255, 0, 0),
    margin_between_bg_objects=10,
    bg_object_size=14,
    number_of_obstacles=2,
    min_obstacle_len=30,
    obstacle_width=1,
    obstacle_color=(0, 0, 255),
    field_of_view=360,
    number_of_rays=40,
    ray_color=(255, 255, 0),
    player=0
)


class Ray(object):
    def __init__(self, start_pos_x, start_pos_y, angle):
        self.angle = angle
        self.start_pos_x = start_pos_x
        self.start_pos_y = start_pos_y

        self.end_pos_x, self.end_pos_y = self.calc_end_pos(pygame.display.get_surface().get_width())
        self.distance = self.calc_distance((self.end_pos_x, self.end_pos_y))

    def calc_end_pos(self, length):
        y_distance = length * math.cos(math.radians(self.angle))
        x_distance = length * math.sin(math.radians(self.angle))

        return self.start_pos_x + x_distance, self.start_pos_y + y_distance

    def calc_distance(self, point):
        return math.sqrt((point[0] - self.start_pos_x) ** 2 + (point[1] - self.start_pos_y) ** 2)


class Car(object):
    def __init__(self, neural_net=None, color=None):
        self.__create_rect()
        self.fitness = 0
        self.alive = True

        if color:
            self.color = color
        else:
            self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.ray_distances = []

        if neural_net:
            self.nn = neural_net
        else:
            self.nn = nn.NeuralNetwork()
        self.fitness = 0

    def __create_rect(self):
        self.rect = pygame.Rect((
            (config.screen_x - config.car_size) / 2,
            (config.screen_y - config.car_size) / 2),
            (config.car_size, config.car_size))

    def kill(self):
        print "Moved: {}".format(self.fitness)
        self.alive = False

    def set_fitness(self, fitness):
        self.fitness = fitness

    def moved(self):
        self.fitness += config.player_movement_speed

    def duplicate(self):
        return Car(self.nn, self.color)

    def reset(self):
        self.ray_distances = []
        self.alive = True
        self.fitness = 0
        self.__create_rect()


class CarGame(object):
    def __init__(self, next_gen):
        pygame.display.set_caption("Car Game")

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(
            [config.screen_x, config.screen_y], pygame.HWSURFACE, 32)

        self.ga = ga.GeneticAlgorithm()
        if next_gen is None:
            self.main_cars = [Car() for i in xrange(ga.ga_config.population_size)]
        else:
            self.main_cars = next_gen

        self.running = True

        self.obstacles = []
        self.rays = []
        self.borders = [
            pygame.Rect((config.screen_x / 5, 0), (1, config.screen_y)),
            pygame.Rect((config.screen_x - config.screen_x / 5, 0), (1, config.screen_y))
        ]

    def __how_many_cars_alive(self):
        alive = 0
        for car in self.main_cars:
            if car.alive:
                alive += 1

        return alive

    def __create_obstacles(self):
        current_obstacles = len(self.obstacles)
        if current_obstacles > 0:
            if self.obstacles[-1].top < config.screen_y / config.number_of_obstacles:
                return

        if current_obstacles != config.number_of_obstacles:
            obs_len = random.randint(
                config.min_obstacle_len,
                (config.screen_x - config.screen_x / (5 * 2)) / 2)

            obs_x, obs_y = random.randint(
                config.screen_x / 5 + config.bg_object_size / 2 + 1,
                config.screen_x - (config.screen_x / 5 * 2) - config.bg_object_size - 1
            ), -config.obstacle_width

            self.obstacles.append(pygame.Rect((obs_x, obs_y), (obs_len, config.obstacle_width)))

    def __handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break

    def __validate_car_in_borders(self, car):
        if car.rect.bottom > config.screen_y:
            car.kill()

    def __update_obstacles(self):
        for obs_idx, obs in enumerate(self.obstacles):
            self.obstacles[obs_idx] = obs.move(0, config.camera_speed)

            if self.obstacles[obs_idx].top > config.screen_y:
                self.obstacles.pop(obs_idx)

    def __can_move(self, car):
        """for bg_object in self.right_background_objects + self.left_background_objects:
            if self.main_car.colliderect(bg_object):
                return False"""

        for border in self.borders:
            if car.rect.colliderect(border):
                return False

        for obs in self.obstacles:
            if car.rect.colliderect(obs):
                return False

        return True

    def __draw_obstacles(self):
        for obs in self.obstacles:
            pygame.draw.rect(self.screen, config.obstacle_color, obs)

        return True

    def __calc_rays(self, car):
        car.rays = []
        for angle in range(180 - config.field_of_view / 2,
                           180 + config.field_of_view / 2,
                           config.field_of_view / config.number_of_rays):
            ray = Ray(
                car.rect.left + config.car_size / 2,
                car.rect.top, angle)

            closest = config.screen_x
            # line = collections.namedtuple('Line', ['left', 'right', 'bottom'])
            # left_line = line(config.screen_x / 5, config.screen_x / 5 + 1, config.screen_y)
            for obstacle in self.obstacles + self.borders:
                x1, y1 = ray.start_pos_x, ray.start_pos_y
                x2, y2 = ray.end_pos_x, ray.end_pos_y

                x3, y3 = obstacle.left, obstacle.top
                x4, y4 = obstacle.right, obstacle.bottom

                div = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
                if div == 0:
                    continue

                t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / div
                u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / div

                if 0.0 < t and u > 0.0 and u < 1:
                    point = (int(x1 + t * (x2 - x1)), int(y1 + t * (y2 - y1)))
                    ray.distance = ray.calc_distance(point)

                    if closest > ray.distance:
                        ray.end_pos_x = point[0]
                        ray.end_pos_y = point[1]

                        closest = ray.distance

            car.rays.append(ray)

    def __draw_rays(self, car):
        for ray in car.rays:
            pygame.draw.line(
                self.screen, config.ray_color,
                (ray.start_pos_x, ray.start_pos_y), (ray.end_pos_x, ray.end_pos_y), 1)

    def __draw_borders(self):
        for border in self.borders:
            pygame.draw.rect(self.screen, config.bg_objects_color, border)

    def __move_main_car_forward(self, car):
        self.main_cars[self.main_cars.index(car)].rect = car.rect.move(
            0, -config.player_movement_speed)

        car.moved()

    def __move_main_car_backward(self, car):
        self.main_cars[self.main_cars.index(car)].rect = car.rect.move(
            0, config.player_movement_speed)

    def __move_main_car_left(self, car):
        self.main_cars[self.main_cars.index(car)].rect = car.rect.move(
            -config.player_movement_speed, 0)

    def __move_main_car_right(self, car):
        self.main_cars[self.main_cars.index(car)].rect = car.rect.move(
            config.player_movement_speed, 0)

    def run(self):
        start_time = time.time()
        while self.running:
            self.time = self.clock.tick(config.fps)

            if self.__how_many_cars_alive() == 0:
                break

            alive_cars = [car for car in self.main_cars if car.alive]
            for car in alive_cars:
                self.main_cars[self.main_cars.index(car)].rect = car.rect.move(
                    0, config.camera_speed)

                # self.__update_bg()
                self.__calc_rays(car)

                self.__validate_car_in_borders(car)
                self.__handle_events()

                if self.__can_move(car):
                    if config.player == 0:
                        distances = [ray.distance for ray in car.rays]
                        left, right, up, down = car.nn.forward(distances)

                        if up > 0.5:
                            self.__move_main_car_forward(car)

                        if down > 0.5:
                            self.__move_main_car_backward(car)

                        if right > 0.5:
                            self.__move_main_car_right(car)

                        if left > 0.5:
                            self.__move_main_car_left(car)
                    else:
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_LEFT]:
                            self.__move_main_car_left(car)
                        elif keys[pygame.K_RIGHT]:
                            self.__move_main_car_right(car)

                        if keys[pygame.K_DOWN]:
                            self.__move_main_car_backward(car)
                        elif keys[pygame.K_UP]:
                            self.__move_main_car_forward(car)
                else:
                    car.kill()

            self.__update_obstacles()
            self.__create_obstacles()

            self.draw()

        end_time = time.time()
        print end_time - start_time

    def draw(self):
        self.screen.fill(config.bg_color)

        for car in self.main_cars:
            if car.alive:
                pygame.draw.rect(self.screen, car.color, car.rect)
                self.__draw_rays(car)

        self.__draw_borders()
        self.__draw_obstacles()
        pygame.display.update()


def main():
    pygame.init()
    genetic_algo = ga.GeneticAlgorithm()

    next_gen = None
    while True:
        game = CarGame(next_gen)
        game.run()
        next_gen = genetic_algo.get_the_next_generation(game.main_cars)

        for i in xrange(6):
            next_gen.append(Car())


if __name__ == '__main__':
    main()
