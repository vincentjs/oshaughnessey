import csv

def writeCSV(csvpath, stockDatabase):
    with open(csvpath, 'w', newline='') as csvf:
        dbWriter = csv.writer(csvf, delimiter='\t', quotechar='|', \
        quoting=csv.QUOTE_MINIMAL)

        # Write header
        dbWriter.writerow(['Rank', 'VC', 'Tick', 'Name', 'Cap',
        'P/E', 'P/S', 'P/B', 'P/FCF', 'Div', 'Mom', 'Price', 'EV/EBITDA', 'SHY',
        'BBY'])

        for i in range(len(stockDatabase)):
            # Get stock data
            row = stockDatabase[i].getStockAsList()

            # Convert market cap (row[4]) to M or B for readability
            if (row[4] / 1000000000 >= 1):
                mktcap = str(row[4] / 1000000000) + ' B'
            else:
                mktcap = str(row[4] / 1000000) + ' M'
            row[4] = mktcap

            # Convert to strings
            for i, x in enumerate(row):
                try:
                    row[i] = str(x)
                except ValueError:
                    pass

            # Write to CSV file
            dbWriter.writerow(row)
