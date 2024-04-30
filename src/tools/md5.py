from tkinter import *
from tkinter import ttk
import hashlib


class MD5GUI:
    """ MD5加密工具 """
    LOG_LINE_NUM = 0

    def __init__(self, master=None):
        self.root = ttk.Frame(master)
        self.set_init_window()

    # 设置窗口
    def set_init_window(self):
        # 标签
        self.init_data_label = ttk.LabelFrame(self.root, text="待处理数据")
        self.init_data_label.pack()
        # 按钮
        self.str_trans_to_md5_button = Button(self.root, text="字符串转MD5", bg="lightblue", width=10, command=self.str_trans_to_md5)  # 调用内部方法  加()为直接调用
        self.str_trans_to_md5_button.pack()

        self.result_data_label = ttk.LabelFrame(self.root, text="输出结果")
        self.result_data_label.pack()

        # 文本框
        self.init_data_Text = Text(self.init_data_label, height=10)  # 原始数据录入框
        self.init_data_Text.pack()
        self.result_data_Text = Text(self.result_data_label, height=10)  # 处理结果展示
        self.result_data_Text.pack()


    # 功能函数
    def str_trans_to_md5(self):
        src = self.init_data_Text.get(1.0, END).strip().replace("\n", "").encode()
        # print("src =",src)
        try:
            myMd5 = hashlib.md5()
            myMd5.update(src)
            myMd5_Digest = myMd5.hexdigest()
            # print(myMd5_Digest)
            # 输出到界面
            self.result_data_Text.delete(1.0, END)
            self.result_data_Text.insert(1.0, myMd5_Digest + "\n")
            self.result_data_Text.insert(END, myMd5_Digest.upper())
            
        except Exception:
            self.result_data_Text.delete(1.0, END)
            self.result_data_Text.insert(1.0, "字符串转MD5失败")
