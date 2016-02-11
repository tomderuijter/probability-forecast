
from scipy.stats import norm
import numpy as np


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


class GaussianMixtureModel:
    """"""

    def __init__(self, member_count):
        """Initialize a univariate normal Gaussian Mixture Model

        Parameters
        ----------
        member_count : integer
            Number of members to initialize the mixture with
        """
        members = [MixtureMember(norm)] * member_count

        self.members = members
        self.member_count = len(members)
        self.weights = np.ones(len(members)) / len(members)

    def fit(self, X, y):
        """

        Parameters
        ----------
        X : array_like, shape (n_samples, n_members)
            Input data, one column for each ensemble member
        y : array_like, shape (n_samples,)
            Targets for input data
            """

        assert X.shape[1] == self.member_count, "Bad number of member inputs"
        assert X.shape[0] == y.shape[0], "Input and tragets do not match."
        assert len(y.shape) == 1, "Provided y is not a vector."

        # Mean bias correction
        model_bias = _maximum_likelihood_bias(X[:, 0], y)

        # Training strategy: train on first member.
        model_std = _maximum_likelihood_std(X[:, 0] - model_bias, y)
        for member in self.members:
            member.scale = model_std
            member.bias = model_bias

        print("Fit model with simple dressing")
        print("Scale: %f" % model_std)
        print("Bias:  %f" % model_bias)

    def cdf(self, x, member_means):
        assert len(member_means) == self.member_count
        return sum([
            member.cdf(x, mean - member.bias) * weight
            for (member, mean, weight)
            in zip(self.members, member_means, self.weights)
        ])

    def mean(self, member_means):
        return sum([
            (mean - member.bias) * weight for (member, mean, weight)
            in zip(self.members, member_means, self.weights)
        ])


class MixtureMember:
    """"""

    def __init__(self, distribution, scale=1):
        """"""
        self.distribution = distribution
        self.scale = scale
        self.bias = 0

    def pdf(self, X, *args):
        """"""
        return self.distribution.pdf(X - self.bias, *args, scale=self.scale)

    def cdf(self, X, *args):
        """"""
        return self.distribution.cdf(X - self.bias, *args, scale=self.scale)

if __name__ == "__main__":
    model = GaussianMixtureModel(10)