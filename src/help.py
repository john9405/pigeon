from tkinter.scrolledtext import ScrolledText


class HelpWindow:
    """帮助窗口"""

    def __init__(self, master=None):
        label = ScrolledText(master)
        label.insert('1.0', """
Print logs can be used
```
console.log("content")
console.error("content")
console.info("content")
console.warning("content")
```

Get environment variables
```
globals("name")             ::Variables of Globals in Var
environment("name")         ::Variables in Active state in Var
collectionVariables("name") ::Variables in the collection
```

Pre-request Script 
```
Retrieve request data
req["body"]    ::dict  'Request Body'
req["headers"] ::dict  'Request header'
req["params"]  ::dict  'Request query'

Example of Assignment Usage: req['body']['username'] = 'x'
```

Post-response Script
```
res ::<class 'requests.models.Response'>
```

Using the '{{name}}' structure in URLs, params, headers, and body can retrieve variables with corresponding names, 
whose values come from collections and Globals.
The Request created by clicking "New Request" will be saved to the currently selected folder.
Where there is a "Save" button, click the Save button, otherwise the program will not save the data.
""")
        label.configure(state='disabled')
        label.pack(fill='both', expand=True)
