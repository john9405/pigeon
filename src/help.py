from tkinter import ttk
from tkinter.scrolledtext import ScrolledText


class HelpWindow:
    """帮助窗口"""

    def __init__(self, master=None):
        root = ttk.Frame(master)
        self.root = root
        label = ScrolledText(root)
        label.insert('1.0', """
Print logs can be used
```
console.log()
console.error()
console.info()
console.warning()
```
The Request created by clicking "New Request" will be saved to the currently selected folder.
Where there is a "Save" button, click the Save button, otherwise the program will not save the data.
""")
        label.configure(state='disabled')
        label.pack(fill='both', expand=True)
