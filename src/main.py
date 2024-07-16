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
from .help import HelpWindow
from .about import AboutWindow
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
        state_bar = ttk.Frame(self.root)
        state_bar.pack(side=tk.BOTTOM, fill=tk.X)
        side_bar = ttk.Frame(self.root)
        side_bar.pack(side=tk.LEFT, fill=tk.Y)

        pwa = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        pwa.pack(fill="both", expand=True)
        self.notebook = ttk.Notebook(pwa)
        pwa.add(self.notebook, weight=3)
        pwb = ttk.PanedWindow(pwa)
        pwa.add(pwb, weight=1)
        nba = ttk.Notebook(pwb)
        pwb.add(nba, weight=5)
        nbb = ttk.Notebook(pwb)
        pwb.add(nbb, weight=5)

        col_top = ttk.Frame(nba)
        self.col_win = CollectionWindow(col_top, **{"callback": self.collection})
        nba.add(col_top, text='collection')
        self.env_win = EnvironmentWindow(master=nba, callback=self.environment)
        nba.add(self.env_win.root, text='environment')
        history_top = ttk.Frame(nbb)
        self.history_window = HistoryWindow(history_top, self.history)
        nbb.add(history_top, text='history')
        console_top = ttk.Frame(nbb)
        self.console_window = ConsoleWindow(console_top)
        nbb.add(console_top, text='console')

        self.new_request()

        ttk.Button(top_bar, text="Request", command=self.new_request).pack(side=tk.LEFT)
        ttk.Button(top_bar, text="AES", command=lambda: self.show_label("AES")).pack(side=tk.LEFT)
        ttk.Button(top_bar, text="Base64", command=lambda: self.show_label("Base64")).pack(side=tk.LEFT)
        ttk.Button(top_bar, text="MD5", command=lambda: self.show_label("MD5")).pack(side=tk.LEFT)
        ttk.Button(top_bar, text="PWD", command=lambda: self.show_label("Password")).pack(side=tk.LEFT)
        ttk.Button(top_bar, text="Timestamp", command=lambda: self.show_label("Timestamp")).pack(side=tk.LEFT)
        ttk.Button(top_bar, text="Regex", command=lambda: self.show_label("Regex")).pack(side=tk.LEFT)
        ttk.Button(top_bar, text="Help", command=lambda: self.show_label("Help")).pack(side=tk.LEFT)
        ttk.Button(top_bar, text="About", command=lambda: self.show_label("About")).pack(side=tk.LEFT)
        ttk.Button(top_bar, text="close", command=self.close_request).pack(side=tk.LEFT)

        ttk.Sizegrip(state_bar).pack(side="right", anchor="se")

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
            else:
                gui = None
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
        page = self.notebook.select()
        if page:
            self.tag_list.pop(self.notebook.index(page))
            self.notebook.forget(page)
