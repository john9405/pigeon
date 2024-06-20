import os
import threading
import tkinter as tk
from tkinter import ttk

from . import BASE_DIR
from .his import HistoryWindow
from .req import RequestWindow
from .console import ConsoleWindow
from .col import CollectionWindow, ProjectWindow, FolderWindow
from .env import EnvironmentWindow, VariableWindow
from .doc.help import HelpWindow
from .doc.about import AboutWindow
from .tools.aes import AesGui
from .tools.b64 import Base64GUI
from .tools.md5 import MD5GUI
from .tools.pwd import GenPwdWindow
from .tools.timestamp import TimestampWindow
from .tools.regex import RegexWindow


class MainWindow:
    tag_list = []  # List of enabled labels
    sidebar = ""
    console_state = False

    def __init__(self):
        self.root = tk.Tk()
        # Create main window
        self.root.title("HTTP Client")
        self.root.after(0, self.on_start)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        top_bar = ttk.Frame(self.root)
        top_bar.pack(fill=tk.X)
        ttk.Separator(self.root).pack(fill=tk.X)
        state_bar = ttk.Frame(self.root)
        state_bar.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Separator(self.root).pack(side=tk.BOTTOM, fill=tk.X)
        side_bar = ttk.Frame(self.root)
        side_bar.pack(side=tk.LEFT, fill=tk.Y)
        ttk.Separator(self.root, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y)

        pw1 = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_sidebar = ttk.Frame(pw1)
        pw1.add(self.main_sidebar)
        self.pw2 = ttk.PanedWindow(pw1)
        self.notebook = ttk.Notebook(self.pw2)
        self.pw2.add(self.notebook, weight=11)
        self.console_top = ttk.Frame(self.pw2)
        pw1.add(self.pw2)
        pw1.pack(fill="both", expand=True)

        self.col_top = ttk.Frame(self.main_sidebar)
        self.col_win = CollectionWindow(self.col_top, **{"callback": self.collection})
        self.history_top = ttk.Frame(self.main_sidebar)
        self.history_window = HistoryWindow(self.history_top, self.history)
        self.env_win = EnvironmentWindow(master=self.main_sidebar, callback=self.environment)
        self.env_top = self.env_win.root
        self.col_top.pack(expand=True, fill=tk.BOTH)
        self.sidebar = "collection"

        self.console_window = ConsoleWindow(self.console_top)
        self.new_request()

        self.images = [
            tk.PhotoImage(
                name="collection",
                file=os.path.join(BASE_DIR, *("assets", "32", "work.png")),
                height=32,
                width=32,
            ),
            tk.PhotoImage(
                name="environment",
                file=os.path.join(BASE_DIR, *("assets", "32", "training.png")),
                height=32,
                width=32,
            ),
            tk.PhotoImage(
                name="history",
                file=os.path.join(BASE_DIR, *("assets", "32", "history.png")),
                height=32,
                width=32,
            ),
            tk.PhotoImage(
                name="close",
                file=os.path.join(BASE_DIR, *("assets", "16", "close.png")),
                height=16,
                width=16
            ),
            tk.PhotoImage(
                name="file-add",
                file=os.path.join(BASE_DIR, *("assets", "16", "file-add.png")),
                height=16,
                width=16
            ),
            tk.PhotoImage(
                name="comment",
                file=os.path.join(BASE_DIR, *("assets", "16", "comment.png")),
                height=16,
                width=16
            )
        ]
        ttk.Button(top_bar, text="AES", command=lambda: self.show_label("AES")).pack(side=tk.LEFT)
        ttk.Button(top_bar, text="Base64", command=lambda: self.show_label("Base64")).pack(side=tk.LEFT)
        ttk.Button(top_bar, text="MD5", command=lambda: self.show_label("MD5")).pack(side=tk.LEFT)
        ttk.Button(top_bar, text="PWD", command=lambda: self.show_label("Password")).pack(side=tk.LEFT)
        ttk.Button(top_bar, text="Timestamp", command=lambda: self.show_label("Timestamp")).pack(side=tk.LEFT)
        ttk.Button(top_bar, text="Regex", command=lambda: self.show_label("Regex")).pack(side=tk.LEFT)
        ttk.Button(top_bar, text="Help", command=lambda: self.show_label("Help")).pack(side=tk.LEFT)
        ttk.Button(top_bar, text="About", command=lambda: self.show_label("About")).pack(side=tk.LEFT)
        ttk.Button(top_bar, image="close", command=self.close_request).pack(side=tk.RIGHT)
        ttk.Button(top_bar, image="file-add", command=self.new_request).pack(side=tk.RIGHT)
        ttk.Separator(top_bar, orient=tk.VERTICAL).pack(side=tk.RIGHT, fill=tk.Y)
        ttk.Button(side_bar, image="collection", command=lambda: self.switch_label("collection")).pack()
        ttk.Button(side_bar, image="environment", command=lambda: self.switch_label("environment")).pack()
        ttk.Button(side_bar, image="history", command=lambda: self.switch_label("history")).pack()
        ttk.Button(state_bar, image="comment", command=self.show_console).pack(side=tk.RIGHT)

    def show_console(self):
        if self.console_state:
            self.pw2.forget(self.console_top)
            self.console_state =False
        else:
            self.pw2.add(self.console_top, weight=1)
            self.console_state = True

    def switch_label(self, name):
        if self.sidebar != name:
            if self.sidebar == 'collection':
                self.col_top.forget()
            elif self.sidebar == 'history':
                self.history_top.forget()
            elif self.sidebar == 'environment':
                self.env_top.forget()
            if name == 'collection':
                self.col_top.pack(expand=tk.YES, fill=tk.BOTH)
            elif name == 'history':
                self.history_top.pack(expand=tk.YES, fill=tk.BOTH)
            elif name == 'environment':
                self.env_top.pack(expand=tk.YES, fill=tk.BOTH)
            self.sidebar = name

    def show_label(self, name):
        if name in self.tag_list:
            self.notebook.select(self.tag_list.index(name))
        else:
            if name == "AES":
                gui = AesGui(self.notebook)
            elif name == "Base64":
                gui = Base64GUI(self.notebook)
            elif name == "MD5":
                gui = MD5GUI(self.notebook)
            elif name == "Password":
                gui = GenPwdWindow(self.notebook)
            elif name == "Timestamp":
                gui = TimestampWindow(self.notebook)
            elif name == "Regex":
                gui = RegexWindow(self.notebook)
            elif name == "Help":
                gui = HelpWindow(self.notebook)
            elif name == "About":
                gui = AboutWindow(self.notebook)
            self.notebook.add(gui.root, text=name)
            self.notebook.select(self.notebook.index(tk.END) - 1)
            self.tag_list.append(name)

    def new_request(self, data=None, **kwargs):
        if kwargs.get("item_id") in self.tag_list:
            self.notebook.select(self.tag_list.index(kwargs["item_id"]))
            return

        tl = ttk.Frame(self.notebook)
        req_win = RequestWindow(
            window=tl, 
            callback=self.request, 
            get_script=self.col_win.get_script,
            env_variable=self.env_win.get_variable,
            local_variable=self.col_win.get_variable
        )
        req_win.item_id = kwargs.get("item_id")
        if data is not None:
            req_win.fill_blank(data)
        self.notebook.add(tl, text="Request")
        self.notebook.select(self.notebook.index(tk.END) - 1)
        self.tag_list.append(kwargs.get("item_id", ""))

    def on_start(self):
        t1 = threading.Thread(target=self.col_win.on_start)
        t2 = threading.Thread(target=self.env_win.on_start)
        t3 = threading.Thread(target=self.history_window.on_start)
        t1.start()
        t2.start()
        t3.start()

    def on_closing(self):
        self.col_win.on_close()
        self.env_win.on_end()
        self.history_window.on_end()
        self.root.destroy()

    def collection(self, **kwargs):
        if kwargs["item_id"] in self.tag_list:
            self.notebook.select(self.tag_list.index(kwargs["item_id"]))
            return

        if kwargs["tag"] == "project":
            win = ProjectWindow(
                master=self.notebook,
                item_id=kwargs["item_id"],
                callback=self.col_win.save_item,
                data=kwargs["data"],
            )
            self.notebook.add(win.root, text=kwargs["tag"])
            self.notebook.select(self.notebook.index(tk.END) - 1)
            self.tag_list.append(kwargs["item_id"])

        if kwargs["tag"] == "folder":
            folder_window = FolderWindow(
                master=self.notebook,
                item_id=kwargs["item_id"],
                callback=self.col_win.save_item,
                data=kwargs["data"],
            )
            self.notebook.add(folder_window.root, text=kwargs["tag"])
            self.notebook.select(self.notebook.index(tk.END) - 1)
            self.tag_list.append(kwargs["item_id"])

        else:
            self.new_request(kwargs["data"], item_id=kwargs["item_id"])

    def request(self, action, **kwargs):
        """Request window callback"""
        if action == "cache":
            # Cache history
            self.history_window.on_cache(kwargs.get("data"))
        elif action == "console":
            # Write console
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
            return self.col_win.save_item(kwargs["item_id"], kwargs["data"])
        return None

    def history(self, **kwargs):
        """History callback"""
        self.new_request(kwargs.get("data"))

    def environment(self, **kwargs):
        if "env_" + kwargs.get("item_id") in self.tag_list:
            self.notebook.select(self.tag_list.index("env_" + kwargs["item_id"]))
            return
        gui = VariableWindow(
            self.notebook,
            collection=kwargs.get("collection", ""),
            data=kwargs.get("data", {}),
            set_variable=self.env_win.set_variable,
        )
        self.notebook.add(gui.root, text=kwargs.get("collection"))
        self.notebook.select(self.notebook.index(tk.END) - 1)
        self.tag_list.append("env_" + kwargs.get("item_id", ""))

    def close_request(self):
        self.tag_list.pop(self.notebook.index(self.notebook.select()))
        self.notebook.forget(self.notebook.select())
