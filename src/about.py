from tkinter.scrolledtext import ScrolledText


class AboutWindow:
    """关于窗口"""

    def __init__(self, master=None):
        label = ScrolledText(master)
        label.insert('1.0', """
Http Client
0.0.1
""")
        label.configure(state='disabled')
        label.pack(fill='both', expand=True)
