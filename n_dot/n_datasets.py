import pickle
import datetime
import sys

import numpy as np


class n_dataset:

    def __init__(self, log):
        self.log = log
        self.gdrive_path = "X:/Apa/cloud/GoogleDriveSync/nDot_Colabs/"
        self.project_path = ""
        self.fields_dict = {}
        self.data = {
                'name': "",  ## ez lesz a file neve
                'project_name': "",  ## ez lesz a file neve
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

    def set_project_name(self, name):
        self.data['project_name'] = name
        self.project_path = "projects/" + name + "/"

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
        self.data['X_count'] += len(array)
        if len(self.data['X']) == 0:
            self.data['X'] = array
        else:
            self.data['X'] = np.vstack((self.data['X'], array))

    def add_y(self, label):
        label = np.array([label])
        label = label.astype(int)
        label = label[0]
        # print("ybug", self.data['y'].shape, label.shape)
        # self.data['y'] = np.concatenate((self.data['y'], label))
        # self.data['y'] = np.concatenate((self.data['y'], label))
        self.data['y'] = np.append(self.data['y'], label)


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
        self.log('n_datasets-> save')
        self.set_y_unique()
        self.data['y'] = self.data['y'].reshape(-1, 1)
        self.log('  X shape: ' + str(self.data['X'].shape))
        self.log('  y shape: ' + str(self.data['y'].shape))
        if np.isnan(self.data['X']).any():
            self.log('  X nan - Error! Dataset not saved!')
            return
        else:
            self.log('  X nan - ok')

        if np.isinf(self.data['X']).any():
            self.log('  X inf - Error! Dataset not saved!')
            return
        else:
            self.log('  X inf - ok')

        if np.isnan(self.data['y']).any():
            self.log('  y nan - Error! Dataset not saved!')
            return
        else:
            self.log('  y nan - ok')

        if np.isinf(self.data['X']).any():
            self.log('  y inf - Error! Dataset not saved!')
            return
        else:
            self.log('  y inf - ok')

        y_type, y_cases = np.unique(self.data['y'],  return_counts=True)
        self.log('  y unique: ' + str(y_type) + " " + str(y_cases))
        self.log('  Historic max shape: ' + str(self.data['historic_max'].shape))
        self.log('  Historic min shape: ' + str(self.data['historic_min'].shape))
        self.data['data_fields'] = str(tuple(self.fields_dict.keys()))
        pickle.dump(self.data, open(self.gdrive_path+self.data['name']+".pickle", "wb"))
        pickle.dump(self.data, open(self.project_path+self.data['name']+".pickle", "wb"))
        self.log('n_dataset-> saved: ' + str(self.gdrive_path+self.data['name']+".pickle"))
        self.log('n_dataset-> saved: ' + str(self.project_path+self.data['name']+".pickle"))

    def load(self, file_name):
        return pickle.load(open(self.gdrive_path+file_name+'.pickle', "rb"))
