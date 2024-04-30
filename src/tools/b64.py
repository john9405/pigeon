import base64
import tkinter as tk
from tkinter import messagebox, ttk


class Base64GUI:
    """ base64 加解密工具 """
    def __init__(self, master=None) -> None:
        self.root = ttk.Frame(master)

        input_frame = ttk.LabelFrame(self.root, text="Input")
        input_frame.pack()
        self.input_box = tk.Text(input_frame, height=10)
        self.input_box.pack()
        bframe = tk.Frame(self.root)
        bframe.pack()
        ebtn = ttk.Button(bframe, text="加密", command=self.encrypto)
        ebtn.pack(side=tk.LEFT)
        dbtn = ttk.Button(bframe, text="解密", command=self.decrypto)
        dbtn.pack(side=tk.LEFT)
        output_frame = ttk.LabelFrame(self.root, text="Output")
        output_frame.pack()
        self.output_box = tk.Text(output_frame, height=10)
        self.output_box.pack()

    def encrypto(self):
        input_text = self.input_box.get(1.0, tk.END)
        res = base64.b64encode(input_text.encode("utf-8")).decode("utf-8")
        self.output_box.delete(1.0, tk.END)
        self.output_box.insert(1.0, res)

    def decrypto(self):
        try:
            input_text = self.input_box.get(1.0, tk.END)
            res = base64.b64decode(input_text.encode("utf-8")).decode("utf-8")
            self.output_box.delete(1.0, tk.END)
            self.output_box.insert(1.0, res)
        except Exception as e:
            messagebox.showerror("错误", e)
