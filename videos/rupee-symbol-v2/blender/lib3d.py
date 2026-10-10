"""Shared Blender helpers for the ₹ Short v2: materials, primitives, stylised figures,
teal mannequins, cameras with depth of field. Scene builders live in scenes_v2.py."""
import argparse
import math
import os
import random
import sys

import bpy  # noqa: I001  (bpy must load before bmesh)
import bmesh
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import textures  # noqa: E402

FPS = 24
DUR = {}  # filled by scenes_v2.py
QUALITY = {}  # filled by scenes_v2.py
FONT_DEVA = os.path.join(textures.FONTS, "NotoSansDevanagari-Bold.ttf")
FONT_DEVA_REG = os.path.join(textures.FONTS, "NotoSansDevanagari-Regular.ttf")
FONT_INTER = os.path.join(textures.FONTS, "Inter-Regular.otf")
TEX = {}
R = math.radians


# ---------------------------------------------------------------- materials

_MATS = {}


def _nodes(m):
    if m.node_tree is None:
        m.use_nodes = True
    return m.node_tree.nodes, m.node_tree.links


def mat(name, color, rough=0.5, metal=0.0, emit=None, emit_strength=0.0, alpha=1.0):
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    nodes, _ = _nodes(m)
    b = nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit is not None:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = emit_strength
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
    m.diffuse_color = (*color, 1)
    _MATS[name] = m
    return m


def img_mat(name, key, emit_strength=0.25, rough=0.6, repeat=None):
    """Image-textured material. Returns (material, emission-strength socket)."""
    m = bpy.data.materials.new(name)
    nodes, links = _nodes(m)
    b = nodes.get("Principled BSDF")
    t = nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(TEX[key], check_existing=True)
    if repeat:
        tc = nodes.new("ShaderNodeTexCoord")
        mp = nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (*repeat, 1)
        links.new(tc.outputs["UV"], mp.inputs["Vector"])
        links.new(mp.outputs["Vector"], t.inputs["Vector"])
    links.new(t.outputs["Color"], b.inputs["Base Color"])
    links.new(t.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = emit_strength
    b.inputs["Roughness"].default_value = rough
    return m, b.inputs["Emission Strength"]


def noisy_mat(name, c1, c2, scale=8.0, rough=0.8, bump=0.3):
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    nodes, links = _nodes(m)
    b = nodes.get("Principled BSDF")
    n = nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = 6
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*c1, 1)
    ramp.color_ramp.elements[1].color = (*c2, 1)
    links.new(n.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    bp = nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = bump
    links.new(n.outputs["Fac"], bp.inputs["Height"])
    links.new(bp.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Roughness"].default_value = rough
    _MATS[name] = m
    return m


def checker_mat(name, c1, c2, scale=6.0, rough=0.4):
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    nodes, links = _nodes(m)
    b = nodes.get("Principled BSDF")
    c = nodes.new("ShaderNodeTexChecker")
    c.inputs["Color1"].default_value = (*c1, 1)
    c.inputs["Color2"].default_value = (*c2, 1)
    c.inputs["Scale"].default_value = scale
    links.new(c.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    _MATS[name] = m
    return m


def reveal_mat(name, color, emit=None):
    """Material with an animated left→right wipe and an opacity control.
    Returns (material, threshold value socket, opacity value socket, emission strength socket)."""
    m = bpy.data.materials.new(name)
    nodes, links = _nodes(m)
    b = nodes.get("Principled BSDF")
    out = nodes.get("Material Output")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = 0.7
    b.inputs["Emission Color"].default_value = (*(emit or color), 1)
    b.inputs["Emission Strength"].default_value = 0.0
    tc = nodes.new("ShaderNodeTexCoord")
    sep = nodes.new("ShaderNodeSeparateXYZ")
    links.new(tc.outputs["Object"], sep.inputs["Vector"])
    thr = nodes.new("ShaderNodeValue")
    lt = nodes.new("ShaderNodeMath")
    lt.operation = "LESS_THAN"
    links.new(sep.outputs["X"], lt.inputs[0])
    links.new(thr.outputs[0], lt.inputs[1])
    op = nodes.new("ShaderNodeValue")
    op.outputs[0].default_value = 1.0
    mul = nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    links.new(lt.outputs[0], mul.inputs[0])
    links.new(op.outputs[0], mul.inputs[1])
    tr = nodes.new("ShaderNodeBsdfTransparent")
    mix = nodes.new("ShaderNodeMixShader")
    links.new(mul.outputs[0], mix.inputs["Fac"])
    links.new(tr.outputs[0], mix.inputs[1])
    links.new(b.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], out.inputs["Surface"])
    try:
        m.surface_render_method = "BLENDED"
    except Exception:
        pass
    return m, thr.outputs[0], op.outputs[0], b.inputs["Emission Strength"]


def key_socket(sock, frame, value):
    sock.default_value = value
    sock.keyframe_insert("default_value", frame=frame)


# ---------------------------------------------------------------- geometry

def _finish(name, me, material, coll, parent=None, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1),
            smooth=True, bevel=0.0):
    if smooth:
        me.shade_smooth()
        try:
            me.set_sharp_from_angle(angle=R(40))
        except Exception:
            pass
    ob = bpy.data.objects.new(name, me)
    if material:
        ob.data.materials.append(material)
    coll.objects.link(ob)
    ob.parent = parent
    ob.location, ob.rotation_euler, ob.scale = loc, [R(a) for a in rot], scale
    if bevel:
        md = ob.modifiers.new("bevel", "BEVEL")
        md.width, md.segments, md.limit_method = bevel, 3, "ANGLE"
    return ob


def box(coll, name, size, loc=(0, 0, 0), material=None, parent=None, rot=(0, 0, 0), bevel=0.0):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(me)
    bm.free()
    return _finish(name, me, material, coll, parent, loc, rot, size, bevel=bevel)


def sphere(coll, name, r, loc=(0, 0, 0), material=None, parent=None, scale=(1, 1, 1), rot=(0, 0, 0), seg=32):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=r)
    bm.to_mesh(me)
    bm.free()
    return _finish(name, me, material, coll, parent, loc, rot, scale)


def cyl(coll, name, r1, r2, depth, loc=(0, 0, 0), material=None, parent=None, rot=(0, 0, 0), seg=24,
        scale=(1, 1, 1)):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r1, radius2=r2, depth=depth)
    bm.to_mesh(me)
    bm.free()
    return _finish(name, me, material, coll, parent, loc, rot, scale)


def crumple(coll, name, r, loc, material, seed):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
    rnd = random.Random(seed)
    for v in bm.verts:
        v.co *= rnd.uniform(0.7, 1.15)
    bm.to_mesh(me)
    bm.free()
    return _finish(name, me, material, coll, None, loc, (rnd.uniform(0, 90),) * 3, smooth=False)


def plane(coll, name, w, h, loc=(0, 0, 0), material=None, parent=None, rot=(0, 0, 0), horizontal=False):
    """Vertical plane in XZ facing -Y (or horizontal in XY facing +Z), UV 0..1."""
    me = bpy.data.meshes.new(name)
    if horizontal:
        verts = [(-w / 2, -h / 2, 0), (w / 2, -h / 2, 0), (w / 2, h / 2, 0), (-w / 2, h / 2, 0)]
    else:
        verts = [(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)]
    me.from_pydata(verts, [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for i, c in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[i].uv = c
    return _finish(name, me, material, coll, parent, loc, rot, smooth=False)


def img_plane(coll, name, key, width, loc=(0, 0, 0), parent=None, rot=(0, 0, 0), horizontal=False,
              emit=0.25, rough=0.6):
    from PIL import Image
    w_px, h_px = Image.open(TEX[key]).size
    m, es = img_mat(name + "_m", key, emit, rough)
    ob = plane(coll, name, width, width * h_px / w_px, loc, m, parent, rot, horizontal)
    return ob, es


def text(coll, name, body, size, loc=(0, 0, 0), material=None, rot=(0, 0, 0), font=FONT_DEVA, extrude=0.0,
         parent=None):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.font = bpy.data.fonts.load(font, check_existing=True)
    cu.size, cu.extrude = size, extrude
    cu.align_x, cu.align_y = "CENTER", "CENTER"
    ob = bpy.data.objects.new(name, cu)
    if material:
        ob.data.materials.append(material)
    coll.objects.link(ob)
    ob.parent = parent
    ob.location, ob.rotation_euler = loc, [R(a) for a in rot]
    return ob


def empty(coll, name, loc=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.05
    coll.objects.link(e)
    e.parent = parent
    e.location = loc
    return e


def arc(coll, name, pts, material, parent, depth=0.006):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth, cu.bevel_resolution = depth, 2
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts):
        p.co = (*c, 1)
    ob = bpy.data.objects.new(name, cu)
    ob.data.materials.append(material)
    coll.objects.link(ob)
    ob.parent = parent
    return ob


def key(ob, frame, loc=None, rot=None, scale=None):
    if loc is not None:
        ob.location = loc
        ob.keyframe_insert("location", frame=frame)
    if rot is not None:
        ob.rotation_euler = [R(a) for a in rot]
        ob.keyframe_insert("rotation_euler", frame=frame)
    if scale is not None:
        ob.scale = scale if hasattr(scale, "__len__") else (scale,) * 3
        ob.keyframe_insert("scale", frame=frame)


def aim(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


# ---------------------------------------------------------------- figure

SKIN_TONES = [(0.26, 0.13, 0.07), (0.36, 0.2, 0.11), (0.2, 0.1, 0.055), (0.45, 0.27, 0.16)]


def figure(coll, name, shirt, pants, skin=SKIN_TONES[0], hair=(0.03, 0.025, 0.02), glasses=True,
           jacket=None, long_kurta=False, shoes=(0.12, 0.07, 0.04), bald=False, faceless=False):
    """Stylised figure, ~1.75 tall, feet at root origin, facing -Y. Returns dict of joint empties."""
    J = {}
    m_skin = mat(f"skin{skin}", skin, 0.45)
    m_pants = pants if isinstance(pants, bpy.types.Material) else mat(f"cloth{pants}", pants, 0.8)
    m_shirt = shirt if isinstance(shirt, bpy.types.Material) else mat(f"cloth{shirt}", shirt, 0.75)
    m_dark = mat("eye_black", (0.01, 0.01, 0.012), 0.15)
    m_hair = mat(f"hair{hair}", hair, 0.55)
    m_shoe = mat(f"shoe{shoes}", shoes, 0.4)
    m_lip = mat("lip", (0.25, 0.08, 0.06), 0.4)
    m_white = mat("eye_white", (0.92, 0.92, 0.9), 0.3)

    root = J["root"] = empty(coll, name + "_root")
    pelvis = J["pelvis"] = empty(coll, name + "_pelvis", (0, 0, 0.95), root)
    box(coll, name + "_hipblock", (0.36, 0.22, 0.18), (0, 0, 0.0), m_pants, pelvis, bevel=0.05)
    for side, sx in (("L", 1), ("R", -1)):
        hip = J["hip" + side] = empty(coll, f"{name}_hip{side}", (0.10 * sx, 0, -0.02), pelvis)
        cyl(coll, f"{name}_thigh{side}", 0.07, 0.078, 0.46, (0, 0, -0.23), m_pants, hip)
        knee = J["knee" + side] = empty(coll, f"{name}_knee{side}", (0, 0, -0.46), hip)
        cyl(coll, f"{name}_shin{side}", 0.05, 0.065, 0.44, (0, 0, -0.22), m_pants, knee)
        box(coll, f"{name}_shoe{side}", (0.11, 0.24, 0.08), (0, -0.05, -0.46), m_shoe, knee, bevel=0.03)

    spine = J["spine"] = empty(coll, name + "_spine", (0, 0, 0.0), pelvis)
    torso_h = 0.56
    box(coll, name + "_torso", (0.40, 0.24, torso_h), (0, 0, 0.27), m_shirt, spine, bevel=0.08)
    if long_kurta:
        box(coll, name + "_kurta", (0.42, 0.26, 0.40), (0, 0, -0.05), m_shirt, spine, bevel=0.06)
    if jacket is not None:
        m_j = mat(f"jacket{jacket}", jacket, 0.7)
        box(coll, name + "_jacketL", (0.15, 0.255, 0.50), (0.125, -0.002, 0.28), m_j, spine, bevel=0.05)
        box(coll, name + "_jacketR", (0.15, 0.255, 0.50), (-0.125, -0.002, 0.28), m_j, spine, bevel=0.05)
    cyl(coll, name + "_neck", 0.05, 0.055, 0.12, (0, 0, 0.58), m_skin, spine)

    head = J["head"] = empty(coll, name + "_head", (0, 0, 0.62), spine)
    sphere(coll, name + "_skull", 0.15, (0, 0, 0.16), m_skin, head, scale=(1, 1, 1.12))
    for side, sx in (() if faceless else (("L", 1), ("R", -1))):
        sphere(coll, f"{name}_white{side}", 0.026, (0.052 * sx, -0.128, 0.175), m_white, head, scale=(1, 0.5, 1))
        J["eye" + side] = sphere(coll, f"{name}_eye{side}", 0.016, (0.052 * sx, -0.141, 0.175), m_dark, head)
        box(coll, f"{name}_brow{side}", (0.055, 0.014, 0.012), (0.052 * sx, -0.142, 0.222), m_hair, head,
            rot=(0, -8 * sx, 0))
        sphere(coll, f"{name}_ear{side}", 0.034, (0.148 * sx, 0.005, 0.16), m_skin, head, scale=(0.5, 0.8, 1))
    if faceless:
        return _arms(coll, name, J, spine, m_shirt, m_skin, jacket)
    sphere(coll, name + "_nose", 0.024, (0, -0.152, 0.13), m_skin, head, scale=(0.9, 1, 1.1))
    J["mouth"] = arc(coll, name + "_mouth",
                     [(-0.045, -0.128, 0.085), (-0.02, -0.142, 0.07), (0.02, -0.142, 0.07),
                      (0.045, -0.128, 0.085)], m_lip, head)
    if not bald:
        sphere(coll, name + "_hair", 0.158, (0, 0.012, 0.2), m_hair, head, scale=(1.03, 1.03, 0.82))
        sphere(coll, name + "_quiff", 0.07, (0.03, -0.09, 0.3), m_hair, head, scale=(1.6, 0.9, 0.6))
    else:
        sphere(coll, name + "_hairband", 0.152, (0, 0.03, 0.12), m_hair, head, scale=(1.02, 1.0, 0.45))
    if glasses:
        m_fr = mat("frame", (0.05, 0.05, 0.06), 0.3)
        for sx in (1, -1):
            cx = 0.054 * sx
            for (dx, dz, sw, sh) in ((0, 0.027, 0.078, 0.008), (0, -0.025, 0.078, 0.008),
                                     (0.038, 0, 0.008, 0.06), (-0.038, 0, 0.008, 0.06)):
                box(coll, f"{name}_fr{sx}{dx}{dz}", (sw, 0.008, sh), (cx + dx, -0.155, 0.175 + dz), m_fr, head)
            box(coll, f"{name}_temple{sx}", (0.006, 0.15, 0.006), (0.094 * sx, -0.08, 0.19), m_fr, head)
        box(coll, name + "_bridge", (0.03, 0.008, 0.006), (0, -0.157, 0.185), m_fr, head)

    return _arms(coll, name, J, spine, m_shirt, m_skin, jacket)


def _arms(coll, name, J, spine, m_shirt, m_skin, jacket):
    for side, sx in (("L", 1), ("R", -1)):
        sh = J["shoulder" + side] = empty(coll, f"{name}_shoulder{side}", (0.245 * sx, 0, 0.50), spine)
        sphere(coll, f"{name}_delt{side}", 0.065, (0, 0, -0.02), m_shirt, sh)
        cyl(coll, f"{name}_upperarm{side}", 0.048, 0.058, 0.30, (0, 0, -0.15), m_shirt, sh)
        el = J["elbow" + side] = empty(coll, f"{name}_elbow{side}", (0, 0, -0.30), sh)
        cyl(coll, f"{name}_forearm{side}", 0.036, 0.045, 0.27, (0, 0, -0.135),
            m_shirt if jacket else m_skin, el)
        hd = J["hand" + side] = empty(coll, f"{name}_hand{side}", (0, 0, -0.28), el)
        sphere(coll, f"{name}_palm{side}", 0.048, (0, 0, -0.035), m_skin, hd, scale=(0.75, 0.55, 1.05))
        cyl(coll, f"{name}_finger{side}", 0.011, 0.013, 0.07, (0, -0.012, -0.095), m_skin, hd)
        sphere(coll, f"{name}_thumb{side}", 0.016, (-0.03 * sx, -0.02, -0.02), m_skin, hd, scale=(1, 1, 1.6))
    return J


def pose(J, frame, **joints):
    for jn, rot in joints.items():
        if jn == "root_loc":
            key(J["root"], frame, loc=rot)
        else:
            key(J[jn], frame, rot=rot)


def seat(J, frame=None, seat_h=0.47):
    """Sitting pose; root placed so the hips sit at seat_h."""
    J["root"].location.z = seat_h - 0.95
    for s in ("L", "R"):
        J["hip" + s].rotation_euler = (R(-90), 0, 0)
        J["knee" + s].rotation_euler = (R(90), 0, 0)
    if frame is not None:
        for s in ("L", "R"):
            key(J["hip" + s], frame, rot=(-90, 0, 0))
            key(J["knee" + s], frame, rot=(90, 0, 0))


# ---------------------------------------------------------------- scene setup

def new_scene(name, quality):
    if name == "S01" and "Scene" in bpy.data.scenes:
        sc = bpy.data.scenes["Scene"]
        sc.name = name
    else:
        sc = bpy.data.scenes.new(name)
    sc.frame_start, sc.frame_end = 1, DUR[name]
    sc.render.fps = FPS
    q = QUALITY[quality]
    sc.render.resolution_x, sc.render.resolution_y = q["res"]
    sc.render.resolution_percentage = 100
    sc.render.engine = q["engine"]
    if q["engine"] == "CYCLES":
        sc.cycles.device = "CPU"
        sc.cycles.samples = q["samples"]
        sc.cycles.use_denoising = True
        sc.cycles.max_bounces = 4
    else:
        sc.eevee.taa_render_samples = q["samples"]
        try:
            sc.eevee.use_shadows = True
            sc.eevee.use_raytracing = q.get("raytrace", False)
        except Exception:
            pass
    sc.render.image_settings.file_format = "PNG"
    sc.render.use_overwrite = False  # resumable: skip frames already on disk
    sc.render.use_placeholder = True
    sc.render.filepath = os.path.join(HERE, "renders", quality, name, "")
    try:
        sc.view_settings.view_transform = "AgX"
        sc.view_settings.look = "AgX - Punchy"
    except Exception:
        pass
    sc.render.film_transparent = False
    return sc, sc.collection


def world(sc, color, strength=1.0):
    w = bpy.data.worlds.new(sc.name + "_world")
    nodes, _ = _nodes(w)
    bg = nodes.get("Background")
    bg.inputs["Color"].default_value = (*color, 1)
    bg.inputs["Strength"].default_value = strength * 0.6  # keep ambient low so key lights shape the forms
    sc.world = w


def light(coll, name, kind, loc, energy, color=(1, 1, 1), size=1.0, target=None, spot=45):
    ld = bpy.data.lights.new(name, kind)
    ld.energy, ld.color = energy, color
    if kind == "AREA":
        ld.size = size
    elif kind in ("POINT", "SPOT"):
        ld.shadow_soft_size = size
    if kind == "SPOT":
        ld.spot_size, ld.spot_blend = R(spot), 0.4
    ob = bpy.data.objects.new(name, ld)
    coll.objects.link(ob)
    ob.location = loc
    if target is not None:
        aim(ob, target)
    return ob


def camera(sc, coll, loc, target, lens=40, name="cam"):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.sensor_fit = "AUTO"
    cam = bpy.data.objects.new(name, cd)
    coll.objects.link(cam)
    cam.location = loc
    tgt = empty(coll, name + "_target", target)
    c = cam.constraints.new("TRACK_TO")
    c.target, c.track_axis, c.up_axis = tgt, "TRACK_NEGATIVE_Z", "UP_Y"
    sc.camera = cam
    return cam, tgt


def floor(coll, material, size=40, z=0.0):
    return box(coll, "floor", (size, size, 0.02), (0, 0, z - 0.01), material)


def udaya(coll, name="udaya"):
    shirt = img_mat("udaya_shirt", "checks", 0.0, 0.8, repeat=(3, 3))[0]
    return figure(coll, name, shirt, (0.35, 0.36, 0.40), skin=SKIN_TONES[0], glasses=True,
                  shoes=(0.18, 0.1, 0.06))


def palace_set(coll):
    floor(coll, checker_mat("tiles", (0.62, 0.56, 0.47), (0.58, 0.52, 0.44), 30, 0.25))
    box(coll, "backwall", (8, 0.2, 5), (0, 2.6, 2.5), mat("peach", (0.78, 0.47, 0.36), 0.6))
    box(coll, "hedge", (3.2, 0.3, 2.4), (-1.0, 2.45, 3.0), noisy_mat("hedge", (0.06, 0.2, 0.05), (0.18, 0.4, 0.1), 40, 0.9, 0.8))
    box(coll, "lintel", (3.6, 0.35, 0.25), (-1.0, 2.35, 1.75), mat("marble", (0.9, 0.88, 0.84), 0.3), bevel=0.03)
    m_marble = mat("marble", (0.9, 0.88, 0.84), 0.3)
    for i, x in enumerate((1.25, 2.4)):
        cyl(coll, f"pillar{i}", 0.2, 0.2, 4.5, (x, 2.0, 2.25), m_marble, seg=32)
        box(coll, f"pillar_cap{i}", (0.55, 0.55, 0.18), (x, 2.0, 4.3), m_marble, bevel=0.03)
        box(coll, f"pillar_base{i}", (0.55, 0.55, 0.18), (x, 2.0, 0.09), m_marble, bevel=0.03)




# ---------------------------------------------------------------- v2 additions

TEAL = (0.07, 0.28, 0.32)


def mannequin(coll, name, tint=TEAL):
    """Faceless teal crowd figure, as in the reference's background characters."""
    m = mat(f"mannequin{tint}", tint, 0.32)
    return figure(coll, name, m, m, skin=tint, glasses=False, shoes=tint, faceless=True, bald=True,
                  hair=tint)


def dof(cam, target_obj, fstop=2.0):
    cam.data.dof.use_dof = True
    cam.data.dof.focus_object = target_obj
    cam.data.dof.aperture_fstop = fstop


def label3d(coll, name, body, size, loc, rot=(80, 0, 0), color=(1.0, 0.8, 0.1), emit=1.5, font=None,
            extrude=0.02):
    """Extruded glowing 3D word floating in the scene (reference: TREASON / DISLOYALTY ...)."""
    m = mat(f"label{color}{emit}", color, 0.3, emit=color, emit_strength=emit)
    return text(coll, name, body, size, loc, m, rot=rot, font=font or os.path.join(textures.FONTS, "Inter-ExtraBold.otf"),
                extrude=extrude)
