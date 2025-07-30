# Waybar Custom Modules

This repo contains the waybar custom modules I use on my system. Each module is
implemented as a subcommand of the `waybar-custom-modules` script provided by
this Python package.

All modules expect that waybar is using the
[FontAwesome](https://fontawesome.com/) font package for icons.

## Installation

Run `pipx install --editable .`

## Usage

Just add `waybar-custom-modules MODULENAME` as the `exec` option in a waybar
custom module after installing.

These modules use the [FontAwesome](https://fontawesome.com/) symbol font for
icons, so you might need to add the following or something similar to your
waybar `style.css`:

```css
/* .config/waybar/style.css */
* {
    font-family: DejaVu Sans, 'FontAwesome 7 Free', sans-serif;
}
```

The following is a list of modules in this package:

## Module `linux`

Checks if the running kernel is still the installed kernel version, to remind
me to reboot my machine if I face weird issues with kernel modules. This is
also mitigated by my
[linux-preserve-modules](https://aur.archlinux.org/packages/linux-preserve-modules)
AUR package, but it doesn't hurt to have an additional reminder.

```js
// .config/waybar/config
{
    "custom/linux": {
        "exec": "waybar-custom-modules linux",
        "format": "{icon}",
        "format-icons": ["", "\uf17c \uf021"],
        "return-type": "json"
    }
}
```

```css
/* .config/waybar/style.css */
#custom-linux {
    background-color: #c59900;
    color: #002b36;
}
```

## Module `powerprofile`

Checks the current power profile of the system using the
`org.freedesktop.UPower.PowerProfiles` DBus service.

```js
// .config/waybar/config
{
    "custom/powerprofile": {
        "exec": "waybar-custom-modules powerprofile",
        "format": "{icon}",
        "format-icons": ["", "\f059", "\uf624", "\uf625"],
        "return-type": "json"
    }
}
```

```css
/* .config/waybar/style.css */
#custom-powerprofile {
    background-color: #c59900;
    color: #002b36;
}

#custom-powerprofile.performance {
    background-color: #cb4b16;
}
```

## Module `battery`

Checks the current battery level of the system's internal battery using the
`org.freedesktop.UPower` DBus service. This is an alternative to Waybar's
built-in battery module that reacts faster to changes in battery level or
charge state.

```js
// .config/waybar/config
{
    "custom/battery": {
        "exec": "waybar-custom-modules battery",
        "format": "{text} {icon}{alt}",
        "format-icons": ["\uf244", "\uf243", "\uf242", "\uf241", "\uf240"],
        "return-type": "json"
    }
}
```

```css
/* .config/waybar/style.css */
#custom-battery {
    background-color: #fdf6e3;
    color: #002b36;
}

#custom-battery.plugged {
    background-color: #268bd2;
}

#custom-battery.full {
    background-color: #268bd2;
}

#custom-battery.almost-full {
    background-color: #268bd2;
}

#custom-battery.high {
    background-color: #859900;
}

#custom-battery.medium {
    background-color: #c59900;
}

#custom-battery.low {
    background-color: #cb4b16;
}
```
