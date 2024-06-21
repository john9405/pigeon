import json
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import time
import re
import xml.dom.minidom
from io import BytesIO
import urllib.parse
from typing import Optional

import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageTk

from .console import Console
from .utils import EditorTable


class ParamsFrame(EditorTable):
    def __init__(self, master=None, **kw):
        self.cb = kw.pop('cb')
        super().__init__(master, **kw)

    def commit(
            self,
            item_id: Optional[str] = None,
            win: Optional[tk.Toplevel] = None,
            name_entry: Optional[ttk.Entry] = None,
            value_entry: Optional[ttk.Entry] = None,
    ):
        name = name_entry.get()
        value = value_entry.get()
        if self.check_name(item_id, name):
            if item_id is None:
                self.treeview.insert("", tk.END, values=(name, value))
            else:
                self.treeview.item(item_id, values=(name, value))
            win.destroy()
            self.cb(str(urllib.parse.urlencode(self.get_data())))
        else:
            messagebox.showerror("error", "Duplicate key")

    def on_del(self):
        if self.editable and len(self.treeview.selection()) > 0:
            self.treeview.delete(self.treeview.selection()[0])
            self.cb(str(urllib.parse.urlencode(self.get_data())))


class BodyFrame:
    current_date_type = "none"

    def __init__(self, **kwargs) -> None:
        self.root = ttk.Frame(kwargs.get("master"))
        self.mode = tk.StringVar()
        self.mode.set(self.current_date_type)
        self.mode.trace_add("write", self.on_data_type_change)
        self.toolbar = ttk.Frame(self.root)
        ttk.Radiobutton(
            self.toolbar, text="none", variable=self.mode, value="none"
        ).pack(side="left")
        ttk.Radiobutton(
            self.toolbar,
            text="urlencoded",
            variable=self.mode,
            value="urlencoded",
        ).pack(side="left")
        ttk.Radiobutton(
            self.toolbar, text="raw", variable=self.mode, value="raw"
        ).pack(side="left")
        self.toolbar.pack(fill=tk.X)

        self.toolbar_right = None
        self.main_frame = ttk.Frame(self.root)
        ttk.Label(self.main_frame, text="This request does not have a body").pack()
        self.main_frame.pack()
        self.edit_table = None
        self.options = None
        self.scrolled_text = None

    def on_data_type_change(self, *args):
        if self.mode.get() != self.current_date_type:
            if self.toolbar_right:
                self.toolbar_right.forget()

            if self.main_frame:
                self.main_frame.forget()

            if self.mode.get() == "none":
                self.main_frame = ttk.Frame(self.root)
                ttk.Label(
                    self.main_frame, text="This request does not have a body"
                ).pack()
                self.main_frame.pack()
                self.current_date_type = "none"

            elif self.mode.get() == "urlencoded":
                self.show_urlencoded()
                self.current_date_type = "urlencoded"

            elif self.mode.get() == "raw":
                self.show_raw()
                self.current_date_type = "raw"

    def show_urlencoded(self):
        self.main_frame = ttk.Frame(self.root)
        self.edit_table = EditorTable(self.main_frame, editable=True)
        self.edit_table.pack(fill=tk.BOTH, expand=tk.YES)
        self.main_frame.pack(fill=tk.BOTH, expand=tk.YES)

    def show_raw(self):
        self.toolbar_right = ttk.Frame(self.toolbar)
        self.options = ttk.Combobox(
            self.toolbar_right,
            values=["Text", "JSON", "XML", "HTML"],
            width=6
        )
        self.options.current(0)
        self.options['state'] = 'readonly'
        self.options.pack(side="left")
        self.toolbar_right.pack(side="left")

        self.main_frame = ttk.Frame(self.root)
        self.scrolled_text = ScrolledText(self.main_frame)
        self.scrolled_text.pack(fill=tk.BOTH, expand=True)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

    def insert(self, kw):
        if kw.get('mode') == 'urlencoded':
            self.mode.set('urlencoded')
            self.edit_table.set_data(kw.get('urlencoded'))
        elif kw.get('mode') == 'raw':
            self.mode.set('raw')
            index = ["Text", "JSON", "XML", "HTML"].index(kw.get('options'))
            self.options.current(index)
            self.scrolled_text.delete('1.0', 'end')
            self.scrolled_text.insert('end', kw.get("raw"))
        else:
            self.mode.set('none')

    def get(self):
        return {
            'mode': self.mode.get(),
            "options": self.options.get() if self.options else "",
            'raw': self.scrolled_text.get('1.0', 'end') if self.scrolled_text else "",
            'urlencoded': self.edit_table.get_data() if self.edit_table else {}
        }


class RequestWindow:
    item_id = None
    method_list = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]

    def __init__(self, **kwargs):
        self.callback = kwargs.get("callback")
        window = kwargs.get("window")
        self.get_script = kwargs.get("get_script")
        self.env_variable = kwargs.get("env_variable")
        self.local_variable = kwargs.get("local_variable")

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
        self.url = tk.StringVar()
        self.url.trace('w', self.change_url)
        url_box = ttk.Entry(north, textvariable=self.url)
        url_box.pack(fill=tk.BOTH, pady=3)

        # Create a PanedWindow
        paned_window = ttk.PanedWindow(window, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=tk.YES)

        # Create notebook
        notebook = ttk.Notebook(paned_window)
        paned_window.add(notebook, weight=1)

        # Create a query parameter page
        self.params_frame = ParamsFrame(master=notebook, editable=True, cb=self.update_url)
        notebook.add(self.params_frame, text="Params")

        # Create the request header page
        self.headers_frame = EditorTable(master=notebook, editable=True)
        notebook.add(self.headers_frame, text="Headers")

        # Create the request body page
        self.body_box = BodyFrame(master=notebook)
        notebook.add(self.body_box.root, text="Body")

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

        self.res_cookie_table = EditorTable(res_note)
        res_note.add(self.res_cookie_table, text="Cookies")

        self.res_header_table = EditorTable(res_note)
        res_note.add(self.res_header_table, text="Headers")

        self.res_tests_box = ScrolledText(res_note)
        res_note.add(self.res_tests_box, text="Test Results")

    def save_handler(self):
        """Save test script"""
        name = self.name_entry.get()
        method = self.method_box.get()
        url = self.url.get()
        params = self.params_frame.get_data()
        headers = self.headers_frame.get_data()
        body = self.body_box.get()
        pre_request_script = self.script_box.get("1.0", tk.END)
        tests = self.tests_box.get("1.0", tk.END)

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
        self.url.set(data.get("url", ""))
        self.headers_frame.set_data(data.get("headers", {}))
        self.body_box.insert(data.get("body", {}))
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
        url = self.url.get()
        if url is None or url == "":
            messagebox.showerror("Error", "Please enter the request address")
            return

        varlist = re.finditer(r"\{\{[^{}]*\}\}", url)
        for m in varlist:
            value = get_variable(m.group()[2:-2])
            if value is not None:
                url = url.replace(m.group(), value)

        # Gets query parameters, request headers, and request bodies
        headers = self.headers_frame.get_data()
        headers = json.dumps(headers)
        varlist = re.finditer(r"\{\{[^{}]*\}\}", headers)
        for m in varlist:
            value = get_variable(m.group()[2:-2])
            if value is not None:
                headers = headers.replace(m.group(), value)
        headers = json.loads(headers)

        req_options = self.body_box.get()
        if req_options.get('mode') == 'raw':
            body = req_options.get("raw")
        elif req_options.get('mode') == 'urlencoded':
            body = req_options.get('urlencoded')
            body = json.dumps(body)
        else:
            body = ''
        varlist = re.finditer(r"\{\{[^{}]*\}\}", body)
        for m in varlist:
            value = get_variable(m.group()[2:-2])
            if value is not None:
                body = body.replace(m.group(), value)
        if (req_options.get('mode') == 'urlencoded'
                or (req_options.get('mode') == 'raw'
                    and req_options.get('options') == 'JSON')):
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

        if req_options.get('mode') == 'urlencoded':
            headers.update({"Content-Type": "application/x-www-form-urlencoded"})
        elif req_options.get('mode') == 'raw':
            if req_options.get('options') == 'JSON':
                body = json.dumps(body)
                headers.update({"Content-Type": "application/json"})
            elif req_options.get('options') == 'Text':
                headers.update({'Content-Type': 'text/plain'})
            elif req_options.get('options') == "XML":
                headers.update({'Content-Type': 'application/xml'})
            elif req_options.get('options') == "HTML":
                headers.update({'Content-Type': 'text/html'})

        # 发送网络请求
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, data=body, headers=headers)
            elif method == "PUT":
                response = requests.put(url, data=body, headers=headers)
            elif method == "PATCH":
                response = requests.patch(url, data=body, headers=headers)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            elif method == "HEAD":
                response = requests.head(url, headers=headers)
            elif method == "OPTIONS":
                response = requests.head(url, headers=headers)
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
        self.res_cookie_table.clear_data()
        self.res_cookie_table.set_data(dict(response.cookies))
        self.res_header_table.clear_data()
        self.res_header_table.set_data(dict(response.headers))
        content_type = response.headers.get("Content-Type")

        self.res_body_box.delete("1.0", tk.END)
        if "application/json" in content_type:
            self.res_body_box.insert(
                tk.END, json.dumps(response.json(), indent=4, ensure_ascii=False)
            )
        elif "text/html" in content_type:
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, "html.parser")
            chunk_size = 1000

            def insert_chunk(offset):
                self.res_body_box.insert(tk.END, soup.prettify()[offset:offset + chunk_size])
                self.res_body_box.after(1, insert_chunk, offset + chunk_size)

            insert_chunk(0)
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
        self.res_tests_box.insert(
            tk.END, f"Get {url} {response.status_code} {cost_time}"
        )
        try:
            exec(tests)
        except Exception as error:
            console.error(str(error))

        for script in script_list:
            try:
                exec(script["tests"])
            except Exception as error:
                console.error(str(error))

        self.callback(
            "cache",
            **{
                "data": {
                    "method": method,
                    "url": url,
                    "params": self.get_params(),
                    "headers": headers,
                    "body": body,
                    "pre_request_script": pre_request_script,
                    "tests": tests,
                }
            },
        )
        if self.item_id is not None:
            self.save_handler()

    def console(self, data):
        self.callback("console", **data)

    def get_params(self):
        x = urllib.parse.urlparse(self.url.get())
        y = urllib.parse.parse_qs(x.query)
        data = {}
        for item in y.keys():
            if len(y[item]) == 1:
                data.update({item: y[item][0]})
            else:
                data.update({item: json.dumps(y[item])})
        return data

    def change_url(self, *args):
        self.params_frame.clear_data()
        self.params_frame.set_data(self.get_params())

    def update_url(self, query: str):
        x = urllib.parse.urlparse(self.url.get())
        scheme = x.scheme
        netloc = x.netloc
        path = x.path
        params = x.params
        fragment = x.fragment
        self.url.set(urllib.parse.urlunparse((scheme, netloc, path, params, query, fragment)))
