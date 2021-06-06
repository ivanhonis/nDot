from datetime import datetime, time as dt_time
import time


class n_tools:

    def __init__(self, gui):
        self.gui = gui

    # def get_df_column(self, df, col):
    #     return df[col].to_numpy().tolist()

    def dbdt_to_unixdt(self, datestring):
        dt = datetime.strptime(datestring, '%Y-%m-%d %H:%M:%S')
        dt2 = datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        i_return = str(int(time.mktime(dt2.timetuple())))
        return i_return

    def unixdt_to_dbdt(self, unix_datetime):
        return str(datetime.fromtimestamp(int(unix_datetime)).strftime('%Y-%m-%d %H:%M:%S'))

    # def get_ui_date_unix(self, fort):
    #
    #     def convert_to_unix_dt(cyear, cmonth, cday, chour, cminute, csecound):
    #         dt = datetime(cyear, cmonth, cday, chour, cminute, csecound)
    #         return str(int(time.mktime(dt.timetuple())))
    #
    #     i_from_year = int(self.gui.From_D.selectedDate().toString("yyyy"))
    #     i_from_month = int(self.gui.From_D.selectedDate().toString("MM"))
    #     i_from_day = int(self.gui.From_D.selectedDate().toString("dd"))
    #     i_from_hour = int(self.gui.From_T.dateTime().toString("hh"))
    #     i_from_minute = int(self.gui.From_T.dateTime().toString("mm"))
    #     i_from_secound = int(self.gui.From_T.dateTime().toString("ss"))
    #
    #     i_to_year = int(self.gui.To_D.selectedDate().toString("yyyy"))
    #     i_to_month = int(self.gui.To_D.selectedDate().toString("MM"))
    #     i_to_day = int(self.gui.To_D.selectedDate().toString("dd"))
    #     i_to_hour = int(self.gui.To_T.dateTime().toString("hh"))
    #     i_to_minute = int(self.gui.To_T.dateTime().toString("mm"))
    #     i_to_secound = int(self.gui.To_T.dateTime().toString("ss"))
    #     if fort == "from":
    #         i_return = convert_to_unix_dt(i_from_year, i_from_month, i_from_day,
    #                                        i_from_hour, i_from_minute, i_from_secound)
    #     else:
    #         i_return = convert_to_unix_dt(i_to_year, i_to_month, i_to_day,
    #                                        i_to_hour, i_to_minute, i_to_secound)
    #     return i_return

    # def get_ui_date_dbdt(self, fort):
    #
    #     def convert_to_unix_dt(cyear, cmonth, cday, chour, cminute, csecound):
    #         dt = datetime(cyear, cmonth, cday, chour, cminute, csecound)
    #         return str(int(time.mktime(dt.timetuple())))
    #
    #     if fort == "from":
    #         i_return = self.unixdt_to_dbdt(self.get_ui_date_unix("from"))
    #     else:
    #         i_return = self.unixdt_to_dbdt(self.get_ui_date_unix("to"))
    #     return i_return
    #
    # def convert_df_to_csvdf(self, i_df):
    #     import io
    #     from io import StringIO
    #     su = io.StringIO()
    #     i_df.to_csv(su, index=False)
    #     i_return = pd.read_csv(StringIO(su.getvalue()), sep=",", index_col=0, parse_dates=True)
    #     return i_return
    #
    # def is_date_in_timeperiod(self, start_time, end_time, Date):
    #     in_time = dt_time(Date.hour, Date.minute)
    #     return in_time >= start_time and in_time <= end_time
