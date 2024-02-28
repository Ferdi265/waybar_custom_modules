from gi.repository import GLib
from pydbus import SystemBus
import json

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

def on_property_changed(interface, changes, args):
    if 'ActiveProfile' in changes:
        report(changes['ActiveProfile'])

def main():
    loop = GLib.MainLoop()

    bus = SystemBus()
    ppd = bus.get("org.freedesktop.UPower.PowerProfiles", "/org/freedesktop/UPower/PowerProfiles")
    ppd.PropertiesChanged.connect(on_property_changed)

    report(ppd.ActiveProfile)
    loop.run()
