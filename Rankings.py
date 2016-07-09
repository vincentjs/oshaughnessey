import numpy

def rankByValue(X):
    "Returns the rank (1, 2, ...) of each item in a list. If items are tied, \
    the item with the lower index is scored with a better rank (i.e. closer to \
    first)."

    narray = numpy.array(X)
    order = narray.argsort()
    ranks = order.argsort()

    return ranks
