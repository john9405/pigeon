import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import re
import os
from .. import BASE_DIR

class RegexWindow:
    def __init__(self, master=None) -> None:
        # 创建主窗口
        root = ttk.Frame(master)

        # 创建选项
        options_frame = ttk.Frame(root)
        options_frame.pack()

        # 创建正则表达式输入框
        regex_label = ttk.Label(options_frame, text="Regular expression:")
        regex_label.pack(side=tk.LEFT)
        regex_entry = ttk.Entry(options_frame)
        regex_entry.pack(side=tk.LEFT)

        ignore_case_var = tk.BooleanVar(value=False)
        ignore_case_checkbox = ttk.Checkbutton(options_frame, text="Ignore case", variable=ignore_case_var)
        ignore_case_checkbox.pack(side=tk.LEFT)

        multi_line_var = tk.BooleanVar(value=False)
        multi_line_checkbox = ttk.Checkbutton(options_frame, text="Multiline mode", variable=multi_line_var)
        multi_line_checkbox.pack(side=tk.LEFT)
        # 创建查找按钮
        find_button = ttk.Button(options_frame,text="Search",command=lambda: self.find_matches(ignore_case_var, multi_line_var))
        find_button.pack(side=tk.LEFT)

        # 创建文本输入框
        text_label = ttk.LabelFrame(root, text="Input:")
        text_label.pack(padx=10)
        text_entry = ScrolledText(text_label, height=10)
        text_entry.pack()

        # 创建结果显示区域
        result_label = ttk.LabelFrame(root, text="Output:")
        result_label.pack(padx=10)
        result_text = ScrolledText(result_label, height=10)
        result_text.pack()

        with open(os.path.join(BASE_DIR, *("assets", "regex.md")), "r", encoding="utf-8") as f:
            st = ScrolledText(root)
            st.insert("1.0", f.read())
            st.configure(state='disabled')
            st.pack(padx=10, pady=10)

        self.root = root
        self.regex_entry = regex_entry
        self.text_entry = text_entry
        self.result_text = result_text

    def find_matches(self, ignore_case_var, multi_line_var):
        regex = self.regex_entry.get()
        text = self.text_entry.get("1.0", tk.END)
        flags = 0
        if ignore_case_var.get():  # 如果勾选了忽略大小写
            flags |= re.IGNORECASE
        if multi_line_var.get():  # 如果勾选了多行模式
            flags |= re.MULTILINE

        try:
            matches = re.finditer(regex, text, flags)
            self.result_text.delete(1.0, tk.END)
            if matches:
                for item in matches:
                    self.result_text.insert(tk.END, f"Match: {item}\n")
            else:
                self.result_text.insert(tk.END, "No matches found.\n")
        except re.error as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Error: {e}")
