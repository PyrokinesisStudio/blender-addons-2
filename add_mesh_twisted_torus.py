# add_mesh_twisted_torus.py Copyright (C) 2009-2010, Paulo Gomes
#
# add twisted torus to the blender 2.50 add->mesh menu
# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****

bl_addon_info = {
    'name': 'Add Mesh: Twisted Torus',
    'author': 'Paulo_Gomes',
    'version': '0.10',
    'blender': (2, 5, 3),
    'location': 'View3D > Add > Mesh ',
    'description': 'Adds a mesh Twisted Torus to the Add Mesh menu',
    'url': 'http://wiki.blender.org/index.php/Extensions:2.5/Py/' \
	    'Scripts/Add_Mesh/Add_Twisted_Torus',
    'category': 'Add Mesh'}


"""
Name: 'Twisted Torus'
Blender: 250
Group: 'AddMesh'
Tip: 'Add a Twisted Torus Object...'
__author__ = ["Paulo_Gomes"]
__version__ = '0.10'
__url__ = [
    ""]
email__=["tuga3d {at} gmail {dot} com"]

Usage:

* Launch from Add Mesh menu

* Modify parameters as desired or keep defaults

"""


import bpy
import mathutils
from math import cos, sin, pi


def add_twisted_torus(major_rad, minor_rad, major_seg, minor_seg, twists):
    Vector = mathutils.Vector
    Quaternion = mathutils.Quaternion

    PI_2 = pi * 2
    z_axis = (0, 0, 1)

    verts = []
    faces = []
    i1 = 0
    tot_verts = major_seg * minor_seg
    for major_index in range(major_seg):
        quat = Quaternion(z_axis, (major_index / major_seg) * PI_2)
        rot_twists = 2 * pi * major_index / major_seg * twists

        for minor_index in range(minor_seg):
            angle = (2 * pi * minor_index / minor_seg) + rot_twists

            vec = Vector(major_rad + (cos(angle) * minor_rad), 0.0,
                        (sin(angle) * minor_rad)) * quat

            verts.extend([vec.x, vec.y, vec.z])

            if minor_index + 1 == minor_seg:
                i2 = (major_index) * minor_seg
                i3 = i1 + minor_seg
                i4 = i2 + minor_seg

            else:
                i2 = i1 + 1
                i3 = i1 + minor_seg
                i4 = i3 + 1

            if i2 >= tot_verts:
                i2 = i2 - tot_verts
            if i3 >= tot_verts:
                i3 = i3 - tot_verts
            if i4 >= tot_verts:
                i4 = i4 - tot_verts

            # stupid eekadoodle
            if i2:
                faces.extend([i1, i3, i4, i2])
            else:
                faces.extend([i2, i1, i3, i4])

            i1 += 1

    return verts, faces

from bpy.props import *


class AddTwistedTorus(bpy.types.Operator):
    '''Add a torus mesh'''
    bl_idname = "mesh.primitive_twisted_torus_add"
    bl_label = "Add Torus"
    bl_options = {'REGISTER', 'UNDO'}

    major_radius = FloatProperty(name="Major Radius",
    description="Radius from the origin to the center of the cross section",
    default=1.0, min=0.01, max=100.0)

    minor_radius = FloatProperty(name="Minor Radius",
    description="Radius of the torus' cross section",
    default=0.25, min=0.01, max=100.0)

    major_segments = IntProperty(name="Major Segments",
    description="Number of segments for the main ring of the torus",
    default=48, min=3, max=256)

    minor_segments = IntProperty(name="Minor Segments",
    description="Number of segments for the minor ring of the torus",
    default=12, min=3, max=256)

    twists = IntProperty(name="Twists",
    description="Number of twists of the torus",
    default=0, min=0, max=10)

    use_abso = BoolProperty(name="Use Int+Ext Controls",
    description="Use the Int / Ext controls for torus dimensions",
    default=False)

    abso_major_rad = FloatProperty(name="Exterior Radius",
    description="Total Exterior Radius of the torus",
    default=1.0, min=0.01, max=100.0)

    abso_minor_rad = FloatProperty(name="Inside Radius",
    description="Total Interior Radius of the torus",
    default=0.5, min=0.01, max=100.0)

    def execute(self, context):
        props = self.properties

        if props.use_abso == True:
            extra_helper = (props.abso_major_rad - props.abso_minor_rad) * 0.5
            props.major_radius = props.abso_minor_rad + extra_helper
            props.minor_radius = extra_helper

        verts_loc, faces = add_twisted_torus(props.major_radius,
                                            props.minor_radius,
                                            props.major_segments,
                                            props.minor_segments,
                                            props.twists)

        mesh = bpy.data.meshes.new("TwistedTorus")

        mesh.add_geometry(int(len(verts_loc) / 3), 0, int(len(faces) / 4))
        mesh.verts.foreach_set("co", verts_loc)
        mesh.faces.foreach_set("verts_raw", faces)
        mesh.faces.foreach_set("smooth", [False] * len(mesh.faces))

        scene = context.scene

        # ugh
        for ob in scene.objects:
            ob.selected = False

        mesh.update()
        ob_new = bpy.data.objects.new("TwistedTorus", mesh)
        scene.objects.link(ob_new)
        ob_new.selected = True

        ob_new.location = scene.cursor_location

        obj_act = scene.objects.active

        if obj_act and obj_act.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')

            obj_act.selected = True
            scene.update()  # apply location
            #scene.objects.active = ob_new

            bpy.ops.object.join()  # join into the active.

            bpy.ops.object.mode_set(mode='EDIT')
        else:
            scene.objects.active = ob_new
            if context.user_preferences.edit.enter_edit_mode:
                bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}


# Add to the menu
menu_func = (lambda self,
            context: self.layout.operator(AddTwistedTorus.bl_idname,
            text="TwistedTorus", icon='MESH_DONUT'))


def register():
    bpy.types.register(AddTwistedTorus)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.types.unregister(AddTwistedTorus)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()
