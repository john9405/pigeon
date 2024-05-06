from tkinter import ttk, messagebox
import tkinter as tk
import datetime
import re


class TimestampWindow:
    """时间戳转换工具"""

    def __init__(self, master=None):
        self.root = ttk.Frame(master)
        # 时间戳转日期时间
        intframe = ttk.Frame(self.root)
        intframe.pack(fill=tk.X)
        ttk.Label(intframe, text="Timestamp:").pack(side=tk.LEFT)
        self.timestamp_entry = ttk.Entry(intframe)
        self.timestamp_entry.pack(side=tk.LEFT)
        ttk.Button(intframe, text="transform", command=self.timestamp_to_datetime).pack(
            side=tk.LEFT
        )
        ttk.Label(intframe, text="Datetime:").pack(side=tk.LEFT)
        self.datetime_entry = ttk.Entry(intframe)
        self.datetime_entry.pack(side=tk.LEFT)

        # 日期时间转时间戳
        strframe = ttk.Frame(self.root)
        strframe.pack(fill=tk.X)
        ttk.Label(strframe, text="DateTime:").pack(side=tk.LEFT)
        self.date_entry = ttk.Entry(strframe)
        self.date_entry.pack(side=tk.LEFT)
        ttk.Button(strframe, text="transform", command=self.datetime_to_timestamp).pack(
            side=tk.LEFT
        )
        ttk.Label(strframe, text="Timestamp:").pack(side=tk.LEFT)
        self.time_entry = ttk.Entry(strframe)
        self.time_entry.pack(side=tk.LEFT)
        ttk.Label(self.root, text="(YYYY-MM-DD HH:MM:SS)").pack()

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
