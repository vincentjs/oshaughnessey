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

    # Get market cap multiplier (either MM or BB)
    if stkraw[dl[4] - 1] == 'B':
        capmult = 1000000000
    else:
        capmult = 1000000

    # Get market cap
    stocks.mktcap.append(capmult * _toFloat(stkraw[dl[3] + 1 : dl[4] - 1]))
    # Get P/E ratio
    stocks.pe.append(_toFloat(stkraw[dl[4] + 1 : dl[5]]))
    # Get P/S ratio
    stocks.ps.append(_toFloat(stkraw[dl[5] + 1 : dl[6]]))
    # Get P/B ratio
    stocks.pb.append(_toFloat(stkraw[dl[6] + 1 : dl[7]]))
    # Get P/FCF ratio
    stocks.pfcf.append(_toFloat(stkraw[dl[7] + 1 : dl[8]]))
    # Get Dividend Yield
    stocks.div.append(_toFloat(stkraw[dl[8] + 1 : dl[9] - 1]))
    # Get 6-mo Relative Price Strength
    stocks.mom.append(_toFloat(stkraw[dl[9] + 1 : dl[10] - 1]))
    # Get Current Stock Price
    stocks.price.append(_toFloat(stkraw[dl[11] + 1 : dl[12]]))

    return

def _toFloat(line):
    "Converts a string to a float"

    try:
        num = float(line)
    except:
        num = float('NaN')

    return num

def readYahooEVEBITDA(line):
    "Imports EV/EBITDA data from Yahoo! Finance"

    # Parse html
    (stkraw, dl) = _parseHtml(line)

    for i in range(0, len(dl)):
        if (stkraw[dl[i] + 1 : dl[i] + 24] == 'Enterprise Value/EBITDA'):
            evebitda = stkraw[dl[i + 1] + 1 : dl[i + 2]]
            break

    return float(evebitda)

def readYahooBBY(line):
    "Imports BBY data from Yahoo! Finance"

    # Line also contains Borrowings details
    if 'Net.Borrowings' in line:
        # Remove extra data
        line = re.sub('Net.Borrowings.*', '', line)

    # Trim prior data
    line = line[line.find('Sale.Purchase.of.Stock')]
    # Determine if buys or sells, replace open parantheses:
    # (#,###) -> -#,###
    line = re.sub(line, '(', '-')
    # Eliminate commas and close parantheses: -#,### -> -####
    line = re.sub(line, ',|)', '')
    # Remove HTML data and markup, replacing with commas
    line = re.sub(line, '<.*?>|&nbsp;', ',')
    # Locate the beginning of quarterly Sale Purchase points
    starts = [m.start() for m in re.finditer(',\d+,|,.\d+', line)]
    # Locate the end of quarterly Sale Purchase points
    ends = [m.start() for m in re.finditer('\d,', line)]

    # Sum all buys and sells
    tot = 0
    for i in range(0, len(starts)):
        tot = tot + float(line[starts[i] + 1 : ends[i]]) * 1000

    return tot

def _parseHtml(line):
    "Parses the HTML line by </td> breaks and returns the delimited string"

    # Replace </td> breaks with placeholder, '`'
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
