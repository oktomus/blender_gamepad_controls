import bpy

def get_selected_camera():
    """Return the selected camera."""
    selected_objects = bpy.context.selected_objects
    
    # None will be returned if nothing match
    return next((obj for obj in selected_objects if obj.type == 'CAMERA'), None)