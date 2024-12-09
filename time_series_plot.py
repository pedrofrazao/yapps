import random
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class TimeSeriesPlot:
    def __init__(self, parent, start_time=0, end_time=100):
        self.parent = parent
        self.start_time = start_time
        self.end_time = end_time
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.data = [random.random() for _ in range(self.start_time, self.end_time)]
        self.update_plot()

    def update_plot(self):
        t = [i for i in range(self.start_time, self.end_time)]
        self.ax.clear()
        self.ax.plot(t, self.data)
        self.canvas.draw()

    def add_value(self, value):
        self.data.append(value)
        if len(self.data) > (self.end_time - self.start_time):
            self.data.pop(0)
        self.update_plot()