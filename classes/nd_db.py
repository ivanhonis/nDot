import pandas as pd
import os


class nd_db():

    def __init__(self, nddf, log):
        self.nddf = nddf
        self.log = log
        self.store = pd.HDFStore('nDot_db.h5', "a")
        for i_key in self.get_keys():
            self.read(i_key, True)
        self.close()

    def get_size(self):
        return int(os.path.getsize('nDot_db.h5')/1024)

    def get_keys(self):
        self.open()
        i_keys = self.store.keys()
        i_return = []
        for i_key in i_keys:
            i_return.append(i_key[1:])
        self.close()
        return i_return

    def write(self, symbol):
        self.log("nd_db-> write:" + symbol)
        self.open()
        self.store.put(symbol, self.nddf[symbol], format='table')
        self.close()

    def read(self, symbol, for_init=False):
        if not for_init:
            self.log("nd_db-> read:" + symbol)
        self.open()
        self.nddf[symbol] = self.store.get(symbol)
        self.close()

    def remove(self, symbol):
        self.log("nd_db-> remove:" + symbol)
        i_return = ""
        if symbol in self.get_keys():
            self.open()
            i_return = self.store.remove(symbol)
            self.close()
        return i_return

    def open(self):
        self.store.open("a")

    def close(self):
        self.store.close()

    def info(self):
        self.open()
        i_nfo = self.store.info()
        self.close()
        return i_nfo
