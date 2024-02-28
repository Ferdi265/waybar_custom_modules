from subprocess import check_output
import os.path
import time
import json
import sys

def report_empty():
    print(json.dumps({
        "text": "",
        "percentage": 0,
    }), flush=True)

def report_updated(uname: str):
    print(json.dumps({
        "text": "",
        "tooltip": uname,
        "percentage": 100
    }), flush=True)

def main():
    uname = check_output(["uname", "-r"]).decode()[:-1]

    while True:
        if os.path.exists(f"/usr/lib/modules/{uname}/vmlinuz"):
            report_empty()
        else:
            report_updated(uname)

        time.sleep(5)
