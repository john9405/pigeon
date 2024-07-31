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
        self.root.geometry("800x600")

        top_bar = ttk.Frame(self.root)
        top_bar.pack(fill=tk.X)
        state_bar = ttk.Frame(self.root)
        state_bar.pack(side=tk.BOTTOM, fill=tk.X)
        side_bar = ttk.Frame(self.root)
        side_bar.pack(side=tk.LEFT, fill=tk.Y)

        nba = ttk.Notebook(self.root)
        col_top = ttk.Frame(nba)
        self.col_win = CollectionWindow(col_top, **{"callback": self.collection})
        nba.add(col_top, text='collection')
        self.env_win = EnvironmentWindow(master=nba, callback=self.environment)
        nba.add(self.env_win.root, text='environment')
        history_top = ttk.Frame(nba)
        self.history_window = HistoryWindow(history_top, self.history)
        nba.add(history_top, text='history')
        console_top = ttk.Frame(nba)
        self.console_window = ConsoleWindow(console_top)
        nba.add(console_top, text='console')
        nba.pack(fill='both', expand=True)

        menu = tk.Menu(self.root)
        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label="New request", command=self.new_request)
        file_menu.add_command(label="New collection", command=self.col_win.new_col)
        file_menu.add_command(label="Import", command=self.col_win.open_proj)
        file_menu.add_command(label="Export", command=self.col_win.export_proj)
        file_menu.add_command(label="Exit", command=self.on_closing)
        menu.add_cascade(label="File", menu=file_menu)
        tool_menu = tk.Menu(menu, tearoff=False)
        tool_menu.add_command(label="AES", command=AesGui)
        tool_menu.add_command(label="Base64", command=Base64GUI)
        tool_menu.add_command(label="MD5", command=MD5GUI)
        tool_menu.add_command(label="PWD", command=GenPwdWindow)
        tool_menu.add_command(label="Timestamp", command=TimestampWindow)
        tool_menu.add_command(label="Regex", command=RegexWindow)
        menu.add_cascade(label="Tools", menu=tool_menu)
        help_menu = tk.Menu(menu, tearoff=False)
        help_menu.add_command(label="Help", command=HelpWindow)
        help_menu.add_command(label="About", command=AboutWindow)
        menu.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menu)

        ttk.Sizegrip(self.root).pack(side="bottom", anchor="se")

    def new_request(self, data=None, **kwargs):
        tl = tk.Toplevel(self.root)
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
        if kwargs["tag"] == "project":
            ProjectWindow(
                master=self.root,
                item_id=kwargs["item_id"],
                callback=self.col_win.save_item,
                data=kwargs["data"],
            )
        elif kwargs["tag"] == "folder":
            FolderWindow(
                master=self.root,
                item_id=kwargs["item_id"],
                callback=self.col_win.save_item,
                data=kwargs["data"],
            )
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
        VariableWindow(
            self.root,
            collection=kwargs.get("collection", ""),
            data=kwargs.get("data", {}),
            set_variable=self.env_win.set_variable,
        )
