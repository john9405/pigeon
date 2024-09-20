import os
import json
import platform
import uuid
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

        self.history_box = tk.Listbox(window)
        scrollbar = ttk.Scrollbar(window, command=self.history_box.yview)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.history_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)

        self.history_box.bind("<Double-Button-1>", self.on_select)
        if platform.system() == "Darwin":
            self.history_box.bind("<Control-Button-1>", self.on_right_click)
            self.history_box.bind("<Button-2>", self.on_right_click)
        else:
            self.history_box.bind("<Button-3>", self.on_right_click)
        self.history_box.config(yscrollcommand=scrollbar.set)

    def on_delete(self):
        selection = self.history_box.curselection()
        if selection:
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
            if 'uuid' not in self.history_list[i]:
                self.history_list[i].update({"uuid": str(uuid.uuid1())})
            self.callback(data=self.history_list[i])

    def on_right_click(self, event):
        self.history_box.selection_clear(0, tk.END)
        index = self.history_box.nearest(event.y)
        self.history_box.selection_set(index)
        menu = tk.Menu(self.window, tearoff=0)
        menu.add_command(label="Open", command=lambda: self.on_select(event))
        menu.add_command(label="Delete", command=self.on_delete)
        menu.add_command(label="Clear", command=self.on_clear)
        menu.post(event.x_root, event.y_root)

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
                    self.history_box.insert(0, f"{item.get('method' '')} {item.get('url', '')}")

    def on_end(self):
        with open(self.cache_file, "w", encoding="utf-8") as file:
            file.write(json.dumps(self.history_list))

    def on_cache(self, data):
        data.update({"uuid": str(uuid.uuid1())})
        self.history_list.append(data)
        self.history_box.insert(0, f"{data.get('method' '')} {data.get('url', '')}")
