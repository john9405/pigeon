import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import hashlib


class MD5GUI:
    """ MD5 Window """
    def __init__(self, master=None):
        self.root = tk.Toplevel(master)

        init_data_label = ttk.LabelFrame(self.root, text="Input")
        init_data_label.pack()
        ttk.Button(self.root, text="MD5", width=10, command=self.str_trans_to_md5).pack()

        result_data_label = ttk.LabelFrame(self.root, text="Output")
        result_data_label.pack()

        self.init_data_text = ScrolledText(init_data_label, height=10)  # Raw data entry box
        self.init_data_text.pack()
        self.result_data_text = ScrolledText(result_data_label, height=10)  # Processing result presentation
        self.result_data_text.pack()

    def str_trans_to_md5(self):
        src = self.init_data_text.get(1.0, "end").strip().replace("\n", "").encode()
        try:
            hasher = hashlib.md5()
            hasher.update(src)
            res = hasher.hexdigest()
            self.result_data_text.delete(1.0, "end")
            self.result_data_text.insert(1.0, res + "\n")
            self.result_data_text.insert("end", res.upper())
        except Exception:
            self.result_data_text.delete(1.0, "end")
            messagebox.showinfo("Error", "MD5 Falied")
