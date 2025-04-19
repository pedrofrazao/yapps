import tkinter as tk
import random
import time
import pygame  # Import pygame for rendering
from time_series_plot import TimeSeriesPlot  # Import the TimeSeriesPlot class
from arena import Arena, ArenaObject
from ppSlib.agent import LivingAgent
import ppSlib.ArenaDemo as arena_demo
from tkinter import filedialog
# import ppSlib.matrix_config
import json
from ppSlib.yml_loader import YMLArenaLoader  # Import the YMLArenaLoader class
import os

imagesdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images'))

class MatrixGUI:
    def __init__(self, rows=16, cols=16):
        self.rows = rows
        self.cols = cols
        self.running = False
        self.last_updates = []  # Attribute to store the list of the last updates
        self.arena = Arena(rows, cols)
        # ## TEST ONLY
        # for i in range(1):
        #     obj = ArenaObject(f"Object{i}",arena=self.arena)
        #     self.arena.add_to_position(random.randint(0, rows-1), random.randint(0, cols-1), obj)
        # ## TEST ONLY
        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)  # Force full-screen mode
        self.max_speed = 1  # Maximum speed for the simulation
        self.last_step_time = 0  # Last time the step method was called
        root = self.root

        self.agent_images = {}  # Dictionary to store images for agent types
        self.pygame_initialized = False  # Track if pygame is initialized

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
        self.bind_mouse_events()  # Bind mouse events
        # Bind the keyboard shortcut to exit the application
        self.root.bind("<Control-q>", self.exit_application)


    def load_agent_images(self, imagesdir=imagesdir, agent_types=[]):
        """Load images for different agent types."""
        self.agent_images = {}
        for t in agent_types:
            try:
                self.agent_images[t] = pygame.image.load(f"{imagesdir}/{t}.png")
            except pygame.error as e:
                print(f"Error loading image for {t}: {e}")


    def init_pygame_canvas(self):
        """Initialize the pygame canvas."""
        if not self.pygame_initialized:
            self.root.update_idletasks()  # Ensure the tkinter canvas is fully initialized
            os.environ['SDL_WINDOWID'] = str(self.canvas.winfo_id())
            os.environ['SDL_VIDEODRIVER'] = 'x11'
            try:
                pygame.init()
                self.screen = pygame.display.set_mode((self.canvas.winfo_width(), self.canvas.winfo_height()))
                pygame.display.set_caption("Arena Visualization")
                self.pygame_initialized = True
                self.load_agent_images()
            except Exception as e:
                self.show_error_popup(f"Error initializing pygame: {e}")

    def draw_matrix(self):
        """Draw the arena using pygame."""
        self.init_pygame_canvas()
        self.screen.fill((255, 255, 255))  # Clear the screen with a white background

        cell_width = self.canvas.winfo_width() // self.cols
        cell_height = self.canvas.winfo_height() // self.rows

        for x in range(self.rows):
            for y in range(self.cols):
                pygame.draw.rect(
                    self.screen,
                    (200, 200, 200),  # Light gray for grid lines
                    pygame.Rect(y * cell_width, x * cell_height, cell_width, cell_height),
                    1  # Border width
                )

        for obj in self.arena.get_objects():
            pos = obj.getposition()
            if pos:
                x, y = pos
                otype = obj.species()
                if otype in self.agent_images:
                    image = pygame.transform.scale(self.agent_images[otype], (cell_width, cell_height))
                    self.screen.blit(image, (y * cell_width, x * cell_height))
                else:
                    pygame.draw.rect(
                        self.screen,
                        (0, 0, 255),  # Default blue color for unknown agents
                        pygame.Rect(y * cell_width, x * cell_height, cell_width, cell_height)
                    )

                # Draw a red dot indicating the direction
                direction = obj.direction()
                if direction is not None and direction not in (0,5):  # Skip if no direction
                    dot_x, dot_y = self.get_dot_position(direction, x, y, cell_width, cell_height)
                    pygame.draw.circle(self.screen, (255, 0, 0), (dot_x, dot_y), 5)  # Red dot with radius 5

        pygame.display.update()

    def get_dot_position(self, direction, row, col, cell_width, cell_height):
        """Calculate the position of the red dot based on the direction."""
        x1 = col * cell_width
        y1 = row * cell_height
        x2 = x1 + cell_width
        y2 = y1 + cell_height

        if direction == 1:  # Top left
            return x1 + 5, y1 + 5
        elif direction == 2:  # Top
            return (x1 + x2) // 2, y1 + 5
        elif direction == 3:  # Top right
            return x2 - 5, y1 + 5
        elif direction == 4:  # Left
            return x1 + 5, (y1 + y2) // 2
        elif direction == 6:  # Right
            return x2 - 5, (y1 + y2) // 2
        elif direction == 7:  # Bottom left
            return x1 + 5, y2 - 5
        elif direction == 8:  # Bottom
            return (x1 + x2) // 2, y2 - 5
        elif direction == 9:  # Bottom right
            return x2 - 5, y2 - 5
        return None, None  # No dot for direction 5

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

    def show_popup(self, event, secondary=False):
        """Show a popup with information about the cell clicked."""
        # Calculate the row and column of the cell under the mouse
        col = int(event.x // (self.canvas.winfo_width() // self.cols))
        row = int(event.y // (self.canvas.winfo_height() // self.rows))
        if 0 <= col < self.cols and 0 <= row < self.rows:
            # Get objects at the clicked position
            objects = self.arena.get_position(row, col)
            if not objects:
                return

            # Prepare the text for the popup
            if secondary:
                text_lst = [f"Extra Info:\n{obj.info(class_name=True, multi_line=True)}\n{obj.extra_info()}" for obj in objects]
            else:
                text_lst = [f"{obj.info(class_name=True, multi_line=True)}" for obj in objects]
            text = "\n".join(text_lst)

            # Create a popup window
            popup = tk.Toplevel(self.root)
            popup.wm_overrideredirect(True)
            popup.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            label = tk.Label(popup, text=text, background="yellow", justify="left")
            label.pack()
            popup.bind("<Motion>", lambda e: popup.destroy())

    def bind_mouse_events(self):
        """Bind mouse events for primary and secondary buttons."""
        self.canvas.bind("<Button-1>", lambda event: self.show_popup(event, secondary=False))  # Primary button
        self.canvas.bind("<Button-3>", lambda event: self.show_popup(event, secondary=True))   # Secondary button

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
        """Handle window resize events."""
        if self.pygame_initialized:
            self.screen = pygame.display.set_mode((self.canvas.winfo_width(), self.canvas.winfo_height()))
        self.draw_matrix()

    def exit_application(self, event=None):
        """Exit the application and clean up pygame."""
        if self.pygame_initialized:
            pygame.quit()
        self.root.quit()

    def update_display(self):
        self.last_updates = self.arena.get_pos_obj_list()
        self.draw_matrix()  # Draw the matrix with the new updates

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
        # num_alive = len([obj for obj in self.arena.get_objects() if isinstance(obj, LivingAgent)])
        c = self.arena.get_count_by_object_type()
        for k,v in c.items():
            self.time_series_plot.add_value(v, k)


    def _msg(self):
        self.log_message( f"##### Epoch: {self.arena.epoch} #####" )
        for obj in sorted(self.arena.get_objects(), key=lambda x: x.nickname):            
            if( isinstance(obj, LivingAgent) ):
                str = obj.info( onlywithmessage=True )
                if str is None:
                    continue
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


    def load_configuration(self,file_path=None):
        if file_path is None:
            file_path = filedialog.askopenfilename(filetypes=[("YAML files", "*.yml *.yaml")])

        if file_path:
            try:
                self.arena = YMLArenaLoader.load_arena_from_yml(file_path)
                self.rows = self.arena.rows
                self.cols = self.arena.cols
                self.load_agent_images(agent_types=self.arena.get_object_types())
            except Exception as e:
                self.show_error_popup(f"Error loading YAML configuration: {e}")

            # check object types
            object_types = self.arena.get_object_types()
            if not object_types:
                self.show_error_popup("No object types found in the configuration.")
                return

            self.object_types = object_types
            # create a new time series object
            self.reset_plot(object_types)
            for otype in object_types:
                self.time_series_plot.add_series(otype)

            self.update_display()

    def reset_plot(self, object_types=None, start_time=0, end_time=100):
        """Reset the plot frame and create a new TimeSeriesPlot with the specified object types"""
        # Destroy the existing plot frame if it exists
        if self.plot_frame:
            self.plot_frame.destroy()
        
        # Create a new plot frame
        self.plot_frame = tk.Frame(self.left_frame, height=int(self.root.winfo_screenheight() / 4))
        self.plot_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Create a new time series plot
        self.time_series_plot = TimeSeriesPlot(self.plot_frame, start_time=start_time, end_time=end_time)
        
        # Add series for each object type
        if object_types:
            for otype in object_types:
                self.time_series_plot.add_series(otype)
                
        # Remove the default series if it exists
        try:
            self.time_series_plot.remove_series("default")
        except:
            pass

    def save_configuration(self):
        file_path = filedialog.asksaveasfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(self.arena.serialize(), file, indent=4)


    def demo_config(self):
        # arena = ppSlib.arena_demo.arena_demo( self.rows, self.cols )
        arena = arena_demo.load_demo( case = 0 )
        self.arena = arena
        self.update_display()
