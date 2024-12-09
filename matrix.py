import tkinter as tk
import random
from time_series_plot import TimeSeriesPlot  # Import the TimeSeriesPlot class

class MatrixGUI:
    def __init__(self, root, rows, cols):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.running = False

        # Create a frame for the left side (buttons, text area, and plot)
        self.left_frame = tk.Frame(root, width=int(root.winfo_screenwidth() / 3))
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Create a frame for the buttons
        self.button_frame = tk.Frame(self.left_frame)
        self.button_frame.pack(side=tk.TOP, fill=tk.X)

        # Add buttons
        self.start_button = tk.Button(self.button_frame, text="Start", command=self.start)
        self.start_button.pack(side=tk.LEFT)

        self.stop_button = tk.Button(self.button_frame, text="Stop", command=self.stop)
        self.stop_button.pack(side=tk.LEFT)

        self.pause_button = tk.Button(self.button_frame, text="Pause", command=self.pause)
        self.pause_button.pack(side=tk.LEFT)

        # Create a text area for execution messages
        self.text_area = tk.Text(self.left_frame, height=10)
        self.text_area.pack(side=tk.TOP, fill=tk.X)

        # Create a frame for the plot
        self.plot_frame = tk.Frame(self.left_frame)
        self.plot_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Create a canvas for the matrix
        self.canvas = tk.Canvas(root)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.draw_matrix()
        self.time_series_plot = TimeSeriesPlot(self.plot_frame, start_time=0, end_time=100)

        # Bind the configure event to resize the matrix cells
        self.root.bind("<Configure>", self.on_resize)

    def draw_matrix(self):
        self.canvas.delete("all")
        cell_width = self.canvas.winfo_width() // self.cols
        cell_height = self.canvas.winfo_height() // self.rows
        for i in range(self.rows):
            for j in range(self.cols):
                color = self.random_color()
                self.canvas.create_rectangle(j * cell_width, i * cell_height, (j + 1) * cell_width, (i + 1) * cell_height, fill=color)

    def random_color(self):
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    def start(self):
        self.log_message("Start button clicked")
        self.running = True
        self.update_time_series()

    def stop(self):
        self.log_message("Stop button clicked")
        self.running = False

    def pause(self):
        self.log_message("Pause button clicked")

    def update_time_series(self):
        if self.running:
            self.time_series_plot.add_value(random.random())
            self.root.after(1000, self.update_time_series)  # Update every second

    def log_message(self, message):
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)

    def on_resize(self, event):
        self.draw_matrix()