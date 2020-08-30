# # ------------------------------------------------------
# # -------------------- mplwidget.py --------------------
# # ------------------------------------------------------
# from PyQt5.QtWidgets import*
#
# from matplotlib.backends.backend_qt5agg import FigureCanvas
# from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
#
# from matplotlib.figure import Figure
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
#
#
# class MplWidget(QWidget):
#
#     def __init__(self, parent = None):
#
#         QWidget.__init__(self, parent)
#         plt.rc('axes', grid=True)
#         plt.rc('grid', color='#aaaaaa', linestyle=':', linewidth=0.5)
#
#         fillcolor = 'b'
#         left, width = 0.0395, 0.96
#         rect1 = [left, 0.28, width, 0.72]
#         rect2 = [left, 0.20, width, 0.2]
#         rect3 = [left, 0.1, width, 0.2]
#
#         fig = plt.figure(facecolor=fillcolor, frameon=False, dpi=80)
#         self.ax1_1 = fig.add_axes(rect1)  # left, bottom, width, height
#
#         for xtick in self.ax1_1.get_xticklabels():
#             xtick.set_color('none')
#
#         self.ax2_1 = fig.add_axes(rect2, sharex=self.ax1_1)
#         self.ax1_1.autoscale()
#         self.ax1_1.autoscale()
#         self.canvas = FigureCanvas(fig)
#         vertical_layout = QVBoxLayout()
#         self.toolbar = NavigationToolbar(self.canvas, self, coordinates=False)
#         vertical_layout.addWidget(self.canvas)
#         vertical_layout.addWidget(self.toolbar)
#
#         self.setLayout(vertical_layout)
#         self.canvas.draw()


# -------------------- mplwidget.py --------------------
# ------------------------------------------------------
from PyQt5.QtWidgets import*

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import mplfinance as mpf


class MplWidget(QWidget):

    def __init__(self, parent = None):

        QWidget.__init__(self, parent)

        df = pd.read_csv('C:/Users/honis.ivan/PycharmProjects/plotchart/mplfinance-master/examples/data/yahoofinance-SPY-20080101-20180101.csv', index_col=0,
                         parse_dates=True)
        df.shape
        df.head(3)
        df.tail(3)




        # plt.rc('axes', grid=True)
        # plt.rc('grid', color='#aaaaaa', linestyle=':', linewidth=0.5)
        #
        # fillcolor = 'b'
        # rect1 = [left, 0.28, width, 0.72]

        # left, width = 0.0395, 0.96        # rect2 = [left, 0.20, width, 0.2]
        # rect3 = [left, 0.1, width, 0.2]
        #
        # fig = plt.figure(facecolor=fillcolor, frameon=False, dpi=80)
        # # self.ax1_1 = fig.add_axes(rect1)  # left, bottom, width, height
        #
        # for xtick in self.ax1_1.get_xticklabels():
        #     xtick.set_color('none')
        #
        # self.ax2_1 = fig.add_axes(rect2, sharex=self.ax1_1)
        # self.ax1_1.autoscale()
        # self.ax1_1.autoscale()
        # fig = mpf.figure()
        #         rect3 = [left, 0.1, width, 0.2]
        #         fig = plt.figure(facecolor=fillcolor, frameon=False, dpi=80)


        # fig = mpf.figure(style='classic', constrained_layout=True)
        fig = mpf.figure(style='binance')
        self.ax1 = fig.add_subplot(2, 1, 1)
        self.ax2 = fig.add_subplot(2, 1, 2, sharex=self.ax1)
        self.ax1.autoscale()
        self.ax2.autoscale()
        fig.subplots_adjust(hspace=0)

        for xtick in self.ax1.get_xticklabels():
            xtick.set_color('none')
        # mpf.plot(df, ax=self.ax1, volume=self.ax2)
        # fig, axlist = mpf.plot(df[700:850], type='line', volume=True, mav=(40, 60), returnfig=True)

        # self.fig = Figure(constrained_layout=True)
        mpf.plot(df, ax=self.ax1, volume=self.ax2, tight_layout=True)
        self.canvas = FigureCanvas(fig)
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        self.toolbar = NavigationToolbar(self.canvas, self, coordinates=False)
        vertical_layout.addWidget(self.toolbar)
        self.setLayout(vertical_layout)
        # chartlayout.addWidget(canvas)

        # from PyQt5 import QtGui, QtCore
        # import matplotlib
        # self.ax = self.fig.add_subplot(111)
        # self.cursor = matplotlib.widgets.Cursor(self.ax)
        # # set cursor
        # # self.canvas.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))
        # # since I find Blank cursor very confusing, I will use a better one:
        # self.canvas.setCursor(QtGui.QCursor(QtCore.Qt.SizeAllCursor))

        self.canvas.draw()



        # self.canvas = FigureCanvas(mpf)
        # vertical_layout = QVBoxLayout()
        # self.toolbar = NavigationToolbar(self.canvas, self, coordinates=False)
        # vertical_layout.addWidget(self.canvas)
        # vertical_layout.addWidget(self.toolbar)
        #
        # self.setLayout(vertical_layout)
        # self.canvas.draw()



