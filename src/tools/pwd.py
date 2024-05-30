import tkinter as tk
from tkinter import ttk
import random
import string


class GenPwdWindow:
    """ 随即密码生成器 """
    def __init__(self, master=None) -> None:
        window = ttk.Frame(master)
        self.root = window
        # 密码长度标签和输入框
        length_label = tk.Label(window, text="Password Length:")
        length_label.grid(row=0, column=0)
        self.length_entry = tk.Entry(window)
        self.length_entry.insert(0, "6")
        self.length_entry.grid(row=0, column=1, sticky='w')

        # 密码复杂程度选择
        complexity_label = tk.Label(window, text="Password Complexity:")
        complexity_label.grid(row=1, column=0)
        self.complexity_dropdown = ttk.Combobox(window, values=("Low", "Medium", "High"))
        self.complexity_dropdown.current(0)
        self.complexity_dropdown.grid(row=1, column=1)

        # 生成密码按钮
        generate_button = tk.Button(window, text="Generate Password", command=self.generate_password)
        generate_button.grid(row=2, column=0, columnspan=2)

        # 生成密码的标签
        password_label = tk.Label(window, text="Generated Password:")
        password_label.grid(row=3, column=0)

        self.pwd_entry = tk.Entry(window)
        self.pwd_entry.grid(row=3, column=1,  sticky='w')

    def generate_password(self):
        password_length = int(self.length_entry.get())
        complexity = self.complexity_dropdown.get()

        if complexity == "Low":
            characters = string.ascii_lowercase + string.digits
        elif complexity == "Medium":
            characters = string.ascii_lowercase + string.digits + string.ascii_uppercase
        else:
            characters = (
                string.ascii_lowercase
                + string.digits
                + string.punctuation
                + string.ascii_uppercase
            )

        password = "".join(random.choice(characters) for _ in range(password_length))
        self.pwd_entry.delete(0, tk.END)
        self.pwd_entry.insert(0, password)
