# Waybar Custom Modules

This repo contains the waybar custom modules I use on my system. Each module is
implemented as a subcommand of the `waybar-custom-modules` script provided by
this Python package.

All modules expect that waybar is using the `FontAwesome 6 Free` font package
for icons.

## Installation

Run `pipx install --editable .`

## Usage

Just add `waybar-custom-modules MODULENAME` as the `exec` option in a waybar
custom module after installing.

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
