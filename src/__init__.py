import os

USER_DIR = os.path.expanduser("~")
WORK_DIR = os.path.join(USER_DIR, "Postman")
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

if not os.path.exists(WORK_DIR):
    os.mkdir(WORK_DIR)
