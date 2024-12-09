import tkinter as tk
from tkinter import filedialog
import random
import json
from time_series_plot import TimeSeriesPlot  # Import the TimeSeriesPlot class
from matrix import MatrixGUI  # Import the MatrixGUI class
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def load_configuration():
    # Open file dialog to select configuration file
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, 'r') as config_file:
            config = json.load(config_file)
            print("Configuration loaded:", config)
            return config
    return None

if __name__ == "__main__":
    root = tk.Tk()
    root.title("2D Matrix with Colored Cells")

    # Create a menu bar
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    # Add "File" menu
    file_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Load Configuration", command=load_configuration)

    # Load initial configuration
    config = load_configuration()
    if config:
        matrix_size = config["matrix_size"]
        app = MatrixGUI(root, matrix_size["rows"], matrix_size["columns"])  # Matrix size from config
    else:
        app = MatrixGUI(root, 10, 10)  # Default matrix size

    root.mainloop()