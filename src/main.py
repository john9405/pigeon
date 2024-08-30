import threading
import tkinter as tk
import uuid
from tkinter import ttk

from .his import HistoryWindow
from .req import RequestWindow
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
from .tools.RSA import RSAKeyFrame, RsaPublicKey, RSACheck, RSAEncrypt, RSADecrypt


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

        state_bar = ttk.Frame(self.root)
        state_bar.pack(side=tk.BOTTOM, fill=tk.X)
        panel_window = ttk.PanedWindow(self.root, orient="horizontal")
        side_bar = ttk.Frame(panel_window)
        nba = ttk.Notebook(side_bar)
        col_top = ttk.Frame(nba)
        self.col_win = CollectionWindow(col_top, **{"callback": self.collection})
        nba.add(col_top, text='Collection')
        self.env_win = EnvironmentWindow(master=nba, callback=self.environment)
        nba.add(self.env_win.root, text='Variable')
        history_top = ttk.Frame(nba)
        self.history_window = HistoryWindow(history_top, self.history)
        nba.add(history_top, text='History')
        nba.pack(fill='both', expand=True)
        panel_window.add(side_bar, weight=1)
        main_frame = ttk.Frame(panel_window)
        nbb = ttk.Notebook(main_frame)
        nbb.pack(fill='both', expand=True)
        self.nbb = nbb
        panel_window.add(main_frame, weight=10)
        panel_window.pack(fill='both', expand=True)

        menu = tk.Menu(self.root)
        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label="New request", command=self.new_request)
        file_menu.add_command(label="New collection", command=self.col_win.new_proj)
        file_menu.add_command(label="Import", command=self.col_win.open_proj)
        file_menu.add_command(label="Export", command=self.col_win.export_proj)
        file_menu.add_command(label="Exit", command=self.on_closing)
        menu.add_cascade(label="File", menu=file_menu)
        tool_menu = tk.Menu(menu, tearoff=False)
        tool_menu.add_command(label="AES", command=lambda: self.new_tab(AesGui, "AES"))
        tool_menu.add_command(label="Base64", command=lambda: self.new_tab(Base64GUI, "Base64"))
        tool_menu.add_command(label="MD5", command=lambda: self.new_tab(MD5GUI, "MD5"))
        tool_menu.add_command(label="Password", command=lambda: self.new_tab(GenPwdWindow, "Password"))
        tool_menu.add_command(label="Timestamp", command=lambda: self.new_tab(TimestampWindow, "Timestamp"))
        tool_menu.add_command(label="Regex", command=lambda: self.new_tab(RegexWindow, "Regex"))
        tool_menu.add_command(label="RSA Key", command=lambda: self.new_tab(RSAKeyFrame, "RSA Key"))
        tool_menu.add_command(label="RSA Public Key", command=lambda: self.new_tab(RsaPublicKey, "RSA Public Key"))
        tool_menu.add_command(label="RSA Check", command=lambda: self.new_tab(RSACheck, "RSA Check"))
        tool_menu.add_command(label="RSA Encrypt", command=lambda: self.new_tab(RSAEncrypt, "RSA Encrypt"))
        tool_menu.add_command(label="RSA Decrypt", command=lambda: self.new_tab(RSADecrypt, "RSA Decrypt"))
        menu.add_cascade(label="Tools", menu=tool_menu)
        help_menu = tk.Menu(menu, tearoff=False)
        help_menu.add_command(label="Help", command=lambda: self.new_tab(HelpWindow, "Help"))
        help_menu.add_command(label="About", command=lambda: self.new_tab(AboutWindow, "About"))
        menu.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menu)

        ttk.Sizegrip(state_bar).pack(side="right", anchor="se")
        ttk.Button(state_bar, text="-", width=3, command=self.close_tab).pack(side="right")
        ttk.Button(state_bar, text="+", width=3, command=self.new_request).pack(side="right")
        ttk.Button(state_bar, text=">", width=3, command=self.next_tab).pack(side="right")
        ttk.Button(state_bar, text="<", width=3, command=self.previous_tab).pack(side="right")

    def new_request(self, data=None, **kwargs):
        tl = ttk.Frame(self.nbb)
        req_win = RequestWindow(
            window=tl,
            get_script=self.col_win.get_script,
            env_variable=self.env_win.get_variable,
            glb_variable=self.env_win.get_globals,
            local_variable=self.col_win.get_variable,
            cache_history=self.history_window.on_cache,
            save_item=self.col_win.save_item,
            path=kwargs.get('path', "Name:"),
            callback=self.request,
        )
        req_win.item_id = kwargs.get("item_id")
        name = "New Request"
        if data is not None:
            req_win.fill_blank(data)
            name = data.get("name", "New Request")
        self.nbb.add(tl, text=name)
        self.nbb.select(tl)
        if data is None:
            self.tag_list.append(str(uuid.uuid1()))  # new request

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

    def request(self, **kwargs):
        name = kwargs.get('name')
        if name is not None:
            self.nbb.tab(self.nbb.index("current"), text=name)
        item_id = kwargs.get('item_id')
        if item_id is not None:
            index = self.nbb.index("current")
            self.tag_list[index] = f"col_{kwargs['item_id']}"

    def collection(self, **kwargs):
        if f"col_{kwargs['item_id']}" in self.tag_list:
            self.nbb.select(self.tag_list.index(f"col_{kwargs['item_id']}"))
            return

        if kwargs["tag"] == "project":
            frame = ttk.Frame(self.nbb)
            ProjectWindow(
                master=frame,
                item_id=kwargs["item_id"],
                callback=self.col_win.save_item,
                data=kwargs["data"],
            )
            self.nbb.add(frame, text=kwargs["data"]['name'])
            self.nbb.select(frame)
        elif kwargs["tag"] == "folder":
            frame = ttk.Frame(self.nbb)
            FolderWindow(
                master=frame,
                item_id=kwargs["item_id"],
                callback=self.col_win.save_item,
                data=kwargs["data"],
                path=kwargs['path'],
            )
            self.nbb.add(frame, text=kwargs["data"]['name'])
            self.nbb.select(frame)
        else:
            self.new_request(kwargs["data"], item_id=kwargs["item_id"], path=kwargs['path'],)
        self.tag_list.append(f"col_{kwargs['item_id']}")

    def history(self, **kwargs):
        """History callback"""
        if kwargs['data']['uuid'] in self.tag_list:
            self.nbb.select(self.tag_list.index(kwargs['data']['uuid']))
            return
        self.new_request(kwargs.get("data"))
        self.tag_list.append(kwargs['data']['uuid'])

    def environment(self, **kwargs):
        if f'env_{kwargs.get("item_id")}' in self.tag_list:
            self.nbb.select(self.tag_list.index(f'env_{kwargs.get("item_id")}'))
            return
        frame = ttk.Frame(self.nbb)
        VariableWindow(
            frame,
            item_id=kwargs.get('item_id'),
            index=kwargs.get('index'),
            collection=kwargs.get("collection", ""),
            data=kwargs.get("data", {}),
            set_variable=self.env_win.set_variable,
            set_active=self.env_win.set_active,
        )
        self.tag_list.append(f'env_{kwargs.get("item_id")}')
        self.nbb.add(frame, text=kwargs.get("collection", "Var"))
        self.nbb.select(frame)

    def previous_tab(self):
        try:
            # 获取当前选中的选项卡的索引
            current_tab_index = self.nbb.index("current")
            # 计算上一个选项卡的索引
            previous_tab_index = (current_tab_index - 1) % self.nbb.index("end")
            # 选中上一个选项卡
            self.nbb.select(previous_tab_index)
        except tk.TclError:
            pass

    def next_tab(self):
        try:
            # 获取当前选中的选项卡的索引
            current_tab_index = self.nbb.index("current")
            # 计算下一个选项卡的索引
            next_tab_index = (current_tab_index + 1) % self.nbb.index("end")
            # 选中下一个选项卡
            self.nbb.select(next_tab_index)
        except tk.TclError:
            pass

    def new_tab(self, ui, text):
        if text in self.tag_list:
            self.nbb.select(self.tag_list.index(text))
            return
        frame = ttk.Frame(self.nbb)
        ui(master=frame)
        self.tag_list.append(text)
        self.nbb.add(frame, text=text)
        self.nbb.select(frame)

    def close_tab(self):
        index = self.nbb.index('current')
        self.tag_list.pop(index)
        self.nbb.forget(index)
