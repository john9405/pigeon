import json
import os
import platform
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

from . import WORK_DIR
from .utils import EditorTable


class EnvironmentWindow:
    cache_file = os.path.join(WORK_DIR, "environment.json")
    data = []

    def __init__(self, master=None, **kwargs):
        self.callback = kwargs.get("callback")
        self.root = ttk.Frame(master)
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill=tk.X)
        ttk.Button(action_frame, text="Add", command=self.on_add).pack(side=tk.RIGHT)
        self.treeview = ttk.Treeview(self.root, show='headings', columns=("name", "status"))
        self.treeview.column("#1", anchor="w", width=10)
        self.treeview.column("#2", anchor="center", width=2)
        self.treeview.heading("#1", text="Name", anchor="center")
        self.treeview.heading("#2", text="Status", anchor="center")
        self.treeview.pack(fill=tk.BOTH, expand=tk.YES)
        self.treeview.bind("<Double-1>", self.on_select)
        if platform.system() == "Darwin":
            self.treeview.bind("<Control-Button-1>", self.on_right_click)
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
                pass

        self.treeview.insert("", tk.END, values=("Globals", ""))
        for item in data:
            if item.get('name') == "Globals":
                continue
            self.treeview.insert("", tk.END, values=(
                item.get('name'),
                "@" if item.get('is_active') else ""
            ))
        self.data = data

    def on_end(self):
        with open(self.cache_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.data))

    def on_select(self, event):
        item_id = self.treeview.identify_row(event.y)
        if item_id:
            index = self.treeview.index(item_id)
            self.treeview.selection_set(item_id)
            self.callback(
                collection=self.data[index]['name'],
                data=self.data[index]['items'],
                item_id=item_id,
                index=index
            )

    def on_right_click(self, event):
        item_id = self.treeview.identify_row(event.y)
        if item_id:
            self.treeview.selection_set(item_id)
            item = self.treeview.item(item_id)
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Edit", command=lambda: self.on_select(event))
            if item["values"][0] != "Globals":
                menu.add_command(label="Active", command=lambda: self.set_active(item_id))
                menu.add_command(label="Delete", command=self.on_delete)
            menu.post(event.x_root, event.y_root)

    def on_add(self):
        name = simpledialog.askstring("Add", prompt="Name", initialvalue="New Environment")
        if name is not None:
            if name == "Globals":
                messagebox.showwarning("Warning", "Reserved words")
                return self.on_add()

            self.data.append({"name": name, "items": [], "is_active": False})
            self.treeview.insert("", tk.END, values=(name, ""))

    def on_delete(self):
        if len(self.treeview.selection()) > 0:
            item_id = self.treeview.selection()[0]
            item = self.treeview.item(item_id)
            if item["values"][0] != "Globals":
                self.data.pop(item["values"][0])
                self.treeview.delete(self.treeview.selection())
            else:
                messagebox.showwarning("Warning", "non-deletable")

    def set_variable(self, item_id, collection, data):
        index = self.treeview.index(item_id)
        is_active = self.data[index]['is_active']
        self.data[index].update({"name": collection, "items": data, 'is_active': is_active})
        self.treeview.item(item_id, values=(collection, "@" if is_active else ""))

    def set_active(self, item_id):
        item = self.treeview.item(item_id)
        if item["values"][0] == 'Globals':
            return
        index = self.treeview.index(item_id)
        # 去除活动标记
        for child_id in self.treeview.get_children():
            child = self.treeview.item(child_id)
            self.treeview.item(child_id, values=(child['values'][0], ""))
        for xtem in self.data:
            xtem['is_active'] = False
        # 标记活动
        self.treeview.item(item_id, values=(self.data[index]['name'], "@"))
        self.data[index]['is_active'] = True
        return

    def get_globals(self, name):
        for item in self.data:
            if item['name'] == 'Globals':
                for var in item['items']:
                    if var['name'] == name:
                        return var['value']
        return None

    def get_variable(self, name):
        for item in self.data:
            if item['is_active']:
                for var in item['items']:
                    if var['name'] == name:
                        return var['value']
        return None


class VariableWindow:

    def __init__(self, master=None, **kwargs):
        self.root = master
        frame = ttk.Frame(self.root)
        name = tk.StringVar(value=kwargs.get('collection'))
        ttk.Button(
            frame,
            command=lambda: self.on_save({
                "item_id": kwargs.get("item_id"),
                "collection": name.get(),
                "items": edit_table.get_data()
            }, kwargs.get("set_variable")),
            text="Save",
        ).pack(side=tk.RIGHT, padx=5)
        if kwargs.get("collection") != 'Globals':
            ttk.Label(frame, text="Name").pack(side=tk.LEFT)
            ttk.Entry(frame, textvariable=name).pack(side=tk.LEFT)
            ttk.Button(
                frame,
                text="Active",
                command=lambda: kwargs.get("set_active")(kwargs.get("item_id")),
            ).pack(side=tk.RIGHT)
        frame.pack(fill=tk.X)
        edit_table = EditorTable(self.root, editable=True)
        data = kwargs.get("data")
        if data is not None:
            edit_table.set_data({item['name']: item['value'] for item in data})
        edit_table.pack(fill=tk.BOTH, expand=tk.YES)

    def on_save(self, data, callback):
        data_list = []
        for key in data['items']:
            data_list.append({"name": key, "value": data['items'][key]})
        callback(data['item_id'], data['collection'], data_list)
