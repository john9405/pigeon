import json
import os
import tkinter as tk
import uuid
from tkinter import ttk, filedialog, messagebox

from . import WORK_DIR, USER_DIR, BASE_DIR


class CollectionWindow:
    cmenu = None

    def __init__(self, window, callback=None):
        self.window = window
        self.callback = callback
        self.images = [
            tk.PhotoImage(
                name="add",
                file=os.path.join(BASE_DIR, *("assets", "16", "add.png")),
                height=16,
                width=16
            ),
            tk.PhotoImage(
                name="import",
                file=os.path.join(BASE_DIR, *("assets", "16", "import.png")),
                height=16,
                width=16
            )
        ]
        frame = ttk.Frame(window)
        ttk.Button(frame, image="import", command=self.open_proj).pack(
            side=tk.RIGHT
        )
        ttk.Button(frame, image="add", command=self.new_proj).pack(
            side=tk.RIGHT
        )
        
        frame.pack(fill=tk.X)
        self.tree = ttk.Treeview(window, show="tree")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_select)
        self.tree.bind("<Button-1>", self.hide_context_menu)
        self.tree.bind("<Button-3>", self.on_right_click)

        self.context_nenu = tk.Menu(window, tearoff=0)
        self.context_nenu.add_command(label="new Project", command=self.new_proj)
        # project
        self.proj_menu = tk.Menu(window, tearoff=0)
        self.proj_menu.add_command(label="Open in tab", command=self.on_open)
        self.proj_menu.add_command(label="new folder", command=self.new_col)
        self.proj_menu.add_command(label="new request", command=self.new_req)
        self.proj_menu.add_command(label="Export", command=self.export_proj)
        self.proj_menu.add_command(label="Delete", command=self.delete_item)
        # folder
        self.folder_menu = tk.Menu(window, tearoff=0)
        self.folder_menu.add_command(label="Open in tab", command=self.on_open)
        self.folder_menu.add_command(label="new folder", command=self.new_col)
        self.folder_menu.add_command(label="new request", command=self.new_req)
        self.folder_menu.add_command(label="Delete", command=self.delete_item)
        # request
        self.req_menu = tk.Menu(window, tearoff=0)
        self.req_menu.add_command(label="Open in tab", command=self.on_open)
        self.req_menu.add_command(label="Delete", command=self.delete_item)

    def open_proj(self):
        """open a program"""
        filepath = filedialog.askopenfilename(
            filetypes=(("Json files", "*.json"),), initialdir=USER_DIR
        )
        if filepath:
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    data = json.loads(f.read())
                    self.show_proj(data)
                except json.JSONDecodeError:
                    messagebox.showerror("Error", "The text content must be a json")

    def show_proj(self, data):
        item = None
        if "item" in data:
            item = data.pop("item")

        node = self.tree.insert(
            "",
            tk.END,
            text=data["name"],
            values=[json.dumps(data)],
            open=False,
            tags=["project", str(uuid.uuid1())],
        )

        if item is not None:
            self.show_item(node, item)

    def show_item(self, node, items):
        for item in items:
            if "item" in item:
                childitem = item.pop("item")
                cnode = self.tree.insert(
                    node,
                    tk.END,
                    text=item["name"],
                    values=[json.dumps(item)],
                    open=False,
                    tags=["folder", str(uuid.uuid1())],
                )
                if len(childitem) > 0:
                    self.show_item(cnode, childitem)
            else:
                self.tree.insert(
                    node,
                    tk.END,
                    text=item["method"] + " " + item["name"],
                    values=[json.dumps(item)],
                    tags=["request", str(uuid.uuid1())],
                )

    def export_proj(self):
        """save program"""
        item = self.tree.item(self.tree.selection()[0])
        bean = json.loads(item["values"][0])

        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("json files", "*.json")],
            initialdir=USER_DIR,
            initialfile=bean["name"] + ".json",
        )
        if filepath:
            with open(filepath, "w", encoding="utf-8") as file:
                bean.update({"item": self.traverse_children(self.tree.selection()[0])})
                file.write(json.dumps(bean, ensure_ascii=False, indent=4))

    def traverse_children(self, item):
        long_bean = []
        children = self.tree.get_children(item)
        for child in children:
            # Process the child item
            bean = self.tree.item(child)
            value = json.loads(bean["values"][0])
            if bean["tags"][0] == "folder":
                # Recursive call for further traversal
                value.update({"item": self.traverse_children(child)})
            long_bean.append(value)
        return long_bean

    def on_select(self, event):
        try:
            item_id = self.tree.selection()[0]
            item = self.tree.item(item_id)
            ctag = item["tags"][0]
            values = json.loads(item["values"][0])
            self.callback(
                data=values,
                tag=ctag,
                request_id=item["tags"][1],
                active="newitem",
                item_id=item_id,
            )
        except IndexError:
            pass

    def on_open(self):
        self.on_select(None)

    def on_right_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            tag = self.tree.item(item)["tags"][0]
            if tag == "project":
                self.proj_menu.post(event.x_root, event.y_root)
                self.cmenu = self.proj_menu
            elif tag == "folder":
                self.folder_menu.post(event.x_root, event.y_root)
                self.cmenu = self.folder_menu
            elif tag == "request":
                self.req_menu.post(event.x_root, event.y_root)
                self.cmenu = self.req_menu
        else:
            self.context_nenu.post(event.x_root, event.y_root)
            self.cmenu = self.context_nenu

    def hide_context_menu(self, event):
        if self.cmenu:
            self.cmenu.unpost()
            self.cmenu = None

    def new_proj(self):
        self.tree.insert(
            "",
            tk.END,
            text="New Collection",
            tags=["project", str(uuid.uuid1())],
            values=[json.dumps({"name": "New Collection"})],
        )

    def new_col(self):
        try:
            ctag = self.tree.item(self.tree.selection()[0])["tags"][0]
            if ctag in ("folder", "project"):
                selected_node = self.tree.selection()[0]
            else:
                selected_node = self.tree.parent(self.tree.selection()[0])
            self.tree.insert(
                selected_node,
                tk.END,
                text="New Folder",
                tags=["folder", str(uuid.uuid1())],
                values=[json.dumps({"name": "New Folder"})],
            )
        except IndexError:
            self.tree.insert(
                "",
                tk.END,
                text="New Collection",
                tags=["project", str(uuid.uuid1())],
                values=[json.dumps({"name": "New Collection"})],
            )

    def new_req(self, data=None):
        if data is None:
            data = {
                "name": "New Request",
                "method": "GET",
                "url": "",
                "params": {},
                "headers": {},
                "body": {},
                "pre_request_script": "",
                "tests": "",
            }
        try:
            ctag = self.tree.item(self.tree.selection()[0])["tags"][0]
            if ctag in ("folder", "project"):
                selected_node = self.tree.selection()[0]
            else:
                selected_node = self.tree.parent(self.tree.selection()[0])

            x = self.tree.insert(
                selected_node,
                tk.END,
                text=data.get("method") + " " + data.get("name"),
                tags=["request", str(uuid.uuid1())],
                values=[json.dumps(data)],
            )
            return x
        except IndexError:
            messagebox.showerror("Error", "Save error, please select folder.")

    def save_item(self, item_id, data):
        if item_id is None:
            return self.new_req(data)

        item = self.tree.item(item_id)
        ctag = item["tags"][0]
        self.tree.item(
            item_id,
            text=(
                data["method"] + " " + data["name"]
                if ctag == "request"
                else data["name"]
            ),
            values=[json.dumps(data)],
        )
        return item_id

    def delete_item(self):
        selected_node = self.tree.selection()
        if selected_node:
            self.tree.delete(selected_node)

    def on_start(self):
        """Read data from the workspace"""
        filepath = os.path.join(WORK_DIR, "workspace.json")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    data = f.read()
                    data = json.loads(data)
                    for proj in data:
                        self.show_proj(proj)
                except json.JSONDecodeError:
                    pass

    def on_close(self):
        """auto save"""
        proj_list = []
        children = self.tree.get_children()
        for child in children:
            bean = self.tree.item(child)
            value = json.loads(bean["values"][0])
            value.update({"item": self.traverse_children(child)})
            proj_list.append(value)
        filepath = os.path.join(WORK_DIR, "workspace.json")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(json.dumps(proj_list))

    def get_script(self, item_id):
        if self.tree.parent(item_id):
            scripts_list = []
            item = self.tree.item(self.tree.parent(item_id))
            value = json.loads(item["values"][0])
            scripts_list.append(
                {
                    "pre_request_script": value.get("pre_request_script", ""),
                    "tests": value.get("tests", ""),
                }
            )
            x = self.get_script(self.tree.parent(item_id))
            scripts_list += x
            return scripts_list
        return []

    def get_variable(self, item_id, name):
        if self.tree.parent(item_id):
            item = self.tree.item(self.tree.parent(item_id))
            if item["tags"][0] == 'project':
                value = json.loads(item['values'][0])
                for var in value.get("variable", []):
                    if var['name'] == name:
                        return var['value']
                return None
            return self.get_variable(item_id, name)


class ProjectWindow:
    def __init__(self, **kwargs) -> None:
        self.root = ttk.Frame(kwargs.get("master"))
        self.callback = kwargs.get("callback")
        self.item_id = kwargs.get("item_id")
        data = kwargs.get('data')

        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.X)
        ttk.Label(frame, text="Name:").pack(side=tk.LEFT)
        self.name_entry = ttk.Entry(frame)
        self.name_entry.insert(tk.END, data.get("name", "New Folder"))
        self.name_entry.pack(side=tk.LEFT)
        save_btn = ttk.Button(frame, text="Save", command=self.on_save)
        save_btn.pack(side=tk.RIGHT)

        notebook = ttk.Notebook(self.root)
        # pre-request script
        script_frame = ttk.Frame(notebook)
        self.script_box = tk.Text(script_frame, height=12)
        self.script_box.insert(tk.END, data.get("pre_request_script", ""))
        self.script_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        script_scrollbar = ttk.Scrollbar(script_frame, command=self.script_box.yview)
        script_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.script_box.config(yscrollcommand=script_scrollbar.set)
        notebook.add(script_frame, text="Pre-request Script")

        # tests
        tests_frame = ttk.Frame(notebook)
        self.tests_box = tk.Text(tests_frame, height=12)
        self.tests_box.insert(tk.END, data.get("tests", ""))
        self.tests_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        tests_scrollbar = ttk.Scrollbar(tests_frame, command=self.tests_box.yview)
        tests_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.tests_box.config(yscrollcommand=tests_scrollbar.set)
        notebook.add(tests_frame, text="Tests")

        variable_frame = ttk.Frame(notebook)
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
        toolbar = ttk.Frame(variable_frame)
        toolbar.pack(fill=tk.X)
        ttk.Button(toolbar, image='delete', command=self.on_delete).pack(side=tk.RIGHT)
        ttk.Button(toolbar, image="edit", command=self.on_edit).pack(side=tk.RIGHT)
        ttk.Button(toolbar, image="add", command=self.on_add).pack(side=tk.RIGHT)
        self.treeview = ttk.Treeview(variable_frame, columns=("name", "value"), show="headings")
        self.treeview.pack(fill=tk.BOTH, expand=tk.YES)
        self.treeview.heading("name", text="name", anchor=tk.CENTER)
        self.treeview.heading("value", text="value", anchor=tk.CENTER)
        self.treeview.column("name", width=100, anchor=tk.CENTER)
        self.treeview.column("value", width=100, anchor=tk.CENTER)
        for item in data.get("variable", []):
            self.treeview.insert("", tk.END, values=(item['name'], item['value']))
        notebook.add(variable_frame, text="Variable")
        notebook.pack(expand=tk.YES, fill=tk.BOTH)

    def on_add(self):
        self.editor()

    def on_edit(self):
        if len(self.treeview.selection()) > 0:
            item_id = self.treeview.selection()[0]
            item = self.treeview.item(item_id)
            self.editor(item_id, name=item['values'][0], value=item['values'][1])
    
    def on_delete(self):
        self.treeview.delete(self.treeview.selection())
    
    def editor(self, item_id=None, name=None, value=None):
        def on_submit():
            name = name_entry.get()
            value = value_entry.get()
            if item_id is None:
                self.treeview.insert("", tk.END, values=(name, value))
            else:
                self.treeview.item(item_id, values=(name, value))
            win.destroy()

        win = tk.Toplevel()
        win.title("Edit")

        name_frame = ttk.Frame(win)
        name_frame.pack(fill=tk.X)
        name_label = ttk.Label(name_frame, text='Name:')
        name_label.pack(side=tk.LEFT)
        name_entry = ttk.Entry(name_frame)
        if name is not None:
            name_entry.insert(0, name)
        name_entry.pack(side=tk.RIGHT)
        value_frame = ttk.Frame(win)
        value_frame.pack(fill=tk.X)
        value_label = ttk.Label(value_frame, text="Value:")
        value_label.pack(side=tk.LEFT)
        value_entry = ttk.Entry(value_frame)
        if value is not None:
            value_entry.insert(0, value)
        value_entry.pack(side=tk.RIGHT)
        action_frame = ttk.Frame(win)
        action_frame.pack()
        can_btn = ttk.Button(action_frame, command=win.destroy, text="Cannel")
        can_btn.pack(side=tk.RIGHT)
        sub_btn = ttk.Button(action_frame, command=on_submit, text="Submit")
        sub_btn.pack(side=tk.RIGHT)

    def on_save(self):
        name = self.name_entry.get()
        pre_request_script = self.script_box.get("1.0", tk.END)
        tests = self.tests_box.get("1.0", tk.END)
        variable = []

        if pre_request_script == "\n":
            pre_request_script = ""
        if tests == "\n":
            tests = ""

        for child in self.treeview.get_children():
            item = self.treeview.item(child)
            variable.append({'name': item['values'][0], 'value': item['values'][1]})

        if self.item_id is None:
            messagebox.showerror("Failed", "Save failed, item id missing.")
            return

        self.callback(
            item_id=self.item_id,
            data={
                "name": name,
                "pre_request_script": pre_request_script,
                "tests": tests,
                "variable": variable
            },
        )

class FolderWindow:
    """Folder properties"""

    item_id = None

    def __init__(self, **kwargs) -> None:
        self.root = ttk.Frame(kwargs.get("master"))
        self.callback = kwargs.get("callback")
        self.item_id = kwargs.get("item_id")
        data = kwargs.get('data')

        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.X)
        ttk.Label(frame, text="Name:").pack(side=tk.LEFT)
        self.name_entry = ttk.Entry(frame)
        self.name_entry.insert(tk.END, data.get("name", "New Folder"))
        self.name_entry.pack(side=tk.LEFT)
        save_btn = ttk.Button(frame, text="Save", command=self.on_save)
        save_btn.pack(side=tk.RIGHT)

        notebook = ttk.Notebook(self.root)
        # pre-request script
        script_frame = ttk.Frame(notebook)
        self.script_box = tk.Text(script_frame, height=12)
        self.script_box.insert(tk.END, data.get("pre_request_script", ""))
        self.script_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        script_scrollbar = ttk.Scrollbar(script_frame, command=self.script_box.yview)
        script_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.script_box.config(yscrollcommand=script_scrollbar.set)
        notebook.add(script_frame, text="Pre-request Script")

        # tests
        tests_frame = ttk.Frame(notebook)
        self.tests_box = tk.Text(tests_frame, height=12)
        self.tests_box.insert(tk.END, data.get("tests", ""))
        self.tests_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        tests_scrollbar = ttk.Scrollbar(tests_frame, command=self.tests_box.yview)
        tests_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.tests_box.config(yscrollcommand=tests_scrollbar.set)
        notebook.add(tests_frame, text="Tests")

        notebook.pack(expand=tk.YES, fill=tk.BOTH)

    def on_save(self):
        name = self.name_entry.get()
        pre_request_script = self.script_box.get("1.0", tk.END)
        tests = self.tests_box.get("1.0", tk.END)
        if pre_request_script == "\n":
            pre_request_script = ""
        if tests == "\n":
            tests = ""

        if self.item_id is None:
            messagebox.showerror("Failed", "Save failed, item id missing.")
            return

        self.callback(
            item_id=self.item_id,
            data={
                "name": name,
                "pre_request_script": pre_request_script,
                "tests": tests,
            },
        )
