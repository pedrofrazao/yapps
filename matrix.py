import tkinter as tk
import random
from time_series_plot import TimeSeriesPlot  # Import the TimeSeriesPlot class

class MatrixGUI:
    def __init__(self, root, rows, cols):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.running = False
        self.last_updates = []  # Attribute to store the list of the last updates

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
        # Bind the mouse click event to show popup
        self.canvas.bind("<Button-1>", self.show_popup)
        # Bind the keyboard shortcut to exit the application
        self.root.bind("<Control-q>", self.exit_application)

    def draw_matrix(self):
        self.canvas.delete("all")
        self.cell_width = self.canvas.winfo_width() // self.cols
        self.cell_height = self.canvas.winfo_height() // self.rows
        self.cell_colors = {}
        for x,y,c,t in self.last_updates:
            x1 = y * self.cell_width
            y1 = x * self.cell_height
            x2 = x1 + self.cell_width
            y2 = y1 + self.cell_height
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=c, outline="black")
            self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=t, fill="black")


    def random_color(self):
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    def show_popup(self, event):
        # Calculate the row and column of the cell under the mouse
        col = int(event.x // self.cell_width)
        row = int(event.y // self.cell_height)
        if 0 <= col < self.cols and 0 <= row < self.rows:
            color = self.cell_colors[(row, col)]
            # Create a popup message
            popup = tk.Toplevel(self.root)
            popup.wm_overrideredirect(True)
            popup.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            label = tk.Label(popup, text=f"Cell ({row}, {col})\nColor: {color}", background="yellow")
            label.pack()
            # Destroy the popup after a short delay
            self.root.after(1000, popup.destroy)

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

    def exit_application(self, event=None):
        self.root.quit()

    def update_display(self, updates):
        self.clear_matrix
        self.last_updates = updates  # Store the updates in the last_updates attribute
        for (row, col, color, caption) in updates:
            if 0 <= row < self.rows and 0 <= col < self.cols:
                x1 = col * self.cell_width
                y1 = row * self.cell_height
                x2 = x1 + self.cell_width
                y2 = y1 + self.cell_height
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
                self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=caption, fill="black")

    def clear_matrix(self):
        self.canvas.delete("all")
        self.cell_colors.clear()

if __name__ == "__main__":
    root = tk.Tk()
    app = MatrixGUI(root, 10, 10)
    root.mainloop()