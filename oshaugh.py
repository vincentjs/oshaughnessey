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
# See LICENSE.

from sys import stdout

from Stock import Stock
import Scraper
import Rankings
import Fixer
import Writer


# Scrape data from FINVIZ. Certain presets have been established (see direct
# link for more details)
url = 'http://finviz.com/screener.ashx?v=152&f=cap_smallover&' + \
    'ft=4&c=0,1,2,6,7,10,11,13,14,45,65'
html = Scraper.importHtml(url)

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
stocks = []

# Parse data from table on the first page of stocks and store in the database
Scraper.importFinvizPage(html, stocks)

# The first page of stocks (20 stocks) has been imported. Now import the
# rest of them
for i in range(1, nPages + 1):
    # Print dynamic progress message
    print('Importing FINVIZ metrics from page ' + str(i) + ' of ' + \
        str(nPages) + '...', file=stdout, flush=True)

    # Scrape data as before
    url = 'http://finviz.com/screener.ashx?v=152&f=cap_smallover&ft=4&r=' + \
        str(i*20+1) + '&c=0,1,2,6,7,10,11,13,14,45,65'
    html = Scraper.importHtml(url)

    # Import stock metrics from page
    Scraper.importFinvizPage(html, stocks)

# FINVIZ stock metrics successfully imported
print('\n')

# Grab EV/EBITDA metrics from Yahoo! Finance
nStocks = len(stocks)

for i in range(nStocks):
    # Print dynamic progress message
    print('Importing Key Statistics for ' + stocks[i].tick +
        ' (' + str(i) + '/' + str(nStocks - 1) + ') from Yahoo! Finance...', \
        file=stdout, flush=True)

    # Scrape data from Yahoo! Finance
    url = 'http://finance.yahoo.com/q/ks?s=' + stocks[i].tick + '+Key+Statistics'
    html = Scraper.importHtml(url)

    # Parse data
    for line in html:
        # Check no value
        if 'There is no Key Statistics' in line or \
        'Get Quotes Results for' in line or \
        'Changed Ticker Symbol' in line or \
        '</html>' in line:
            # Non-financial file (e.g. mutual fund) or
            # Ticker not located or
            # End of html page
            stocks[i].evebitda = 1000
            break
        elif 'Enterprise Value/EBITDA' in line:
            # Line contains EV/EBITDA data
            evebitda = Scraper.readYahooEVEBITDA(line)
            stocks[i].evebitda = evebitda
            break


# Yahoo! Finance EV/EBITDA successfully imported
print('\n')

# Grab BBY metrics from Yahoo! Finance
for i in range(nStocks):
    # Print dynamic progress message
    print('Importing Cash Flow for ' + stocks[i].tick +
        ' (' + str(i) + '/' + str(nStocks - 1) + ') from Yahoo! Finance...', \
        file=stdout, flush=True)

    # Scrape data from Yahoo! Finance
    url = 'http://finance.yahoo.com/q/cf?s=' + stocks[i].tick + '&ql=1'
    html = Scraper.importHtml(url)

    # Parse data
    totalBuysAndSells = 0
    for line in html:
        # Check no value
        if 'There is no Cash Flow' in line or \
        'Get Quotes Results for' in line or \
        'Changed Ticker Symbol' in line or \
        '</html>' in line:
            # Non-financial file (e.g. mutual fund) or
            # Ticker not located or
            # End of html page
            break
        elif 'Sale Purchase of Stock' in line:
            # Line contains Sale/Purchase of Stock information
            totalBuysAndSells = Scraper.readYahooBBY(line)
            break

    # Calculate BBY as a percentage of current market cap
    bby = round(-totalBuysAndSells / stocks[i].mktcap * 100, 2)
    stocks[i].bby = bby

# Yahoo! Finance BBY successfully imported
# All data imported
print('\n')
print('Fixing screener errors...')

stocks = Fixer.fixBrokenMetrics(stocks)

print('Ranking stocks...')

# Calculate shareholder Yield
for i in range(nStocks):
    stocks[i].shy = stocks[i].div + stocks[i].bby

# Time to rank! Lowest value gets 100
rankPE = 100 * (1 - Rankings.rankByValue([o.pe for o in stocks]) / nStocks)
rankPS = 100 * (1 - Rankings.rankByValue([o.ps for o in stocks]) / nStocks)
rankPB = 100 * (1 - Rankings.rankByValue([o.pb for o in stocks]) / nStocks)
rankPFCF = 100 * (1 - Rankings.rankByValue([o.pfcf for o in stocks]) / nStocks)
rankEVEBITDA = 100 * (1 - Rankings.rankByValue([o.evebitda for o in stocks]) / nStocks)

# Shareholder yield ranked with highest getting 100
rankSHY = 100 * (Rankings.rankByValue([o.shy for o in stocks]) / nStocks)

# Rank total stock valuation
rankStock = rankPE + rankPS + rankPB + rankPFCF + rankEVEBITDA + rankSHY

# Rank 'em
rankOverall = Rankings.rankByValue(rankStock)
# Calculate Value Composite - higher the better
valueComposite = 100 * rankOverall / len(rankStock)
# Reverse indices - lower index -> better score
rankOverall = [len(rankStock) - 1 - x for x in rankOverall]

# Assign to stocks
for i in range(nStocks):
    stocks[i].rank = rankOverall[i]
    stocks[i].vc = round(valueComposite[i], 2)

print('Sorting stocks...')

# Sort all stocks by normalized rank
stocks = [x for (y, x) in sorted(zip(rankOverall, stocks))]

# Sort top decile by momentum factor
dec = int(nStocks / 10)
topDecile = []

# Store temporary momentums from top decile
moms = [o.mom for o in stocks[:dec]]

for i in range(dec):
    # Get index of top momentum performer in top decile
    topMomInd = moms.index(max(moms))
    # Sort
    topDecile.append(stocks[topMomInd])
    # Remove top momentum performer from further consideration
    moms[topMomInd] = -100

print('Saving stocks...')

# Save momentum-weighted top decile
csvpath = 'top.csv'
Writer.writeCSV(csvpath, topDecile)

# Save results to .csv
csvpath = 'stocks.csv'
Writer.writeCSV(csvpath, stocks)

print('\n')
print('Complete.')
print('Results saved to ' + csvpath)
