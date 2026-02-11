from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

device = AudioUtilities.GetSpeakers()

interface = device._dev.Activate(
    IAudioEndpointVolume._iid_,
    CLSCTX_ALL,
    None
)

volume = cast(interface, POINTER(IAudioEndpointVolume))

def mute_laptop(mute: bool):
    """
    Mute or unmute the laptop's audio.
    """
    if mute:
        volume.SetMute(1, None)  # Mute
    else:
        volume.SetMute(0, None)  # Unmute