import json
import os
import platform
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

from . import WORK_DIR
from .utils import EditorTable


class EnvironmentWindow:
    cache_file = os.path.join(WORK_DIR, "environment.json")
    data = {"Globals": {}}

    def __init__(self, master=None, **kwargs):
        self.callback = kwargs.get("callback")
        self.root = ttk.Frame(master)
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill=tk.X)
        ttk.Label(action_frame, text="Environment").pack(side=tk.LEFT)
        ttk.Button(action_frame, text="Add", command=self.on_add).pack(side=tk.RIGHT)
        self.treeview = ttk.Treeview(self.root, show="tree")
        self.treeview.pack(fill=tk.BOTH, expand=tk.YES)
        self.treeview.bind("<Double-1>", self.on_select)
        if platform.system() == "Darwin":
            self.treeview.bind("<Control-Button-1>",self.on_right_click)
            self.treeview.bind("<Button-2>", self.on_right_click)
        else:
            self.treeview.bind("<Button-3>", self.on_right_click)

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
            data = {"Globals": {}}

        self.treeview.insert("", tk.END, text="Globals", values=())
        for key in data:
            if key == "Globals":
                continue
            self.treeview.insert("", tk.END, text=key, values=())
        self.data = data

    def on_end(self):
        with open(self.cache_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.data))

    def on_select(self, event):
        if len(self.treeview.selection()) > 0:
            item_id = self.treeview.selection()[0]
            item = self.treeview.item(item_id)
            self.callback(
                collection=item["text"],
                data=self.data.get(item["text"], {}),
                item_id=item_id,
            )

    def on_right_click(self, event):
        item_id = self.treeview.identify_row(event.y)
        if item_id:
            self.treeview.selection_set(item_id)
            item = self.treeview.item(item_id)
            if item["text"] != "Globals":
                menu = tk.Menu(self.root, tearoff=0)
                menu.add_command(label="Delete", command=self.on_delete)
                menu.post(event.x_root, event.y_root)

    def on_add(self):
        name = simpledialog.askstring(
            "Add", prompt="Name", initialvalue="New Environment"
        )
        if name is not None and name in self.data:
            messagebox.showerror("Error", "Already exist")
            self.on_add()
        elif name is not None:
            self.data.update({name: {}})
            self.treeview.insert("", tk.END, text=name)

    def on_delete(self):
        if len(self.treeview.selection()) > 0:
            item_id = self.treeview.selection()[0]
            item = self.treeview.item(item_id)
            if item["text"] != "Globals":
                self.data.pop(item["text"])
                self.treeview.delete(self.treeview.selection())
            else:
                messagebox.showwarning("Warning", "non-deletable")

    def get_variable(self, collection, name):
        if collection in self.data:
            if name in self.data[collection]:
                return self.data[collection][name]
        return None

    def set_variable(self, collection, data):
        self.data.update({collection: data})


class VariableWindow:

    def __init__(self, master=None, **kwargs):
        self.root = ttk.Frame(master)
        edit_table = EditorTable(self.root, editable=True)
        save_btn = ttk.Button(
            self.root,
            command=lambda: kwargs.get("set_variable")(
                kwargs.get("collection"), edit_table.get_data()
            ),
            text="Save",
        )

        data = kwargs.get("data")
        if data is not None:
            edit_table.set_data(data)

        save_btn.pack(anchor="e")
        edit_table.pack(fill=tk.BOTH, expand=tk.YES)
