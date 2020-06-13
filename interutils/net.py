
from re import match
from subprocess import call, check_output, DEVNULL, CalledProcessError

from .interactive import pr


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
