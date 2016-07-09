import re
from urllib.request import urlopen

from StockDatabase import StockDatabase

def importHtml(url):
    "Scrapes the HTML file from the given URL"

    response = urlopen(url, data = None)
    html = response.read().decode('utf-8').split('\n')

    return html

def importFinvizPage(html, stocks):
    "Imports data from a FINVIZ HTML page"

    isFound = False

    for line in html:
        if line[0:15] == '<td height="10"':
            isFound = True
            # Import data line into stock database
            _readFinvizLine(line, stocks)

        if isFound and len(line) < 10:
            break

    return

def _readFinvizLine(line, stocks):
    "Imports stock metrics from the data line and stores it in the database"

    # Parse html
    (stkraw, dl) = _parseHtml(line)

    # Get ticker symbol
    stocks.tick.append(stkraw[dl[1] + 1: dl[2]])
    # Get company name
    stocks.name.append(stkraw[dl[2] + 1 : dl[3]])
    # Get market cap
    stocks.mktcap.append(stkraw[dl[3] + 1 : dl[4]])
    # Get P/E ratio
    stocks.pe.append(stkraw[dl[4] + 1 : dl[5]])
    # Get P/S ratio
    stocks.ps.append(stkraw[dl[5] + 1 : dl[6]])
    # Get P/B ratio
    stocks.pb.append(stkraw[dl[6] + 1 : dl[7]])
    # Get P/FCF ratio
    stocks.pfcf.append(stkraw[dl[7] + 1 : dl[8]])
    # Get Dividend Yield
    stocks.div.append(stkraw[dl[8] + 1 : dl[9]])
    # Get 6-mo Relative Price Strength
    stocks.mom.append(stkraw[dl[9] + 1 : dl[10]])
    # Get Current Stock Price
    stocks.price.append(stkraw[dl[11] + 1 : dl[12]])

    return

def readYahooLine(line):
    "Imports stock metrics from a Yahoo Finance data line and stores it in "
    "the database"

    # Parse html
    (stkraw, dl) = _parseHtml(line)

    for i in range(0, len(dl)):
        if (stkraw[dl[i] + 1 : dl[i] + 24] == 'Enterprise Value/EBITDA'):
            evebitda = stkraw[dl[i + 1] + 1 : dl[i + 2]]
            break

    return evebitda

def _parseHtml(line):
    "Parses the HTML line"

    # Replace </td> breaks with placeholder
    ph = '`'
    rem = re.sub('</td>', ph, line)

    # The ticker symbol initial delimiter is different
    # Remove all other remaining HTML data
    stkraw = re.sub('<.*?>', '', rem)

    # Replace unbalanced HTML
    stkraw = re.sub('">', '`', stkraw)

    # Find the placeholders
    dl = [m.start() for m in re.finditer(ph, stkraw)]

    return (stkraw, dl)
