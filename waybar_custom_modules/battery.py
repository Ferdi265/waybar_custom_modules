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
class ChargingState:
    plugged_in: bool
    charging: bool
    discharging: bool
    full: bool

def time_to_hrs_min_sec(t_sec: int) -> tuple[int, int, int]:
    t_min, t_sec = t_sec // 60, t_sec % 60
    t_hrs, t_min = t_min // 60, t_min % 60
    return t_hrs, t_min, t_sec

def format_time(t_sec: int) -> str:
    t_hrs, t_min, t_sec = time_to_hrs_min_sec(t_sec)
    return f"{t_hrs} h {t_min} min"

@dataclass
class State:
    bus: SystemBus
    upower: object

    batteries: dict[str, object] = field(default_factory=dict)

    main_battery: object | None = None
    main_battery_path: str | None = None

    main_adapter: object | None = None
    main_adapter_path: str | None = None

    def check_battery_percentage(self) -> tuple[int, str]:
        """
        returns battery percentage and battery percentage state class
        """

        # check battery percentage
        percentage = 0
        if self.main_battery is not None:
            percentage = int(self.main_battery.Percentage)
            if Config.BATTERY_FULL_AT < 100:
                percentage = int(round(percentage * 100 / Config.BATTERY_FULL_AT))

            percentage = min(percentage, 100)

        # check percentage class
        percentage_class = ""
        for state_class, threshold in sorted(Config.STATES.items(), key=lambda t: t[1]):
            if percentage <= threshold:
                percentage_class = state_class
                break

        return percentage, percentage_class

    def check_charge_state(self, percentage: int) -> ChargingState:
        """
        returns plugged_in, charging, discharging, and full state
        """

        # check adapter state
        plugged_in = False
        if self.main_adapter is not None:
            plugged_in = self.main_adapter.Online

        # check charge state
        charging = False
        discharging = False
        if self.main_battery is not None:
            charging = self.main_battery.State in [BatteryState.CHARGING, BatteryState.PENDING_CHARGE]
            discharging = self.main_battery.State in [BatteryState.DISCHARGING, BatteryState.PENDING_DISCHARGE]

        # check full state
        full = False
        if self.main_battery is not None:
            full = self.main_battery.State in [BatteryState.FULLY_CHARGED]
            if percentage == 100 and plugged_in:
                full = True

            # ensure full and charging/discharging are mutually exclusive
            if full:
                charging = False
                discharging = False

        return ChargingState(plugged_in, charging, discharging, full)

    def check_charge_time(self) -> tuple[int, int]:
        """
        returns time_to_full and time_to_empty
        """

        # check time to full and time to empty
        time_to_full = 0
        time_to_empty = 0
        if self.main_battery is not None:
            time_to_full = self.main_battery.TimeToFull
            time_to_empty = self.main_battery.TimeToEmpty

        return time_to_full, time_to_empty

    def generate_charge_state_icon(self, state: ChargingState) -> tuple[str, str]:
        """
        returns charging state icon and and charging state css class
        """

        # check state class
        charge_icon = ""
        charge_class = ""
        if state.full and state.plugged_in:
            charge_class = "plugged"
            charge_icon = Config.ALT_ICON_PLUGGED
        elif state.charging:
            charge_class = "charging"
            charge_icon = Config.ALT_ICON_CHARGING
        elif state.plugged_in:
            charge_class = "plugged"
            charge_icon = Config.ALT_ICON_PLUGGED

        return charge_icon, charge_class

    def generate_text(self, percentage: int) -> str:
        """
        returns main charging indicator text
        """

        text = "?"
        if self.main_battery is not None:
            text = f"{int(percentage)}%"

        return text

    def generate_tooltip(self, state: ChargingState, time_to_full: int, time_to_empty: int) -> str:
        """
        returns charging indicator tooltip
        """

        # generate tooltip
        tooltip = ""
        if state.full:
            tooltip = "Full"
        elif time_to_full != 0:
            tooltip = f"Time to full: {format_time(time_to_full)}"
        elif time_to_empty != 0:
            tooltip = f"Time to empty: {format_time(time_to_empty)}"
        elif state.charging:
            tooltip = "Charging..."
        elif state.discharging and state.plugged_in:
            tooltip = "Discharging while plugged..."
        elif state.discharging:
            tooltip = "Discharging..."
        elif state.plugged_in:
            tooltip = "Plugged"
        else:
            tooltip = "Unknown"

        return tooltip

    def report(self):
        state_classes = []

        percentage, percentage_class = self.check_battery_percentage()
        if percentage_class != "":
            state_classes.append(percentage_class)

        state = self.check_charge_state(percentage)
        time_to_full, time_to_empty = self.check_charge_time()

        charge_icon, charge_class = self.generate_charge_state_icon(state)
        if charge_class != "":
            state_classes.append(charge_class)

        text = self.generate_text(percentage)
        tooltip = self.generate_tooltip(state, time_to_full, time_to_empty)

        print(json.dumps({
            "text": text,
            "alt": charge_icon,
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
                'Percentage' in changes or
                'TimeToFull' in changes or
                'TimeToEmpty' in changes
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
