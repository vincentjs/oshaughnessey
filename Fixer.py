import numpy as np

def fixBrokenMetrics(stocks):
    "Fix negative earnings, dividends, etc. and artificially replace with a \
    value (0 or 100,000) that removes the metric from consideration"

    # Fix errors caused by negative earnings, no dividends, etc.
    nanPE = np.isnan([o.pe for o in stocks])
    nanPS = np.isnan([o.ps for o in stocks])
    nanPB = np.isnan([o.pb for o in stocks])
    nanPFCF = np.isnan([o.pfcf for o in stocks])
    nanDiv = np.isnan([o.div for o in stocks])
    nanMOM = np.isnan([o.mom for o in stocks])
    nanEVEBITDA = np.isnan([o.evebitda for o in stocks])

    # Some EV/EBITDA data is negative. How weird
    # negEVEBITDA = np.less([o.evebitda for o in stocks], 0)

    # Artificially set values to 100000 or 0, an arbitrary number that places the
    # item at the last of the list when sorted
    mHigh = 100000
    mLow = 0

    for i in range(len(stocks)):
        stocks[i].pe = mHigh if nanPE[i] else stocks[i].pe
        stocks[i].ps = mHigh if nanPS[i] else stocks[i].ps
        stocks[i].pb = mHigh if nanPB[i] else stocks[i].pb
        stocks[i].pfcf = mHigh if nanPFCF[i] else stocks[i].pfcf
        stocks[i].div = mLow if nanDiv[i] else stocks[i].div
        stocks[i].mom = mLow if nanMOM[i] else stocks[i].mom
        stocks[i].evebitda = mHigh if nanEVEBITDA[i] else stocks[i].evebitda
        # stocks[i].evebitda = mHigh if negEVEBITDA[i] else stocks[i].evebitda

    return stocks
