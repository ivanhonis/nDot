import pickle


class n_date_frame_meta:

    def __init__(self, log):
        self.log = log
        self.nddf_meta = {}
        self.load()

    def write(self):
        # self.log(f"n_date_frame_meta->write")
        with open('nddf_meta.pickle', 'wb') as f:
            pickle.dump(self.nddf_meta, f)

    def load(self):
        try:
            with open('nddf_meta.pickle', 'rb') as f:
                self.nddf_meta = pickle.load(f)
        except:
            self.nddf_meta = {}

    def add_meta_key(self, symbol, key, value):
        # self.log(f"n_date_frame_meta->add_meta_key {symbol} {key}")
        i_meta_name = symbol + '_META'
        if i_meta_name in self.nddf_meta.keys():
            self.nddf_meta[i_meta_name][key] = value
        else:
            self.nddf_meta[i_meta_name] = {}
            self.nddf_meta[i_meta_name][key] = value
        self.write()

    def remove_meta_key(self, symbol, key):
        i_meta_name = symbol + '_META'
        if i_meta_name in self.nddf_meta.keys():
            if key in self.nddf_meta[i_meta_name].keys():
                del self.nddf_meta[i_meta_name][key]
                self.write()

    def remove_meta(self, symbol):
        i_meta_name = symbol + '_META'
        if i_meta_name in self.nddf_meta.keys():
            del self.nddf_meta[i_meta_name]
            self.write()

    def get_meta_key(self, symbol, key):
        i_meta_name = symbol + '_META'
        if i_meta_name in self.nddf_meta.keys():
            if key in self.nddf_meta[i_meta_name].keys():
                i_return = self.nddf_meta[i_meta_name][key]
            else:
                i_return = ""
        else:
            i_return = ""
        return i_return

    def get_all_meta_key(self, symbol):
        i_meta_name = symbol + '_META'
        i_return = ""
        if i_meta_name in self.nddf_meta.keys():
            for i_mk in self.nddf_meta[i_meta_name]:
                i_return = i_return + str(i_mk) + ": " + str(self.nddf_meta[i_meta_name][i_mk]) + "\n   "
        else:
            i_return = ""
        return i_return
