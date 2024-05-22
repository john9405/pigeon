import os
import json
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import time
import re
import xml.dom.minidom
from io import BytesIO
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageTk

from . import BASE_DIR
from .console import Console

class ParamsFrame:
    def __init__(self, **kw) -> None:
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
        self.root = ttk.Frame(kw.get("master"))

        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X)

        add_btn = ttk.Button(toolbar, image="add", command=self.on_add)
        add_btn.pack(side=tk.LEFT)
        edt_btn = ttk.Button(toolbar, image="edit", command=self.on_edit)
        edt_btn.pack(side=tk.LEFT)
        del_btn = ttk.Button(toolbar, image="delete", command=self.on_del)
        del_btn.pack(side=tk.LEFT)

        self.treeview = ttk.Treeview(self.root, columns=("name","value"), show="headings")
        self.treeview.pack(fill=tk.BOTH, expand=True)

        self.treeview.heading("name", text="name", anchor=tk.CENTER)
        self.treeview.heading("value", text="value", anchor=tk.CENTER)

        self.treeview.column("name", width=1)
        self.treeview.column("value")

    def get_data(self) -> dict:
        data = {}
        for child in self.treeview.get_children():
            item = self.treeview.item(child)
            data.update({str(item['values'][0]): str(item['values'][1])})
        return data

    def set_data(self, data: dict):
        for key in data.keys():
            self.treeview.insert("", tk.END, values=(key, data[key]))

    def on_add(self):
        self.editor()

    def on_edit(self):
        if len(self.treeview.selection()) > 0:
            item_id = self.treeview.selection()[0]
            item = self.treeview.item(item_id)
            self.editor(item_id, name=item['values'][0], value=item['values'][1])

    def on_del(self):
        if len(self.treeview.selection()) > 0:
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


class HeaderFrame:
    def __init__(self, **kw) -> None:
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
        self.root = ttk.Frame(kw.get('master'))

        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X)

        add_btn = ttk.Button(toolbar, image="add", command=self.on_add)
        add_btn.pack(side=tk.LEFT)
        edt_btn = ttk.Button(toolbar, image="edit", command=self.on_edit)
        edt_btn.pack(side=tk.LEFT)
        del_btn = ttk.Button(toolbar, image="delete", command=self.on_del)
        del_btn.pack(side=tk.LEFT)

        self.treeview = ttk.Treeview(self.root, columns=("name", "value",), show="headings")
        self.treeview.pack(fill=tk.BOTH, expand=True)
        
        self.treeview.heading("name", text="name", anchor=tk.CENTER)
        self.treeview.heading("value", text="value", anchor=tk.CENTER)

        self.treeview.column("name", width=1)
        self.treeview.column("value")

    def get_data(self) -> dict:
        data = {}
        for child in self.treeview.get_children():
            item = self.treeview.item(child)
            data.update({str(item['values'][0]): str(item['values'][1])})
        return data

    def set_data(self, data: dict):
        for key in data.keys():
            self.treeview.insert("", tk.END, values=(key, data[key]))

    def on_add(self):
        self.editor()

    def on_edit(self):
        if len(self.treeview.selection()) > 0:
            item_id = self.treeview.selection()[0]
            item = self.treeview.item(item_id)
            self.editor(item_id, name=item['values'][0], value=item['values'][1])

    def on_del(self):
        if len(self.treeview.selection()) > 0:
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


class RequestWindow:
    item_id = None
    method_list = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]

    def __init__(self, **kwargs):
        self.callback = kwargs.get("callback")
        window = kwargs.get("window")
        self.get_script = kwargs.get("get_script")
        self.env_variable = kwargs.get('env_variable')
        self.local_variable = kwargs.get('local_variable')

        ff = ttk.Frame(window)
        ff.pack(fill=tk.X)
        ttk.Label(ff, text="Name:").pack(side=tk.LEFT)
        self.name_entry = ttk.Entry(ff)
        self.name_entry.insert(0, "New Request")
        self.name_entry.pack(side=tk.LEFT)
        save_btn = ttk.Button(ff, text="Save", command=self.save_handler)
        save_btn.pack(side=tk.RIGHT)

        north = ttk.Frame(window)
        north.pack(fill=tk.X)
        # Create request mode drop-down box and URL input box
        self.method_box = ttk.Combobox(north, width=8, values=self.method_list)
        self.method_box.current(0)
        self.method_box["state"] = "readonly"
        self.method_box.pack(side=tk.LEFT)
        sub_btn = ttk.Button(north, text="Send")  # Send request button
        sub_btn.config(command=self.send_request)  # Bind the event handler to send the request button
        sub_btn.pack(side=tk.RIGHT)
        self.url_box = ttk.Entry(north)
        self.url_box.pack(fill=tk.BOTH, pady=3)

        # Create a PanedWindow
        paned_window = ttk.PanedWindow(window, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=tk.YES)

        # Create notebook
        notebook = ttk.Notebook(paned_window)
        paned_window.add(notebook, weight=1)

        # Create a query parameter page
        self.params_frame = ParamsFrame(master=notebook)
        notebook.add(self.params_frame.root, text="Params")

        # Create the request header page
        self.headers_frame = HeaderFrame(master=notebook)
        notebook.add(self.headers_frame.root, text="Headers")

        # Create the request body page
        self.body_box = ScrolledText(notebook)
        notebook.add(self.body_box, text="Body")

        # pre-request script
        self.script_box = ScrolledText(notebook)
        notebook.add(self.script_box, text="Pre-request Script")

        # tests
        self.tests_box = ScrolledText(notebook)
        notebook.add(self.tests_box, text="Tests")

        # Create response area
        res_note = ttk.Notebook(paned_window)
        paned_window.add(res_note, weight=1)

        self.res_body_box = ScrolledText(res_note)
        res_note.add(self.res_body_box, text="Body")

        res_cookie_frame = ttk.Frame(res_note)
        self.res_cookie_table = ttk.Treeview(
            res_cookie_frame, 
            columns=("key", "value"), 
            show="headings"
        )
        res_cookie_scrollbar_x = ttk.Scrollbar(
            res_cookie_frame, 
            orient=tk.HORIZONTAL, 
            command=self.res_cookie_table.xview
        )
        res_cookie_scrollbar_y = ttk.Scrollbar(
            res_cookie_frame, 
            command=self.res_cookie_table.yview
        )
        self.res_cookie_table.column("key", width=1)
        self.res_cookie_table.heading("key", text="key")
        self.res_cookie_table.heading("value", text="value")
        res_cookie_scrollbar_y.pack(
            side=tk.RIGHT, 
            fill=tk.Y, 
            pady=(0, res_cookie_scrollbar_x.winfo_reqheight())
        )
        res_cookie_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.res_cookie_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        self.res_cookie_table.config(
            xscrollcommand=res_cookie_scrollbar_x.set,
            yscrollcommand=res_cookie_scrollbar_y.set,
        )
        res_note.add(res_cookie_frame, text="Cookies")

        res_header_frame = ttk.Frame(res_note)
        self.res_header_table = ttk.Treeview(
            res_header_frame, 
            columns=("key", "value"), 
            show="headings"
        )
        self.res_header_table.column("key", width=1)
        self.res_header_table.heading("key", text="key")
        self.res_header_table.heading("value", text="value")
        res_header_scrollbar_x = ttk.Scrollbar(
            res_header_frame, 
            orient=tk.HORIZONTAL, 
            command=self.res_header_table.xview
        )
        res_header_scrollbar_y = ttk.Scrollbar(
            res_header_frame, command=self.res_header_table.yview
        )
        res_header_scrollbar_y.pack(
            side="right", fill=tk.Y, pady=(0, res_header_scrollbar_x.winfo_reqheight())
        )
        res_header_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.res_header_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        self.res_header_table.config(
            xscrollcommand=res_header_scrollbar_x.set,
            yscrollcommand=res_header_scrollbar_y.set,
        )
        res_note.add(res_header_frame, text="Headers")

        self.res_tests_box = ScrolledText(res_note)
        res_note.add(self.res_tests_box, text="Test Results")

    def save_handler(self):
        """Save test script"""
        name = self.name_entry.get()
        method = self.method_box.get()
        url = self.url_box.get()
        params = self.headers_frame.get_data()
        headers = self.headers_frame.get_data()
        body = self.body_box.get("1.0", tk.END)
        pre_request_script = self.script_box.get("1.0", tk.END)
        tests = self.tests_box.get("1.0", tk.END)

        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            body = {}
        
        pre_request_script = pre_request_script.rstrip("\n")
        tests = tests.rstrip("\n")

        if name == "" and url > "":
            name = url
        elif name == "":
            name = "New Request"

        x = self.callback(
            "save",
            item_id=self.item_id,
            data={
                "method": method,
                "url": url,
                "params": params,
                "headers": headers,
                "body": body,
                "pre_request_script": pre_request_script,
                "tests": tests,
                "name": name,
            },
        )
        self.item_id = x

    def fill_blank(self, data):
        method = data.get("method", "GET")
        self.method_box.current(self.method_list.index(method))
        self.url_box.delete(0, tk.END)
        self.url_box.insert(tk.END, data.get("url", ""))
        self.params_frame.set_data(data.get("params", {}))
        self.headers_frame.set_data(data.get("headers", {}))
        self.body_box.delete("1.0", tk.END)
        self.body_box.insert(tk.END, json.dumps(data.get("body", {}), ensure_ascii=False, indent=4))
        self.script_box.delete("1.0", tk.END)
        self.script_box.insert(tk.END, data.get("pre_request_script", ""))
        self.tests_box.delete("1.0", tk.END)
        self.tests_box.insert(tk.END, data.get("tests", ""))
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(tk.END, data.get("name", "New Request"))

    def get_variable(self, name):
        var = self.local_variable(self.item_id, name)
        if var is not None:
            return var
        var = self.env_variable("Globals", name)
        return var

    def send_request(self):
        """Define the function that sends the request"""
        console = Console(self.console)
        get_variable = self.get_variable
        collectionVariables = self.local_variable
        environment = self.env_variable
        # Gets the request method and URL
        method = self.method_box.get()
        url = self.url_box.get()
        if url is None or url == "":
            messagebox.showerror("Error", "Please enter the request address")
            return
        varlist = re.finditer(r"\{\{[^{}]*\}\}", url)
        for m in varlist:
            value = get_variable(m.group()[2:-2])
            if value is not None:
                url = url.replace(m.group(), value)
        # Gets query parameters, request headers, and request bodies
        params = self.params_frame.get_data()
        headers = self.headers_frame.get_data()
        body = self.body_box.get("1.0", tk.END)

        params = json.dumps(params)
        varlist = re.finditer(r"\{\{[^{}]*\}\}", params)
        for m in varlist:
            value = get_variable(m.group()[2:-2])
            if value is not None:
                params = params.replace(m.group(), value)
        params = json.loads(params)

        headers = json.dumps(headers)
        varlist = re.finditer(r"\{\{[^{}]*\}\}", headers)
        for m in varlist:
            value = get_variable(m.group()[2:-2])
            if value is not None:
                headers = headers.replace(m.group(), value)
        headers = json.loads(headers)

        varlist = re.finditer(r"\{\{[^{}]*\}\}", body)
        for m in varlist:
            value = get_variable(m.group()[2:-2])
            if value is not None:
                body = body.replace(m.group(), value)

        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            body = {}

        if self.item_id is not None:
            script_list = self.get_script(self.item_id)
        else:
            script_list = []

        pre_request_script = self.script_box.get("1.0", tk.END)
        tests = self.tests_box.get("1.0", tk.END)

        try:
            exec(pre_request_script)
        except Exception as error:
            console.error(str(error))

        for script in script_list:
            try:
                exec(script["pre_request_script"])
            except Exception as error:
                console.error(str(error))
        start_time = time.time()
        # 发送网络请求
        try:
            if method == "GET":
                response = requests.get(url, params=params, headers=headers)
            elif method == "POST":
                response = requests.post(url, params=params, data=body, headers=headers)
            elif method == "PUT":
                response = requests.put(url, params=params, data=body, headers=headers)
            elif method == "PATCH":
                response = requests.patch(url, params=params, data=body, headers=headers)
            elif method == "DELETE":
                response = requests.delete(url, params=params, headers=headers)
            elif method == "HEAD":
                response = requests.head(url, params=params, headers=headers)
            elif method == "OPTIONS":
                response = requests.head(url, params=params, headers=headers)
            else:
                messagebox.showerror("Error", "Unsupported request type")
                return
        except requests.exceptions.MissingSchema:
            messagebox.showerror("Error", "Request error")
            return
        cost_time = time.time() - start_time
        if cost_time < 1:
            cost_time = f"{round(cost_time * 1000)}ms"
        else:
            cost_time = f"{round(cost_time)}s"
        # 将响应显示在响应区域
        self.res_cookie_table.delete(*self.res_cookie_table.get_children())
        for item in response.cookies.keys():
            self.res_cookie_table.insert("", tk.END, values=(item, response.cookies.get(item)))

        self.res_header_table.delete(*self.res_header_table.get_children())
        content_type = ""
        for item in response.headers.keys():
            if item == "Content-Type":
                content_type = response.headers.get(item)
            self.res_header_table.insert("", tk.END, values=(item, response.headers.get(item)))

        self.res_body_box.delete("1.0", tk.END)
        if "application/json" in content_type:
            self.res_body_box.insert(
                tk.END, json.dumps(response.json(), indent=4, ensure_ascii=False)
            )
        elif "text/html" in content_type:
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, "html.parser")
            self.res_body_box.insert(tk.END, soup.prettify())
        elif "text/xml" in content_type or "application/xml" in content_type:
            response.encoding = "utf-8"
            dom = xml.dom.minidom.parseString(response.text)
            self.res_body_box.insert(tk.END, dom.toprettyxml(indent="    "))
        elif "image" in content_type:
            data_stream = BytesIO(response.content)
            pil_image = Image.open(data_stream)
            tk_image = ImageTk.PhotoImage(pil_image)
            self.res_body_box.image_create(tk.END, image=tk_image)
        else:
            self.res_body_box.insert(tk.END, response.text)

        self.res_tests_box.delete("1.0", tk.END)
        self.res_tests_box.insert(tk.END, f"Get {url} {response.status_code} {cost_time}")
        try:
            exec(tests)
        except Exception as error:
            console.error(str(error))

        for script in script_list:
            try:
                exec(script["tests"])
            except Exception as error:
                console.error(str(error))

        self.callback("cache",**{"data": {
            "method": method,
            "url": url,
            "params": params,
            "headers": headers,
            "body": body,
            "pre_request_script": pre_request_script,
            "tests": tests,
        }})
        if self.item_id is not None:
            self.save_handler()

    def console(self, data):
        self.callback("console", **data)
