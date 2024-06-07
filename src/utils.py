import tkinter as tk
from tkinter import ttk


class EditorTable(ttk.Frame):
    def __init__(self, **kw) -> None:
        toolbar = ttk.Frame(self)
        add_btn = ttk.Button(toolbar, text="add", command=self.on_add)
        add_btn.pack(side="left")
        edit_btn = ttk.Button(toolbar, text="edit", command=self.on_edit)
        edit_btn.pack(side="left")
        delete_btn = ttk.Button(toolbar, text="delete", command=self.on_del)
        delete_btn.pack(side="left")
        toolbar.pack(fill="x")
        self.treeview = ttk.Treeview(self, columns=("name", "value"), show="headings")

    def on_add(self):
        pass

    def on_edit(self):
        pass

    def on_del(self):
        pass

    def editor(self, item_id=None, name=None, value=None):
        win = tk.Toplevel()
        win.title("editor")
        win.geometry("400x200")

        name_label = ttk.Label(win, text="name")
        name_label.pack()
        name_entry = ttk.Entry(win)
        name_entry.insert(0, name)
        name_entry.pack()
        value_label = ttk.Label(win, text="value")
        value_label.pack()
        value_entry = ttk.Entry(win)
        value_entry.insert(0, value)
        value_entry.pack()
        
        action_bar = ttk.Frame(win)
        ttk.Button(action_bar, text="save", command=lambda: self.commit()).pack()
        ttk.Button(action_bar, text="cancel", command=lambda: win.destroy()).pack()
        action_bar.pack(fill="x")
        
    
    def commit(self, win):
        pass

    def get_data(self) -> dict:
        pass

    def set_data(self, data: dict):
        pass
