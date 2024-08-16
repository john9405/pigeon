import platform
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from typing import Optional


class EditorTable(ttk.Frame):
    editable = False

    def __init__(self, master=None, **kw):
        self.editable = kw.pop("editable") if "editable" in kw else False
        super().__init__(master, **kw)

        self.treeview = ttk.Treeview(self, columns=("name", "value"), show="headings")        
        self.treeview.heading("name", text="name (+)" if self.editable else "name", anchor=tk.CENTER)
        self.treeview.heading("value", text="value", anchor=tk.CENTER)
        self.treeview.column("name", width=1)
        self.treeview.column("value")
        self.treeview.bind("<Button-1>", self.on_click)
        self.treeview.bind("<Double-1>", self.on_edit)
        if platform.system() == "Darwin":
            self.treeview.bind("<Control-Button-1>", self.on_right_click)
            self.treeview.bind("<Button-2>", self.on_right_click)
        else:
            self.treeview.bind("<Button-3>", self.on_right_click)
        scroll_x = ttk.Scrollbar(
            self, orient=tk.HORIZONTAL, command=self.treeview.xview
        )
        scroll_y = ttk.Scrollbar(self, command=self.treeview.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, scroll_x.winfo_reqheight()))
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.treeview.pack(fill=tk.BOTH, expand=tk.YES)

    def on_click(self, event):
        region = self.treeview.identify('region', event.x, event.y)
        if region == 'heading':
            column = self.treeview.identify_column(event.x)
            if column == '#1' and self.editable:
                self.on_add(event.x, event.y)

    def on_right_click(self, event):
        if self.editable:
            item = self.treeview.identify_row(event.y)
            self.treeview.selection_set(item)
            menu = tk.Menu(self, tearoff=False)
            if item:
                menu.add_command(label="Edit", command=lambda: self.on_edit(event))
                menu.add_command(label="Delete", command=self.on_del)
            else:
                menu.add_command(label="Add", command=lambda: self.on_add(event.x, event.y))
            menu.post(event.x_root, event.y_root)

    def on_add(self, x, y):
        if self.editable:
            self.editor(None, "", "", x, y)

    def on_edit(self, event):
        region = self.treeview.identify('region', event.x, event.y)
        if region != 'heading' and len(self.treeview.selection()) > 0:
            item_id = self.treeview.selection()[0]
            item = self.treeview.item(item_id)
            self.editor(item_id, item["values"][0], item["values"][1], event.x, event.y)

    def on_del(self):
        if self.editable and len(self.treeview.selection()) > 0:
            self.treeview.delete(self.treeview.selection()[0])

    def editor(self, item_id=None, name=None, value=None, x=0, y=0):
        x += self.winfo_rootx()
        y += self.winfo_rooty()

        win = tk.Toplevel(self)
        win.title("editor")
        win.geometry(f"+{x}+{y}")
        
        back = ttk.Frame(win)
        back.pack(fill=tk.BOTH, expand=tk.YES)

        frame = ttk.Frame(back)
        frame.pack(fill=tk.BOTH, expand=tk.YES, padx=10, pady=10)

        name_label = ttk.Label(frame, text="name")
        name_label.pack(anchor="w")
        name_entry = ttk.Entry(frame)
        if item_id:
            name_entry.insert('end', name)
        name_entry.pack(fill='x')

        value_label = ttk.Label(frame, text="value")
        value_label.pack(anchor="w")
        value_entry = ScrolledText(frame)
        if item_id:
            value_entry.insert('end', value)
        value_entry.pack()

        action_bar = ttk.Frame(frame)
        if self.editable:
            ttk.Button(
                action_bar,
                text="Submit",
                command=lambda: self.commit(item_id, win, name_entry, value_entry),
            ).pack(side="left")
        ttk.Button(action_bar, text="Cancel", command=win.destroy).pack(side="left")
        action_bar.pack(pady=(10, 0))

    def commit(
        self,
        item_id: Optional[str] = None,
        win: Optional[tk.Toplevel] = None,
        name_entry: Optional[ttk.Entry] = None,
        value_entry: Optional[ScrolledText] = None,
    ):
        name = name_entry.get()
        value = value_entry.get('1.0', "end")[:-1]
        if self.check_name(item_id, name):
            if item_id is None:
                self.treeview.insert("", tk.END, values=(name, value))
            else:
                self.treeview.item(item_id, values=(name, value))
            win.destroy()
        else:
            messagebox.showerror("error", "Duplicate key")

    def check_name(
        self, item_id: Optional[str] = None, name: Optional[str] = None
    ) -> bool:
        if name:
            for child in self.treeview.get_children():
                if child == item_id:
                    continue
                item = self.treeview.item(child)
                if str(item["values"][0]) == name:
                    return False
            return True
        return False

    def get_data(self) -> dict:
        data = {}
        for child in self.treeview.get_children():
            item = self.treeview.item(child)
            data.update({str(item["values"][0]): str(item["values"][1])})
        return data

    def set_data(self, data: dict):
        for key in data.keys():
            self.treeview.insert("", tk.END, values=(key, data[key]))

    def clear_data(self):
        self.treeview.delete(*self.treeview.get_children())
