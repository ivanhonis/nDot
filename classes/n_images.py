import pickle
import datetime

class n_images():

    def __init__(self, log):
        self.log = log
        self.gdrive_path = "C:/Users/honis.ivan/Google Drive/nDot_Colabs/"
        self.data = {
                'name': "",  ## ez lesz a file neve
                'timestamp': "",  ## mikor készültek az adatok
                'source': "",  ## melyik eljárás milyen paraméterekkel állította elő
                'symbol': "",  ## melyik érszvényhez készült
                'description': "",  ## magyarázat mit volt az ötlet
                'images': {},  ## ezek az adat csomagok
                'images_count': 0,  ## hány adatcsomagot tartalmaz
                'target_names': {},  ## a targetek értelmezése
                'meta': "",  ## a good minták milyen beállításokkal keletkeztek
                'historic_max': {} ## az adatok egységes normalizálásoh a történelmi maximum értékek
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

    def add_target_names(self, target_names):
        self.data['target_names'] = target_names

    def set_historic_max(self, historic_max):
        self.data['historic_max'] = historic_max

    def add_image(self, dict, target):
        dict['target'] = target
        self.data['images'][self.data['images_count']] = {}
        self.data['images'][self.data['images_count']] = dict
        self.data['images_count'] += 1

    def save(self):
        self.log('n_images->save: ' + str(self.data['images_count']))
        pickle.dump(self.data, open(self.gdrive_path+self.data['name']+".pickle", "wb"))
        self.log('n_images->saved: ' + str(self.gdrive_path+self.data['name']+".pickle"))

    def load(self, file_name):
        return pickle.load(open(self.gdrive_path+file_name+'.pickle', "rb"))


if __name__ == "__main__":
    n_image = n_images()

    n_image.set_name("APA_v01")
    n_image.set_symbol("APA")
    n_image.set_source("chart.py proto project V0.0")
    n_image.set_description("APA description")

    dict = {}
    dict['close'] = [1, 2, 3]
    dict['open'] = [1, 2, 3]

    n_image.add_image(dict, "q1")
    n_image.add_image(dict, "q2")

    t_names = {}
    t_names['q1'] = "Good LONG signal"
    t_names['q2'] = "Good SHORT signal"
    t_names['q3'] = "Bad LONG signal"
    t_names['q4'] = "Bad SHORT signal"
    n_image.add_target_names(t_names)

    # TESZT -------------------------------------------------------
    i_data = n_image.data
    print(i_data.__dict__)

    n_image.save()

    i_data2 = n_image.load("APA_V01.pickle")
    print('-----------------------------------------------------------')
    print(i_data2.__dict__)
    print(i_data2.name)
    print(i_data2.images[0]['close'][1])