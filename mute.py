import ctypes

muted = False

# This sends a 'Virtual Key' command to Windows
def toggle_mute():
    # 0xAD is the virtual key code for Volume Mute
    ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)

def mute_laptop():
    global muted
    if not muted:
        toggle_mute()
        muted = True

def unmute_laptop():
    global muted
    if muted:
        toggle_mute()
        muted = False