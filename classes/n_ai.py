import pickle as pickle
from json import loads as json_loads, dumps as json_dumps
from re import sub as re_sub
from os import rename as os_rename, environ as os_environ, path as os_path
import numpy as np
from datetime import datetime
from shutil import copy2  # ai.download

os_environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from tensorflow.keras.models import load_model
# import time as time


class n_ai:
    
    def __init__(self):
        # print("itt")
        self.ai_models = {}
        self.ai_settings = {}
        self.ndot_path = "C:\\Users\\honis.ivan\\PycharmProjects\\nDot\\"
        self.projects_path = "C:\\Users\\honis.ivan\\PycharmProjects\\nDot\\projects\\"
        self.gdrive_path = "C:\\Users\\honis.ivan\\Google Drive\\nDot_Colabs\\"
        self.model_dict = {
            "MinMaxScaler": "",
            "MinMaxScaler_last_update": 0,
            "tf_model": "",
            "tf_model_last_update": 0,
            "last_y_predict_datetime": 0,
            "last_y_predict_sig": 4,
            "last_y_predict_perc": 4
        }

        self.settings_dict = {
            "dataset_config": {},
            "original_fields": [],
            "contras": [],
            "last_update": 0
        }
        
        self.load()
        
    def save(self):
        with open(self.ndot_path + 'ai_settings.pickle', 'wb') as f:
            pickle.dump(self.ai_settings, f)
    
    def load(self):
        try:
            with open(self.ndot_path + 'ai_settings.pickle', 'rb') as f:
                self.ai_settings = pickle.load(f)
        except FileNotFoundError:
            self.ai_settings = {}
        # finally:
        #     self.print()
    
    def x_transform(self, use, x, **kwargs):
        if use == 1:
            x_np_mod = np.array(x)
            x_np_mod_reshaped = np.reshape(x_np_mod, (x_np_mod.shape[0], kwargs['time_window_size'], kwargs['number_of_fields']))
            return x_np_mod_reshaped
        elif use == 2:
            pass
        else:
            self.ai_log("X_transfom is out of range.")
    
    def add(self, symbol, project):
        try:
            del self.ai_models[symbol][project]
        except KeyError as e:
            pass

        try:
            del self.ai_settings[symbol][project]
        except KeyError as e:
            pass
        
        if symbol not in self.ai_settings.keys():
            self.ai_settings[symbol] = {}
            self.ai_models[symbol] = {}
            
        # if project not in self.ai_settings[symbol].keys():
        #     self.ai_settings[symbol][project] = self.settings_dict
        #     self.ai_models[symbol][project] = self.model_dict
        self.ai_settings[symbol][project] = self.settings_dict
        self.save()
    
    def get(self, symbol, project, field):
        if symbol in self.ai_settings and project in self.ai_settings[symbol] and field in self.ai_settings[symbol][project]:
            return self.ai_settings[symbol][project][field]
        else:
            return "semmi"
   
    # def get_model(self, symbol, project, field):
    #     if symbol in self.ai_models.keys() and project in self.ai_models[symbol].keys() and field in self.ai_models[symbol][project].keys():
    #         return self.ai_models[symbol][project][field]
    #     else:
    #         return ""
   
    def get_projects_by_symbol(self, symbol):
        if symbol in self.ai_settings:
            return self.ai_settings[symbol].keys()
        else:
            return ""
        
    def remove_symbol(self, symbol):
        try:
            del self.ai_settings[symbol]
        except KeyError as e:
            pass
        
        try:
            del self.ai_models[symbol]
        except KeyError as e:
            pass
        self.save()

    def remove_project(self, symbol, project):
        try:
            del self.ai_settings[symbol][project]
        except KeyError as e:
            pass
        
        try:
            del self.ai_models[symbol][project]
        except KeyError as e:
            pass
        
        if len(self.ai_settings[symbol].keys()) == 0:
            try:
                del self.ai_settings[symbol]
            except KeyError as e:
                pass
            
            try:
                del self.ai_models[symbol]
            except KeyError as e:
                pass
        
        self.save()
    
    def predict(self, symbol, project, x, datetime):
        if self.ai_models[symbol][project]["last_y_predict_datetime"] != datetime:
            x = x.reshape(1, -1)  # tömbe teszem a tömböt
            x_norm = self.ai_models[symbol][project]['MinMaxScaler'].transform(x)
            time_window_size = int(self.ai_settings[symbol][project]["dataset_config"]["time_window_size"])
            x_tansform = int(self.ai_settings[symbol][project]["dataset_config"]["x_tansform"])
            number_of_fields = int(self.ai_settings[symbol][project]["number_of_fields"])
            x_nomr_reshaped = self.x_transform(x_tansform, x_norm,time_window_size=time_window_size, number_of_fields=number_of_fields)
            y_predict = self.ai_models[symbol][project]['tf_model'].predict(x_nomr_reshaped)
            y_predict_sig = np.argmax(y_predict, axis=1)[0]
            y_predict_perc = y_predict[0][y_predict_sig]
            self.ai_models[symbol][project]["last_y_predict_sig"] = y_predict_sig
            self.ai_models[symbol][project]["last_y_predict_perc"] = y_predict_perc
            self.ai_models[symbol][project]["last_y_predict_datetime"] = datetime
            return y_predict_sig, y_predict_perc
        else:
            return self.ai_models[symbol][project]["last_y_predict_sig"], self.ai_models[symbol][project]["last_y_predict_perc"]

    def ai_log(self, text):
        print(text)
        
    def build(self):
        for i_symbol in self.ai_settings:
            for i_project in self.ai_settings[i_symbol]:
                local_path = self.projects_path + i_project + "\\nDot_PRO_" + i_project + ".txt"
                if self.ai_settings[i_symbol][i_project]["last_update"] != os_path.getmtime(local_path):
                    gdc_ok, description, dataset_config, original_fields, contras = self.get_dataset_config(local_path)
                    self.ai_settings[i_symbol][i_project]["dataset_config"] = dataset_config
                    self.ai_settings[i_symbol][i_project]["original_fields"] = original_fields
                    self.ai_settings[i_symbol][i_project]["contras"] = contras
                    self.ai_settings[i_symbol][i_project]["last_update"] = os_path.getmtime(local_path)
                    self.ai_settings[i_symbol][i_project]["number_of_fields"] = len(self.ai_settings[i_symbol][i_project]["original_fields"]) + \
                                                                                len(self.ai_settings[i_symbol][i_project]["contras"])

                # init norm model from local drive
                local_path = self.projects_path + i_project + "\\nDot_MinMaxScaler_" + i_project + ".pickle"
                if i_symbol not in self.ai_models:
                    self.ai_models[i_symbol] = {}
                    
                if i_project not in self.ai_models[i_symbol]:
                    self.ai_models[i_symbol][i_project] = self.model_dict
                
                if self.ai_models[i_symbol][i_project]["MinMaxScaler_last_update"] != os_path.getmtime(local_path):
                    self.ai_models[i_symbol][i_project]["MinMaxScaler"] = pickle.load(open(local_path, "rb"))
                    self.ai_models[i_symbol][i_project]["MinMaxScaler_last_update"] = os_path.getmtime(local_path)

                # init tf_model fromlocl drive
                local_path = self.projects_path + i_project + '\\nDot_TF_MODEL_' + i_project + '.h5'
                if self.ai_models[i_symbol][i_project]["tf_model_last_update"] != os_path.getmtime(local_path):
                    self.ai_models[i_symbol][i_project]["tf_model"] = load_model(local_path)
                    self.ai_models[i_symbol][i_project]["tf_model_last_update"] = os_path.getmtime(local_path)

    def get_project_config(self, project):
        local_path = self.projects_path + project + "\\nDot_PRO_" + project + ".txt"
        return self.get_dataset_config(local_path)

    def get_dataset_config(self, config_file_path):
        ok = True
        # ez nem vizsgálja, hogy létezik e file, ezt hívás előtt kell

        def clear_string(contents, space=True):
            if space:
                contents = contents.replace(" ", "")
            contents = contents.replace('\n', '').replace('\r', '')
            contents = re_sub('<.*?>', '', contents)
            if contents[-2:] == ",]":
                contents = contents[:-2] + "]"
            return contents

        with open(config_file_path) as f:
            contents = f.read()
        contents = contents.split(";")
        description = clear_string(contents[0], space=False)

        try:
            dataset_config = json_loads(clear_string(contents[1]))
        except ValueError:
            dataset_config = []
            ok = False

        try:
            original_fields = json_loads(clear_string(contents[2]))
        except ValueError:
            original_fields = []
            ok = False

        try:
            contras = json_loads(clear_string(contents[3]))
        except ValueError:
            contras = []
            ok = False

        return ok, description, dataset_config, original_fields, contras
        
    def print(self):
        print(json_dumps(self.ai_settings, sort_keys=False, indent=6))
        print(self.ai_models)
        
    def download(self, project_name):
        # rename existing file
        i_now = str(datetime.now()).replace("-", "_").replace(":", "_").replace(".", "_").replace(" ", "_")
    
        path_1 = self.projects_path + project_name + "\\nDot_TF_MODEL_" + project_name + ".h5"
        path_2 = self.projects_path + project_name + "\\nDot_TF_MODEL_" + project_name + "_" + i_now + ".h5"
        try:
            os_rename(path_1, path_2)
        except FileNotFoundError as e:
            pass
        else:
            self.ai_log(f"{project_name} - Acctual TensorFlow model has renamed id: " + i_now)
    
        path_1 = self.projects_path + project_name + "\\nDot_MinMaxScaler_" + project_name + ".pickle"
        path_2 = self.projects_path + + project_name + "\\nDot_MinMaxScaler_" + project_name + "_" + i_now + ".pickle"
        try:
            os_rename(path_1, path_2)
        except FileNotFoundError as e:
            pass
        else:
            self.ai_log(f"{project_name} - Acctual MinMaxScaler model has renamed id: " + i_now)
    
        to_path = self.projects_path + project_name
    
        # copy modell
        from_path = self.gdrive_path + "nDot_TF_MODEL_" + project_name + ".h5"
        try:
            copy2(from_path, to_path)
        except FileNotFoundError as e:
            self.ai_log(f"{project_name} - TensorFlow model not found.")
        else:
            self.ai_log(f"{project_name} - TensorFlow model downloaded.")
    
        # copy normal model
        from_path = self.projects_path + "nDot_MinMaxScaler_" + project_name + ".pickle"
        try:
            copy2(from_path, to_path)
        except FileNotFoundError as e:
            self.ai_log(f"{project_name} - Norm model not found.")
        else:
            self.ai_log(f"{project_name} - Norm model downloaded.")


if __name__ == "__main__":
    
    ai = n_ai()
    ai.add("APA", "APA_SMA5813")
    ai.add("PLAY", "APA_SMA5813")
    print("-"*80)
    ai.build()
    # print(ai.get("APA", "APA_SMA5813", "dataset_config"))
    # print(ai.get_model("APA", "APA_SMA5813", "MinMaxScaler"))
    print("-"*80)
    ai.build()
    # print(ai.get("APA", "APA_SMA5813", "dataset_config"))
    # print(ai.get_model("APA", "APA_SMA5813", "MinMaxScaler"))
    # ai.x_transforms(1,1,time_window_size=1, number_of_fields=2)
    
    print(ai.print())
