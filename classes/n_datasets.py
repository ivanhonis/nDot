import pickle
import datetime

import numpy as np


class n_dataset():

    def __init__(self, log):
        self.log = log
        self.gdrive_path = "C:/Users/honis.ivan/Google Drive/nDot_Colabs/"
        self.fields_dict = {}
        self.data = {
                'name': "",  ## ez lesz a file neve
                'data_structure_ver': "2.0",  ## ez lesz a file neve
                'timestamp': "",  ## mikor készültek az adatok
                'source': "",  ## melyik eljárás milyen paraméterekkel állította elő
                'symbol': "",  ## melyik érszvényhez készült
                'description': "",  ## magyarázat mit volt az ötlet
                'X': np.array([]),  ## ezek az adat sorok
                'X_count': 0,  ## hány adatcsomagot tartalmaz
                'y': np.array([]),  ## cimkék
                'y_names': np.array,  ## a targetek értelmezése
                'y_unique': {},  # melyik cimkéből hány van az adatszetben
                'data_fields': [],  ## milyen adatokból készült a dataset
                'window_size': 0, ## mekkora az abalak mérete
                'meta': "",  ## a good minták milyen beállításokkal keletkeztek
                'historic_max': np.array([]), ## az adatok egységes normalizálásoh a történelmi maximum értékek
                'historic_min': np.array([])  ## az adatok egységes normalizálásoh a történelmi maximum értékek
        }

    def set_name(self, name):
        self.data['name'] = name
        self.data['timestamp'] = str(datetime.datetime.now())  ## névadáskor jön létra az időbélyeg

    def set_symbol(self, symbol):
        self.data['symbol'] = symbol

    def set_source(self, source):
        self.data['source'] = source

    def set_meta(self, meta):
        self.data['meta'] = "   " + meta

    def set_description(self, description):
        self.data['description'] = description

    def add_y_names(self, target_names):
        self.data['y_names'] = target_names

    def set_historic_max(self, historic_max):
        self.data['historic_max'] = historic_max

    def set_historic_min(self, historic_min):
        self.data['historic_min'] = historic_min

    def add_X(self, array):
        if len(self.data['X']) == 0:
            self.data['X'] = array
        else:
            self.data['X'] = np.vstack((self.data['X'], array))
        self.data['X_count'] += 1

    def add_y(self, label):
        label = np.array([label])
        self.data['y'] = np.concatenate((self.data['y'], label))

    def add_field(self, field):
        self.fields_dict[field] = 0

    def set_window_size(self, window_size):
        self.data['window_size'] = window_size

    def set_y_unique(self):
        self.data['y_unique'] = {}
        values, counts = np.unique(self.data['y'], return_counts=True)
        self.data['y_unique']["values"] = values
        self.data['y_unique']["counts"] = counts

    def save(self):
        self.set_y_unique()
        self.log('X shape: ' + str(self.data['X'].shape))
        self.log('y shape: ' + str(self.data['y'].shape))
        self.log('Historic max shape: ' + str(self.data['historic_max'].shape))
        self.log('Historic min shape: ' + str(self.data['historic_min'].shape))
        self.data['data_fields'] = str(tuple(self.fields_dict.keys()))
        pickle.dump(self.data, open(self.gdrive_path+self.data['name']+".pickle", "wb"))
        self.log('n_dataset->saved: ' + str(self.gdrive_path+self.data['name']+".pickle"))

    def load(self, file_name):
        return pickle.load(open(self.gdrive_path+file_name+'.pickle', "rb"))
