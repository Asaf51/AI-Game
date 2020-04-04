import collections

config = collections.namedtuple('Game_Configuration', [
    'screen_x',
    'screen_y',
    'car_size',
    'car_color',
    'bg_color',
    'camera_speed',
    'fps',
    'player_movement_speed',
    'bg_objects_color',
    'number_of_obstacles',
    'min_obstacle_len',
    'obstacle_width',
    'obstacle_color',
    'field_of_view',
    'number_of_rays',
    'ray_color',
    'player',  # 0 - NN, 1 - Real player
    'draw_rays'
])(
    screen_x=500,
    screen_y=500,
    car_size=25,
    car_color=(255, 255, 255),
    bg_color=(0, 0, 0),
    camera_speed=2,
    fps=120,
    player_movement_speed=2,
    bg_objects_color=(255, 0, 0),
    number_of_obstacles=4,
    min_obstacle_len=30,
    obstacle_width=1,
    obstacle_color=(0, 0, 255),
    field_of_view=120,
    number_of_rays=40,
    ray_color=(255, 255, 0),
    player=0,
    draw_rays=True
)

ga_config = collections.namedtuple('Genetic_Algorithm_Config', [
    'population_size',
    'crossover_swap_probability',
    'mutation_probability',
    'mutation_amout',
    'precent_of_mutations',
    'selection_amount'
])(
    population_size=15,
    crossover_swap_probability=0.6,
    mutation_probability=0.3,
    mutation_amout=2,
    precent_of_mutations=1,
    selection_amount=4
)

nn_config = collections.namedtuple('Neural_Network_Config', [
    'input_layer_size',
    'hidden_layer_size',
    'output_layer_size',
])(
    input_layer_size=config.number_of_rays,
    hidden_layer_size=16,
    output_layer_size=4,
)
