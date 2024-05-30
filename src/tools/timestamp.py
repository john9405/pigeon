from tkinter import ttk, messagebox
import tkinter as tk
import datetime
import re


class TimestampWindow:
    """时间戳转换工具"""

    def __init__(self, master=None):
        self.root = ttk.Frame(master)
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
