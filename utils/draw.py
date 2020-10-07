from mathutils import Vector
import blf

SCREEN_DPI = 72

WHITE = Vector((1.0, 1.0, 1.0, 1.0))
RED = Vector((1.0, 0.0, 0.0, 1.0))
ORANGE = Vector((1.0, 0.6, 0.0, 1.0))
GREEN = Vector((0.0, 1.0, 0.0, 1.0))

def draw_text_left_alignement(text, size, x, y, color, context):
    font_id = 0
    blf.size(font_id, size, SCREEN_DPI)
    blf.position(font_id, x, y, 0)
    blf.color(font_id, color.x, color.y, color.z, color.w)
    blf.draw(font_id, text)

def draw_text(text, size, y, color, context):
    font_id = 0

    middle = int(context.region.width * 0.5)

    blf.size(font_id, size, SCREEN_DPI)
    blf.position(font_id, middle - blf.dimensions(font_id, text)[0] / 2, y, 0)
    blf.color(font_id, color.x, color.y, color.z, color.w)
    blf.draw(font_id, text)