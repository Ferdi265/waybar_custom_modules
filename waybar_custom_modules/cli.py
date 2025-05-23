import sys
from . import linux
from . import powerprofile
from . import battery

def usage():
    print("usage: waybar-custom-modules <module>")
    print("")
    print("MODULES:")
    print("- linux: displays a warning if the kernel was updated")
    print("- powerprofile: displays the current power profile")
    print("- battery: displays the current battery state")
    sys.exit(1)

def main():
    args = sys.argv[1:]

    if len(args) != 1:
        usage()

    name = args[0]
    match args[0]:
        case "linux":
            linux.main()
        case "powerprofile":
            powerprofile.main()
        case "battery":
            battery.main()
        case _:
            usage()

if __name__ == "__main__":
    main()
