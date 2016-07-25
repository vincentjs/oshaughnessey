# oshaughnessey
Implements the "Trending Value" strategy introduced by James O'Shaughnessey in "What Works on Wall Street"

## Install
```
git clone https://github.com/vincentjs/oshaughnessey
```
## Run
```
python3 oshaugh.py
```

## Restart
Stock metrics are obtained by reading HTML data from Finviz and Yahoo! Finance, a process which may take 30+ minutes. In some cases, a connection error may occur, stopping the procedure. When this occurs, existing stock data is saved to a PKL file before exiting the script. Rerun the script to have the option of reloading this data, and restarting from where the program left off before being interrupted.
