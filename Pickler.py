import os
import pickle
from Stock import Stock

class PickleSource:
    "Source during which scraping encountered an error"

    NOPICKLE = 0
    FINVIZ = 1
    YHOOEV = 2
    YHOOBBY = 3

    def __str__(self):
        if self == NOPICKLE:
            return 'NOPICKLE'
        elif self == FINVIZ:
            return 'FINVIZ'
        elif self == YHOOEV:
            return 'YHOOEV'
        elif self == YHOOBBY:
            return 'YHOOBBY'
        else:
            return 'NOPICKLE'

class Pickler:
    "Handles HTML connection errors"

    # .pkl filename
    fileName = ''
    # Was a PKL file loaded?
    isFileLoaded = False
    # HTML source where connection error occurred
    source = PickleSource.NOPICKLE
    # Index (stock number or page number, depending on source)
    index = 0
    # Has an error occurred
    hasErrorOccurred = False

    def loadPickledFile(self, pklFileName):
        "Check if file exists. Load if it does. Then delete the file."

        stocks = []
        self.fileName = pklFileName

        if os.path.isfile(pklFileName):
            # Pickle file found
            userInput = input('A temporary stock database from a previous ' +
            'run was found. Do you wish to load it (y/n)? ')

            if (userInput == 'y' or userInput == 'Y'):
                # Load PKL file
                self.isFileLoaded = True
                with open(pklFileName, 'rb') as pklFile:
                    # Left off at either FINVIZ, YHOOEV, or YHOOBBY depending on which
                    # source was being scraped.
                    self.source = pickle.load(pklFile)
                    # Index can be page number or unsorted stock number
                    self.index = pickle.load(pklFile)
                    # Current stock data in list
                    stocks = pickle.load(pklFile)

            # Delete existing file regardless of if the user chose to load the data
            os.remove(pklFileName)

        return stocks

    def getIndex(self, source, nMin, nMax):
        "Returns the index if we're at the correct source location. If we're \
        not, return either the nMin or nMax, depending on whether we want to \
        skip this source. The index will be used as the start index in a for \
        loop. If an error has occurred, by default we want to skip this (and \
        all subsequent sources)."

        if self.hasErrorOccurred:
            iS = nMax
        elif self.isFileLoaded:
            if self.source == source:
                # We're at the correct source. Return the loaded index and flip
                # the bool so we know we've read in the data.
                self.isFileLoaded = False
                iS = self.index
            else:
                # We're not at the correct source yet, which means we've already
                # imported this source and can skip it.
                iS = nMax
        else:
            # No file loaded. Read in the whole source starting at the beginning
            iS = nMin

        return iS

    def setError(self, source, i, stocks):
        "Triggers the error protocol. Saves source, index, and stocks to PKL file."

        self.hasErrorOccurred = True

        print('\n')
        print('The connection has been severed. Saving existing data to: ' +
        self.fileName)

        with open(self.fileName, 'wb') as pklFile:
            pickler = pickle.Pickler(pklFile, pickle.HIGHEST_PROTOCOL)

            # Dump location
            pickler.dump(source)
            # Dump page number
            pickler.dump(i)
            # Dump stocks list
            pickler.dump(stocks)

        return
