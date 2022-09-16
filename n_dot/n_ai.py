import pickle as pickle
from json import loads as json_loads, dumps as json_dumps
from re import sub as re_sub
from os import rename as os_rename, environ as os_environ, path as os_path
import numpy as np
from datetime import datetime
from shutil import copy2  # ai.download
from pathlib import Path  # dataset config beolvasóhoz kell
from time import ctime

os_environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from tensorflow.keras.models import load_model
from focal_loss import SparseCategoricalFocalLoss
# import time as time

import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf


class n_ai:
    
    def __init__(self, log, nddf, gui):
        self.nddf = nddf
        self.log = log
        self.gui = gui
        # print("itt")
        self.ai_models = {}
        self.ai_settings = {}
        self.ndot_path = "C:\\Users\\ivanh\\PycharmProjects\\nDot\\"
        self.projects_path = "C:\\Users\\ivanh\\PycharmProjects\\nDot\\projects\\"
        # self.projects_path = "C:\\Users\\honis.ivan\\PycharmProjects\\nDot\\projects\\"

        self.gdrive_path = "X:\\Apa\\cloud\\GoogleDrive\\Saját meghajtó\\nDot_Colabs\\"
        self.model_dict = {
            "MinMaxScaler": "-",
            "MinMaxScaler_last_update": 0,
            "tf_model": "-",
            "tf_model_last_update": 0,
            "predict_used_count": 0,
            "predict_average_runtime": 0,
        }

        self.settings_dict = {
            "dataset_config": {},
            "original_fields": [],
            "contras": [],
            "tech": [],
            "last_update": 0,
            "last_y_predict_datetime": 0,
            "last_y_predict_sig": 4,
            "last_y_predict_perc": 0
        }
        
        self.load()

    def set_avg_runtime(self, project, last_runtime):
        last_runtime = float(last_runtime.total_seconds())
        uc = self.ai_models[project]["predict_used_count"]
        avgrt = self.ai_models[project]["predict_average_runtime"]
        new_avg = ((uc * avgrt) + (1 * last_runtime)) / (uc + 1)
        self.ai_models[project]["predict_average_runtime"] = new_avg
        self.ai_models[project]["predict_used_count"] += 1
        
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
            
    def is_file_exist(self, path):
        file = Path(path)
        if file.exists():
            return True
        else:
            return False

    def confusion(self, predict, predict_strength,  sig):
        self.ai_log(f" ai.confusion martix", line=True)
        sig = np.array(sig)
        # predict_strength = np.array(predict_strength)
        # predict = np.array(predict)
        sig[sig == 9] = 0
        confusion_mtx = tf.math.confusion_matrix(sig[0:len(predict)], predict)
        fig = plt.figure(figsize=(5, 4))
        fig.canvas.manager.window.move(50, 250)
        sns.heatmap(confusion_mtx, xticklabels=[0, 1, 2, "off"], yticklabels=[0, 1, 2, "off"],
                    annot=True, fmt='g', cbar=False)
        plt.xlabel('Prediction')
        plt.ylabel('Label')
        plt.title('Confusion Matrix - not filtered')
        plt.show()

        # filters = [.1, .15, .2, .25, .3, .35, .4, .45, .46]
        # # filters = filters / 100
        # # print(filters)
        #
        # self.ai_log(f" Filtering y. filters: {filters}")
        # poses = (331, 332, 333, 334, 335, 336, 337, 338, 339)
        #
        # fig2 = plt.figure(figsize=(13, 6))
        # fig2.canvas.manager.window.move(600, 100)
        # for pos, filter in enumerate(filters):
        #     y_filtered = []
        #     for xy, ys in enumerate(predict_strength):
        #         if ys > filter:
        #             y_filtered.append(predict[xy])
        #         else:
        #             y_filtered.append(3)
        #
        #     confusion_mtx = tf.math.confusion_matrix(sig[0:len(predict)], y_filtered)
        #     # print(int(confusion_mtx[1][1]))
        #     plt.subplot(poses[pos])
        #
        #     sns.set(font_scale=.8)
        #     sns.heatmap(confusion_mtx, xticklabels=[0, 1, 2, "off"], yticklabels=[0, 1, 2, "off"],
        #                 annot=True, fmt='g', cbar=False)
        #     plt.xlabel('Prediction')
        #     plt.ylabel('Label')
        #     plt.title('Conf. Mtrx.:' + str(filter))
        # plt.tight_layout(pad=2, w_pad=0.5, h_pad=1.0)
        # plt.show()


        startplt = 30
        filters = np.array(range(startplt, startplt + 9))
        filters = filters / 100
        # print(filters)

        self.ai_log(f" Filtering y. filters: {filters}")
        poses = (331, 332, 333, 334, 335, 336, 337, 338, 339)

        fig2 = plt.figure(figsize=(13, 6))
        fig2.canvas.manager.window.move(600, 100)
        for pos, filter in enumerate(filters):
            y_filtered = []
            for xy, ys in enumerate(predict_strength):
                if ys > filter:
                    y_filtered.append(predict[xy])
                else:
                    y_filtered.append(3)

            confusion_mtx = tf.math.confusion_matrix(sig[0:len(predict)], y_filtered)
            # print(int(confusion_mtx[1][1]))
            plt.subplot(poses[pos])

            sns.set(font_scale=.8)
            sns.heatmap(confusion_mtx, xticklabels=[0, 1, 2, "off"], yticklabels=[0, 1, 2, "off"],
                        annot=True, fmt='g', cbar=False)
            plt.xlabel('Prediction')
            plt.ylabel('Label')
            plt.title('Conf. Mtrx.:' + str(filter))
        plt.tight_layout(pad=2, w_pad=0.5, h_pad=1.0)
        plt.show()

        # startplt = 51
        # filters = np.array(range(startplt, startplt + 9))
        # filters = filters / 100
        # # print(filters)
        #
        # self.ai_log(f" Filtering y. filters: {filters}")
        # poses = (331, 332, 333, 334, 335, 336, 337, 338, 339)
        #
        # fig2 = plt.figure(figsize=(13, 6))
        # fig2.canvas.manager.window.move(600, 100)
        # for pos, filter in enumerate(filters):
        #     y_filtered = []
        #     for xy, ys in enumerate(predict_strength):
        #         if ys > filter:
        #             y_filtered.append(predict[xy])
        #         else:
        #             y_filtered.append(3)
        #
        #     confusion_mtx = tf.math.confusion_matrix(sig[0:len(predict)], y_filtered)
        #     plt.subplot(poses[pos])
        #
        #     sns.set(font_scale=.8)
        #     sns.heatmap(confusion_mtx, xticklabels=[0, 1, 2, "off"], yticklabels=[0, 1, 2, "off"],
        #                 annot=True, fmt='g', cbar=False)
        #     plt.xlabel('Prediction')
        #     plt.ylabel('Label')
        #     plt.title('Conf. Mtrx.:' + str(filter))
        # plt.tight_layout(pad=2, w_pad=0.5, h_pad=1.0)
        # plt.show()


    def add(self, symbol, project):
        local_path_pro = self.is_file_exist(self.projects_path + project + "\\nDot_PRO_" + project + ".txt")
        local_path_minmax = self.is_file_exist(self.projects_path + project + "\\nDot_MinMaxScaler_" + project + ".pickle")
        local_path_tf = self.is_file_exist(self.projects_path + project + '\\nDot_TF_MODEL_' + project + '.h5')
        
        if local_path_pro and local_path_minmax and local_path_tf:
            
            try:
                del self.ai_settings[symbol][project]
            except KeyError as e:
                pass
            
            if symbol not in self.ai_settings.keys():
                self.ai_settings[symbol] = {}
               
            self.ai_settings[symbol][project] = self.settings_dict
            self.save()
        else:
            if not local_path_pro:
                self.ai_log("Project config file is missing")
            if not local_path_minmax:
                self.ai_log("Project MinMaxScaler file is missing")
            if not local_path_tf:
                self.ai_log("Project TF model file is missing")
    
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
        self.save()

    def remove_project(self, symbol, project):
        try:
            del self.ai_settings[symbol][project]
        except KeyError as e:
            pass
        
        if len(self.ai_settings[symbol].keys()) == 0:
            try:
                del self.ai_settings[symbol]
            except KeyError as e:
                pass
        
        self.save()
    
    def predict_multi(self, symbol, project, x):
        x_norm = self.ai_models[project]['MinMaxScaler'].transform(x)

        x_nomr_reshaped = self.x_transform(use=int(self.ai_settings[symbol][project]["dataset_config"]["x_tansform"]),
                                           x=x_norm,
                                           time_window_size=int(self.ai_settings[symbol][project]["dataset_config"]["time_window_size"]),
                                           number_of_fields=int(self.ai_settings[symbol][project]["number_of_fields"])
                                           )
        y_predict = self.ai_models[project]['tf_model'].predict(x_nomr_reshaped, verbose=0)
        y_predict_sig = np.argmax(y_predict, axis=1)
        y_predict_perc = np.take_along_axis(y_predict, np.expand_dims(y_predict_sig, axis=-1), axis=-1).squeeze(axis=-1)
        return y_predict, y_predict_sig, y_predict_perc
        
    def predict(self, symbol, project, x, datetime):
        i_start = datetime.now()
        if self.ai_settings[symbol][project]["last_y_predict_datetime"] != datetime:
            x = x.reshape(1, -1)  # tömbe teszem a tömböt
            x_norm = self.ai_models[project]['MinMaxScaler'].transform(x)
            if x_norm.max() > 1 or x_norm.min() < -1:
                self.ai_log("MinMaxScaler out of rande (-1 , 1)")

            x_nomr_reshaped = self.x_transform(use=int(self.ai_settings[symbol][project]["dataset_config"]["x_tansform"]),
                                               x=x_norm,
                                               time_window_size=int(self.ai_settings[symbol][project]["dataset_config"]["time_window_size"]),
                                               number_of_fields=int(self.ai_settings[symbol][project]["number_of_fields"])
                                               )
            
            y_predict = self.ai_models[project]['tf_model'].predict(x_nomr_reshaped)
            y_predict_sig = np.argmax(y_predict, axis=1)[0]
            y_predict_perc = y_predict[0][y_predict_sig]
            self.ai_settings[symbol][project]["last_y_predict_sig"] = y_predict_sig
            self.ai_settings[symbol][project]["last_y_predict_perc"] = y_predict_perc
            self.ai_settings[symbol][project]["last_y_predict_datetime"] = datetime
            i_return = y_predict_sig, y_predict_perc
        else:
            i_return = self.ai_settings[symbol][project]["last_y_predict_sig"], self.ai_settings[symbol][project]["last_y_predict_perc"]
        self.set_avg_runtime(project, datetime.now() - i_start)
        return i_return
        
    def ai_log(self, text, line=False):
        self.gui.ailog(text, line=line)
        # print(text)
        
    def build(self):
        used_projects = []
        for i_symbol in self.ai_settings:
            # print(i_symbol)
            for i_project in self.ai_settings[i_symbol]:
                # print(i_project)
                local_path = self.projects_path + i_project + "\\nDot_PRO_" + i_project + ".txt"
                if self.ai_settings[i_symbol][i_project]["last_update"] != os_path.getmtime(local_path):
                    gdc_ok, description, dataset_config, original_fields, contras, tech = self.get_dataset_config(local_path)
                    self.ai_settings[i_symbol][i_project]["dataset_config"] = dataset_config
                    self.ai_settings[i_symbol][i_project]["original_fields"] = original_fields
                    self.ai_settings[i_symbol][i_project]["contras"] = contras
                    self.ai_settings[i_symbol][i_project]["tech"] = tech
                    self.ai_settings[i_symbol][i_project]["last_update"] = os_path.getmtime(local_path)
                    self.ai_settings[i_symbol][i_project]["number_of_fields"] = len(self.ai_settings[i_symbol][i_project]["original_fields"]) + \
                                                                                len(self.ai_settings[i_symbol][i_project]["contras"])

                # init norm model from local drive
                local_path = self.projects_path + i_project + "\\nDot_MinMaxScaler_" + i_project + ".pickle"
                if i_project not in self.ai_models:
                    # self.ai_models[i_project] = {}
                    self.ai_models[i_project] = self.model_dict.copy()
                
                # print('MLUPD: ',self.ai_models[i_project]["MinMaxScaler_last_update"], os_path.getmtime(local_path))
                
                if self.ai_models[i_project]["MinMaxScaler_last_update"] != os_path.getmtime(local_path):
                    self.ai_log(f"MinMaxScaler model has been set: {i_project}", line=True)
                    self.ai_models[i_project]["MinMaxScaler"] = pickle.load(open(local_path, "rb"))
                    self.ai_models[i_project]["MinMaxScaler_last_update"] = os_path.getmtime(local_path)

                # init tf_model fromlocl drive
                local_path = self.projects_path + i_project + '\\nDot_TF_MODEL_' + i_project + '.h5'
                # print('TFLMUP: ',self.ai_models[i_project]["tf_model_last_update"], os_path.getmtime(local_path))
                if self.ai_models[i_project]["tf_model_last_update"] != os_path.getmtime(local_path):
                    self.ai_log(f"tf_model has been set: {i_project}")
                    self.ai_models[i_project]["tf_model"] = load_model(local_path)
                    self.ai_models[i_project]["tf_model_last_update"] = os_path.getmtime(local_path)
                
                used_projects.append(i_project)
        
        # print("used_projects ", used_projects)
        # delete all unused projects
        for allp in self.ai_models:
            if allp not in used_projects:
                del self.ai_models[allp]
                
        # print(self.ai_models)
            
    def get_project_config(self, project):
        local_path = self.projects_path + project + "\\nDot_PRO_" + project + ".txt"
        # print(local_path)
        return self.get_dataset_config(local_path)

    def get_dataset_config(self, config_file_path):
    
        file = Path(config_file_path)
        if file.exists():
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
    
            try:
                indexes = json_loads(clear_string(contents[4]))
            except ValueError:
                indexes = []
                ok = False
        else:
            self.ai_log("Project config file is not found.")
            ok = False
            description = ""
            dataset_config = {}
            original_fields = []
            contras = []
            indexes = []

        return ok, description, dataset_config, original_fields, contras, indexes
        
    def print(self):
        print(json_dumps(self.ai_settings, sort_keys=False, indent=6))
        print(self.ai_models)
        
    def get_all_indicators_by_symbols(self):
        i_symbols = tuple(self.nddf.keys())
        result_dict = {}
        for smb in i_symbols:
            i_project = self.get_projects_by_symbol(smb)
            indexes_array = []
            for i in i_project:
                # print(i)
                ok, description, dataset_config, original_fields, contras, indexes = self.get_project_config(i)
                # print(indexes)
                indexes_array = indexes_array + indexes
            if len(indexes_array) > 0:
                result_dict[smb] = set(indexes_array)
        # print(result_dict)
        return result_dict
        
    def download(self, project_name, rename):
        # rename existing file
        if rename == "rename":
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
            path_2 = self.projects_path + project_name + "\\nDot_MinMaxScaler_" + project_name + "_" + i_now + ".pickle"
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
            self.ai_log(f"Last modified: {ctime(os_path.getmtime(from_path))}")
    
        # copy normal model
        from_path = self.gdrive_path + "nDot_MinMaxScaler_" + project_name + ".pickle"
        try:
            copy2(from_path, to_path)
        except FileNotFoundError as e:
            self.ai_log(f"{project_name} - Norm model not found.")
        else:
            self.ai_log(f"{project_name} - Norm model downloaded.")
            self.ai_log(f"Last modified: {ctime(os_path.getmtime(from_path))}")


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
