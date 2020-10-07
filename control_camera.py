
import bpy
import bgl

from threading import Thread, Event
from functools import partial

from datetime import datetime

from . inputs import devices
from . inputs import get_gamepad
from . inputs_utils import is_gamepad_plugged

from . gamepad_input import XboxController

from . dev_mode import is_dev_mode

from . utils.draw import draw_text, draw_text_left_alignement, ORANGE, WHITE, RED

from . diagnostict import XBOXDiagnostic

from . viewport_utils import toggle_viewport_camera_viewpoint
from . camera_utils import get_selected_camera

from mathutils import Vector, Matrix

from . math_utils import clamp

class ControlCamera(bpy.types.Operator):
    """Control camera with a gamepad controller"""      

    bl_idname = "xbox.run"                          
    bl_label = "Control camera with XBOX controller"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        """Allow use of this operator only in 3D viewport."""
        is_view_3d = (
            bpy.context.area != None 
            and bpy.context.area.type == 'VIEW_3D'
        )
        
        return is_view_3d

    def invoke(self, context, event):
        args = (self, context)

        if not is_gamepad_plugged():
            self.report(
                {'ERROR'},
                'No gamepad found. \n'
                + 'Try to run the diagnostic mode (F3 > {}).'.format(XBOXDiagnostic.bl_label))
            return {'CANCELLED'}

        self.original_frame_current = bpy.data.scenes['Scene'].frame_current

        # We use a timer to compute the time delta between two events.
        # The time delta is then used in input handling to keep the time consistent.
        # https://docs.unity3d.com/ScriptReference/Time-deltaTime.html
        self.time_now = datetime.now()

        # Start a recording session for the gamepad.
        self.real_controller = XboxController()

        # Register a drawing overlay.
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_operator, args, "WINDOW", "POST_PIXEL")

        # Receive all events.
        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):

        # Stop the operator on demand.
        if event.type in {'ESC'}:
            return self.finish()

        time_then = self.time_now
        self.time_now = datetime.now() 
        self.delta_time = (self.time_now - time_then).total_seconds()

        # Extend the timeline.
        scene = bpy.data.scenes['Scene']

        if scene.frame_current + 5 > scene.frame_end:
            scene.frame_end += 5

        # Draw on top of the 3D viewport.
        if context.area:
            context.area.tag_redraw()

        # Only consider frame events.
        # https://docs.blender.org/api/current/bpy.types.Event.html#bpy.types.Event.type
        if event.type != 'TIMER0':
            return {'PASS_THROUGH'}

        # Handle gamepad inputs.
        self._process_gamepad_inputs()
        
        return {'PASS_THROUGH'}

    def finish(self):
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, "WINDOW")
        self._handle = None

        self.real_controller.stop()
        del self.real_controller

        # Come back to the begining of the animation.
        if bpy.ops.screen.animation_cancel.poll():
            bpy.ops.screen.animation_cancel(restore_frame=True)

        bpy.data.scenes['Scene'].frame_current = self.original_frame_current

        return {'FINISHED'}

    def draw_operator(tmp, self, context):

        # Nothing is done while animation is not playing.
        # Warn the user about that.
        if not bpy.context.screen.is_animation_playing:
            draw_text("Animation must be playing to use the controller (Space).", 12, 25, ORANGE, context)
        else:
            draw_text("Running...", 12, 25, ORANGE, context)

    def _process_gamepad_inputs(self):
        """Act based on gamepad inputs."""

        self.real_controller.tick()

        # Start: toggle camera as active view.
        # fixme: crash when toggling back.
        if self.real_controller.start.is_down():
            print("Toggle")
            toggle_viewport_camera_viewpoint()

        # Get the camera.
        camera = get_selected_camera()

        # No camera
        if camera is None:
            print("Please select camera")
            return

        camera_data = camera.data

        joystick_epsilon = 0.01
        left_x, left_y = self.real_controller.left_joystick.get_normalized()
        right_x, right_y = self.real_controller.right_joystick.get_normalized()

        # Only consider joystick inputs if the user really move them.
        trigger_left_x = abs(left_x) > joystick_epsilon
        trigger_left_y = abs(left_y) > joystick_epsilon
        trigger_right_x = abs(right_x) > joystick_epsilon
        trigger_right_y = abs(right_y) > joystick_epsilon

        # Control field of view.
        if self.real_controller.left_bumper.is_hold() and trigger_left_y:
            current_fov = camera_data.angle
            # https://docs.blender.org/api/current/bpy.types.Camera.html#bpy.types.Camera.angle
            new_fov = clamp(current_fov - left_y * self.delta_time, 0.00640536, 3.01675)
            camera_data.angle = new_fov
            # Keyframe it.
            camera_data.keyframe_insert('lens')
            return

        # https://i.redd.it/hrr79vpb0m601.png
        # Truck
        if trigger_left_x:
            vec = Vector((left_x * self.delta_time * (5.0), 0.0, 0.0))
            inv = camera.matrix_world.copy()
            inv.invert()
            vec_rot = vec @ inv
            camera.location = camera.location + vec_rot
            camera.keyframe_insert('location')

        # Dolly
        if trigger_left_y:
            vec = Vector((0.0, 0.0, left_y * self.delta_time * (-5.0)))
            inv = camera.matrix_world.copy()
            inv.invert()
            vec_rot = vec @ inv
            camera.location = camera.location + vec_rot
            camera.keyframe_insert('location')

        # Pan
        if trigger_right_x:
            camera.rotation_euler[2] += right_x * self.delta_time * (-2.0)
            camera.keyframe_insert('rotation_euler')

        # Tilt
        if trigger_right_y:
            camera.rotation_euler[0] += right_y * self.delta_time * (2.0)
            camera.keyframe_insert('rotation_euler')
