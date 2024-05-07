import json
import os
import tkinter as tk
from tkinter import ttk

from . import WORK_DIR


class EnvironmentWindow:
    cache_file = os.path.join(WORK_DIR, "environment.json")
    data = {"Globals": {}}

    def __init__(self, master=None, **kwargs):
        self.callback = kwargs.get('callback')
        self.root = ttk.Frame(master)
        self.treeview = ttk.Treeview(self.root, show="tree")
        self.treeview.pack(fill=tk.BOTH, expand=tk.YES)

    def on_start(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r", encoding="utf-8") as f:
                data = f.read()
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                data = {"Globals": {}}
            if "Globals" not in data:
                data.update({"Globals": {}})
        else:
            data =  {"Globals": {}}

        self.treeview.insert("", tk.END, text="Globals", values=())
        for key in data:
            if key == "Globals":
                continue
            self.treeview.insert("", tk.END, text=key, values=())
        self.data = data

    def on_end(self):
        with open(self.cache_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.data))

    def on_select(self):
        pass

    def on_save(self):
        pass

    def on_delete(self):
        pass

    def get_variable(self, collection, name):
        if collection in self.data:
            if name in self.data[collection]:
                return self.data[collection][name]
        return None

    def set_variable(self, collection, name, value):
        if collection in self.data:
            self.data[collection].update({name: value})
        else:
            self.data.update({collection: {name: value}})


class VariableWindow:

    def __init__(self, master=None, **kwargs):
        self.root = ttk.Frame(master)
        ff = ttk.Frame(self.root)
        ff.pack(fill=tk.X)
        ttk.Button(ff, text="Save", command=self.on_save).pack(side=tk.LEFT)
        self.treeview = ttk.Treeview(self.root, columns=("name", "value",))
        self.treeview.pack(fill=tk.BOTH, expand=tk.YES)
        
        data = kwargs.get('data')
        if data is not None:
            for (k, v) in data.items():
                pass

    def on_save(self):
        pass
