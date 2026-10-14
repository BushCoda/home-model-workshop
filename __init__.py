"""Home Model Workshop - procedural house layout and blockout generator for Blender."""

bl_info = {
    "name": "Home Model Workshop",
    "author": "Home Model Workshop contributors",
    "version": (0, 1, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Home Model Workshop",
    "description": "Build editable house models from room layouts",
    "category": "3D View",
}

import bpy
import uuid
from bpy.props import EnumProperty, FloatProperty, BoolProperty, IntProperty, PointerProperty, CollectionProperty, StringProperty
from mathutils import Vector

ROOM_COLLECTION = "HF_Room_Layout"
MODEL_COLLECTION = "HF_Generated_Model"
GUIDE_COLLECTION = "HF_Layout_Guide"
EPS = 0.0005


def get_or_create_collection(name, parent=None):
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
    target = parent or bpy.context.scene.collection
    if collection.name not in target.children:
        target.children.link(collection)
    return collection


def clear_collection_objects(collection):
    if collection:
        for obj in list(collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)


def make_material(name, color):
    material = bpy.data.materials.get(name)
    if material is None:
        material = bpy.data.materials.new(name)
        material.diffuse_color = (*color, 1.0)
    return material


def make_box(name, center, dimensions, collection, material=None):
    cx, cy, cz = center
    dx, dy, dz = dimensions
    if min(dx, dy, dz) <= 0.001:
        return None
    verts = [
        (cx-dx/2, cy-dy/2, cz-dz/2), (cx+dx/2, cy-dy/2, cz-dz/2),
        (cx+dx/2, cy+dy/2, cz-dz/2), (cx-dx/2, cy+dy/2, cz-dz/2),
        (cx-dx/2, cy-dy/2, cz+dz/2), (cx+dx/2, cy-dy/2, cz+dz/2),
        (cx+dx/2, cy+dy/2, cz+dz/2), (cx-dx/2, cy+dy/2, cz+dz/2),
    ]
    faces = [(0,1,2,3), (4,7,6,5), (0,4,5,1), (1,5,6,2), (2,6,7,3), (4,0,3,7)]
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    obj["houseforge_generated"] = True
    return obj


def room_bounds(obj):
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return (min(p.x for p in points), max(p.x for p in points),
            min(p.y for p in points), max(p.y for p in points))


def unique_sorted(values, precision=4):
    return sorted(set(round(float(v), precision) for v in values))


def build_room_program(settings):
    """Return (name, zone) pairs so related rooms can be placed together."""
    rooms = []
    if settings.include_entry:
        rooms.append(("Entry Hall", "PUBLIC"))
    for index in range(settings.bedroom_count):
        rooms.append(("Master Bedroom" if index == 0 else f"Bedroom {index + 1}", "MASTER" if index == 0 else "PRIVATE"))
    for index in range(settings.bathroom_count):
        rooms.append(("Bathroom" if index == 0 else f"Bathroom {index + 1}", "PRIVATE"))
    if settings.bedroom_count:
        if settings.include_ensuite:
            rooms.append(("Ensuite", "MASTER"))
        if settings.include_wir:
            rooms.append(("Walk-in Robe", "MASTER"))
    for attr, label, zone in (
        ("include_living", "Living Room", "PUBLIC"), ("include_kitchen", "Kitchen", "PUBLIC"),
        ("include_dining", "Dining Room", "PUBLIC"), ("include_laundry", "Laundry", "SERVICE"),
        ("include_study", "Study", "PRIVATE"), ("include_garage", "Garage", "SERVICE"),
    ):
        if getattr(settings, attr):
            rooms.append((label, zone))
    for custom in settings.custom_rooms:
        label = custom.room_name.strip()
        if label:
            rooms.extend([(label, custom.zone)] * custom.quantity)
    return rooms


def starter_rooms(width, depth, layout_shape, room_program):
    """Place separate starter footprints in a non-overlapping staging grid."""
    defaults = {
        "Entry Hall": (2.2, 2.0), "Master Bedroom": (4.6, 4.2),
        "Ensuite": (2.4, 2.0), "Walk-in Robe": (2.4, 1.8),
        "Bathroom": (2.5, 2.4), "Living Room": (5.0, 4.0),
        "Kitchen": (3.4, 3.0), "Dining Room": (3.4, 3.0),
        "Laundry": (2.4, 2.0), "Study": (3.0, 3.0), "Garage": (6.0, 5.8),
    }
    result = []
    margin, gap = 0.4, 0.4
    x, y, row_depth = margin, margin, 0.0
    for name, zone in room_program:
        if name.startswith("Bedroom "):
            room_width, room_depth = 3.4, 3.2
        else:
            room_width, room_depth = defaults.get(name, (4.0, 3.0))
        if x + room_width > width - margin and x > margin:
            x = margin
            y += row_depth + gap
            row_depth = 0.0
        suite_id = "primary_suite_1" if zone == "MASTER" else ""
        result.append((name, x, x + room_width, y, y + room_depth, zone, suite_id))
        x += room_width + gap
        row_depth = max(row_depth, room_depth)
    return result


def layout_guide_outline(width, depth, layout_shape):
    """Return the closed perimeter for a visual-only footprint guide."""
    w, d = width, depth
    if layout_shape == 'L':
        points = [(0, 0), (w, 0), (w, d*0.38), (w*0.48, d*0.38), (w*0.48, d), (0, d)]
    elif layout_shape == 'H':
        points = [(0, 0), (0, d), (w*0.30, d), (w*0.30, d*0.65),
                  (w*0.70, d*0.65), (w*0.70, d), (w, d), (w, 0),
                  (w*0.70, 0), (w*0.70, d*0.35), (w*0.30, d*0.35), (w*0.30, 0)]
    elif layout_shape == 'U':
        points = [(0, 0), (w, 0), (w, d), (w*0.70, d), (w*0.70, d*0.35),
                  (w*0.30, d*0.35), (w*0.30, d), (0, d)]
    else:
        points = [(0, 0), (w, 0), (w, d), (0, d)]
    return points


def create_layout_guide(collection, width, depth, layout_shape):
    """Create a separate, non-rendering guide which never participates in wall generation."""
    points = layout_guide_outline(width, depth, layout_shape)
    mesh = bpy.data.meshes.new("HF_Layout_Guide_Mesh")
    mesh.from_pydata([(x, y, 0.025) for x, y in points],
                     [(i, (i+1) % len(points)) for i in range(len(points))], [])
    mesh.update()
    obj = bpy.data.objects.new(f"HF_{layout_shape}_Shape_Guide", mesh)
    collection.objects.link(obj)
    obj.display_type = 'WIRE'
    obj.show_in_front = True
    obj.hide_render = True
    obj.color = (0.05, 0.75, 0.95, 1.0)
    obj["hf_layout_guide"] = True
    obj["hf_guide_shape"] = layout_shape
    obj["hf_guide_width"] = width
    obj["hf_guide_depth"] = depth
    return obj


def create_room_footprint(collection, name, x0, x1, y0, y1, zone="PRIVATE", suite_id=""):
    verts = [(0,0,0), (x1-x0,0,0), (x1-x0,y1-y0,0), (0,y1-y0,0)]
    mesh = bpy.data.meshes.new("HF_RoomFootprint_Mesh")
    mesh.from_pydata(verts, [], [(0,1,2,3)])
    mesh.update()
    obj = bpy.data.objects.new("HF_ROOM_" + name.replace(" ", "_"), mesh)
    collection.objects.link(obj)
    obj.location = (x0, y0, 0.015)
    obj.display_type = 'WIRE'
    obj.show_in_front = True
    obj["houseforge_room"] = True
    obj["hf_room_id"] = "room_" + uuid.uuid4().hex[:12]
    obj["room_name"] = name
    obj["hf_room_zone"] = zone
    if suite_id:
        obj["hf_suite_id"] = suite_id
    return obj


class HF_CustomRoomDefinition(bpy.types.PropertyGroup):
    room_name: StringProperty(name="Room", default="Study")
    quantity: IntProperty(name="Count", default=1, min=1, max=12)
    zone: EnumProperty(name="Zone", items=[('PUBLIC', "Public", "Social or shared room"), ('PRIVATE', "Private", "Bedroom, study, or quiet room"), ('MASTER', "Primary Suite", "Room associated with the master bedroom"), ('SERVICE', "Service", "Utility or service room")], default='PRIVATE')


class HF_Settings(bpy.types.PropertyGroup):
    ui_show_help: BoolProperty(name="Quick Start & Help", default=False)
    ui_show_house_settings: BoolProperty(name="House & Construction", default=False)
    ui_show_room_plan: BoolProperty(name="Room Selection & Starting Guide", default=True)
    ui_show_custom_rooms: BoolProperty(name="Custom Room Program", default=False)
    ui_show_import_layout: BoolProperty(name="Import Existing Layout", default=False)
    ui_show_model_output: BoolProperty(name="Model Output", default=True)
    ui_show_openings: BoolProperty(name="Doors & Windows", default=False)
    workflow: EnumProperty(name="Workflow", items=[('ARCHITECTURE', "Architectural Design", "Prioritise dimensions, room schedules and visualisation"), ('GAME_ASSET', "Game Asset Creation", "Prioritise modular assets and game export preparation")], default='ARCHITECTURE')
    project_id: StringProperty(name="Project ID", default="")
    house_width: FloatProperty(name="House Width", default=16.0, min=6.0, max=60.0, unit='LENGTH')
    house_depth: FloatProperty(name="House Depth", default=10.0, min=6.0, max=50.0, unit='LENGTH')
    wall_height: FloatProperty(name="Wall Height", default=2.7, min=2.1, max=6.0, unit='LENGTH')
    wall_thickness: FloatProperty(name="Wall Thickness", default=0.15, min=0.07, max=0.5, unit='LENGTH')
    floor_thickness: FloatProperty(name="Floor Thickness", default=0.2, min=0.05, max=0.6, unit='LENGTH')
    layout_type: EnumProperty(name="Starter Layout", items=[('THREE_BED', "3 Bedroom", "Legacy three-bedroom layout"), ('FOUR_BED', "4 Bedroom", "Legacy four-bedroom layout")], default='THREE_BED')
    layout_shape: EnumProperty(name="Footprint Style", items=[('BOX', "Box", "Simple rectangular footprint"), ('L', "L Shape", "Two connected rectangular wings"), ('H', "H Shape", "Two wings joined by a central connector"), ('U', "U Shape", "Three wings around an open courtyard")], default='BOX')
    include_entry: BoolProperty(name="Entry Hall", default=True)
    bedroom_count: IntProperty(name="Bedrooms", default=3, min=0, max=12)
    bathroom_count: IntProperty(name="Bathrooms", default=1, min=0, max=8)
    include_ensuite: BoolProperty(name="Ensuite", default=True)
    include_wir: BoolProperty(name="Walk-in Robe", default=True)
    include_living: BoolProperty(name="Living Room", default=True)
    include_kitchen: BoolProperty(name="Kitchen", default=True)
    include_dining: BoolProperty(name="Dining Room", default=True)
    include_laundry: BoolProperty(name="Laundry", default=False)
    include_study: BoolProperty(name="Study", default=False)
    include_garage: BoolProperty(name="Garage", default=False)
    custom_rooms: CollectionProperty(type=HF_CustomRoomDefinition)
    generate_room_floors: BoolProperty(name="Room Floor Slabs", default=True)
    show_room_names: BoolProperty(name="Room Names", default=True)
    generate_doorways: BoolProperty(name="Enable Doorway Placement", description="Allow manually placed doorways; no openings are generated automatically", default=False)
    door_width: FloatProperty(name="Door Width", default=0.9, min=0.55, max=1.8, unit='LENGTH')
    door_height: FloatProperty(name="Door Height", default=2.1, min=1.7, max=2.6, unit='LENGTH')
    generate_windows: BoolProperty(name="Enable Window Placement", description="Allow manually placed windows; no openings are generated automatically", default=False)
    window_width: FloatProperty(name="Window Width", default=1.5, min=0.5, max=3.5, unit='LENGTH')
    window_height: FloatProperty(name="Window Height", default=1.1, min=0.4, max=2.0, unit='LENGTH')
    window_sill: FloatProperty(name="Window Sill Height", default=0.9, min=0.2, max=1.8, unit='LENGTH')
    opening_position: FloatProperty(name="Position Along Wall (%)", description="Opening centre measured from the start of the selected wall", default=50.0, min=5.0, max=95.0)


class HF_OpeningDefinition(bpy.types.PropertyGroup):
    kind: EnumProperty(name="Type", items=[('DOOR', "Doorway", "Door opening"), ('WINDOW', "Window", "Window opening")], default='DOOR')
    axis: StringProperty()
    fixed: FloatProperty()
    start: FloatProperty()
    end: FloatProperty()
    position: FloatProperty(default=0.5, min=0.05, max=0.95)
    width: FloatProperty(default=0.9, min=0.3, max=4.0)
    height: FloatProperty(default=2.1, min=0.3, max=4.0)
    sill: FloatProperty(default=0.0, min=0.0, max=4.0)
    wall_key: StringProperty()


class HF_OT_generate_layout(bpy.types.Operator):
    bl_idname = "houseforge.generate_layout"
    bl_label = "Generate Starter Layout"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        collection = bpy.data.collections.get(ROOM_COLLECTION)
        if collection and any(obj.get("houseforge_room") for obj in collection.objects):
            return context.window_manager.invoke_confirm(self, event, title="Create New Starting Plan", message="This replaces the current room footprints. Continue?")
        return self.execute(context)

    def execute(self, context):
        settings = context.scene.houseforge_settings
        context.scene.unit_settings.system = 'METRIC'
        context.scene.unit_settings.length_unit = 'METERS'
        room_program = build_room_program(settings)
        if not room_program:
            self.report({'ERROR'}, "Select at least one room or add a custom room first.")
            return {'CANCELLED'}
        collection = get_or_create_collection(ROOM_COLLECTION)
        clear_collection_objects(collection)
        guide_collection = get_or_create_collection(GUIDE_COLLECTION)
        clear_collection_objects(guide_collection)
        create_layout_guide(guide_collection, settings.house_width, settings.house_depth, settings.layout_shape)
        for name, x0, x1, y0, y1, zone, suite_id in starter_rooms(settings.house_width, settings.house_depth, settings.layout_shape, room_program):
            create_room_footprint(collection, name, x0, x1, y0, y1, zone, suite_id)
        bpy.ops.object.select_all(action='DESELECT')
        for obj in collection.objects:
            obj.select_set(True)
        if collection.objects:
            context.view_layer.objects.active = collection.objects[0]
        self.report({'INFO'}, f"Created {len(collection.objects)} separate room footprints and a {settings.layout_shape} placement guide. Move rooms into the guide, then build walls.")
        return {'FINISHED'}


class HF_OT_add_custom_room(bpy.types.Operator):
    bl_idname = "houseforge.add_custom_room"
    bl_label = "Add Custom Room"
    room_name: StringProperty(name="Room Name", default="Study")
    quantity: IntProperty(name="Count", default=1, min=1, max=12)
    zone: EnumProperty(name="Zone", items=[('PUBLIC', "Public", "Social or shared room"), ('PRIVATE', "Private", "Bedroom, study, or quiet room"), ('MASTER', "Primary Suite", "Room associated with the master bedroom"), ('SERVICE', "Service", "Utility or service room")], default='PRIVATE')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        self.layout.prop(self, "room_name")
        self.layout.prop(self, "quantity")
        self.layout.prop(self, "zone")

    def execute(self, context):
        room_name = self.room_name.strip()
        if not room_name:
            self.report({'ERROR'}, "Enter a name for the custom room.")
            return {'CANCELLED'}
        item = context.scene.houseforge_settings.custom_rooms.add()
        item.room_name = room_name
        item.quantity = self.quantity
        item.zone = self.zone
        return {'FINISHED'}


class HF_OT_remove_custom_room(bpy.types.Operator):
    bl_idname = "houseforge.remove_custom_room"
    bl_label = "Remove Custom Room"
    index: IntProperty()

    def execute(self, context):
        rooms = context.scene.houseforge_settings.custom_rooms
        if 0 <= self.index < len(rooms):
            rooms.remove(self.index)
        return {'FINISHED'}


class HF_OT_import_selected_layout(bpy.types.Operator):
    bl_idname = "houseforge.import_selected_layout"
    bl_label = "Use Selected Objects as Rooms"
    bl_description = "Create Home Model Workshop room footprints from selected mesh objects' world-space bounding boxes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected = [o for o in context.selected_objects if o.type == 'MESH' and o.name not in {"HF_ROOM_"}]
        if not selected:
            self.report({'ERROR'}, "Select one or more mesh objects that represent rooms, then try again.")
            return {'CANCELLED'}
        collection = get_or_create_collection(ROOM_COLLECTION)
        created = 0
        for source in selected:
            x0, x1, y0, y1 = room_bounds(source)
            if x1-x0 < 0.2 or y1-y0 < 0.2:
                continue
            create_room_footprint(collection, source.name, x0, x1, y0, y1)
            created += 1
        if not created:
            self.report({'ERROR'}, "No selected mesh objects had usable room-sized bounds.")
            return {'CANCELLED'}
        self.report({'INFO'}, f"Imported {created} room footprints. Original objects were left untouched.")
        return {'FINISHED'}


class HF_OT_add_room(bpy.types.Operator):
    bl_idname = "houseforge.add_room"
    bl_label = "Add Room to Layout"
    bl_description = "Add a named room footprint while editing the current layout"
    bl_options = {'REGISTER', 'UNDO'}

    room_name: StringProperty(name="Room Name", default="Extra Room")
    room_width: FloatProperty(name="Width", default=4.0, min=0.5, max=30.0, unit='LENGTH')
    room_depth: FloatProperty(name="Depth", default=3.0, min=0.5, max=30.0, unit='LENGTH')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        self.layout.prop(self, "room_name")
        self.layout.prop(self, "room_width")
        self.layout.prop(self, "room_depth")

    def execute(self, context):
        room_name = self.room_name.strip()
        if not room_name:
            self.report({'ERROR'}, "Enter a name for the room.")
            return {'CANCELLED'}
        collection = get_or_create_collection(ROOM_COLLECTION)
        existing = [room_bounds(o) for o in collection.objects if o.get("houseforge_room")]
        start_x = max((b[1] for b in existing), default=0.0) + 0.5
        obj = create_room_footprint(collection, room_name, start_x, start_x + self.room_width, 0.0, self.room_depth)
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        self.report({'INFO'}, f"{room_name} added. Move/resize it, then rebuild the model.")
        return {'FINISHED'}


def touching_edge_rooms(rooms, axis, fixed, start, end):
    """Return rooms whose actual rectangle edge lies on this candidate wall interval."""
    negative, positive = [], []
    for name, b in rooms:
        x0, x1, y0, y1 = b
        if axis == 'V':
            overlap = min(end, y1) - max(start, y0)
            if overlap <= EPS:
                continue
            if abs(x1-fixed) <= EPS:
                negative.append(name)
            if abs(x0-fixed) <= EPS:
                positive.append(name)
        else:
            overlap = min(end, x1) - max(start, x0)
            if overlap <= EPS:
                continue
            if abs(y1-fixed) <= EPS:
                negative.append(name)
            if abs(y0-fixed) <= EPS:
                positive.append(name)
    return negative, positive


def add_wall_with_opening(output, material, name, axis, fixed, start, end, settings, opening=None):
    """Build a wall with zero or more rectangular openings.

    `opening` may be a single legacy tuple or a list of tuples:
    (center, width, bottom, opening_height, kind).
    """
    thickness = settings.wall_thickness
    height = settings.wall_height
    length = end - start
    if length <= EPS:
        return

    def piece(a, b, z0, z1, suffix):
        a, b = max(start, a), min(end, b)
        z0, z1 = max(0.0, z0), min(height, z1)
        if b-a <= EPS or z1-z0 <= EPS:
            return
        if axis == 'V':
            center = (fixed, (a+b)/2, (z0+z1)/2)
            dims = (thickness, b-a, z1-z0)
        else:
            center = ((a+b)/2, fixed, (z0+z1)/2)
            dims = (b-a, thickness, z1-z0)
        make_box(name + suffix, center, dims, output, material)

    if not opening:
        piece(start, end, 0, height, "")
        return

    # Accept both the previous single-opening tuple and the new list format.
    if isinstance(opening, tuple) and len(opening) == 5 and isinstance(opening[0], (int, float)):
        openings = [opening]
    else:
        openings = list(opening) if isinstance(opening, (list, tuple)) else []

    # Clamp openings to the wall and reject horizontal overlaps deterministically.
    valid = []
    for item in sorted(openings, key=lambda op: op[0] - op[1] / 2):
        try:
            center, width, bottom, opening_height, kind = item
            center, width = float(center), float(width)
            bottom, opening_height = float(bottom), float(opening_height)
        except (TypeError, ValueError):
            continue
        left, right = max(start, center-width/2), min(end, center+width/2)
        bottom = max(0.0, bottom)
        top = min(height, bottom+opening_height)
        if right-left <= EPS or top-bottom <= EPS:
            continue
        if valid and left < valid[-1][1] - EPS:
            # Do not create overlapping geometry; keep the first opening and skip this one.
            continue
        valid.append((left, right, bottom, top, kind))

    if not valid:
        piece(start, end, 0, height, "")
        return

    # Fill the wall between opening spans, then add sill/header regions within each span.
    cursor = start
    for index, (left, right, bottom, top, kind) in enumerate(valid, 1):
        piece(cursor, left, 0, height, f"_SPAN_{index:02d}_L")
        if bottom > EPS:
            piece(left, right, 0, bottom, f"_OPEN_{index:02d}_SILL")
        if top < height-EPS:
            piece(left, right, top, height, f"_OPEN_{index:02d}_HEADER")
        cursor = max(cursor, right)
    piece(cursor, end, 0, height, f"_SPAN_{len(valid)+1:02d}_R")


def collect_room_records():
    collection = bpy.data.collections.get(ROOM_COLLECTION)
    records = []
    seen_room_ids = set()
    if not collection:
        return records
    for obj in collection.objects:
        if not obj.get("houseforge_room"):
            continue
        bounds = room_bounds(obj)
        if bounds[1] - bounds[0] <= 0.2 or bounds[3] - bounds[2] <= 0.2:
            continue
        room_id = str(obj.get("hf_room_id", ""))
        if not room_id or room_id in seen_room_ids:
            room_id = "room_" + uuid.uuid4().hex[:12]
            while room_id in seen_room_ids:
                room_id = "room_" + uuid.uuid4().hex[:12]
            obj["hf_room_id"] = room_id
        seen_room_ids.add(room_id)
        records.append({"id": room_id, "name": obj.get("room_name", obj.name.replace('HF_ROOM_', '').replace('_', ' ')), "bounds": bounds, "object": obj})
    return records


def room_overlap_pairs(records):
    """Return room pairs whose world-space footprints intersect by positive area."""
    overlaps = []
    for index, room_a in enumerate(records):
        ax0, ax1, ay0, ay1 = room_a["bounds"]
        for room_b in records[index+1:]:
            bx0, bx1, by0, by1 = room_b["bounds"]
            overlap_x = min(ax1, bx1) - max(ax0, bx0)
            overlap_y = min(ay1, by1) - max(ay0, by0)
            if overlap_x > EPS and overlap_y > EPS:
                overlaps.append((room_a, room_b, overlap_x, overlap_y))
    return overlaps


def show_room_overlap_popup(context, overlaps):
    """Show actionable overlap details in Blender's popup menu."""
    def draw(menu, _context):
        layout = menu.layout
        layout.label(text="Move or resize these room footprints:", icon='ERROR')
        for room_a, room_b, overlap_x, overlap_y in overlaps[:12]:
            layout.label(text=f"{room_a['name']} ({room_a['object'].name}) overlaps {room_b['name']} ({room_b['object'].name})")
            layout.label(text=f"Overlap area: {overlap_x:.2f} x {overlap_y:.2f} m")
        if len(overlaps) > 12:
            layout.label(text=f"And {len(overlaps) - 12} more overlapping pair(s).")
    context.window_manager.popup_menu(draw, title="Cannot Build: Rooms Overlap", icon='ERROR')


def room_records_for_walls(records):
    return [(r["id"], r["bounds"]) for r in records]


def make_wall_segments(room_pairs):
    """Build a unique axis-aligned wall graph from room boundary intervals."""
    bounds_list = [b for _, b in room_pairs]
    xs = unique_sorted([v for b in bounds_list for v in (b[0], b[1])])
    ys = unique_sorted([v for b in bounds_list for v in (b[2], b[3])])
    segments = []
    for x in xs:
        for ya, yb in zip(ys, ys[1:]):
            if yb - ya < 0.02:
                continue
            neg, pos = touching_edge_rooms(room_pairs, 'V', x, ya, yb)
            if neg or pos:
                segments.append(('V', x, ya, yb, bool(neg and pos), tuple(neg), tuple(pos)))
    for y in ys:
        for xa, xb in zip(xs, xs[1:]):
            if xb - xa < 0.02:
                continue
            neg, pos = touching_edge_rooms(room_pairs, 'H', y, xa, xb)
            if neg or pos:
                segments.append(('H', y, xa, xb, bool(neg and pos), tuple(neg), tuple(pos)))
    merged = []
    for axis, fixed, start, end, internal, neg, pos in sorted(segments, key=lambda v:(v[0],v[1],v[4],v[5],v[6],v[2])):
        if merged:
            prev = merged[-1]
            if (prev[0],prev[1],prev[4],prev[5],prev[6]) == (axis,fixed,internal,neg,pos) and abs(prev[3]-start) <= EPS:
                merged[-1] = (*prev[:3], end, *prev[4:])
                continue
        merged.append((axis,fixed,start,end,internal,neg,pos))
    return merged


def find_opening_host(frame, records, segments, settings):
    """Bind a new/unbound frame to the closest wall boundary and store room-side metadata."""
    fb = opening_frame_bounds(frame)
    cx, cy = (fb[0]+fb[1])/2, (fb[2]+fb[3])/2
    axis = frame.get('hf_axis', 'V')
    candidates = []
    tol = max(settings.wall_thickness * 2.0, 0.25)
    for seg in segments:
        saxis, fixed, start, end, internal, neg, pos = seg
        if saxis != axis:
            continue
        along = cy if axis == 'V' else cx
        fixed_coord = cx if axis == 'V' else cy
        if along < start - 0.05 or along > end + 0.05:
            continue
        dist = abs(fixed_coord - fixed)
        if dist > tol:
            continue
        # Prefer a boundary where the clicked frame centre lies on the wall span.
        candidates.append((dist, seg))
    if not candidates:
        return False
    candidates.sort(key=lambda item: item[0])
    seg = candidates[0][1]
    saxis, fixed, start, end, internal, neg, pos = seg
    # Identify which adjacent room owns the side the frame was initially closest to.
    if axis == 'V':
        fixed_coord = cx
        neg_ids, pos_ids = list(neg), list(pos)
        if neg_ids and (not pos_ids or fixed_coord <= fixed):
            host, neighbor, side = neg_ids[0], (pos_ids[0] if pos_ids else ''), 'X_MAX'
        else:
            host, neighbor, side = pos_ids[0], (neg_ids[0] if neg_ids else ''), 'X_MIN'
        along = cy
    else:
        neg_ids, pos_ids = list(neg), list(pos)
        if neg_ids and (not pos_ids or cy <= fixed):
            host, neighbor, side = neg_ids[0], (pos_ids[0] if pos_ids else ''), 'Y_MAX'
        else:
            host, neighbor, side = pos_ids[0], (neg_ids[0] if neg_ids else ''), 'Y_MIN'
        along = cx
    frame['hf_host_room_id'] = host
    frame['hf_host_neighbor_id'] = neighbor
    frame['hf_host_side'] = side
    frame['hf_wall_position'] = max(0.0, min(1.0, (along - start) / max(end - start, EPS)))
    frame['hf_hosted'] = True
    frame['hf_host_axis'] = axis
    frame['hf_host_fixed'] = fixed
    frame['hf_host_start'] = start
    frame['hf_host_end'] = end
    return True


def opening_segment_match(frame, segment):
    axis, fixed, start, end, internal, neg, pos = segment
    if not frame.get('hf_hosted'):
        return False
    if frame.get('hf_host_axis') != axis:
        return False
    host = frame.get('hf_host_room_id', '')
    neighbor = frame.get('hf_host_neighbor_id', '')
    side = frame.get('hf_host_side', '')
    if axis == 'V':
        if side == 'X_MAX':
            return host in neg and (neighbor in pos if neighbor else not pos)
        if side == 'X_MIN':
            return host in pos and (neighbor in neg if neighbor else not neg)
    else:
        if side == 'Y_MAX':
            return host in neg and (neighbor in pos if neighbor else not pos)
        if side == 'Y_MIN':
            return host in pos and (neighbor in neg if neighbor else not neg)
    return False


def opening_frame_bounds(obj):
    pts = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return (min(p.x for p in pts), max(p.x for p in pts),
            min(p.y for p in pts), max(p.y for p in pts),
            min(p.z for p in pts), max(p.z for p in pts))


def create_opening_frame(context, kind, axis, location, settings):
    if kind == 'DOOR':
        width, height, sill = settings.door_width, settings.door_height, 0.0
        label = 'DOOR'
    else:
        width, height, sill = settings.window_width, settings.window_height, settings.window_sill
        label = 'WINDOW'
    # A visible wireframe rectangle with an inner rectangle gives the user a resize/move handle.
    half_w, half_h = width / 2, height / 2
    inset = min(0.08, width * 0.12, height * 0.12)
    if axis == 'V':
        verts = [(0,-half_w,-half_h),(0,half_w,-half_h),(0,half_w,half_h),(0,-half_w,half_h),
                 (0,-half_w+inset,-half_h+inset),(0,half_w-inset,-half_h+inset),
                 (0,half_w-inset,half_h-inset),(0,-half_w+inset,half_h-inset)]
    else:
        verts = [(-half_w,0,-half_h),(half_w,0,-half_h),(half_w,0,half_h),(-half_w,0,half_h),
                 (-half_w+inset,0,-half_h+inset),(half_w-inset,0,-half_h+inset),
                 (half_w-inset,0,half_h-inset),(-half_w+inset,0,half_h-inset)]
    edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4)]
    mesh = bpy.data.meshes.new(f'HF_{label}_Frame_Mesh')
    mesh.from_pydata(verts, edges, [])
    mesh.update()
    obj = bpy.data.objects.new(f'HF_{label}_Frame', mesh)
    context.scene.collection.objects.link(obj)
    obj.location = (location[0], location[1], sill + height/2)
    obj.display_type = 'WIRE'
    obj.show_in_front = True
    obj.color = (0.1, 0.8, 1.0, 1.0) if kind == 'WINDOW' else (1.0, 0.55, 0.1, 1.0)
    obj['houseforge_opening_frame'] = True
    obj['hf_opening_kind'] = kind
    obj['hf_axis'] = axis
    obj['hf_sill'] = sill
    obj['hf_opening_id'] = 'opening_' + uuid.uuid4().hex[:12]
    obj['hf_opening_schema'] = '0.5.4'
    obj['hf_host_room_id'] = ''
    obj['hf_host_neighbor_id'] = ''
    obj['hf_host_side'] = ''
    obj['hf_wall_position'] = 0.5
    obj['hf_hosted'] = False
    return obj


class HF_OT_add_opening(bpy.types.Operator):
    bl_idname = "houseforge.add_opening"
    bl_label = "Place Door / Window Frame"
    bl_description = "Click a wall in the generated house to place a movable and resizable opening frame"
    bl_options = {'REGISTER', 'UNDO'}

    kind: EnumProperty(name="Opening Type", items=[('DOOR', "Doorway", "Place a doorway frame"), ('WINDOW', "Window", "Place a window frame")], default='DOOR')

    def invoke(self, context, event):
        settings = context.scene.houseforge_settings
        if self.kind == 'DOOR' and not settings.generate_doorways:
            self.report({'ERROR'}, "Enable Doorway Placement first.")
            return {'CANCELLED'}
        if self.kind == 'WINDOW' and not settings.generate_windows:
            self.report({'ERROR'}, "Enable Window Placement first.")
            return {'CANCELLED'}
        if context.area.type != 'VIEW_3D':
            self.report({'ERROR'}, "Start placement from the 3D Viewport.")
            return {'CANCELLED'}
        self.report({'INFO'}, "Click a vertical wall face in the generated house to place the frame. Esc cancels.")
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            return {'CANCELLED'}
        if event.type != 'LEFTMOUSE' or event.value != 'PRESS':
            return {'PASS_THROUGH'}
        region = context.region
        rv3d = context.region_data
        if not region or not rv3d:
            return {'PASS_THROUGH'}
        from bpy_extras import view3d_utils
        coord = (event.mouse_region_x, event.mouse_region_y)
        origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        depsgraph = context.evaluated_depsgraph_get()
        hit, loc, normal, face_index, obj, matrix = context.scene.ray_cast(depsgraph, origin, direction)
        if not hit or not obj or not obj.get('houseforge_model'):
            self.report({'WARNING'}, "Click a wall face on the generated Home Model Workshop model.")
            return {'RUNNING_MODAL'}
        world_normal = (matrix.to_3x3() @ normal).normalized()
        if abs(world_normal.z) > 0.35:
            self.report({'WARNING'}, "Click a vertical wall face, not the floor or top of a wall.")
            return {'RUNNING_MODAL'}
        axis = 'V' if abs(world_normal.x) >= abs(world_normal.y) else 'H'
        settings = context.scene.houseforge_settings
        frame = create_opening_frame(context, self.kind, axis, loc, settings)
        # Door frames sit on the floor; window frames are centred at their configured sill height.
        if self.kind == 'DOOR':
            frame.location.z = settings.door_height / 2
        else:
            frame.location.z = settings.window_sill + settings.window_height / 2
        records = collect_room_records()
        if not find_opening_host(frame, records, make_wall_segments(room_records_for_walls(records)), settings):
            self.report({'WARNING'}, "Frame placed, but no matching room boundary was found. It will use legacy position matching until attached to a wall.")
        bpy.ops.object.select_all(action='DESELECT')
        frame.select_set(True)
        context.view_layer.objects.active = frame
        self.report({'INFO'}, f"{self.kind.title()} frame placed. Move/scale it, then rebuild the house model.")
        return {'FINISHED'}


class HF_OT_clear_openings(bpy.types.Operator):
    bl_idname = "houseforge.clear_openings"
    bl_label = "Clear Manual Openings"
    bl_description = "Remove all manually configured door and window openings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.houseforge_openings.clear()
        frames = [o for o in context.scene.objects if o.get("houseforge_opening_frame")]
        for frame in frames:
            bpy.data.objects.remove(frame, do_unlink=True)
        self.report({'INFO'}, f"Removed {len(frames)} opening frames. Rebuild the model to restore solid walls.")
        return {'FINISHED'}


class HF_OT_build_model(bpy.types.Operator):
    bl_idname = "houseforge.build_model"
    bl_label = "Build / Rebuild House Model"
    bl_description = "Rebuild generated geometry from the current room footprint positions and dimensions"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.houseforge_settings
        room_collection = bpy.data.collections.get(ROOM_COLLECTION)
        if not room_collection:
            self.report({'ERROR'}, "Create a starter layout, add a room, or import selected room objects first.")
            return {'CANCELLED'}
        records = collect_room_records()
        rooms = [(r["name"], r["bounds"], r["id"]) for r in records]
        if not rooms:
            self.report({'ERROR'}, "No valid room footprints found in the Home Model Workshop layout collection.")
            return {'CANCELLED'}
        overlaps = room_overlap_pairs(records)
        if overlaps:
            self.report({'ERROR'}, f"Cannot build: {len(overlaps)} overlapping room pair(s). Adjust the footprints and try again.")
            show_room_overlap_popup(context, overlaps)
            return {'CANCELLED'}

        # Clear and recreate output every time, so rebuilding always reflects current room transforms.
        output = get_or_create_collection(MODEL_COLLECTION)
        clear_collection_objects(output)
        floor_mat = make_material("HF_Floor_Material", (0.42, 0.34, 0.25))
        wall_mat = make_material("HF_Wall_Material", (0.78, 0.76, 0.70))
        label_mat = make_material("HF_Label_Material", (0.08, 0.08, 0.08))
        bounds_list = [b for _, b, _rid in rooms]
        room_id_pairs = [(rid, bounds) for _name, bounds, rid in rooms]
        if not settings.project_id:
            settings.project_id = "house_" + uuid.uuid4().hex[:12]

        if settings.generate_room_floors:
            for idx, (name, (x0,x1,y0,y1), _rid) in enumerate(rooms, 1):
                make_box(f"HF_Floor_{idx:03d}_{name.replace(' ', '_')}", ((x0+x1)/2, (y0+y1)/2, -settings.floor_thickness/2), (x1-x0, y1-y0, settings.floor_thickness), output, floor_mat)

        # Build one unique wall graph from stable room IDs and shared boundaries.
        merged = make_wall_segments(room_id_pairs)

        placed_door_count = 0
        placed_window_count = 0
        opening_frames = [o for o in context.scene.objects if o.get("houseforge_opening_frame")]
        # Duplicating a Blender object copies its custom properties. Give copied guides
        # independent IDs, then refresh each guide's host from its current world-space
        # position when it is actually sitting on a wall. If it is off-wall, retain its
        # previous host metadata so it can still follow a wall that moved during editing.
        seen_opening_ids = set()
        for frame in opening_frames:
            opening_id = frame.get("hf_opening_id", "")
            if not opening_id or opening_id in seen_opening_ids:
                opening_id = "opening_" + uuid.uuid4().hex[:12]
                while opening_id in seen_opening_ids:
                    opening_id = "opening_" + uuid.uuid4().hex[:12]
                frame["hf_opening_id"] = opening_id
            frame["hf_opening_schema"] = "0.5.4"
            seen_opening_ids.add(opening_id)
            find_opening_host(frame, records, merged, settings)
        used_frames = set()
        for idx, (axis, fixed, start, end, internal, neg, pos) in enumerate(merged, 1):
            length = end-start
            wall_key = f"{axis}|{fixed:.4f}|{start:.4f}|{end:.4f}|{'I' if internal else 'E'}"
            wall_openings = []
            for frame in opening_frames:
                if frame.name in used_frames:
                    continue
                kind = frame.get('hf_opening_kind', 'DOOR')
                fb = opening_frame_bounds(frame)
                frame_axis = frame.get('hf_axis', 'V')
                if frame.get('hf_hosted'):
                    if not opening_segment_match(frame, (axis, fixed, start, end, internal, neg, pos)):
                        continue
                    frame_width = fb[3]-fb[2] if axis == 'V' else fb[1]-fb[0]
                    frame_height = fb[5]-fb[4]
                    sill = fb[4]
                    current_center = ((fb[2]+fb[3])/2) if axis == 'V' else ((fb[0]+fb[1])/2)
                    current_fixed = ((fb[0]+fb[1])/2) if axis == 'V' else ((fb[2]+fb[3])/2)
                    # If the guide is still on this wall, honour the user's manual move.
                    # If the wall moved away from the guide, preserve the stored relative position.
                    still_on_wall = abs(current_fixed-fixed) <= max(settings.wall_thickness*1.5, 0.12)
                    fits_current_position = current_center-frame_width/2 >= start-EPS and current_center+frame_width/2 <= end+EPS
                    if still_on_wall and fits_current_position:
                        frame_center = current_center
                        position = (frame_center-start) / max(end-start, EPS)
                        frame['hf_wall_position'] = max(0.0, min(1.0, position))
                    else:
                        position = float(frame.get('hf_wall_position', 0.5))
                        frame_center = start + max(0.0, min(1.0, position)) * (end-start)
                    # Do not assign frame.location from the wall coordinates. The object
                    # origin can differ from the evaluated bounding-box centre, especially
                    # after users move/scale frames or duplicate them. That direct assignment
                    # caused subsequent guides to jump toward (0, 0, 0).
                    # Keep the guide exactly where the user put it while its host wall is
                    # unchanged. If the wall has moved, translate by the delta between the
                    # desired and evaluated centres instead of overwriting the origin.
                    previous_fixed = float(frame.get('hf_host_fixed', fixed))
                    previous_start = float(frame.get('hf_host_start', start))
                    previous_end = float(frame.get('hf_host_end', end))
                    host_changed = (abs(previous_fixed-fixed) > EPS or
                                    abs(previous_start-start) > EPS or
                                    abs(previous_end-end) > EPS)
                    if host_changed or not still_on_wall:
                        if axis == 'V':
                            current_obj_center = (fb[2] + fb[3]) / 2
                            frame.location.x += fixed - current_fixed
                            frame.location.y += frame_center - current_obj_center
                        else:
                            current_obj_center = (fb[0] + fb[1]) / 2
                            frame.location.y += fixed - current_fixed
                            frame.location.x += frame_center - current_obj_center
                    frame['hf_host_fixed'] = fixed
                    frame['hf_host_start'] = start
                    frame['hf_host_end'] = end
                else:
                    cx, cy = (fb[0]+fb[1])/2, (fb[2]+fb[3])/2
                    frame_fixed = cx if frame_axis == 'V' else cy
                    frame_start, frame_end = (fb[2], fb[3]) if axis == 'V' else (fb[0], fb[1])
                    frame_width = frame_end-frame_start
                    sill = fb[4]
                    frame_height = fb[5]-fb[4]
                    frame_center = (frame_start+frame_end)/2
                    if frame_axis != axis or abs(frame_fixed-fixed) > max(settings.wall_thickness*1.5, 0.12):
                        continue
                    if frame_center-frame_width/2 < start-EPS or frame_center+frame_width/2 > end+EPS:
                        continue
                if frame_width <= 0.05 or frame_height <= 0.05 or frame_width > (end-start)+EPS:
                    continue
                if kind == 'DOOR' and sill <= 0.15 and frame_height < settings.wall_height:
                    wall_openings.append((frame_center, frame_width, 0.0, frame_height, 'DOOR'))
                    placed_door_count += 1
                    used_frames.add(frame.name)
                    continue
                if kind == 'WINDOW' and sill >= 0 and sill+frame_height < settings.wall_height:
                    wall_openings.append((frame_center, frame_width, sill, frame_height, 'WINDOW'))
                    placed_window_count += 1
                    used_frames.add(frame.name)
                    continue
            # Multiple guides may share a wall. Reject overlapping spans and release their
            # frames so validation can report them instead of silently consuming them.
            wall_openings.sort(key=lambda op: op[0] - op[1] / 2)
            non_overlapping = []
            rejected_openings = 0
            for op in wall_openings:
                left, right = op[0] - op[1]/2, op[0] + op[1]/2
                if non_overlapping and left < non_overlapping[-1][0] + non_overlapping[-1][1]/2 - EPS:
                    rejected_openings += 1
                    continue
                non_overlapping.append(op)
            if rejected_openings:
                self.report({'WARNING'}, f"Skipped {rejected_openings} overlapping opening(s) on wall {idx}.")
            placed_door_count -= sum(1 for op in wall_openings if op not in non_overlapping and op[4] == 'DOOR')
            placed_window_count -= sum(1 for op in wall_openings if op not in non_overlapping and op[4] == 'WINDOW')
            before = set(output.objects)
            add_wall_with_opening(output, wall_mat, f"HF_Wall_{idx:03d}", axis, fixed, start, end, settings, non_overlapping)
            for wall_obj in (set(output.objects) - before):
                wall_obj["houseforge_wall"] = True
                wall_obj["hf_wall_key"] = wall_key
                wall_obj["hf_axis"] = axis
                wall_obj["hf_fixed"] = fixed
                wall_obj["hf_start"] = start
                wall_obj["hf_end"] = end
                wall_obj["hf_internal"] = internal
                wall_obj["hf_room_ids_negative"] = ",".join(neg)
                wall_obj["hf_room_ids_positive"] = ",".join(pos)

        if settings.show_room_names:
            for idx, (name, (x0,x1,y0,y1), _rid) in enumerate(rooms, 1):
                curve = bpy.data.curves.new(f"HF_LabelCurve_{idx:03d}", 'FONT')
                curve.body = name
                curve.size = min(0.32, max(0.16, (x1-x0)/max(8, len(name)*1.3)))
                curve.align_x = 'CENTER'
                curve.align_y = 'CENTER'
                label = bpy.data.objects.new(f"HF_Label_{idx:03d}", curve)
                output.objects.link(label)
                label.location = ((x0+x1)/2, (y0+y1)/2, 0.04)
                label.data.materials.append(label_mat)
                label["houseforge_generated"] = True

        # Consolidate all generated house geometry (including labels converted to mesh) into one mesh object.
        generated = list(output.objects)
        bpy.ops.object.select_all(action='DESELECT')
        for obj in generated:
            if obj.type == 'CURVE':
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.convert(target='MESH')
                obj.select_set(False)
        generated = [obj for obj in list(output.objects) if obj.type == 'MESH']
        if generated:
            bpy.ops.object.select_all(action='DESELECT')
            for obj in generated:
                obj.select_set(True)
            context.view_layer.objects.active = generated[0]
            bpy.ops.object.join()
            model = context.view_layer.objects.active
            model.name = 'HF_House_Model'
            model.data.name = 'HF_House_Model_Mesh'
            model['houseforge_model'] = True
            model['houseforge_generated'] = True
            model['hf_project_id'] = settings.project_id
            model['hf_schema_version'] = '0.5.0'
        # Keep opening frames separate so users can move/scale them before rebuilding.
        bpy.ops.object.select_all(action='DESELECT')
        model = bpy.data.objects.get('HF_House_Model')
        if model:
            model.select_set(True)
            context.view_layer.objects.active = model
        self.report({'INFO'}, f"Rebuilt from {len(rooms)} rooms: {len(merged)} unique wall segments, {placed_door_count} doorways and {placed_window_count} windows. House geometry is one mesh.")
        return {'FINISHED'}


class HF_OT_validate_project(bpy.types.Operator):
    bl_idname = "houseforge.validate_project"
    bl_label = "Validate House Project"
    bl_description = "Check room footprints and opening guides before rebuilding or exporting"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.houseforge_settings
        records = collect_room_records()
        errors, warnings = [], []
        if not records:
            errors.append("No valid room footprints found.")
        ids = [r["id"] for r in records]
        if len(ids) != len(set(ids)):
            errors.append("Duplicate room IDs detected.")
        overlaps = room_overlap_pairs(records)
        for room_a, room_b, overlap_x, overlap_y in overlaps:
            errors.append(f"Rooms '{room_a['name']}' and '{room_b['name']}' overlap ({overlap_x:.2f} x {overlap_y:.2f} m).")
        for frame in [o for o in context.scene.objects if o.get('houseforge_opening_frame')]:
            fb = opening_frame_bounds(frame)
            width = (fb[3]-fb[2]) if frame.get('hf_axis') == 'V' else (fb[1]-fb[0])
            height = fb[5]-fb[4]
            if width <= 0.05 or height <= 0.05:
                warnings.append(f"Opening frame '{frame.name}' has invalid dimensions.")
            if frame.get('hf_hosted') and frame.get('hf_host_room_id') not in ids:
                warnings.append(f"Opening frame '{frame.name}' references a missing room.")
        for message in errors:
            self.report({'ERROR'}, message)
        if overlaps:
            show_room_overlap_popup(context, overlaps)
        for message in warnings[:4]:
            self.report({'WARNING'}, message)
        if not errors and not warnings:
            self.report({'INFO'}, f"Validation passed: {len(records)} rooms and {len([o for o in context.scene.objects if o.get('houseforge_opening_frame')])} opening guides.")
        elif not errors:
            self.report({'WARNING'}, f"Validation found {len(warnings)} warning(s). See the operator report.")
        return {'CANCELLED'} if errors else {'FINISHED'}


class HF_OT_clear_model(bpy.types.Operator):
    bl_idname = "houseforge.clear_model"
    bl_label = "Clear Generated Model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        clear_collection_objects(bpy.data.collections.get(MODEL_COLLECTION))
        self.report({'INFO'}, "Generated model cleared. Room layout was preserved.")
        return {'FINISHED'}


class HF_PT_main_panel(bpy.types.Panel):
    bl_label = "Home Model Workshop"
    bl_idname = "HF_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Home Model Workshop"

    def section(self, layout, settings, property_name, title):
        is_open = getattr(settings, property_name)
        box = layout.box()
        row = box.row(align=True)
        row.prop(settings, property_name, text=title,
                 icon='DISCLOSURE_TRI_DOWN' if is_open else 'DISCLOSURE_TRI_RIGHT',
                 emboss=False, toggle=True)
        return box.column(align=True) if is_open else None

    def draw(self, context):
        layout = self.layout
        settings = context.scene.houseforge_settings
        body = self.section(layout, settings, "ui_show_help", "Quick Start & Help")
        if body:
            body.label(text="1. Choose dimensions, a guide shape, and the rooms you need.")
            body.label(text="2. Create the plan, then move and resize each room footprint.")
            body.label(text="3. Validate. Overlaps block the build; open gaps are allowed.")
            body.label(text="4. Build the model. Shared room edges produce one wall.")
            body.label(text="5. Add door/window frames, then rebuild to apply openings.")
            body.separator()
            body.label(text="The shape guide is visual only; footprints control walls and floors.")
            body.label(text="Hallways are manual rooms. Add one in Custom Room Program.")
            body.label(text="Use axis-aligned rectangular room footprints.")

        body = self.section(layout, settings, "ui_show_house_settings", "House & Construction")
        if body:
            body.prop(settings, "workflow", text="Workflow")
            body.label(text="House Dimensions (metres)")
            body.prop(settings, "house_width")
            body.prop(settings, "house_depth")
            body.label(text="Construction")
            body.prop(settings, "wall_height")
            body.prop(settings, "wall_thickness")
            body.prop(settings, "floor_thickness")

        body = self.section(layout, settings, "ui_show_room_plan", "Room Selection & Starting Guide")
        if body:
            body.prop(settings, "layout_shape")
            body.prop(settings, "include_entry")
            body.prop(settings, "bedroom_count")
            body.prop(settings, "bathroom_count")
            suite_col = body.column()
            suite_col.enabled = settings.bedroom_count > 0
            suite_col.prop(settings, "include_ensuite")
            suite_col.prop(settings, "include_wir")
            for prop_name in ("include_living", "include_kitchen", "include_dining", "include_laundry", "include_study", "include_garage"):
                body.prop(settings, prop_name)
            body.operator("houseforge.generate_layout", text="Create Rooms & Shape Guide", icon='MESH_GRID')
            body.label(text="Rooms start separated. Place them within the guide.")
            body.label(text="The guide is visual only; walls follow room footprints.")
            body.operator("houseforge.add_room", text="Add Room to Layout", icon='ADD')

        body = self.section(layout, settings, "ui_show_custom_rooms", "Custom Room Program")
        if body:
            for index, room in enumerate(settings.custom_rooms):
                row = body.row(align=True)
                row.prop(room, "room_name", text="")
                row.prop(room, "quantity", text="Count")
                row.prop(room, "zone", text="")
                remove = row.operator("houseforge.remove_custom_room", text="", icon='X')
                remove.index = index
            body.operator("houseforge.add_custom_room", text="Add to generated room list", icon='ADD')

        body = self.section(layout, settings, "ui_show_import_layout", "Import Existing Layout")
        if body:
            body.operator("houseforge.import_selected_layout", text="Use Selected Objects as Rooms", icon='IMPORT')
            body.label(text="Select mesh room blocks first to import.")

        body = self.section(layout, settings, "ui_show_model_output", "Model Output")
        if body:
            body.prop(settings, "generate_room_floors")
            body.prop(settings, "show_room_names")
            body.operator("houseforge.build_model", icon='FILE_REFRESH')
            body.operator("houseforge.validate_project", icon='CHECKMARK')
            body.operator("houseforge.clear_model", icon='TRASH')
            body.separator()
            body.label(text="Gaps stay open; shared edges create one wall.")
            body.label(text="Overlapping rooms block the build.")
            body.label(text="Room footprints must stay axis-aligned.")

        body = self.section(layout, settings, "ui_show_openings", "Doors & Windows")
        if body:
            body.label(text="Place editable frames on walls; openings apply on rebuild.")
            body.prop(settings, "generate_doorways")
            sub = body.column(align=True)
            sub.enabled = settings.generate_doorways
            sub.prop(settings, "door_width")
            sub.prop(settings, "door_height")
            body.separator()
            body.prop(settings, "generate_windows")
            sub = body.column(align=True)
            sub.enabled = settings.generate_windows
            sub.prop(settings, "window_width")
            sub.prop(settings, "window_height")
            sub.prop(settings, "window_sill")
            body.separator()
            row = body.row(align=True)
            op = row.operator("houseforge.add_opening", text="Place Door Frame", icon='MOD_BOOLEAN')
            op.kind = 'DOOR'
            op = row.operator("houseforge.add_opening", text="Place Window Frame", icon='WINDOW')
            op.kind = 'WINDOW'
            body.operator("houseforge.clear_openings", text="Remove All Frames", icon='TRASH')
            body.label(text="Click a vertical wall face, then move/scale the frame.")
            body.label(text="Window size is set above before placement.")


classes = (HF_OpeningDefinition, HF_CustomRoomDefinition, HF_Settings, HF_OT_generate_layout, HF_OT_add_custom_room,
           HF_OT_remove_custom_room, HF_OT_import_selected_layout, HF_OT_add_room,
           HF_OT_add_opening, HF_OT_clear_openings, HF_OT_build_model, HF_OT_validate_project, HF_OT_clear_model, HF_PT_main_panel)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.houseforge_settings = PointerProperty(type=HF_Settings)
    bpy.types.Scene.houseforge_openings = CollectionProperty(type=HF_OpeningDefinition)


def unregister():
    if hasattr(bpy.types.Scene, "houseforge_settings"):
        del bpy.types.Scene.houseforge_settings
    if hasattr(bpy.types.Scene, "houseforge_openings"):
        del bpy.types.Scene.houseforge_openings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
