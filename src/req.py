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

from .console import Console
from .utils import EditorTable


class ParamsFrame(EditorTable):
    pass


class BodyFrame:
    current_date_type = "none"

    def __init__(self, **kwargs) -> None:
        self.root = ttk.Frame(kwargs.get("master"))
        self.data_type = tk.StringVar()
        self.data_type.set(self.current_date_type)
        self.data_type.trace_add("write", self.on_data_type_change)
        self.toolbar = ttk.Frame(self.root)
        ttk.Radiobutton(
            self.toolbar, text="none", variable=self.data_type, value="none"
        ).pack(side="left")
        ttk.Radiobutton(
            self.toolbar,
            text="x-www-form-urlencoded",
            variable=self.data_type,
            value="x-www-form-urlencoded",
        ).pack(side="left")
        ttk.Radiobutton(
            self.toolbar, text="raw", variable=self.data_type, value="raw"
        ).pack(side="left")
        self.toolbar.pack(fill=tk.X)

        self.toolbar_right = None
        self.main_frame = ttk.Frame(self.root)
        ttk.Label(self.main_frame, text="This request does not have a body").pack()
        self.main_frame.pack()
        self.edit_table = None
        self.scrolled_text = None
        self.data = kwargs.get("data", {})

    def on_data_type_change(self, *args):
        if self.data_type.get() != self.current_date_type:
            if self.toolbar_right:
                self.toolbar_right.forget()

            if self.main_frame:
                self.main_frame.forget()

            if self.data_type.get() == "none":
                self.main_frame = ttk.Frame(self.root)
                ttk.Label(
                    self.main_frame, text="This request does not have a body"
                ).pack()
                self.main_frame.pack()
                self.current_date_type = "none"

            elif self.data_type.get() == "x-www-form-urlencoded":
                self.show_x_www_form_urlencoded()
                self.current_date_type = "x-www-form-urlencoded"

            elif self.data_type.get() == "raw":
                self.show_raw()
                self.current_date_type = "raw"

    def show_x_www_form_urlencoded(self):
        self.main_frame = ttk.Frame(self.root)
        self.edit_table = EditorTable(self.main_frame, editable=True)
        self.edit_table.pack(fill=tk.BOTH, expand=tk.YES)
        self.main_frame.pack(fill=tk.BOTH, expand=tk.YES)

    def show_raw(self):
        self.toolbar_right = ttk.Frame(self.toolbar)
        detail_combo = ttk.Combobox(
            self.toolbar_right,
            values=["Text", "JSON", "XML", "HTML"],
            width=6
        )
        detail_combo.current(0)
        detail_combo['state'] = 'readonly'
        detail_combo.pack(side="left")
        self.toolbar_right.pack(side="left")

        self.main_frame = ttk.Frame(self.root)
        self.scrolled_text = ScrolledText(self.main_frame)
        self.scrolled_text.pack(fill=tk.BOTH, expand=True)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

    def insert(self, *args):
        return None

    def get(self, *args):
        return "{}"

    def delete(self, *args):
        return None


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
        sub_btn.config(
            command=self.send_request
        )  # Bind the event handler to send the request button
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
        self.params_frame = ParamsFrame(master=notebook, editable=True)
        notebook.add(self.params_frame, text="Params")

        # Create the request header page
        self.headers_frame = EditorTable(master=notebook, editable=True)
        notebook.add(self.headers_frame, text="Headers")

        # Create the request body page
        # self.body_box = ScrolledText(notebook)
        # notebook.add(self.body_box, text="Body")
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
        url = self.url_box.get()
        params = self.params_frame.get_data()
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
        self.body_box.insert(
            tk.END, json.dumps(data.get("body", {}), ensure_ascii=False, indent=4)
        )
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
                response = requests.get(url, params=params, headers=headers, timeout=60)
            elif method == "POST":
                response = requests.post(
                    url, params=params, data=body, headers=headers, timeout=60
                )
            elif method == "PUT":
                response = requests.put(
                    url, params=params, data=body, headers=headers, timeout=60
                )
            elif method == "PATCH":
                response = requests.patch(
                    url, params=params, data=body, headers=headers, timeout=60
                )
            elif method == "DELETE":
                response = requests.delete(
                    url, params=params, headers=headers, timeout=60
                )
            elif method == "HEAD":
                response = requests.head(
                    url, params=params, headers=headers, timeout=60
                )
            elif method == "OPTIONS":
                response = requests.head(
                    url, params=params, headers=headers, timeout=60
                )
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
        self.res_cookie_table.set_data(response.cookies)
        self.res_header_table.clear_data()
        self.res_header_table.set_data(response.headers)
        content_type = response.headers.get("Content-Type")

        self.res_body_box.delete("1.0", tk.END)
        if "application/json" in content_type:
            self.res_body_box.insert(
                tk.END, json.dumps(response.json(), indent=4, ensure_ascii=False)
            )
        elif "text/html" in content_type:
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, "html.parser")
            chunk_size=1000
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
                    "params": params,
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
