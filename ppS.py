#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, messagebox
import random
import json
import sys
import os
import argparse  # Import argparse for command-line argument parsing

dirname = os.path.dirname(__file__)
libpath = os.path.abspath(os.path.join(dirname, 'ppSlib'))
sys.path.append(libpath)

from ppSlib.matrix import MatrixGUI  # Import the MatrixGUI class
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run the ppS simulation.")
    parser.add_argument('-f', '--file', type=str, help='File to load the arena from')
    args = parser.parse_args()

    # Initialize the application
    app = MatrixGUI()

    # Load the configuration file if provided
    if args.file:
        if os.path.exists(args.file):
            app.load_configuration(args.file)
        else:
            print(f"Error: File '{args.file}' does not exist.")
            sys.exit(1)

    # Run the application
    app.update_display()
    app.run()


if __name__ == "__main__":
    main()
