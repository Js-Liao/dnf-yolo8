import ctypes
import time

SendInput = ctypes.windll.user32.SendInput


# https://www.win.tue.nl/~aeb/linux/kbd/scancodes-10.html#keyboardid
class Keys:
    Q = 0x10
    W = 0x11
    E = 0x12
    R = 0x13
    T = 0x14
    Y = 0x15
    U = 0x16
    I = 0x17
    O = 0x18
    P = 0x19
    A = 0x1e
    S = 0x1f
    D = 0x20
    F = 0x21
    G = 0x22
    H = 0x23
    J = 0x24
    K = 0x25
    L = 0x26
    Z = 0x2c
    X = 0x2d
    C = 0x2e
    V = 0x2f
    B = 0x30
    N = 0x31
    M = 0x32
    ESC = 0x01
    SPACE = 0x39
    UP = 0xC8
    DOWN = 0xD0
    LEFT = 0xCB
    RIGHT = 0xCD
    RSHIFT = 0x36

    RIGHT_UP = [0xCD, 0xC8]
    RIGHT_DOWN = [0xCD, 0xD0]
    LEFT_UP = [0xCB, 0xC8]
    LEFT_DOWN = [0xCB, 0xD0]


# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)


class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]


# Actual Functions
def press_key(hex_keycode: int):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hex_keycode, 0x0008, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def release_key(hex_keycode: int):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hex_keycode, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def press_and_release_key(hex_keycode: int, interval: float = 0.02):
    time.sleep(0.2)
    press_key(hex_keycode)
    time.sleep(interval)
    release_key(hex_keycode)


def click_down(button: int = 1):
    # not valid
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    if button == 0:  # left click
        ii_.mi.dwFlags = ctypes.c_ulong(0x0002)
    elif button == 2:  # right click
        ii_.mi.dwFlags = ctypes.c_ulong(0x0008)
    else:  # middle click
        ii_.mi.dwFlags = ctypes.c_ulong(0x0020)
    ii_.mi.mouseData = ctypes.c_ulong(0)
    ii_.mi.time = ctypes.c_ulong(0)
    ii_.mi.dwExtraInfo = ctypes.pointer(extra)
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def click_up(button: int = 1):
    # not valid
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    if button == 0:  # left click
        ii_.mi.dwFlags = ctypes.c_ulong(0x0004)
    elif button == 2:  # right click
        ii_.mi.dwFlags = ctypes.c_ulong(0x0010)
    else:  # middle click
        ii_.mi.dwFlags = ctypes.c_ulong(0x0020)
    ii_.mi.mouseData = ctypes.c_ulong(0)
    ii_.mi.time = ctypes.c_ulong(0)
    ii_.mi.dwExtraInfo = ctypes.pointer(extra)
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def run_to(hex_keycode: int, interval: float = 0.02, lasting: float = 0.5):
    press_and_release_key(hex_keycode, interval)
    time.sleep(interval)
    press_and_release_key(hex_keycode, lasting)
