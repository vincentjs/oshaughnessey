import numpy as np

class Stock:
    "Stock metrics for a single stock"

    # Ticker
    tick = ""
    # Full company name
    name = ""
    # Value composite
    vc = 0.0
    # Trending value rank
    rank = 0.0
    # Market cap
    mktcap = 0.0
    # P/E ratio
    pe = 0.0
    # P/S ratio
    ps = 0.0
    # P/B ratio
    pb = 0.0
    # P/FCF ratio
    pfcf = 0.0
    # Dividend
    div = 0.0
    # Momentum
    mom = 0.0
    # Price
    price = 0.0
    # EV/EBITDA ratio
    evebitda = 0.0
    # Shareholder yield
    shy = 0.0
    # Buyback yield
    bby = 0.0

    def getStockAsList(self):
        "Returns stock attributes as a List"
        return [self.rank, self.vc, self.tick, self.name, self.mktcap,
        self.pe, self.ps, self.pb, self.pfcf, self.div,
        self.mom, self.price, self.evebitda, self.shy, self.bby]
