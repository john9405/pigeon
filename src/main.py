import json
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from . import BASE_DIR
from .his import HistoryWindow
from .req import RequestWindow
from .console import ConsoleWindow
from .col import CollectionWindow
from .doc.help import HelpWindow
from .doc.about import AboutWindow
from .tools.aes import AES_GUI
from .tools.b64 import Base64GUI
from .tools.md5 import MD5GUI
from .tools.pwd import GenPwdWindow
from .tools.timestamp import TimestampWindow
from .folder import FolderWindow


class MainWindow:
    history_list = []  # 历史记录列表

    def __init__(self):
        self.setup()
        self.root = tk.Tk()
        # 创建主窗口
        self.root.title("HTTP Client")
        self.root.after(0, self.on_start)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        ff = ttk.Frame(self.root)
        ff.pack(fill=tk.X)

        pw1 = ttk.PanedWindow(self.root)
        pw1.pack(fill="both", expand=True)
        pw2 = ttk.PanedWindow(pw1, orient=tk.HORIZONTAL)
        pw1.add(pw2)

        self.col_top = ttk.Frame(pw2)
        pw2.add(self.col_top)
        self.col_win = CollectionWindow(self.col_top, **{"callback": self.collection})
        self.col_win.on_start()

        self.notebook = ttk.Notebook(pw2)
        pw2.add(self.notebook)

        self.history_top = ttk.Frame(pw2)
        pw2.add(self.history_top)
        self.history_window = HistoryWindow(self.history_top, self.history)

        console_top = ttk.Frame(pw1)
        pw1.add(console_top)
        self.console_window = ConsoleWindow(console_top)
        self.new_request()

        ttk.Button(ff, text="New Request", command=self.new_request).pack(
            side=tk.LEFT, padx=5, pady=5
        )
        ttk.Button(ff, text="New Project", command=self.col_win.new_proj).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(ff, text="Open", command=self.col_win.open_proj).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(ff, text="CLose", command=self.close_request).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(ff, text="AES", command=self.aes_label).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(ff, text="Base64", command=self.b64_label).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(ff, text="MD5", command=self.md5_label).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(ff, text="PWD", command=self.pwd_label).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(ff, text="Timestamp", command=self.ts_label).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(ff, text="Help", command=self.help_label).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(ff, text="About", command=self.about_label).pack(
            side=tk.LEFT, padx=(0, 5)
        )

    def aes_label(self):
        self.new_label("aes")

    def b64_label(self):
        self.new_label("b64")

    def md5_label(self):
        self.new_label("md5")

    def pwd_label(self):
        self.new_label("pwd")

    def ts_label(self):
        self.new_label("ts")

    def help_label(self):
        self.new_label("help")

    def about_label(self):
        self.new_label("about")

    def new_label(self, command):
        if command == "aes":
            gui = AES_GUI(self.notebook)
            text = "AES"
        elif command == "b64":
            gui = Base64GUI(self.notebook)
            text = "Base64"
        elif command == "md5":
            gui = MD5GUI(self.notebook)
            text = "MD5"
        elif command == "pwd":
            gui = GenPwdWindow(self.notebook)
            text = "Password"
        elif command == "ts":
            gui = TimestampWindow(self.notebook)
            text = "Timestamp"
        elif command == "about":
            gui = AboutWindow(self.notebook)
            text = "About"
        elif command == "help":
            gui = HelpWindow(self.notebook)
            text = "Help"

        self.notebook.add(gui.root, text=text)
        self.notebook.select(self.notebook.index(tk.END) - 1)

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

    def new_request(self, data=None, **kwargs):
        tl = ttk.Frame(self.notebook)
        req_win = RequestWindow(
            window=tl, callback=self.request, get_script=self.col_win.get_script
        )
        if data is not None:
            req_win.fill_blank(data)
        if "item_id" in kwargs:
            req_win.item_id = kwargs["item_id"]
        self.notebook.add(tl, text="Request")
        self.notebook.select(self.notebook.index(tk.END) - 1)

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
        self.col_win.on_close()
        with open(
            os.path.join(BASE_DIR, "history.json"), "w", encoding="utf-8"
        ) as file:
            file.write(json.dumps(self.history_list))
        self.root.destroy()

    def collection(self, **kwargs):
        if kwargs["tag"] in ["project", "folder"]:
            folder_window = FolderWindow(
                master=self.notebook,
                item_id=kwargs["item_id"],
                callback=self.col_win.save_item,
                data=kwargs["data"],
            )
            self.notebook.add(folder_window.root, text=kwargs["tag"])
            self.notebook.select(self.notebook.index(tk.END) - 1)
        else:
            self.new_request(kwargs["data"], item_id=kwargs["item_id"])

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
        elif action == "save":
            self.col_win.save_item(kwargs["item_id"], kwargs["data"])

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
