import json
import tkinter as tk
from tkinter import messagebox, ttk
import time
import xml.dom.minidom
from io import BytesIO
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageTk

from .console import Console


class RequestWindow:
    item_id = None
    method_list = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]

    def __init__(self, **kwargs):
        self.callback = kwargs.get("callback")
        window = kwargs.get("window")
        self.get_script = kwargs.get("get_script")

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
        paned_window.add(notebook)

        # Create a query parameter page
        params_frame = ttk.Frame(notebook)
        self.params_box = tk.Text(params_frame, height=12)
        self.params_box.insert(tk.END, "{}")
        self.params_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        params_scrollbar = ttk.Scrollbar(params_frame, command=self.params_box.yview)
        params_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.params_box.config(yscrollcommand=params_scrollbar.set)
        notebook.add(params_frame, text="Params")

        # Create the request header page
        headers_frame = ttk.Frame(notebook)
        self.headers_box = tk.Text(headers_frame, height=12)
        self.headers_box.insert(tk.END, "{}")
        self.headers_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        headers_scrollbar = ttk.Scrollbar(headers_frame, command=self.headers_box.yview)
        headers_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.headers_box.config(yscrollcommand=headers_scrollbar.set)
        notebook.add(headers_frame, text="Headers")

        # Create the request body page
        body_frame = ttk.Frame(notebook)
        self.body_box = tk.Text(body_frame, height=12)
        self.body_box.insert(tk.END, "{}")
        self.body_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        body_scrollbar = ttk.Scrollbar(body_frame, command=self.body_box.yview)
        body_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.body_box.config(yscrollcommand=body_scrollbar.set)
        notebook.add(body_frame, text="Body")

        # pre-request script
        script_frame = ttk.Frame(notebook)
        self.script_box = tk.Text(script_frame, height=12)
        self.script_box.insert(tk.END, "")
        self.script_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        script_scrollbar = ttk.Scrollbar(script_frame, command=self.script_box.yview)
        script_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.script_box.config(yscrollcommand=script_scrollbar.set)
        notebook.add(script_frame, text="Pre-request Script")

        # tests
        tests_frame = ttk.Frame(notebook)
        self.tests_box = tk.Text(tests_frame, height=12)
        self.tests_box.insert(tk.END, "")
        self.tests_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        tests_scrollbar = ttk.Scrollbar(tests_frame, command=self.tests_box.yview)
        tests_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.tests_box.config(yscrollcommand=tests_scrollbar.set)
        notebook.add(tests_frame, text="Tests")

        # Create response area
        res_note = ttk.Notebook(paned_window)
        paned_window.add(res_note)

        res_body_frame = ttk.Frame(res_note)
        self.res_body_box = tk.Text(res_body_frame, height=12)
        self.res_body_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        res_body_scrollbar = ttk.Scrollbar(
            res_body_frame, command=self.res_body_box.yview
        )
        res_body_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.res_body_box.config(yscrollcommand=res_body_scrollbar.set)
        res_note.add(res_body_frame, text="Body")

        res_cookie_frame = ttk.Frame(res_note)
        self.res_cookie_table = ttk.Treeview(
            res_cookie_frame, columns=("key", "value"), show="headings", height=6
        )
        res_cookie_scrollbar_x = ttk.Scrollbar(
            res_cookie_frame, orient=tk.HORIZONTAL, command=self.res_cookie_table.xview
        )
        res_cookie_scrollbar_y = ttk.Scrollbar(
            res_cookie_frame, command=self.res_cookie_table.yview
        )
        self.res_cookie_table.column("key", width=1)
        self.res_cookie_table.heading("key", text="key")
        self.res_cookie_table.heading("value", text="value")
        res_cookie_scrollbar_y.pack(
            side=tk.RIGHT, fill=tk.Y, pady=(0, res_cookie_scrollbar_x.winfo_reqheight())
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
            res_header_frame, columns=("key", "value"), show="headings", height=6
        )
        self.res_header_table.column("key", width=1)
        self.res_header_table.heading("key", text="key")
        self.res_header_table.heading("value", text="value")
        res_header_scrollbar_x = ttk.Scrollbar(
            res_header_frame, orient=tk.HORIZONTAL, command=self.res_header_table.xview
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

        res_tests_frame = ttk.Frame(res_note)
        self.res_tests_box = tk.Text(res_tests_frame, height=12)
        self.res_tests_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        res_tests_scrollbar = ttk.Scrollbar(
            res_tests_frame, command=self.res_tests_box.yview
        )
        res_tests_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.res_tests_box.config(yscrollcommand=res_tests_scrollbar.set)
        res_note.add(res_tests_frame, text="Test Results")

    def save_handler(self):
        """Save test script"""
        name = self.name_entry.get()
        method = self.method_box.get()
        url = self.url_box.get()
        params = self.params_box.get("1.0", tk.END)
        headers = self.headers_box.get("1.0", tk.END)
        body = self.body_box.get("1.0", tk.END)
        pre_request_script = self.script_box.get("1.0", tk.END)
        tests = self.tests_box.get("1.0", tk.END)

        try:
            params = json.loads(params)
        except json.JSONDecodeError:
            params = {}
        try:
            headers = json.loads(headers)
        except json.JSONDecodeError:
            headers = {}
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            body = {}
        if pre_request_script == "\n":
            pre_request_script = ""
        if tests == "\n":
            tests = ""

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
        self.params_box.delete("1.0", tk.END)
        self.params_box.insert(
            tk.END, json.dumps(data.get("params", {}), ensure_ascii=False, indent=4)
        )
        self.headers_box.delete("1.0", tk.END)
        self.headers_box.insert(
            tk.END, json.dumps(data.get("headers", {}), ensure_ascii=False, indent=4)
        )
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

    def send_request(self):
        """Define the function that sends the request"""
        console = Console(self.console)

        # Gets the request method and URL
        method = self.method_box.get()
        url = self.url_box.get()
        if url is None or url == "":
            messagebox.showerror("Error", "Please enter the request address")
            return

        # Gets query parameters, request headers, and request bodies
        params = self.params_box.get("1.0", tk.END)
        headers = self.headers_box.get("1.0", tk.END)
        body = self.body_box.get("1.0", tk.END)

        try:
            params = json.loads(params)
        except json.JSONDecodeError:
            params = {}
        try:
            headers = json.loads(headers)
        except json.JSONDecodeError:
            headers = {}
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            body = {}

        if self.item_id is not None:
            script_list = self.get_script(self.item_id)

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
                response = requests.patch(
                    url, params=params, data=body, headers=headers
                )
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
        console.log(f"Get {url} {response.status_code} {cost_time}")
        # 将响应显示在响应区域
        self.res_cookie_table.delete(*self.res_cookie_table.get_children())
        for item in response.cookies.keys():
            self.res_cookie_table.insert(
                "", tk.END, values=(item, response.cookies.get(item))
            )

        self.res_header_table.delete(*self.res_header_table.get_children())
        content_type = ""
        for item in response.headers.keys():
            if item == "Content-Type":
                content_type = response.headers.get(item)
            self.res_header_table.insert(
                "", tk.END, values=(item, response.headers.get(item))
            )

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
        self.save_handler()

    def console(self, data):
        self.callback("console", **data)
