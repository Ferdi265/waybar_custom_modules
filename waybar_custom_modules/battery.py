from dataclasses import dataclass, field
from enum import Enum
from gi.repository import GLib
from pydbus import SystemBus
import json

class Config:
    BATTERY_FULL_AT = 80
    ALT_ICON_CHARGING = " \uf0e7"
    ALT_ICON_PLUGGED = " \uf1e6"
    STATES = {
        "almost-full": 100,
        "high": 89,
        "medium": 49,
        "low": 10
    }

class DeviceType:
    UNKNOWN = 0
    LINE_POWER = 1
    BATTERY = 2

class BatteryState:
    UNKNOWN = 0
    CHARGING = 1
    DISCHARGING = 2
    EMPTY = 3
    FULLY_CHARGED = 4
    PENDING_CHARGE = 5
    PENDING_DISCHARGE = 6

@dataclass
class State:
    bus: SystemBus
    upower: object

    batteries: dict[str, object] = field(default_factory=dict)

    main_battery: object | None = None
    main_battery_path: str | None = None

    main_adapter: object | None = None
    main_adapter_path: str | None = None

    def report(self):
        state_classes = []

        # check adapter state
        plugged_in = False
        if self.main_adapter is not None:
            plugged_in = self.main_adapter.Online

        # check battery percentage
        percentage = 0
        if self.main_battery is not None:
            percentage = int(self.main_battery.Percentage)
            if Config.BATTERY_FULL_AT < 100:
                percentage = percentage * 100 // Config.BATTERY_FULL_AT

            percentage = min(percentage, 100)

            # check percentage class
            for state_class, threshold in sorted(Config.STATES.items(), key=lambda t: t[1]):
                if percentage <= threshold:
                    state_classes.append(state_class)
                    break

        # check charge state
        charging = False
        if self.main_battery is not None:
            charging = self.main_battery.State in [BatteryState.CHARGING, BatteryState.PENDING_CHARGE]

        # check full state
        full = False
        if self.main_battery is not None:
            full = self.main_battery.State in [BatteryState.FULLY_CHARGED]
            if percentage == 100 and plugged_in:
                full = True

        # check state class
        alt_icon = ""
        if full and plugged_in:
            state_classes.append("plugged")
            alt_icon = Config.ALT_ICON_PLUGGED
        elif charging:
            state_classes.append("charging")
            alt_icon = Config.ALT_ICON_CHARGING
        elif plugged_in:
            state_classes.append("plugged")
            alt_icon = Config.ALT_ICON_PLUGGED

        # generate text
        text = "?"
        if self.main_battery is not None:
            text = f"{int(percentage)}%"

        # generate tooltip
        tooltip = ""
        # TODO: TimeToFull, TimeToEmpty
        # TODO: additional batteries

        print(json.dumps({
            "text": text,
            "alt": alt_icon,
            "tooltip": tooltip,
            "class": state_classes,
            "percentage": percentage,
        }), flush=True)

    def on_device_property_changed(self, device_path, interface, changes, args):
        if (
            # adapter change
            device_path == self.main_adapter_path and (
                'Online' in changes
            ) or
            # battery change
            device_path in self.batteries and (
                'State' in changes or
                'Percentage' in changes
            )
        ):
            self.report()

    def on_device_added(self, device_path: str):
        device = self.bus.get("org.freedesktop.UPower", device_path)

        # match on all batteries or battery-like devices
        if device.Type == DeviceType.BATTERY or (device.Energy != 0.0 and device.EnergyFull != 0.0):
            self.batteries[device_path] = device

            if device.PowerSupply and self.main_battery_path is None:
                self.main_battery_path = device_path
                self.main_battery = device

            device.PropertiesChanged.connect(lambda interface, changes, args: self.on_device_property_changed(device_path, interface, changes, args))
            self.report()
        elif device.Type == DeviceType.LINE_POWER and device.PowerSupply and self.main_adapter_path is None:
            self.main_adapter = device
            self.main_adapter_path = device_path

            device.PropertiesChanged.connect(lambda interface, changes, args: self.on_device_property_changed(device_path, interface, changes, args))

        self.report()

    def on_device_removed(self, device_path: str):
        if device_path in self.batteries:
            del self.batteries[device_path]

        if device_path == self.main_battery_path:
            self.main_battery_path = None
            self.main_battery = None

            # find backup main battery
            for device in self.batteries:
                if device.PowerSupply:
                    self.main_battery_path = device_path
                    self.main_battery = device
                    break

        if device_path == self.main_adapter_path:
            self.main_adapter_path = None
            self.main_adapter = None

        self.report()

def main():
    loop = GLib.MainLoop()

    bus = SystemBus()
    upower = bus.get("org.freedesktop.UPower", "/org/freedesktop/UPower")
    state = State(bus, upower)

    upower.DeviceAdded.connect(state.on_device_added)
    upower.DeviceRemoved.connect(state.on_device_removed)

    for device in upower.EnumerateDevices():
        state.on_device_added(device)

    state.report()
    loop.run()
