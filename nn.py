import numpy


class NeuralNetwork(object):
    def __init__(self):
        # 40 inputs, 1 input for each ray
        self.input_layer_size = 40

        # Sounds good, it is multiplied by 2 because we have a second
        # hidden layer - the softmax layer
        self.hidden_layer_size = 16
        self.ouput_layer_size = 4

        self.input_to_hidden_weights = numpy.random.randn(
            self.input_layer_size, self.hidden_layer_size)

        self.hidden_to_output_weights = numpy.random.randn(
            self.hidden_layer_size, self.ouput_layer_size)

        # self.bias = numpy.random.rand(1)[0]

    def forward(self, inputs):
        z1 = numpy.dot(inputs, self.input_to_hidden_weights)
        a1 = self.sigmoid(z1)

        z2 = numpy.dot(a1, self.hidden_to_output_weights)
        a2 = self.sigmoid(z2)

        return a2

    def sigmoid(self, input):
        return 1 / (1 + numpy.exp(-input))
