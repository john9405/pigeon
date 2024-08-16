from tkinter import ttk, messagebox
import tkinter as tk
import datetime
import re
import time
import threading


def update_now(var, var2):
    while True:
        try:
            var.delete(0, tk.END)
            var.insert(0, str(round(time.time())))
            var2.delete(0, tk.END)
            var2.insert(0, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            time.sleep(1)
        except RuntimeError:
            break


class TimestampWindow:
    """时间戳转换工具"""

    def __init__(self, master=None):
        self.root = ttk.Frame(master)
        self.root.pack(fill='both', expand=True, padx=5, pady=5)
        # 时间戳转日期时间
        ttk.Label(self.root, text="Timestamp:").grid(row=0, column=0)
        self.timestamp_entry = ttk.Entry(self.root)
        self.timestamp_entry.grid(row=0, column=1)
        ttk.Button(self.root, text="transform", command=self.timestamp_to_datetime).grid(row=0, column=2)
        ttk.Label(self.root, text="Datetime:").grid(row=0, column=3)
        self.datetime_entry = ttk.Entry(self.root)
        self.datetime_entry.grid(row=0, column=4)

        # 日期时间转时间戳
        ttk.Label(self.root, text="DateTime:").grid(row=1, column=0)
        self.date_entry = ttk.Entry(self.root)
        self.date_entry.grid(row=1, column=1)
        ttk.Button(self.root, text="transform", command=self.datetime_to_timestamp).grid(row=1, column=2)
        ttk.Label(self.root, text="Timestamp:").grid(row=1, column=3)
        self.time_entry = ttk.Entry(self.root)
        self.time_entry.grid(row=1, column=4)
        ttk.Label(self.root, text="(YYYY-MM-DD HH:MM:SS)").grid(row=2, column=0, columnspan=2)

        # 现在的时间
        ttk.Label(self.root, text="Now:").grid(row=3, column=0)
        now_var = ttk.Entry(self.root)
        now_var.grid(row=3, column=1)
        date_var = ttk.Entry(self.root)
        date_var.grid(row=4, column=1)
        thread = threading.Thread(target=update_now, args=(now_var, date_var, ))
        thread.start()

    def timestamp_to_datetime(self):
        timestamp = self.timestamp_entry.get()
        if re.search(r"^\d+$", timestamp) is None:
            messagebox.showinfo("Warning", "Invalid timestamp!")
            return

        timestamp = int(timestamp)
        try:
            dt = datetime.datetime.fromtimestamp(timestamp)
            self.datetime_entry.delete(0, tk.END)
            self.datetime_entry.insert(0, str(dt))
        except ValueError:
            messagebox.showinfo("Warning", "Invalid timestamp!")

    def datetime_to_timestamp(self):
        date_str = self.date_entry.get()
        if (
            re.search(r"^\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2}$", date_str)
            is None
        ):
            messagebox.showinfo("Warning", "Invalid datetime format!")
            return

        try:
            dt = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            timestamp = int(dt.timestamp())
            self.time_entry.delete(0, tk.END)
            self.time_entry.insert(0, str(timestamp))
        except ValueError:
            messagebox.showinfo("Warning", "Invalid datetime format!")
