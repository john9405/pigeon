import json
import os
import tkinter as tk
import uuid
import platform
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText

from . import WORK_DIR, USER_DIR
from .utils import EditorTable


class CollectionWindow:

    def __init__(self, window, callback=None):
        self.window = window
        self.callback = callback

        self.tree = ttk.Treeview(window)
        self.tree.heading("#0", text="(+)", anchor='e')
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Button-1>", self.on_click)
        self.tree.bind("<Double-1>", self.on_select)
        if platform.system() == "Darwin":
            self.tree.bind("<Control-Button-1>", self.on_right_click)
            self.tree.bind("<Button-2>", self.on_right_click)
        else:
            self.tree.bind("<Button-3>", self.on_right_click)

    def open_proj(self):
        """open a program"""
        filepath = filedialog.askopenfilename(
            filetypes=(("Json files", "*.json"),),
            initialdir=USER_DIR,
            parent=self.window)
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
            parent=self.window
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

    def on_click(self, event):
        region = self.tree.identify('region', event.x, event.y)
        if region == 'heading':
            self.new_proj()

    def on_select(self, event):
        region = self.tree.identify('region', event.x, event.y)
        if region == 'heading':
            return

        try:
            item_id = self.tree.selection()[0]
            item = self.tree.item(item_id)
            ctag = item["tags"][0]
            values = json.loads(item["values"][0])
            if ctag != 'project':
                path = self.get_path(item_id)
            else:
                path = ''
            self.callback(
                data=values,
                tag=ctag,
                request_id=item["tags"][1],
                active="newitem",
                item_id=item_id,
                path=path,
            )
        except IndexError:
            pass

    def on_open(self):
        self.on_select(None)

    def get_path(self, item_id):
        path = ""
        parent_id = self.tree.parent(item_id)
        parent = self.tree.item(parent_id)
        if parent['tags'][0] == 'project':
            return parent['text'] + '/'
        elif parent['tags'][0] == 'folder':
            return self.get_path(parent_id) + parent['text'] + '/'
        return ''

    def on_right_click(self, event):
        item = self.tree.identify_row(event.y)

        if item:
            self.tree.selection_set(item)
            tag = self.tree.item(item)["tags"][0]
            menu = tk.Menu(self.window, tearoff=0)
            if tag == "project":
                menu.add_command(label="Open in tab", command=self.on_open)
                menu.add_command(label="Add folder", command=self.new_col)
                menu.add_command(label="Add request", command=self.new_req)
                menu.add_command(label="Export", command=self.export_proj)
                menu.add_command(label="Delete", command=self.delete_item)
            elif tag == "folder":
                menu.add_command(label="Open in tab", command=self.on_open)
                menu.add_command(label="Add folder", command=self.new_col)
                menu.add_command(label="Add request", command=self.new_req)
                menu.add_command(label="Delete", command=self.delete_item)
            elif tag == "request":
                menu.add_command(label="Open in tab", command=self.on_open)
                menu.add_command(label="Delete", command=self.delete_item)
            menu.post(event.x_root, event.y_root)

    def new_proj(self):
        name = simpledialog.askstring("ask", "Name:", initialvalue='New Collection', parent=self.window)
        if name is None:
            return
        self.tree.insert(
            "",
            tk.END,
            text=name if name > "" else "New Collection",
            tags=["project", str(uuid.uuid1())],
            values=[json.dumps({"name": name if name > "" else "New Collection"})],
        )

    def new_col(self):
        name = simpledialog.askstring("ask", "Name:", initialvalue='New Folder', parent=self.window)
        if name is None:
            return
        try:
            ctag = self.tree.item(self.tree.selection()[0])["tags"][0]
            if ctag in ("folder", "project"):
                selected_node = self.tree.selection()[0]
            else:
                selected_node = self.tree.parent(self.tree.selection()[0])
            self.tree.insert(
                selected_node,
                tk.END,
                text= name if name > "" else "New Folder",
                tags=["folder", str(uuid.uuid1())],
                values=[json.dumps({"name": name if name > "" else "New Folder"})],
            )
        except IndexError:
            self.tree.insert(
                "",
                tk.END,
                text= name if name > "" else "New Collection",
                tags=["project", str(uuid.uuid1())],
                values=[json.dumps({"name": name if name > "" else "New Collection"})],
            )

    def new_req(self, data=None):
        if data is None:
            name = simpledialog.askstring("ask", "Name:", initialvalue='New Request', parent=self.window)
            if name is None:
                return
            data = {
                "name": name if name > "" else "New Request",
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
            return self.get_variable(self.tree.parent(item_id), name)


class ProjectWindow:
    def __init__(self, **kwargs) -> None:
        self.root = kwargs.get("master")
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
        self.script_box = ScrolledText(notebook)
        self.script_box.insert(tk.END, data.get("pre_request_script", ""))
        notebook.add(self.script_box, text="Pre-request Script")

        # tests
        self.tests_box = ScrolledText(notebook)
        self.tests_box.insert(tk.END, data.get("tests", ""))
        notebook.add(self.tests_box, text="Post-response Script")

        self.variable_frame = EditorTable(notebook, editable=True)
        temp = {}
        for i in data.get("variable", []):
            temp[i["name"]] = i["value"]
        self.variable_frame.set_data(temp)
        notebook.add(self.variable_frame, text="Variable")
        notebook.pack(expand=tk.YES, fill=tk.BOTH)

    def on_save(self):
        name = self.name_entry.get()
        pre_request_script = self.script_box.get("1.0", tk.END)
        tests = self.tests_box.get("1.0", tk.END)
        variable = []

        pre_request_script = pre_request_script.rstrip("\n")
        tests = tests.rstrip("\n")

        temp = self.variable_frame.get_data()
        for item in temp.items():
            variable.append({'name': item[0], 'value': item[1]})

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
        self.root = kwargs.get("master")
        self.callback = kwargs.get("callback")
        self.item_id = kwargs.get("item_id")
        data = kwargs.get('data')

        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.X)
        ttk.Label(frame, text=kwargs.get("path", "Name:")).pack(side=tk.LEFT)
        self.name_entry = ttk.Entry(frame)
        self.name_entry.insert(tk.END, data.get("name", "New Folder"))
        self.name_entry.pack(side=tk.LEFT)
        save_btn = ttk.Button(frame, text="Save", command=self.on_save)
        save_btn.pack(side=tk.RIGHT)

        notebook = ttk.Notebook(self.root)
        # pre-request script
        self.script_box = ScrolledText(notebook)
        self.script_box.insert(tk.END, data.get("pre_request_script", ""))
        notebook.add(self.script_box, text="Pre-request Script")

        # tests
        self.tests_box = ScrolledText(notebook)
        self.tests_box.insert(tk.END, data.get("tests", ""))
        notebook.add(self.tests_box, text="Post-response Script")

        notebook.pack(expand=tk.YES, fill=tk.BOTH)

    def on_save(self):
        name = self.name_entry.get()
        pre_request_script = self.script_box.get("1.0", tk.END)
        tests = self.tests_box.get("1.0", tk.END)

        pre_request_script = pre_request_script.rstrip("\n")
        tests = tests.rstrip("\n")

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
