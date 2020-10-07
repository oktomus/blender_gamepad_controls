"""
Helpers for blender 3D viewport.
"""

import bpy

def get_viewport():
    all_3d_areas = [area for area in bpy.context.window.screen.areas if area.type == 'VIEW_3D']

    if not all_3d_areas:
        return None

    return all_3d_areas[0]

def toggle_viewport_camera_viewpoint():
    """Toggle camera viewpoint (like Numpad-0)."""

    viewport = get_viewport()

    if not viewport:
        return

    region = [region for region in viewport.regions if region.type == 'WINDOW']

    override = {
        'window':   bpy.context.window,
        'screen':   bpy.context.window.screen,
        'area':     viewport,
        'region':   region,
        'scene':    bpy.context.scene,
    }
    
    # The override should not be a keyword argument.
    # See https://blender.stackexchange.com/questions/15118/how-do-i-override-context-for-bpy-ops-mesh-loopcut.
    bpy.ops.view3d.view_camera(override)