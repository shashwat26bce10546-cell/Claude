"""Build (and optionally render) the 10 shots of the ₹ Short in Blender (bpy 5.x).

Usage (system python with the `bpy` wheel):
  python3 build_scenes.py --save                      # write rupee_short.blend with scenes S01..S10
  python3 build_scenes.py --render S04 --quality draft [--frames 1-144] [--step N]

Everything is built from primitives — stylised "vinyl toy" figures, no external assets.
Frames land in renders/<quality>/<scene>/####.png.
"""
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
DUR = {"S01": 72, "S02": 120, "S03": 120, "S04": 144, "S05": 192,
       "S06": 144, "S07": 144, "S08": 192, "S09": 144, "S10": 72}
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
           jacket=None, long_kurta=False, shoes=(0.12, 0.07, 0.04), bald=False):
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
    for side, sx in (("L", 1), ("R", -1)):
        sphere(coll, f"{name}_white{side}", 0.026, (0.052 * sx, -0.128, 0.175), m_white, head, scale=(1, 0.5, 1))
        J["eye" + side] = sphere(coll, f"{name}_eye{side}", 0.016, (0.052 * sx, -0.141, 0.175), m_dark, head)
        box(coll, f"{name}_brow{side}", (0.055, 0.014, 0.012), (0.052 * sx, -0.142, 0.222), m_hair, head,
            rot=(0, -8 * sx, 0))
        sphere(coll, f"{name}_ear{side}", 0.034, (0.148 * sx, 0.005, 0.16), m_skin, head, scale=(0.5, 0.8, 1))
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


# ---------------------------------------------------------------- scenes

def hook_pose(J, f):
    """Holds the note up on screen-left, points at it with the other hand."""
    pose(J, f,
         shoulderR=(30, 110, 21), elbowR=(-83, 0, 0), handR=(40, 0, 40),
         shoulderL=(-85, -54, -31), elbowL=(-75, 0, 0), handL=(16, 0, 20),
         spine=(0, 0, 0), head=(0, -6, 0))


def build_hook(sc, coll, loop=False):
    world(sc, (0.6, 0.62, 0.66), 0.3)
    palace_set(coll)
    J = udaya(coll)
    n = DUR[sc.name]
    img_plane(coll, "note", "note", 0.45, (-0.39, -0.215, 1.70), rot=(0, 0, 4), emit=0.2)
    hook_pose(J, 1)
    # finger taps (elbow pulses) and a little head bob
    taps = [(14, 20), (26, 32)] if not loop else [(8, 14), (20, 26)]
    for a, b in taps:
        pose(J, a, elbowL=(-75, 0, 0))
        pose(J, (a + b) // 2, elbowL=(-83, 0, 0))
        pose(J, b, elbowL=(-75, 0, 0))
    pose(J, n, elbowL=(-75, 0, 0), head=(0, -2, 0))
    if loop:
        eye = J["eyeR"]
        for f, s in ((34, 1), (38, 0.08), (44, 0.08), (48, 1)):
            key(eye, f, scale=(1, 1, s))
    cam, tgt = camera(sc, coll, (-0.27, -2.15, 1.55), (-0.27, 0, 1.45), lens=42)
    near, far = (-0.27, -1.8, 1.55), (-0.27, -2.15, 1.55)
    key(cam, 1, loc=near if loop else far); key(cam, n, loc=far if loop else near)
    light(coll, "key", "AREA", (-1.6, -1.8, 2.6), 400, (1, 0.94, 0.86), 2.0, (0, 0, 1.4))
    light(coll, "fill", "AREA", (1.8, -1.2, 1.6), 120, (0.85, 0.9, 1), 2.0, (0, 0, 1.4))
    light(coll, "rim", "AREA", (0.8, 1.2, 2.4), 250, (1, 0.9, 0.8), 1.0, (0, 0, 1.5))


def build_s02(sc, coll):
    world(sc, (0.55, 0.55, 0.6), 0.5)
    floor(coll, mat("woodfloor", (0.3, 0.2, 0.13), 0.5))
    box(coll, "wall", (6, 0.2, 4), (0, 1.4, 2), mat("wall2", (0.72, 0.68, 0.6), 0.8))
    m_wood = noisy_mat("tablewood", (0.32, 0.18, 0.09), (0.45, 0.27, 0.14), 3, 0.45, 0.05)
    box(coll, "tabletop", (1.6, 1.0, 0.05), (0, 0.1, 0.725), m_wood, bevel=0.01)
    for i, (x, y) in enumerate(((-0.7, -0.3), (0.7, -0.3), (-0.7, 0.5), (0.7, 0.5))):
        box(coll, f"leg{i}", (0.06, 0.06, 0.7), (x, y, 0.35), m_wood)
    img_plane(coll, "paper", "newspaper", 0.42, (-0.05, -0.12, 0.752), rot=(0, 0, 4), horizontal=True, emit=0.15)
    m_alu = mat("alu", (0.6, 0.62, 0.65), 0.25, 0.8)
    box(coll, "lap_base", (0.36, 0.25, 0.02), (0.08, 0.3, 0.76), m_alu, bevel=0.005)
    lid = empty(coll, "lid", (0.08, 0.425, 0.77))
    lid.rotation_euler = (R(-12), 0, 0)
    box(coll, "lap_lid", (0.36, 0.012, 0.24), (0, 0, 0.12), m_alu, lid, bevel=0.004)
    scr, _ = img_plane(coll, "lap_screen", "submit", 0.33, (0, -0.0075, 0.12), lid, emit=1.6)
    cyl(coll, "mug", 0.045, 0.045, 0.1, (-0.45, 0.35, 0.8), mat("mug", (0.85, 0.2, 0.15), 0.3))
    cyl(coll, "pen", 0.006, 0.006, 0.15, (0.25, -0.15, 0.758), mat("pen", (0.1, 0.2, 0.6), 0.3), rot=(0, 90, 30))
    light(coll, "window", "AREA", (-1.6, -0.6, 2.0), 300, (1, 0.95, 0.85), 1.5, (0, 0.1, 0.75))
    light(coll, "fill", "AREA", (1.4, -1.2, 1.6), 80, (0.8, 0.88, 1), 2, (0, 0.1, 0.75))
    cam, tgt = camera(sc, coll, (-0.05, -0.42, 1.45), (-0.05, -0.1, 0.75), lens=40)
    n = DUR[sc.name]
    key(cam, 1, loc=(-0.05, -0.42, 1.45)); key(tgt, 1, loc=(-0.05, -0.1, 0.75))
    key(cam, 40, loc=(-0.05, -0.45, 1.42)); key(tgt, 40, loc=(-0.05, -0.1, 0.75))
    key(cam, 95, loc=(0.02, -0.55, 1.08)); key(tgt, 95, loc=(0.08, 0.42, 0.9))
    key(cam, n, loc=(0.03, -0.45, 1.06)); key(tgt, n, loc=(0.08, 0.42, 0.9))


def build_s03(sc, coll):
    world(sc, (0.6, 0.6, 0.65), 0.6)
    floor(coll, checker_mat("hallfloor", (0.55, 0.5, 0.45), (0.5, 0.46, 0.41), 20, 0.35))
    box(coll, "wall", (12, 0.2, 5), (0, 4.2, 2.5), mat("wall3", (0.7, 0.72, 0.75), 0.8))
    m_desk = mat("desk3", (0.5, 0.33, 0.2), 0.5)
    shirts = [(0.75, 0.25, 0.2), (0.2, 0.45, 0.3), (0.85, 0.7, 0.3), (0.35, 0.3, 0.6), (0.9, 0.9, 0.88),
              (0.2, 0.35, 0.55)]
    starts = []
    n = DUR[sc.name]
    for i in range(6):
        row, col = divmod(i, 3)
        x, y = (col - 1) * 1.5 + (0.4 if row else 0), 1.4 + row * 1.5
        box(coll, f"desk{i}", (1.0, 0.6, 0.05), (x, y - 0.45, 0.72), m_desk)
        box(coll, f"desklegs{i}", (0.95, 0.55, 0.68), (x, y - 0.45, 0.35), mat("deskleg", (0.2, 0.2, 0.22), 0.5))
        box(coll, f"chair{i}", (0.4, 0.4, 0.45), (x, y + 0.05, 0.225), mat("chair", (0.25, 0.25, 0.3), 0.6))
        J = figure(coll, f"p{i}", shirts[i], (0.2, 0.2, 0.25), skin=SKIN_TONES[i % 4], glasses=(i % 2 == 0),
                   hair=(0.03, 0.025, 0.02) if i != 4 else (0.5, 0.5, 0.5))
        J["root"].location = (x, y, 0)
        seat(J, 1)
        ph = i * 7
        for f in range(1, n + 1, 12):
            k = ((f + ph) // 12) % 2
            pose(J, f, shoulderR=(-55, 0, -10), elbowR=(-40 - 12 * k, 0, 0),
                 shoulderL=(-45, 0, 10), elbowL=(-50, 0, 0), head=(18 + 4 * k, 0, 0))
        starts.append((x, y - 0.45, 0.8))
    # cardboard ENTRIES box
    m_card = noisy_mat("cardboard", (0.55, 0.4, 0.24), (0.6, 0.45, 0.28), 30, 0.85, 0.1)
    bx, by = 0, -0.6
    for (sx, sy, lx, ly) in ((0.9, 0.04, 0, -0.33), (0.9, 0.04, 0, 0.33), (0.04, 0.7, -0.45, 0), (0.04, 0.7, 0.45, 0)):
        box(coll, "cbox", (sx, sy, 0.6), (bx + lx, by + ly, 0.3), m_card)
    box(coll, "cbox_bottom", (0.9, 0.7, 0.04), (bx, by, 0.02), m_card)
    img_plane(coll, "entries_label", "entries", 0.7, (bx, by - 0.355, 0.33), emit=0.3)
    m_env = mat("envelope", (0.93, 0.91, 0.86), 0.6)
    rnd = random.Random(3)
    for i in range(34):
        e = box(coll, f"env{i}", (0.18, 0.12, 0.006), (0, 0, 0), m_env)
        sx, sy, sz = starts[i % 6]
        sx += rnd.uniform(-0.3, 0.3)
        t0 = 4 + int(i * 2.6)
        t1 = t0 + 20
        ex, ey = bx + rnd.uniform(-0.25, 0.25), by + rnd.uniform(-0.2, 0.2)
        e.scale = (0, 0, 0); e.keyframe_insert("scale", frame=t0 - 1)
        key(e, t0, loc=(sx, sy, sz), rot=(0, 0, 0), scale=(0.18, 0.12, 0.006))
        key(e, (t0 + t1) // 2, loc=((sx + ex) / 2, (sy + ey) / 2, 2.0 + rnd.uniform(0, 0.5)),
            rot=(rnd.uniform(-180, 180), rnd.uniform(-90, 90), rnd.uniform(-180, 180)))
        key(e, t1, loc=(ex, ey, 0.45), rot=(rnd.uniform(-20, 20), rnd.uniform(-20, 20), rnd.uniform(0, 180)))
        key(e, t1 + 3, loc=(ex, ey, 0.3), scale=(0.18, 0.12, 0.006))
        key(e, t1 + 4, scale=(0, 0, 0))
    # overflow pile grows
    for i in range(40):
        e = box(coll, f"pile{i}", (1, 1, 1), (bx + rnd.uniform(-0.4, 0.4), by + rnd.uniform(-0.3, 0.3),
                                              0.62 + rnd.uniform(0, 0.25)), m_env,
                rot=(rnd.uniform(-25, 25), rnd.uniform(-25, 25), rnd.uniform(0, 180)))
        t = 40 + int(i * 1.9)
        key(e, t - 1, scale=(0, 0, 0))
        key(e, t + 3, scale=(0.18, 0.12, 0.006))
    for i in range(12):
        ang = rnd.uniform(0, math.tau)
        box(coll, f"spill{i}", (0.18, 0.12, 0.006), (bx + math.cos(ang) * rnd.uniform(0.55, 0.9),
                                                   by + math.sin(ang) * rnd.uniform(0.5, 0.8), 0.004), m_env,
            rot=(0, 0, rnd.uniform(0, 180)))
    light(coll, "sun", "SUN", (0, 0, 5), 2.5, (1, 0.96, 0.9))
    sc.objects["sun"].rotation_euler = (R(45), R(10), R(-30))
    light(coll, "fill", "AREA", (0, -3, 2.5), 300, (0.9, 0.92, 1), 3, (0, 0, 0.6))
    cam, tgt = camera(sc, coll, (0.1, -3.4, 1.15), (0, 0.6, 0.85), lens=32)
    key(cam, 1, loc=(0.1, -3.4, 1.15)); key(cam, n, loc=(0.05, -2.9, 1.05))


def build_s04(sc, coll):
    world(sc, (0.02, 0.03, 0.07), 1.0)
    floor(coll, mat("hostelfloor", (0.25, 0.22, 0.2), 0.6))
    m_wall = mat("hostelwall", (0.55, 0.58, 0.62), 0.85)
    box(coll, "backwall", (6, 0.15, 3.2), (0, 1.5, 1.6), m_wall)
    box(coll, "sidewall", (0.15, 6, 3.2), (-1.8, 0, 1.6), m_wall)
    img_plane(coll, "poster", "poster", 0.5, (-0.6, 1.42, 1.75), emit=0.05)
    img_plane(coll, "calendar", "calendar", 0.3, (0.35, 1.42, 1.65), emit=0.05)
    # window with moonlight
    plane(coll, "window", 0.7, 0.9, (-1.72, 0.2, 1.7), mat("night", (0.1, 0.15, 0.35), 0.2, emit=(0.15, 0.25, 0.6),
                                                           emit_strength=1.2), rot=(0, 0, -90))
    m_desk = mat("hosteldesk", (0.42, 0.28, 0.17), 0.55)
    box(coll, "desk", (1.2, 0.65, 0.05), (0, 0, 0.74), m_desk, bevel=0.01)
    box(coll, "deskfront", (1.2, 0.03, 0.66), (0, -0.31, 0.38), m_desk)
    J = udaya(coll)
    J["root"].location = (0.05, 0.55, 0)
    seat(J, 1)
    box(coll, "chair", (0.44, 0.44, 0.45), (0.05, 0.6, 0.225), mat("chair4", (0.2, 0.2, 0.24), 0.6))
    box(coll, "chairback", (0.44, 0.05, 0.5), (0.05, 0.84, 0.7), mat("chair4", (0.2, 0.2, 0.24), 0.6))
    paper_m = mat("sheet", (0.95, 0.94, 0.9), 0.7)
    plane(coll, "sheet", 0.3, 0.4, (0.0, 0.05, 0.768), paper_m, horizontal=True, rot=(0, 0, 8))
    n = DUR[sc.name]
    for f in range(1, n + 1, 8):
        k = (f // 8) % 2
        pose(J, f, shoulderR=(-62, 0, -18), elbowR=(-38 - 10 * k, 0, 0), handR=(10, 0, 0),
             shoulderL=(-50, 0, 15), elbowL=(-55, 0, 0), spine=(10, 0, 0), head=(10 + 3 * k, 0, 4 * k))
    # desk lamp
    m_lamp = mat("lamp", (0.1, 0.1, 0.12), 0.35, 0.5)
    cyl(coll, "lampbase", 0.08, 0.08, 0.03, (0.45, 0.15, 0.78), m_lamp)
    cyl(coll, "lamparm", 0.012, 0.012, 0.45, (0.45, 0.12, 0.99), m_lamp, rot=(-15, 0, 0))
    cyl(coll, "lampshade", 0.03, 0.11, 0.12, (0.42, -0.0, 1.2), m_lamp, rot=(-140, 0, 20))
    light(coll, "lampspot", "SPOT", (0.38, -0.05, 1.17), 120, (1, 0.72, 0.4), 0.05, (0.0, 0.1, 0.76), spot=80)
    light(coll, "lampglow", "POINT", (0.4, -0.02, 1.13), 15, (1, 0.7, 0.4), 0.05)
    light(coll, "moon", "AREA", (-1.6, 0.2, 1.8), 60, (0.45, 0.6, 1), 0.8, (0.1, 0.4, 0.9))
    light(coll, "rimblue", "AREA", (1.4, 1.2, 2.2), 40, (0.4, 0.5, 1), 1.0, (0.05, 0.5, 1.1))
    m_crump = mat("crumple", (0.92, 0.9, 0.85), 0.8)
    rnd = random.Random(11)
    for i in range(14):
        on_desk = i < 4
        loc = ((rnd.uniform(-0.5, -0.2) if on_desk else rnd.uniform(-1.3, 1.2)),
               (rnd.uniform(-0.2, 0.2) if on_desk else rnd.uniform(-1.4, 1.2)),
               0.8 if on_desk else 0.035)
        crumple(coll, f"ball{i}", 0.04, loc, m_crump, i)
    # bunk bed
    m_bed = mat("bed", (0.3, 0.32, 0.36), 0.4, 0.6)
    for x in (0.9, 1.75):
        for y in (0.6, 1.4):
            box(coll, f"bedpost{x}{y}", (0.05, 0.05, 1.8), (x, y, 0.9), m_bed)
    for z in (0.45, 1.4):
        box(coll, f"mattress{z}", (0.9, 0.85, 0.12), (1.32, 1.0, z), mat("mattress", (0.6, 0.25, 0.25), 0.9))
    cam, tgt = camera(sc, coll, (-1.15, -1.55, 1.55), (0.05, 0.35, 0.95), lens=32)
    key(cam, 1, loc=(-1.15, -1.55, 1.55)); key(cam, n, loc=(-0.9, -1.25, 1.45))


def build_s05(sc, coll):
    world(sc, (0.4, 0.38, 0.36), 0.4)
    box(coll, "desktop", (2, 2, 0.04), (0, 0, -0.02), noisy_mat("desk5", (0.36, 0.22, 0.12), (0.46, 0.29, 0.16), 4, 0.5, 0.05))
    img_plane(coll, "paper", "paper_plain", 0.32, (0, 0.0, 0.001), horizontal=True, emit=0.05)
    n = DUR[sc.name]
    graphite = (0.03, 0.03, 0.035)
    m_ra, thr_ra, op_ra, _ = reveal_mat("ra_mat", graphite)
    m_r, thr_r, op_r, _ = reveal_mat("r_mat", graphite)
    m_ru, thr_ru, op_ru, em_ru = reveal_mat("rupee_mat", (0.55, 0.2, 0.02), emit=(1.0, 0.42, 0.05))
    ra = text(coll, "ra", "र", 0.11, (-0.065, 0.02, 0.002), m_ra, font=FONT_DEVA_REG)
    rr = text(coll, "R", "R", 0.10, (0.065, 0.02, 0.002), m_r, font=FONT_INTER)
    ru = text(coll, "rupee", "₹", 0.17, (0, 0.0, 0.002), m_ru, font=FONT_DEVA)
    # wipe timings
    key_socket(thr_ra, 1, -0.06); key_socket(thr_ra, 44, 0.06)
    key_socket(thr_r, 1, -0.06); key_socket(thr_r, 48, -0.06); key_socket(thr_r, 90, 0.06)
    key_socket(thr_ru, 1, 1.0)
    key_socket(op_ra, 1, 1.0); key_socket(op_ra, 100, 1.0); key_socket(op_ra, 122, 0.0)
    key_socket(op_r, 1, 1.0); key_socket(op_r, 100, 1.0); key_socket(op_r, 122, 0.0)
    key_socket(op_ru, 1, 0.0); key_socket(op_ru, 104, 0.0); key_socket(op_ru, 126, 1.0)
    key_socket(em_ru, 1, 0.0); key_socket(em_ru, 126, 0.0); key_socket(em_ru, 150, 1.2); key_socket(em_ru, n, 0.9)
    key(ra, 100, loc=(-0.065, 0.02, 0.002)); key(ra, 124, loc=(-0.005, 0.0, 0.002))
    key(rr, 100, loc=(0.065, 0.02, 0.002)); key(rr, 124, loc=(0.005, 0.0, 0.002))
    key(ru, 1, scale=0.8); key(ru, 104, scale=0.8); key(ru, 130, scale=1.0)
    # pencil
    m_y = mat("pencil_y", (0.95, 0.72, 0.1), 0.4)
    pencil = empty(coll, "pencil")
    cyl(coll, "pencil_body", 0.0075, 0.0075, 0.16, (0, 0, 0.1), m_y, pencil, seg=6)
    cyl(coll, "pencil_wood", 0.0075, 0.0015, 0.02, (0, 0, 0.01), mat("pencil_wood", (0.85, 0.65, 0.45), 0.7), pencil,
        seg=6, rot=(180, 0, 0))
    cyl(coll, "pencil_eraser", 0.0078, 0.0078, 0.015, (0, 0, 0.185), mat("eraser", (0.9, 0.4, 0.45), 0.6), pencil)
    pencil.rotation_euler = (R(-40), R(35), 0)

    def tip(f, x, y, z=0.004):
        key(pencil, f, loc=(x, y, z))

    for f in range(1, 45, 4):  # drawing र
        t = (f - 1) / 43
        tip(f, -0.065 - 0.05 + 0.1 * t, 0.02 + 0.03 * math.sin(f * 0.9))
    tip(48, 0.02, 0.05, 0.03)
    for f in range(52, 91, 4):  # drawing R
        t = (f - 52) / 38
        tip(f, 0.065 - 0.04 + 0.08 * t, 0.02 + 0.035 * math.sin(f * 0.8))
    tip(100, 0.16, 0.08, 0.06)
    tip(n, 0.22, 0.12, 0.08)
    light(coll, "key", "AREA", (-0.4, -0.3, 0.6), 14, (1, 0.9, 0.78), 0.5, (0, 0, 0))
    light(coll, "fill", "AREA", (0.5, -0.2, 0.4), 8, (0.8, 0.88, 1), 0.5, (0, 0, 0))
    cam, tgt = camera(sc, coll, (0.0, -0.17, 0.36), (0, 0.01, 0), lens=45)
    key(cam, 1, loc=(0.0, -0.17, 0.36)); key(cam, 110, loc=(0.0, -0.15, 0.34))
    key(cam, n, loc=(0.05, -0.12, 0.28))


def build_s06(sc, coll):
    world(sc, (0.4, 0.36, 0.32), 0.4)
    floor(coll, mat("carpet", (0.35, 0.12, 0.1), 0.95))
    m_panel = noisy_mat("panel", (0.28, 0.16, 0.09), (0.36, 0.22, 0.12), 2, 0.5, 0.05)
    box(coll, "backwall", (8, 0.2, 4), (0, 3.2, 2), m_panel)
    box(coll, "leftwall", (0.2, 8, 4), (-2.6, 0, 2), m_panel)
    img_plane(coll, "banner", "committee", 2.4, (0, 3.08, 2.6), emit=0.3)
    # clock
    cyl(coll, "clock", 0.22, 0.22, 0.04, (1.6, 3.08, 2.9), mat("clock", (0.95, 0.94, 0.9), 0.3), rot=(90, 0, 0))
    m_tab = noisy_mat("committee_table", (0.25, 0.13, 0.07), (0.33, 0.18, 0.1), 3, 0.35, 0.03)
    box(coll, "table", (0.9, 3.2, 0.06), (-1.2, 0.6, 0.75), m_tab, bevel=0.01)
    box(coll, "tablebase", (0.8, 3.0, 0.7), (-1.2, 0.6, 0.36), m_tab)
    kurtas = [(0.92, 0.9, 0.84), (0.85, 0.78, 0.62), (0.93, 0.93, 0.93), (0.7, 0.72, 0.75), (0.88, 0.84, 0.74)]
    jackets = [(0.15, 0.15, 0.2), None, (0.35, 0.22, 0.12), None, (0.12, 0.18, 0.15)]
    n = DUR[sc.name]
    for i in range(5):
        y = -0.6 + i * 0.6
        J = figure(coll, f"o{i}", kurtas[i], (0.9, 0.9, 0.88), skin=SKIN_TONES[(i + 1) % 4], hair=(0.6, 0.6, 0.6),
                   glasses=(i != 2), jacket=jackets[i], long_kurta=True, bald=(i == 3))
        J["root"].location = (-1.75, y, 0)
        J["root"].rotation_euler = (0, 0, R(90))
        seat(J, 1)
        pose(J, 1, shoulderL=(-40, 0, 10), elbowL=(-60, 0, 0), shoulderR=(-40, 0, -10), elbowR=(-60, 0, 0),
             head=(0, 0, -10 + i * 3))
        pose(J, n, head=(0, 0, -25 + i * 2))
        box(coll, f"seat{i}", (0.45, 0.45, 0.46), (-1.8, y, 0.23), mat("seat6", (0.5, 0.1, 0.1), 0.7))
        box(coll, f"seatback{i}", (0.05, 0.45, 0.6), (-2.05, y, 0.75), mat("seat6", (0.5, 0.1, 0.1), 0.7))
    # easels (index 2 = the winning ₹)
    order = [0, 1, 4, 3, 2]  # design index per easel position
    m_easel = mat("easel", (0.45, 0.3, 0.18), 0.6)
    lights = []
    for i, d in enumerate(order):
        y = -1.2 + i * 0.95
        g = empty(coll, f"easel{i}", (0.85, y, 0))
        g.rotation_euler = (0, 0, R(-28))
        for lx in (-0.25, 0.25):
            box(coll, f"easel_leg{i}{lx}", (0.035, 0.035, 1.7), (lx, 0.1, 0.82), m_easel, g, rot=(-6, 0, lx * 18))
        box(coll, f"easel_tray{i}", (0.6, 0.06, 0.03), (0, -0.02, 0.85), m_easel, g)
        _, es = img_plane(coll, f"card{i}", f"design{d}", 0.5, (0, -0.04, 1.17), g, emit=0.35)
        L = light(coll, f"spot{i}", "SPOT", (0.6, y - 0.4, 2.6), 160, (1, 0.92, 0.8), 0.1, (0.85, y, 1.15), spot=35)
        lights.append((L, es, d))
    off = {0: 40, 1: 56, 3: 72, 2: 88}  # design → frame it dims
    for L, es, d in lights:
        if d in off:
            f = off[d]
            L.data.energy = 160; L.data.keyframe_insert("energy", frame=f - 4)
            L.data.energy = 4; L.data.keyframe_insert("energy", frame=f + 2)
            key_socket(es, f - 4, 0.35); key_socket(es, f + 2, 0.02)
        else:
            L.data.energy = 160; L.data.keyframe_insert("energy", frame=88)
            L.data.energy = 320; L.data.keyframe_insert("energy", frame=100)
            key_socket(es, 88, 0.35); key_socket(es, 100, 0.8)
    light(coll, "ceiling", "AREA", (0, 0.6, 3.6), 260, (1, 0.9, 0.78), 3, (0, 0.6, 0))
    cam, tgt = camera(sc, coll, (0.2, -3.6, 2.0), (-0.35, 0.4, 0.95), lens=24)
    key(cam, 1, loc=(0.2, -3.6, 2.0)); key(tgt, 1, loc=(-0.35, 0.4, 0.95))
    key(cam, 92, loc=(0.15, -3.3, 1.95)); key(tgt, 92, loc=(-0.3, 0.45, 0.95))
    key(cam, n, loc=(0.36, -0.2, 1.25)); key(tgt, n, loc=(0.85, 0.7, 1.17))


def build_s07(sc, coll):
    world(sc, (0.05, 0.06, 0.1), 0.6)
    floor(coll, mat("gallery_floor", (0.15, 0.15, 0.17), 0.4))
    box(coll, "wall", (6, 0.2, 4), (0, 0.3, 2), mat("navy", (0.06, 0.09, 0.18), 0.8))
    m_frame = mat("goldframe", (0.75, 0.55, 0.2), 0.3, 0.9)
    for i, (k, x) in enumerate((("proof_card", -0.32), ("sketch_paper", 0.32))):
        box(coll, f"frame{i}", (0.58, 0.04, 0.71), (x, 0.19, 1.85), m_frame, bevel=0.01)
        img_plane(coll, f"panel{i}", k, 0.5, (x, 0.165, 1.85), emit=0.25)
        light(coll, f"picture{i}", "SPOT", (x, -0.6, 2.7), 70, (1, 0.93, 0.82), 0.05, (x, 0.2, 1.85), spot=40)
    light(coll, "fill", "AREA", (0, -2, 1.5), 40, (0.7, 0.8, 1), 2, (0, 0.2, 1.8))
    n = DUR[sc.name]
    cam, tgt = camera(sc, coll, (-0.25, -1.9, 1.45), (0, 0.2, 1.55), lens=34)
    key(cam, 1, loc=(-0.25, -1.9, 1.45)); key(cam, n, loc=(0.15, -1.6, 1.45))


def build_s08(sc, coll):
    world(sc, (0.55, 0.72, 0.95), 1.0)
    floor(coll, noisy_mat("grass", (0.12, 0.3, 0.07), (0.2, 0.42, 0.12), 6, 0.9, 0.4), size=120)
    box(coll, "path", (2.2, 30, 0.02), (0, 3, 0.005), noisy_mat("path", (0.5, 0.48, 0.45), (0.58, 0.56, 0.52), 10, 0.9, 0.1))
    m_pillar = mat("gatepillar", (0.72, 0.35, 0.24), 0.7)
    m_cream = mat("cream", (0.9, 0.86, 0.76), 0.6)
    for x in (-1.6, 1.6):
        box(coll, f"gatepillar{x}", (0.6, 0.6, 3.2), (x, 6, 1.6), m_pillar, bevel=0.02)
        box(coll, f"gatecap{x}", (0.75, 0.75, 0.2), (x, 6, 3.3), m_cream, bevel=0.02)
    box(coll, "gatebeam", (3.8, 0.4, 0.55), (0, 6, 3.05), m_cream, bevel=0.02)
    img_plane(coll, "gatesign", "gate_sign", 3.0, (0, 5.79, 3.05), emit=0.2)
    m_hill = noisy_mat("hill", (0.16, 0.32, 0.22), (0.22, 0.4, 0.28), 1.5, 0.95, 0.5)
    for i, (x, y, r) in enumerate(((-14, 40, 14), (6, 46, 18), (24, 38, 12), (-30, 50, 16))):
        sphere(coll, f"hill{i}", r, (x, y, -r * 0.55), m_hill, scale=(1.4, 1, 0.8))
    m_trunk = mat("trunk", (0.25, 0.16, 0.1), 0.8)
    m_leaf = noisy_mat("leaf", (0.08, 0.25, 0.06), (0.15, 0.38, 0.1), 5, 0.8, 0.4)
    rnd = random.Random(5)
    for i in range(14):
        x = rnd.choice((-1, 1)) * rnd.uniform(2.6, 9)
        y = rnd.uniform(4, 22)
        cyl(coll, f"trunk{i}", 0.12, 0.15, 1.6, (x, y, 0.8), m_trunk)
        sphere(coll, f"crown{i}", rnd.uniform(0.9, 1.4), (x, y, 2.3), m_leaf, scale=(1, 1, 1.15), seg=16)
    J = udaya(coll)
    n = DUR[sc.name]
    # backpack strap + bag
    box(coll, "bag", (0.3, 0.16, 0.4), (0, 0.18, 0.28), mat("bag", (0.15, 0.2, 0.35), 0.7), J["spine"], bevel=0.04)
    # phone in right hand
    phone = box(coll, "phone", (0.075, 0.009, 0.15), (0.0, -0.035, -0.07), mat("phone", (0.02, 0.02, 0.03), 0.2),
                J["handR"], rot=(0, 0, 0), bevel=0.005)
    scr, scr_es = img_plane(coll, "phone_screen", "phone_news", 0.066, (0.0, -0.041, -0.07), J["handR"], emit=0.3)
    stop = 110
    y0, y1 = 6.4, 1.2
    for f in range(1, stop + 1, 6):
        t = (f - 1) / (stop - 1)
        ph = math.sin(f / 24 * math.tau)
        bob = abs(math.cos(f / 24 * math.tau)) * 0.025
        pose(J, f, root_loc=(0, y0 + (y1 - y0) * t, bob), hipL=(25 * ph, 0, 0), hipR=(-25 * ph, 0, 0),
             kneeL=(max(0, -30 * ph), 0, 0), kneeR=(max(0, 30 * ph), 0, 0),
             shoulderL=(-20 * ph, 0, 6), shoulderR=(20 * ph, 0, -6), elbowL=(-15, 0, 0), elbowR=(-15, 0, 0))
    pose(J, stop + 6, root_loc=(0, y1, 0), hipL=(0, 0, 0), hipR=(0, 0, 0), kneeL=(0, 0, 0), kneeR=(0, 0, 0),
         shoulderL=(0, 0, 6), shoulderR=(0, 0, -6), elbowL=(-10, 0, 0), elbowR=(-15, 0, 0), head=(0, 0, 0),
         spine=(0, 0, 0))
    # buzz → raise phone → stunned
    pose(J, 126, shoulderR=(-30, 0, -10), elbowR=(-110, 0, 0), handR=(0, 0, 0), head=(10, 0, -20))
    for i, f in enumerate(range(124, 140, 2)):
        key(phone, f, loc=(0.004 * (1 if i % 2 else -1), -0.035, -0.07))
    key(phone, 142, loc=(0.0, -0.035, -0.07))
    key_socket(scr_es, 118, 0.3); key_socket(scr_es, 124, 2.0)
    pose(J, 150, shoulderR=(-38, 0, -12), elbowR=(-118, 0, 0), head=(16, 0, -28), spine=(-6, 0, 0),
         shoulderL=(-10, 0, 25), elbowL=(-30, 0, 0))
    pose(J, n, shoulderR=(-38, 0, -12), elbowR=(-120, 0, 0), head=(18, 0, -30), spine=(-8, 0, 0),
         shoulderL=(-12, 0, 28), elbowL=(-32, 0, 0))
    sun = light(coll, "sun", "SUN", (0, 0, 10), 3.5, (1, 0.95, 0.85))
    sun.rotation_euler = (R(50), R(0), R(-35))
    cam, tgt = camera(sc, coll, (0.6, -1.8, 1.45), (0, 4.5, 1.6), lens=35)
    key(tgt, 1, loc=(0, 5.5, 1.7)); key(tgt, stop, loc=(0, 1.2, 1.45)); key(tgt, n, loc=(0, 1.2, 1.55))
    key(cam, 1, loc=(0.6, -1.8, 1.45)); key(cam, stop, loc=(0.3, -0.6, 1.5)); key(cam, n, loc=(-0.1, 0.0, 1.6))


def build_s09(sc, coll):
    world(sc, (0.55, 0.7, 0.92), 0.8)
    cams = []
    # a) fuel price board under a canopy
    ox = 0
    floor(coll, mat("asphalt", (0.12, 0.12, 0.13), 0.8), size=200)
    cyl(coll, "pole", 0.06, 0.06, 3.0, (ox, 0.1, 1.5), mat("steel", (0.6, 0.6, 0.62), 0.3, 0.8))
    box(coll, "boardframe", (1.5, 0.12, 1.1), (ox, 0.0, 3.1), mat("boardred", (0.8, 0.15, 0.1), 0.5), bevel=0.02)
    img_plane(coll, "board", "price_board", 1.36, (ox, -0.065, 3.1), emit=0.6)
    box(coll, "canopy", (6, 4, 0.4), (ox + 1.5, 3, 4.8), mat("canopy", (0.95, 0.95, 0.95), 0.5))
    ca, ta = camera(sc, coll, (ox - 0.4, -2.4, 1.6), (ox, 0, 3.0), lens=35, name="camA")
    key(ca, 1, loc=(ox - 0.4, -2.4, 1.6)); key(ca, 36, loc=(ox - 0.2, -2.0, 1.75))
    cams.append(ca)
    # b) phone keyboard on a desk, finger presses ₹
    ox = 20
    box(coll, "desk9", (2, 2, 0.04), (ox, 0, 0.98), noisy_mat("desk9", (0.36, 0.22, 0.12), (0.46, 0.29, 0.16), 4, 0.5, 0.05))
    box(coll, "phone9", (0.36, 0.17, 0.012), (ox, 0, 1.006), mat("phone", (0.02, 0.02, 0.03), 0.2), bevel=0.01)
    img_plane(coll, "kbd", "keyboard", 0.33, (ox, 0, 1.0125), horizontal=True, emit=0.9)
    fing = cyl(coll, "finger9", 0.016, 0.018, 0.2, (0, 0, 0), mat(f"skin{SKIN_TONES[1]}", SKIN_TONES[1], 0.45),
               rot=(25, 0, 0))
    kx = ox - 0.33 / 2 + (40 + 3 * 152 + 70) / 1600 * 0.33
    ky = (700 / 2 - (30 + 70)) / 700 * (0.33 * 700 / 1600)
    key(fing, 37, loc=(kx, ky - 0.05, 1.14)); key(fing, 54, loc=(kx, ky - 0.045, 1.115))
    key(fing, 58, loc=(kx, ky - 0.043, 1.105)); key(fing, 64, loc=(kx, ky - 0.045, 1.12))
    cb, tb = camera(sc, coll, (ox + 0.05, -0.3, 1.3), (ox - 0.02, 0.0, 1.0), lens=40, name="camB")
    key(cb, 37, loc=(ox + 0.05, -0.3, 1.3)); key(cb, 72, loc=(ox + 0.04, -0.24, 1.24))
    cams.append(cb)
    # c) swinging price tag on a kurta
    ox = 40
    box(coll, "shopwall", (4, 0.1, 3), (ox, 0.5, 1.5), mat("shopwall", (0.9, 0.85, 0.75), 0.8))
    box(coll, "kurta9", (0.7, 0.08, 1.1), (ox - 0.15, 0.3, 1.3), noisy_mat("kurtacloth", (0.65, 0.08, 0.12), (0.75, 0.12, 0.15), 30, 0.9, 0.2), bevel=0.05)
    tagp = empty(coll, "tagpivot", (ox + 0.25, 0.2, 1.55))
    cyl(coll, "string", 0.002, 0.002, 0.2, (0, 0, -0.1), mat("string", (0.9, 0.9, 0.9), 0.5), tagp)
    img_plane(coll, "tag", "price_tag", 0.3, (0, -0.002, -0.28), tagp, emit=0.35)
    for f, a in ((73, 18), (82, -12), (91, 8), (100, -5), (108, 2)):
        key(tagp, f, rot=(0, a, 0))
    cc, tcc = camera(sc, coll, (ox + 0.2, -0.75, 1.35), (ox + 0.2, 0.2, 1.3), lens=45, name="camC")
    cams.append(cc)
    # d) payment success screen held in a hand
    ox = 60
    box(coll, "cafewall", (4, 0.1, 3), (ox, 1.0, 1.5), noisy_mat("cafewall", (0.4, 0.25, 0.18), (0.5, 0.33, 0.24), 3, 0.8, 0.1))
    ph = empty(coll, "phonegrp", (ox, 0, 1.4))
    ph.rotation_euler = (R(8), 0, R(-6))
    box(coll, "phone9d", (0.085, 0.01, 0.17), (0, 0, 0), mat("phone", (0.02, 0.02, 0.03), 0.2), ph, bevel=0.006)
    img_plane(coll, "pay", "pay_screen", 0.078, (0, -0.0055, 0), ph, emit=1.2)
    sphere(coll, "holdhand", 0.06, (0.0, 0.03, -0.09), mat(f"skin{SKIN_TONES[1]}", SKIN_TONES[1], 0.45), ph,
           scale=(1.2, 0.6, 1.0))
    cd_, td = camera(sc, coll, (ox, -0.6, 1.42), (ox, 0, 1.4), lens=45, name="camD")
    key(cd_, 109, loc=(ox, -0.6, 1.42)); key(cd_, 144, loc=(ox, -0.36, 1.41))
    cams.append(cd_)
    for i, f in enumerate((1, 37, 73, 109)):
        mk = sc.timeline_markers.new(f"cut{i}", frame=f)
        mk.camera = cams[i]
    sc.camera = cams[0]
    sun = light(coll, "sun", "SUN", (0, 0, 10), 3.0, (1, 0.96, 0.9))
    sun.rotation_euler = (R(40), R(10), R(-25))
    for ox in (20, 40, 60):
        light(coll, f"soft{ox}", "AREA", (ox - 0.6, -1.2, 2.2), 120, (1, 0.95, 0.88), 2, (ox, 0, 1.2))


BUILDERS = {
    "S01": lambda s, c: build_hook(s, c, loop=False), "S02": build_s02, "S03": build_s03, "S04": build_s04,
    "S05": build_s05, "S06": build_s06, "S07": build_s07, "S08": build_s08, "S09": build_s09,
    "S10": lambda s, c: build_hook(s, c, loop=True),
}

QUALITY = {
    "draft": {"res": (540, 960), "engine": "BLENDER_EEVEE", "samples": 4},
    "final": {"res": (1080, 1920), "engine": "BLENDER_EEVEE", "samples": 48, "raytrace": False},
}


def extra_textures():
    """Small textures only this script needs."""
    from PIL import Image, ImageDraw
    out = {}
    p = os.path.join(textures.OUT, "submit.png")
    if not os.path.exists(p):
        im = Image.new("RGB", (1200, 800), (24, 60, 140))
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 1200, 120], fill=(14, 36, 90))
        d.text((600, 60), "rupee symbol competition", font=textures.font(textures.INTER_SB, 54), fill=(220, 230, 255), anchor="mm")
        d.text((600, 330), "SUBMIT YOUR", font=textures.font(textures.INTER_XB, 130), fill=(255, 255, 255), anchor="mm")
        d.text((600, 480), "DESIGN", font=textures.font(textures.INTER_XB, 150), fill=(255, 200, 60), anchor="mm")
        d.rounded_rectangle([400, 590, 800, 700], radius=50, fill=(255, 140, 30))
        d.text((600, 645), "UPLOAD", font=textures.font(textures.INTER_B, 60), fill=(255, 255, 255), anchor="mm")
        im.save(p)
    out["submit"] = p
    p = os.path.join(textures.OUT, "phone_news.png")
    if not os.path.exists(p):
        im = Image.new("RGB", (600, 1300), (16, 18, 26))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([40, 300, 560, 820], radius=40, fill=(245, 245, 248))
        d.text((300, 380), "BREAKING", font=textures.font(textures.INTER_XB, 64), fill=(220, 40, 40), anchor="mm")
        d.text((300, 560), "₹", font=textures.font(textures.DEVA_B, 260), fill=(20, 20, 26), anchor="mm")
        d.text((300, 740), "Your design is selected!", font=textures.font(textures.INTER_B, 38), fill=(40, 40, 50), anchor="mm")
        im.save(p)
    out["phone_news"] = p
    return out


def build(quality, only=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _MATS.clear()
    TEX.update(textures.build_all())
    TEX.update(extra_textures())
    for name in DUR:
        if only and name not in only:
            continue
        sc, coll = new_scene(name, quality)
        BUILDERS[name](sc, coll)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true")
    ap.add_argument("--render")
    ap.add_argument("--quality", default="draft")
    ap.add_argument("--frames")
    ap.add_argument("--step", type=int, default=1)
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])
    if a.save:
        build(a.quality)
        for img in bpy.data.images:
            if img.filepath:
                img.filepath = bpy.path.relpath(img.filepath, start=HERE)
        bpy.context.preferences.filepaths.save_version = 0  # no .blend1 backups
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "rupee_short.blend"), relative_remap=True)
        print("saved", os.path.join(HERE, "rupee_short.blend"))
    if a.render:
        build(a.quality, only=[a.render])
        sc = bpy.data.scenes[a.render]
        if a.frames:
            s, e = (int(x) for x in a.frames.split("-"))
            sc.frame_start, sc.frame_end = s, e
        sc.frame_step = a.step
        bpy.ops.render.render(animation=True, scene=sc.name)


if __name__ == "__main__":
    main()
