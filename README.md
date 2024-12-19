# API TEST

A simple api testing tool

Develop on Windows 10(Python 3.8)  

How to run the program
```
pip install -r requirements.txt
python __main__.py
```

Package into an application
```
pip install pyinstaller
pip install cryptojwt  # JWE
pyinstaller __main__.py -n ApiTest -w -y --hidden-import cryptojwt --clean --onefile
```

bug：
1.文件夹剪切时会导致子文件夹和请求丢失
