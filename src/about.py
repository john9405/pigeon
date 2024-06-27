from tkinter import ttk
from tkinter.scrolledtext import ScrolledText


class AboutWindow:
    """关于窗口"""

    def __init__(self, master=None):
        root = ttk.Frame(master)
        self.root = root
        label = ScrolledText(root)
        label.insert('1.0', """
Http Client
0.0.1
""")
        label.configure(state='disabled')
        label.pack(fill='both', expand=True)
