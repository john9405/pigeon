import tkinter as tk
from tkinter import ttk, messagebox
import secrets
import string
import re

class GenPwdWindow:
    """ 随即密码生成器 """
    def __init__(self, master=None) -> None:
        self.root = ttk.Frame(master)
        self.dcb = tk.BooleanVar(value=True)  # 数字
        self.lccb = tk.BooleanVar(value=True)  # 小写字母
        self.uccb = tk.BooleanVar(value=True)  # 大写字母
        self.pcb = tk.BooleanVar()  # 字符
        self.l = tk.IntVar(value=8)

        vcmd = (self.root.register(lambda x: re.search(r"^\d+$", x) is not None), '%P')
        ivcmd = (self.root.register(lambda :messagebox.showerror("Error", "The password length must be an integer")), )
        # 密码长度标签和输入框
        length_label = ttk.Label(self.root, text="Password Length:")
        length_label.grid(row=0, column=0)
        ttk.Entry(self.root, textvariable=self.l, validate='key', validatecommand=vcmd, invalidcommand=ivcmd).grid(row=0, column=1, columnspan=4, sticky='w')

        # 密码复杂程度选择
        complexity_label = ttk.Label(self.root, text="Password Complexity:")
        complexity_label.grid(row=1, column=0)
        ttk.Checkbutton(self.root, text="0-9", variable=self.dcb).grid(row=1, column=1)
        ttk.Checkbutton(self.root, text="a-z", variable=self.lccb).grid(row=1, column=2)
        ttk.Checkbutton(self.root, text="A-z", variable=self.uccb).grid(row=1, column=3)
        ttk.Checkbutton(self.root, text="other", variable=self.pcb).grid(row=1, column=4)

        # 生成密码按钮
        generate_button = ttk.Button(self.root, text="Generate Password", command=self.generate_password)
        generate_button.grid(row=2, column=0, columnspan=5)

        # 生成密码的标签
        password_label = ttk.Label(self.root, text="Generated Password:")
        password_label.grid(row=3, column=0)

        self.pwd_entry = ttk.Entry(self.root)
        self.pwd_entry.grid(row=3, column=1, columnspan=4, sticky='w')

    def generate_password(self):
        password_length = self.l.get()
        alphabet = string.digits if self.dcb.get() else ""
        alphabet += string.ascii_lowercase if self.lccb.get() else ""
        alphabet += string.ascii_uppercase if self.uccb.get() else ""
        alphabet += string.punctuation if self.pcb.get() else ""
        password = "".join(secrets.choice(alphabet) for _ in range(password_length)) if alphabet > "" else ""
        self.pwd_entry.delete(0, tk.END)
        self.pwd_entry.insert(0, password)
