import os
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from .. import BASE_DIR

class AboutWindow:
    """关于窗口"""

    def __init__(self, master=None):
        root = ttk.Frame(master)
        self.root = root
        with open(os.path.join(BASE_DIR, *("assets", "about.md")), "r", encoding="utf-8") as f:
            label = ScrolledText(root)
            label.insert('1.0', f.read())
            label.configure(state='disabled')
            label.pack(fill='both', expand=True)
