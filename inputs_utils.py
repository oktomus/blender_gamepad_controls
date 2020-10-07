"""Utils functions for Inputs.
"""

from . inputs import devices

def reset_device_manager():
    """Reset to get the actual list of plugged-in devices."""

    devices.gamepads = []
    devices.keyboards = []
    devices.mice = []
    devices.microbits = []

    devices._post_init()

def is_gamepad_plugged():
    """Check if the gamepad is plugged"""

    # Make sure a new plugged-in gamepad is detected.
    reset_device_manager()

    return len(devices.gamepads) > 0