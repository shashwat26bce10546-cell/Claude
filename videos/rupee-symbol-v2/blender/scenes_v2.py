"""₹ Short v2 — six cinematic 3D shots (dramatic light, teal mannequin crowds, DOF, 3D word labels).

  python3 scenes_v2.py --save                                  # rupee_v2.blend with scenes A, C, E, F, G, I
  python3 scenes_v2.py --render E --quality draft [--frames 1-144]
"""
import argparse
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib3d as L  # noqa: E402  (imports bpy)
import bpy  # noqa: E402
from lib3d import (R, box, cyl, sphere, plane, img_plane, text, empty, key, pose, seat, mat, noisy_mat,  # noqa: E402
                   checker_mat, reveal_mat, key_socket, light, camera, floor, world, figure, mannequin, dof,
                   label3d, crumple, udaya, SKIN_TONES)

L.DUR.update({"A": 84, "C": 120, "E": 144, "F": 168, "G": 120, "I": 168})
L.QUALITY.update({
    "draft": {"res": (540, 960), "engine": "BLENDER_EEVEE", "samples": 4},
    "final": {"res": (1080, 1920), "engine": "BLENDER_EEVEE", "samples": 6},
})
L.HERE = HERE  # renders/ and tex/ live next to this file
YELLOW = (1.0, 0.78, 0.08)
BLUE = (0.15, 0.55, 1.0)
SAFFRON = (1.0, 0.45, 0.05)


def walk(J, f0, f1, p0, p1, period=24, step=6, arms=True):
    """Simple walk cycle moving the root from p0 to p1 between frames f0..f1."""
    for f in range(f0, f1 + 1, step):
        t = (f - f0) / max(1, f1 - f0)
        ph = math.sin((f - f0) / period * math.tau)
        bob = abs(math.cos((f - f0) / period * math.tau)) * 0.025
        loc = tuple(a + (b - a) * t for a, b in zip(p0, p1))
        kw = dict(root_loc=(loc[0], loc[1], loc[2] + bob), hipL=(25 * ph, 0, 0), hipR=(-25 * ph, 0, 0),
                  kneeL=(max(0, -30 * ph), 0, 0), kneeR=(max(0, 30 * ph), 0, 0))
        if arms:
            kw.update(shoulderL=(-20 * ph, 0, 6), shoulderR=(20 * ph, 0, -6), elbowL=(-15, 0, 0), elbowR=(-15, 0, 0))
        pose(J, f, **kw)


def pop(ob, f, s=1.0, dur=6):
    """Scale-pop an object in at frame f."""
    key(ob, f - 1, scale=0.0)
    key(ob, f + dur, scale=s * 1.12)
    key(ob, f + dur + 4, scale=s)


# ---------------------------------------------------------------- A: night plaza, giant ₹, teal crowd

def build_A(sc, coll):
    world(sc, (0.01, 0.015, 0.04), 1.0)
    floor(coll, noisy_mat("plaza", (0.05, 0.05, 0.06), (0.09, 0.09, 0.1), 6, 0.6, 0.2), size=80)
    # skyline silhouettes
    rnd = random.Random(2)
    m_bld = mat("bld", (0.02, 0.025, 0.04), 0.9)
    m_win = mat("win", (1, 0.75, 0.35), 0.5, emit=(1, 0.7, 0.3), emit_strength=2.0)
    for i in range(16):
        x = -14 + i * 1.9 + rnd.uniform(-0.4, 0.4)
        h = rnd.uniform(3, 9)
        box(coll, f"bld{i}", (1.6, 1.6, h), (x, 14 + rnd.uniform(0, 4), h / 2), m_bld)
        for k in range(int(h // 1.4)):
            if rnd.random() < 0.45:
                plane(coll, f"win{i}_{k}", 0.25, 0.35, (x + rnd.uniform(-0.5, 0.5), 13.18, 0.8 + k * 1.3), m_win)
    # pedestal + giant ₹
    m_stone = noisy_mat("pedestal", (0.25, 0.24, 0.23), (0.32, 0.31, 0.3), 10, 0.5, 0.1)
    box(coll, "pedestal", (2.2, 1.4, 0.8), (0, 0, 0.4), m_stone, bevel=0.04)
    box(coll, "pedestal2", (1.8, 1.1, 0.25), (0, 0, 0.92), m_stone, bevel=0.03)
    m_gold = mat("gold", (0.95, 0.38, 0.03), 0.3, 0.85, emit=SAFFRON, emit_strength=0.0)
    ru = text(coll, "giant_rupee", "₹", 2.6, (0, 0, 2.15), m_gold, rot=(90, 0, 0), extrude=0.18)
    b = m_gold.node_tree.nodes.get("Principled BSDF")
    key_socket(b.inputs["Emission Strength"], 1, 0.2)
    key_socket(b.inputs["Emission Strength"], 30, 0.7)
    key(ru, 1, rot=(90, 0, -18))
    key(ru, DUR("A"), rot=(90, 0, 10))
    # crowd of teal mannequins looking up
    rnd2 = random.Random(9)
    i = 0
    for row, y in enumerate((-1.4, -2.1, -2.8, -3.4)):
        for x in (-1.55, -1.0, -0.55, 0.55, 1.0, 1.55):
            if row == 3 and abs(x) < 0.6:
                continue
            xx, yy = x + rnd2.uniform(-0.12, 0.12), y + rnd2.uniform(-0.15, 0.15)
            J = mannequin(coll, f"m{i}")
            J["root"].location = (xx, yy, 0)
            J["root"].rotation_euler = (0, 0, math.pi + math.atan2(-xx, -yy) * 0.5 + math.pi)
            pose(J, 1, head=(-24 - (i % 4) * 5, 0, 0))
            if i % 3 == 0:
                pose(J, 1, shoulderR=(-150, 0, -10), elbowR=(-10, 0, 0))
                pose(J, 40, shoulderR=(-165, 0, -10), elbowR=(-25, 0, 0))
                pose(J, DUR("A"), shoulderR=(-150, 0, -10), elbowR=(-10, 0, 0))
            i += 1
    # light: warm uplights on the monument, cold moon rim
    for x in (-1.6, 1.6):
        light(coll, f"up{x}", "SPOT", (x, -1.4, 0.2), 900, (1, 0.7, 0.35), 0.1, (0, 0, 2.3), spot=40)
    light(coll, "moon", "AREA", (3, 6, 6), 800, (0.4, 0.55, 1), 4, (0, 0, 1))
    light(coll, "crowdfill", "AREA", (0, -6, 3), 150, (0.5, 0.65, 1), 4, (0, -2, 1))
    cam, tgt = camera(sc, coll, (0.0, -9.0, 0.7), (0, 0, 2.3), lens=24)
    key(cam, 1, loc=(0.0, -8.5, 0.75)); key(cam, DUR("A"), loc=(0.0, -4.6, 1.0))
    key(tgt, 1, loc=(0, 0, 2.6)); key(tgt, DUR("A"), loc=(0, 0, 2.2))
    dof(cam, ru, 2.8)


# ---------------------------------------------------------------- C: entries pour in (night hall)

def build_C(sc, coll):
    n = DUR("C")
    world(sc, (0.01, 0.012, 0.025), 1.0)
    floor(coll, checker_mat("hall", (0.09, 0.09, 0.1), (0.07, 0.07, 0.08), 20, 0.3))
    box(coll, "wall", (16, 0.2, 6), (0, 5.5, 3), mat("hallwall", (0.06, 0.07, 0.09), 0.8))
    m_desk = mat("desk_dark", (0.25, 0.16, 0.1), 0.45)
    starts = []
    for i in range(10):
        row, col = divmod(i, 5)
        x, y = (col - 2) * 1.45 + (0.5 if row else 0), 1.6 + row * 1.7
        box(coll, f"desk{i}", (1.0, 0.6, 0.05), (x, y - 0.45, 0.72), m_desk)
        box(coll, f"dlegs{i}", (0.95, 0.55, 0.68), (x, y - 0.45, 0.35), mat("dleg", (0.04, 0.04, 0.05), 0.5))
        box(coll, f"chair{i}", (0.4, 0.4, 0.45), (x, y + 0.05, 0.225), mat("chair_d", (0.05, 0.05, 0.06), 0.6))
        J = mannequin(coll, f"c{i}")
        J["root"].location = (x, y, 0)
        seat(J, 1)
        for f in range(1, n + 1, 10):
            k = ((f + i * 5) // 10) % 2
            pose(J, f, shoulderR=(-55, 0, -10), elbowR=(-40 - 12 * k, 0, 0),
                 shoulderL=(-45, 0, 10), elbowL=(-50, 0, 0), head=(18 + 4 * k, 0, 0))
        light(coll, f"desklamp{i}", "SPOT", (x, y - 0.45, 2.6), 120, (1, 0.85, 0.65), 0.1, (x, y - 0.45, 0.7), spot=50)
        starts.append((x, y - 0.45, 0.8))
    # glowing ENTRIES box
    m_card = noisy_mat("cardboard", (0.55, 0.4, 0.24), (0.6, 0.45, 0.28), 30, 0.85, 0.1)
    bx, by = 0, -0.9
    for (sx, sy, lx, ly) in ((0.9, 0.04, 0, -0.33), (0.9, 0.04, 0, 0.33), (0.04, 0.7, -0.45, 0), (0.04, 0.7, 0.45, 0)):
        box(coll, "cbox", (sx, sy, 0.6), (bx + lx, by + ly, 0.3), m_card)
    img_plane(coll, "entries_label", "entries", 0.7, (bx, by - 0.355, 0.33), emit=0.6)
    plane(coll, "boxglow", 0.85, 0.65, (bx, by, 0.5), mat("glow", (1, 0.8, 0.4), 0.5, emit=(1, 0.75, 0.35),
                                                          emit_strength=6), horizontal=True)
    light(coll, "boxlight", "POINT", (bx, by, 0.9), 220, (1, 0.75, 0.4), 0.3)
    m_env = mat("envelope", (0.95, 0.93, 0.88), 0.5, emit=(1, 1, 1), emit_strength=0.15)
    rnd = random.Random(3)
    for i in range(46):
        e = box(coll, f"env{i}", (0.18, 0.12, 0.006), (0, 0, 0), m_env)
        sx, sy, sz = starts[i % 10]
        t0 = 2 + int(i * 2.1)
        t1 = t0 + 18
        ex, ey = bx + rnd.uniform(-0.25, 0.25), by + rnd.uniform(-0.2, 0.2)
        e.scale = (0, 0, 0); e.keyframe_insert("scale", frame=t0 - 1)
        key(e, t0, loc=(sx, sy, sz), rot=(0, 0, 0), scale=(0.18, 0.12, 0.006))
        key(e, (t0 + t1) // 2, loc=((sx + ex) / 2, (sy + ey) / 2, 2.4 + rnd.uniform(0, 0.6)),
            rot=(rnd.uniform(-180, 180), rnd.uniform(-90, 90), rnd.uniform(-180, 180)))
        key(e, t1, loc=(ex, ey, 0.55), rot=(rnd.uniform(-20, 20), rnd.uniform(-20, 20), rnd.uniform(0, 180)))
        key(e, t1 + 3, loc=(ex, ey, 0.35), scale=(0.18, 0.12, 0.006))
        key(e, t1 + 4, scale=(0, 0, 0))
    # floating 3D words
    for j, (word, x, z, f) in enumerate((("DESIGNERS", -1.6, 2.5, 18), ("STUDENTS", 1.5, 2.9, 44), ("ARTISTS", -0.2, 3.4, 70))):
        lb = label3d(coll, f"lbl{j}", word, 0.42, (x, 1.8, z), rot=(90, 0, (-1) ** j * 8),
                     color=YELLOW if j != 1 else BLUE, emit=2.2)
        pop(lb, f)
    light(coll, "rim", "AREA", (0, 6, 4), 500, (0.4, 0.55, 1), 6, (0, 1, 1))
    # orbiting low camera around the box
    cam, tgt = camera(sc, coll, (2.4, -4.4, 0.7), (0, 0.4, 1.0), lens=22)
    for f, ang in ((1, -28), (n // 2, -10), (n, 8)):
        a = math.radians(ang)
        key(cam, f, loc=(math.sin(a) * 4.6, by - math.cos(a) * 4.6 + 0.6, 0.65 + 0.15 * (f / n)))
    dof(cam, tgt, 4.0)


# ---------------------------------------------------------------- E: hostel, hero at desk, rack focus

def build_E(sc, coll):
    n = DUR("E")
    world(sc, (0.01, 0.015, 0.04), 1.0)
    floor(coll, mat("hostelfloor", (0.12, 0.1, 0.09), 0.6))
    m_wall = mat("hostelwall", (0.22, 0.25, 0.3), 0.85)
    box(coll, "backwall", (6, 0.15, 3.2), (0, 1.5, 1.6), m_wall)
    box(coll, "sidewall", (0.15, 6, 3.2), (-1.8, 0, 1.6), m_wall)
    box(coll, "rightwall", (0.15, 6, 3.2), (2.4, 0, 1.6), m_wall)
    # doorway frame the camera passes through
    m_door = mat("doorframe", (0.08, 0.06, 0.05), 0.6)
    for x in (-0.95, 0.75):
        box(coll, f"doorjamb{x}", (0.12, 0.2, 2.3), (x, -2.4, 1.15), m_door)
    box(coll, "doorhead", (1.85, 0.2, 0.15), (-0.1, -2.4, 2.35), m_door)
    for x0, x1 in ((-1.9, -1.01), (0.81, 2.5)):
        box(coll, f"frontwall{x0}", (x1 - x0, 0.15, 3.2), ((x0 + x1) / 2, -2.45, 1.6), m_wall)
    img_plane(coll, "poster", "poster", 0.5, (-0.6, 1.42, 1.75), emit=0.05)
    img_plane(coll, "calendar", "calendar", 0.3, (0.35, 1.42, 1.65), emit=0.08)
    plane(coll, "window", 0.7, 0.9, (-1.72, 0.2, 1.7), mat("night", (0.1, 0.15, 0.35), 0.2, emit=(0.15, 0.25, 0.6),
                                                           emit_strength=1.5), rot=(0, 0, -90))
    m_desk = mat("hosteldesk", (0.42, 0.28, 0.17), 0.55)
    box(coll, "desk", (1.2, 0.65, 0.05), (0, 0, 0.74), m_desk, bevel=0.01)
    box(coll, "deskfront", (1.2, 0.03, 0.66), (0, -0.31, 0.38), m_desk)
    J = udaya(coll)
    J["root"].location = (0.05, 0.55, 0)
    seat(J, 1)
    box(coll, "chair", (0.44, 0.44, 0.45), (0.05, 0.6, 0.225), mat("chair4", (0.2, 0.2, 0.24), 0.6))
    plane(coll, "sheet", 0.3, 0.4, (0.0, 0.05, 0.768), mat("sheet", (0.95, 0.94, 0.9), 0.7), horizontal=True, rot=(0, 0, 8))
    for f in range(1, n + 1, 8):
        k = (f // 8) % 2
        pose(J, f, shoulderR=(-62, 0, -18), elbowR=(-38 - 10 * k, 0, 0), handR=(10, 0, 0),
             shoulderL=(-50, 0, 15), elbowL=(-55, 0, 0), spine=(10, 0, 0), head=(10 + 3 * k, 0, 4 * k))
    # he looks up at the camera at the end — a beat of eye contact
    pose(J, 112, head=(10, 0, 0), spine=(10, 0, 0))
    pose(J, 126, head=(-6, 0, 12), spine=(4, 0, 0))
    m_lamp = mat("lamp", (0.1, 0.1, 0.12), 0.35, 0.5)
    cyl(coll, "lampbase", 0.08, 0.08, 0.03, (0.45, 0.15, 0.78), m_lamp)
    cyl(coll, "lamparm", 0.012, 0.012, 0.45, (0.45, 0.12, 0.99), m_lamp, rot=(-15, 0, 0))
    cyl(coll, "lampshade", 0.03, 0.11, 0.12, (0.42, -0.0, 1.2), m_lamp, rot=(-140, 0, 20))
    light(coll, "lampspot", "SPOT", (0.38, -0.05, 1.17), 160, (1, 0.7, 0.38), 0.05, (0.0, 0.1, 0.76), spot=85)
    light(coll, "lampglow", "POINT", (0.4, -0.02, 1.13), 20, (1, 0.7, 0.4), 0.05)
    light(coll, "moon", "AREA", (-1.6, 0.2, 1.8), 70, (0.45, 0.6, 1), 0.8, (0.1, 0.4, 0.9))
    light(coll, "rimblue", "AREA", (1.6, 1.3, 2.2), 60, (0.4, 0.5, 1), 1.0, (0.05, 0.5, 1.1))
    m_crump = mat("crumple", (0.92, 0.9, 0.85), 0.8)
    rnd = random.Random(11)
    for i in range(16):
        on_desk = i < 4
        loc = ((rnd.uniform(-0.5, -0.2) if on_desk else rnd.uniform(-1.3, 1.6)),
               (rnd.uniform(-0.2, 0.2) if on_desk else rnd.uniform(-1.8, 1.2)),
               0.8 if on_desk else 0.035)
        crumple(coll, f"ball{i}", 0.04, loc, m_crump, i)
    # bunk with a sleeping teal roommate
    m_bed = mat("bed", (0.3, 0.32, 0.36), 0.4, 0.6)
    for x in (1.2, 2.1):
        for y in (0.4, 1.3):
            box(coll, f"bedpost{x}{y}", (0.05, 0.05, 1.8), (x, y, 0.9), m_bed)
    for z in (0.45, 1.4):
        box(coll, f"mattress{z}", (0.95, 0.95, 0.12), (1.65, 0.85, z), mat("mattress", (0.5, 0.2, 0.2), 0.9))
    Jm = mannequin(coll, "roommate")
    Jm["root"].location = (1.65, 1.6, 0.6)
    Jm["root"].rotation_euler = (R(-90), 0, 0)
    cam, tgt = camera(sc, coll, (-0.1, -3.6, 1.45), (0.05, 0.4, 1.05), lens=30)
    key(cam, 1, loc=(-0.1, -3.6, 1.45)); key(cam, 70, loc=(-0.25, -1.5, 1.3)); key(cam, n, loc=(-0.3, -1.05, 1.22))
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = 1.8
    cam.data.dof.focus_distance = 1.2
    cam.data.dof.keyframe_insert("focus_distance", frame=1)
    cam.data.dof.focus_distance = 1.2
    cam.data.dof.keyframe_insert("focus_distance", frame=14)
    cam.data.dof.focus_distance = 3.9
    cam.data.dof.keyframe_insert("focus_distance", frame=34)
    cam.data.dof.focus_distance = 2.0
    cam.data.dof.keyframe_insert("focus_distance", frame=70)
    cam.data.dof.focus_distance = 1.55
    cam.data.dof.keyframe_insert("focus_distance", frame=n)


# ---------------------------------------------------------------- F: र + R → ₹ with floating labels

def build_F(sc, coll):
    n = DUR("F")
    world(sc, (0.05, 0.045, 0.04), 0.4)
    box(coll, "desktop", (2, 2, 0.04), (0, 0, -0.02), noisy_mat("desk5", (0.2, 0.12, 0.07), (0.28, 0.17, 0.1), 4, 0.5, 0.05))
    img_plane(coll, "paper", "paper_plain", 0.32, (0, 0.0, 0.001), horizontal=True, emit=0.03)
    graphite = (0.03, 0.03, 0.035)
    m_ra, thr_ra, op_ra, _ = reveal_mat("ra_mat", graphite)
    m_r, thr_r, op_r, _ = reveal_mat("r_mat", graphite)
    m_ru, thr_ru, op_ru, em_ru = reveal_mat("rupee_mat", (0.8, 0.22, 0.0), emit=(1.0, 0.35, 0.0))
    ra = text(coll, "ra", "र", 0.15, (-0.06, 0.02, 0.002), m_ra, font=L.FONT_DEVA_REG)
    rr = text(coll, "R", "R", 0.10, (0.055, 0.02, 0.002), m_r, font=L.FONT_INTER)
    ru = text(coll, "rupee", "₹", 0.17, (0, 0.0, 0.002), m_ru, font=L.FONT_DEVA)
    key_socket(thr_ra, 1, -0.06); key_socket(thr_ra, 40, 0.06)
    key_socket(thr_r, 1, -0.06); key_socket(thr_r, 46, -0.06); key_socket(thr_r, 84, 0.06)
    key_socket(thr_ru, 1, 1.0)
    for op, a, b in ((op_ra, 1.0, 0.0), (op_r, 1.0, 0.0)):
        key_socket(op, 1, a); key_socket(op, 96, a); key_socket(op, 116, b)
    key_socket(op_ru, 1, 0.0); key_socket(op_ru, 100, 0.0); key_socket(op_ru, 120, 1.0)
    key_socket(em_ru, 1, 0.0); key_socket(em_ru, 120, 0.0); key_socket(em_ru, 140, 0.8); key_socket(em_ru, n, 0.6)
    key(ra, 96, loc=(-0.06, 0.02, 0.002)); key(ra, 118, loc=(-0.005, 0.0, 0.002))
    key(rr, 96, loc=(0.055, 0.02, 0.002)); key(rr, 118, loc=(0.005, 0.0, 0.002))
    key(ru, 1, scale=0.8); key(ru, 100, scale=0.8); key(ru, 124, scale=1.0)
    # floating labels hovering over the paper, casting shadows
    font = os.path.join(L.textures.FONTS, "Inter-ExtraBold.otf")
    lbls = [("DEVANAGARI", (-0.045, 0.085, 0.03), YELLOW, 12, 112), ("ROMAN", (0.055, 0.085, 0.03), BLUE, 58, 112),
            ("TIRANGA", (-0.04, 0.075, 0.03), SAFFRON, 132, None), ("EQUALITY", (0.04, -0.07, 0.03), (0.2, 0.75, 0.3), 144, None)]
    for j, (word, loc, col, f_in, f_out) in enumerate(lbls):
        lb = label3d(coll, f"flbl{j}", word, 0.014, loc, rot=(20, 0, 0), color=col, emit=1.6, font=font, extrude=0.002)
        pop(lb, f_in, dur=5)
        if f_out:
            key(lb, f_out, scale=1.0)
            key(lb, f_out + 6, scale=0.0)
    m_y = mat("pencil_y", (0.95, 0.72, 0.1), 0.4)
    pencil = empty(coll, "pencil")
    cyl(coll, "pencil_body", 0.0075, 0.0075, 0.16, (0, 0, 0.1), m_y, pencil, seg=6)
    cyl(coll, "pencil_wood", 0.0075, 0.0015, 0.02, (0, 0, 0.01), mat("pencil_wood", (0.85, 0.65, 0.45), 0.7), pencil,
        seg=6, rot=(180, 0, 0))
    cyl(coll, "pencil_eraser", 0.0078, 0.0078, 0.015, (0, 0, 0.185), mat("eraser", (0.9, 0.4, 0.45), 0.6), pencil)
    pencil.rotation_euler = (R(-40), R(35), 0)
    for f in range(1, 41, 4):
        t = (f - 1) / 39
        key(pencil, f, loc=(-0.06 - 0.05 + 0.1 * t, 0.02 + 0.03 * math.sin(f * 0.9), 0.004))
    key(pencil, 44, loc=(0.02, 0.05, 0.03))
    for f in range(48, 85, 4):
        t = (f - 48) / 36
        key(pencil, f, loc=(0.055 - 0.04 + 0.08 * t, 0.02 + 0.035 * math.sin(f * 0.8), 0.004))
    key(pencil, 96, loc=(0.16, 0.08, 0.06)); key(pencil, n, loc=(0.22, 0.12, 0.08))
    light(coll, "key", "SPOT", (-0.35, -0.25, 0.55), 18, (1, 0.85, 0.7), 0.05, (0, 0, 0), spot=55)
    light(coll, "fill", "AREA", (0.5, -0.2, 0.4), 2.5, (0.6, 0.75, 1), 0.5, (0, 0, 0))
    cam, tgt = camera(sc, coll, (-0.05, -0.2, 0.34), (0, 0.01, 0), lens=42)
    key(cam, 1, loc=(-0.05, -0.2, 0.34)); key(cam, 100, loc=(0.0, -0.16, 0.31))
    key(cam, n, loc=(0.05, -0.15, 0.28))
    dof(cam, tgt, 2.2)


# ---------------------------------------------------------------- G: committee, dramatic spots

def build_G(sc, coll):
    n = DUR("G")
    world(sc, (0.01, 0.01, 0.015), 1.0)
    floor(coll, mat("carpet", (0.2, 0.06, 0.05), 0.95))
    m_panel = noisy_mat("panel", (0.12, 0.07, 0.04), (0.18, 0.1, 0.06), 2, 0.5, 0.05)
    box(coll, "backwall", (8, 0.2, 4), (0, 3.2, 2), m_panel)
    box(coll, "leftwall", (0.2, 8, 4), (-2.6, 0, 2), m_panel)
    img_plane(coll, "banner", "committee", 2.4, (0, 3.08, 2.6), emit=0.5)
    m_tab = noisy_mat("committee_table", (0.18, 0.09, 0.05), (0.25, 0.13, 0.07), 3, 0.3, 0.03)
    box(coll, "table", (0.9, 3.2, 0.06), (-1.2, 0.6, 0.75), m_tab, bevel=0.01)
    box(coll, "tablebase", (0.8, 3.0, 0.7), (-1.2, 0.6, 0.36), m_tab)
    kurtas = [(0.3, 0.3, 0.32), (0.25, 0.2, 0.15), (0.6, 0.58, 0.55), (0.2, 0.22, 0.28), (0.35, 0.3, 0.25)]
    for i in range(5):
        y = -0.6 + i * 0.6
        J = figure(coll, f"o{i}", kurtas[i], (0.15, 0.15, 0.17), skin=SKIN_TONES[(i + 1) % 4], hair=(0.6, 0.6, 0.6),
                   glasses=(i != 2), long_kurta=True, bald=(i == 3))
        J["root"].location = (-1.75, y, 0)
        J["root"].rotation_euler = (0, 0, R(90))
        seat(J, 1)
        pose(J, 1, shoulderL=(-40, 0, 10), elbowL=(-60, 0, 0), shoulderR=(-40, 0, -10), elbowR=(-60, 0, 0),
             head=(0, 0, -10 + i * 3))
        pose(J, n, head=(0, 0, -25 + i * 2))
        box(coll, f"seat{i}", (0.45, 0.45, 0.46), (-1.8, y, 0.23), mat("seat6", (0.3, 0.05, 0.05), 0.7))
        box(coll, f"seatback{i}", (0.05, 0.45, 0.6), (-2.05, y, 0.75), mat("seat6", (0.3, 0.05, 0.05), 0.7))
        light(coll, f"pendant{i}", "SPOT", (-1.2, y, 2.4), 220, (1, 0.85, 0.6), 0.1, (-1.4, y, 0.9), spot=55)
    order = [0, 1, 4, 3, 2]
    m_easel = mat("easel", (0.35, 0.22, 0.12), 0.6)
    lights = []
    for i, d in enumerate(order):
        y = -1.2 + i * 0.95
        g = empty(coll, f"easel{i}", (0.85, y, 0))
        g.rotation_euler = (0, 0, R(-28))
        for lx in (-0.25, 0.25):
            box(coll, f"easel_leg{i}{lx}", (0.035, 0.035, 1.7), (lx, 0.1, 0.82), m_easel, g, rot=(-6, 0, lx * 18))
        box(coll, f"easel_tray{i}", (0.6, 0.06, 0.03), (0, -0.02, 0.85), m_easel, g)
        _, es = img_plane(coll, f"card{i}", f"design{d}", 0.5, (0, -0.04, 1.17), g, emit=0.5)
        Ls = light(coll, f"spot{i}", "SPOT", (0.6, y - 0.4, 2.6), 260, (1, 0.92, 0.8), 0.1, (0.85, y, 1.15), spot=30)
        lights.append((Ls, es, d))
    off = {0: 24, 1: 38, 3: 52, 2: 66}
    for Ls, es, d in lights:
        if d in off:
            f = off[d]
            Ls.data.energy = 260; Ls.data.keyframe_insert("energy", frame=f - 3)
            Ls.data.energy = 2; Ls.data.keyframe_insert("energy", frame=f + 1)
            key_socket(es, f - 3, 0.5); key_socket(es, f + 1, 0.01)
        else:
            Ls.data.energy = 260; Ls.data.keyframe_insert("energy", frame=66)
            Ls.data.energy = 600; Ls.data.keyframe_insert("energy", frame=78)
            key_socket(es, 66, 0.5); key_socket(es, 78, 1.1)
    light(coll, "roomfill", "AREA", (0.5, -2.5, 2.8), 260, (1, 0.85, 0.7), 4, (-0.5, 0.6, 0.8))
    cam, tgt = camera(sc, coll, (0.4, -3.4, 0.6), (-0.3, 0.5, 1.0), lens=22)
    key(cam, 1, loc=(0.4, -3.4, 0.6)); key(tgt, 1, loc=(-0.3, 0.5, 1.0))
    key(cam, 68, loc=(0.3, -2.9, 0.75)); key(tgt, 68, loc=(-0.2, 0.55, 1.0))
    key(cam, n, loc=(0.3, 0.08, 1.15)); key(tgt, n, loc=(0.85, 0.7, 1.17))
    dof(cam, tgt, 2.5)


# ---------------------------------------------------------------- I: campus at golden hour

def build_I(sc, coll):
    n = DUR("I")
    world(sc, (0.95, 0.55, 0.35), 0.6)
    floor(coll, noisy_mat("grass", (0.1, 0.22, 0.05), (0.18, 0.32, 0.08), 6, 0.9, 0.4), size=120)
    box(coll, "path", (2.6, 30, 0.02), (0, 3, 0.005), noisy_mat("path", (0.45, 0.4, 0.36), (0.52, 0.47, 0.42), 10, 0.9, 0.1))
    m_pillar = mat("gatepillar", (0.6, 0.28, 0.18), 0.7)
    m_cream = mat("cream", (0.9, 0.84, 0.72), 0.6)
    for x in (-1.6, 1.6):
        box(coll, f"gatepillar{x}", (0.6, 0.6, 3.2), (x, 6, 1.6), m_pillar, bevel=0.02)
        box(coll, f"gatecap{x}", (0.75, 0.75, 0.2), (x, 6, 3.3), m_cream, bevel=0.02)
    box(coll, "gatebeam", (3.8, 0.4, 0.55), (0, 6, 3.05), m_cream, bevel=0.02)
    img_plane(coll, "gatesign", "gate_sign", 3.0, (0, 5.79, 3.05), emit=0.3)
    m_hill = noisy_mat("hill", (0.25, 0.22, 0.3), (0.32, 0.28, 0.36), 1.5, 0.95, 0.5)
    for i, (x, y, r) in enumerate(((-14, 40, 14), (6, 46, 18), (24, 38, 12), (-30, 50, 16))):
        sphere(coll, f"hill{i}", r, (x, y, -r * 0.55), m_hill, scale=(1.4, 1, 0.8))
    m_trunk = mat("trunk", (0.2, 0.12, 0.07), 0.8)
    m_leaf = noisy_mat("leaf", (0.12, 0.2, 0.05), (0.25, 0.32, 0.08), 5, 0.8, 0.4)
    rnd = random.Random(5)
    for i in range(14):
        x = rnd.choice((-1, 1)) * rnd.uniform(2.8, 9)
        y = rnd.uniform(4, 22)
        cyl(coll, f"trunk{i}", 0.12, 0.15, 1.6, (x, y, 0.8), m_trunk)
        sphere(coll, f"crown{i}", rnd.uniform(0.9, 1.4), (x, y, 2.3), m_leaf, scale=(1, 1, 1.15), seg=16)
    # teal students crossing the frame in the background
    for k in range(7):
        Jm = mannequin(coll, f"st{k}")
        y = 4.0 + (k % 3) * 1.6
        x0, x1 = (-6, 6) if k % 2 else (6, -6)
        Jm["root"].rotation_euler = (0, 0, R(-90 if k % 2 else 90))
        walk(Jm, 1 + k * 5, n, (x0 + k * 0.7, y, 0), (x1 + k * 0.7, y, 0), period=26, step=6)
    J = udaya(coll)
    box(coll, "bag", (0.3, 0.16, 0.4), (0, 0.18, 0.28), mat("bag", (0.15, 0.2, 0.35), 0.7), J["spine"], bevel=0.04)
    phone = box(coll, "phone", (0.075, 0.009, 0.15), (0.0, -0.035, -0.07), mat("phone", (0.02, 0.02, 0.03), 0.2),
                J["handR"], bevel=0.005)
    scr, scr_es = img_plane(coll, "phone_screen", "phone_news", 0.066, (0.0, -0.041, -0.07), J["handR"], emit=0.3)
    stop = 96
    walk(J, 1, stop, (0, 6.6, 0), (0, 1.4, 0))
    pose(J, stop + 6, root_loc=(0, 1.4, 0), hipL=(0, 0, 0), hipR=(0, 0, 0), kneeL=(0, 0, 0), kneeR=(0, 0, 0),
         shoulderL=(0, 0, 6), shoulderR=(0, 0, -6), elbowL=(-10, 0, 0), elbowR=(-15, 0, 0), head=(0, 0, 0), spine=(0, 0, 0))
    pose(J, 110, shoulderR=(-30, 0, -10), elbowR=(-110, 0, 0), handR=(0, 0, 0), head=(10, 0, -20))
    for i, f in enumerate(range(106, 122, 2)):
        key(phone, f, loc=(0.004 * (1 if i % 2 else -1), -0.035, -0.07))
    key(phone, 124, loc=(0.0, -0.035, -0.07))
    key_socket(scr_es, 102, 0.3); key_socket(scr_es, 108, 2.2)
    pose(J, 130, shoulderR=(-38, 0, -12), elbowR=(-118, 0, 0), head=(16, 0, -28), spine=(-6, 0, 0),
         shoulderL=(-10, 0, 25), elbowL=(-30, 0, 0))
    pose(J, n, shoulderR=(-38, 0, -12), elbowR=(-120, 0, 0), head=(18, 0, -30), spine=(-8, 0, 0),
         shoulderL=(-12, 0, 28), elbowL=(-32, 0, 0))
    lb = label3d(coll, "sameday", "SAME DAY?!", 0.2, (0.05, 1.2, 2.2), rot=(90, 0, -6), color=YELLOW, emit=2.4)
    pop(lb, 128)
    sun = light(coll, "sun", "SUN", (0, 0, 10), 4.0, (1, 0.62, 0.32))
    sun.rotation_euler = (R(76), R(0), R(-150))
    light(coll, "fill", "AREA", (1.5, -3, 2), 200, (0.5, 0.6, 1), 3, (0, 1.4, 1.2))
    cam, tgt = camera(sc, coll, (0.7, -2.0, 0.55), (0, 5.5, 1.7), lens=26)
    key(tgt, 1, loc=(0, 5.5, 1.8)); key(tgt, stop, loc=(0, 1.4, 1.5)); key(tgt, n, loc=(0.1, 1.4, 1.65))
    key(cam, 1, loc=(0.7, -2.0, 0.55)); key(cam, stop, loc=(0.35, -0.6, 0.95)); key(cam, n, loc=(-0.1, 0.0, 1.35))
    dof(cam, J["head"], 2.4)


def extra_textures():
    """Small textures only this script needs."""
    from PIL import Image, ImageDraw
    out = {}
    p = os.path.join(L.textures.OUT, "submit.png")
    if not os.path.exists(p):
        im = Image.new("RGB", (1200, 800), (24, 60, 140))
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 1200, 120], fill=(14, 36, 90))
        d.text((600, 60), "rupee symbol competition", font=L.textures.font(L.textures.INTER_SB, 54), fill=(220, 230, 255), anchor="mm")
        d.text((600, 330), "SUBMIT YOUR", font=L.textures.font(L.textures.INTER_XB, 130), fill=(255, 255, 255), anchor="mm")
        d.text((600, 480), "DESIGN", font=L.textures.font(L.textures.INTER_XB, 150), fill=(255, 200, 60), anchor="mm")
        d.rounded_rectangle([400, 590, 800, 700], radius=50, fill=(255, 140, 30))
        d.text((600, 645), "UPLOAD", font=L.textures.font(L.textures.INTER_B, 60), fill=(255, 255, 255), anchor="mm")
        im.save(p)
    out["submit"] = p
    p = os.path.join(L.textures.OUT, "phone_news.png")
    if not os.path.exists(p):
        im = Image.new("RGB", (600, 1300), (16, 18, 26))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([40, 300, 560, 820], radius=40, fill=(245, 245, 248))
        d.text((300, 380), "BREAKING", font=L.textures.font(L.textures.INTER_XB, 64), fill=(220, 40, 40), anchor="mm")
        d.text((300, 560), "₹", font=L.textures.font(L.textures.DEVA_B, 260), fill=(20, 20, 26), anchor="mm")
        d.text((300, 740), "Your design is selected!", font=L.textures.font(L.textures.INTER_B, 38), fill=(40, 40, 50), anchor="mm")
        im.save(p)
    out["phone_news"] = p
    return out


BUILDERS = {"A": build_A, "C": build_C, "E": build_E, "F": build_F, "G": build_G, "I": build_I}


def DUR(name):
    return L.DUR[name]


def build(quality, only=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    L._MATS.clear()
    L.TEX.update(L.textures.build_all())
    L.TEX.update(extra_textures())
    for name in L.DUR:
        if only and name not in only:
            continue
        sc, coll = L.new_scene(name, quality)
        BUILDERS[name](sc, coll)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true")
    ap.add_argument("--render")
    ap.add_argument("--quality", default="draft")
    ap.add_argument("--frames")
    a = ap.parse_args(sys.argv[1:])
    if a.save:
        build(a.quality)
        bpy.context.preferences.filepaths.save_version = 0
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "rupee_v2.blend"), relative_remap=True)
        print("saved", os.path.join(HERE, "rupee_v2.blend"))
    if a.render:
        build(a.quality, only=[a.render])
        sc = bpy.data.scenes[a.render]
        if a.frames:
            s, e = (int(x) for x in a.frames.split("-"))
            sc.frame_start, sc.frame_end = s, e
        bpy.ops.render.render(animation=True, scene=sc.name)


if __name__ == "__main__":
    main()
