import json
import tkinter as tk
from tkinter import ttk


class Console:
    def __init__(self, callback):
        self.callback = callback

    def to_string(self, *args) -> str:
        temp = ""
        for item in args:
            if isinstance(item, (str, int, float)):
                temp += f"{item} "
            elif isinstance(item, (dict, list)):
                temp += f"{json.dumps(item)} "
            else:
                temp += str(temp)
        return temp

    def log(self, *args):
        self.callback({"level": "log", "content": self.to_string(*args)})

    def info(self, *args):
        self.callback({"level": "info", "content": self.to_string(*args)})

    def error(self, *args):
        self.callback({"level": "error", "content": self.to_string(*args)})

    def warning(self, *args):
        self.callback({"level": "warning", "content": self.to_string(*args)})


class ConsoleWindow:
    """Control console"""

    def __init__(self, window):
        self.window = window
        ff = ttk.Frame(window)
        ff.pack(fill=tk.X)
        ttk.Label(ff, text="Console").pack(side=tk.LEFT)
        ttk.Button(ff, text="Clear", command=self.clear).pack(side="right")

        self.text_box = tk.Text(window, height=12)
        scrollbar = ttk.Scrollbar(window, command=self.text_box.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        self.text_box.config(yscrollcommand=scrollbar.set)

    def log(self, data):
        self.text_box.insert(tk.END, data)
        self.text_box.insert(tk.END, "\n")

    def info(self, data):
        self.text_box.insert(tk.END, data)
        self.text_box.insert(tk.END, "\n")

    def warning(self, data):
        self.text_box.insert(tk.END, data)
        line_start = self.text_box.index("insert linestart")
        line_end = self.text_box.index("insert lineend")
        self.text_box.tag_config("warning", foreground="orange")
        self.text_box.tag_add("warning", line_start, line_end)
        self.text_box.insert(tk.END, "\n")

    def error(self, data):
        self.text_box.insert(tk.END, data)
        line_start = self.text_box.index("insert linestart")
        line_end = self.text_box.index("insert lineend")
        self.text_box.tag_config("error", foreground="red")
        self.text_box.tag_add("error", line_start, line_end)
        self.text_box.insert(tk.END, "\n")

    def clear(self):
        self.text_box.delete("1.0", tk.END)
