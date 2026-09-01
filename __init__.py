bl_info = {
    "name": "Texture Remap Panel",
    "author": "Winn (Whatify)",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View 3D > Sidebar > Sources",
    "category": "3D View",
}


import bpy
from bpy.types import Panel, PropertyGroup
from bpy.props import BoolProperty, PointerProperty, IntProperty
from bpy_extras.io_utils import ExportHelper
import bmesh
from mathutils import Vector
import mathutils


def get_selection_bounds(context):
    objs = [obj for obj in context.selected_objects if obj.type == 'MESH']
    if not objs:
        return None

    min_bound = mathutils.Vector((float('inf'), float('inf'), float('inf')))
    max_bound = mathutils.Vector((float('-inf'), float('-inf'), float('-inf')))

    for obj in objs:
        for v in obj.bound_box:
            world_v = obj.matrix_world @ mathutils.Vector(v)
            min_bound = mathutils.Vector(map(min, min_bound, world_v))
            max_bound = mathutils.Vector(map(max, max_bound, world_v))

    return min_bound, max_bound

def fit_camera_to_bounds(camera, bounds_min, bounds_max):
    # Center point
    center = (bounds_min + bounds_max) / 2
    size = bounds_max - bounds_min

    # Set camera position for top-down view
    camera.location = (center.x, center.y, center.z + 10)
    camera.rotation_euler = (0, 0, 0)

    ratio = getattr(bpy.context.scene.my_tool, "x_camera_size")/ getattr(bpy.context.scene.my_tool, "y_camera_size")
    
    # Orthographic scale needs to cover the larger dimension
    ortho_scale = max(size.x/ratio, size.y*ratio) * 0.5
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = ortho_scale * 2  # Full width/height

def set_render_settings():
    render = bpy.context.scene.render
    render.resolution_x = getattr(bpy.context.scene.my_tool, "x_camera_size")
    render.resolution_y = getattr(bpy.context.scene.my_tool, "y_camera_size")
    render.resolution_percentage = 100

_last_index = 0
def source_update(index):
    def update(self, context):
        property_name = f"source_{index}"

        ignore_unrelated_update = self.get("_updating_sources", False)
        if ignore_unrelated_update:
            return
        
        global _last_index
        this_is_deselected = not getattr(self, property_name)
        if this_is_deselected:
            if _last_index == index:
                setattr(self, property_name, True)
            return

        self["_updating_sources"] = True
        _last_index = index
        try:
            for other_index in range(10):
                if other_index == index:
                    continue

                other_name = f"source_{other_index}"

                if getattr(self, other_name):
                    setattr(self, other_name, False)

        finally:
            self["_updating_sources"] = False

    return update

class MyToolProperties(PropertyGroup):
    x_camera_size: IntProperty(name='x_camera_size', default=512, min=512, soft_max=4096)
    y_camera_size: IntProperty(name='y_camera_size', default=512, min=512, soft_max=4096)
    
    source_0: BoolProperty(
        name="source_0",
        default=True,
        update=source_update(0),
    )
    source_1: BoolProperty(
        name="source_1",
        default=False,
        update=source_update(1),
    )
    source_2: BoolProperty(
        name="source_2",
        default=False,
        update=source_update(2),
    )
    source_3: BoolProperty(
        name="source_3",
        default=False,
        update=source_update(3),
    )
    source_4: BoolProperty(
        name="source_4",
        default=False,
        update=source_update(4),
    )
    source_5: BoolProperty(
        name="source_5",
        default=False,
        update=source_update(5),
    )
    source_6: BoolProperty(
        name="source_6",
        default=False,
        update=source_update(6),
    )
    source_7: BoolProperty(
        name="source_7",
        default=False,
        update=source_update(7),
    )
    source_8: BoolProperty(
        name="source_8",
        default=False,
        update=source_update(8),
    )
    source_9: BoolProperty(
        name="source_9",
        default=False,
        update=source_update(9),
    )
    
    
class OBJECT_OT_set_camera_size(bpy.types.Operator):
    bl_idname = "object.set_camera_size"
    bl_label = "Align Camera to Flat Mesh"
    bl_description = "Set camera to the selection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bounds = get_selection_bounds(context)
        if not bounds:
            self.report({'ERROR'}, "No mesh objects selected")
            return {'CANCELLED'}

        scene = context.scene
        source_obj = scene.camera
        for target_obj in context.selected_objects:    
            if target_obj.type != 'CAMERA':
                continue
            source_obj = target_obj
            
            
        if not source_obj:
            self.report({'ERROR'}, "No camera found in scene")
            return {'CANCELLED'}

        fit_camera_to_bounds(source_obj, *bounds)
        set_render_settings()

        return {'FINISHED'}
    
class OBJECT_OT_fix_rgb_render(bpy.types.Operator):
    bl_idname = "object.fix_rgb"
    bl_label = "Fix Camera Colors"
    bl_description = "Fix faded and dull colors in camera render previews"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = bpy.context.scene
        color_management = scene.render.image_settings
        display_settings = scene.display_settings
        view_settings = scene.view_settings
        color_management.file_format = 'PNG' 
        color_management.color_mode = 'RGBA' 
        color_management.color_depth = '8'
        scene.display_settings.display_device = 'sRGB' #
        scene.view_settings.view_transform = 'Standard' #
        scene.view_settings.look = 'None'
        self.report({'INFO'}, "Cameras should have accurate flat colors now!")
        return {'FINISHED'}


class OBJECT_OT_uv_to_geometry(bpy.types.Operator):
    bl_idname = "object.uv_to_geometry"
    bl_label = "Flatten UV to Target UV (Geometry)"
    bl_description = "Physically flattens the active object's geometry using the UV map of another selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selection = context.selected_objects

        target_obj = context.selected_objects[_last_index] #context.active_object

        source_objs = []
        if len(selection)>1:
            source_objs = [obj for obj in selection if obj != target_obj and obj.type == 'MESH']
        else:
            source_objs = [target_obj]
            
        for source_obj in source_objs:    
            if len(target_obj.data.polygons) != len(source_obj.data.polygons):
                self.report({'ERROR'}, "Selected objects must have identical geometry (same face count)")
                return {'CANCELLED'}
            
        # Create UV guide plane
        plane_mesh = bpy.data.meshes.new("UV_BasePlane")
        plane_obj = bpy.data.objects.new("UV_BasePlane", plane_mesh)
        context.collection.objects.link(plane_obj)

        verts = [
            Vector((0, 0, -0.01)),
            Vector((2.0, 0, -0.01)),
            Vector((2.0, 2.0, -0.01)),
            Vector((0, 2.0, -0.01)),
        ]
        faces = [(0, 1, 2, 3)]
        plane_mesh.from_pydata(verts, [], faces)
        plane_mesh.update()
        
        for source_obj in source_objs:    
            # Prepare bmeshes
            target_bm = bmesh.new()
            target_bm.from_mesh(source_obj.data)
            source_bm = bmesh.new()
            source_bm.from_mesh(target_obj.data)
            uv_layer = source_bm.loops.layers.uv.active

            if uv_layer is None:
                self.report({'ERROR'}, "Source object has no UV map")
                return {'CANCELLED'}

            flat_bm = bmesh.new()

            # Use a matching-by-face-order approach
            source_faces = list(source_bm.faces)
            target_faces = list(target_bm.faces)

            for src_face, tgt_face in zip(source_faces, target_faces):
                new_verts = []
                for src_loop, tgt_loop in zip(src_face.loops, tgt_face.loops):
                    uv = src_loop[uv_layer].uv
                    # Place new vertex at UV coordinates in XY space
                    vert = flat_bm.verts.new((uv.x * 2.0, uv.y * 2.0, 0))
                    new_verts.append(vert)
                try:
                    flat_bm.faces.new(new_verts)
                except ValueError:
                    # Face might already exist due to shared verts; skip
                    pass
            
            # Create UV layer in new mesh and copy target UVs
            uv_target_layer = target_bm.loops.layers.uv.active
            uv_new_layer = flat_bm.loops.layers.uv.new("OriginalUV")

            for flat_face, tgt_face in zip(flat_bm.faces, target_bm.faces):
                for flat_loop, tgt_loop in zip(flat_face.loops, tgt_face.loops):
                    flat_loop[uv_new_layer].uv = tgt_loop[uv_target_layer].uv.copy()

            flat_bm.normal_update()
            new_mesh = bpy.data.meshes.new(source_obj.name + "_UVFlat")
            flat_bm.to_mesh(new_mesh)
            flat_bm.free()
            target_bm.free()
            source_bm.free()


            new_obj = bpy.data.objects.new(source_obj.name + "_UVFlat", new_mesh)
            for mat in target_obj.data.materials:
                new_obj.data.materials.append(mat)
            context.collection.objects.link(new_obj)
            #new_obj.select_set(True)
            #context.view_layer.objects.active = new_obj

            new_obj.parent = plane_obj

            self.report({'INFO'}, "Flattened mesh created using UVs from source object.")
        return {'FINISHED'}

class VIEW3D_PT_radio_sources(Panel):
    bl_label = "Texture UV Porting Tool"
    bl_idname = "VIEW3D_PT_radio_sources"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Texture Transfer"

    def draw(self, context):
        global _last_index
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False

        topbox = layout.box()
        topbox.label(text="Fix faded RGB Colors:", icon="COLOR")
        topbox.operator("object.fix_rgb")
        
        mytool = context.scene.my_tool
        layout.label(text="Select up to 10 Meshes to continue")
        
        selection = context.selected_objects        
        i = 0
        box = layout.box()
        box.label(text="Select 1 Target Mesh", icon="PINNED")
        for target_obj in selection:    
            if i > 9 :
                break
            source_obj = target_obj

            if target_obj.type != 'MESH' or source_obj.type != 'MESH':
                box.label(text = f"Not a mesh: {source_obj.name}")
                continue
            
            property_name = f"source_{i}"
            value = getattr(mytool, property_name)

            # The first column gets 12% of the row width.
            split = box.split(factor=0.12, align=True)

            checkbox_column = split.column(align=True)
            label_column = split.column(align=True)
            
            checkbox_column.prop(
                mytool,
                property_name,
                text="",
                icon="PINNED" if value else "CHECKBOX_DEHLT",
                emboss=True,
            )
            
            label_column.label(text=source_obj.name)
            i = i + 1
        
        if _last_index < 10 and _last_index < len(selection) and i > 0:
            layout.label(text=f"Ready to Flatten?", icon="PINNED" )
            box2 = layout.box()
            box2.label(text="Flatten All To Target Mesh")
            box2.operator("object.uv_to_geometry")
        else:
            layout.label(text="No Target Mesh")
        
        lastbox = layout.box()
        lastbox.label(text="Set Camera Render Size (Pixels)", icon="SELECT_INTERSECT")
        
        split = lastbox.split(factor=0.25, align=True)
        label_column = split.column(align=True)
        checkbox_column = split.column(align=True)
        last_column = split.column(align=True)
        
        label_column.label(text="Size:")
        
        checkbox_column.prop(mytool,"x_camera_size", text="x:")
        last_column.prop(mytool,"y_camera_size", text="y:")
        
        cam_obj = None
        for obj in selection:    
            if obj.type != 'CAMERA' or obj.type != 'CAMERA':
                continue
            cam_obj = obj
        if cam_obj:
            lastbox.operator("object.set_camera_size")
        
classes = (
    MyToolProperties,
    VIEW3D_PT_radio_sources,
    OBJECT_OT_uv_to_geometry,
    OBJECT_OT_fix_rgb_render,
    OBJECT_OT_set_camera_size
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.my_tool = PointerProperty(
        type=MyToolProperties
    )


def unregister():
    del bpy.types.Scene.my_tool

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
