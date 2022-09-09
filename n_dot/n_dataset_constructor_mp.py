import sys
import pandas as pd
import numpy as np


class n_dataset_constructor_mp:
    
    def __init__(self, param_mp):
        self.temp_path = "C:\\Users\\ivanh\\PycharmProjects\\nDot\\temp\\"
        self.cores = param_mp['cores']  # összesen hány process van
        self.process = param_mp['process']  # én hanyadik process vagyok
        self.mpi = str(self.process + 1) + "/" + str(self.cores) + " core ->"
        if self.process == 7:
            print(self.mpi, "start multiprocessing dataset_constuctor. Last speak.")
        self.dataset_constructor(param_mp)

    def get_dataset_by_index(self, symbol, index, time_window_size, original_fields,
                             contras, contra_copies_dt, nddf):
    
        i_int_to = int(index)
        i_int_from = i_int_to - time_window_size + 1
        # print(nddf[symbol]["Date"][i_int_to:i_int_to + 1])
        # sys.exit(0)
    
        i_data_array = np.array([])
        if i_int_from > 0:
            if len(original_fields) > 0:
                for i_of in original_fields:
                    i_add = np.array(nddf[symbol][i_of][i_int_from:i_int_to + 1])
                    i_data_array = np.append(i_data_array, i_add)
        
            if len(contras) > 0:
                for i_con in contras:
                    contra_sep_pre = i_con.split('_')
                    con_sep = []
                    if len(contra_sep_pre) > 2:
                        con_sep.append(contra_sep_pre[0])
                        s = "_"
                        con_sep.append(s.join(contra_sep_pre[1:]))
                    else:
                        con_sep = contra_sep_pre
                
                    con_symbol = con_sep[0]
                    con_field = con_sep[1]
                
                    orig_date = nddf[symbol]["Date"][index:index + 1].values[0]
                    try:
                        i_int_to_contra = np.where(contra_copies_dt[con_symbol] == orig_date)[0][0]
                    except:
                        return np.array([])
                
                    i_int_from_contra = i_int_to_contra - time_window_size + 1
                    i_new = np.array(nddf[con_symbol][con_field][i_int_from_contra:i_int_to_contra + 1])
                    i_data_array = np.append(i_data_array, i_new)
        return i_data_array
    
    def dataset_constructor(self, params):
        symbol = params['symbol']
        indexes = params['indexes']
        time_window_size = params['time_window_size']
        y = params['y']
        original_fields = params['original_fields']
        contras = params['contras']
        back_shift = params['back_shift']
        contra_copies_dt = params['contra_copies_dt']
        nddf = params['nddf']
        gap_manager = params['gap_manager']

        array_len = time_window_size * (len(original_fields) + len(contras))
        
        asked = 0
        recieved = 0
        X_array = np.array([])
        y_array = np.array([])
        last_X = []
        gap_manager_count = 0
        for nx, i_il in enumerate(indexes):
            asked += 1
            
            i_data_array = self.get_dataset_by_index(symbol=symbol,
                                                     index=i_il + back_shift,
                                                     # :) predict in the present, but trade in the future
                                                     time_window_size=time_window_size,
                                                     original_fields=original_fields,
                                                     contras=contras,
                                                     contra_copies_dt=contra_copies_dt,
                                                     nddf=nddf)

            if not np.isnan(i_data_array).any() \
                    and array_len == len(i_data_array) \
                    and np.isfinite(i_data_array).all():
                recieved += 1
                if len(X_array) == 0:
                    X_array = i_data_array
                else:
                    X_array = np.vstack((X_array, i_data_array))
                y_array = np.append(y_array, y)
            elif gap_manager == "empty":
                gap_manager_count += 1
                if len(X_array) == 0:
                    X_array = np.array([0] * array_len)
                else:
                    X_array = np.vstack((X_array, np.array([0] * array_len)))
                y_array = np.append(y_array, 9)
            elif gap_manager == "last":
                gap_manager_count += 1
                if len(X_array) == 0:
                    X_array = last_X
                else:
                    X_array = np.vstack((X_array, last_X))
                y_array = np.append(y_array, y)
            elif gap_manager == "drop":
                gap_manager_count += 1

            last_X = i_data_array

            if nx % 1000 == 0:
                if self.process == 7:
                    print(f"{self.mpi} {len(indexes)} / {nx} gaps: {gap_manager_count}")
                    # print(X_array)
        if gap_manager_count > 0:
            print(f"{self.mpi} gaps: {gap_manager_count}")
        file_name = self.temp_path + 'DATASET_DATACONSTRUCTOR_X_RESULTS' + str(self.process)
        np.save(file_name, X_array)
        file_name = self.temp_path + 'DATASET_DATACONSTRUCTOR_y_RESULTS' + str(self.process)
        np.save(file_name, y_array)
    

if __name__ == '__main__':
    pass
