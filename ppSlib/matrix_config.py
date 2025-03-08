import json
import tkinter as tk

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