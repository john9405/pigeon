import json
import os
import tkinter as tk
import uuid
from tkinter import ttk, filedialog, messagebox

from . import BASE_DIR, USER_DIR


class CollectionWindow:
    cmenu = None

    def __init__(self, window, callback=None):
        self.window = window
        self.callback = callback

        self.tree = ttk.Treeview(window)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_select)
        self.tree.bind("<Button-1>", self.hide_context_menu)
        self.tree.bind("<Button-3>", self.on_right_click)

        self.context_nenu = tk.Menu(window, tearoff=0)
        self.context_nenu.add_command(label="new Project", command=self.new_proj)
        # project
        self.proj_menu = tk.Menu(window, tearoff=0)
        self.proj_menu.add_command(label="new folder", command=self.new_col)
        self.proj_menu.add_command(label="new request", command=self.new_req)
        self.proj_menu.add_command(label="Export", command=self.export_proj)
        self.proj_menu.add_command(label="Delete", command=self.delete_item)
        # folder
        self.folder_menu = tk.Menu(window, tearoff=0)
        self.folder_menu.add_command(label="new folder", command=self.new_col)
        self.folder_menu.add_command(label="new request", command=self.new_req)
        self.folder_menu.add_command(label="Delete", command=self.delete_item)
        # request
        self.req_menu = tk.Menu(window, tearoff=0)
        self.req_menu.add_command(label="Delete", command=self.delete_item)

    def open_proj(self):
        """ 打开项目 """
        filepath = filedialog.askopenfilename(
            filetypes=(("Json files", "*.json"),), initialdir=USER_DIR
        )
        if filepath:
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    data = json.loads(f.read())
                    self.show_proj(data)
                except json.JSONDecodeError:
                    messagebox.showerror("错误", "文本内容必须是一个json")

    def show_proj(self, data):
        temp = {}
        for key in data.keys():
            if key != "item":
                temp.update({key: data[key]})
        node = self.tree.insert(
            "",
            "end",
            text=data["info"]["name"],
            values=[json.dumps(temp)],
            open=True,
            tags=["project", str(uuid.uuid1())],
        )
        self.show_item(node, data["item"])

    def show_item(self, node, items):
        for item in items:
            if "item" in item:
                temp = {}
                for key in item.keys():
                    if key != "item":
                        temp.update({key: item[key]})
                cnode = self.tree.insert(
                    node,
                    "end",
                    text=item["name"],
                    values=[json.dumps(temp)],
                    open=False,
                    tags=["folder", str(uuid.uuid1())],
                )
                if len(item["item"]) > 0:
                    self.show_item(cnode, item["item"])
            else:
                self.tree.insert(
                    node,
                    "end",
                    text=item["name"],
                    values=[json.dumps(item)],
                    tags=["request", str(uuid.uuid1())],
                )

    def autosave_proj(self):
        pass

    def export_proj(self):
        """ 保存项目 """
        item = self.tree.item(self.tree.selection()[0])
        bean = json.loads(item["values"][0])

        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("json files", "*.json")],
            initialdir=USER_DIR,
            initialfile=bean['info']['name'] + ".json"
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
            value = json.loads(bean['values'][0])
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
                item_id=item_id
            )
        except IndexError:
            pass

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
            "end",
            text="New Collection",
            tags=["project", str(uuid.uuid1())],
            values=[json.dumps({"info": {"name": "New Collection"}})]
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
                "end",
                text="New Folder",
                tags=["folder", str(uuid.uuid1())],
                values=[json.dumps({"name": "New Folder"})],
            )
        except IndexError:
            self.tree.insert(
                "",
                "end",
                text="New Collection",
                tags=["project", str(uuid.uuid1())],
                values=[json.dumps({"info": {"name": "New Collection"}})],
            )

    def new_req(self):
        try:
            ctag = self.tree.item(self.tree.selection()[0])["tags"][0]
            if ctag in ("folder", "project"):
                selected_node = self.tree.selection()[0]
            else:
                selected_node = self.tree.parent(self.tree.selection()[0])

            self.tree.insert(
                selected_node,
                "end",
                text="New Request",
                tags=["request", str(uuid.uuid1())],
                values=[json.dumps({
                    "name": "New Request",
                    "request": {"method": "GET", "header": []},
                    "response": [],
                })],
            )
        except IndexError:
            pass
    
    def save_item(self, item_id, data):
        self.tree.set(item_id, "text", data['name'])
        self.tree.set(item_id, "values", [json.dumps(data)])
    
    def delete_item(self):
        selected_node = self.tree.selection()
        if selected_node:
            self.tree.delete(selected_node)
