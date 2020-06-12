#!/usr/bin/env python3
"""
###
# A collection of handy utilities and snippets
#   for creating interactive programs.
##
# TODO:
# + add 'check_dependencies' function & check all over
#       the WD for possible implementations and integrations
#
"""

from re import match
from subprocess import call, check_output, DEVNULL, CalledProcessError
from os import listdir
from pathlib import Path
from typing import Optional

from termcolor import colored, cprint


def clear() -> None:
    print(chr(27) + "[2J")


PRL_WARN = ('yellow', '!')
PRL_SU = ('yellow', '#')
PRL_ERR = ('red', 'X')
PRL_CHOICE = ('cyan', '?')
PRL_HEAD = ('cyan', '')
PRL_VERB = ('blue', '~')


def prl(text: str, lvl: iter = ('green', '+'), attrib: list = ()) -> None:
    text = str(text)
    if lvl == PRL_HEAD:
        a = list(attrib)
        if attrib:
            a.insert(0, 'bold')
        cprint(text, lvl[0], attrs=a)
    else:
        print(colored('[%s] ' % lvl[1], lvl[0], attrs=attrib) + text)


def pr(text: str, notation: str = '+', end='\n') -> None:
    col = {
        '+': 'green',
        '*': 'cyan',
        '~': 'cyan',
        'X': 'red',
        '!': 'yellow',
        '?': 'blue'
    }[notation]
    print(f"{colored(f'[{notation}]' , col)} {text}", end=end)


def choose(options: iter = ('Yes', 'No'), prompt: str = 'Choose action:', default: int = 0) -> int:
    if not options:
        raise ValueError(
            " [!] No options passed to choice() !!!")  # No options
    pr(prompt, '?')
    for index, option in enumerate(options):
        line = '\t'
        if index == default:
            line += '[%d]. ' % (index + 1)
        else:
            line += ' %d.  ' % (index + 1)
        line += option
        cprint(line, 'yellow')
    try:
        ans = input(colored('[>>>] ', 'yellow'))
        if not ans:
            return default
        ans = int(ans)
        assert 0 < ans <= len(options)
        return ans - 1
    except KeyboardInterrupt:
        return -2  # Keyboard Interrupt
    except AssertionError:
        return -1  # Bad Number
    except ValueError:
        return -1  # Probably text received


def ask(question: str) -> (None, str):
    """
    Ask the user something
    :param question:
    :return: the response, None if no response
    ** Expect a KeyboardInterrupt!!
    """
    pr(question, '?')
    answer = input('>')
    if answer == '':
        return None
    try:
        answer = int(answer)
    except ValueError:
        pass
    return answer


def pause(reason: str = 'continue', cancel: bool = False):
    s = 'Press %s to %s' % (colored('[ENTER]', 'cyan'), reason)
    if cancel:
        s += ', %s to cancel' % colored('[^C]', 'red')
    pr(s, '?')

    try:
        input()
        return True
    except KeyboardInterrupt:
        return False


def cyan(text: str) -> str:
    return colored(text, 'cyan')


def banner(txt: str, style: str = 'slant') -> str:
    """
    Depends on: "pyfiglet"
    :param txt: The text to return as an ASCII art
    :param style: The style (From: /usr/lib/python3.6/site-packages/pyfiglet/fonts/)
    :return: The created ASCII art
    """
    try:
        from pyfiglet import Figlet
    except ImportError:
        pr('Module "pyfiglet" not installed, rendering legacy banner', '!')
        return '~=~=~ %s ~=~=~' % txt
    f = Figlet(font=style)
    return f.renderText(text=txt)


def choose_file(root_dir: Path) -> Optional[Path]:
    def _format(root_dir: Path, entry: str) -> str:
        f = root_dir / entry
        if f.is_dir():
            return entry
        return f'{entry}\t({human_bytes(f.stat().st_size)}, {count_lines(f)})'
    listing = listdir(root_dir)
    if not listing:
        return pr('Empty directory!', '!')
    while 1:
        c = choose([_format(root_dir, i) for i in listing], default=-1)
        if c < 0:
            return
        f = root_dir / listing[c]
        if f.is_dir():
            f = choose_file(root_dir / f)
            if not f:
                continue
        return f


def generic_menu_loop(directory: str, menu: dict) -> None:
    while 1:
        inp = input(colored(f'.{directory}->', 'red', attrs=['bold']))
        if not inp:
            break
        if 'help' in inp:
            for c in menu:
                v = menu[c]
                desc = v[1] if type(
                    v[1]) is str else f'Enter {v[0].capitalize()} menu'
                print(f'  {cyan(c)} -> {colored(desc, "yellow")}')
            continue

        pts = inp.split(' ')
        if pts[0] not in menu:
            pr('No such command! try "help".', '!')
            continue

        command = menu.get(pts[0])
        func = command[0]
        if callable(func):
            func(tuple([i for i in pts[1:] if i]))
        else:
            generic_menu_loop(f'{directory}.{func}', command[1])
        print()


def get_date() -> str:
    """
    :return: today's date (e.g. "28.11.2017" ;P)
    """
    from datetime import datetime
    return datetime.now().strftime("%d.%m.%Y")


def count_lines(file_path: Path) -> int:
    # TODO Crossplatformize
    return int(check_output(('/usr/bin/wc', '-l', str(file_path.resolve()))).decode().split(' ')[0])


def human_bytes(size_in_bytes: int) -> str:
    unit = 0
    while size_in_bytes >= 1024:
        unit += 1
        size_in_bytes /= 1024
    return str(round(size_in_bytes)) + ('', 'KB', 'MB', 'GB', 'TB')[unit]


def file_volume(path: Path) -> tuple:
    sb = path.stat().st_size
    lc = count_lines(path)
    return sb, lc, f'{cyan(path.name)} ({human_bytes(sb)}, {lc})'


def is_image(image_path: str) -> (str, None):
    """
    Checks the file signature (magic number)
            for an image

    :param image_path: The path to the image
    :return: True if the image is PNG or JPG
    """

    signatures = {'JPG': 'ffd8ff',
                  'PNG': '89504e',
                  'GIF': '474946'}

    with open(image_path, 'rb') as img_file:
        signature = img_file.read(3).hex()
        for sig in signatures:
            if signature == signatures[sig]:
                return sig
    return None


def is_package(package_name) -> (str, None):
    """
    Check if a system package is installed

    :param package_name: Package to check
    :return: The version of the installed package or None if no such package
    """
    try:
        return check_output(['/usr/bin/pacman', '-Q', package_name], stderr=DEVNULL).decode().strip().split(' ')[1]
    except CalledProcessError:
        return False
    except FileNotFoundError:
        try:
            return check_output(('apt', 'list', '-qq', package_name)).decode().split(' ')[1]
        except CalledProcessError:
            pass
    return None


def is_mac(mac: str) -> bool:
    """
    Check if the specified string is a mac address
    Bytes delimiter can be either '-' or ':'
    The MAC string is stripped.
    :param mac: The MAC address string
    :return: True if the MAC address is valid
    """
    return bool(match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.strip().lower()))


def get_net() -> (None, dict):
    # Uses iproute2 (ip)

    # Example raw:
    # default via 192.168.1.1 dev eth0
    # 192.168.1.0/24 dev eth0 proto kernel scope link src 192.168.1.28

    raw = check_output(['ip', 'route']).decode().strip().split('\n')
    d = {}
    if not raw or 'default' not in raw[0]:
        return None  # No route
    else:
        # default: (gateway, interface)
        d.update({'default': raw[0].split(' ')[2:5:2]})

    for li in raw[1:]:
        ls = li.split(' ')
        d.update({ls[2]: {'interface': ls[2], 'subnet': ls[0], 'ip': ls[8]}})

    return d


def ping(ip: str, count: int = 1, timeout: int = 1) -> bool:
    """
    Depends on: "iputils"
    A binding for system call ping
    :param ip: Destination
    :param count: How much ping requests to send
    :param timeout: How long wait for a reply
    :return: A boolean that represents success of the ping
    """
    if count < 1:
        raise ValueError('Count cannot be lower than 1')
    try:
        return call(['ping', '-c', str(count), '-w', str(timeout), ip], stdout=DEVNULL, stderr=DEVNULL) == 0
    except CalledProcessError:
        pass
    except KeyboardInterrupt:
        pr('[utils] Ping interrupted!', '!')
    return False
