from subprocess import check_output
import os.path
import time
import json

def report_empty():
    print(json.dumps({
        "text": "",
        "percentage": 0,
    }), flush=True)

def report_updated(uname: str, has_modules: bool):
    print(json.dumps({
        "text": "",
        "tooltip": uname,
        "percentage": 100 if has_modules else 50,
    }), flush=True)

def get_updated_tooltip(uname: str, has_modules: bool) -> str:
    linux_version = check_output(["pacman", "-Q", "linux"]).decode()[:-1]
    linux_version_parts = linux_version.split(" ")
    if not has_modules:
        uname += " (!)"
    if len(linux_version_parts) != 2:
        return f"{uname} -> ???"
    else:
        new_uname = linux_version_parts[1]
        return f"{uname} -> {new_uname}"

def main():
    uname = check_output(["uname", "-r"]).decode()[:-1]

    while True:
        if os.path.exists(f"/usr/lib/modules/{uname}/vmlinuz"):
            report_empty()
        else:
            has_modules = os.path.exists(f"/usr/lib/modules/{uname}/kernel/arch")
            report_updated(get_updated_tooltip(uname, has_modules), has_modules)

        time.sleep(5)
