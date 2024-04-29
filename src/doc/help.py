import tkinter as tk
from tkinter import ttk

class HelpWindow:
    """帮助窗口"""

    def __init__(self, master=None):
        root = tk.Toplevel(master)
        
        with open("help.md", "r", encoding="utf-8") as f:
            label = ttk.Label(root, text=f.read())
            label.pack()
