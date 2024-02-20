import json
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from . import BASE_DIR
from .his import HistoryWindow
from .req import RequestWindow
from .con import ConsoleWindow
from .col import CollectionWindow


class MainWindow:

    history_list = []  # 历史记录列表

    def __init__(self):
        self.setup()
        self.root = tk.Tk()
        # 创建主窗口
        self.root.title("HTTP Client")
        self.root.after(0, self.on_start)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        pw1 = ttk.PanedWindow(self.root)
        pw1.pack()
        pw2 = ttk.PanedWindow(pw1, orient=tk.HORIZONTAL)
        pw1.add(pw2)

        self.history_top = ttk.Frame(pw2)
        pw2.add(self.history_top)
        self.history_window = HistoryWindow(self.history_top, self.history)

        self.notebook = ttk.Notebook(pw2)
        pw2.add(self.notebook)

        # self.col_top = ttk.Frame(pw2)
        # pw2.add(self.col_top)
        # self.col_win = CollectionWindow(self.col_top, **{"callback": self.colcb})

        console_top = ttk.Frame(pw1)
        pw1.add(console_top)
        self.console_window = ConsoleWindow(console_top)
        self.new_request()

        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        # file_menu.add_command(label="New Project", command=self.col_win.new_proj)
        file_menu.add_command(label="New Request", command=self.new_request)
        # file_menu.add_command(label="Open", command=self.col_win.open_proj)
        file_menu.add_command(label="Exit", command=self.on_closing)
        self.root.config(menu=menu_bar)

    def setup(self):
        if not os.path.exists(BASE_DIR):
            os.mkdir(BASE_DIR)

    def run(self):
        # 进入消息循环
        self.root.mainloop()

    def open_handler(self):
        """打开文件"""
        filepath = filedialog.askopenfilename()
        if filepath:
            with open(filepath, "r", encoding="utf-8") as file:
                data = file.read()

                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    messagebox.showerror("错误", "文本内容必须是一个json")
                    return

                self.new_request(data)

    def new_request(self, data=None):

        tl = ttk.Frame(self.notebook)
        req_win = RequestWindow(tl, self.request)
        if data is not None:
            req_win.fill_blank(data)
        self.notebook.add(tl, text="New request")
        self.notebook.select(self.notebook.index("end") - 1)

    def show_history(self, data):

        self.history_window.clear()
        for item in data:
            self.history_list.append(item)
            try:
                self.history_window.log(
                    f"{item.get('method' '')} {item.get('url', '')}"
                )
            except AttributeError:
                pass

    def on_start(self):

        filepath = os.path.join(BASE_DIR, "history.json")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as file:
                try:
                    data = file.read()
                    data = json.loads(data)
                    thread = threading.Thread(target=self.show_history, args=(data,))
                    thread.start()
                except json.JSONDecodeError:
                    pass

    def on_closing(self):

        with open(
            os.path.join(BASE_DIR, "history.json"), "w", encoding="utf-8"
        ) as file:
            file.write(json.dumps(self.history_list))
        self.root.destroy()

    def collection(self, action):

        if action == "new":
            self.new_request()

    def request(self, action, **kwargs):
        """请求窗口回调"""
        if action == "cache":
            # 缓存历史记录
            self.history_list.append(kwargs.get("data"))
        elif action == "history":
            # 写入历史记录列表
            self.history_window.log(kwargs.get("data"))
        elif action == "console":
            # 写入控制台
            level = kwargs.get("level")
            if level == "log":
                self.console_window.log(kwargs.get("content"))
            elif level == "info":
                self.console_window.info(kwargs.get("content"))
            elif level == "error":
                self.console_window.error(kwargs.get("content"))
            elif level == "warning":
                self.console_window.warning(kwargs.get("content"))
        elif action == "close":
            self.close_request()

    def history(self, action, **kwargs):
        """历史记录回调"""
        if action == "select":
            index = kwargs.get("index")
            if index is not None:
                i = len(self.history_list) - index - 1
                data = self.history_list[i]
                self.new_request(data)

        elif action == "destroy":
            index = kwargs.get("index")
            if index is not None:
                i = len(self.history_list) - index - 1
                self.history_list.pop(i)

        elif action == "clear":
            self.history_list = []

    def close_request(self):
        self.notebook.forget(self.notebook.select())

    def colcb(self, *args, **kwargs):
        print(kwargs)
