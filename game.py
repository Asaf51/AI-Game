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
    fps=60,
    player_movement_speed=3,
    bg_objects_color=(255, 0, 0),
    margin_between_bg_objects=10,
    bg_object_size=14,
    number_of_obstacles=6,
    min_obstacle_len=30,
    obstacle_width=1,
    obstacle_color=(0, 0, 255),
    field_of_view=120,
    number_of_rays=40,
    ray_color=(255, 255, 0),
    player=1
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


class CarGame(object):
    def __init__(self):
        pygame.display.set_caption("Car Game")

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(
            [config.screen_x, config.screen_y], pygame.HWSURFACE, 32)

        self.main_car = pygame.Rect((
            (config.screen_x - config.car_size) / 2,
            (config.screen_y - config.car_size) / 2),
            (config.car_size, config.car_size)
        )

        self.running = True
        self.right_background_objects = []
        self.left_background_objects = []

        self.obstacles = []
        self.rays = []
        self.borders = [
            pygame.Rect((config.screen_x / 5, 0), (1, config.screen_y)),
            pygame.Rect((config.screen_x - config.screen_x / 5, 0), (1, config.screen_y))
        ]
        self.__create_background_objects()

        self.nn_player = nn.NeuralNetwork()
        self.ga = ga.GeneticAlgorithm()

    def __create_background_objects(self):
        objects_per_line = config.screen_y / (
            config.bg_object_size + config.margin_between_bg_objects)

        for i in xrange(objects_per_line):
            self.left_background_objects.append(
                pygame.Rect(
                    (config.screen_x / 5, i * (
                        config.margin_between_bg_objects + config.bg_object_size)), (
                        config.bg_object_size, config.bg_object_size)))

            left_x = config.screen_x - (config.screen_x / 5)
            self.right_background_objects.append(
                pygame.Rect(
                    (left_x, i * (
                        config.margin_between_bg_objects + config.bg_object_size)), (
                        config.bg_object_size, config.bg_object_size)))

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

    def __validate_car_in_borders(self):
        if self.main_car.bottom > config.screen_y:
            self.running = False

    def __get_the_upper_bg_object(self):
        upper_left_bg_object = self.left_background_objects[0]
        upper_right_bg_object = self.right_background_objects[0]

        for bg_idx, bg_object in enumerate(self.left_background_objects):
            if bg_object.top < upper_left_bg_object.top:
                upper_left_bg_object = bg_object
                upper_right_bg_object = self.right_background_objects[bg_idx]

        return upper_left_bg_object, upper_right_bg_object

    def __update_bg(self):
        # should we add new bg object?
        left_upper, right_upper = self.__get_the_upper_bg_object()
        if left_upper.top >= config.margin_between_bg_objects:
            self.left_background_objects.append(
                pygame.Rect((
                    config.screen_x / 5,
                    -config.margin_between_bg_objects - config.bg_object_size / 2), (
                    config.bg_object_size, config.bg_object_size)))

            self.right_background_objects.append(
                pygame.Rect((
                    config.screen_x - (config.screen_x / 5),
                    -config.margin_between_bg_objects - config.bg_object_size / 2), (
                    config.bg_object_size, config.bg_object_size)))

        for bg_idx, bg_object in enumerate(self.left_background_objects):
            self.left_background_objects[bg_idx] = bg_object.move(0, config.camera_speed)
            self.right_background_objects[bg_idx] = self.right_background_objects[bg_idx].move(
                0, config.camera_speed)

            # If the object is outside the screen, destory it
            if self.left_background_objects[bg_idx].top > config.screen_y:
                self.left_background_objects.pop(bg_idx)
                self.right_background_objects.pop(bg_idx)

    def __update_obstacles(self):
        for obs_idx, obs in enumerate(self.obstacles):
            self.obstacles[obs_idx] = obs.move(0, config.camera_speed)

            if self.obstacles[obs_idx].top > config.screen_y:
                self.obstacles.pop(obs_idx)

    def __draw_bg(self):
        for bg_object in self.left_background_objects:
            pygame.draw.rect(self.screen, config.bg_objects_color, bg_object)

        for bg_object in self.right_background_objects:
            pygame.draw.rect(self.screen, config.bg_objects_color, bg_object)

    def __can_move(self):
        """for bg_object in self.right_background_objects + self.left_background_objects:
            if self.main_car.colliderect(bg_object):
                return False"""

        for border in self.borders:
            if self.main_car.colliderect(border):
                return False

        for obs in self.obstacles:
            if self.main_car.colliderect(obs):
                return False

        return True

    def __draw_obstacles(self):
        for obs in self.obstacles:
            pygame.draw.rect(self.screen, config.obstacle_color, obs)

        return True

    def __get_distances(self):
        to_bottom = config.screen_y - self.main_car.bottom
        to_up = self.main_car.top

        return to_bottom, to_up

    def __calc_rays(self):
        self.rays = []
        for angle in range(180 - config.field_of_view / 2,
                           180 + config.field_of_view / 2,
                           config.field_of_view / config.number_of_rays):
            ray = Ray(
                self.main_car.left + config.car_size / 2,
                self.main_car.top, angle)

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

            self.rays.append(ray)

    def __draw_rays(self):
        for ray in self.rays:
            pygame.draw.line(
                self.screen, config.ray_color,
                (ray.start_pos_x, ray.start_pos_y), (ray.end_pos_x, ray.end_pos_y), 1)

    def __draw_borders(self):
        for border in self.borders:
            pygame.draw.rect(self.screen, config.bg_objects_color, border)

    def __move_main_car_forward(self):
        self.main_car = self.main_car.move(0, -config.player_movement_speed)

    def __move_main_car_backward(self):
        self.main_car = self.main_car.move(0, config.player_movement_speed)

    def __move_main_car_left(self):
        self.main_car = self.main_car.move(-config.player_movement_speed, 0)

    def __move_main_car_right(self):
        self.main_car = self.main_car.move(config.player_movement_speed, 0)

    def run(self):
        start_time = time.time()
        while self.running:
            self.__get_distances()
            self.time = self.clock.tick(config.fps)
            self.main_car = self.main_car.move(0, config.camera_speed)
            # self.__update_bg()
            self.__update_obstacles()
            self.__calc_rays()
            self.__create_obstacles()

            self.__validate_car_in_borders()
            self.__handle_events()

            if self.__can_move():
                if config.player == 0:
                    y_axis, x_axis = self.nn_player.forward([ray.distance for ray in self.rays])

                    if y_axis > 0.5:
                        self.__move_main_car_forward()
                    else:
                        self.__move_main_car_backward()

                    if x_axis > 0.5:
                        self.__move_main_car_right()
                    else:
                        self.__move_main_car_left()

                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    self.__move_main_car_left()
                elif keys[pygame.K_RIGHT]:
                    self.__move_main_car_right()

                if keys[pygame.K_DOWN]:
                    self.__move_main_car_backward()
                elif keys[pygame.K_UP]:
                    self.__move_main_car_forward()
            else:
                self.running = False

            self.draw()

        end_time = time.time()
        print end_time - start_time

    def draw(self):
        self.screen.fill(config.bg_color)
        pygame.draw.rect(self.screen, config.car_color, self.main_car)
        # self.__draw_bg()
        self.__draw_borders()
        self.__draw_obstacles()
        self.__draw_rays()
        pygame.display.update()


def main():
    pygame.init()
    game = CarGame()
    game.run()


if __name__ == '__main__':
    main()
