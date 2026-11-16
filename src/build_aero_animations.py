#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_aero_animations.py
========================
Lee `aero_flight_animations.xml` y genera los archivos de animación Havok 64-bit
(`hk_2014.1.0-r1` `.hkx`) para Vuelo Estacionario (Hover), Vuelo de Avance
(Walk/Jog/Run/Sprint) y Descenso Controlado (AeroDescent), tanto para el
esqueleto Humano como para Servoarmadura (Power Armor).
"""

import os
import math
import shutil
import struct
import zlib
import xml.etree.ElementTree as ET

FO4_DATA_DIR = r"C:\Program Files (x86)\Steam\steamapps\common\Fallout 4\Data"
ANIM_BA2_PATH = os.path.join(FO4_DATA_DIR, "Fallout4 - Animations.ba2")
XML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aero_flight_animations.xml")
LOCAL_MESHES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "meshes")


def align(p: int, a: int) -> int:
    return (p + a - 1) & ~(a - 1)


def quat_mul(q1, q2):
    x1, y1, z1, w1 = q1
    x2, y2, z2, w2 = q2
    return (
        w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
        w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
        w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
        w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
    )


def quat_from_euler_deg(rx_deg: float, ry_deg: float, rz_deg: float):
    hx = math.radians(rx_deg) * 0.5
    hy = math.radians(ry_deg) * 0.5
    hz = math.radians(rz_deg) * 0.5
    cx, sx = math.cos(hx), math.sin(hx)
    cy, sy = math.cos(hy), math.sin(hy)
    cz, sz = math.cos(hz), math.sin(hz)
    return (
        sx * cy * cz - cx * sy * sz,
        cx * sy * cz + sx * cy * sz,
        cx * cy * sz - sx * sy * cz,
        cx * cy * cz + sx * sy * sz,
    )


def encode_40bit_quat(x: float, y: float, z: float, w: float) -> bytes:
    """Codifica un cuaternión (x, y, z, w) en el formato Havok 40-bit (5 bytes)."""
    n = math.sqrt(x * x + y * y + z * z + w * w)
    if n < 1e-8:
        q = [0.0, 0.0, 0.0, 1.0]
    else:
        q = [x / n, y / n, z / n, w / n]
    shift = max(range(4), key=lambda i: abs(q[i]))
    inv = 1 if q[shift] < 0.0 else 0
    rem = [q[i] for i in range(4) if i != shift]
    scale = 0.0003454348
    c = [max(0, min(4095, int(round(v / scale)) + 2048)) for v in rem]
    val = (
        (c[0] & 0xFFF)
        | ((c[1] & 0xFFF) << 12)
        | ((c[2] & 0xFFF) << 24)
        | ((shift & 0x3) << 36)
        | ((inv & 0x1) << 38)
    )
    return val.to_bytes(5, "little")


def decode_40bit_quat(b5: bytes):
    """Decodifica un cuaternión Havok 40-bit (5 bytes) a (x, y, z, w) normalizado."""
    v = int.from_bytes(b5, "little")
    c0 = (v & 0xFFF) - 2048
    c1 = ((v >> 12) & 0xFFF) - 2048
    c2 = ((v >> 24) & 0xFFF) - 2048
    missing = (v >> 36) & 0x3
    neg = (v >> 38) & 0x1
    scale = 0.0003454348
    f0, f1, f2 = c0 * scale, c1 * scale, c2 * scale
    sq = max(0.0, 1.0 - (f0 * f0 + f1 * f1 + f2 * f2))
    fm = -math.sqrt(sq) if neg else math.sqrt(sq)
    vals = [0.0, 0.0, 0.0, 0.0]
    idx = 0
    for i in range(4):
        if i == missing:
            vals[i] = fm
        else:
            vals[i] = (f0, f1, f2)[idx]
            idx += 1
    return tuple(vals)


def quat_inv(q):
    n2 = q[0] * q[0] + q[1] * q[1] + q[2] * q[2] + q[3] * q[3]
    if n2 < 1e-12:
        return (0.0, 0.0, 0.0, 1.0)
    return (-q[0] / n2, -q[1] / n2, -q[2] / n2, q[3] / n2)


def quat_axis_deg(ax: float, ay: float, az: float, deg: float):
    al = math.sqrt(ax * ax + ay * ay + az * az)
    if al < 1e-8 or abs(deg) < 1e-8:
        return (0.0, 0.0, 0.0, 1.0)
    r = math.radians(deg) * 0.5
    s, c = math.sin(r) / al, math.cos(r)
    return (ax * s, ay * s, az * s, c)


def extract_skeleton_rest_pos(raw_sk: bytes, num_tracks: int = 95) -> list:
    s2 = struct.unpack_from("<I", raw_sk, 0xD0 + 20)[0]
    for off in range(s2, len(raw_sk) - 48 * 10, 4):
        s0 = struct.unpack_from("<3f", raw_sk, off + 32)
        s1 = struct.unpack_from("<3f", raw_sk, off + 48 + 32)
        if all(abs(x - 1.0) < 1e-4 for x in s0 + s1):
            return [struct.unpack_from("<3f", raw_sk, off + i * 48) for i in range(num_tracks)]
    return [(0.0, 0.0, 0.0) for _ in range(num_tracks)]


def extract_frame0_pose(raw: bytes, rest_pos: list):
    """Extrae traslaciones y cuaterniones exactos del fotograma 0 de un HKX spline."""
    s2_off = struct.unpack_from("<I", raw, 0xD0 + 20)[0]
    l_off = s2_off + struct.unpack_from("<I", raw, 0xD0 + 24)[0]
    g_off = s2_off + struct.unpack_from("<I", raw, 0xD0 + 28)[0]
    fixups = {}
    pos = l_off
    while pos < g_off:
        src, dst = struct.unpack_from("<II", raw, pos)
        if src != 0xFFFFFFFF:
            fixups[src] = dst
        pos += 8

    spline_off = 0x130
    ntracks = struct.unpack_from("<I", raw, s2_off + spline_off + 24)[0]
    bo_off = s2_off + fixups[spline_off + 0x58]
    blk_rel = struct.unpack_from("<I", raw, bo_off)[0]
    data_off = s2_off + fixups[spline_off + 0x98] + blk_rel
    p = align(ntracks * 4, 4)

    trans_map = {}
    quat_map = {}
    for i in range(ntracks):
        q, t, r, s = raw[data_off + i * 4 : data_off + i * 4 + 4]
        base_t = list(rest_pos[i]) if i < len(rest_pos) else [0.0, 0.0, 0.0]

        if t & 0x70:
            p = align(p, 4)
            ni = struct.unpack_from("<H", raw, data_off + p)[0]
            dg = raw[data_off + p + 2]
            p = align(p + 3 + (ni + dg + 2), 4)
            sp_bounds = {}
            for bit in range(3):
                if t & (0x10 << bit):
                    sp_bounds[bit] = struct.unpack_from("<2f", raw, data_off + p)
                    p += 8
                elif t & (0x01 << bit):
                    base_t[bit] = struct.unpack_from("<f", raw, data_off + p)[0]
                    p += 4
            sp_chs = [bit for bit in range(3) if (t & (0x10 << bit))]
            for ch_idx, bit in enumerate(sp_chs):
                u0 = struct.unpack_from("<H", raw, data_off + p + ch_idx * 2)[0] / 65535.0
                mn, mx = sp_bounds[bit]
                base_t[bit] = mn + (mx - mn) * u0
            p += (ni + 1) * len(sp_chs) * 2
        elif t & 0x07:
            p = align(p, 4)
            for bit in range(3):
                if t & (0x01 << bit):
                    base_t[bit] = struct.unpack_from("<f", raw, data_off + p)[0]
                    p += 4
        trans_map[i] = tuple(base_t)

        rq = (q >> 2) & 0x03
        rb = {0: 4, 1: 5, 2: 6, 3: 6}[rq]
        ra = {0: 4, 1: 1, 2: 2, 3: 2}[rq]
        if r & 0xF0:
            p = align(p, 4)
            ni = struct.unpack_from("<H", raw, data_off + p)[0]
            dg = raw[data_off + p + 2]
            p = align(p + 3 + (ni + dg + 2), ra)
            quat_map[i] = (
                decode_40bit_quat(raw[data_off + p : data_off + p + 5])
                if rb == 5
                else (0.0, 0.0, 0.0, 1.0)
            )
            p += (ni + 1) * rb
        elif r & 0x0F:
            p = align(p, 4)
            quat_map[i] = (
                decode_40bit_quat(raw[data_off + p : data_off + p + 5])
                if rb == 5
                else (0.0, 0.0, 0.0, 1.0)
            )
            p += rb
        else:
            quat_map[i] = (0.0, 0.0, 0.0, 1.0)

        if s & 0x70:
            p = align(p, 4)
            ni = struct.unpack_from("<H", raw, data_off + p)[0]
            dg = raw[data_off + p + 2]
            p = align(p + 3 + (ni + dg + 2), 4)
            for bit in range(3):
                if s & (0x10 << bit):
                    p += 8
                elif s & (0x01 << bit):
                    p += 4
            p += (ni + 1) * sum(1 for bit in range(3) if (s & (0x10 << bit))) * 2
        elif s & 0x07:
            p = align(p, 4) + sum(4 for bit in range(3) if (s & (0x01 << bit)))
        p = align(p, 4)

    return trans_map, quat_map


class BA2AnimationReader:
    def __init__(self, ba2_path: str):
        self.ba2_path = ba2_path
        self.f = open(ba2_path, "rb")
        magic, ver, btype, num_files, name_table_offset = struct.unpack("<4sI4sIQ", self.f.read(24))
        assert magic == b"BTDX", f"Invalid BA2 magic: {magic}"
        self.entries = [struct.unpack("<4IQ3I", self.f.read(36)) for _ in range(num_files)]
        self.f.seek(name_table_offset)
        self.names = [self.f.read(struct.unpack("<H", self.f.read(2))[0]).decode("latin1") for _ in range(num_files)]
        self.name_to_idx = {n.lower().replace("/", "\\"): i for i, n in enumerate(self.names)}

    def extract(self, rel_path: str) -> bytearray:
        key = rel_path.lower().replace("/", "\\")
        if key not in self.name_to_idx:
            raise KeyError(f"Animation not found in BA2: {rel_path}")
        idx = self.name_to_idx[key]
        _, _, _, _, offset, packed_sz, unpacked_sz, _ = self.entries[idx]
        self.f.seek(offset)
        raw = zlib.decompress(self.f.read(packed_sz)) if packed_sz > 0 else self.f.read(unpacked_sz)
        return bytearray(raw)

    def exists(self, rel_path: str) -> bool:
        return rel_path.lower().replace("/", "\\") in self.name_to_idx

    def close(self):
        self.f.close()


def strip_footstep_annotations_in_place(raw: bytearray, s2_off: int, fixups: dict, spline_off: int = 0x130):
    """
    Neutraliza los eventos de sonido de pasos ('FootLeft', 'FootRight',
    'FootScuffLeft', 'FootScuffRight', 'FootSprintLeft', 'FootSprintRight', 'FootUp')
    sobrescribiéndolos in-place sin alterar 'SyncLeft'/'SyncRight' ni los eventos
    de transición del grafo ('JumpDown', 'Land').
    """
    if (spline_off + 0x28) not in fixups:
        return
    ann_arr_off = fixups[spline_off + 0x28]
    ann_cnt = struct.unpack_from("<I", raw, s2_off + spline_off + 0x30)[0]
    mute_prefixes = (
        b"FootLeft",
        b"FootRight",
        b"FootScuff",
        b"FootSprint",
        b"FootUp",
        b"CameraShake",
        b"PowerArmorHardLanding",
        b"ImpactLand",
    )
    for i in range(ann_cnt):
        elem_off = ann_arr_off + i * 24
        if s2_off + elem_off + 20 > len(raw):
            break
        num_ann = struct.unpack_from("<I", raw, s2_off + elem_off + 16)[0]
        if num_ann > 0 and (elem_off + 8) in fixups:
            ann_data_off = fixups[elem_off + 8]
            for j in range(num_ann):
                str_ptr_key = ann_data_off + j * 16 + 8
                if str_ptr_key in fixups:
                    p = s2_off + fixups[str_ptr_key]
                    end = raw.find(b"\x00", p)
                    s_bytes = bytes(raw[p:end])
                    if any(s_bytes.startswith(pref) for pref in mute_prefixes):
                        # Reemplazar por cadena silenciosa de igual longitud
                        replacement = b"AeroMute"[: len(s_bytes)].ljust(len(s_bytes), b"0")
                        raw[p:end] = replacement


def smooth_first_person_hkx(raw: bytearray) -> bytearray:
    """
    Estabiliza una animación de 1ª persona (sin armas y con armas, humano y Servoarmadura)
    eliminando:
      1. Todos los eventos de sonido de pisadas ('FootLeft', 'FootRight', 'FootSprint*', 'FootUp').
      2. Las sacudidas bruscas de cámara y brazos en el hueso COM (Track 1) y Camera (Track 78),
         aplanando la traslación al punto medio estacionario y fijando la rotación de la cámara
         para lograr un planeo en primera persona 100% fluido y sin trompicones.
    """
    s0_off = struct.unpack_from("<I", raw, 0x50 + 20)[0]
    s2_off = struct.unpack_from("<I", raw, 0xD0 + 20)[0]
    local_fixup_off = s2_off + struct.unpack_from("<I", raw, 0xD0 + 24)[0]
    global_fixup_off = s2_off + struct.unpack_from("<I", raw, 0xD0 + 28)[0]
    virtual_fixup_off = s2_off + struct.unpack_from("<I", raw, 0xD0 + 32)[0]
    exports_off = s2_off + struct.unpack_from("<I", raw, 0xD0 + 36)[0]

    fixups = {}
    pos = local_fixup_off
    while pos < global_fixup_off:
        src, dst = struct.unpack_from("<II", raw, pos)
        if src != 0xFFFFFFFF:
            fixups[src] = dst
        pos += 8

    classes = {}
    pos = virtual_fixup_off
    while pos + 12 <= exports_off:
        src, _, dst = struct.unpack_from("<3I", raw, pos)
        if src != 0xFFFFFFFF:
            end = raw.find(b"\x00", s0_off + dst)
            classes[raw[s0_off + dst : end].decode("latin1")] = src
        pos += 12

    spline_off = classes.get("hkaSplineCompressedAnimation")
    if spline_off is None:
        return raw

    # No eliminamos las anotaciones de pasos en 1a persona para preservar el sonido
    # nativo al caminar/correr en tierra; en vuelo se silencia AudioCategoryFSTplayer.

    ntracks = struct.unpack_from("<I", raw, s2_off + spline_off + 24)[0]
    nblocks = struct.unpack_from("<I", raw, s2_off + spline_off + 0x3C)[0]
    bo_off = s2_off + fixups[spline_off + 0x58]
    block_offsets = [struct.unpack_from("<I", raw, bo_off + b * 4)[0] for b in range(nblocks)]
    base_data_off = s2_off + fixups[spline_off + 0x98]
    data_sz = struct.unpack_from("<I", raw, s2_off + spline_off + 0xA0)[0]

    for b_idx, blk_rel_off in enumerate(block_offsets):
        data_off = base_data_off + blk_rel_off
        p = align(ntracks * 4, 4)
        for i in range(ntracks):
            q, t, r, s = raw[data_off + i * 4 : data_off + i * 4 + 4]

            # 1. TRANSLATION
            if t & 0x70:
                p = align(p, 4)
                nitems = struct.unpack_from("<H", raw, data_off + p)[0]
                deg = raw[data_off + p + 2]
                p += 3 + (nitems + deg + 2)
                p = align(p, 4)

                # Calcular primero el offset de los puntos cuantizados <H para extraer el valor exacto
                # del fotograma 0 (val0), idéntico a WPNIdleReady, evitando cualquier salto al iniciar/parar.
                sp_bounds_offs = {}
                st_offs = {}
                scan_p = p
                for bit in range(3):
                    if t & (0x10 << bit):
                        sp_bounds_offs[bit] = scan_p
                        scan_p += 8
                    elif t & (0x01 << bit):
                        st_offs[bit] = scan_p
                        scan_p += 4
                sp_channels = [bit for bit in range(3) if (t & (0x10 << bit))]
                n_sp_ch = len(sp_channels)
                quant_base = scan_p

                for ch_idx, bit in enumerate(sp_channels):
                    boff = sp_bounds_offs[bit]
                    mn, mx = struct.unpack_from("<2f", raw, data_off + boff)
                    u0 = struct.unpack_from("<H", raw, data_off + quant_base + ch_idx * 2)[0] / 65535.0
                    val0 = mn + (mx - mn) * u0
                    if i == 78:
                        if bit in (0, 1):
                            struct.pack_into("<2f", raw, data_off + boff, 0.0, 0.0)
                        else:
                            struct.pack_into("<2f", raw, data_off + boff, val0, val0)
                    elif i == 79:
                        struct.pack_into("<2f", raw, data_off + boff, 0.0, 0.0)
                    elif i >= 1:
                        # Estabilizar por completo COM (Track 1) y huesos del arma/brazos (2..77) en su
                        # posición neutra exacta de Frame 0, eliminando el balanceo de pasos en 1ª persona.
                        struct.pack_into("<2f", raw, data_off + boff, val0, val0)

                if i == 79:
                    for bit, soff in st_offs.items():
                        struct.pack_into("<f", raw, data_off + soff, 0.0)

                if i >= 1 and n_sp_ch > 0:
                    for k in range((nitems + 1) * n_sp_ch):
                        struct.pack_into("<H", raw, data_off + quant_base + k * 2, 32768)

                p = quant_base + (nitems + 1) * n_sp_ch * 2
            elif t & 0x07:
                p = align(p, 4)
                for bit in range(3):
                    if t & (0x01 << bit):
                        if i == 79:
                            struct.pack_into("<f", raw, data_off + p, 0.0)
                        p += 4

            # 2. ROTATION
            r_qtype = (q >> 2) & 0x03
            r_bsize = {0: 4, 1: 5, 2: 6, 3: 6}[r_qtype]
            r_align = {0: 4, 1: 1, 2: 2, 3: 2}[r_qtype]
            if r & 0xF0:
                p = align(p, 4)
                nitems = struct.unpack_from("<H", raw, data_off + p)[0]
                deg = raw[data_off + p + 2]
                p += 3 + (nitems + deg + 2)
                p = align(p, r_align)
                if i >= 1:
                    # Fijar tanto Camera (78) como COM (1) y brazos/manos/arma (2..77) al cuaternión
                    # neutro de 48 bits (6 bytes) del fotograma 0, suprimiendo el cabeceo de zancada.
                    first_q = bytes(raw[data_off + p : data_off + p + r_bsize])
                    for k in range(nitems + 1):
                        raw[data_off + p + k * r_bsize : data_off + p + (k + 1) * r_bsize] = first_q
                p += (nitems + 1) * r_bsize
            elif r & 0x0F:
                p = align(p, 4)
                p += r_bsize

            # 3. SCALE
            if s & 0x70:
                p = align(p, 4)
                nitems = struct.unpack_from("<H", raw, data_off + p)[0]
                deg = raw[data_off + p + 2]
                p += 3 + (nitems + deg + 2)
                p = align(p, 4)
                for bit in range(3):
                    if s & (0x10 << bit):
                        p += 8
                    elif s & (0x01 << bit):
                        p += 4
                n_sp_ch = sum(1 for bit in range(3) if (s & (0x10 << bit)))
                p += (nitems + 1) * n_sp_ch * 2
            elif s & 0x07:
                p = align(p, 4)
                n_st_ch = sum(1 for bit in range(3) if (s & (0x01 << bit)))
                p += n_st_ch * 4

            p = align(p, 4)

        next_blk_off = block_offsets[b_idx + 1] if (b_idx + 1) < nblocks else data_sz
        assert (
            align(blk_rel_off + p, 16) == next_blk_off
        ), f"1stPerson Spline block {b_idx} size mismatch: {align(blk_rel_off + p, 16)} != {next_blk_off}"
    return raw


def apply_xml_profile_to_hkx(
    raw: bytearray,
    bone_overrides: dict,
    target_com_z: float,
    bob_amp_z: float,
    strip_footsteps: bool,
    fallback_rot_map: dict = None,
) -> bytearray:
    """
    Aplica las poses óseas definidas en el XML directamente sobre el buffer
    comprimido de `hkaSplineCompressedAnimation` manteniendo intactos todos los
    offsets, duración, root motion (`hkaDefaultAnimatedReferenceFrame`) y fixups.
    """
    s2_off = struct.unpack_from("<I", raw, 0xD0 + 20)[0]
    local_fixup_off = s2_off + struct.unpack_from("<I", raw, 0xD0 + 24)[0]
    global_fixup_off = s2_off + struct.unpack_from("<I", raw, 0xD0 + 28)[0]
    virtual_fixup_off = s2_off + struct.unpack_from("<I", raw, 0xD0 + 32)[0]

    fixups = {}
    pos = local_fixup_off
    while pos < global_fixup_off:
        src, dst = struct.unpack_from("<II", raw, pos)
        if src != 0xFFFFFFFF:
            fixups[src] = dst
        pos += 8

    vfixups = {}
    pos = global_fixup_off
    while pos < virtual_fixup_off:
        src, _, dst = struct.unpack_from("<3I", raw, pos)
        if src != 0xFFFFFFFF:
            vfixups[src] = dst
        pos += 12

    if strip_footsteps:
        strip_footstep_annotations_in_place(raw, s2_off, fixups)

    # Linealizar la velocidad de avance en hkaDefaultAnimatedReferenceFrame (root motion)
    # para eliminar cualquier variación de velocidad entre zancadas en vuelo hacia adelante
    rf_off = vfixups.get(0x150)
    if rf_off and (rf_off + 0x48) in fixups and bob_amp_z <= 0.05:
        samp_off = fixups[rf_off + 0x48]
        nsamp = struct.unpack_from("<I", raw, s2_off + rf_off + 0x50)[0]
        if nsamp >= 2:
            x0, y0, z0, w0 = struct.unpack_from("<4f", raw, s2_off + samp_off)
            x1, y1, z1, w1 = struct.unpack_from("<4f", raw, s2_off + samp_off + (nsamp - 1) * 16)
            if abs(y1 - y0) > 5.0 and abs(x1 - x0) < 1.0 and abs(w1 - w0) < 0.05:
                for s_idx in range(nsamp):
                    u = s_idx / float(nsamp - 1)
                    yi = y0 + (y1 - y0) * u
                    struct.pack_into("<4f", raw, s2_off + samp_off + s_idx * 16, 0.0, yi, 0.0, w0)

    spline_off = 0x130
    ntracks = struct.unpack_from("<I", raw, s2_off + spline_off + 24)[0]
    nblocks = struct.unpack_from("<I", raw, s2_off + spline_off + 0x3C)[0]
    bo_off = s2_off + fixups[spline_off + 0x58]
    block_offsets = [struct.unpack_from("<I", raw, bo_off + b * 4)[0] for b in range(nblocks)]
    base_data_off = s2_off + fixups[spline_off + 0x98]
    data_sz = struct.unpack_from("<I", raw, s2_off + spline_off + 0xA0)[0]
    cam_fwd_enc = encode_40bit_quat(0.7071068, 0.0, 0.0, 0.7071068)

    for b_idx, blk_rel_off in enumerate(block_offsets):
        data_off = base_data_off + blk_rel_off
        p = align(ntracks * 4, 4)
        for i in range(ntracks):
            q, t, r, s = raw[data_off + i * 4 : data_off + i * 4 + 4]

            # ------------------------------------------------------------------
            # 1. TRANSLATION
            # ------------------------------------------------------------------
            if t & 0x70:
                p = align(p, 4)
                nitems = struct.unpack_from("<H", raw, data_off + p)[0]
                deg = raw[data_off + p + 2]
                p += 3 + (nitems + deg + 2)
                p = align(p, 4)
                for bit in range(3):
                    if t & (0x10 << bit):
                        if i == 1 and target_com_z > 0:
                            if bit in (0, 1):
                                # Anular por completo los tirones laterales (X) y de frenado/impulso de zancada (Y) del COM
                                struct.pack_into("<2f", raw, data_off + p, 0.0, 0.0)
                            elif bit == 2:
                                mn = target_com_z - bob_amp_z
                                mx = target_com_z + bob_amp_z
                                struct.pack_into("<2f", raw, data_off + p, mn, mx)
                        elif i == 78 and target_com_z > 0:
                            mn, mx = struct.unpack_from("<2f", raw, data_off + p)
                            mid = 0.0 if bit == 0 else 0.5 * (mn + mx)
                            struct.pack_into("<2f", raw, data_off + p, mid, mid)
                        elif i == 79 and target_com_z > 0:
                            # Desactivar Camera Control (peso 0.0) en 3a persona para evitar que UpwardDrift/Jump
                            # secuestren la camara orbital y la claven dentro del casco mirando al vacio.
                            struct.pack_into("<2f", raw, data_off + p, 0.0, 0.0)
                        p += 8
                    elif t & (0x01 << bit):
                        if i == 1 and target_com_z > 0:
                            if bit in (0, 1):
                                struct.pack_into("<f", raw, data_off + p, 0.0)
                            elif bit == 2:
                                struct.pack_into("<f", raw, data_off + p, target_com_z)
                        elif i == 79 and target_com_z > 0:
                            struct.pack_into("<f", raw, data_off + p, 0.0)
                        p += 4
                sp_channels = [bit for bit in range(3) if (t & (0x10 << bit))]
                n_sp_ch = len(sp_channels)
                if i == 1 and 2 in sp_channels and target_com_z > 0:
                    z_ch_idx = sp_channels.index(2)
                    for k in range(nitems + 1):
                        if bob_amp_z <= 0.01:
                            qval = 32768
                        else:
                            phase = (2.0 * math.pi * k) / max(1, nitems)
                            u = 0.5 + 0.5 * math.sin(phase)
                            qval = max(0, min(65535, int(round(u * 65535.0))))
                        ch_off = data_off + p + (k * n_sp_ch + z_ch_idx) * 2
                        struct.pack_into("<H", raw, ch_off, qval)
                elif i == 79 and n_sp_ch > 0 and target_com_z > 0:
                    for k in range((nitems + 1) * n_sp_ch):
                        struct.pack_into("<H", raw, data_off + p + k * 2, 32768)
                p += (nitems + 1) * n_sp_ch * 2
            elif t & 0x07:
                p = align(p, 4)
                for bit in range(3):
                    if t & (0x01 << bit):
                        if i == 1 and target_com_z > 0:
                            if bit in (0, 1):
                                struct.pack_into("<f", raw, data_off + p, 0.0)
                            elif bit == 2:
                                struct.pack_into("<f", raw, data_off + p, target_com_z)
                        elif i == 79 and target_com_z > 0:
                            struct.pack_into("<f", raw, data_off + p, 0.0)
                        p += 4

            # ------------------------------------------------------------------
            # 2. ROTATION
            # ------------------------------------------------------------------
            r_qtype = (q >> 2) & 0x03
            r_bsize = {0: 4, 1: 5, 2: 6, 3: 6}[r_qtype]
            r_align = {0: 4, 1: 1, 2: 2, 3: 2}[r_qtype]
            b_ovr = bone_overrides.get(i)
            if r & 0xF0:
                p = align(p, 4)
                nitems = struct.unpack_from("<H", raw, data_off + p)[0]
                deg = raw[data_off + p + 2]
                p += 3 + (nitems + deg + 2)
                p = align(p, r_align)
                if b_ovr is not None and r_bsize == 5:
                    base_q = b_ovr["quat"]
                    osc_rx = b_ovr.get("osc_rx_deg", 0.0)
                    osc_ry = b_ovr.get("osc_ry_deg", 0.0)
                    osc_rz = b_ovr.get("osc_rz_deg", 0.0)
                    phase_rad = math.radians(b_ovr.get("phase_deg", 0.0))
                    for k in range(nitems + 1):
                        phase = (2.0 * math.pi * k) / max(1, nitems) + phase_rad
                        s_val = math.sin(phase)
                        dq = quat_from_euler_deg(osc_rx * s_val, osc_ry * s_val, osc_rz * s_val)
                        kq = quat_mul(base_q, dq)
                        enc = encode_40bit_quat(*kq)
                        raw[data_off + p + k * 5 : data_off + p + (k + 1) * 5] = enc
                elif fallback_rot_map and (2 <= i <= 77) and i in fallback_rot_map and r_bsize == 5:
                    enc_fb = fallback_rot_map[i]
                    for k in range(nitems + 1):
                        raw[data_off + p + k * 5 : data_off + p + (k + 1) * 5] = enc_fb
                elif i == 78 and target_com_z > 0:
                    first_q = cam_fwd_enc if r_bsize == 5 else bytes(raw[data_off + p : data_off + p + r_bsize])
                    for k in range(nitems + 1):
                        raw[data_off + p + k * r_bsize : data_off + p + (k + 1) * r_bsize] = first_q
                p += (nitems + 1) * r_bsize
            elif r & 0x0F:
                p = align(p, 4)
                if b_ovr is not None and r_bsize == 5:
                    enc = encode_40bit_quat(*b_ovr["quat"])
                    raw[data_off + p : data_off + p + 5] = enc
                elif fallback_rot_map and (2 <= i <= 77) and i in fallback_rot_map and r_bsize == 5:
                    raw[data_off + p : data_off + p + 5] = fallback_rot_map[i]
                elif i == 78 and target_com_z > 0 and r_bsize == 5:
                    raw[data_off + p : data_off + p + 5] = cam_fwd_enc
                p += r_bsize

            # ------------------------------------------------------------------
            # 3. SCALE
            # ------------------------------------------------------------------
            if s & 0x70:
                p = align(p, 4)
                nitems = struct.unpack_from("<H", raw, data_off + p)[0]
                deg = raw[data_off + p + 2]
                p += 3 + (nitems + deg + 2)
                p = align(p, 4)
                for bit in range(3):
                    if s & (0x10 << bit):
                        p += 8
                    elif s & (0x01 << bit):
                        p += 4
                n_sp_ch = ((s >> 4) & 1) + ((s >> 5) & 1) + ((s >> 6) & 1)
                p += (nitems + 1) * n_sp_ch * 2
            elif s & 0x07:
                p = align(p, 4)
                n_st_ch = (s & 1) + ((s >> 1) & 1) + ((s >> 2) & 1)
                p += n_st_ch * 4

            p = align(p, 4)

        next_blk_off = block_offsets[b_idx + 1] if (b_idx + 1) < nblocks else data_sz
        assert (
            align(blk_rel_off + p, 16) == next_blk_off
        ), f"Spline block {b_idx} size mismatch: {align(blk_rel_off + p, 16)} != {next_blk_off}"
    return raw


def extract_first_frame_rotations(raw: bytearray) -> dict:
    """Extrae el primer cuaternión codificado (5 bytes) de cada pista de una animación .hkx."""
    s2_off = struct.unpack_from("<I", raw, 0xD0 + 20)[0]
    local_fixup_off = s2_off + struct.unpack_from("<I", raw, 0xD0 + 24)[0]
    global_fixup_off = s2_off + struct.unpack_from("<I", raw, 0xD0 + 28)[0]
    fixups = {}
    pos = local_fixup_off
    while pos < global_fixup_off:
        src, dst = struct.unpack_from("<II", raw, pos)
        if src != 0xFFFFFFFF:
            fixups[src] = dst
        pos += 8

    spline_off = 0x130
    ntracks = struct.unpack_from("<I", raw, s2_off + spline_off + 24)[0]
    bo_off = s2_off + fixups[spline_off + 0x58]
    blk_rel_off = struct.unpack_from("<I", raw, bo_off)[0]
    base_data_off = s2_off + fixups[spline_off + 0x98]
    data_off = base_data_off + blk_rel_off

    rot_map = {}
    p = align(ntracks * 4, 4)
    for i in range(ntracks):
        q, t, r, s = raw[data_off + i * 4 : data_off + i * 4 + 4]
        if t & 0x70:
            p = align(p, 4)
            nitems = struct.unpack_from("<H", raw, data_off + p)[0]
            deg = raw[data_off + p + 2]
            p += 3 + (nitems + deg + 2)
            p = align(p, 4)
            for bit in range(3):
                if t & (0x10 << bit):
                    p += 8
                elif t & (0x01 << bit):
                    p += 4
            n_sp_ch = sum(1 for bit in range(3) if (t & (0x10 << bit)))
            p += (nitems + 1) * n_sp_ch * 2
        elif t & 0x07:
            p = align(p, 4)
            for bit in range(3):
                if t & (0x01 << bit):
                    p += 4

        r_qtype = (q >> 2) & 0x03
        r_bsize = {0: 4, 1: 5, 2: 6, 3: 6}[r_qtype]
        r_align = {0: 4, 1: 1, 2: 2, 3: 2}[r_qtype]
        if r & 0xF0:
            p = align(p, 4)
            nitems = struct.unpack_from("<H", raw, data_off + p)[0]
            deg = raw[data_off + p + 2]
            p += 3 + (nitems + deg + 2)
            p = align(p, r_align)
            if r_bsize == 5 and (2 <= i <= 77):
                rot_map[i] = bytes(raw[data_off + p : data_off + p + 5])
            p += (nitems + 1) * r_bsize
        elif r & 0x0F:
            p = align(p, 4)
            if r_bsize == 5 and (2 <= i <= 77):
                rot_map[i] = bytes(raw[data_off + p : data_off + p + 5])
            p += r_bsize

        if s & 0x70:
            p = align(p, 4)
            nitems = struct.unpack_from("<H", raw, data_off + p)[0]
            deg = raw[data_off + p + 2]
            p += 3 + (nitems + deg + 2)
            p = align(p, 4)
            for bit in range(3):
                if s & (0x10 << bit):
                    p += 8
                elif s & (0x01 << bit):
                    p += 4
            n_sp_ch = sum(1 for bit in range(3) if (s & (0x10 << bit)))
            p += (nitems + 1) * n_sp_ch * 2
        elif s & 0x07:
            p = align(p, 4)
            n_st_ch = sum(1 for bit in range(3) if (s & (0x01 << bit)))
            p += n_st_ch * 4
        p = align(p, 4)
    return rot_map


def build_fast_transition_hkx(
    raw: bytearray,
    bone_overrides: dict,
    fallback_rot_map: dict,
    target_com_z: float,
) -> bytearray:
    """
    Aplica una postura fija (de vuelo, descenso o erguida normal) sobre una plantilla
    vanilla nativa de 2 fotogramas (0.033s) SIN modificar su duración, número de fotogramas
    ni sus nudos B-spline (evitando matrices NaN / desaparición del cuerpo).
    """
    s2_off = struct.unpack_from("<I", raw, 0xD0 + 20)[0]
    local_fixup_off = s2_off + struct.unpack_from("<I", raw, 0xD0 + 24)[0]
    global_fixup_off = s2_off + struct.unpack_from("<I", raw, 0xD0 + 28)[0]
    virtual_fixup_off = s2_off + struct.unpack_from("<I", raw, 0xD0 + 32)[0]

    fixups = {}
    pos = local_fixup_off
    while pos < global_fixup_off:
        src, dst = struct.unpack_from("<II", raw, pos)
        if src != 0xFFFFFFFF:
            fixups[src] = dst
        pos += 8

    vfixups = {}
    pos = global_fixup_off
    while pos < virtual_fixup_off:
        src, _, dst = struct.unpack_from("<3I", raw, pos)
        if src != 0xFFFFFFFF:
            vfixups[src] = dst
        pos += 12

    strip_footstep_annotations_in_place(raw, s2_off, fixups)

    rf_off = vfixups.get(0x150)
    if rf_off:
        num_rf_frames = struct.unpack_from("<I", raw, s2_off + rf_off + 0x50)[0]
        if (rf_off + 0x48) in fixups:
            samp_off = fixups[rf_off + 0x48]
            for s_idx in range(num_rf_frames):
                struct.pack_into("<4f", raw, s2_off + samp_off + s_idx * 16, 0.0, 0.0, 0.0, 0.0)

    spline_off = 0x130
    ntracks = struct.unpack_from("<I", raw, s2_off + spline_off + 24)[0]
    nblocks = struct.unpack_from("<I", raw, s2_off + spline_off + 0x3C)[0]
    bo_off = s2_off + fixups[spline_off + 0x58]
    block_offsets = [struct.unpack_from("<I", raw, bo_off + b * 4)[0] for b in range(nblocks)]
    base_data_off = s2_off + fixups[spline_off + 0x98]
    data_sz = struct.unpack_from("<I", raw, s2_off + spline_off + 0xA0)[0]
    cam_fwd_enc = encode_40bit_quat(0.7071068, 0.0, 0.0, 0.7071068)

    for b_idx, blk_rel_off in enumerate(block_offsets):
        data_off = base_data_off + blk_rel_off
        p = align(ntracks * 4, 4)
        for i in range(ntracks):
            q, t, r, s = raw[data_off + i * 4 : data_off + i * 4 + 4]

            # 1. TRANSLATION
            if t & 0x70:
                p = align(p, 4)
                nitems = struct.unpack_from("<H", raw, data_off + p)[0]
                deg = raw[data_off + p + 2]
                knot_len = nitems + deg + 2
                p += 3 + knot_len
                p = align(p, 4)
                for bit in range(3):
                    if t & (0x10 << bit):
                        if i == 0:
                            struct.pack_into("<2f", raw, data_off + p, 0.0, 0.0)
                        elif i == 1:
                            val = target_com_z if bit == 2 else 0.0
                            struct.pack_into("<2f", raw, data_off + p, val, val)
                        elif i == 78:
                            mn, mx = struct.unpack_from("<2f", raw, data_off + p)
                            mid = 0.0 if bit == 0 else 0.5 * (mn + mx)
                            struct.pack_into("<2f", raw, data_off + p, mid, mid)
                        elif i == 79:
                            struct.pack_into("<2f", raw, data_off + p, 0.0, 0.0)
                        p += 8
                    elif t & (0x01 << bit):
                        if i == 0:
                            struct.pack_into("<f", raw, data_off + p, 0.0)
                        elif i == 1:
                            val = target_com_z if bit == 2 else 0.0
                            struct.pack_into("<f", raw, data_off + p, val)
                        elif i == 79:
                            struct.pack_into("<f", raw, data_off + p, 0.0)
                        p += 4
                n_sp_ch = sum(1 for bit in range(3) if (t & (0x10 << bit)))
                if i in (0, 1, 79):
                    for k in range((nitems + 1) * n_sp_ch):
                        struct.pack_into("<H", raw, data_off + p + k * 2, 32768)
                p += (nitems + 1) * n_sp_ch * 2
            elif t & 0x07:
                p = align(p, 4)
                for bit in range(3):
                    if t & (0x01 << bit):
                        if i in (0, 79):
                            struct.pack_into("<f", raw, data_off + p, 0.0)
                        elif i == 1:
                            val = target_com_z if bit == 2 else 0.0
                            struct.pack_into("<f", raw, data_off + p, val)
                        p += 4

            # 2. ROTATION
            r_qtype = (q >> 2) & 0x03
            r_bsize = {0: 4, 1: 5, 2: 6, 3: 6}[r_qtype]
            r_align = {0: 4, 1: 1, 2: 2, 3: 2}[r_qtype]
            b_ovr = bone_overrides.get(i)
            enc_target = None
            if r_bsize == 5:
                if b_ovr is not None:
                    enc_target = encode_40bit_quat(*b_ovr["quat"])
                elif (2 <= i <= 77) and i in fallback_rot_map:
                    enc_target = fallback_rot_map[i]
                elif i == 78:
                    enc_target = cam_fwd_enc

            if r & 0xF0:
                p = align(p, 4)
                nitems = struct.unpack_from("<H", raw, data_off + p)[0]
                deg = raw[data_off + p + 2]
                knot_len = nitems + deg + 2
                p += 3 + knot_len
                p = align(p, r_align)
                if enc_target is not None:
                    for k in range(nitems + 1):
                        raw[data_off + p + k * 5 : data_off + p + (k + 1) * 5] = enc_target
                p += (nitems + 1) * r_bsize
            elif r & 0x0F:
                p = align(p, 4)
                if enc_target is not None:
                    raw[data_off + p : data_off + p + 5] = enc_target
                p += r_bsize

            # 3. SCALE
            if s & 0x70:
                p = align(p, 4)
                nitems = struct.unpack_from("<H", raw, data_off + p)[0]
                deg = raw[data_off + p + 2]
                knot_len = nitems + deg + 2
                p += 3 + knot_len
                p = align(p, 4)
                for bit in range(3):
                    if s & (0x10 << bit):
                        p += 8
                    elif s & (0x01 << bit):
                        p += 4
                n_sp_ch = sum(1 for bit in range(3) if (s & (0x10 << bit)))
                p += (nitems + 1) * n_sp_ch * 2
            elif s & 0x07:
                p = align(p, 4)
                n_st_ch = sum(1 for bit in range(3) if (s & (0x01 << bit)))
                p += n_st_ch * 4

            p = align(p, 4)

        next_blk_off = block_offsets[b_idx + 1] if (b_idx + 1) < nblocks else data_sz
        assert (
            align(blk_rel_off + p, 16) == next_blk_off
        ), f"Transition Spline block {b_idx} size mismatch: {align(blk_rel_off + p, 16)} != {next_blk_off}"
    return raw


def build_aerial_weapon_hkx(
    raw: bytearray,
    pose_trans: dict,
    pose_quats: dict,
    leg_osc_map: dict = None,
    target_com_z: float = 80.5,
    bob_amp_z: float = 0.0,
) -> bytearray:
    """
    Convierte una animación de rifle de 3ª persona (95 pistas) en una postura limpia
    de tirador aeropropulsado en vuelo:
      - Fija el tren superior, brazos, manos, hueso Weapon e IK (pistas 9..77 y 80..94)
        a la pose limpia de referencia (Ready / Relaxed / Sighted / Sprint), eliminando
        al 100% el rebote de carrera, el braceo de zancada y cualquier efecto de tropiezo.
      - Orienta aerodinámicamente el COM (pista 1) y las piernas en estela (pistas 3..8)
        según la dirección y velocidad de vuelo (avance, retroceso con aerofreno, alabeo
        lateral o sprint supersónico), elevando los pies muy por encima de la losa para
        evitar que FootIK doble las rodillas.
      - Linealiza el root motion y estabiliza Camera (78) / Camera Control (79).
    """
    s2_off = struct.unpack_from("<I", raw, 0xD0 + 20)[0]
    local_fixup_off = s2_off + struct.unpack_from("<I", raw, 0xD0 + 24)[0]
    global_fixup_off = s2_off + struct.unpack_from("<I", raw, 0xD0 + 28)[0]
    virtual_fixup_off = s2_off + struct.unpack_from("<I", raw, 0xD0 + 32)[0]

    fixups = {}
    pos = local_fixup_off
    while pos < global_fixup_off:
        src, dst = struct.unpack_from("<II", raw, pos)
        if src != 0xFFFFFFFF:
            fixups[src] = dst
        pos += 8

    vfixups = {}
    pos = global_fixup_off
    while pos < virtual_fixup_off:
        src, _, dst = struct.unpack_from("<3I", raw, pos)
        if src != 0xFFFFFFFF:
            vfixups[src] = dst
        pos += 12

    strip_footstep_annotations_in_place(raw, s2_off, fixups)

    rf_off = vfixups.get(0x150)
    if rf_off and (rf_off + 0x48) in fixups and bob_amp_z <= 0.05:
        samp_off = fixups[rf_off + 0x48]
        nsamp = struct.unpack_from("<I", raw, s2_off + rf_off + 0x50)[0]
        if nsamp >= 2:
            x0, y0, z0, w0 = struct.unpack_from("<4f", raw, s2_off + samp_off)
            x1, y1, z1, w1 = struct.unpack_from("<4f", raw, s2_off + samp_off + (nsamp - 1) * 16)
            if (abs(x1 - x0) > 2.0 or abs(y1 - y0) > 2.0) and abs(w1 - w0) < 0.05:
                for s_idx in range(nsamp):
                    u = s_idx / float(nsamp - 1)
                    xi = x0 + (x1 - x0) * u
                    yi = y0 + (y1 - y0) * u
                    struct.pack_into("<4f", raw, s2_off + samp_off + s_idx * 16, xi, yi, 0.0, w0)

    spline_off = 0x130
    ntracks = struct.unpack_from("<I", raw, s2_off + spline_off + 24)[0]
    nblocks = struct.unpack_from("<I", raw, s2_off + spline_off + 0x3C)[0]
    bo_off = s2_off + fixups[spline_off + 0x58]
    block_offsets = [struct.unpack_from("<I", raw, bo_off + b * 4)[0] for b in range(nblocks)]
    base_data_off = s2_off + fixups[spline_off + 0x98]
    data_sz = struct.unpack_from("<I", raw, s2_off + spline_off + 0xA0)[0]

    enc_pose_quats = {idx: encode_40bit_quat(*qt) for idx, qt in pose_quats.items()}

    for b_idx, blk_rel_off in enumerate(block_offsets):
        data_off = base_data_off + blk_rel_off
        p = align(ntracks * 4, 4)
        for i in range(ntracks):
            q, t, r, s = raw[data_off + i * 4 : data_off + i * 4 + 4]

            # 1. TRANSLATION
            if t & 0x70:
                p = align(p, 4)
                nitems = struct.unpack_from("<H", raw, data_off + p)[0]
                deg = raw[data_off + p + 2]
                p += 3 + (nitems + deg + 2)
                p = align(p, 4)
                for bit in range(3):
                    if t & (0x10 << bit):
                        if i == 1 and target_com_z > 0:
                            if bit in (0, 1):
                                struct.pack_into("<2f", raw, data_off + p, 0.0, 0.0)
                            elif bit == 2:
                                struct.pack_into(
                                    "<2f",
                                    raw,
                                    data_off + p,
                                    target_com_z - bob_amp_z,
                                    target_com_z + bob_amp_z,
                                )
                        elif i == 78:
                            mn, mx = struct.unpack_from("<2f", raw, data_off + p)
                            mid = 0.0 if bit == 0 else 0.5 * (mn + mx)
                            struct.pack_into("<2f", raw, data_off + p, mid, mid)
                        elif i == 79:
                            struct.pack_into("<2f", raw, data_off + p, 0.0, 0.0)
                        elif i > 1 and i != 109 and i in pose_trans:
                            tv = pose_trans[i][bit]
                            struct.pack_into("<2f", raw, data_off + p, tv, tv)
                        p += 8
                    elif t & (0x01 << bit):
                        if i == 1 and target_com_z > 0:
                            val = target_com_z if bit == 2 else 0.0
                            struct.pack_into("<f", raw, data_off + p, val)
                        elif i == 79:
                            struct.pack_into("<f", raw, data_off + p, 0.0)
                        elif i > 1 and i not in (78, 109) and i in pose_trans:
                            struct.pack_into("<f", raw, data_off + p, pose_trans[i][bit])
                        p += 4
                sp_channels = [bit for bit in range(3) if (t & (0x10 << bit))]
                n_sp_ch = len(sp_channels)
                if i == 1 and 2 in sp_channels and target_com_z > 0:
                    z_ch_idx = sp_channels.index(2)
                    for k in range(nitems + 1):
                        if bob_amp_z <= 0.01:
                            qval = 32768
                        else:
                            phase = (2.0 * math.pi * k) / max(1, nitems)
                            u = 0.5 + 0.5 * math.sin(phase)
                            qval = max(0, min(65535, int(round(u * 65535.0))))
                        ch_off = data_off + p + (k * n_sp_ch + z_ch_idx) * 2
                        struct.pack_into("<H", raw, ch_off, qval)
                elif i not in (78, 109) and n_sp_ch > 0:
                    for k in range((nitems + 1) * n_sp_ch):
                        struct.pack_into("<H", raw, data_off + p + k * 2, 32768)
                p += (nitems + 1) * n_sp_ch * 2
            elif t & 0x07:
                p = align(p, 4)
                for bit in range(3):
                    if t & (0x01 << bit):
                        if i == 1 and target_com_z > 0:
                            val = target_com_z if bit == 2 else 0.0
                            struct.pack_into("<f", raw, data_off + p, val)
                        elif i == 79:
                            struct.pack_into("<f", raw, data_off + p, 0.0)
                        elif i > 1 and i not in (78, 109) and i in pose_trans:
                            struct.pack_into("<f", raw, data_off + p, pose_trans[i][bit])
                        p += 4

            # 2. ROTATION
            r_qtype = (q >> 2) & 0x03
            r_bsize = {0: 4, 1: 5, 2: 6, 3: 6}[r_qtype]
            r_align = {0: 4, 1: 1, 2: 2, 3: 2}[r_qtype]
            osc_cfg = leg_osc_map.get(i) if leg_osc_map else None
            if r & 0xF0:
                p = align(p, 4)
                nitems = struct.unpack_from("<H", raw, data_off + p)[0]
                deg = raw[data_off + p + 2]
                p += 3 + (nitems + deg + 2)
                p = align(p, r_align)
                if i not in (0, 78, 79, 109) and i in enc_pose_quats and r_bsize == 5:
                    if osc_cfg is not None:
                        base_q = pose_quats[i]
                        osc_rx = osc_cfg.get("osc_rx_deg", 0.0)
                        osc_ry = osc_cfg.get("osc_ry_deg", 0.0)
                        osc_rz = osc_cfg.get("osc_rz_deg", 0.0)
                        phase_rad = math.radians(osc_cfg.get("phase_deg", 0.0))
                        for k in range(nitems + 1):
                            phase = (2.0 * math.pi * k) / max(1, nitems) + phase_rad
                            s_val = math.sin(phase)
                            dq = quat_from_euler_deg(osc_rx * s_val, osc_ry * s_val, osc_rz * s_val)
                            kq = quat_mul(base_q, dq)
                            raw[data_off + p + k * 5 : data_off + p + (k + 1) * 5] = encode_40bit_quat(*kq)
                    else:
                        enc_q = enc_pose_quats[i]
                        for k in range(nitems + 1):
                            raw[data_off + p + k * 5 : data_off + p + (k + 1) * 5] = enc_q
                elif i == 78:
                    first_q = bytes(raw[data_off + p : data_off + p + r_bsize])
                    for k in range(nitems + 1):
                        raw[data_off + p + k * r_bsize : data_off + p + (k + 1) * r_bsize] = first_q
                p += (nitems + 1) * r_bsize
            elif r & 0x0F:
                p = align(p, 4)
                if i not in (0, 78, 79, 109) and i in enc_pose_quats and r_bsize == 5:
                    raw[data_off + p : data_off + p + 5] = enc_pose_quats[i]
                p += r_bsize

            # 3. SCALE
            if s & 0x70:
                p = align(p, 4)
                nitems = struct.unpack_from("<H", raw, data_off + p)[0]
                deg = raw[data_off + p + 2]
                p += 3 + (nitems + deg + 2)
                p = align(p, 4)
                for bit in range(3):
                    if s & (0x10 << bit):
                        p += 8
                    elif s & (0x01 << bit):
                        p += 4
                n_sp_ch = sum(1 for bit in range(3) if (s & (0x10 << bit)))
                p += (nitems + 1) * n_sp_ch * 2
            elif s & 0x07:
                p = align(p, 4)
                n_st_ch = sum(1 for bit in range(3) if (s & (0x01 << bit)))
                p += n_st_ch * 4

            p = align(p, 4)

        next_blk_off = block_offsets[b_idx + 1] if (b_idx + 1) < nblocks else data_sz
        assert (
            align(blk_rel_off + p, 16) == next_blk_off
        ), f"AerialWeapon Spline block {b_idx} size mismatch: {align(blk_rel_off + p, 16)} != {next_blk_off}"
    return raw


def parse_bone_overrides(elem) -> dict:
    overrides = {}
    if elem is None:
        return overrides
    for b in elem.findall("Bone"):
        idx = int(b.attrib["index"])
        qx = float(b.attrib["qx"])
        qy = float(b.attrib["qy"])
        qz = float(b.attrib["qz"])
        qw = float(b.attrib["qw"])
        rx_deg = float(b.attrib.get("rx_deg", 0.0))
        ry_deg = float(b.attrib.get("ry_deg", 0.0))
        rz_deg = float(b.attrib.get("rz_deg", 0.0))
        if rx_deg != 0.0 or ry_deg != 0.0 or rz_deg != 0.0:
            qx, qy, qz, qw = quat_mul((qx, qy, qz, qw), quat_from_euler_deg(rx_deg, ry_deg, rz_deg))
        overrides[idx] = {
            "name": b.attrib.get("name", f"Bone_{idx}"),
            "quat": (qx, qy, qz, qw),
            "osc_rx_deg": float(b.attrib.get("osc_rx_deg", 0.0)),
            "osc_ry_deg": float(b.attrib.get("osc_ry_deg", 0.0)),
            "osc_rz_deg": float(b.attrib.get("osc_rz_deg", 0.0)),
            "phase_deg": float(b.attrib.get("phase_deg", 0.0)),
        }
    return overrides


def restore_clean_hover_platform_nif():
    """
    Restaura el archivo `HoverPlatform.nif` original intacto (`HoverPlatform_orig.nif`),
    garantizando que el árbol BVH/dominio de `hknpCompressedMeshShape` sea 100% nativo
    y no provoque cierres (CTD) de Havok al descargar celdas durante el Viaje Rápido.
    """
    data_nif = os.path.join(FO4_DATA_DIR, "Meshes", "AeroArmor", "HoverPlatform.nif")
    local_nif = os.path.join(LOCAL_MESHES_DIR, "AeroArmor", "HoverPlatform.nif")
    orig_backup = os.path.join(LOCAL_MESHES_DIR, "AeroArmor", "HoverPlatform_orig.nif")

    if os.path.exists(orig_backup):
        for dst in (local_nif, data_nif):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(orig_backup, dst)
        print("[OK] HoverPlatform.nif restaurado al NIF vanilla intacto (100% seguro en Fast Travel).")


def main():
    print(f"Leyendo definicion XML: {XML_PATH}")
    tree = ET.parse(XML_PATH)
    root = tree.getroot()

    ba2 = BA2AnimationReader(ANIM_BA2_PATH)
    generated_count = 0
    human_flight_files = set()
    human_descent_files = set()
    pa_flight_files = set()
    pa_descent_files = set()

    # Limpiar carpetas de destino previas para evitar archivos .hkx obsoletos
    clean_rel_dirs = [
        r"Meshes\Actors\Character\Animations\MT\AeroFlight",
        r"Meshes\Actors\Character\Animations\MT\AeroDescent",
        r"Meshes\Actors\Character\Animations\MT\Neutral\Female\BombReactionBaby",
        r"Meshes\Actors\Character\Animations\MT\Neutral\BombReaction",
        r"Meshes\Actors\Character\Animations\MT\Neutral\Military",
        r"Meshes\Actors\PowerArmor\Animations\MT\AeroFlight",
        r"Meshes\Actors\PowerArmor\Animations\MT\AeroDescent",
        r"Meshes\Actors\PowerArmor\Animations\MT\Neutral\Military",
        r"Meshes\Actors\Character\Animations\Weapon\LaserRifleGripStraight\Player\AeroSky",
        r"Meshes\Actors\PowerArmor\Animations\Weapons\CosmosPACannon\AeroSky",
        r"Meshes\Actors\Character\_1stPerson\Animations",
        r"Meshes\Actors\PowerArmor\_1stPerson\Animations",
    ]
    for base_root in (FO4_DATA_DIR, LOCAL_MESHES_DIR):
        for rel_d in clean_rel_dirs:
            full_d = os.path.join(base_root, rel_d)
            if os.path.isdir(full_d):
                shutil.rmtree(full_d, ignore_errors=True)

    try:
        human_stand_rots = extract_first_frame_rotations(
            ba2.extract(r"Meshes\Actors\Character\Animations\MT\Neutral\PoseA_Idle1.hkx")
        )
        pa_stand_rots = extract_first_frame_rotations(
            ba2.extract(r"Meshes\Actors\PowerArmor\Animations\MT\Neutral\Military\PoseA_Idle1.hkx")
        )
        for prof in root.findall("AnimationProfile"):
            prof_id = prof.attrib["id"]
            arch_folder = prof.attrib["archetypeFolder"]
            strip_footsteps = prof.attrib.get("stripFootstepSounds", "true").lower() == "true"
            com_z_human = float(prof.attrib.get("comElevationZ_Human", 76.0))
            com_z_pa = float(prof.attrib.get("comElevationZ_PA", 103.0))
            bob_z = float(prof.attrib.get("comBobAmplitudeZ", 1.0))

            human_bones = parse_bone_overrides(prof.find("BoneOverrides"))
            pa_bones = parse_bone_overrides(prof.find("PowerArmorBoneOverrides"))

            target_files = prof.find("TargetFiles").findall("File")
            print(f"\n=== Perfil: {prof_id} -> Subcarpeta: {arch_folder} ({len(target_files)} archivos) ===")

            for f_elem in target_files:
                fname = f_elem.attrib["name"]
                pa_only = f_elem.attrib.get("powerArmorOnly", "false").lower() == "true"
                legs_only = f_elem.attrib.get("legsOnly", "false").lower() == "true"

                active_human_bones = (
                    {k: v for k, v in human_bones.items() if k <= 8} if legs_only else human_bones
                )
                active_pa_bones = (
                    {k: v for k, v in pa_bones.items() if k <= 8} if legs_only else pa_bones
                )

                # 1. Generar animación para Esqueleto Humano (Masculino y Femenino)
                if not pa_only:
                    if fname.lower() == "posea_idle1.hkx":
                        human_candidates = [
                            r"Meshes\Actors\Character\Animations\MT\Neutral\Female\BombReactionBaby\PoseA_Idle1.hkx"
                            if arch_folder == "AeroFlight"
                            else r"Meshes\Actors\Character\Animations\MT\Neutral\BombReaction\PoseA_Idle1.hkx"
                        ]
                    else:
                        human_candidates = [
                            f"Meshes\\Actors\\Character\\Animations\\MT\\Neutral\\{fname}",
                            f"Meshes\\Actors\\Character\\Animations\\Weapon\\Pistol\\Player\\{fname}",
                            f"Meshes\\Actors\\Character\\Animations\\Weapon\\Pistol\\{fname}",
                            f"Meshes\\Actors\\Character\\Animations\\Player\\{fname}",
                            f"Meshes\\Actors\\Character\\Animations\\{fname}",
                        ]
                    human_src = next((c for c in human_candidates if ba2.exists(c)), None)
                    if human_src:
                        raw_human = ba2.extract(human_src)
                        mod_human = apply_xml_profile_to_hkx(
                            raw_human, active_human_bones, com_z_human, bob_z, strip_footsteps, human_stand_rots
                        )
                        sapt_mirrors = (
                            [r"Neutral\Female\BombReactionBaby"]
                            if arch_folder == "AeroFlight"
                            else [r"Neutral\BombReaction"]
                        )
                        for base_root in (FO4_DATA_DIR, LOCAL_MESHES_DIR):
                            for sub in [arch_folder] + sapt_mirrors:
                                out_path = os.path.join(
                                    base_root,
                                    "Meshes",
                                    "Actors",
                                    "Character",
                                    "Animations",
                                    "MT",
                                    sub,
                                    fname,
                                )
                                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                                with open(out_path, "wb") as out_f:
                                    out_f.write(mod_human)
                        if arch_folder == "AeroFlight":
                            human_flight_files.add(fname.lower())
                        else:
                            human_descent_files.add(fname.lower())
                        generated_count += 1

                # 2. Generar animaciones aisladas de Vuelo en Servoarmadura (perfil AeroFlight completo -> Neutral\Military)
                #    Incluye fall/impactland suavizados para evitar que al frenar un descenso parcial en pleno aire
                #    se dispare la animación pesada de impacto de rodillas antes de tocar suelo real.
                if arch_folder == "AeroFlight" and pa_bones:
                    if fname.lower() == "idle.hkx":
                        pa_candidates = [
                            r"Meshes\Actors\PowerArmor\Animations\MT\Neutral\Military\PoseA_Idle1.hkx",
                        ]
                    else:
                        pa_candidates = [
                            f"Meshes\\Actors\\PowerArmor\\Animations\\MT\\Neutral\\Military\\{fname}",
                            f"Meshes\\Actors\\PowerArmor\\Animations\\MT\\{fname}",
                            f"Meshes\\Actors\\PowerArmor\\Animations\\Weapon\\Pistol\\{fname}",
                            f"Meshes\\Actors\\PowerArmor\\Animations\\{fname}",
                        ]
                    pa_src = next((c for c in pa_candidates if ba2.exists(c)), None)
                    if pa_src:
                        raw_pa = ba2.extract(pa_src)
                        mod_pa = apply_xml_profile_to_hkx(
                            raw_pa, active_pa_bones, com_z_pa, bob_z, strip_footsteps, pa_stand_rots
                        )
                        for base_root in (FO4_DATA_DIR, LOCAL_MESHES_DIR):
                            for sub in (r"Neutral\Military", arch_folder):
                                out_pa_path = os.path.join(
                                    base_root,
                                    "Meshes",
                                    "Actors",
                                    "PowerArmor",
                                    "Animations",
                                    "MT",
                                    sub,
                                    fname,
                                )
                                os.makedirs(os.path.dirname(out_pa_path), exist_ok=True)
                                with open(out_pa_path, "wb") as out_f:
                                    out_f.write(mod_pa)
                        pa_flight_files.add(fname.lower())
                        generated_count += 1

        # 2.5. Neutralizar clips de transición de subgrafo (To_BombReaction, To_BombReactionBaby, To_Normal)
        #      usando plantillas vanilla nativas de 2 fotogramas (0.033s) sin alterar los nudos B-spline,
        #      eliminando la animación de cubrirse la cabeza (2.2s) al iniciar el descenso y el bloqueo
        #      de movimiento de 5.5s al aterrizar en 3ª persona, y preservando el cuerpo 3D intacto.
        hover_prof = next(p for p in root.findall("AnimationProfile") if p.attrib["id"] == "FlightHover")
        desc_prof = next(p for p in root.findall("AnimationProfile") if p.attrib["id"] == "FlightDescend")
        hover_h_bones = parse_bone_overrides(hover_prof.find("BoneOverrides"))
        desc_h_bones = parse_bone_overrides(desc_prof.find("BoneOverrides"))

        human_2frame_tpl = r"Meshes\Actors\Character\Animations\Furniture\FightAnnouncer\ExitToStand.hkx"
        pa_2frame_tpl = r"Meshes\Actors\PowerArmor\Animations\PowerlessIdle.hkx"

        transition_jobs = [
            # Entrada a FlightHover (BombReactionBaby): 0.033s (2 frames) en postura de vuelo
            (
                human_2frame_tpl,
                hover_h_bones,
                human_stand_rots,
                76.5,
                [
                    r"Meshes\Actors\Character\Animations\MT\Neutral\Female\To_BombReactionBaby.hkx",
                    r"Meshes\Actors\Character\Animations\MT\Neutral\To_BombReactionBaby.hkx",
                ],
            ),
            # Entrada a FlightDescend (BombReaction): 0.033s (2 frames) en postura de descenso (sin cubrirse la cabeza)
            (
                human_2frame_tpl,
                desc_h_bones,
                human_stand_rots,
                75.5,
                [
                    r"Meshes\Actors\Character\Animations\MT\Neutral\To_BombReaction.hkx",
                    r"Meshes\Actors\Character\Animations\MT\Neutral\Female\To_BombReaction.hkx",
                ],
            ),
            # Salida de BombReaction a tierra (To_Normal): 0.033s (2 frames) en postura erguida normal (elimina bloqueo de 5.47s)
            (
                human_2frame_tpl,
                {},
                human_stand_rots,
                69.1,
                [
                    r"Meshes\Actors\Character\Animations\MT\Neutral\BombReaction\To_Normal.hkx",
                ],
            ),
            # Salida de BombReactionBaby a tierra (To_Normal): 0.033s (2 frames) en postura erguida normal (elimina bloqueo de 1.77s)
            (
                human_2frame_tpl,
                {},
                human_stand_rots,
                69.1,
                [
                    r"Meshes\Actors\Character\Animations\MT\Neutral\Female\BombReactionBaby\To_Normal.hkx",
                    r"Meshes\Actors\Character\Animations\MT\Neutral\BombReactionBaby\To_Normal.hkx",
                ],
            ),
            # Salida de vuelo en Servoarmadura (Military\To_Normal): 0.033s (2 frames, elimina bloqueo de 1.33s al descender/aterrizar)
            (
                pa_2frame_tpl,
                {},
                pa_stand_rots,
                89.4,
                [
                    r"Meshes\Actors\PowerArmor\Animations\MT\Neutral\Military\To_Normal.hkx",
                ],
            ),
        ]

        trans_count = 0
        for src_ba2_key, bone_map, fb_rots, target_com_z, out_rel_list in transition_jobs:
            if ba2.exists(src_ba2_key):
                raw_tr = ba2.extract(src_ba2_key)
                fast_tr = build_fast_transition_hkx(raw_tr, bone_map, fb_rots, target_com_z)
                for rel_out in out_rel_list:
                    for base_root in (FO4_DATA_DIR, LOCAL_MESHES_DIR):
                        full_out = os.path.join(base_root, rel_out)
                        os.makedirs(os.path.dirname(full_out), exist_ok=True)
                        with open(full_out, "wb") as tf_out:
                            tf_out.write(fast_tr)
                trans_count += len(out_rel_list)
        print(f"[OK] Clips de transicion To_*/To_Normal acelerados a 0.067s: {trans_count} archivos.")

        # Eliminar 13779283315143243725.txt si existía (Human Military no usado)
        for base_root in (FO4_DATA_DIR, LOCAL_MESHES_DIR):
            for old_txt in ("13779283315143243725.txt",):
                old_mil_txt = os.path.join(
                    base_root, "Meshes", "AnimTextData", "AnimationFileData", old_txt
                )
                if os.path.exists(old_mil_txt):
                    os.remove(old_mil_txt)

        # 3. Generar overrides de AnimTextData\AnimationFileData apuntando a las carpetas SAPT aisladas
        anim_data_targets = [
            (
                "9591542742431070157.txt",
                [
                    (human_flight_files, r"Actors\Character\Animations\MT\Neutral\Female\BombReactionBaby"),
                ],
            ),
            (
                "18105890810579154893.txt",
                [
                    (human_descent_files, r"Actors\Character\Animations\MT\Neutral\BombReaction"),
                ],
            ),
            (
                "2981040044650035149.txt",
                [
                    (human_descent_files, r"Actors\Character\Animations\MT\Neutral\BombReaction"),
                ],
            ),
            (
                "6102835159731828685.txt",
                [
                    (pa_flight_files, r"Actors\PowerArmor\Animations\MT\Neutral\Military"),
                ],
            ),
        ]
        for txt_name, rule_list in anim_data_targets:
            ba2_txt_path = f"Meshes\\AnimTextData\\AnimationFileData\\{txt_name}"
            raw_txt = ba2.extract(ba2_txt_path).decode("latin1")
            lines = raw_txt.splitlines()
            replaced_lines = 0
            for idx in range(4, len(lines)):
                bname = os.path.basename(lines[idx].replace("/", "\\"))
                bname_low = bname.lower()
                for file_set, target_dir in rule_list:
                    if bname_low in file_set:
                        lines[idx] = f"{target_dir}\\{bname}"
                        replaced_lines += 1
                        break
            out_txt_bytes = ("\r\n".join(lines) + "\r\n").encode("latin1")
            for base_root in (FO4_DATA_DIR, LOCAL_MESHES_DIR):
                out_txt_path = os.path.join(
                    base_root, "Meshes", "AnimTextData", "AnimationFileData", txt_name
                )
                os.makedirs(os.path.dirname(out_txt_path), exist_ok=True)
                with open(out_txt_path, "wb") as tf:
                    tf.write(out_txt_bytes)
            print(f"[OK] AnimationFileData\\{txt_name} actualizado ({replaced_lines} rutas redirigidas).")

        # 3.5. Generar animaciones de combate aéreo con la Carabina Astro-Cosmos en 3ª persona
        #      (subgrafo WeaponBehavior 8443591340*.txt -> LaserRifleGripStraight\Player\AeroSky):
        #      - Sustituye AnimationSpeedInfo y DynamicIdleData de 8443591340* (que heredaban los
        #        contornos de cojera de pierna herida de 62.32 u/s) por los de 7567814488* (velocidad
        #        constante y lineal de 99.19 u/s con 0 curvas de tropiezo).
        #      - Calcula por cinemática directa (FK) sobre skeleton.hkx poses de tirador aeropropulsado
        #        con tren superior/manos/arma 100% estabilizados y piernas en estela aerodinámica según
        #        dirección y velocidad (levitación, avance, retroceso con aerofreno, alabeo y sprint).
        def sync_subgraph_tables(pairs, tables):
            """Copia las tablas binarias/texto de AnimTextData desde subgrafos sanos a los subgrafos aereos."""
            for sub_table in tables:
                for dst_txt, src_healthy_txt in pairs:
                    ba2_tbl_key = f"Meshes\\AnimTextData\\{sub_table}\\{src_healthy_txt}"
                    if ba2.exists(ba2_tbl_key):
                        healthy_tbl_bytes = bytes(ba2.extract(ba2_tbl_key))
                        for base_root in (FO4_DATA_DIR, LOCAL_MESHES_DIR):
                            out_tbl_p = os.path.join(base_root, "Meshes", "AnimTextData", sub_table, dst_txt)
                            os.makedirs(os.path.dirname(out_tbl_p), exist_ok=True)
                            with open(out_tbl_p, "wb") as tf_tbl:
                                tf_tbl.write(healthy_tbl_bytes)

        def collect_healthy_wpn_map(afd_names):
            """Indexa rutas de clips no heridos desde los AnimationFileData indicados."""
            out_map = {}
            for h_txt in afd_names:
                h_lines = ba2.extract(f"Meshes\\AnimTextData\\AnimationFileData\\{h_txt}").decode("latin1").splitlines()
                for hl in h_lines[4:]:
                    hb = os.path.basename(hl.replace("/", "\\")).lower()
                    if hb.endswith(".hkx") and "injured" not in hl.lower():
                        out_map[hb] = hl.replace("/", "\\")
            return out_map

        def extract_wpn_ref_poses(wpn_map, rest_pos):
            """Extrae las poses base Frame-0 (ready, relaxed, sighted, sprint) para el esqueleto dado."""
            r_ready = extract_frame0_pose(ba2.extract(f"Meshes\\{wpn_map['wpnidleready.hkx']}"), rest_pos)
            r_relaxed = (
                extract_frame0_pose(ba2.extract(f"Meshes\\{wpn_map['wpnidlerelaxed.hkx']}"), rest_pos)
                if "wpnidlerelaxed.hkx" in wpn_map
                else r_ready
            )
            r_sighted = (
                extract_frame0_pose(ba2.extract(f"Meshes\\{wpn_map['wpnidlesighted.hkx']}"), rest_pos)
                if "wpnidlesighted.hkx" in wpn_map
                else r_ready
            )
            r_sprint = (
                extract_frame0_pose(ba2.extract(f"Meshes\\{wpn_map['wpnsprint.hkx']}"), rest_pos)
                if "wpnsprint.hkx" in wpn_map
                else r_ready
            )
            return r_ready, r_relaxed, r_sighted, r_sprint

        wpn_subgraph_pairs = (
            ("8443591340230402662.txt", "7567814488867431014.txt"),
            ("8443591340344157257.txt", "7567814488981185609.txt"),
            ("8443591340433812971.txt", "7567814489070841323.txt"),
            ("8443591340896620446.txt", "7567814489533648798.txt"),
        )
        sync_subgraph_tables(wpn_subgraph_pairs, ("AnimationSpeedInfo", "AnimationStanceData", "DynamicIdleData"))
        print("[OK] SpeedInfo/StanceData/DynamicIdleData\\8443591340*.txt sincronizado con subgrafo sano 7567814488*.")

        healthy_wpn_map = collect_healthy_wpn_map((
            "15068350602796142494.txt",
            "15068350602129924710.txt",
            "7567814488867431014.txt",
            "7567814488981185609.txt",
        ))

        human_rest_pos = extract_skeleton_rest_pos(
            ba2.extract(r"Meshes\Actors\Character\CharacterAssets\skeleton.hkx")
        )
        carbine_refs = extract_wpn_ref_poses(healthy_wpn_map, human_rest_pos)

        hover_leg_bones = {k: v for k, v in hover_h_bones.items() if 3 <= k <= 8}
        xml_leg_quats = {k: v["quat"] for k, v in hover_leg_bones.items()}
        hover_leg_osc = {
            k: v
            for k, v in hover_leg_bones.items()
            if abs(v.get("osc_rx_deg", 0.0)) + abs(v.get("osc_ry_deg", 0.0)) + abs(v.get("osc_rz_deg", 0.0)) > 0.01
        }
        w_upright = (0.0, -0.7071068, 0.0, 0.7071068)

        def compute_aerial_rifle_clip_params(bname_low: str, refs=carbine_refs):
            r_ready, r_relaxed, r_sighted, r_sprint = refs
            stem = os.path.splitext(bname_low)[0].split("_")[0]
            fwd = 1.0 if "forward" in stem else (-1.0 if ("backward" in stem or "backpedal" in stem) else 0.0)
            lat = 1.0 if "right" in stem else (-1.0 if "left" in stem else 0.0)
            if fwd != 0.0 and lat != 0.0:
                fwd *= 0.75
                lat *= 0.75

            if bname_low.startswith("wpnsprint"):
                t_ref, q_ref = r_sprint
                com_z, bob, osc = 85.5, 0.0, None
                up_p, up_r, leg_p, leg_r = 14.0, 0.0, 46.0, 0.0
            elif "sighted" in stem:
                t_ref, q_ref = r_sighted
                com_z, bob, osc = 80.5, 0.0, None
                up_p, up_r, leg_p, leg_r = 0.0, 0.0, 10.0, 0.0
            elif bname_low.startswith(("wpnidle", "wpnjump", "turninplace", "sneakwpnidle")):
                t_ref, q_ref = r_relaxed if "relaxed" in stem else r_ready
                is_main_idle = bname_low in ("wpnidleready.hkx", "wpnidlerelaxed.hkx")
                com_z = 80.5
                bob = 0.50 if is_main_idle else 0.0
                osc = hover_leg_osc if is_main_idle else None
                up_p, up_r, leg_p, leg_r = 0.0, 0.0, 10.0, 0.0
            elif "run" in stem:
                if fwd == 0.0 and lat == 0.0:
                    fwd = 1.0
                t_ref, q_ref = r_relaxed if "relaxed" in stem else r_ready
                com_z, bob, osc = 84.0, 0.0, None
                up_p = (8.0 * fwd) if fwd >= 0.0 else (4.0 * fwd)
                up_r = 5.0 * lat
                leg_p = ((36.0 * fwd) if fwd > 0.0 else (20.0 * fwd)) + (10.0 if fwd == 0.0 else 0.0)
                leg_r = 24.0 * lat
            else:
                if fwd == 0.0 and lat == 0.0:
                    fwd = 1.0
                t_ref, q_ref = r_relaxed if "relaxed" in stem else r_ready
                com_z, bob, osc = 82.0, 0.0, None
                up_p = (4.0 * fwd) if fwd >= 0.0 else (3.0 * fwd)
                up_r = 3.0 * lat
                leg_p = ((24.0 * fwd) if fwd > 0.0 else (14.0 * fwd)) + (8.0 if fwd == 0.0 else 0.0)
                leg_r = 18.0 * lat

            q_up = quat_mul(quat_axis_deg(0.0, 1.0, 0.0, up_r), quat_axis_deg(1.0, 0.0, 0.0, -up_p))
            w_com = quat_mul(q_up, q_ref[1])
            q_leg_world = quat_mul(
                quat_axis_deg(0.0, 1.0, 0.0, leg_r),
                quat_mul(
                    quat_axis_deg(1.0, 0.0, 0.0, -leg_p),
                    quat_mul(quat_axis_deg(0.0, 0.0, 1.0, -18.0), w_upright),
                ),
            )
            w_com_inv = quat_inv(w_com)
            pose_q = dict(q_ref)
            pose_q[1] = w_com
            pose_q[2] = (0.0, 0.0, 0.0, 1.0)
            pose_q[3] = quat_mul(w_com_inv, quat_mul(q_leg_world, xml_leg_quats[3]))
            pose_q[4] = xml_leg_quats[4]
            pose_q[5] = xml_leg_quats[5]
            pose_q[6] = quat_mul(w_com_inv, quat_mul(q_leg_world, xml_leg_quats[6]))
            pose_q[7] = xml_leg_quats[7]
            pose_q[8] = xml_leg_quats[8]
            return t_ref, pose_q, osc, com_z, bob

        aero_sky_rel_dir = r"Actors\Character\Animations\Weapon\LaserRifleGripStraight\Player\AeroSky"
        aerial_wpn_prefixes = (
            "wpnidleready",
            "wpnidlerelaxed",
            "wpnidlesighted",
            "wpnwalk",
            "wpnrun",
            "wpnsprint",
            "wpnjump",
            "wpnstep",
            "turninplace",
            "sneakwpnwalk",
            "sneakwpnrun",
            "sneakwpnidle",
        )
        aerial_wpn_generated = {}
        wpn_afd_files = [dst_t for dst_t, _ in wpn_subgraph_pairs]
        for wtxt_name in wpn_afd_files:
            w_raw_txt = ba2.extract(f"Meshes\\AnimTextData\\AnimationFileData\\{wtxt_name}").decode("latin1")
            w_lines = w_raw_txt.splitlines()
            w_replaced = 0
            for idx in range(4, len(w_lines)):
                cur_rel = w_lines[idx].replace("/", "\\")
                bname = os.path.basename(cur_rel)
                bname_low = bname.lower()
                if not bname_low.endswith(".hkx"):
                    continue

                clean_rel = healthy_wpn_map.get(bname_low, cur_rel)
                if any(bname_low.startswith(pref) for pref in aerial_wpn_prefixes):
                    src_ba2 = f"Meshes\\{clean_rel}"
                    if not ba2.exists(src_ba2):
                        src_ba2 = f"Meshes\\{cur_rel}"
                    if ba2.exists(src_ba2):
                        if bname_low not in aerial_wpn_generated:
                            t_ref, pose_q, osc_map, clip_com_z, clip_bob = compute_aerial_rifle_clip_params(
                                bname_low
                            )
                            mod_wpn = build_aerial_weapon_hkx(
                                ba2.extract(src_ba2),
                                t_ref,
                                pose_q,
                                leg_osc_map=osc_map,
                                target_com_z=clip_com_z,
                                bob_amp_z=clip_bob,
                            )
                            for base_root in (FO4_DATA_DIR, LOCAL_MESHES_DIR):
                                out_wpn_p = os.path.join(base_root, "Meshes", aero_sky_rel_dir, bname)
                                os.makedirs(os.path.dirname(out_wpn_p), exist_ok=True)
                                with open(out_wpn_p, "wb") as wf_out:
                                    wf_out.write(mod_wpn)
                            aerial_wpn_generated[bname_low] = f"{aero_sky_rel_dir}\\{bname}"
                        w_lines[idx] = aerial_wpn_generated[bname_low]
                        w_replaced += 1
                elif "injured" in cur_rel.lower() and bname_low in healthy_wpn_map:
                    w_lines[idx] = healthy_wpn_map[bname_low]
                    w_replaced += 1

            w_out_bytes = ("\r\n".join(w_lines) + "\r\n").encode("latin1")
            for base_root in (FO4_DATA_DIR, LOCAL_MESHES_DIR):
                w_out_path = os.path.join(
                    base_root, "Meshes", "AnimTextData", "AnimationFileData", wtxt_name
                )
                os.makedirs(os.path.dirname(w_out_path), exist_ok=True)
                with open(w_out_path, "wb") as wtf:
                    wtf.write(w_out_bytes)
            print(f"[OK] AnimationFileData\\{wtxt_name} (Carabina Aerea 3aP): {w_replaced} rutas actualizadas.")
        generated_count += len(aerial_wpn_generated)
        print(f"[OK] Clips de combate aereo en 3a persona (AeroSky): {len(aerial_wpn_generated)} archivos .hkx.")

        # 3.5b. Generar animaciones de combate aéreo con el Cañón Orbital Gauss Astro-Cosmos en 3ª persona (Traje Humano)
        #       (subgrafos WeaponBehavior 13275926613*.txt -> GaussRifle\Player\AeroSky, sincronizado con 12213354680*)
        gauss_subgraph_pairs = (
            ("13275926613385503334.txt", "12213354680767439462.txt"),
            ("13275926613499257929.txt", "12213354680881194057.txt"),
            ("13275926613588913643.txt", "12213354680970849771.txt"),
            ("13275926614051721118.txt", "12213354681433657246.txt"),
        )
        sync_subgraph_tables(
            gauss_subgraph_pairs,
            ("AnimationSpeedInfo", "AnimationStanceData", "DynamicIdleData", "AnimationOffsets"),
        )
        print("[OK] Tables\\13275926613*.txt sincronizadas con subgrafo sano GaussRifle 12213354680*.")

        healthy_gauss_map = collect_healthy_wpn_map((
            "12213354680767439462.txt",
            "12213354680881194057.txt",
        ))
        gauss_refs = extract_wpn_ref_poses(healthy_gauss_map, human_rest_pos)
        gauss_aero_sky_rel_dir = r"Actors\Character\Animations\Weapon\GaussRifle\Player\AeroSky"
        gauss_aerial_generated = {}
        for gtxt_name, _ in gauss_subgraph_pairs:
            g_raw_txt = ba2.extract(f"Meshes\\AnimTextData\\AnimationFileData\\{gtxt_name}").decode("latin1")
            g_lines = g_raw_txt.splitlines()
            g_replaced = 0
            for idx in range(4, len(g_lines)):
                cur_rel = g_lines[idx].replace("/", "\\")
                bname = os.path.basename(cur_rel)
                bname_low = bname.lower()
                if not bname_low.endswith(".hkx"):
                    continue
                clean_rel = healthy_gauss_map.get(bname_low, cur_rel)
                if any(bname_low.startswith(pref) for pref in aerial_wpn_prefixes):
                    src_ba2 = f"Meshes\\{clean_rel}"
                    if not ba2.exists(src_ba2):
                        src_ba2 = f"Meshes\\{cur_rel}"
                    if ba2.exists(src_ba2):
                        if bname_low not in gauss_aerial_generated:
                            t_ref, pose_q, osc_map, clip_com_z, clip_bob = compute_aerial_rifle_clip_params(
                                bname_low, gauss_refs
                            )
                            mod_g_wpn = build_aerial_weapon_hkx(
                                ba2.extract(src_ba2),
                                t_ref,
                                pose_q,
                                leg_osc_map=osc_map,
                                target_com_z=clip_com_z,
                                bob_amp_z=clip_bob,
                            )
                            for base_root in (FO4_DATA_DIR, LOCAL_MESHES_DIR):
                                out_g_p = os.path.join(base_root, "Meshes", gauss_aero_sky_rel_dir, bname)
                                os.makedirs(os.path.dirname(out_g_p), exist_ok=True)
                                with open(out_g_p, "wb") as gf_out:
                                    gf_out.write(mod_g_wpn)
                            gauss_aerial_generated[bname_low] = f"{gauss_aero_sky_rel_dir}\\{bname}"
                        g_lines[idx] = gauss_aerial_generated[bname_low]
                        g_replaced += 1
                elif "injured" in cur_rel.lower() and bname_low in healthy_gauss_map:
                    g_lines[idx] = healthy_gauss_map[bname_low]
                    g_replaced += 1

            g_out_bytes = ("\r\n".join(g_lines) + "\r\n").encode("latin1")
            for base_root in (FO4_DATA_DIR, LOCAL_MESHES_DIR):
                g_out_path = os.path.join(
                    base_root, "Meshes", "AnimTextData", "AnimationFileData", gtxt_name
                )
                os.makedirs(os.path.dirname(g_out_path), exist_ok=True)
                with open(g_out_path, "wb") as gtf:
                    gtf.write(g_out_bytes)
            print(f"[OK] AnimationFileData\\{gtxt_name} (Canon Orbital en Traje 3aP): {g_replaced} rutas actualizadas.")
        generated_count += len(gauss_aerial_generated)
        print(f"[OK] Clips de Canon Orbital en Traje 3aP (GaussRifle AeroSky): {len(gauss_aerial_generated)} archivos .hkx.")

        # 3.6. Generar animaciones de combate aéreo con el Cañón Orbital Gauss Astro-Cosmos en Servoarmadura 3ª persona
        #      (subgrafo WeaponBehavior 18249293482037677982.txt -> PowerArmor\Animations\Weapons\CosmosPACannon\AeroSky):
        #      - Sincroniza AnimationSpeedInfo, AnimationStanceData y DynamicIdleData de 18249293482037677982.txt con el subgrafo GaussRifle
        #        de Servoarmadura 15964126763214507934.txt (incluyendo RifleBoltChargeState_SM para carga electromagnética).
        #      - Genera los clips .hkx de 110 pistas sobre PowerArmor\CharacterAssets\skeleton.hkx con tren superior,
        #        manos y cañón 100% estabilizados y piernas acorazadas en estela aerodinámica según dirección y velocidad.
        pa_gauss_crc = "15964126763214507934.txt"
        pa_aerial_crc = "18249293482037677982.txt"
        sync_subgraph_tables(((pa_aerial_crc, pa_gauss_crc),), ("AnimationSpeedInfo", "AnimationStanceData", "DynamicIdleData"))
        print(f"[OK] SpeedInfo/StanceData/DynamicIdleData\\{pa_aerial_crc} sincronizados con GaussRifle PA ({pa_gauss_crc}).")

        pa_gauss_lines = (
            ba2.extract(f"Meshes\\AnimTextData\\AnimationFileData\\{pa_gauss_crc}")
            .decode("latin1")
            .splitlines()
        )
        pa_wpn_map = collect_healthy_wpn_map((pa_gauss_crc,))

        pa_rest_pos = extract_skeleton_rest_pos(
            ba2.extract(r"Meshes\Actors\PowerArmor\CharacterAssets\skeleton.hkx"),
            num_tracks=110,
        )
        pa_cannon_refs = extract_wpn_ref_poses(pa_wpn_map, pa_rest_pos)

        hover_pa_bones_full = parse_bone_overrides(hover_prof.find("PowerArmorBoneOverrides"))
        hover_pa_leg_bones = {k: v for k, v in hover_pa_bones_full.items() if 3 <= k <= 8}
        hover_pa_leg_osc = {
            k: v
            for k, v in hover_pa_leg_bones.items()
            if abs(v.get("osc_rx_deg", 0.0)) + abs(v.get("osc_ry_deg", 0.0)) + abs(v.get("osc_rz_deg", 0.0)) > 0.01
        }
        w_hov_pa_com = hover_pa_bones_full[1]["quat"]

        def compute_pa_aerial_rifle_clip_params(bname_low: str, pa_refs=pa_cannon_refs):
            pr_ready, pr_relaxed, pr_sighted, pr_sprint = pa_refs
            stem = os.path.splitext(bname_low)[0].split("_")[0]
            fwd = 1.0 if "forward" in stem else (-1.0 if ("backward" in stem or "backpedal" in stem) else 0.0)
            lat = 1.0 if "right" in stem else (-1.0 if "left" in stem else 0.0)
            if fwd != 0.0 and lat != 0.0:
                fwd *= 0.75
                lat *= 0.75

            if bname_low.startswith("wpnsprint"):
                t_ref, q_ref = pr_sprint
                com_z, bob, osc = 110.5, 0.0, None
                up_p, up_r, leg_p, leg_r = 12.0, 0.0, 42.0, 0.0
            elif "sighted" in stem:
                t_ref, q_ref = pr_sighted
                com_z, bob, osc = 104.5, 0.0, None
                up_p, up_r, leg_p, leg_r = 0.0, 0.0, 10.0, 0.0
            elif bname_low.startswith(("wpnidle", "wpnjump", "turninplace", "sneakwpnidle")):
                t_ref, q_ref = pr_relaxed if "relaxed" in stem else pr_ready
                is_main_idle = bname_low in ("wpnidleready.hkx", "wpnidlerelaxed.hkx")
                com_z = 104.5
                bob = 0.55 if is_main_idle else 0.0
                osc = hover_pa_leg_osc if is_main_idle else None
                up_p, up_r, leg_p, leg_r = 0.0, 0.0, 10.0, 0.0
            elif "run" in stem:
                if fwd == 0.0 and lat == 0.0:
                    fwd = 1.0
                t_ref, q_ref = pr_relaxed if "relaxed" in stem else pr_ready
                com_z, bob, osc = 108.5, 0.0, None
                up_p = (7.0 * fwd) if fwd >= 0.0 else (3.5 * fwd)
                up_r = 4.5 * lat
                leg_p = ((34.0 * fwd) if fwd > 0.0 else (18.0 * fwd)) + (10.0 if fwd == 0.0 else 0.0)
                leg_r = 22.0 * lat
            else:
                if fwd == 0.0 and lat == 0.0:
                    fwd = 1.0
                t_ref, q_ref = pr_relaxed if "relaxed" in stem else pr_ready
                com_z, bob, osc = 106.5, 0.0, None
                up_p = (3.5 * fwd) if fwd >= 0.0 else (2.5 * fwd)
                up_r = 2.5 * lat
                leg_p = ((22.0 * fwd) if fwd > 0.0 else (12.0 * fwd)) + (8.0 if fwd == 0.0 else 0.0)
                leg_r = 16.0 * lat

            q_up = quat_mul(quat_axis_deg(0.0, 1.0, 0.0, up_r), quat_axis_deg(1.0, 0.0, 0.0, -up_p))
            w_com = quat_mul(q_up, q_ref[1])
            q_delta = quat_mul(
                quat_axis_deg(0.0, 1.0, 0.0, leg_r),
                quat_axis_deg(1.0, 0.0, 0.0, -(leg_p - 8.0)),
            )
            w_pel = quat_mul(w_com, q_ref[2])
            w_pel_inv = quat_inv(w_pel)
            pose_q = dict(q_ref)
            pose_q[1] = w_com
            for th in (3, 6):
                w_th_hov = quat_mul(quat_mul(w_hov_pa_com, q_ref[2]), hover_pa_leg_bones[th]["quat"])
                pose_q[th] = quat_mul(w_pel_inv, quat_mul(q_delta, w_th_hov))
            pose_q[4] = hover_pa_leg_bones[4]["quat"]
            pose_q[5] = hover_pa_leg_bones[5]["quat"]
            pose_q[7] = hover_pa_leg_bones[7]["quat"]
            pose_q[8] = hover_pa_leg_bones[8]["quat"]
            return t_ref, pose_q, osc, com_z, bob

        def build_pa_aerial_afd_set(src_crc: str, dst_crc: str, dst_rel_dir: str, pa_refs, label: str):
            """Genera un conjunto completo de animaciones aereas PA y escribe su AnimationFileData."""
            src_lines = (
                ba2.extract(f"Meshes\\AnimTextData\\AnimationFileData\\{src_crc}")
                .decode("latin1")
                .splitlines()
            )
            generated_map = {}
            out_lines = list(src_lines)
            out_lines[2] = os.path.splitext(dst_crc)[0]
            replaced_cnt = 0
            for idx in range(4, len(out_lines)):
                cur_rel = out_lines[idx].replace("/", "\\")
                bname = os.path.basename(cur_rel)
                bname_low = bname.lower()
                if not bname_low.endswith(".hkx"):
                    continue
                if any(bname_low.startswith(pref) for pref in aerial_wpn_prefixes):
                    src_ba2 = f"Meshes\\{cur_rel}"
                    if ba2.exists(src_ba2):
                        if bname_low not in generated_map:
                            t_ref, pose_q, osc_map, clip_com_z, clip_bob = compute_pa_aerial_rifle_clip_params(
                                bname_low, pa_refs
                            )
                            mod_pa_wpn = build_aerial_weapon_hkx(
                                ba2.extract(src_ba2),
                                t_ref,
                                pose_q,
                                leg_osc_map=osc_map,
                                target_com_z=clip_com_z,
                                bob_amp_z=clip_bob,
                            )
                            for base_root in (FO4_DATA_DIR, LOCAL_MESHES_DIR):
                                out_pa_wpn_p = os.path.join(base_root, "Meshes", dst_rel_dir, bname)
                                os.makedirs(os.path.dirname(out_pa_wpn_p), exist_ok=True)
                                with open(out_pa_wpn_p, "wb") as pwf_out:
                                    pwf_out.write(mod_pa_wpn)
                            generated_map[bname_low] = f"{dst_rel_dir}\\{bname}"
                        out_lines[idx] = generated_map[bname_low]
                        replaced_cnt += 1

            out_bytes = ("\r\n".join(out_lines) + "\r\n").encode("latin1")
            for base_root in (FO4_DATA_DIR, LOCAL_MESHES_DIR):
                out_path = os.path.join(base_root, "Meshes", "AnimTextData", "AnimationFileData", dst_crc)
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with open(out_path, "wb") as pwtf:
                    pwtf.write(out_bytes)
            print(
                f"[OK] AnimationFileData\\{dst_crc} ({label}): "
                f"{replaced_cnt} rutas actualizadas ({len(generated_map)} clips .hkx)."
            )
            return len(generated_map)

        generated_count += build_pa_aerial_afd_set(
            pa_gauss_crc,
            pa_aerial_crc,
            r"Actors\PowerArmor\Animations\Weapons\CosmosPACannon\AeroSky",
            pa_cannon_refs,
            "Canon Orbital PA 3aP",
        )

        # 3.6b. Generar animaciones de combate aéreo con la Carabina de Rayos Astro-Cosmos en Servoarmadura 3ª persona
        #       (subgrafo WeaponBehavior 1769963494426611614.txt -> PowerArmor\Animations\Weapons\CosmosHeroCarbine\AeroSky,
        #       sincronizado con LaserRifleGripStraight PA 4841667677245476766.txt).
        pa_laser_crc = "4841667677245476766.txt"
        pa_carbine_aerial_crc = "1769963494426611614.txt"
        sync_subgraph_tables(
            ((pa_carbine_aerial_crc, pa_laser_crc),),
            ("AnimationSpeedInfo", "AnimationStanceData", "DynamicIdleData"),
        )
        print(f"[OK] SpeedInfo/StanceData/DynamicIdleData\\{pa_carbine_aerial_crc} sincronizados con LaserRifleGripStraight PA ({pa_laser_crc}).")
        pa_laser_wpn_map = collect_healthy_wpn_map((pa_laser_crc,))
        pa_laser_refs = extract_wpn_ref_poses(pa_laser_wpn_map, pa_rest_pos)
        generated_count += build_pa_aerial_afd_set(
            pa_laser_crc,
            pa_carbine_aerial_crc,
            r"Actors\PowerArmor\Animations\Weapons\CosmosHeroCarbine\AeroSky",
            pa_laser_refs,
            "Carabina en PA 3aP",
        )

        # 4. Suavizar las animaciones de locomocion en 1a persona (desarmado + Carabina + Canon Orbital PA)
        #    estabilizando COM (Track 1), brazos/arma (2..77) y Camera (Track 78) para un planeo 100% fluido
        fp_rel_paths = [
            r"Actors\Character\_1stPerson\Animations\Common\RunForwardReady.hkx",
            r"Actors\Character\_1stPerson\Animations\Common\JumpImpactLand.hkx",
            r"Actors\Character\_1stPerson\Animations\Rifle\MTSprint.hkx",
            r"Actors\Character\_1stPerson\Animations\LaserRifleGripStraight\WPNWalkForwardReady.hkx",
            r"Actors\Character\_1stPerson\Animations\LaserRifleGripStraight\WPNWalkForwardSighted.hkx",
            r"Actors\Character\_1stPerson\Animations\LaserRifleGripStraight\WPNRunForwardReady.hkx",
            r"Actors\Character\_1stPerson\Animations\LaserRifleGripStraight\WPNRunGunDown.hkx",
            r"Actors\Character\_1stPerson\Animations\LaserRifleGripStraight\WPNRunLeftReady.hkx",
            r"Actors\Character\_1stPerson\Animations\LaserRifleGripStraight\WPNRunRightReady.hkx",
            r"Actors\Character\_1stPerson\Animations\LaserRifleGripStraight\WPNSprint.hkx",
            r"Actors\Character\_1stPerson\Animations\LaserRifleGripStraight\WPNJumpImpactLand.hkx",
            r"Actors\Character\_1stPerson\Animations\GaussRifle\WPNWalkForwardReady.hkx",
            r"Actors\Character\_1stPerson\Animations\GaussRifle\WPNWalkForwardSighted.hkx",
            r"Actors\Character\_1stPerson\Animations\GaussRifle\WPNRunForwardReady.hkx",
            r"Actors\Character\_1stPerson\Animations\GaussRifle\WPNRunGunDown.hkx",
            r"Actors\Character\_1stPerson\Animations\GaussRifle\WPNRunLeftReady.hkx",
            r"Actors\Character\_1stPerson\Animations\GaussRifle\WPNRunRightReady.hkx",
            r"Actors\Character\_1stPerson\Animations\GaussRifle\WPNSprint.hkx",
            r"Actors\Character\_1stPerson\Animations\GaussRifle\WPNJumpImpactLand.hkx",
            r"Actors\PowerArmor\_1stPerson\Animations\Common\RunForwardReady.hkx",
            r"Actors\PowerArmor\_1stPerson\Animations\Common\MTSprint.hkx",
            r"Actors\PowerArmor\_1stPerson\Animations\Common\JumpImpactLand.hkx",
            r"Actors\PowerArmor\_1stPerson\Animations\GaussRifle\WPNWalkForwardReady.hkx",
            r"Actors\PowerArmor\_1stPerson\Animations\GaussRifle\WPNWalkForwardSighted.hkx",
            r"Actors\PowerArmor\_1stPerson\Animations\GaussRifle\WPNRunForwardReady.hkx",
            r"Actors\PowerArmor\_1stPerson\Animations\GaussRifle\WPNRunGunDown.hkx",
            r"Actors\PowerArmor\_1stPerson\Animations\GaussRifle\WPNRunLeftReady.hkx",
            r"Actors\PowerArmor\_1stPerson\Animations\GaussRifle\WPNRunRightReady.hkx",
            r"Actors\PowerArmor\_1stPerson\Animations\GaussRifle\WPNSprint.hkx",
            r"Actors\PowerArmor\_1stPerson\Animations\LaserRifleGripStraight\WPNWalkForwardReady.hkx",
            r"Actors\PowerArmor\_1stPerson\Animations\LaserRifleGripStraight\WPNWalkForwardSighted.hkx",
            r"Actors\PowerArmor\_1stPerson\Animations\LaserRifleGripStraight\WPNRunForwardReady.hkx",
            r"Actors\PowerArmor\_1stPerson\Animations\LaserRifleGripStraight\WPNRunGunDown.hkx",
            r"Actors\PowerArmor\_1stPerson\Animations\LaserRifleGripStraight\WPNRunLeftReady.hkx",
            r"Actors\PowerArmor\_1stPerson\Animations\LaserRifleGripStraight\WPNRunRightReady.hkx",
            r"Actors\PowerArmor\_1stPerson\Animations\LaserRifleGripStraight\WPNSprint.hkx",
        ]

        fp_generated = 0
        for rel_p in fp_rel_paths:
            ba2_key = f"Meshes\\{rel_p}"
            if ba2.exists(ba2_key):
                raw_fp = ba2.extract(ba2_key)
                mod_fp = smooth_first_person_hkx(raw_fp)
                for base_root in (FO4_DATA_DIR, LOCAL_MESHES_DIR):
                    out_fp_path = os.path.join(base_root, "Meshes", rel_p)
                    os.makedirs(os.path.dirname(out_fp_path), exist_ok=True)
                    with open(out_fp_path, "wb") as f_out:
                        f_out.write(mod_fp)
                fp_generated += 1

        print(f"[OK] Animaciones desarmadas de 1a persona suavizadas (Camera Track 78): {fp_generated} archivos.")

        print(f"\n[OK] Total de animaciones .hkx generadas e instaladas desde XML: {generated_count + fp_generated}")
    finally:
        ba2.close()

    restore_clean_hover_platform_nif()

    # Sincronizar también AeroArmorMod.esp en Data\
    try:
        import update_aero_esp
        update_aero_esp.main()
    except Exception as e:
        print(f"[AVISO] No se pudo actualizar AeroArmorMod.esp: {e}")


if __name__ == "__main__":
    main()
