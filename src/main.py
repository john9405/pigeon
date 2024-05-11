import os
import threading
import tkinter as tk
from tkinter import ttk

from . import WORK_DIR, BASE_DIR
from .his import HistoryWindow
from .req import RequestWindow
from .console import ConsoleWindow
from .col import CollectionWindow, ProjectWindow, FolderWindow
from .env import EnvironmentWindow, VariableWindow
from .doc.help import HelpWindow
from .doc.about import AboutWindow
from .tools.aes import AES_GUI
from .tools.b64 import Base64GUI
from .tools.md5 import MD5GUI
from .tools.pwd import GenPwdWindow
from .tools.timestamp import TimestampWindow
from .tools.regex import RegexWindow


class MainWindow:
    tag_list = []  # List of enabled labels
    sidebar = ""

    def __init__(self):
        self.setup()
        self.root = tk.Tk()
        # Create main window
        self.root.title("HTTP Client")
        self.root.after(0, self.on_start)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        ff = ttk.Frame(self.root)
        ff.pack(fill=tk.X)
        fe = ttk.Frame(self.root)
        fe.pack(side=tk.LEFT, fill=tk.Y)

        pw1 = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_sidebar = ttk.Frame(pw1)
        pw1.add(self.main_sidebar)
        pw2 = ttk.PanedWindow(pw1)
        self.notebook = ttk.Notebook(pw2)
        pw2.add(self.notebook)
        console_top = ttk.Frame(pw2)
        pw2.add(console_top)
        pw1.add(pw2)
        pw1.pack(fill="both", expand=True)

        self.col_top = ttk.Frame(self.main_sidebar)
        self.col_win = CollectionWindow(self.col_top, **{"callback": self.collection})
        self.history_top = ttk.Frame(self.main_sidebar)
        self.history_window = HistoryWindow(self.history_top, self.history)
        self.env_win = EnvironmentWindow(master=self.main_sidebar, callback=self.environment)
        self.env_top = self.env_win.root
        self.col_top.pack(expand=True, fill=tk.BOTH)
        self.sidebar = "collection"

        self.console_window = ConsoleWindow(console_top)
        self.new_request()

        ttk.Button(ff, text="AES", command=self.aes_label).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(ff, text="Base64", command=self.b64_label).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(ff, text="MD5", command=self.md5_label).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(ff, text="PWD", command=self.pwd_label).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(ff, text="Timestamp", command=self.ts_label).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(ff, text="Regex", command=self.regex_label).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(ff, text="Help", command=self.help_label).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(ff, text="About", command=self.about_label).pack(side=tk.LEFT, padx=(0, 5))

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
                name="add",
                file=os.path.join(BASE_DIR, *("assets", "16", "add.png")),
                height=16,
                width=16
            )
        ]
        btnframe = ttk.Frame(self.root)
        btnframe.place(relx=1-0.002, rely=0.04, anchor=tk.NE)
        ttk.Button(btnframe, image="close", command=self.close_request).pack(side=tk.RIGHT)
        ttk.Button(btnframe, image="add", command=self.new_request).pack(side=tk.RIGHT)
        ttk.Button(fe, image="collection", text="Col", command=self.col_lab).pack()
        ttk.Button(fe, image="environment", text="Env", command=self.env_lab).pack()
        ttk.Button(fe, image="history", text="His", command=self.his_lab).pack()

    def col_lab(self):
        if self.sidebar != "collection":
            self.env_top.forget()
            self.history_top.forget()
            self.col_top.pack(expand=tk.YES, fill=tk.BOTH)
            self.sidebar = "collection"

    def his_lab(self):
        if self.sidebar != "history":
            self.col_top.forget()
            self.env_top.forget()
            self.history_top.pack(expand=tk.YES, fill=tk.BOTH)
            self.sidebar = "history"

    def env_lab(self):
        if self.sidebar != "environment":
            self.col_top.forget()
            self.history_top.forget()
            self.env_top.pack(expand=tk.YES, fill=tk.BOTH)
            self.sidebar = "environment"

    def aes_label(self):
        if "AES" in self.tag_list:
            self.notebook.select(self.tag_list.index("AES"))
        else:
            self.notebook.add(AES_GUI(self.notebook).root, text="AES")
            self.notebook.select(self.notebook.index(tk.END) - 1)
            self.tag_list.append("AES")

    def b64_label(self):
        if "Base64" in self.tag_list:
            self.notebook.select(self.tag_list.index("Base64"))
        else:
            self.notebook.add(Base64GUI(self.notebook).root, text="Base64")
            self.notebook.select(self.notebook.index(tk.END) - 1)
            self.tag_list.append("Base64")

    def md5_label(self):
        if "MD5" in self.tag_list:
            self.notebook.select(self.tag_list.index("MD5"))
        else:
            self.notebook.add(MD5GUI(self.notebook).root, text="MD5")
            self.notebook.select(self.notebook.index(tk.END) - 1)
            self.tag_list.append("MD5")

    def pwd_label(self):
        if "Password" in self.tag_list:
            self.notebook.select(self.tag_list.index("Password"))
        else:
            self.notebook.add(GenPwdWindow(self.notebook).root, text="Password")
            self.notebook.select(self.notebook.index(tk.END) - 1)
            self.tag_list.append("Password")

    def ts_label(self):
        if "Timestamp" in self.tag_list:
            self.notebook.select(self.tag_list.index("Timestamp"))
        else:
            self.notebook.add(TimestampWindow(self.notebook).root, text="Timestamp")
            self.notebook.select(self.notebook.index(tk.END) - 1)
            self.tag_list.append("Timestamp")

    def regex_label(self):
        if "Regex" in self.tag_list:
            self.notebook.select(self.tag_list.index("Regex"))
        else:
            self.notebook.add(RegexWindow(self.notebook).root, text="Regex")
            self.notebook.select(self.notebook.index(tk.END) - 1)
            self.tag_list.append("Regex")

    def help_label(self):
        if "Help" in self.tag_list:
            self.notebook.select(self.tag_list.index("Help"))
        else:
            self.notebook.add(HelpWindow(self.notebook).root, text="Help")
            self.notebook.select(self.notebook.index(tk.END) - 1)
            self.tag_list.append("Help")

    def about_label(self):
        if "About" in self.tag_list:
            self.notebook.select(self.tag_list.index("About"))
        else:
            self.notebook.add(AboutWindow(self.notebook).root, text="About")
            self.notebook.select(self.notebook.index(tk.END) - 1)
            self.tag_list.append("About")

    def setup(self):
        if not os.path.exists(WORK_DIR):
            os.mkdir(WORK_DIR)

    def run(self):
        # Enter message loop
        self.root.mainloop()

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
            del_variable=self.env_win.del_variable,
        )
        self.notebook.add(gui.root, text=kwargs.get("collection"))
        self.notebook.select(self.notebook.index(tk.END) - 1)
        self.tag_list.append("env_" + kwargs.get("item_id", ""))

    def close_request(self):
        self.tag_list.pop(self.notebook.index(self.notebook.select()))
        self.notebook.forget(self.notebook.select())
