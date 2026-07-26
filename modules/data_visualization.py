import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

class DataVisualization:
    def __init__(self):
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

    def plot_series(self, series_list):
        self.ax.clear()
        for series in series_list:
            if series.name.startswith("Formula:"):
                self.ax.plot(series.x_data, series.y_data, 
                             label=series.name, color=series.color)
            else:
                self.ax.errorbar(series.x_data, series.y_data, 
                                 xerr=series.x_error, yerr=series.y_error,
                                 fmt='o', label=series.name, color=series.color)
        self.ax.legend()
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_title('Plot delle Serie di Dati')
        self.canvas.draw()

    def plot_fit(self, series, x_fit, y_fit, fit_equation):
        self.ax.plot(x_fit, y_fit, '--', color=series.color)
        self.ax.text(0.05, 0.95, fit_equation, transform=self.ax.transAxes,
                     verticalalignment='top', fontsize=10, 
                     bbox=dict(facecolor='white', alpha=0.7))
        self.canvas.draw()

    def clear_plot(self):
        self.ax.clear()
        self.canvas.draw()

    def set_labels(self, title=None, x_label=None, y_label=None):
        if title:
            self.ax.set_title(title)
        if x_label:
            self.ax.set_xlabel(x_label)
        if y_label:
            self.ax.set_ylabel(y_label)
        self.canvas.draw()

    def save_plot(self, filename):
        self.figure.savefig(filename)

    def get_figure(self):
        return self.figure

    def set_axis_limits(self, x_min, x_max, y_min, y_max):
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        self.canvas.draw()

    def add_grid(self, visible=True):
        self.ax.grid(visible)
        self.canvas.draw()
