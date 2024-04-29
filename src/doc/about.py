import tkinter as tk
from tkinter import ttk


class AboutWindow:
    """关于窗口"""

    def __init__(self, master=None):
        root = tk.Toplevel(master)

        with open("about.md", "r", encoding="utf-8") as f:
            label = ttk.Label(root, text=f.read())
            label.pack()
