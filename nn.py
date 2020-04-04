import numpy

from config import nn_config


class NeuralNetwork(object):
    def __init__(self):
        self.input_layer_size = nn_config.input_layer_size
        self.hidden_layer_size = nn_config.hidden_layer_size
        self.ouput_layer_size = nn_config.output_layer_size

        self.input_to_hidden_weights = numpy.random.randn(
            self.input_layer_size, self.hidden_layer_size)
        self.hidden_to_output_weights = numpy.random.randn(
            self.hidden_layer_size, self.ouput_layer_size)

        self.input_to_hidden_bias = numpy.random.randn(self.hidden_layer_size)
        self.hidden_to_output_bias = numpy.random.randn(self.ouput_layer_size)

    def forward(self, inputs):
        z1 = numpy.add(numpy.dot(inputs, self.input_to_hidden_weights), self.input_to_hidden_bias)
        a1 = self.sigmoid(z1)

        z2 = numpy.add(numpy.dot(a1, self.hidden_to_output_weights), self.hidden_to_output_bias)
        a2 = self.sigmoid(z2)

        return a2

    def sigmoid(self, input):
        return 1 / (1 + numpy.exp(-input))

    def change_input_weight(self, i, j, new_value):
        self.input_to_hidden_weights[i][j] = new_value

    def change_hidden_weight(self, i, j, new_value):
        self.hidden_to_output_weights[i][j] = new_value

    def get_input_weight(self, i, j):
        return self.input_to_hidden_weights[i][j]

    def get_hidden_weight(self, i, j):
        return self.hidden_to_output_weights[i][j]
