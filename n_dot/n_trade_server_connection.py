import paramiko
import os
import pickle
import numpy as np


class n_trade_server_connection:

    def __init__(self, log):
        self.gui_log = log
        self.sever_name = "Vultr - 2C; 2GB Ram"
        self.username = 'root'
        self.password = 'C7?dB#3#,KvQ7q+W'
        self.hostname = '207.148.99.176'
        self.ports = 22
        # self.transport = ""
        # self.sftp = ""
        self.client = '1'
        self.local_projects_dir = r"projects/"
        self.trade_fname = "nDot_command_trade.pickle"
        self.push_fname = "nDot_command_push.npy"
        self.local_incoming = "incoming/"
        self.local_ountgoing = "outgoing/"

    def log(self, text):
        self.gui_log(text)

    def open_connect(self):
        self.log(f"Login. nDot_trade_server: {self.hostname}")
        self.transport = paramiko.Transport((self.hostname, self.ports))
        self.transport.connect(username=self.username, password=self.password)
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)

    def close_connect(self):
        self.sftp.close()
        self.transport.close()
        self.log(f"Log Out nDot_trade_server")

    def put(self, remotepath, localpath):
        try:
            self.sftp.put(remotepath=remotepath, localpath=localpath)
        except BaseException as error:
            print(f'n_trade_server_connection -> put exception: {error}')

    def get(self, remotepath, localpath):
        try:
            self.sftp.get(remotepath=remotepath, localpath=localpath)
        except BaseException as error:
            print(f'n_trade_server_connection -> get exception: {error}')

    def remove(self, remotepath):
        try:
            self.sftp.remove(path=remotepath)
        except BaseException as error:
            print(f'n_trade_server_connection -> get exception: {error}')

    def listdir(self, remotepath):
        try:
            i_return = self.sftp.listdir(path=remotepath)
            return i_return
        except BaseException as error:
            print(f'n_trade_server_connection -> listdir exception: {error}')
            return []

    def set_trade(self):
        remote_fname = "CLIENTS/" + self.client + "/INCOMING/" + self.trade_fname
        local_fname = self.local_ountgoing + self.trade_fname
        if os.path.exists(local_fname):
            self.put(remotepath=remote_fname, localpath=local_fname)

    def send_attachment(self, fname):
        remote_fname = "CLIENTS/" + self.client + "/INCOMING/ATTACHMENT/" + fname
        self.put(remotepath=remote_fname, localpath=fname)

    def get_messages(self):
        remote_fname = "CLIENTS/" + self.client + "/OUTGOING/"
        mlist = self.listdir(remote_fname)
        for ml in mlist:
            remote_fm = remote_fname + ml
            local_ml = self.local_incoming + ml
            self.get(remotepath=remote_fm, localpath=local_ml)
            self.remove(remotepath=remote_fm)

    def push_project(self, project):
        remote_dir = "CLIENTS/" + self.client + "/INCOMING/ATTACHMENT/"
        l_fname = [f"nDot_TF_MODEL_{project}.h5",
                   f"nDot_MinMaxScaler_{project}.pickle",
                   f"nDot_PRO_{project}.txt"]
        for lfn in l_fname:
            local_fn = f"{self.local_projects_dir}{project}/{lfn}"
            remote_fn = remote_dir + lfn
            # print(local_fn, remote_fn)
            if os.path.exists(local_fn):
                self.put(remotepath=remote_fn, localpath=local_fn)
                self.log(f"    push: {local_fn}")

        remote_fn = "CLIENTS/" + self.client + "/INCOMING/" + self.push_fname
        local_fn = self.local_ountgoing + self.push_fname
        if os.path.exists(local_fn):
            self.put(remotepath=remote_fn, localpath=local_fn)
            self.log(f"    push: {local_fn}")


if __name__ == '__main__':
    tc = n_trade_server_connection()
    tc.get_messages()
    print(pickle.load(open("incoming/nDot_trade_server_status.pickle", "rb")))

    push = np.array(["BTCUSDT_P10INT",
          "ETHUSDT_P10INT"])

    np.save("nDot_command_push", push)

    trade = {"BTCUSDT_P10INT": False,
             "ETHUSDT_P10INT": True}

    pickle.dump(trade, open("nDot_command_trade.pickle", "wb"))

    #
    #
    # tc.push_project("BTCUSDT_P10INT")
    # tc.set_trade()

    # tc.get_messages()
    # print(pickle.load(open("incoming/nDot_trade_server_status.pickle", "rb")))

