from tkinter import ttk
import datetime


class TimestampWindow:
    """ 时间戳转换工具 """
    def __init__(self, master=None):
        self.root = ttk.Frame(master)
        # 时间戳转日期时间
        timestamp_label = ttk.Label(self.root, text="Timestamp:")
        timestamp_label.pack()
        self.timestamp_entry = ttk.Entry(self.root)
        self.timestamp_entry.pack()
        timestamp_button = ttk.Button(self.root, text="Convert to Datetime", command=self.timestamp_to_datetime)
        timestamp_button.pack()
        self.datetime_label = ttk.Label(self.root, text="Datetime:")
        self.datetime_label.pack()

        # 日期时间转时间戳
        date_label = ttk.Label(self.root, text="Date (YYYY-MM-DD):")
        date_label.pack()
        self.date_entry = ttk.Entry(self.root)
        self.date_entry.pack()
        time_label = ttk.Label(self.root, text="Time (HH:MM:SS):")
        time_label.pack()
        self.time_entry = ttk.Entry(self.root)
        self.time_entry.pack()
        datetime_button = ttk.Button(self.root, text="Convert to Timestamp", command=self.datetime_to_timestamp)
        datetime_button.pack()
        self.timestamp_label = ttk.Label(self.root, text="Timestamp:")
        self.timestamp_label.pack()

    def timestamp_to_datetime(self):
        timestamp = int(self.timestamp_entry.get())
        try:
            if len(str(timestamp)) == 10:
                dt = datetime.datetime.fromtimestamp(timestamp)
                self.datetime_label.config(text="Datetime: " + str(dt))
            elif len(str(timestamp)) == 13:
                dt = datetime.datetime.fromtimestamp(timestamp / 1000)
                self.datetime_label.config(text="Datetime: " + str(dt))
            else:
                self.datetime_label.config(text="Invalid timestamp length!")
        except ValueError:
            self.datetime_label.config(text="Invalid timestamp!")

    def datetime_to_timestamp(self):
        date_str = self.date_entry.get()
        time_str = self.time_entry.get()
        try:
            dt = datetime.datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M:%S")
            timestamp = int(dt.timestamp())
            self.timestamp_label.config(text="Timestamp: " + str(timestamp))
        except ValueError:
            self.timestamp_label.config(text="Invalid datetime format!")