from . xbox_gamepad import XboxController

controller = None

def get_controller():

    global controller
    if controller is None:
        controller = XboxController()

    return controller
