# Original Work: James O'Shaughnessey, "What Works on Wall Street"
# MATLAB Script: Justin Riley, 2012-2014
# Python 3.x Script: Vincent San Miguel, July 2016
#
# Replicates the concept of Trending Value. Each company is scored on six
# performance metrics:
#   (1) P/E ratio (Price to Earnings)
#   (2) P/S ratio (Price to Sales)
#   (3) P/B ratio (Price to Book)
#   (4) P/FCF ratio (Price to Free Cash Flow)
#   (5) EV/EBITDA ratio (Enterprise Value to Earnings Before Interest, Taxes,
#                        Depreciation, and Amortization)
#   (6) Shareholder Yield (Dividend Yield + Buyback Yield)
#
# O'Shaughnessey individually scores these on a scale of 0-100 (where 100
# is the best). The scores are summed (0-600) to represent the stock's
# intrinsic value relative to the market. A perfect score of 600 represents
# a highly undervalued stock.
#
# Post-processing is done to arrange stocks in descending order; the top 10%
# is marked for further sorting. The list is rearranged by 6 month price
# momentum.
#
# The top 25 stocks are bought in equal amounts and held for 1 year.
# Historically, this has averaged a return of 21% per year.
#
# Some equities do not report certain metrics (e.g. mutual funds and EV/EBITDA).
# These values are set to either 0 or 100,000 depending on the metric.
#
# See Copyright.

import numpy as np
from sys import stdout
from itertools import compress

from StockDatabase import StockDatabase
from Scraper import importFinvizPage, importHtml, readYahooEVEBITDA, \
    readYahooBBY
from Rankings import rankByValue
from Mask import fixit


# Scrape data from FINVIZ. Certain presets have been established (see direct
# link for more details)
url = 'http://finviz.com/screener.ashx?v=152&f=cap_smallover&' + \
    'ft=4&c=0,1,2,6,7,10,11,13,14,45,65'
html = importHtml(url)

# Parse the HTML for the number of pages from which we'll pull data
nPages = -1
for line in html:
    if line[0:40] == '<option selected="selected" value=1>Page':
        # Find indices
        b1 = line.index('/') + 1
        b2 = b1 + line[b1:].index('<')
        # Number of pages containing stock data
        nPages = int(line[b1:b2])
        break

# Create a database containing all stocks
stocks = StockDatabase()

# Parse data from table on the first page of stocks and store in the database
importFinvizPage(html, stocks)

# The first page of stocks (20 stocks) has been imported. Now import the
# rest of them
# for i in range(1, nPages + 1):
#     # Print dynamic progress message
#     print('Scraping FINVIZ metrics from page ' + str(i) + ' of ' + \
#         str(nPages) + '...', file=stdout, flush=True)
#
#     # Scrape data as before
#     url = 'http://finviz.com/screener.ashx?v=152&f=cap_smallover&ft=4&r=' + \
#         str(i*20+1) + '&c=0,1,2,6,7,10,11,13,14,45,65'
#     html = importHtml(url)
#
#     # Import stock metrics from page
#     importFinvizPage(html, stocks)

# FINVIZ stock metrics successfully imported
print('\n')

# Grab EV/EBITDA metrics from Yahoo! Finance
nStocks = len(stocks.name)

for i in range(0, nStocks):
    # Print dynamic progress message
    print('Scraping EV/EBITDA for ' + stocks.tick[i] +
        ' (' + str(i) + '/' + str(nStocks - 1) + ') from Yahoo! Finance...', \
        file=stdout, flush=True)

    # Scrape data from Yahoo! Finance
    url = 'http://finance.yahoo.com/q/ks?s=' + stocks.tick[i] + '+Key+Statistics'
    html = importHtml(url)

    # Parse data
    for line in html:
        # Check no value
        if 'There.is.no.Key.Statistics' in line or \
        'Get.Quotes.Results.for' in line or \
        'Changed.Ticker.Symbol' in line or \
        '</html>' in line:
            # Non-financial file (e.g. mutual fund) or
            # Ticker not located or
            # End of html page
            stocks.evebitda.append(1000)
            break
        elif 'Enterprise.Value/EBITDA' in line:
            # Line contains EV/EBITDA data
            evebitda = readYahooEVEBITDA(line)
            stocks.evebitda.append(evebitda)
            break


# Yahoo! Finance EV/EBITDA successfully imported
print('\n')

# Grab BBY metrics from Yahoo! Finance
for i in range(0, nStocks):
    # Print dynamic progress message
    print('Scraping BBY for ' + stocks.tick[i] +
        ' (' + str(i) + '/' + str(nStocks - 1) + ') from Yahoo! Finance...', \
        file=stdout, flush=True)

    # Scrape data from Yahoo! Finance
    url = 'http://finance.yahoo.com/q/cf?s=' + stocks.tick[i] + '&ql=1'
    html = importHtml(url)

    # Parse data
    totalBuysAndSells = 0
    for line in html:
        # Check no value
        if 'There.is.no.Cash.Flow' in line or \
        'Get.Quotes.Results.for' in line or \
        'Changed.Ticker.Symbol' in line or \
        '</html>' in line:
            # Non-financial file (e.g. mutual fund) or
            # Ticker not located or
            # End of html page
            break
        elif 'Sale.Purchase.of.Stock' in line:
            # Line contains Sale/Purchase of Stock information
            totalBuysAndSells = readYahooBBY(line)
            break

    # Calculate BBY as a percentage of current market cap
    bby = -totalBuysAndSells / stocks.mktcap[i] * 100
    stocks.bby.append(bby)

# Yahoo! Finance BBY successfully imported
# All data imported
print('\n')

print('Fixing screener errors...')

# Fix errors caused by negative earnings, no dividends, etc.
nanPE = np.isnan(stocks.pe)
nanPS = np.isnan(stocks.ps)
nanPB = np.isnan(stocks.pb)
nanPFCF = np.isnan(stocks.pfcf)
nanDiv = np.isnan(stocks.div)
nanMOM = np.isnan(stocks.mom)
nanEVEBITDA = np.isnan(stocks.evebitda)

# Some EV/EBITDA data is negative
negEVEBITDA = [x for x in stocks.evebitda if x < 0]

# Artificially set values to 100000 or 0, an arbitrary number that places the
# item at the last of the list when sorted
magicHigh = 100000
magicLow = 0

stocks.pe = fixit(stocks.pe, nanPE, magicHigh)
stocks.ps = fixit(stocks.ps, nanPS, magicHigh)
stocks.pb = fixit(stocks.pb, nanPB, magicHigh)
stocks.pfcf = fixit(stocks.pfcf, nanPFCF, magicHigh)
stocks.div = fixit(stocks.div, nanDiv, magicLow)
stocks.mom = fixit(stocks.mom, nanMOM, magicLow)
stocks.evebitda = fixit(stocks.evebitda, nanEVEBITDA, magicHigh)
stocks.evebitda = fixit(stocks.evebitda, negEVEBITDA, magicHigh)

# Calculate shareholder Yield
div = np.array(stocks.div)
bby = np.array(stocks.bby)
shy = div + bby
stocks.shy = np.ndarray.tolist(shy)

# Time to rank! Lowest value gets 100
rankPE = 100 * (-rankByValue(stocks.pe) / len(stocks.pe) + 1)
rankPS = 100 * (-rankByValue(stocks.ps) / len(stocks.ps) + 1)
rankPB = 100 * (-rankByValue(stocks.pb) / len(stocks.pb) + 1)
rankPFCF = 100 * (-rankByValue(stocks.pfcf) / len(stocks.pfcf) + 1)
rankEVEBITDA = 100 * (-rankByValue(stocks.evebitda) / len(stocks.evebitda) + 1)

# Shareholder yield ranked with highest getting 100
rankSHY = 100 * (rankByValue(stocks.shy) / len(stocks.shy))

# Rank total stock valuation
rankStock = rankPE + rankPS + rankPB + rankPFCF + rankEVEBITDA + rankSHY

# Normalize rankings
rankOverall = rankByValue(rankStock) / len(rankStock)

# Sort all stocks by overall rank
for i in range(nStocks):
    

# # Get top decile
# topDecile = np.where(rankOverall >= 0.9)
# # Sort top decile by price momentum
# mom = np.array(stocks.mom)
# topMOM = rankByValue(mom[topDecile])
#
# Get indices of top 25 stocks
# n = 25
# topStockIndices = np.zeros(n)
# for i in range(n):
#     indexTopMOM = np.argmax(mom[topDecile])
#     print(indexTopMOM)
#
#     # Add stock index to list
#     topStockIndices[i] = indexTopMOM
#
#     # Artificially set momentum to -100% to remove it from further consideration
#     mom[indexTopMOM] = -100

tick = np.array(stocks.tick)
print(tick[topMOM])

print("Done.")
