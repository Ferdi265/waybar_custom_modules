import sys
from . import linux

def usage():
    print("usage: waybar-custom-modules <module>")
    print("")
    print("MODULES:")
    print("- linux: displays a warning if the kernel was updated")
    sys.exit(1)

def main():
    args = sys.argv[1:]

    if len(args) != 1:
        usage()

    name = args[0]
    if name == "linux":
        linux.main()
    else:
        usage()

if __name__ == "__main__":
    main()
