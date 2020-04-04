import pygame
import random
import math

import car
import ga
from config import config, ga_config


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
    def __init__(self, next_gen):
        pygame.display.set_caption("Car Game")

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(
            [config.screen_x, config.screen_y], pygame.HWSURFACE, 32)

        self.ga = ga.GeneticAlgorithm()
        if next_gen is None:
            self.cars = [car.Car() for i in xrange(ga_config.population_size)]
        else:
            self.cars = next_gen

        self.running = True

        self.obstacles = []
        self.rays = []
        self.borders = [
            pygame.Rect((config.screen_x / 5, 0), (1, config.screen_y)),
            pygame.Rect((config.screen_x - config.screen_x / 5, 0), (1, config.screen_y))
        ]

    def __how_many_cars_alive(self):
        alive = 0
        for car_obj in self.cars:
            if car_obj.alive:
                alive += 1

        return alive

    def __create_obstacles(self):
        current_obstacles = len(self.obstacles)
        if current_obstacles > 0:
            if self.obstacles[-1].top < config.screen_y / config.number_of_obstacles:
                return

        if current_obstacles != config.number_of_obstacles:
            distance_between_borders = config.screen_x - ((config.screen_x / 5) * 2)
            obs_len = random.randint(config.min_obstacle_len, distance_between_borders - 2 - config.car_size * 2)

            obs_x = random.choice([config.screen_x / 5, (config.screen_x - (config.screen_x / 5)) - obs_len])

            self.obstacles.append(pygame.Rect((obs_x, -config.obstacle_width), (obs_len, config.obstacle_width)))

    def __handle_pygame_events(self):
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

    def run(self):
        while self.running:
            self.time = self.clock.tick(config.fps)

            alive_cars = [car_obj for car_obj in self.cars if car_obj.alive]
            if len(alive_cars) == 0:
                break

            for car_obj in alive_cars:
                car_obj.move_backward(config.camera_speed)

                self.__calc_rays(car_obj)
                self.__validate_car_in_borders(car_obj)
                self.__handle_pygame_events()

                if self.__can_move(car_obj):
                    if config.player == 0:
                        distances = [ray.distance for ray in car_obj.rays]
                        left, right, up, down = car_obj.nn.forward(distances)

                        if up > 0.5:
                            car_obj.move_forward()

                        if down > 0.5:
                            car_obj.move_backward(config.player_movement_speed)

                        if right > 0.5:
                            car_obj.move_right()

                        if left > 0.5:
                            car_obj.move_left()
                    else:
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_LEFT]:
                            car_obj.move_left()
                        elif keys[pygame.K_RIGHT]:
                            car_obj.move_right()

                        if keys[pygame.K_DOWN]:
                            car_obj.move_backward()
                        elif keys[pygame.K_UP]:
                            car_obj.move_forward()
                else:
                    car_obj.kill()

            self.__update_obstacles()
            self.__create_obstacles()

            self.draw()

    def draw(self):
        self.screen.fill(config.bg_color)

        for car_obj in self.cars:
            if car_obj.alive:
                pygame.draw.rect(self.screen, car_obj.color, car_obj.rect)

                if config.draw_rays:
                    self.__draw_rays(car_obj)

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
        next_gen = genetic_algo.get_the_next_generation(game.cars)


if __name__ == '__main__':
    main()
