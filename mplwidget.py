# ------------------------------------------------------
# -------------------- mplwidget.py --------------------
# ------------------------------------------------------
from PyQt5.QtWidgets import*

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class MplWidget(QWidget):

    def __init__(self, parent = None):

        QWidget.__init__(self, parent)
        plt.rc('axes', grid=True)
        plt.rc('grid', color='#aaaaaa', linestyle=':', linewidth=0.5)

        fillcolor = 'b'
        left, width = 0.0395, 0.96
        rect1 = [left, 0.25, width, 0.75]
        rect2 = [left, 0.05, width, 0.2]
        rect3 = [left, 0.1, width, 0.2]

        fig = plt.figure(facecolor=fillcolor, frameon=False, dpi=80)
        self.ax1_1 = fig.add_axes(rect1)  # left, bottom, width, height

        for xtick in self.ax1_1.get_xticklabels():
            xtick.set_color('none')

        self.ax2_1 = fig.add_axes(rect2, sharex=self.ax1_1)
        self.ax1_1.autoscale()
        self.ax1_1.autoscale()
        self.canvas = FigureCanvas(fig)
        vertical_layout = QVBoxLayout()
        self.toolbar = NavigationToolbar(self.canvas, self, coordinates=False)
        vertical_layout.addWidget(self.canvas)
        vertical_layout.addWidget(self.toolbar)

        self.setLayout(vertical_layout)
        self.canvas.draw()

