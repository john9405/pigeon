from tkinter import *
from tkinter import ttk, messagebox
import hashlib


class MD5GUI:
    """ MD5 Window """
    LOG_LINE_NUM = 0

    def __init__(self, master=None):
        self.root = ttk.Frame(master)
        self.set_init_window()

    def set_init_window(self):
        self.init_data_label = ttk.LabelFrame(self.root, text="Input")
        self.init_data_label.pack()
        self.str_trans_to_md5_button = Button(self.root, text="MD5", bg="lightblue", width=10, command=self.str_trans_to_md5)
        self.str_trans_to_md5_button.pack()

        self.result_data_label = ttk.LabelFrame(self.root, text="Output")
        self.result_data_label.pack()

        self.init_data_Text = Text(self.init_data_label, height=10)  # Raw data entry box
        self.init_data_Text.pack()
        self.result_data_Text = Text(self.result_data_label, height=10)  # Processing result presentation
        self.result_data_Text.pack()


    def str_trans_to_md5(self):
        src = self.init_data_Text.get(1.0, END).strip().replace("\n", "").encode()
        try:
            myMd5 = hashlib.md5()
            myMd5.update(src)
            myMd5_Digest = myMd5.hexdigest()
            self.result_data_Text.delete(1.0, END)
            self.result_data_Text.insert(1.0, myMd5_Digest + "\n")
            self.result_data_Text.insert(END, myMd5_Digest.upper())

        except Exception:
            self.result_data_Text.delete(1.0, END)
            messagebox.showinfo("Error", "MD5 Falied")
