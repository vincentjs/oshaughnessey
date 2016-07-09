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

from sys import stdout

from Scraper import importFinvizPage, importHtml, readYahooLine
from StockDatabase import StockDatabase

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
for i in range(1, nPages + 1):
    # Print dynamic progress message
    stdout.write('\Scraping FINVIZ metrics from page ' + str(i) + ' of ' + \
        str(nPages) + '...')
    if i < nPages:
        stdout.flush()

    # Scrape data as before
    url = 'http://finviz.com/screener.ashx?v=152&f=cap_smallover&ft=4&r=' + \
        str(i*20+1) + '&c=0,1,2,6,7,10,11,13,14,45,65'
    html = importHtml(url)

    # Import stock metrics from page
    importFinvizPage(html, stocks)

# FINVIZ stock metrics successfully imported
print('\n')

# Grab EV/EBITDA metrics from Yahoo! Finance
nStocks = len(stocks.name)

for i in range(0, nStocks + 1):
    # Print dynamic progress message
    stdout.write('\Scraping EV/EBITDA for ' + stocks.tick[i] +
        ' (' + str(i) + '/' + str(nStocks + 1) + ') from Yahoo! Finance...')
    if i < nStocks:
        stdout.flush()

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
            evebitda = readYahooLine(line)
            stocks.evebitda.append(evebitda)
            break


# Yahoo! Finance EV/EBITDA successfully imported
print('\n')

# Grab BBY metrics from Yahoo! Finance
for i in range(0, nStocks + 1):
    # Print dynamic progress message
    stdout.write('\Scraping BBY for ' + stocks.tick[i] +
        ' (' + str(i) + '/' + str(nStocks + 1) + ') from Yahoo! Finance...')
    if i < nStocks:
        stdout.flush()

    # Scrape data from Yahoo! Finance
    url = 'http://finance.yahoo.com/q/cf?s=' + stocks.tick[i] + '&ql=1'
    html = importHtml(url)

    # Parse data
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
            if 'Net.Borrowings' in line:
                # Line also contains Borrowings details

print("Done.")
