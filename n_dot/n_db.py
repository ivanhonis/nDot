import pandas as pd
import tables
import os
import threading


class n_db:

    def __init__(self, nddf, log):
        self.nddf = nddf
        self.log = log
        self.paralell_load()
        self.store = pd.HDFStore('nDot_db.h5', "a")

    def paralell_load(self):
        print("Status: nDot Database loading...")
        i_store = pd.HDFStore('nDot_db.h5', "a")
        i_store.open("r")
        i_keys = i_store.keys()
        i_keys_array = []
        for i_key in i_keys:
            i_keys_array.append(i_key[1:])

        def read_paralell(symbol):
            self.nddf[symbol] = i_store.get(symbol)

        threads = list()
        for i_k in i_keys_array:
            xt = threading.Thread(target=read_paralell, args=(i_k,))
            threads.append(xt)

        for th in threads:
            th.start()

        for th in threads:
            th.join()

        i_store.close()

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

    def write(self, symbol, log_off=False):
        if not log_off:
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
