import os
import json
import tkinter as tk
from tkinter import ttk

from . import WORK_DIR

class HistoryWindow:
    """History window"""
    history_list = []  # History list
    cache_file = os.path.join(WORK_DIR, "history.json")

    def __init__(self, window, callback=None):
        self.window = window
        self.callback = callback
        ff = ttk.Frame(window)
        ff.pack(fill=tk.X)
        ttk.Label(ff, text="History").pack(side=tk.LEFT)
        ttk.Button(ff, text="Clear", command=self.on_clear).pack(side="right")
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

    def on_delete(self):
        selection = self.history_box.curselection()
        if selection:
            print(selection)
            self.history_box.delete(selection)
            i = len(self.history_list) - selection[0] - 1
            self.history_list.pop(i)

    def on_clear(self):
        self.history_box.delete(0, tk.END)
        self.history_list = []

    def on_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            i = len(self.history_list) - index - 1
            data = self.history_list[i]
            self.callback("select", **{"data": data})

    def on_start(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r", encoding="utf-8") as file:
                try:
                    data = file.read()
                    data = json.loads(data)
                except json.JSONDecodeError:
                    return
                self.history_box.delete(0, tk.END)
                for item in data:
                    self.history_list.append(item)
                    self.log(f"{item.get('method' '')} {item.get('url', '')}")

    def on_end(self):
        with open(self.cache_file, "w", encoding="utf-8") as file:
            file.write(json.dumps(self.history_list))

    def on_cache(self, data):
        self.history_list.append(data)
        self.log(f"{data.get('method' '')} {data.get('url', '')}")
