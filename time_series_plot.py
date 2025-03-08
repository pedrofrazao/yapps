import random
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class TimeSeriesPlot:
    def __init__(self, parent, start_time=-99, end_time=0, initial_values=None):
        self.parent = parent
        self.start_time = start_time
        self.end_time = end_time
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        # self.data = [random.random() for _ in range(self.start_time, self.end_time)]
        self.data = initial_values if initial_values is not None else [0 for _ in range(self.start_time, self.end_time+1)]
        self.plot_points = [ i for i in range(self.start_time, self.end_time+1) ]
        self.update_plot()

    def update_plot(self):
        self.ax.clear()
        # self.ax.plot( self.plot_points, self.data)
        self.ax.plot(self.data)
        self.ax.set_ylim(bottom=0)  # Force the y-axis to start at 0
        self.canvas.draw()

    def add_value(self, value):
        self.data.append(value)
        # if len(self.data) > (self.end_time - self.start_time):
        self.data.pop(0)
        self.update_plot()