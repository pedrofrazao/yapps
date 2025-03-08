#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, messagebox
import random
import json
import sys
import os

dirname = os.path.dirname(__file__)
libpath = os.path.abspath(os.path.join(dirname, 'ppSlib'))
sys.path.append(libpath)

from ppSlib.matrix import MatrixGUI  # Import the MatrixGUI class
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


if __name__ == "__main__":
    
    # Load initial configuration
    app = MatrixGUI()

    app.update_display()
    app.run()
