#!/usr/bin/env python
# https://github.com/kevinhughes27/TensorKart/blob/master/utils.py

import sys
import array

from typing import NamedTuple

from ..thirdparties.inputs import get_gamepad, devices, UnpluggedError
from ..dev_mode import is_dev_mode
from ..utils.math import map_float

import math
import threading

class XYTuple():
    """Simple class containing a 2D coordinate."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "[{}, {}]".format(self.x, self.y)

class GamepadButton():
    """A button with a state and up/down event detection."""

    def __init__(self):
        self.state = 0

        self._is_up = False
        self._is_down = False
        self._is_hold = False

    def tick(self):
        """Update up and down state for a new frame.

        A tick is a moment of time where we want to know
        is the button has just been pressed or released.

        Without that, we only know if the button is active or not.
        But when you want to trigger an action on a button press,
        you want to trigger only once. To do so, we need to detect
        up and down events.

        Up means the button has just been released (will remain true during one moment).
        Down means the button has just been pressed (will remain true during one moment).
        """

        was_down = self._is_down
        was_hold = self._is_hold
        was_up = self._is_up

        # "Hold" is True during "Is down" and "Is up" moments.
        self._is_hold = self.state == 1 and (was_down or was_hold)

        # "Is down" is True at the moment the user press the button.
        self._is_down = self.state == 1 and not was_down and not was_hold and not self._is_hold

        # "Is up" is True at the moment the user release the button.
        # We can go from down to up without going to hold.
        self._is_up = self.state == 0 and (was_hold or was_down)

        # Only one or zero of those state should be on.
        assert int(self._is_down) + int(self._is_hold) + int(self._is_up) <= 1

    def is_down(self):
        """Return true durring the frame the user press the button."""
        return self._is_down

    def is_up(self):
        """Return true durring the frame the user release the button."""
        return self._is_up

    def is_hold(self):
        """Return true during frames where the user hold the button.

        The up and down frames are not included.
        """
        return self._is_hold

    def update_state(self, state):
        self.state = state

    def __str__(self):
        if self.is_down():
            return "[{} - DOWN]".format(self.state)
        elif self.is_hold():
            return "[{} - HOLD]".format(self.state)
        elif self.is_up():
            return "[{} - UP]".format(self.state)
        else:
            return "[{}...]".format(self.state)

class GamepadJoystick():
    """A gamepad joystick with a raw and normalized value [-1, 1]^2.

    With the inputs library, the xbox gamepad joysticks values 
    goes from -32768 to 32767 on each axis.
    """

    def __init__(self, expected_min, expected_max):
        self.raw = XYTuple(0, 0)

        assert expected_min != 0
        assert expected_max != 0 and expected_max > expected_min

        self.expected_min = expected_min
        self.expected_max = expected_max

    def update_x_state(self, state):
        """Update the joystick value using a new state."""
        self.raw.x = state

    def update_y_state(self, state):
        """Update the joystick value using a new state."""
        self.raw.y = state

    def get_normalized(self):
        # Compute values in [-1, 1]
        normed_x = map_float(float(self.expected_min), float(self.expected_max), -1.0, 1.0, self.raw.x)
        normed_y = map_float(float(self.expected_min), float(self.expected_max), -1.0, 1.0, self.raw.y)
        return normed_x, normed_y

class GamepadTrigger():
    """A gamepad trigger with a raw and noramlized value.

    With the inputs library, the xbox gamepad controller trigger
    values goes from 0 to 255 on each axis.
    """

    def __init__(self, expected_max):
        self.raw = 0

        assert(expected_max > 0)
        self.expected_max = expected_max

    def update_state(self, state):
        """Update the trigger value using a new state."""
        self.raw = state

    def get_normalized_value():
        return self.raw / float(self.expected_max)

class GamepadArrows():
    """4 arrows on the gamepad.

    The four arrows react as buttons.
    """

    def __init__(self):
        self.left = GamepadButton()
        self.right = GamepadButton()
        self.up = GamepadButton()
        self.down = GamepadButton()

    def tick(self):
        self.left.tick()
        self.right.tick()
        self.up.tick()
        self.down.tick()

    def update_x_state(self, state):
        """Update the left and right state."""

        if state == -1:
            self.left.update_state(1)
            self.right.update_state(0)
        elif state == 1:
            self.left.update_state(0)
            self.right.update_state(1)
        else:
            self.left.update_state(0)
            self.right.update_state(0)

    def update_y_state(self, state):
        """Update the up and down state."""

        if state == -1:
            self.up.update_state(1)
            self.down.update_state(0)
        elif state == 1:
            self.up.update_state(0)
            self.down.update_state(1)
        else:
            self.up.update_state(0)
            self.down.update_state(0)

    def update_left_state(self, state):
        """Manually update left arrow state."""
        self.left.update_state(state)

    def update_right_state(self, state):
        """Manually update right arrow state."""
        self.right.update_state(state)

    def update_up_state(self, state):
        """Manually update up arrow state."""
        self.up.update_state(state)

    def update_down_state(self, state):
        """Manually update down arrow state."""
        self.down.update_state(state)

class XboxController(object):

    def __init__(self):

        # Joysticks inputs
        self.left_joystick = GamepadJoystick(-32768, 32767)
        self.right_joystick = GamepadJoystick(-32768, 32767)
        self.left_joystick_thumb = GamepadButton()
        self.right_joystick_thumb = GamepadButton()

        # Trigger inputs
        self.left_trigger = GamepadTrigger(255)
        self.right_trigger = GamepadTrigger(255)

        # Inputs (1 or 0)
        self.left_bumper = GamepadButton()
        self.right_bumper = GamepadButton()
        self.a = GamepadButton()
        self.x = GamepadButton()
        self.y = GamepadButton()
        self.b = GamepadButton()
        self.back = GamepadButton()
        self.start = GamepadButton()

        # Arrows (4 buttons)
        self.arrows = GamepadArrows()

        # Input detection will be done in another thread to keep 
        # the main thread running smoothly.
        # The pill to kill is used to stop that new thread.        
        # We use a deamon thread to make sure it is killed when blender stops.
        self._pill_to_kill = threading.Event()
        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=(self._pill_to_kill,))
        self._monitor_thread.daemon = True
        self._monitor_thread.start()

    def tick(self):
        """Update the state of the inputs at the begining of a frame.

        Must be called once per frame and before checking inputs values.

        The gamepad state is continuously updated with a monitor thread.

        But there is additional states (button up, hold, down) that needs to 
        be computed on a frame basis.
        """

        self.arrows.tick()
        self.left_bumper.tick()
        self.right_bumper.tick()
        self.a.tick()
        self.x.tick()
        self.b.tick()
        self.y.tick()
        self.back.tick()
        self.start.tick()

    def stop(self):
        self._pill_to_kill.set()

    def _monitor_controller(self, pill_to_kill):
        while not pill_to_kill.is_set():

            if len(devices.gamepads) == 0:
                continue

            try:
                events = get_gamepad()
            except UnpluggedError as e:
                continue

            for event in events:
                self._handle_event(event)

    def _handle_event(self, event):
        # Debug the event.
        if is_dev_mode:
            print("Event [{}] = [{}]".format(event.code, event.state))

        # Joystics.
        if event.code == 'ABS_Y':
            self.left_joystick.update_y_state(event.state)
        elif event.code == 'ABS_X':
            self.left_joystick.update_x_state(event.state)
        elif event.code == 'ABS_RY':
            self.right_joystick.update_y_state(event.state)
        elif event.code == 'ABS_RX':
            self.right_joystick.update_x_state(event.state)
        # Triggers.
        elif event.code == 'ABS_Z':
            self.left_trigger.update_state(event.state)
        elif event.code == 'ABS_RZ':
            self.right_trigger.update_state(event.state)
        # Buttons.
        elif event.code == 'BTN_TL':
            self.left_bumper.update_state(event.state)
        elif event.code == 'BTN_TR':
            self.right_bumper.update_state(event.state)
        elif event.code == 'BTN_SOUTH':
            self.a.update_state(event.state)
        elif event.code == 'BTN_EAST':
            self.b.update_state(event.state)
        elif event.code == 'BTN_WEST':
            self.x.update_state(event.state)
        elif event.code == 'BTN_NORTH':
            self.y.update_state(event.state)
        elif event.code == 'BTN_THUMBL':
            self.left_joystick_thumb.update_state(event.state)
        elif event.code == 'BTN_THUMBR':
            self.right_joystick_thumb.update_state(event.state)
        elif event.code == 'BTN_SELECT':
            self.start.update_state(event.state)
        elif event.code == 'BTN_START':
            self.back.update_state(event.state)
        # Arrows.
        elif event.code == 'ABS_HAT0X':
            self.arrows.update_x_state(event.state)
        elif event.code == 'ABS_HAT0Y':
            self.arrows.update_y_state(event.state)
        elif event.code == 'BTN_TRIGGER_HAPPY1':
            self.arrows.update_left_state(event.state)
        elif event.code == 'BTN_TRIGGER_HAPPY2':
            self.arrows.update_right_state(event.state)
        elif event.code == 'BTN_TRIGGER_HAPPY3':
            self.arrows.update_up_state(event.state)
        elif event.code == 'BTN_TRIGGER_HAPPY4':
            self.arrows.update_down_state(event.state)

# Debug purpose
# Run this script from the terminal.
if __name__ == "__main__":
    while True:
        events = get_gamepad()
        for event in events:
            print("Code {} State {}\n".format(event.code, event.state))
