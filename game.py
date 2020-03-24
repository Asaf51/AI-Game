import pygame
import collections
import random


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
    number_of_obstacles=5,
    min_obstacle_len=30,
    obstacle_width=20,
    obstacle_color=(0, 0, 255),
)


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
        self.__create_background_objects()

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

            print obs_x, obs_y

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
        for bg_object in self.right_background_objects + self.left_background_objects:
            if self.main_car.colliderect(bg_object):
                return False

        for obs in self.obstacles:
            if self.main_car.colliderect(obs):
                return False

        return True

    def __draw_obstacles(self):
        for obs in self.obstacles:
            pygame.draw.rect(self.screen, config.obstacle_color, obs)

        return True

    def run(self):
        while self.running:
            self.time = self.clock.tick(config.fps)
            self.main_car = self.main_car.move(0, config.camera_speed)
            self.__update_bg()
            self.__create_obstacles()

            self.__validate_car_in_borders()
            self.__handle_events()

            if self.__can_move():
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    self.main_car = self.main_car.move(-config.player_movement_speed, 0)
                elif keys[pygame.K_RIGHT]:
                    self.main_car = self.main_car.move(config.player_movement_speed, 0)

                if keys[pygame.K_DOWN]:
                    self.main_car = self.main_car.move(0, config.player_movement_speed)
                elif keys[pygame.K_UP]:
                    self.main_car = self.main_car.move(0, -config.player_movement_speed)
            else:
                self.running = False

            self.draw()

    def draw(self):
        self.screen.fill(config.bg_color)
        pygame.draw.rect(self.screen, config.car_color, self.main_car)
        self.__draw_bg()
        self.__draw_obstacles()
        pygame.display.update()


def main():
    pygame.init()
    game = CarGame()
    game.run()


if __name__ == '__main__':
    main()
