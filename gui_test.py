import tkinter as tk
from tkinter import filedialog, messagebox
import random
import json
import sys
import os

dirname = os.path.dirname(__file__)
libpath = os.path.abspath(os.path.join(dirname, 'ppSlib'))
sys.path.append(libpath)

from matrix import MatrixGUI  # Import the MatrixGUI class
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# import arena

def load_configuration(root, filename=None):
    # Open file dialog to select configuration file
    if filename is None:
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    file_path = filename if 'json' in filename else filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    
    if file_path:
        try:
            with open(file_path, 'r') as config_file:
                config = json.load(config_file)
                print("Configuration loaded:", config)
                return config
        except (json.JSONDecodeError, IOError) as e:
            messagebox.showerror("Error", f"Failed to load configuration file: {e}")
            root.quit()
    return None

# def place_cells_randomly(matrix_size, cell_types, num_by_types):
#     updates = []
#     positions = [(row, col) for row in range(matrix_size["rows"]) for col in range(matrix_size["columns"])]
#     random.shuffle(positions)
    
#     for cell_type, amount in num_by_types.items():
#         for _ in range(amount):
#             if positions:
#                 row, col = positions.pop()
#                 updates.append((row, col, cell_types[cell_type]["color"], cell_types[cell_type]["name"]))
    
#     return updates

if __name__ == "__main__":
    root = tk.Tk()
    root.title("2D Matrix with Colored Cells")

    # Create a menu bar
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    # Add "File" menu
    file_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Load Configuration", command=lambda: load_configuration(root))

    # Load initial configuration
    config = load_configuration(root, 'config.json')
    if config:
        matrix_size = config["matrix_size"]
        cell_types = config["cell_types"]
        num_by_types = config["cells"]["num_by_types"]
        app = MatrixGUI(root, matrix_size["rows"], matrix_size["columns"])  # Matrix size from config
        # updates = place_cells_randomly(matrix_size, cell_types, num_by_types)
        app.update_display()
    else:
        app = MatrixGUI(root, 10, 10)  # Default matrix size

    def periodic_step():
        app.step()
        app.self.log_message("new stop")
        root.after(1000, periodic_step)  # Call step method every second

    root.after(1000, periodic_step)  # Start the periodic step
    root.mainloop()