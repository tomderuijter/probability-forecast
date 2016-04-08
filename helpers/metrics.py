"""Module containing verification metrics."""
import math
import numpy as np


def _heavyside(thresholds, actual):
    # TODO Optimize assuming thresholds is sorted in ascending order.
    """Return 1 if threshold >= actual, else 0."""
    result = [1 if t >= actual else 0 for t in thresholds]
    return result


def _is_cdf_valid(case):
    """Return whether all cdf probabilities are in [0,1] and non-decreasing."""
    precision = 10e-9
    if case[0] < 0 - precision or case[0] > 1 + precision:
        return False
    for i in range(1, len(case)):
        if case[i] > 1 + precision or case[i] < case[i - 1]:
            return False
    return True


def crps(thresholds, case, actual):
    """Calculate the CRPS for a single observation and distribution."""
    crps = 0
    # Check whether the right number of prediction bins has been provided
    # and whether it encodes a cumulative distribution.
    if (len(case) == len(thresholds)) and _is_cdf_valid(case):
        obscdf = _heavyside(thresholds, actual)
        for fprob, oprob in zip(case, obscdf):
            crps += (fprob - oprob) * (fprob - oprob)
    else:
        print("Warning: bad CDF provided.")
        crps += len(thresholds)  # treat delta at each threshold as 1
    crps /= len(thresholds)
    return crps


def mean_crps(thresholds, predictions, actuals):
    """ Calculate the Continuous Ranked Probability Score.

    Parameters
    ----------
    1D array of thresholds
    2D array consisting of rows of [predictions P(y <= t) for each threshold]
    1D array consisting of rows of observations

    For more on CRPS, see:
    http://www.eumetcal.org/resources/ukmeteocal/verification/www/english/msg/ver_prob_forec/uos3b/uos3b_ko1.htm
    """
    ncases = len(predictions)
    mean_crps = 0
    for case, actual in zip(predictions, actuals):
        mean_crps += crps(thresholds, case, actual)
    mean_crps /= float(ncases)

    return mean_crps


def _nearly_equal(a, b, tol):
    return abs(a - b) < tol


# Test
def percentiles(cdf_fun, percentiles):
    """Return scores corresponding to given percentiles."""
    assert np.logical_and(percentiles < 1, percentiles > 0).all()

    values = [math.nan] * len(percentiles)
    cdfs = [math.nan] * len(percentiles)
    # TODO Find better initialization of last_value.
    last_value = -30.0 + 273.15

    # Simple uniform search scheme
    # step_size = 0.5  # Expressed in value
    step_size = 0.1
    # tolerance = 0.01  # Expressed in probability mass
    for count, percentile in enumerate(percentiles):
        # print("Finding percentile %.2f" % percentile)
        fringe = last_value
        fringe_cdf = cdf_fun(fringe)
        # Increment fringe until value is at or over percentile.
        while fringe_cdf < percentile:
            fringe += step_size
            fringe_cdf = cdf_fun(fringe)
            # print('%.2f, %.2f' % (fringe, fringe_cdf))
        # print("Overshot the percentile.")
        # It holds that;
        #  fringe >= percentile_value
        #  cdf(fringe) < cdf(percentile_value + step_size)

        # # Simple binary search
        # factor = 1
        # sign = -1
        # while not _nearly_equal(fringe_cdf, percentile, tolerance):
        #     fringe += factor * sign * step_size
        #     fringe_cdf = cdf_fun(fringe)
        #     # print('%.2f, %.2f' % (fringe, fringe_cdf))
        #     if fringe_cdf > percentile:
        #         sign = -1
        #     else:
        #         sign = 1
        #     factor /= 2
        # print("Found the percentile.")
        values[count] = fringe
        cdfs[count] = fringe_cdf
        print('%.2f, %.2f' % (percentile, fringe_cdf))
        last_value = fringe
    return values
