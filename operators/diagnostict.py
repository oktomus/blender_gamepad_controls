
# https://blender.stackexchange.com/questions/28999/constantly-running-modal-operator
# https://blender.stackexchange.com/questions/23532/get-events-without-running-modal
# https://docs.blender.org/api/current/info_gotcha.html?highlight=update
import bpy
import blf
import bgl

from threading import Thread, Event
from functools import partial

from ..thirdparties.inputs import devices
from ..thirdparties.inputs import get_gamepad
from ..utils.inputs import is_gamepad_plugged
from ..gamepad.xbox_gamepad import XboxController
from ..utils.draw import draw_text, draw_text_left_alignement, ORANGE, WHITE, RED, GREEN

from mathutils import Vector

from time import sleep

class XBOXDiagnostic(bpy.types.Operator):
    """My Object Moving Script"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "xbox.diagnostic_controller"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Diagnostic XBOX controller"         # Display name in the interface.
    bl_options = {'REGISTER'}  # Enable undo for the operator.

    BUTTON_NEVER_PRESSED = 0
    BUTTON_PRESSED = 1

    def invoke(self, context, event):
        args = (self, context)

        self._was_A_pressed = False
        self._was_B_pressed = False
        self._was_X_pressed = False
        self._was_Y_pressed = False
        self._was_Start_pressed = False
        self._was_Back_pressed = False
        self._was_LB_pressed = False
        self._was_RB_pressed = False
        self._was_Up_pressed = False
        self._was_Down_pressed = False
        self._was_Left_pressed = False
        self._was_Right_pressed = False
        self._left_joystick_x_min = 0
        self._left_joystick_x_max = 0
        self._left_joystick_y_min = 0
        self._left_joystick_y_max = 0
        self._right_joystick_x_min = 0
        self._right_joystick_x_max = 0
        self._right_joystick_y_min = 0
        self._right_joystick_y_max = 0
        self._was_left_trigger_pressed = False
        self._was_right_trigger_pressed = False

        if not is_gamepad_plugged():
            self.report(
                {'ERROR'},
                'No gamepad found. \n'
                + 'Try to run the diagnostic mode (F3 > {}).'.format(XBOXDiagnostic.bl_label))
            return {'CANCELLED'}

        self._handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_diagnostic, args, "WINDOW", "POST_PIXEL")

        bpy.ops.screen.animation_play()

        # Init contoller for manual override
        self.real_controller = XboxController()

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):

        if context.area:
            context.area.tag_redraw()

        if event.type in {'ESC'}:
            return self.finish()
        
        return {'PASS_THROUGH'}

    def finish(self):
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, "WINDOW")

        self.real_controller.stop()
        del self.real_controller

        bpy.ops.screen.animation_cancel(restore_frame=False)

        return {'FINISHED'}

    def update_controller_state(self):
        # Update controller inputs state.
        self.real_controller.tick()

        self._was_A_pressed |= self.real_controller.a.is_down()
        self._was_B_pressed |= self.real_controller.b.is_down()
        self._was_X_pressed |= self.real_controller.x.is_down()
        self._was_Y_pressed |= self.real_controller.y.is_down()
        self._was_Start_pressed |= self.real_controller.start.is_down()
        self._was_Back_pressed |= self.real_controller.back.is_down()
        self._was_LB_pressed |= self.real_controller.left_bumper.is_down()
        self._was_RB_pressed |= self.real_controller.right_bumper.is_down()
        self._was_Up_pressed |= self.real_controller.arrows.up.is_down()
        self._was_Down_pressed |= self.real_controller.arrows.down.is_down()
        self._was_Left_pressed |= self.real_controller.arrows.left.is_down()
        self._was_Right_pressed |= self.real_controller.arrows.right.is_down()

        self._left_joystick_x_min = min(self._left_joystick_x_min, self.real_controller.left_joystick.raw.x)
        self._left_joystick_x_max = max(self._left_joystick_x_max, self.real_controller.left_joystick.raw.x)
        self._left_joystick_y_min = min(self._left_joystick_y_min, self.real_controller.left_joystick.raw.y)
        self._left_joystick_y_max = max(self._left_joystick_y_max, self.real_controller.left_joystick.raw.y)
        self._right_joystick_x_min = min(self._right_joystick_x_min, self.real_controller.right_joystick.raw.x)
        self._right_joystick_x_max = max(self._right_joystick_x_max, self.real_controller.right_joystick.raw.x)
        self._right_joystick_y_min = min(self._right_joystick_y_min, self.real_controller.right_joystick.raw.y)
        self._right_joystick_y_max = max(self._right_joystick_y_max, self.real_controller.right_joystick.raw.y)

        self._was_left_trigger_pressed |= self.real_controller.left_trigger.raw == self.real_controller.left_trigger.expected_max
        self._was_right_trigger_pressed |= self.real_controller.right_trigger.raw == self.real_controller.right_trigger.expected_max

    def draw_diagnostic(tmp, self, context):

        self.update_controller_state()

        # Draw header.
        draw_text("XBOX 360 Controller Diagnostic. Press (ESC) to stop.", 14, 10, WHITE, context)
        draw_text("Animation must be playing to use the controller.", 12, 25, ORANGE, context)

        if len(devices.gamepads) > 0:
            draw_text(devices.gamepads[0].name, 12, 38, WHITE, context)
        else:
            draw_text("No gamepad", 12, 38, RED, context)

        # Draw inputs.
        # First column: A, B, X, Y, Start, Back
        draw_text_left_alignement(
            "A" if self._was_A_pressed else "Press A",
            16, 10, 50,
            GREEN if self._was_A_pressed else RED,
            context)
        draw_text_left_alignement(
            "B" if self._was_B_pressed else "Press B",
            16, 10, 70,
            GREEN if self._was_B_pressed else RED,
            context)
        draw_text_left_alignement(
            "X" if self._was_X_pressed else "Press X",
            16, 10, 90,
            GREEN if self._was_X_pressed else RED,
            context)
        draw_text_left_alignement(
            "Y" if self._was_Y_pressed else "Press Y",
            16, 10, 110,
            GREEN if self._was_Y_pressed else RED,
            context)
        draw_text_left_alignement(
            "Start" if self._was_Start_pressed else "Press Start",
            16, 10, 130,
            GREEN if self._was_Start_pressed else RED,
            context)
        draw_text_left_alignement(
            "Back" if self._was_Back_pressed else "Press Back",
            16, 10, 150,
            GREEN if self._was_Back_pressed else RED,
            context)

        # Second column: Up, Dow, Left, Right, LT, RT
        draw_text_left_alignement(
            "LB" if self._was_LB_pressed else "Press LB",
            16, 150, 50,
            GREEN if self._was_LB_pressed else RED,
            context)
        draw_text_left_alignement(
            "RB" if self._was_RB_pressed else "Press RB",
            16, 150, 70,
            GREEN if self._was_RB_pressed else RED,
            context)
        draw_text_left_alignement(
            "Up arrow" if self._was_Up_pressed else "Press Up arrow",
            16, 150, 90,
            GREEN if self._was_Up_pressed else RED,
            context)
        draw_text_left_alignement(
            "Down arrow" if self._was_Down_pressed else "Press Down arrow",
            16, 150, 110,
            GREEN if self._was_Down_pressed else RED,
            context)
        draw_text_left_alignement(
            "Left arrow" if self._was_Left_pressed else "Press Left arrow",
            16, 150, 130,
            GREEN if self._was_Left_pressed else RED,
            context)
        draw_text_left_alignement(
            "Right" if self._was_Right_pressed else "Press Right arrow",
            16, 150, 150,
            GREEN if self._was_Right_pressed else RED,
            context)

        # Third column: Left joystick
        draw_text_left_alignement(
            "Left joystick {}".format(self.real_controller.left_joystick.raw),
            16, 310, 50,
            WHITE,
            context)
        draw_text_left_alignement(
            "Min X",
            16, 310, 70,
            GREEN if self._left_joystick_x_min == self.real_controller.left_joystick.expected_min else RED,
            context)
        draw_text_left_alignement(
            "Max X",
            16, 310, 90,
            GREEN if self._left_joystick_x_max == self.real_controller.left_joystick.expected_max else RED,
            context)
        draw_text_left_alignement(
            "Min Y",
            16, 310, 110,
            GREEN if self._left_joystick_y_min == self.real_controller.left_joystick.expected_min else RED,
            context)
        draw_text_left_alignement(
            "Max Y",
            16, 310, 130,
            GREEN if self._left_joystick_y_max == self.real_controller.left_joystick.expected_max else RED,
            context)

        # Fourth column: Rigth joystick
        draw_text_left_alignement(
            "Right joystick {}".format(self.real_controller.right_joystick.raw),
            16, 470, 50,
            WHITE,
            context)
        draw_text_left_alignement(
            "Min X",
            16, 470, 70,
            GREEN if self._right_joystick_x_min == self.real_controller.right_joystick.expected_min else RED,
            context)
        draw_text_left_alignement(
            "Max X",
            16, 470, 90,
            GREEN if self._right_joystick_x_max == self.real_controller.right_joystick.expected_max else RED,
            context)
        draw_text_left_alignement(
            "Min Y",
            16, 470, 110,
            GREEN if self._right_joystick_y_min == self.real_controller.right_joystick.expected_min else RED,
            context)
        draw_text_left_alignement(
            "Max Y",
            16, 470, 130,
            GREEN if self._right_joystick_y_max == self.real_controller.right_joystick.expected_max else RED,
            context)

        # Fith column: Left and right trigger
        draw_text_left_alignement(
            "Left trigger {}".format(self.real_controller.left_trigger.raw),
            16, 620, 90,
            GREEN if self._was_left_trigger_pressed else RED,
            context)
        draw_text_left_alignement(
            "Right trigger {}".format(self.real_controller.right_trigger.raw),
            16, 620, 70,
            GREEN if self._was_right_trigger_pressed else RED,
            context)
