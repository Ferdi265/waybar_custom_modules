from subprocess import check_output
import os.path
import time
import json
import sys

def report_profile(profile: str, percentage: int):
    print(json.dumps({
        "text": "",
        "tooltip": profile,
        "class": profile,
        "percentage": percentage,
    }), flush=True)

def report(profile: str):
    match profile:
        case "power-saver":
            report_profile(profile, 0)
        case "balanced":
            report_profile(profile, 60)
        case "performance":
            report_profile(profile, 100)
        case _:
            report_profile(profile, 40)


def main():
    while True:
        profile = check_output(["powerprofilesctl", "get"]).decode()[:-1]
        report(profile)

        time.sleep(5)
