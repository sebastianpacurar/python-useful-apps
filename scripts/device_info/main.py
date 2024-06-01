import platform

from device_info.platforms.available_platforms import AvailablePlatforms
from device_info.platforms.darwin import Darwin
from device_info.platforms.linux import Linux
from device_info.platforms.windows import Windows

if __name__ == '__main__':
    match platform.system():
        case AvailablePlatforms.WINDOWS.value:
            p = Windows()
        case AvailablePlatforms.DARWIN.value:
            p = Darwin()
        case AvailablePlatforms.LINUX.value:
            p = Linux()
        case _:
            raise RuntimeError("Unsupported platform")

    p.print_platform_info()