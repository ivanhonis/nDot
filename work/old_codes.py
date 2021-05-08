# def find_first_signal(symbol, col, new_col, n):
#     log(f"ndf->add_tech->find_first_signal on {col}")
#     i_good_signals = 0
#
#     def find_pattern(df):
#         nonlocal i_good_signals
#         i_o = tuple([1.0])
#         i_z = tuple([0.0])
#         i_pattern = i_z + (i_o * (n - 1))
#         i_data = tuple(df)
#         # print(i_pattern, i_data)
#         if i_pattern == i_data:
#             i_return = True
#             i_good_signals += 1
#         else:
#             i_return = False
#         return i_return
#
#     nddf[symbol][new_col] = nddf[symbol][col] \
#         .rolling(window=n, center=False) \
#         .apply(lambda x: find_pattern(x)) \
#         .astype(bool)
#
#     log(f"  Result: {i_good_signals}")
#
#
# def check_signal_overlay(symbol, column_name, overlay_window=45):
#     log(f"ndf-> add_tech-> check_signal_overlay {symbol} {column_name} {overlay_window}")
#     self.case_set_back(symbol)
#     i_basis_signal_position = 0
#     i_signal_count = 0
#     i_del_overlay = 0
#     i_del_over_time = 0
#
#     df_len = len(tuple(nddf[symbol][column_name]))
#
#     for i_i in range(1, df_len):
#         if i_i / 1000 == int(i_i / 1000):
#             s(str(round(i_i / df_len * 100, 2)) + " %")
#         if nddf[symbol].iloc[i_i][column_name]:
#             i_signal_count += 1
#
#             i_Date = nddf[symbol].iloc[i_i]['Date']  # a signálnak kell elég idő zárás előtt 45 perc, hogy kifusson
#
#             if tools.is_date_in_timeperiod(dt_time(16, 20), dt_time(21, 15), i_Date):
#                 i_signal_distnace = i_i - i_basis_signal_position
#                 if i_signal_distnace < overlay_window:
#                     i_del_overlay += 1
#                     nddf[symbol].loc[i_i, column_name] = False
#                 else:
#                     i_basis_signal_position = i_i
#             else:
#                 i_del_over_time += 1
#                 nddf[symbol].loc[i_i, column_name] = False
#
#     log(f"  Result: Total / overlay / over time: {i_signal_count} / {i_del_overlay} / {i_del_over_time} Checked signals: {i_signal_count - i_del_overlay - i_del_over_time}")
#     s("")
#
#
# def qualify_signal(symbol, col, new_col, side, qualify_config):
#     i_len_df = len(tuple(nddf[symbol][col]))
#
#     tech_qualify_block_size = qualify_config['tech_qualify_block_size']
#     tech_qualify_min_profit = qualify_config['tech_qualify_min_profit']
#     tech_qualify_stop = qualify_config['tech_qualify_stop']
#     tech_qualify_max_steps = qualify_config['tech_qualify_max_steps']
#
#     log(f"ndf->add_tech->qualify_signal: {side} {tech_qualify_block_size} USD p/s:"
#         f"{tech_qualify_min_profit}/{tech_qualify_stop} steps:{tech_qualify_max_steps}")
#
#     # print(tech_qualify_stop)
#     # print(tech_qualify_min_profit)
#     # print(tech_qualify_block_size)
#     # print(tech_qualify_max_steps)
#
#     i_all_signals = 0
#     i_good_signals = 0
#
#     def qualify(df):
#         nonlocal i_all_signals, i_good_signals, i_len_df
#         i_pattern = tuple([1.0])
#         i_data = tuple(df)
#         if i_pattern == i_data:
#             i_all_signals += 1
#             i_start_index = df.index.values.astype(int)[0]
#             if i_start_index / 10 == int(i_start_index / 10):
#                 s(str(round(i_start_index / i_len_df * 100, 2)) + " %")
#             i_start_ohlc4 = nddf[symbol].loc[[i_start_index]].ohlc4.values[0]
#             i_qty = int(tech_qualify_block_size / i_start_ohlc4)
#             i_i = 1
#             i_profit = 0
#             i_stop = False
#             # print('----------------------------')
#             # i_date = nddf[symbol].loc[[i_start_index + i_i]].Date.values[0]
#             # i_act_ohlc4 = nddf[symbol].loc[[i_start_index + i_i]].ohlc4.values[0]
#             # print(i_i, ' Profit: ', i_profit, "Date: ", i_date, " Act price: ", i_act_ohlc4, "Side: ", side)
#             while i_i < tech_qualify_max_steps and i_profit < tech_qualify_min_profit and not i_stop and \
#                     nddf[symbol].shape[0] > i_start_index + i_i:
#                 # print(nddf[symbol].shape, i_start_index + i_i)
#                 i_act_ohlc4 = nddf[symbol].loc[[i_start_index + i_i]].ohlc4.values[0]
#
#                 # print(i_start_ohlc4, i_act_ohlc4)
#                 if side == 'LONG':
#                     i_profit = int((i_act_ohlc4 - i_start_ohlc4) * i_qty)
#                 else:
#                     i_profit = int((i_start_ohlc4 - i_act_ohlc4) * i_qty)
#                 # print(i_i, ' Profit: ', i_profit, "Date: ", i_date," Act price: ", i_act_ohlc4 )
#                 if i_profit < tech_qualify_stop:
#                     i_stop = True
#                     # print('Stop')
#                 i_i += 1
#             if i_profit > tech_qualify_min_profit:
#                 i_return = True
#                 i_good_signals += 1
#             else:
#                 i_return = False
#
#             # i_date = nddf[symbol].loc[[i_start_index + i_i]].Date.values[0]
#             # i_act_ohlc4 = nddf[symbol].loc[[i_start_index + i_i]].ohlc4.values[0]
#             # print(i_i, ' Profit: ', i_profit, "Date: ", i_date, " Act price: ", i_act_ohlc4, "Side: ", side)
#         else:
#             i_return = False
#         return i_return
#
#     nddf[symbol][new_col] = nddf[symbol][col] \
#         .rolling(window=1, center=False) \
#         .apply(lambda x: qualify(x)) \
#         .astype(bool)
#     s("")
#     # save settings for qualification signals ---------------------------------------------------------------
#     ndf_meta.add_meta_key(symbol, new_col, qualify_config)
#     log(f"  Result: all/good: {i_all_signals}/{i_good_signals}  {round(i_good_signals / i_all_signals * 100, 2)}%")
#     return
#
#
# def add_to_nddf(symbol, df, col):
#     i_df_temp = nddf[symbol].copy()
#     # print("1--------------------------------------")
#     # print(i_df_temp.head(3))
#     i_df_temp.drop([col], axis=1, errors='ignore', inplace=True)
#     # print("2--------------------------------------")
#     # print(i_df_temp.head(3))
#     i_df_temp = i_df_temp.set_index('t').join(df.set_index('t')[col])
#     # print("3--------------------------------------")
#     # print(i_df_temp.head(3))
#     i_df_temp.reset_index(drop=False, inplace=True)
#     # print("4--------------------------------------")
#     # print(i_df_temp.head(3))
#     i_df_temp.drop_duplicates('t', keep='last', inplace=True)
#     # print("5--------------------------------------")
#     # print(i_df_temp.head(3))
#     i_df_temp.sort_values(by=['t'], inplace=True, ascending=True)
#     # print("6--------------------------------------")
#     # print(i_df_temp.head(3))
#     i_df_temp.reset_index(drop=True, inplace=True)
#     i_df_temp[col].fillna(False, inplace=True)
#     # print("7--------------------------------------")
#     # print(i_df_temp.head(3))
#     nddf[symbol][col] = i_df_temp[col]


# # Segéd függvények Bármelyik image készítő használhatja --------------------------------------------------
# def time_gap_section(symbol, i_il,
#                      time_frame_size):  ## egy számsor állít elő ha van benne szünet akkor kihagy egy számot
#
#     i_int_to = int(i_il)
#     i_int_from = i_int_to - time_frame_size + 1
#     time_data = tuple(nddf[symbol].loc[i_int_from:i_int_to, 'Date'])
#     base = time_data[0]
#     time_gap = []
#     for i_td in time_data:
#         time_gap.append((i_td - base).total_seconds() / 60)
#     # print(time_gap)
#
#     i_int_to = int(i_il)
#     i_int_from = i_int_to - time_frame_size + 1
#     time_data = tuple(nddf[symbol].loc[i_int_from:i_int_to, 'Date'])
#     base = time_data[0]
#     base_mod = datetime(base.year, base.month, base.day, 0, 0, 0)
#     # print(base_mod)
#     time_section = []
#     for i_td in time_data:
#         time_section.append(round(((i_td - base_mod).total_seconds() / 60) / 758, 6))
#     # print(time_section)
#
#     return tuple(time_gap), tuple(time_section)

# def create_images(self, symbol, images_for, contras):
#
#     contras = contras.split(',')
#
#     # image fej megcsinálása, minden image nél ugyan az
#     n_img = ""
#     n_img = n_images(log)
#     n_img.set_symbol(symbol)
#     n_img.set_source("nDot.py->n_data_frame2->create_images <ICX1>")
#     n_img.set_name("nDot_DATASET_" + symbol + "_" + images_for)
#
#     # Segéd függvények Bármelyik image készítő használhatja --------------------------------------------------
#     def time_gap_section(symbol, i_il, time_frame_size):  ## egy számsor állít elő ha van benne szünet akkor kihagy egy számot
#
#         i_int_to = int(i_il)
#         i_int_from = i_int_to - time_frame_size + 1
#         time_data = tuple(nddf[symbol].loc[i_int_from:i_int_to, 'Date'])
#         base = time_data[0]
#         time_gap = []
#         for i_td in time_data:
#             time_gap.append((i_td - base).total_seconds() / 60)
#         # print(time_gap)
#
#         i_int_to = int(i_il)
#         i_int_from = i_int_to - time_frame_size + 1
#         time_data = tuple(nddf[symbol].loc[i_int_from:i_int_to, 'Date'])
#         base = time_data[0]
#         base_mod = datetime(base.year, base.month, base.day, 0, 0, 0)
#         # print(base_mod)
#         time_section = []
#         for i_td in time_data:
#             time_section.append(round(((i_td - base_mod).total_seconds() / 60)/758,6))
#         # print(time_section)
#
#         return tuple(time_gap), tuple(time_section)
#
#     def array_diff(from_array, this_array):  ## from arrayból eltávolitja a this_arrayt
#         for i_nx in this_array:
#             if i_nx in from_array:
#                 from_array.remove((i_nx))
#         return from_array
#
#     def array_random_select(from_array, no):
#         no = min(no, len(from_array))
#         return random.choices(from_array, k=no)
#
#     # def r_v(i_tuple):  ## relative view, a szignálkori értéket veszi 1 nek és visszafelé abból számolja 0,9 - 1,1 stb
#     #     mod_array = []
#     #     last = i_tuple[len(i_tuple) - 1]
#     #     for i_t in i_tuple:
#     #         mod_array.append(round(i_t / last, 6))
#     #     return mod_array
#
#     contra_ok = True
#     if len(contras[0]) > 0:
#         for con in contras:
#             if not ndf.is_contra(con):
#                 log("Contra symbol or field is wrong: " + str(con))
#                 contra_ok = False
#
#     if contra_ok:
#         # image törzs létrehozása
#         if images_for == 'ICHIMOKU':
#
#             time_frame_size = 45  # a indikátortól visszafelé hány percet tegyen az image-ba
#
#             ### minden image kreátornak saját konstruktora van, ahány stratégiától függően mást teszek bele
#             def images_constructor(symbol, indexes, time_frame_size, q):
#                 # print("indexes", len(indexes))
#
#                 for i_il in indexes:
#                     i_int_to = int(i_il)
#                     i_int_from = i_int_to - time_frame_size + 1
#
#                     if i_int_from > 0:
#                         time_gap, time_section = time_gap_section(symbol, i_il, time_frame_size)
#                         # print(time_section)
#                         i_cmo = nddf[symbol].loc[i_int_from:i_int_to, 'Close'] - nddf[symbol].loc[i_int_from:i_int_to, 'Open']
#                         i_hml = nddf[symbol].loc[i_int_from:i_int_to, 'High'] - nddf[symbol].loc[i_int_from:i_int_to, 'Low']
#
#
#                         i_data_dict = {
#                             # 'ohlc4': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'ohlc4']),
#                             # 'Low': r_v(tuple(nddf[symbol].loc[i_int_from:i_int_to, 'Low'])),
#                             # 'High': r_v(tuple(nddf[symbol].loc[i_int_from:i_int_to, 'High'])),
#                             # 'Open': r_v(tuple(nddf[symbol].loc[i_int_from:i_int_to, 'Open'])),
#                             # 'Close': r_v(tuple(nddf[symbol].loc[i_int_from:i_int_to, 'Close'])),
#                             # 'ADX_8_ONE': r_v(tuple(nddf[symbol].loc[i_int_from:i_int_to, 'ADX_8_ONE'])),
#                             # 'Close-Open': tuple(i_cmo),
#                             # 'High-Low': tuple(i_hml),
#                             'High': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'High']),
#                             'Low': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'Low']),
#                             # 'Close': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'Close']),
#                             'ADX_8_ONE': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'ADX_8_ONE']),
#                             # 'RSI_14': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'RSI_14']),
#                             # 'MSFT_High': tuple(nddf['MSFT'].loc[i_int_from:i_int_to, 'High']),
#                             # 'MSFT_Low': tuple(nddf['MSFT'].loc[i_int_from:i_int_to, 'Low']),
#                             'MSFT_ohlc4': tuple(nddf['MSFT'].loc[i_int_from:i_int_to, 'ohlc4']),
#                             # 'MSFT_RSI14': tuple(nddf['MSFT'].loc[i_int_from:i_int_to, 'RSI_14']),
#
#                             # 'DMP_8': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'DMP_8']),
#                             # 'DMN_8': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'DMN_8']),
#                             # 'Volume': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'Volume']),
#                             # 'time_gap': time_gap,
#                             # 'time_section': time_section,
#                                        }
#                         n_img.add_image(i_data_dict, q)
#
#             i_indicators_need = ['ICHIMOKU', 'ADX8', 'RSI14']
#             if self.check_indicators(symbol, i_indicators_need):
#
#                 n_img.set_description("""
#                 Ötlet: Ichimoku szignálok közül kiválasztottam 'good' teljesítményüeket.
#                 ezek előtti bekövetkezése előtti 45 percet(ticket) kiszedem és megpróbálom bennük felfedeztetni a közöset
#                 ha sikerül akkor ezzel tudom erősítem az indikátort
#                 """)
#
#                 target_names = {'1': "Good LONG signal",
#                                 '2': "Good SHORT signal",
#                                 '3': "Bad LONG signal",
#                                 '4': "Bad SHORT signal"
#                                 }
#
#                 n_img.add_target_names(target_names)
#
#                 #  beteszem a 'good' Longokat -----------------------------------------
#                 i_index_long = (tuple(nddf[symbol].loc[nddf[symbol]['SIG_QFY_ICHI_LONG']].index))
#                 images_constructor(symbol, i_index_long, time_frame_size, 1)  ## a constructor teszi bele az images-ek közé
#
#                 #  beteszem a 'good' Shortokat -----------------------------------------
#                 i_index_short = (tuple(nddf[symbol].loc[nddf[symbol]['SIG_QFY_ICHI_SHORT']].index))
#                 images_constructor(symbol, i_index_short, time_frame_size, 2)  ## a constructor teszi bele az images-ek közé
#
#                 bad_over_weight = 1  # szorzó
#                 #  beteszem a 'bad' Longokat -----------------------------------------
#                 average_element_no = int((len(i_index_long) + len(i_index_short))/2)
#                 i_index_long_first_m = (list(nddf[symbol].loc[nddf[symbol]['SIG_ICHI_LONG_FIRST']].index))
#                 i_index_long_first_m = array_diff(i_index_long_first_m, i_index_long)  # kiveszem a qualified elemeket
#                 i_index_long_first_m = array_random_select(i_index_long_first_m, average_element_no * bad_over_weight)
#                 images_constructor(symbol, i_index_long_first_m, time_frame_size, 3)  ## a constructor teszi bele az images-ek közé
#
#                 #  beteszem a 'bad' Shortokat -----------------------------------------
#                 i_index_short_first_m = (list(nddf[symbol].loc[nddf[symbol]['SIG_ICHI_SHORT_FIRST']].index))
#                 i_index_short_first_m = array_diff(i_index_short_first_m, i_index_short)  # kiveszem a qualified elemeket
#                 i_index_short_first_m = array_random_select(i_index_short_first_m, average_element_no * bad_over_weight)
#                 images_constructor(symbol, i_index_short_first_m, time_frame_size, 4)  ## a constructor teszi bele az images-ek közé
#
#                 n_img.set_meta(ndf_meta.get_all_meta_key(symbol))
#                 n_img.save()
#
#         elif images_for == 'SMA5813' or images_for == 'SMA5813_FULL':
#
#             time_frame_size = 45  # a indikátortól visszafelé hány percet tegyen az image-ba
#
#             ### minden image kreátornak saját konstruktora van, ahány stratégiától függően mást teszek bele
#             def images_constructor(symbol, indexes, time_frame_size, q):
#                 # print("itt", indexes)
#                 # print("indexes", len(indexes))
#
#                 for i_il in indexes:
#                     i_int_to = int(i_il)
#                     i_int_from = i_int_to - time_frame_size + 1
#
#                     if i_int_from > 0:
#                         # time_gap, time_section = time_gap_section(symbol, i_il, time_frame_size)
#                         i_data_dict = {
#                             # 'ohlc4': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'ohlc4']),
#                             # 'Low': r_v(tuple(nddf[symbol].loc[i_int_from:i_int_to, 'Low'])),
#                             # 'High': r_v(tuple(nddf[symbol].loc[i_int_from:i_int_to, 'High'])),
#                             # 'Open': r_v(tuple(nddf[symbol].loc[i_int_from:i_int_to, 'Open'])),
#                             # 'Close': r_v(tuple(nddf[symbol].loc[i_int_from:i_int_to, 'Close'])),
#                             # 'ADX_8_ONE': r_v(tuple(nddf[symbol].loc[i_int_from:i_int_to, 'ADX_8_ONE'])),
#                             'Low': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'Low']),
#                             'High': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'High']),
#
#                             # 'Close': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'Close']),
#                             # 'Open': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'Open']),
#
#                             'ADX_8_ONE': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'ADX_8_ONE']),
#                             'RSI_14': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'RSI_14']),
#                             # 'Volume': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'Volume']),
#                             # 'DMP_8': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'DMP_8']),
#                             # 'DMN_8': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'DMN_8']),
#
#                             # 'time_gap': time_gap,
#                             # 'time_section': time_section,
#                         }
#                         if len(contras[0]) > 0:
#                             for i_con in contras:
#
#                                 contra_sep_pre = i_con.split('_')
#                                 con_sep = []
#                                 if len(contra_sep_pre) > 2:
#                                     con_sep.append(contra_sep_pre[0])
#                                     s = "_"
#                                     con_sep.append(s.join(contra_sep_pre[1:]))
#                                 else:
#                                     con_sep = contra_sep_pre
#
#                                 con_symbol = con_sep[0]
#                                 con_field = con_sep[1]
#                                 i_data_dict[i_con] = tuple(nddf[con_symbol].loc[i_int_from:i_int_to, con_field])
#
#                         n_img.add_image(i_data_dict, q)
#
#             # i_indicators_need = ['SMA5813', 'ADX8', 'RSI14']
#             i_indicators_need = ['SMA5813']
#             if self.check_indicators(symbol, i_indicators_need):
#                 n_img.set_description("""
#                 Ötlet: 5 8 13 mozgóátlagokat figyelek, ha 5 alatta 8 alatta 13, akkor az egy LONG jel (visszafele SHORT),
#                 ezek körül kiválasztom azt amin lehet legalább x dollárt (50 körül) keresni (qualified),
#                 (pontos paraméterek a meta adatok között találhatók) és ezeket megpráblom
#                 klasszifikálni, elválasztani azoktól amiken nem lehet pénzt keresni.
#                 """)
#
#                 target_names = {'0': "Good LONG signal",
#                                 '1': "Good SHORT signal",
#                                 '2': "Bad LONG signal",
#                                 '3': "Bad SHORT signal"
#                                 }
#
#                 n_img.add_target_names(target_names)
#
#                 #  beteszem a 'good' Longokat -----------------------------------------
#                 i_index_long = (tuple(nddf[symbol].loc[nddf[symbol]['SIG_QFY_SMA5813_LONG']].index))
#                 images_constructor(symbol, i_index_long, time_frame_size,
#                                    0)  ## a constructor teszi bele az images-ek közé
#
#                 #  beteszem a 'good' Shortokat -----------------------------------------
#                 i_index_short = (tuple(nddf[symbol].loc[nddf[symbol]['SIG_QFY_SMA5813_SHORT']].index))
#                 images_constructor(symbol, i_index_short, time_frame_size,
#                                    1)  ## a constructor teszi bele az images-ek közé
#
#                 bad_over_weight = 1.1  # szorzó
#                 #  beteszem a 'bad' Longokat -----------------------------------------
#                 average_element_no = int((len(i_index_long) + len(i_index_short)) / 2)
#                 i_index_long_first_m = (list(nddf[symbol].loc[nddf[symbol]['SIG_SMA5813_LONG_FIRST']].index))
#                 i_index_long_first_m = array_diff(i_index_long_first_m, i_index_long)  # kiveszem a qualified elemeket
#
#                 if images_for == 'SMA5813':
#                     i_index_long_first_m = array_random_select(i_index_long_first_m, int(average_element_no * bad_over_weight))
#                 images_constructor(symbol, i_index_long_first_m, time_frame_size,
#                                    2)  ## a constructor teszi bele az images-ek közé
#
#                 #  beteszem a 'bad' Shortokat -----------------------------------------
#                 i_index_short_first_m = (list(nddf[symbol].loc[nddf[symbol]['SIG_SMA5813_SHORT_FIRST']].index))
#                 i_index_short_first_m = array_diff(i_index_short_first_m, i_index_short)  # kiveszem a qualified elemeket
#                 if images_for == 'SMA5813':
#                     i_index_short_first_m = array_random_select(i_index_short_first_m, int(average_element_no * bad_over_weight))
#                 images_constructor(symbol, i_index_short_first_m, time_frame_size,
#                                    3)  ## a constructor teszi bele az images-ek közé
#
#                 i_historic_max = {}
#                 i_historic_max["ohlc4" + "_MAX"] = str(max(tuple(nddf[symbol]['ohlc4'])))
#                 i_historic_max["Low" + "_MAX"] = str(max(tuple(nddf[symbol]['Low'])))
#                 i_historic_max["High" + "_MAX"] = str(max(tuple(nddf[symbol]['High'])))
#                 i_historic_max["ADX_8_ONE" + "_MAX"] = str(max(tuple(nddf[symbol]['ADX_8_ONE'])))
#                 i_historic_max["RSI_14" + "_MAX"] = str(max(tuple(nddf[symbol]['RSI_14'])))
#
#                 # i_historic_max["Close" + "_MAX"] = str(max(tuple(nddf[symbol]['Close'])))
#                 # i_historic_max["Open" + "_MAX"] = str(max(tuple(nddf[symbol]['Open'])))
#                 # i_historic_max["Volume" + "_MAX"] = str(max(tuple(nddf[symbol]['Volume'])))
#                 if len(contras[0]) > 0:
#                     for i_con in contras:
#                         contra_sep_pre = i_con.split('_')
#                         con_sep = []
#                         if len(contra_sep_pre) > 2:
#                             con_sep.append(contra_sep_pre[0])
#                             s = "_"
#                             con_sep.append(s.join(contra_sep_pre[1:]))
#                         else:
#                             con_sep = contra_sep_pre
#
#                         con_symbol = con_sep[0]
#                         con_field = con_sep[1]
#                         i_historic_max[str(i_con) + "_MAX"] = str(max(tuple(nddf[con_symbol][con_field])))
#
#                 n_img.set_historic_max(i_historic_max)
#                 n_img.set_meta(ndf_meta.get_all_meta_key(symbol))
#                 n_img.save()
#
#         elif images_for == 'BREAKOUT' or images_for == 'BREAKOUT_FULL':
#
#             time_frame_size = 45  # a indikátortól visszafelé hány percet tegyen az image-ba
#
#             ### minden image kreátornak saját konstruktora van, ahány stratégiától függően mást teszek bele
#             def images_constructor(symbol, indexes, time_frame_size, q):
#                 # print("indexes", len(indexes))
#
#                 for i_il in indexes:
#                     i_int_to = int(i_il)
#                     i_int_from = i_int_to - time_frame_size + 1
#
#                     if i_int_from > 0:
#                         # time_gap, time_section = time_gap_section(symbol, i_il, time_frame_size)
#                         i_data_dict = {
#                             # 'ohlc4': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'ohlc4']),
#                             # 'Low': r_v(tuple(nddf[symbol].loc[i_int_from:i_int_to, 'Low'])),
#                             # 'High': r_v(tuple(nddf[symbol].loc[i_int_from:i_int_to, 'High'])),
#                             # 'Open': r_v(tuple(nddf[symbol].loc[i_int_from:i_int_to, 'Open'])),
#                             # 'Close': r_v(tuple(nddf[symbol].loc[i_int_from:i_int_to, 'Close'])),
#                             # 'ADX_8_ONE': r_v(tuple(nddf[symbol].loc[i_int_from:i_int_to, 'ADX_8_ONE'])),
#                             'Low': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'Low']),
#                             'High': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'High']),
#                             # 'Close': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'Close']),
#                             # 'Open': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'Open']),
#                             # 'ADX_8_ONE': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'ADX_8_ONE']),
#                             # 'RSI_14': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'RSI_14']),
#                             # 'DMP_8': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'DMP_8']),
#                             # 'DMN_8': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'DMN_8']),
#                             # 'Volume': tuple(nddf[symbol].loc[i_int_from:i_int_to, 'Volume']),
#                             # 'MSFT_ohlc4': tuple(nddf['MSFT'].loc[i_int_from:i_int_to, 'ohlc4']),
#                             # 'time_gap': time_gap,
#                             # 'time_section': time_section,
#                         }
#                         n_img.add_image(i_data_dict, q)
#
#             i_indicators_need = ['BREAKOUT']
#             if self.check_indicators(symbol, i_indicators_need):
#                 n_img.set_description("""
#                 Ötlet: végigmegyek az OHLC4-n kereselm a lokális minimumot illetve lokális maximumot és onnan indítok
#                 egy kvalifikációt, ha sikerül 50 USD-t keresni 30 perc alatt úgy, hogy stoploss -5 usd, akkor az egy
#                 kvalifikált szignál. Itt most nincs klasszikus tchnikai indikátor. Keresem a pontokat ahol lehet
#                 3000 USD-vel 50 dollárt keresni maximum 30 perc alatt. Azt vettem észre, hogy átlagosan napi 2-3 ilyen
#                 eset előfordul azoknál a részvényekél amelyek nincsenek agyon trédelve (pl. MSFT).
#                 """)
#
#                 target_names = {'0': "Good LONG signal",
#                                 '1': "Good SHORT signal",
#                                 '2': "Bad LONG signal",
#                                 '3': "Bad SHORT signal"
#                                 }
#
#                 n_img.add_target_names(target_names)
#
#                 # oszlop nevek
#                 # SIG_BREAKOUT_LONG_ALL
#                 # SIG_QFY_BREAKOUT_LONG
#                 # SIG_BREAKOUT_SHORT_ALL
#                 # SIG_QFY_BREAKOUT_SHORT
#
#                 #  beteszem a 'good' Longokat -----------------------------------------
#                 i_index_long = (tuple(nddf[symbol].loc[nddf[symbol]['SIG_QFY_BREAKOUT_LONG']].index))
#                 images_constructor(symbol, i_index_long, time_frame_size,
#                                    0)  ## a constructor teszi bele az images-ek közé
#
#                 #  beteszem a 'good' Shortokat -----------------------------------------
#                 i_index_short = (tuple(nddf[symbol].loc[nddf[symbol]['SIG_QFY_BREAKOUT_SHORT']].index))
#                 images_constructor(symbol, i_index_short, time_frame_size,
#                                    1)  ## a constructor teszi bele az images-ek közé
#
#                 bad_over_weight = 2  # szorzó ha nagyon kevés a jó szignál akkor túl mintavételezem a rossz szignálokat
#                 #  beteszem a 'bad' Longokat -----------------------------------------
#                 average_element_no = int((len(i_index_long) + len(i_index_short)) / 2)
#                 i_index_long_first_m = (list(nddf[symbol].loc[nddf[symbol]['SIG_BREAKOUT_LONG_ALL']].index))
#                 i_index_long_first_m = array_diff(i_index_long_first_m, i_index_long)  # kiveszem a qualified elemeket
#                 if images_for == "BREAKOUT":  # BREAKOUT_FULL esetén a rosszakat mindet beleteszem tesztlésre
#                     i_index_long_first_m = array_random_select(i_index_long_first_m, average_element_no * bad_over_weight)
#                 images_constructor(symbol, i_index_long_first_m, time_frame_size,
#                                    2)  ## a constructor teszi bele az images-ek közé
#
#                 #  beteszem a 'bad' Shortokat -----------------------------------------
#                 i_index_short_first_m = (list(nddf[symbol].loc[nddf[symbol]['SIG_BREAKOUT_SHORT_ALL']].index))
#                 i_index_short_first_m = array_diff(i_index_short_first_m,
#                                                    i_index_short)  # kiveszem a qualified elemeket
#                 if images_for == "BREAKOUT":  # BREAKOUT_FULL esetén a rosszakat mindet beleteszem tesztlésre
#                     i_index_short_first_m = array_random_select(i_index_short_first_m, average_element_no * bad_over_weight)
#                 images_constructor(symbol, i_index_short_first_m, time_frame_size,
#                                    3)  ## a constructor teszi bele az images-ek közé
#
#                 n_img.set_meta(ndf_meta.get_all_meta_key(symbol))
#
#                 n_img.save()
#
#         elif images_for == 'ADX_Ai':
#             i_indicators_need = ['ADX8']
#             if self.check_indicators(symbol, i_indicators_need):
#                 log('minden okmehet')
#         else:
#             log("Image style is missing...")
#         del n_img




# class back_processes(object):
#     def __init__(self, interval=60):
#         self.interval = interval
#         self.kill = False
#         self.runnig = False
#         self.start()
#
#     def stop(self):
#         self.kill = True
#         log("bp-> stopped")
#
#     def start(self):
#         if self.runnig:
#             log("bp-> already running...")
#         else:
#             log("bp-> started")
#             self.kill = False
#             thread = threading.Thread(target=self.run, args=())
#             thread.daemon = True
#             self.runnig = True
#             thread.start()
#         return
#
#     def run(self):
#         while True:
#             # More statements comes here
#             # print(datetime.now().__str__() + ' : Start task in the background')
#             wl.refresh_close()
#             gui.refresh_ui()
#             time.sleep(self.interval)
#             if self.kill:
#                 self.runnig = False
#                 break

# Socket ----------------------------------------------------

# from PyQt5 import QtCore
# class ListenWebsocket(QtCore.QThread):
#     def __init__(self, parent=None):
#         super(ListenWebsocket, self).__init__(parent)
#         websocket.enableTrace(False)
#         self.ws = websocket.WebSocketApp("wss://ws.finnhub.io?token=bs9c9lvrh5rahoaofmt0",
#                                         on_message=self.on_message,
#                                         on_error=self.on_error,
#                                         on_close=self.on_close
#                                         )
#         self.cdx = 1
#         self.cont_datetime = datetime.now()
#
#     def on_message(self, message):
#         # print(message)
#         # print(datetime.now(), self.cont_datetime)
#         duration = datetime.now() - self.cont_datetime
#         duration_in_s = int(duration.total_seconds())
#         # print(duration_in_s)
#         # print(duration_in_s)
#         if duration_in_s > 15:
#             s(message)
#             # print("segg")
#             # print(datetime.now())
#             # print(self.cont_datetime)
#             self.cont_datetime = datetime.now()
#
#     def on_error(self, error):
#         print("error" + error)
#
#     def on_close(self):
#         print("Status: FinnHub socket closed")
#
#     def on_open(self):
#
#         self.ws.send('{"type":"subscribe","symbol":"AAPL"}')
#         # self.ws.send('{"type":"subscribe","symbol":"AMZN"}')
#         self.ws.send('{"type":"subscribe","symbol":"BINANCE:BTCUSDT"}')
#         # self.ws.send('{"type":"subscribe","symbol":"IC MARKETS:1"}')
#         print("Status: FinnHub socket opened")
#
#     def run(self):
#         self.ws.on_open = self.on_open
#         self.ws.run_forever()
