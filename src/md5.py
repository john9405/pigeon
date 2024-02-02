from tkinter import *
from tkinter import ttk
import hashlib
import time


class MD5GUI:
    """ MD5加密工具 """
    LOG_LINE_NUM = 0

    def __init__(self, init_window_name):
        self.init_window_name = init_window_name

    # 设置窗口
    def set_init_window(self):
        # 标签
        self.init_data_label = ttk.LabelFrame(self.init_window_name, text="待处理数据")
        self.init_data_label.grid(row=0, column=0, rowspan=10, columnspan=10)
        self.result_data_label = ttk.LabelFrame(self.init_window_name, text="输出结果")
        self.result_data_label.grid(row=0, column=12, rowspan=10, columnspan=10)
        self.log_label = ttk.LabelFrame(self.init_window_name, text="日志")
        self.log_label.grid(row=12, column=0, columnspan=20)
        btn = Button(self.init_window_name, text="清除", command=self.on_clear)
        btn.grid(row=12, column=21, pady=5)
        # 文本框
        self.init_data_Text = Text(self.init_data_label, width=67, height=35)  # 原始数据录入框
        self.init_data_Text.pack()
        self.result_data_Text = Text(self.result_data_label, width=67, height=35)  # 处理结果展示
        self.result_data_Text.pack()
        self.log_data_Text = Text(self.log_label, width=120, height=9)  # 日志框
        self.log_data_Text.pack()
        # 按钮
        self.str_trans_to_md5_button = Button(self.init_window_name, text="字符串转MD5", bg="lightblue", width=10, command=self.str_trans_to_md5)  # 调用内部方法  加()为直接调用
        self.str_trans_to_md5_button.grid(row=1, column=11, padx=5)

    # 功能函数
    def str_trans_to_md5(self):
        src = self.init_data_Text.get(1.0, END).strip().replace("\n", "").encode()
        # print("src =",src)
        if src:
            try:
                myMd5 = hashlib.md5()
                myMd5.update(src)
                myMd5_Digest = myMd5.hexdigest()
                # print(myMd5_Digest)
                # 输出到界面
                self.result_data_Text.delete(1.0, END)
                self.result_data_Text.insert(1.0, myMd5_Digest + "\n")
                self.result_data_Text.insert(END, myMd5_Digest.upper())
                self.write_log_to_Text("INFO:str_trans_to_md5 success")
            except Exception:
                self.result_data_Text.delete(1.0, END)
                self.result_data_Text.insert(1.0, "字符串转MD5失败")
        else:
            self.write_log_to_Text("ERROR:str_trans_to_md5 failed")

    # 获取当前时间
    def get_current_time(self):
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        return current_time

    # 日志动态打印
    def write_log_to_Text(self, logmsg):
        current_time = self.get_current_time()
        logmsg_in = str(current_time) + " " + str(logmsg) + "\n"  # 换行
        if self.LOG_LINE_NUM <= 7:
            self.log_data_Text.insert(END, logmsg_in)
            self.LOG_LINE_NUM = self.LOG_LINE_NUM + 1
        else:
            self.log_data_Text.delete(1.0, 2.0)
            self.log_data_Text.insert(END, logmsg_in)

    def on_clear(self):
        self.log_data_Text.delete(1.0, END)
