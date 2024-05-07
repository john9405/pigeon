import json
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from . import WORK_DIR, BASE_DIR
from .his import HistoryWindow
from .req import RequestWindow
from .console import ConsoleWindow
from .col import CollectionWindow
from .env import EnvironmentWindow
from .folder import FolderWindow
from .doc.help import HelpWindow
from .doc.about import AboutWindow
from .tools.aes import AES_GUI
from .tools.b64 import Base64GUI
from .tools.md5 import MD5GUI
from .tools.pwd import GenPwdWindow
from .tools.timestamp import TimestampWindow
from .tools.regex import RegexWindow


class MainWindow:
    history_list = []  # History list
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

        pw1 = ttk.PanedWindow(self.root)
        pw1.pack(fill="both", expand=True)
        pw2 = ttk.PanedWindow(pw1, orient=tk.HORIZONTAL)
        pw1.add(pw2)

        self.main_sidebar = ttk.Frame(pw2)
        pw2.add(self.main_sidebar)
        self.notebook = ttk.Notebook(pw2)
        pw2.add(self.notebook)

        self.col_top = ttk.Frame(self.main_sidebar)
        self.col_win = CollectionWindow(self.col_top, **{"callback": self.collection})
        self.col_win.on_start()
        self.history_top = ttk.Frame(self.main_sidebar)
        self.history_window = HistoryWindow(self.history_top, self.history)
        self.env_win = EnvironmentWindow(master=self.main_sidebar)
        self.env_top = self.env_win.root
        self.col_top.pack(expand=True, fill=tk.BOTH)
        self.sidebar = "collection"

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
        ttk.Button(ff, text="Regex", command=self.regex_label).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(ff, text="Help", command=self.help_label).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(ff, text="About", command=self.about_label).pack(
            side=tk.LEFT, padx=(0, 5)
        )

        self.images = [
            tk.PhotoImage(
                name="collection",
                file=os.path.join(BASE_DIR, *("assets", "send.png")),
                height=32,
                width=32
            ),
            tk.PhotoImage(
                name="environment",
                file=os.path.join(BASE_DIR, *("assets", "book.png")),
                height=32,
                width=32
            ),
            tk.PhotoImage(
                name="history",
                file=os.path.join(BASE_DIR, *('assets', 'history.png')),
                height=32,
                width=32
            )
        ]
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
        if self.sidebar != 'environment':
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
        if 'Regex' in self.tag_list:
            self.notebook.select(self.tag_list.index('Regex'))
        else:
            self.notebook.add(RegexWindow(self.notebook).root, text='Regex')
            self.notebook.select(self.notebook.index(tk.END) - 1)
            self.tag_list.append('Regex')

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

    def open_handler(self):
        """Open file"""
        filepath = filedialog.askopenfilename()
        if filepath:
            with open(filepath, "r", encoding="utf-8") as file:
                data = file.read()
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    messagebox.showerror("Error", "The text content must be a json")
                    return

                self.new_request(data)

    def new_request(self, data=None, **kwargs):
        if kwargs.get("item_id") in self.tag_list:
            self.notebook.select(self.tag_list.index(kwargs["item_id"]))
            return

        tl = ttk.Frame(self.notebook)
        req_win = RequestWindow(
            window=tl, callback=self.request, get_script=self.col_win.get_script
        )
        req_win.item_id = kwargs.get("item_id")
        if data is not None:
            req_win.fill_blank(data)

        self.notebook.add(tl, text="Request")
        self.notebook.select(self.notebook.index(tk.END) - 1)
        self.tag_list.append(kwargs.get("item_id", ""))

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
        thread = threading.Thread(target=self.env_win.on_start)
        thread.start()
        filepath = os.path.join(WORK_DIR, "history.json")
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
        thread = threading.Thread(target=self.env_win.on_end)
        thread.start()
        self.col_win.on_close()
        with open(
            os.path.join(WORK_DIR, "history.json"), "w", encoding="utf-8"
        ) as file:
            file.write(json.dumps(self.history_list))
        self.root.destroy()

    def collection(self, **kwargs):
        if kwargs["tag"] in ["project", "folder"]:
            if kwargs["item_id"] in self.tag_list:
                self.notebook.select(self.tag_list.index(kwargs["item_id"]))
                return

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
            self.history_list.append(kwargs.get("data"))
        elif action == "history":
            # Writes to the history list
            self.history_window.log(kwargs.get("data"))
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

    def history(self, action, **kwargs):
        """History callback"""
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
        self.tag_list.pop(self.notebook.index(self.notebook.select()))
        self.notebook.forget(self.notebook.select())
