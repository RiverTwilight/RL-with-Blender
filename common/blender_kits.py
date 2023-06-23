import bpy

def render_image(camera_name, output_path):
    # Set the active camera
    bpy.context.scene.camera = bpy.data.objects[camera_name]

    # Set render settings
    bpy.context.scene.render.image_settings.file_format = 'PNG'  # or 'JPEG', 'BMP', etc.
    bpy.context.scene.render.filepath = output_path

    # Render image
    bpy.ops.render.render(write_still = True)

def render_image_sequence(camera_name, output_path, start_frame, end_frame):
    # Set the active camera
    bpy.context.scene.camera = bpy.data.objects[camera_name]

    # Set render settings
    bpy.context.scene.render.image_settings.file_format = 'PNG'  # or 'JPEG', 'BMP', etc.
    bpy.context.scene.frame_start = start_frame
    bpy.context.scene.frame_end = end_frame

    for frame in range(start_frame, end_frame + 1):
        bpy.context.scene.frame_set(frame)
        bpy.context.scene.render.filepath = f"{output_path}_{frame:04d}"  # output path includes frame number
        bpy.ops.render.render(write_still = True)

if __name__ == "main":
    render_image('UAV_Camera', '/tmp/image.png')
    render_image_sequence('UAV_Camera', '/tmp/image_sequence', 0, 100)
