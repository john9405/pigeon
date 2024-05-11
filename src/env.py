import json
import os
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

from . import WORK_DIR, BASE_DIR


class EnvironmentWindow:
    cache_file = os.path.join(WORK_DIR, "environment.json")
    data = {"Globals": {}}

    def __init__(self, master=None, **kwargs):
        self.callback = kwargs.get("callback")
        self.root = ttk.Frame(master)
        self.images = [
            tk.PhotoImage(
                name="add",
                file=os.path.join(BASE_DIR, *("assets", "16", "add.png")),
                height=16,
                width=16
            ),
            tk.PhotoImage(
                name="delete",
                file=os.path.join(BASE_DIR, *("assets", "16", "delete.png")),
                height=16,
                width=16
            )
        ]
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill=tk.X)
        ttk.Button(action_frame, image="delete", command=self.on_delete).pack(side=tk.RIGHT)
        ttk.Button(action_frame, image="add", command=self.on_add).pack(side=tk.RIGHT)
        self.treeview = ttk.Treeview(self.root, show="tree")
        self.treeview.pack(fill=tk.BOTH, expand=tk.YES)
        self.treeview.bind("<Double-1>", self.on_select)

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

    def on_add(self):
        name = simpledialog.askstring("Add", prompt="Name", initialvalue="New Environment")
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

    def set_variable(self, collection, name, value):
        if collection in self.data:
            self.data[collection].update({name: value})
        else:
            self.data.update({collection: {name: value}})

    def del_variable(self, collection, name):
        if collection in self.data:
            if name in self.data[collection]:
                self.data[collection].pop(name)


class VariableWindow:

    def __init__(self, master=None, **kwargs):
        self.root = ttk.Frame(master)
        self.images = [
            tk.PhotoImage(
                name="add",
                file=os.path.join(BASE_DIR, *("assets", "16", "add.png")),
                height=16,
                width=16
            ),
            tk.PhotoImage(
                name="edit",
                file=os.path.join(BASE_DIR, *("assets", "16", "edit.png")),
                height=16,
                width=16
            ),
            tk.PhotoImage(
                name="delete",
                file=os.path.join(BASE_DIR, *("assets", "16", "delete.png")),
                height=16,
                width=16
            )
        ]
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X)
        ttk.Button(toolbar, image='delete', command=self.on_delete).pack(side=tk.RIGHT)
        ttk.Button(toolbar, image="edit", command=self.on_edit).pack(side=tk.RIGHT)
        ttk.Button(toolbar, image="add", command=self.on_add).pack(side=tk.RIGHT)

        self.treeview = ttk.Treeview(
            self.root,
            columns=("name","value"),
            show="headings",
        )
        self.treeview.pack(fill=tk.BOTH, expand=tk.YES)

        self.treeview.heading("name", text="name", anchor=tk.CENTER)
        self.treeview.heading("value", text="value", anchor=tk.CENTER)

        self.treeview.column("name", width=100, anchor=tk.CENTER)
        self.treeview.column("value", width=100, anchor=tk.CENTER)

        data = kwargs.get("data")
        if data is not None:
            for item in data.items():
                self.treeview.insert("", tk.END, values=item)

        self.del_variable = kwargs.get('del_variable')
        self.set_variable = kwargs.get('set_variable')
        self.collection = kwargs.get('collection')

    def on_add(self):
        self.editor()

    def on_edit(self):
        if len(self.treeview.selection()) > 0:
            item_id = self.treeview.selection()[0]
            item = self.treeview.item(item_id)
            self.editor(item_id, name=item['values'][0], value=item['values'][1])

    def on_delete(self):
        if len(self.treeview.selection()) > 0:
            item_id = self.treeview.selection()[0]
            item = self.treeview.item(item_id)
            self.del_variable(self.collection, item['values'][0])
            self.treeview.delete(self.treeview.selection())

    def editor(self, item_id=None, name=None, value=None):
        def on_submit():
            name = name_entry.get()
            value = value_entry.get()
            if item_id is None:
                self.treeview.insert("", tk.END, values=(name, value))
            else:
                self.treeview.item(item_id, values=(name, value))
            self.set_variable(self.collection, name, value)
            win.destroy()

        win = tk.Toplevel()
        win.title("Edit")

        name_frame = ttk.Frame(win)
        name_frame.pack()
        name_label = ttk.Label(name_frame, text='Name:')
        name_label.pack(side=tk.LEFT)
        name_entry = ttk.Entry(name_frame)
        if name is not None:
            name_entry.insert(0, name)
        name_entry.pack(side=tk.LEFT)
        value_frame = ttk.Frame(win)
        value_frame.pack()
        value_label = ttk.Label(value_frame, text="Value:")
        value_label.pack(side=tk.LEFT)
        value_entry = ttk.Entry(value_frame)
        if value is not None:
            value_entry.insert(0, value)
        value_entry.pack(side=tk.LEFT)
        action_frame = ttk.Frame(win)
        action_frame.pack()
        can_btn = ttk.Button(action_frame, command=win.destroy, text="Cannel")
        can_btn.pack(side=tk.RIGHT)
        sub_btn = ttk.Button(action_frame, command=on_submit, text="Submit")
        sub_btn.pack(side=tk.RIGHT)
