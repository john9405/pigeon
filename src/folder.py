import tkinter as tk
from tkinter import ttk, messagebox


class FolderWindow:
    """文件夹属性"""

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
