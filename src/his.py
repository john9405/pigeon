import tkinter as tk
from tkinter import ttk

class HistoryWindow:
    """History window"""

    def __init__(self, window, callback=None):
        self.window = window
        self.callback = callback
        ff = ttk.Frame(window)
        ff.pack(fill=tk.X)
        ttk.Label(ff, text="History").pack(side=tk.LEFT)
        ttk.Button(ff, text="Clear", command=self.clear).pack(side="right")
        self.history_box = tk.Listbox(window)
        scrollbar = ttk.Scrollbar(window, command=self.history_box.yview)
        sbx = ttk.Scrollbar(
            window, command=self.history_box.xview, orient=tk.HORIZONTAL
        )
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT, pady=(0, sbx.winfo_reqheight()))
        sbx.pack(side=tk.BOTTOM, fill=tk.X)
        self.history_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)

        self.menu = tk.Menu(window, tearoff=0)
        self.menu.add_command(label="Delete", command=self.on_delete)
        self.history_box.bind("<Double-Button-1>", self.on_select)
        self.history_box.bind("<Button-3>", self.popup_menu)
        self.history_box.config(yscrollcommand=scrollbar.set, xscrollcommand=sbx.set)

    def popup_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def log(self, data):
        self.history_box.insert(0, data)

    def clear(self):
        self.history_box.delete(0, tk.END)

    def on_delete(self):
        selection = self.history_box.curselection()
        if selection:
            print(selection)
            self.history_box.delete(selection)
            self.callback("destroy", **{"index": selection[0]})

    def on_clear(self):
        self.clear()
        self.callback("clear")

    def on_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            self.callback("select", **{"index": index})

    def on_start(self):
        pass

    def on_end(self):
        pass
    
    def on_cache(self, data):
        pass
