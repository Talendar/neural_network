"""
    By Talendar (Gabriel Nogueira)
"""

import numpy as np
import random
import time
#from IPython.display import clear_output  # required to clean the output when using notebooks


class NeuralNetwork:
    """
    """

    def __init__(self, layers_size=None, cost_type="mse", layers_activation="sigmoid"):
        """
        Constructor
        :param layers_size: list containing the sizes of the layers. The layers activation functions will be the default one.
        """
        self.cost_type = cost_type
        self.layers = []

        if layers_size is not None:
            for s in layers_size:
                input_count = self.layers[-1].size if len(self.layers) > 0 else 0
                self.layers.append(NeuralLayer(s, input_count, layers_activation))

    def add_layer(self, size, activation="sigmoid"):
        """
        :param size:
        :param activation:
        :return:
        """
        try:
            for s in size:
                input_count = self.layers[-1].size if len(self.layers) > 0 else 0
                self.layers.append(NeuralLayer(s, input_count, activation))
        except TypeError:
            input_count = self.layers[-1].size if len(self.layers) > 0 else 0
            self.layers.append(NeuralLayer(size, input_count, activation))

    def predict(self, x):
        """
        Feedforward.
        :param x: column vector containing the features of the sample. If an out of shape numpy array is fed, this function
        won't work properly due to errors in matrix multiplications.
        :return:
        """
        a = self.colvector(x)
        for l in self.layers[1:]:
            w, b = l.weights, l.bias
            a = l.activate(np.dot(w, a) + b)

        return a

    def costfunc_unit(self, h, y, derivative=False):

        """
        :param x:
        :param y:
        :param derivative:
        :return:
        """
        if self.cost_type.lower() == "mse":
            if not derivative:
                return ((h - y) ** 2) / 2
            else:
                return h - y

        raise NameError("Cost function of the type \"%s\" is not defined!" % str(self.cost_type))

    def costfunc(self, data):
        """
        :param training_set:
        :param labels:
        :return:
        """
        p_cols = 1
        try:
            p_cols = len(data[0][0])
        except TypeError:
            pass

        l_cols = 1
        try:
            l_cols = len(data[0][1])
        except TypeError:
            pass

        m = len(data)
        predictions = np.zeros((m, p_cols))
        labels = np.zeros((m, l_cols))

        for i in range(m):
            h, y = data[i]
            predictions[i] = h.transpose()
            labels[i] = y.transpose()

        if self.cost_type.lower() == "mse":
            loss = np.sum((predictions - labels) ** 2) / (2 * m)
            return loss

        raise NameError("Cost function of the type \"%s\" is not defined!" % str(self.cost_type))

        # non-vectorized general implementation
        """total = 0
        for x, y in zip(training_set, labels):
            x, y = self.colvector(x), self.colvector(y)
            total += sum(self.costfunc_unit(self.predict(x), y))
        return total / len(training_set)"""

    def colvector(self, v):
        """
        Turn a numpy array into a column vector.
        :param v:
        :return:
        """
        try:
            v.shape = (len(v), 1)
        except Exception:
            pass

        return v

    def generate_mini_batches(self, training_data, labels, mini_batch_size):
        """
        :param training_data:
        :param mini_batch_size_pc:
        :return:
        """
        m = len(training_data)
        indexes = [n for n in range(m)]
        random.shuffle(indexes)

        mini_batches_x = [training_data[indexes[k:(k + mini_batch_size)]] for k in range(0, m, mini_batch_size)]
        mini_batches_y = [labels[indexes[k:(k + mini_batch_size)]] for k in range(0, m, mini_batch_size)]

        return mini_batches_x, mini_batches_y

    def backpropagation(self, x, y):
        """
        :param x:
        :param y:
        :return: a tuple containing, respectively: the gradient of the cost function with respect to the weights; the
        gradient of the cost function with respect to the bias; the prediction (activation result of the output layer)
        of the model for the given sample.
        """
        grad_w = [np.zeros(l.weights.shape) for l in self.layers]
        grad_b = [np.zeros(l.bias.shape) for l in self.layers]

        # FORWARD PASS
        activations = [self.colvector(x)]
        zs = []  # note that the input layer is not considered! So this list will have a size num_layers - 1

        for l in self.layers[1:]:  # excluding the input layer from the iteration
            w, b = l.weights, l.bias
            a = self.colvector(activations[-1])
            z = np.dot(w, a) + b

            zs.append(z)
            activations.append(l.activate(z))

        # BACKWARD PASS
        delta = self.costfunc_unit(activations[-1], y, derivative=True) * \
                self.layers[-1].activate(zs[-1],
                                         derivative=True)  # initial delta is delta_L (delta for the output layer)

        # gradients with respect to the output layer
        grad_b[-1] = delta
        grad_w[-1] = np.dot(delta, activations[-2].transpose())

        # gradients with respect to the hidden layers
        for l in range((len(self.layers) - 2), 0, -1):
            w_p1, delta_lp1 = self.layers[l + 1].weights, delta
            a_der = self.layers[l].activate(zs[l - 1], derivative=True)

            delta = np.dot(w_p1.transpose(), delta) * a_der
            grad_b[l] = delta
            grad_w[l] = np.dot(delta, activations[l - 1].transpose())

        return grad_w, grad_b, activations[-1]

    def numerical_derivative(self):
        """
        :return:
        """
        pass

    def regularization_term(self, m, method, factor, derivative=False, w=None):
        """

        """
        if method.lower() == "l2":
            if derivative:
                return w * factor / m
            else:
                w_sum = 0
                for l in self.layers:
                    w_sum += np.sum(np.square(l.weights))

                return w_sum * factor / (2 * m)

        raise NameError("Regularization method of the type \"%s\" is not defined!" % str(method))

    def sgd(self, training_data, labels, epochs, learning_rate, mini_batch_size,
            reg_method=None, reg_factor=0, verbose=True):
        """
        Fit the network's parameters to the training data using Stochastic Gradient Descent.

        :param training_data: numpy ndarray containing, in each row, all the samples of the training set (each row is a
        vector of the features representing one of the samples).
        :param labels: column vector, in the form of a numpy array of the appropriate shape, containing the labels with
        respect to the training set samples.
        :param epochs: number of iterations to be ran by the algorithm.
        :param mini_batch_size: size of the mini batches of samples to be used in each iteration.
        :return:
        """
        starting_time = time.time()
        for e in range(epochs):
            mini_batches = self.generate_mini_batches(training_data, labels, mini_batch_size)
            predictions = []

            for mini_batch_x, mini_batch_y in zip(mini_batches[0], mini_batches[1]):

                # gradient of the cost function (considering the current batch) with respect to the weights and bias
                grad_w = [np.zeros(l.weights.shape) for l in self.layers]
                grad_b = [np.zeros(l.bias.shape) for l in self.layers]
                for x, y in zip(mini_batch_x, mini_batch_y):
                    x, y = self.colvector(x), self.colvector(y)
                    grad_w_variation, grad_b_variation, h = self.backpropagation(x, y)
                    predictions.append((h, y))

                    grad_w = [cur + var for cur, var in zip(grad_w, grad_w_variation)]
                    grad_b = [cur + var for cur, var in zip(grad_b, grad_b_variation)]

                    # updating weights and bias
                m = len(mini_batch_y)
                for i in range(1, len(self.layers)):
                    l = self.layers[i]
                    gw, gb = grad_w[i] / m, grad_b[i] / m

                    l.bias -= (learning_rate * gb)
                    reg_term = 0 if reg_method is None else self.regularization_term(m, reg_method, reg_factor,
                                                                                     derivative=True, w=l.weights)
                    l.weights -= learning_rate * (gw + reg_term)

            # print status
            if verbose:
                pc = (e + 1) / epochs
                bar = "|" + "#" * int(70 * pc) + "_" * int(70 * (1 - pc)) + "|"

                elapsed_time = time.time() - starting_time
                remaining_time = elapsed_time * (epochs - e + 1) / (e + 1)

                m, s = divmod(remaining_time, 60)
                h, m = divmod(m, 60)

                cost = self.costfunc(predictions)
                # cost_reg_term = 0 if reg_method is None else self.regularization_term(m, reg_method, reg_factor)
                # cost = cost0 + cost_reg_term

                print("\n"*50)
                #clear_output(wait=True)  # notebook
                print("Epoch: %d/%d  %s  ETA: %02dh %02dmin %02ds"
                      "\nTotal loss/cost: %.6f"
                      % ((e + 1), epochs, bar, h, m, s, cost))

    def save_params(self, file_name="./data/params.txt"):
        """
        :param file_name:
        :return:
        """
        file = open(file_name, "w")

        for i in range(1, len(self.layers)):
            l = self.layers[i]
            for W in l.weights:
                for w in W:
                    to_write = str(w).replace("[", "").replace("]", "")
                    file.write(to_write + " ")
                file.write("\n")

            for b in l.bias:
                to_write = str(b).replace("[", "").replace("]", "")
                file.write(to_write + " ")
            file.write("\n")

        file.close()


    def load_params(self, file_name="./data/params.txt"):
        """
        :param file_name:
        :return:
        """
        file = open(file_name, "r")
        for l in self.layers[1:]:

            for i in range(len(l.weights)):
                raw = file.readline().split()
                for j in range(len(l.weights[i])):
                    l.weights[i][j] = float(raw[j])

            raw = file.readline().split()
            for i in range(len(l.bias)):
                l.bias[i] = float(raw[i])
        file.close()


class NeuralLayer:
    """
    """

    def __init__(self, size, input_count, activation="sigmoid"):
        self.size = size
        self.input_count = input_count
        self.activation = activation

        self.weights = np.random.uniform(low=-1, high=1, size=(size, input_count))
        self.bias = np.random.uniform(low=-1, high=1, size=(size, 1))

    def activate(self, z, derivative=False):
        """
        :param z:
        :return:
        """
        if self.activation.lower() == "sigmoid":
            return 1 / (1 + np.exp(-z)) if not derivative else (self.activate(z) * (1 - self.activate(z)))
        if self.activation.lower() == "relu":
            return np.maximum(z, 0) if not derivative else np.ceil(np.clip(z, 0, 1))
        if self.activation.lower() == "linear":
            return z if not derivative else 1

        raise NameError("Activation function of the type \"%s\" is not defined!" % str(self.activation))
