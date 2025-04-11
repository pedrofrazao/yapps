import random
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class TimeSeriesPlot:
    def __init__(self, parent, start_time=-99, end_time=0, initial_values=None):
        self.parent = parent
        self.start_time = start_time
        self.end_time = end_time
        self.fig = Figure(figsize=(5, 3), dpi=100)
        self.ax = self.fig.add_subplot()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        # Initialize the data structure as a dictionary of series
        self.data = {}
        self.plot_points = [i for i in range(self.start_time, self.end_time+1)]
        
        # Handle initial values
        if initial_values is None:
            # Create default series
            self.data['default'] = [0 for _ in range(self.start_time, self.end_time+1)]
        elif isinstance(initial_values, dict):
            # Multiple series provided
            self.data = initial_values
        else:
            # Single series provided as a list
            self.data['default'] = initial_values
        
        self.update_plot()

    def update_plot(self):
        self.ax.clear()
        
        # Plot each series
        for series_name, series_data in self.data.items():
            self.ax.plot(series_data, label=series_name)
        
        # Add legend if we have multiple series
        if len(self.data) > 1:
            self.ax.legend()
            
        self.ax.set_ylim(bottom=0)  # Force the y-axis to start at 0
        self.canvas.draw()

    def add_value(self, value, series_name='default'):
        # Create series if it doesn't exist
        if series_name not in self.data:
            self.add_series(series_name)
            
        self.data[series_name].append(value)
        self.data[series_name].pop(0)
        self.update_plot()
    
    def add_series(self, series_name, initial_values=None):
        if series_name not in self.data:
            if initial_values is None:
                self.data[series_name] = [0 for _ in range(self.start_time, self.end_time+1)]
            else:
                self.data[series_name] = initial_values
            self.update_plot()
    
    def remove_series(self, series_name):
        if series_name in self.data:
            del self.data[series_name]
            self.update_plot()
    
    def get_series_list(self):
        return list(self.data.keys())