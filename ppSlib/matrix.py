import tkinter as tk
import random
import time
from time_series_plot import TimeSeriesPlot  # Import the TimeSeriesPlot class
from arena import Arena, ArenaObject
from ppSlib.agent import LivingAgent
import ppSlib.ArenaDemo as arena_demo
from tkinter import filedialog
# import ppSlib.matrix_config
import json

class MatrixGUI:
    def __init__(self, rows=16, cols=16):
        self.rows = rows
        self.cols = cols
        self.running = False
        self.last_updates = []  # Attribute to store the list of the last updates
        self.arena = Arena(rows, cols)
        ## TEST ONLY
        for i in range(1):
            obj = ArenaObject(f"Object{i}")
            self.arena.add_to_position(random.randint(0, rows-1), random.randint(0, cols-1), obj)
        ## TEST ONLY
        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)  # Force full-screen mode
        self.max_speed = 1  # Maximum speed for the simulation
        self.last_step_time = 0  # Last time the step method was called
        root = self.root

        self.create_menu()
        
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

        self.step_button = tk.Button(self.button_frame, text="Step", command=self._single_step)
        self.step_button.pack(side=tk.LEFT)

        # Create a frame for the plot
        self.plot_frame = tk.Frame(self.left_frame, height=int(root.winfo_screenheight() / 4))
        self.plot_frame.pack(side=tk.TOP, fill=tk.X)

        # Create a text area for execution messages
        self.text_area = tk.Text(self.left_frame)
        self.text_area.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

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

    def show_error_popup(self, message):
        tk.messagebox.showerror("Error", message)

    def from_configuration(self, configuration_file):
        with open(configuration_file, 'r') as file:
            try:
                config = json.load(file)
            except json.JSONDecodeError as e:
                self.show_error_popup(f"Error loading configuration: {e}")
                return

        
        newarena = Arena.deserialize(config)

        self.rows = newarena.rows
        self.cols = newarena.cols
        
        self.arena = newarena
        self.update_display()

    def _draw_matrix_cells(self):
        for o in self.last_updates:
            x, y, c, t = o.get()
            if 0 <= x < self.rows and 0 <= y < self.cols:
                x1 = y * self.cell_width
                y1 = x * self.cell_height
                x2 = x1 + self.cell_width
                y2 = y1 + self.cell_height
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=c, outline="black")
                self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=t, fill="black")
                self.cell_colors[(x, y)] = c

    def _draw_matrix_borders(self):
        matrix_width = self.cols * self.cell_width
        matrix_height = self.rows * self.cell_height
        self.canvas.create_rectangle(0, 0, matrix_width, matrix_height, outline="black", width=2)

        for x in range(self.rows):
            for y in range(self.cols):
                color = "white"
                text = ""
                x1 = y * self.cell_width
                y1 = x * self.cell_height
                x2 = x1 + self.cell_width
                y2 = y1 + self.cell_height
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
                self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=text, fill="black")
                self.cell_colors[(x, y)] = color

    def draw_matrix(self):
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        cell_size = min(canvas_width // self.cols, canvas_height // self.rows)
        self.cell_width = self.cell_height = cell_size
        self.cell_colors = {}
        self._draw_matrix_borders()
        self._draw_matrix_cells()

    def random_color(self):
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    def show_popup(self, event):
        # Calculate the row and column of the cell under the mouse
        col = int(event.x // self.cell_width)
        row = int(event.y // self.cell_height)
        if 0 <= col < self.cols and 0 <= row < self.rows:
            l = self.arena.get_position(row, col)
            text_lst = [ f"{o.info(class_name=True, multi_line=True)}" for o in l ]
            text = "\n".join(text_lst)

            color = self.cell_colors.get((row, col), "white")
            # Create a popup message
            popup = tk.Toplevel(self.root)
            popup.wm_overrideredirect(True)
            popup.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            # label = tk.Label(popup, text=f"Cell ({row}, {col})\n{text}", background="yellow")
            label = tk.Label(popup, text=f"{text}", background="yellow")
            label.pack()
            popup.bind("<Motion>", lambda e: popup.destroy())

    def start(self):
        # self.log_message("Start button clicked")
        self.running = True
        self.step()

    def stop(self):
        # self.log_message("Stop button clicked")
        self.running = False

    def update_time_series(self):
        pass
        # self.time_series_plot.add_value(random.random())
        # self.root.after(1000, self.update_time_series)  # Update every second

    def log_message(self, message):
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)

    def on_resize(self, event):
        self.draw_matrix()

    def exit_application(self, event=None):
        self.root.quit()

    def update_display(self):
        self.clear_matrix()  # Clear the matrix before updating
        self.last_updates = self.arena.get_pos_obj_list()
        self.draw_matrix()  # Draw the matrix with the new updates

    def clear_matrix(self):
        self.canvas.delete("all")
        self.cell_colors.clear()

    def _single_step(self):
        self.step( force_1_step=True )
        self.running = False  # Stop the execution after a single step

    def step(self, force_1_step=False ):
        delta = time.time() - self.last_step_time
        if( delta < self.max_speed ):
            time.sleep( (self.max_speed - delta) )
            
        # random.shuffle(self.last_updates)
        if self.running or force_1_step:
            # self.log_message("step")
            # self.arena._move_objects_at_random()
            self.arena.run_step()
            self._msg()
            self._add_to_plot()
            self.update_display()
            self.update_time_series()
            if self.running:
                self.root.after(1, self.step)

    def _add_to_plot(self):
        # get the number of alive agents
        num_alive = len([obj for obj in self.arena.get_objects() if isinstance(obj, LivingAgent)])
        self.time_series_plot.add_value(num_alive)

    def _msg(self):
        self.log_message( f"## Epoch: {self.arena.epoch} ##" )
        for obj in sorted(self.arena.get_objects(), key=lambda x: x.nickname):
            if( isinstance(obj, LivingAgent) ):
                self.log_message( f"{obj.nickname}-{obj.info()}" )

    def run(self):
        self.root.mainloop()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Configuration", command=self.load_configuration)
        file_menu.add_command(label="Save Configuration", command=self.save_configuration)
        file_menu.add_command(label="Demo config", command=self.demo_config)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.exit_application)

    def load_configuration(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            self.from_configuration(file_path)

    def save_configuration(self):
        file_path = filedialog.asksaveasfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(self.arena.serialize(), file, indent=4)


    def demo_config(self):
        # arena = ppSlib.arena_demo.arena_demo( self.rows, self.cols )
        arena = arena_demo.load_demo( case = 1 )
        self.arena = arena
        self.update_display()
