import numpy as np

# User modules
from .base import BiasCorrector


def _error_calculation(X, y):

    # Numpy column-wise subtraction is expressed as row-wise subtraction.
    E = (X.transpose() - y).transpose()
    return E


def _maximum_likelihood_bias(X, y):
    # Calculate errors
    errors = _error_calculation(X, y)
    # Calculate maximum likelihood means per column
    return errors.mean(axis=0)


def _maximum_likelihood_std(X, y):
    # Calculate errors
    errors = _error_calculation(X, y)
    # Calculate maximum likelihood means per column
    return errors.std(axis=0)


class SimpleBiasCorrector(BiasCorrector):

    def __init__(self, member_count, grouping=None):
        # TODO Support grouping
        super().__init__(member_count)

        # Initialize parameters
        self.intercept_per_model = np.zeros(member_count)
        self.deviation_per_model = np.zeros(member_count)

    def fit(self, X, y):
        super()._validate_data(X)
        self.intercept_per_model = _maximum_likelihood_bias(X, y)

    def predict(self, X):
        return X - self.intercept_per_model