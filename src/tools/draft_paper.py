from tkinter import *
from tkinter.ttk import *
from tkinter.scrolledtext import ScrolledText


class DraftPaper:
    def __init__(self, master=None):
        root = Frame(master)
        root.pack(fill=BOTH, expand=True)
        Label(root, text='No content will be saved').pack(anchor='w')
        ScrolledText(root).pack(fill=BOTH, expand=True)
