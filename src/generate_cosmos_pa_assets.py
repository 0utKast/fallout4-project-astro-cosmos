#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_cosmos_pa_assets.py
============================
Genera de forma 100 % autónoma (cero dependencias de Creation Club / terceros) todos los
activos 3D PBR de la «Servoarmadura Astro-Cosmos» (6 piezas a juego inspiradas en el
Capitán Cosmos de Hubris Comics) para Fallout 4 (1.10.163 y Next-Gen/AE):

  - Texturas 2048x2048 BC1/DXT1 (12 mipmaps) y mapas normales/especulares BC5/ATI2:
      * CosmosPABody_d.dds / _n.dds / _s.dds   (Coraza azul cobalto cósmico + cintura carmesí + remaches dorados)
      * CosmosPAHelmet_d.dds / _n.dds / _s.dds (Casco cobalto + sellado carmesí + válvulas doradas)
      * CosmosPAArm_d.dds / _n.dds / _s.dds    (Hombreras y bíceps cobalto + guanteletes espaciales carmesí y oro)
      * CosmosPALeg_d.dds / _n.dds / _s.dds    (Musleras cobalto + grebas/botas espaciales carmesí y oro)
      * CosmosPAGold_d.dds / _n.dds / _s.dds   (Oro aeroespacial bruñido 24k)
      * CosmosPAVisor_d.dds / _n.dds / _s.dds  (Visor panorámico reflectante oro-iridio)
      * CosmosPAGlow_d.dds / _n.dds / _s.dds   (Plasma estelar cian autoiluminado)
  - Materiales binarios BGSM v2:
      * CosmosPABody.BGSM, CosmosPAHelmet.BGSM, CosmosPAArm.BGSM, CosmosPALeg.BGSM
      * CosmosPAGold.BGSM, CosmosPAVisor.BGSM (castShadows=False para linterna), CosmosPAGlow.BGSM (emissive)
  - Modelos 3D .NIF esculpidos y riggeados en Blender 5.2 + PyNifly 30.2.0 con BSConnectPoints exactos:
      * CosmosPA_Body.nif   (Propulsor dorsal birreactor con aletas cósmicas doradas + toberas de plasma cian
                             dejando libre el puerto central del núcleo de fusión + emblema pectoral 3D + cinturón en V)
      * CosmosPA_Helmet.nif (Visor curvo panorámico oro-iridio + cresta dorsal Art-Deco + antenas laterales)
      * CosmosPA_LArm.nif / CosmosPA_RArm.nif + _1st.nif (Chevrón alado en hombreras + aleta y brazalete en guanteletes)
      * CosmosPA_LLeg.nif / CosmosPA_RLeg.nif (Escudos de rodilla en V + aletas estabilizadoras de tobillo)
      * GO_CosmosPA_Body.nif / GO_CosmosPA_Helmet.nif / GO_CosmosPA_Arm.nif / GO_CosmosPA_Leg.nif (Pip-Boy / mundo)
"""

import math
import os
import shutil
import struct
import subprocess
import sys
from collections import deque
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

from fallout_pbr_weathering import (
    extract_masked_template_highpass,
    height_to_bc5_normal,
    tileable_fbm,
    weather_antique_brass,
    weather_painted_metal,
    directional_scratches_and_drips,
)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_MESHES_DIR = os.path.join(THIS_DIR, "tools_3d", "test_meshes")
PA_TPL_DIR = os.path.join(TEST_MESHES_DIR, "pa_templates")
FO4_DATA_DIR = r"C:\Program Files (x86)\Steam\steamapps\common\Fallout 4\Data"

PA_ASSETS_DIR = os.path.join(THIS_DIR, "cosmos_pa_assets")
TEX_OUT_DIR = os.path.join(PA_ASSETS_DIR, "textures", "AeroArmor", "PowerArmor")
MAT_OUT_DIR = os.path.join(PA_ASSETS_DIR, "materials", "AeroArmor", "PowerArmor")
MESH_OUT_DIR = os.path.join(PA_ASSETS_DIR, "meshes", "AeroArmor", "PowerArmor")

BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
PYNIFLY_DIR = r"C:\Users\educa\AppData\Roaming\Blender Foundation\Blender\5.2\scripts\addons\io_scene_nifly"

if PYNIFLY_DIR not in sys.path:
    sys.path.insert(0, PYNIFLY_DIR)
from pyn import pynifly
from pyn.bgsmaterial import BGSMaterial


# ==============================================================================
# 1. CODIFICADORES BINARIOS DDS (BC1 / DXT1 Y BC5 / ATI2) Y MATERIALES BGSM V2
# ==============================================================================
def _rgb_to_565(r: np.ndarray, g: np.ndarray, b: np.ndarray) -> np.ndarray:
    r5 = np.clip(np.round(r * (31.0 / 255.0)), 0, 31).astype(np.uint16)
    g6 = np.clip(np.round(g * (63.0 / 255.0)), 0, 63).astype(np.uint16)
    b5 = np.clip(np.round(b * (31.0 / 255.0)), 0, 31).astype(np.uint16)
    return (r5 << 11) | (g6 << 5) | b5


def _565_to_rgb_float(c565: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    r = ((c565 >> 11) & 0x1F).astype(np.float32) * (255.0 / 31.0)
    g = ((c565 >> 5) & 0x3F).astype(np.float32) * (255.0 / 63.0)
    b = (c565 & 0x1F).astype(np.float32) * (255.0 / 31.0)
    return r, g, b


def compress_bc1_level(rgb: np.ndarray) -> bytes:
    h, w, _ = rgb.shape
    pad_h = max(4, (h + 3) & ~3)
    pad_w = max(4, (w + 3) & ~3)
    if pad_h != h or pad_w != w:
        padded = np.zeros((pad_h, pad_w, 3), dtype=np.uint8)
        padded[:h, :w] = rgb
        padded[h:, :w] = rgb[h - 1 : h, :w]
        padded[:, w:] = padded[:, w - 1 : w]
        rgb = padded

    bh, bw = pad_h // 4, pad_w // 4
    blocks = rgb.reshape(bh, 4, bw, 4, 3).transpose(0, 2, 1, 3, 4).reshape(-1, 16, 3).astype(np.float32)

    lum = 0.299 * blocks[:, :, 0] + 0.587 * blocks[:, :, 1] + 0.114 * blocks[:, :, 2]
    min_idx = np.argmin(lum, axis=1)
    max_idx = np.argmax(lum, axis=1)
    n_blocks = blocks.shape[0]
    ar = np.arange(n_blocks)

    c_max = blocks[ar, max_idx]
    c_min = blocks[ar, min_idx]

    c0_565 = _rgb_to_565(c_max[:, 0], c_max[:, 1], c_max[:, 2])
    c1_565 = _rgb_to_565(c_min[:, 0], c_min[:, 1], c_min[:, 2])

    swap = c0_565 < c1_565
    c0_final = np.where(swap, c1_565, c0_565)
    c1_final = np.where(swap, c0_565, c1_565)

    equal = c0_final == c1_final
    can_inc = equal & (c0_final < 0xFFFF)
    can_dec = equal & (~can_inc)
    c0_final = np.where(can_inc, c0_final + 1, c0_final)
    c1_final = np.where(can_dec, c1_final - 1, c1_final)

    r0, g0, b0 = _565_to_rgb_float(c0_final)
    r1, g1, b1 = _565_to_rgb_float(c1_final)

    pal = np.empty((n_blocks, 4, 3), dtype=np.float32)
    pal[:, 0, 0], pal[:, 0, 1], pal[:, 0, 2] = r0, g0, b0
    pal[:, 1, 0], pal[:, 1, 1], pal[:, 1, 2] = r1, g1, b1
    pal[:, 2, 0] = (2.0 * r0 + r1) / 3.0
    pal[:, 2, 1] = (2.0 * g0 + g1) / 3.0
    pal[:, 2, 2] = (2.0 * b0 + b1) / 3.0
    pal[:, 3, 0] = (r0 + 2.0 * r1) / 3.0
    pal[:, 3, 1] = (g0 + 2.0 * g1) / 3.0
    pal[:, 3, 2] = (b0 + 2.0 * b1) / 3.0

    diff = blocks[:, :, None, :] - pal[:, None, :, :]
    dist2 = np.sum(diff * diff, axis=3)
    best = np.argmin(dist2, axis=2).astype(np.uint32)

    shifts = (np.arange(16, dtype=np.uint32) * 2)[None, :]
    indices32 = np.sum(best << shifts, axis=1, dtype=np.uint32)

    out = np.empty(n_blocks, dtype=[("c0", "<u2"), ("c1", "<u2"), ("idx", "<u4")])
    out["c0"] = c0_final
    out["c1"] = c1_final
    out["idx"] = indices32
    return out.tobytes()


def write_bc1_dds_from_image(dst_path: str, base_img: Image.Image) -> None:
    if base_img.size != (2048, 2048):
        base_img = base_img.resize((2048, 2048), Image.Resampling.LANCZOS)
    mips = []
    cur = base_img.convert("RGB")
    for level in range(12):
        arr = np.asarray(cur, dtype=np.uint8)
        mips.append(compress_bc1_level(arr))
        if level < 11:
            nw = max(1, cur.width // 2)
            nh = max(1, cur.height // 2)
            cur = cur.resize((nw, nh), Image.Resampling.LANCZOS)

    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    flags = 0x00000001 | 0x00000002 | 0x00000004 | 0x00001000 | 0x00020000 | 0x00080000
    pf = struct.pack("<II4sIIIII", 32, 0x00000004, b"DXT1", 0, 0, 0, 0, 0)
    caps = 0x00001000 | 0x00000008 | 0x00400000
    hdr = struct.pack(
        "<4sIIIIIII44s32sIIIII",
        b"DDS ",
        124,
        flags,
        2048,
        2048,
        len(mips[0]),
        0,
        len(mips),
        b"\x00" * 44,
        pf,
        caps,
        0,
        0,
        0,
        0,
    )
    with open(dst_path, "wb") as wf:
        wf.write(hdr)
        for m in mips:
            wf.write(m)


def compress_bc4_channel(ch: np.ndarray) -> np.ndarray:
    h, w = ch.shape
    pad_h = max(4, (h + 3) & ~3)
    pad_w = max(4, (w + 3) & ~3)
    if pad_h != h or pad_w != w:
        padded = np.zeros((pad_h, pad_w), dtype=np.float32)
        padded[:h, :w] = ch
        padded[h:, :w] = ch[h - 1 : h, :w]
        padded[:, w:] = padded[:, w - 1 : w]
        ch = padded
    else:
        ch = ch.astype(np.float32)

    bh, bw = pad_h // 4, pad_w // 4
    vals = ch.reshape(bh, 4, bw, 4).transpose(0, 2, 1, 3).reshape(-1, 16)
    new_max = np.clip(np.round(vals.max(axis=1)), 0, 255).astype(np.uint8)
    new_min = np.clip(np.round(vals.min(axis=1)), 0, 255).astype(np.uint8)
    eq = new_max <= new_min
    new_max = np.where(eq & (new_max < 255), new_min + 1, new_max)
    new_min = np.where(eq & (new_max == 255), new_max - 1, new_min)

    p_new = np.empty((len(new_max), 8), dtype=np.float32)
    p_new[:, 0] = new_max
    p_new[:, 1] = new_min
    for k in range(1, 7):
        p_new[:, k + 1] = ((7 - k) * p_new[:, 0] + k * p_new[:, 1]) / 7.0

    shifts = np.arange(0, 48, 3, dtype=np.uint64)[None, :]
    dists = np.abs(vals[:, :, None] - p_new[:, None, :])
    best_idx = np.argmin(dists, axis=2).astype(np.uint64)
    bits48 = np.sum(best_idx << shifts, axis=1, dtype=np.uint64)

    out = np.empty((len(new_max), 8), dtype=np.uint8)
    out[:, 0] = new_max
    out[:, 1] = new_min
    for b in range(6):
        out[:, 2 + b] = ((bits48 >> (8 * b)) & 0xFF).astype(np.uint8)
    return out


def write_bc5_dds_from_rg_arrays(dst_path: str, r_img: np.ndarray, g_img: np.ndarray, nmips: int = 11) -> None:
    h, w = r_img.shape
    cur_r = Image.fromarray(np.clip(r_img, 0, 255).astype(np.uint8), mode="L")
    cur_g = Image.fromarray(np.clip(g_img, 0, 255).astype(np.uint8), mode="L")
    chunks = []
    for mip_idx in range(nmips):
        ra = np.asarray(cur_r, dtype=np.float32)
        ga = np.asarray(cur_g, dtype=np.float32)
        b_r = compress_bc4_channel(ra)
        b_g = compress_bc4_channel(ga)
        blk16 = np.concatenate([b_r, b_g], axis=1)
        chunks.append(blk16.tobytes())
        if mip_idx < nmips - 1:
            nw = max(1, cur_r.width // 2)
            nh = max(1, cur_r.height // 2)
            cur_r = cur_r.resize((nw, nh), Image.Resampling.LANCZOS)
            cur_g = cur_g.resize((nw, nh), Image.Resampling.LANCZOS)

    top_size = (w // 4) * (h // 4) * 16
    ddspf = struct.pack("<II4sIIIII", 32, 0x4, b"ATI2", 0, 0, 0, 0, 0)
    header = struct.pack(
        "<IIIIIII44s32sIIIII",
        124,
        0x1 | 0x2 | 0x4 | 0x1000 | 0x20000 | 0x80000,
        h,
        w,
        top_size,
        0,
        nmips,
        b"\x00" * 44,
        ddspf,
        0x8 | 0x1000 | 0x400000,
        0,
        0,
        0,
        0,
    )
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    with open(dst_path, "wb") as wf:
        wf.write(b"DDS " + header + b"".join(chunks))


def build_bgsm_v2_bytes(
    diffuse_path: str,
    normal_path: str,
    specular_path: str,
    envmap_path: str = "Shared/Cubemaps/mipblur_DefaultOutside1.dds",
    root_material: str = "template/OutfitTemplate_Wet.bgsm",
    envmap_scale: float = 1.15,
    specular_color: tuple[float, float, float] = (0.92, 0.96, 1.00),
    specular_mult: float = 1.45,
    smoothness: float = 1.35,
    subsurface_lighting: int = 0,
    subsurface_rolloff: float = 0.0,
    two_sided: bool = False,
    cast_shadows: bool = True,
    emit_enabled: bool = False,
    emit_color: tuple[float, float, float] = (0.0, 0.0, 0.0),
    emit_mult: float = 1.0,
) -> bytes:
    """Construye un archivo binario BGSM v2 válido y lo verifica con BGSMaterial de PyNifly."""
    with open(os.path.join(TEST_MESHES_DIR, "syntharmorblack.bgsm"), "rb") as rf:
        tpl = rf.read()

    hdr = bytearray(tpl[:63])
    hdr[48] = 1 if two_sided else 0  # twoSided
    hdr[57] = 1  # environmentMapping = True
    struct.pack_into("<f", hdr, 58, envmap_scale)
    hdr[62] = 0  # grayscaleToPaletteColor = False

    def pack_lstr(s: str) -> bytes:
        b = s.encode("ascii") + b"\x00"
        return struct.pack("<I", len(b)) + b

    tex_block = (
        pack_lstr(diffuse_path)
        + pack_lstr(normal_path)
        + pack_lstr(specular_path)
        + pack_lstr("")
        + pack_lstr(envmap_path)
        + pack_lstr("")
        + pack_lstr("")
        + pack_lstr("")
        + pack_lstr("")
    )

    mid_64 = struct.pack(
        "<BBffBfBffffffffffff",
        0,
        0,
        2.0,
        0.0,
        subsurface_lighting,
        subsurface_rolloff,
        1,
        specular_color[0],
        specular_color[1],
        specular_color[2],
        specular_mult,
        smoothness,
        5.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
    )

    root_block = pack_lstr(root_material)
    tail_src = bytearray(tpl[-59:])
    # Offset en tail_59 (sin emittanceColor):
    # [0]=anisoLighting, [1]=emitEnabled, [2..5]=emittanceMult, [6]=modelSpaceNormals,
    # [7]=externalEmittance, [8]=backLighting, [9]=receiveShadows, [10]=hideSecret, [11]=castShadows
    tail_src[11] = 1 if cast_shadows else 0
    if emit_enabled:
        tail = (
            struct.pack("<BB3ff", 0, 1, emit_color[0], emit_color[1], emit_color[2], emit_mult)
            + bytes(tail_src[6:])
        )
    else:
        tail_src[0] = 0
        tail_src[1] = 0
        struct.pack_into("<f", tail_src, 2, 1.0)
        tail = bytes(tail_src)

    return bytes(hdr) + tex_block + mid_64 + root_block + tail


# ==============================================================================
# 2. PINTURA UV PBR 2K BASADA EN PLACAS REALES DE SERVOARMADURA + HIGH-PASS ENMASCARADO + DESGASTE FALLOUT
# ==============================================================================
def _extract_pa_highpass(src_dds_path: str, detail_gain: float = 0.88, macro_gain: float = 0.14) -> np.ndarray:
    """Usa extract_masked_template_highpass para evitar halos blancos/rosados de fondo negro."""
    return extract_masked_template_highpass(
        src_dds_path,
        lum_thresh=14.0,
        detail_gain=detail_gain,
        macro_gain=macro_gain,
    )


def _connected_plate_components(shape):
    adj = [set() for _ in range(len(shape.verts))]
    for a, b, c in shape.tris:
        adj[a].update([b, c])
        adj[b].update([a, c])
        adj[c].update([a, b])
    vis = set()
    vert_to_comp = {}
    comps = []
    for i in range(len(shape.verts)):
        if i in vis:
            continue
        q = deque([i])
        vis.add(i)
        comp = []
        while q:
            u = q.popleft()
            comp.append(u)
            for w in adj[u]:
                if w not in vis:
                    vis.add(w)
                    q.append(w)
        cid = len(comps)
        for v in comp:
            vert_to_comp[v] = cid
        comps.append(comp)
    return comps, vert_to_comp


def _dilate_zone_map(zone_img: Image.Image, radius_iters: int = 8) -> np.ndarray:
    """Expande cada isla UV hacia los márgenes vacíos para evitar sangrado en mipmaps."""
    z = np.asarray(zone_img, dtype=np.uint8).copy()
    for _ in range(radius_iters):
        empty = z == 0
        if not np.any(empty):
            break
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            shifted = np.roll(np.roll(z, dy, axis=0), dx, axis=1)
            fill = empty & (shifted > 0)
            z[fill] = shifted[fill]
            empty = z == 0
    z[z == 0] = 1  # fondo por defecto: cobalto
    return z


def _paint_armor_sheet_from_zones(
    tpl_diff_dds: str,
    zone_map: np.ndarray,
    preview_png_path: str = "",
    seed: int = 310,
) -> tuple[Image.Image, np.ndarray, np.ndarray]:
    """
    Combina el mapa de zonas por placa (1=Azul Cobalto Envejecido, 2=Carmesí Óxido, 3=Latón Antiguo,
    4=Acero Pavonado) con el relieve High-Pass enmascarado de T-51 y el envejecido Fallout 4
    (desconchones de pintura, arañazos, óxido en costuras y especular calibrado).
    """
    hp = _extract_pa_highpass(tpl_diff_dds, detail_gain=0.86, macro_gain=0.14)
    edge_mask = np.clip((hp - 2.5) / 13.0, 0.0, 1.0).astype(np.float32)
    cav_mask = np.clip((-hp - 2.5) / 13.0, 0.0, 1.0).astype(np.float32)

    # Capas base envejecidas estilo Fallout 4 por zona
    cob_rgb, _, cob_sr, cob_sg = weather_painted_metal(
        (36.0, 60.0, 106.0), edge_mask, cav_mask, seed=seed + 1,
        chip_amount=0.38, grime_amount=0.42, rust_amount=0.22,
    )
    crim_rgb, _, crim_sr, crim_sg = weather_painted_metal(
        (122.0, 28.0, 30.0), edge_mask, cav_mask, seed=seed + 2,
        chip_amount=0.36, grime_amount=0.40, rust_amount=0.20,
    )
    brass_rgb, _, brass_sr, brass_sg = weather_antique_brass(
        2048, 2048, cavity_mask=cav_mask, seed=seed + 3,
    )
    steel_rgb, _, steel_sr, steel_sg = weather_painted_metal(
        (76.0, 82.0, 90.0), edge_mask, cav_mask, seed=seed + 4,
        chip_amount=0.25, grime_amount=0.48, rust_amount=0.28,
    )

    zone_layers = {
        1: (cob_rgb, cob_sr, cob_sg),
        2: (crim_rgb, crim_sr, crim_sg),
        3: (brass_rgb, brass_sr, brass_sg),
        4: (steel_rgb, steel_sr, steel_sg),
    }

    rgb = np.zeros((2048, 2048, 3), dtype=np.float32)
    spec_r = np.zeros((2048, 2048), dtype=np.float32)
    spec_g = np.zeros((2048, 2048), dtype=np.float32)

    for zid, (l_rgb, l_sr, l_sg) in zone_layers.items():
        m = zone_map == zid
        if not np.any(m):
            continue
        gain = 0.72 if zid in (1, 2) else 0.58
        for c in range(3):
            rgb[m, c] = l_rgb[m, c] + hp[m] * gain
        spec_r[m] = l_sr[m] + hp[m] * 0.25
        spec_g[m] = l_sg[m] + hp[m] * 0.22

    diff_u8 = np.clip(rgb, 8, 232).astype(np.uint8)
    diff_img = Image.fromarray(diff_u8, mode="RGB")
    if preview_png_path:
        os.makedirs(os.path.dirname(preview_png_path), exist_ok=True)
        diff_img.save(preview_png_path)

    sr_1k = np.asarray(
        Image.fromarray(np.clip(spec_r, 16, 185).astype(np.uint8), mode="L").resize((1024, 1024), Image.Resampling.LANCZOS),
        dtype=np.float32,
    )
    sg_1k = np.asarray(
        Image.fromarray(np.clip(spec_g, 16, 175).astype(np.uint8), mode="L").resize((1024, 1024), Image.Resampling.LANCZOS),
        dtype=np.float32,
    )
    return diff_img, sr_1k, sg_1k


def _build_diver_helmet_textures(preview_png_path: str) -> tuple[Image.Image, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Genera texturas PBR 2K dedicadas para la Escafandra Circular del Capitán Cosmos
    (CosmosPA_DiverDome:0), con mapeo cilíndrico/esférico limpio:
      - U in [0..1]: ángulo azimutal alrededor de la cabeza (6 meridianos remachados)
      - V_img in [0..1]: polo superior -> collarín inferior (franja carmesí desgastada en V=0.66..0.82)
    Devuelve (diff_2k, nx_1k, ny_1k, sr_1k, sg_1k).
    """
    yy, xx = np.mgrid[0:2048, 0:2048].astype(np.float32)
    u = xx / 2048.0
    v = yy / 2048.0

    # Costuras meridianas (6 paneles de acero remachado) + costura ecuatorial y cuello
    meridians = np.abs(((u * 6.0) % 1.0) - 0.5)
    seam_v = (meridians > 0.486).astype(np.float32)
    seam_h = ((np.abs(v - 0.34) < 0.006) | (np.abs(v - 0.65) < 0.008) | (np.abs(v - 0.83) < 0.008)).astype(np.float32)
    seams = np.clip(seam_v + seam_h, 0.0, 1.0)

    # Remaches alineados junto a los meridianos y borde inferior
    rivet_grid = np.sin(u * math.pi * 6.0 * 2.0) ** 2
    rivet_y = np.abs(((v * 16.0) % 1.0) - 0.5)
    rivets = ((meridians > 0.445) & (meridians < 0.472) & (rivet_y < 0.14) & (rivet_grid > 0.3)).astype(np.float32)

    edge_w = np.clip(rivets * 0.85 + (np.abs(v - 0.65) < 0.025).astype(np.float32) * 0.7 + (v > 0.88).astype(np.float32) * 0.65, 0.0, 1.0)
    cav_w = np.clip(seams * 0.90 + (v > 0.84).astype(np.float32) * 0.55, 0.0, 1.0)

    cob_rgb, cob_h, cob_sr, cob_sg = weather_painted_metal(
        (36.0, 60.0, 106.0), edge_w, cav_w, seed=511, chip_amount=0.40, grime_amount=0.44, rust_amount=0.25,
    )
    crim_rgb, crim_h, crim_sr, crim_sg = weather_painted_metal(
        (120.0, 28.0, 30.0), edge_w, cav_w, seed=523, chip_amount=0.38, grime_amount=0.42, rust_amount=0.22,
    )
    brass_rgb, brass_h, brass_sr, brass_sg = weather_antique_brass(2048, 2048, cavity_mask=cav_w, seed=547)

    # Zona banda carmesí y filetes de latón en torno a V=0.66..0.82 + cuello inferior V>0.84
    band_crim = ((v >= 0.675) & (v <= 0.805)).astype(np.float32)
    band_brass = (((v >= 0.650) & (v < 0.675)) | ((v > 0.805) & (v <= 0.835))).astype(np.float32)

    rgb = cob_rgb * (1.0 - band_crim[:, :, None]) + crim_rgb * band_crim[:, :, None]
    rgb = rgb * (1.0 - band_brass[:, :, None]) + brass_rgb * band_brass[:, :, None]
    rgb = rgb * (1.0 - rivets[:, :, None] * 0.6) + brass_rgb * (rivets[:, :, None] * 0.6)
    rgb = rgb * (1.0 - seams[:, :, None] * 0.65) + np.array([22.0, 24.0, 28.0], dtype=np.float32) * (seams[:, :, None] * 0.65)

    spec_r = cob_sr * (1.0 - band_crim) + crim_sr * band_crim
    spec_g = cob_sg * (1.0 - band_crim) + crim_sg * band_crim
    spec_r = spec_r * (1.0 - band_brass) + brass_sr * band_brass
    spec_g = spec_g * (1.0 - band_brass) + brass_sg * band_brass
    spec_r = spec_r * (1.0 - seams * 0.7) + 26.0 * (seams * 0.7)
    spec_g = spec_g * (1.0 - seams * 0.7) + 24.0 * (seams * 0.7)

    h_map = cob_h * (1.0 - band_crim) + crim_h * band_crim + rivets * 0.65 - seams * 0.90 + band_brass * 0.30
    diff_img = Image.fromarray(np.clip(rgb, 8, 230).astype(np.uint8), mode="RGB")
    if preview_png_path:
        diff_img.save(preview_png_path)

    h_1k = np.asarray(
        Image.fromarray(np.clip((h_map + 1.5) * 80.0, 0, 255).astype(np.uint8), mode="L").resize((1024, 1024), Image.Resampling.LANCZOS),
        dtype=np.float32,
    ) / 80.0 - 1.5
    nx_1k, ny_1k = height_to_bc5_normal(h_1k, strength=2.4)
    sr_1k = np.asarray(
        Image.fromarray(np.clip(spec_r, 16, 185).astype(np.uint8), mode="L").resize((1024, 1024), Image.Resampling.LANCZOS),
        dtype=np.float32,
    )
    sg_1k = np.asarray(
        Image.fromarray(np.clip(spec_g, 16, 175).astype(np.uint8), mode="L").resize((1024, 1024), Image.Resampling.LANCZOS),
        dtype=np.float32,
    )
    return diff_img, nx_1k, ny_1k, sr_1k, sg_1k


def _rasterize_shape_plates(zone_draw: ImageDraw.ImageDraw, shape, comp_classifier) -> None:
    comps, vert_to_comp = _connected_plate_components(shape)
    comp_zone = {}
    for cid, vlist in enumerate(comps):
        pts3d = [shape.verts[v] for v in vlist]
        comp_zone[cid] = comp_classifier(pts3d)
    for a, b, c in shape.tris:
        zid = comp_zone[vert_to_comp[a]]
        pts_uv = [((shape.uvs[i][0] % 1.0) * 2047.0, (shape.uvs[i][1] % 1.0) * 2047.0) for i in (a, b, c)]
        zone_draw.polygon(pts_uv, fill=int(zid))


def generate_all_pa_textures_and_materials() -> None:
    os.makedirs(TEX_OUT_DIR, exist_ok=True)
    os.makedirs(MAT_OUT_DIR, exist_ok=True)

    # 1. TORSO (CosmosPABody)
    nf_body = pynifly.NifFile(os.path.join(PA_TPL_DIR, "pa_t51_body.nif"))
    s_body = next(s for s in nf_body.shapes if "DECAL" not in s.name)
    zimg_body = Image.new("L", (2048, 2048), 0)
    zdrw_body = ImageDraw.Draw(zimg_body)

    def classify_body_plate(pts):
        zs = [p[2] for p in pts]
        n = len(pts)
        zmin, zmax = min(zs), max(zs)
        if zmax < 99.0:
            return 2  # Calzón/faldón blindado heroico carmesí
        if zmin > 136.5 or n <= 36:
            return 3  # Collarín superior y pernos de latón antiguo
        return 1      # Coraza pectoral y dorsal azul cobalto envejecido

    _rasterize_shape_plates(zdrw_body, s_body, classify_body_plate)
    zmap_body = _dilate_zone_map(zimg_body, radius_iters=10)
    body_diff, body_sr, body_sg = _paint_armor_sheet_from_zones(
        os.path.join(PA_TPL_DIR, "t51body01_d.dds"),
        zmap_body,
        os.path.join(PA_ASSETS_DIR, "preview_body_d.png"),
        seed=101,
    )
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "CosmosPABody_d.dds"), body_diff)
    shutil.copy2(os.path.join(PA_TPL_DIR, "t51body01_n.dds"), os.path.join(TEX_OUT_DIR, "CosmosPABody_n.dds"))
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosPABody_s.dds"), body_sr, body_sg)

    # 2. CASCO ESCAFANDRA PROPIA (CosmosPAHelmet)
    helm_diff, helm_nx, helm_ny, helm_sr, helm_sg = _build_diver_helmet_textures(
        os.path.join(PA_ASSETS_DIR, "preview_helmet_d.png"),
    )
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "CosmosPAHelmet_d.dds"), helm_diff)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosPAHelmet_n.dds"), helm_nx, helm_ny)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosPAHelmet_s.dds"), helm_sr, helm_sg)

    # 3A. BRAZOS Y GUANTELETES 3ª + 1ª PERSONA (CosmosPAArm — SOLO forma :1, sin mezclar hombrera :2 ni herraje :0)
    nf_arm = pynifly.NifFile(os.path.join(PA_TPL_DIR, "pa_t51_larm.nif"))
    zimg_arm = Image.new("L", (2048, 2048), 0)
    zdrw_arm = ImageDraw.Draw(zimg_arm)
    for sh in nf_arm.shapes:
        if sh.name.endswith(":1"):
            def classify_arm_plate(pts):
                zs = [p[2] for p in pts]
                zmin = min(zs)
                if len(pts) <= 24 and zmin > 95.0:
                    return 3  # Codo / abrazaderas latón antiguo
                if zmin < 92.0:
                    return 3 if len(pts) <= 18 else 2  # Guanteletes espaciales carmesí envejecido
                return 1  # Bíceps azul cobalto envejecido
            _rasterize_shape_plates(zdrw_arm, sh, classify_arm_plate)

    zmap_arm = _dilate_zone_map(zimg_arm, radius_iters=10)
    arm_diff, arm_sr, arm_sg = _paint_armor_sheet_from_zones(
        os.path.join(PA_TPL_DIR, "t51arm01_d.dds"),
        zmap_arm,
        os.path.join(PA_ASSETS_DIR, "preview_arm_d.png"),
        seed=201,
    )
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "CosmosPAArm_d.dds"), arm_diff)
    shutil.copy2(os.path.join(PA_TPL_DIR, "t51arm01_n.dds"), os.path.join(TEX_OUT_DIR, "CosmosPAArm_n.dds"))
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosPAArm_s.dds"), arm_sr, arm_sg)

    # 3B. HOMBRERAS SEPARADAS (CosmosPAPauldron — SOLO forma :2 sobre el atlas t51arm01)
    zimg_paul = Image.new("L", (2048, 2048), 0)
    zdrw_paul = ImageDraw.Draw(zimg_paul)
    for sh in nf_arm.shapes:
        if sh.name.endswith(":2"):
            _rasterize_shape_plates(zdrw_paul, sh, lambda pts: 3 if len(pts) <= 37 else 1)

    zmap_paul = _dilate_zone_map(zimg_paul, radius_iters=10)
    paul_diff, paul_sr, paul_sg = _paint_armor_sheet_from_zones(
        os.path.join(PA_TPL_DIR, "t51arm01_d.dds"),
        zmap_paul,
        os.path.join(PA_ASSETS_DIR, "preview_pauldron_d.png"),
        seed=251,
    )
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "CosmosPAPauldron_d.dds"), paul_diff)
    shutil.copy2(os.path.join(PA_TPL_DIR, "t51arm01_n.dds"), os.path.join(TEX_OUT_DIR, "CosmosPAPauldron_n.dds"))
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosPAPauldron_s.dds"), paul_sr, paul_sg)

    # 4. PIERNAS Y BOTAS ESPACIALES (CosmosPALeg)
    nf_leg = pynifly.NifFile(os.path.join(PA_TPL_DIR, "pa_t51_lleg.nif"))
    zimg_leg = Image.new("L", (2048, 2048), 0)
    zdrw_leg = ImageDraw.Draw(zimg_leg)
    for sh in nf_leg.shapes:
        if sh.name.endswith(":2") or sh.name.endswith(":1"):
            def classify_leg_plate(pts):
                zs = [p[2] for p in pts]
                zmin = min(zs)
                if 31.0 <= zmin <= 50.0 and len(pts) <= 50:
                    return 3  # Rodillera y herrajes latón antiguo
                if zmin < 31.0:
                    return 2  # Botas y grebas carmesí envejecido
                return 1      # Musleras azul cobalto envejecido
            _rasterize_shape_plates(zdrw_leg, sh, classify_leg_plate)

    zmap_leg = _dilate_zone_map(zimg_leg, radius_iters=10)
    leg_diff, leg_sr, leg_sg = _paint_armor_sheet_from_zones(
        os.path.join(PA_TPL_DIR, "t51leg01_d.dds"),
        zmap_leg,
        os.path.join(PA_ASSETS_DIR, "preview_leg_d.png"),
        seed=301,
    )
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "CosmosPALeg_d.dds"), leg_diff)
    shutil.copy2(os.path.join(PA_TPL_DIR, "t51leg01_n.dds"), os.path.join(TEX_OUT_DIR, "CosmosPALeg_n.dds"))
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosPALeg_s.dds"), leg_sr, leg_sg)

    # 5. BRONCE / LATÓN ANTIGUO ENVEJECIDO FALLOUT (CosmosPAGold — adiós plástico amarillo canario)
    gold_rgb, gold_h, gold_sr2k, gold_sg2k = weather_antique_brass(2048, 2048, seed=77)
    gold_img = Image.fromarray(np.clip(gold_rgb, 12, 220).astype(np.uint8), mode="RGB")
    gold_img.save(os.path.join(PA_ASSETS_DIR, "preview_gold_d.png"))
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "CosmosPAGold_d.dds"), gold_img)
    gold_h_1k = np.asarray(
        Image.fromarray(np.clip((gold_h + 1.0) * 120.0, 0, 255).astype(np.uint8), mode="L").resize((1024, 1024), Image.Resampling.LANCZOS),
        dtype=np.float32,
    ) / 120.0 - 1.0
    gnx, gny = height_to_bc5_normal(gold_h_1k, strength=2.0)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosPAGold_n.dds"), gnx, gny)
    gsr_1k = np.asarray(Image.fromarray(gold_sr2k.astype(np.uint8), mode="L").resize((1024, 1024), Image.Resampling.LANCZOS), dtype=np.float32)
    gsg_1k = np.asarray(Image.fromarray(gold_sg2k.astype(np.uint8), mode="L").resize((1024, 1024), Image.Resampling.LANCZOS), dtype=np.float32)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosPAGold_s.dds"), gsr_1k, gsg_1k)

    # 6. CÚPULA VISOR DE ESCAFANDRA ÁMBAR-BRONCE AHUMADO (CosmosPAVisor)
    yy, xx = np.mgrid[0:2048, 0:2048].astype(np.float32)
    grad_u = (xx / 2047.0) * 2.0 - 1.0
    grad_v = (yy / 2047.0) * 2.0 - 1.0
    rad_v = np.sqrt(grad_u ** 2 + grad_v ** 2)
    scratches_v, _ = directional_scratches_and_drips(2048, 2048, seed=619)
    fbm_v = tileable_fbm(2048, 2048, base_cells=8, octaves=3, seed=621)
    edge_dirt = np.clip((rad_v - 0.62) * 2.2, 0.0, 0.85)
    visor_rgb = np.zeros((2048, 2048, 3), dtype=np.float32)
    sheen = (1.0 - np.clip(rad_v * 0.65, 0.0, 1.0)) * 26.0
    visor_rgb[:, :, 0] = np.clip(124.0 + sheen + (fbm_v - 0.5) * 14.0 - edge_dirt * 64.0 + scratches_v * 18.0, 18, 195)
    visor_rgb[:, :, 1] = np.clip(84.0 + sheen * 0.85 + (fbm_v - 0.5) * 10.0 - edge_dirt * 46.0 + scratches_v * 14.0, 14, 160)
    visor_rgb[:, :, 2] = np.clip(32.0 + sheen * 0.45 + (fbm_v - 0.5) * 8.0 - edge_dirt * 14.0 + scratches_v * 10.0, 10, 100)
    visor_img = Image.fromarray(visor_rgb.astype(np.uint8), mode="RGB")
    visor_img.save(os.path.join(PA_ASSETS_DIR, "preview_visor_d.png"))
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "CosmosPAVisor_d.dds"), visor_img)
    flat_nx = np.full((1024, 1024), 128.0, dtype=np.float32)
    flat_ny = np.full((1024, 1024), 128.0, dtype=np.float32)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosPAVisor_n.dds"), flat_nx, flat_ny)
    vsr_1k = np.asarray(Image.fromarray(np.clip(204.0 - edge_dirt * 95.0 - scratches_v * 35.0, 45, 220).astype(np.uint8), mode="L").resize((1024, 1024)), dtype=np.float32)
    vsg_1k = np.asarray(Image.fromarray(np.clip(186.0 - edge_dirt * 90.0 - scratches_v * 30.0, 40, 205).astype(np.uint8), mode="L").resize((1024, 1024)), dtype=np.float32)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosPAVisor_s.dds"), vsr_1k, vsg_1k)

    # 7. PLASMA CÓSMICO CIAN AUTOILUMINADO (CosmosPAGlow)
    rx = (xx - 1024.0) / 1024.0
    ry = (yy - 1024.0) / 1024.0
    rr = np.sqrt(rx * rx + ry * ry)
    core = np.clip(1.0 - rr * 0.65, 0.25, 1.0)
    glow_rgb = np.zeros((2048, 2048, 3), dtype=np.float32)
    glow_rgb[:, :, 0] = np.clip(55.0 + 165.0 * (core ** 2), 0, 255)
    glow_rgb[:, :, 1] = np.clip(215.0 + 40.0 * core, 0, 255)
    glow_rgb[:, :, 2] = 255.0
    glow_img = Image.fromarray(glow_rgb.astype(np.uint8), mode="RGB")
    glow_img.save(os.path.join(PA_ASSETS_DIR, "preview_glow_d.png"))
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "CosmosPAGlow_d.dds"), glow_img)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosPAGlow_n.dds"), flat_nx, flat_ny)
    write_bc5_dds_from_rg_arrays(
        os.path.join(TEX_OUT_DIR, "CosmosPAGlow_s.dds"),
        np.full((1024, 1024), 160.0, dtype=np.float32),
        np.full((1024, 1024), 150.0, dtype=np.float32),
    )

    # 8. ARCHIVOS DE MATERIAL BGSM V2 CALIBRADOS A ESTÁNDAR FALLOUT 4 (sin brillo plástico)
    bgsm_specs = [
        (
            "CosmosPABody.BGSM",
            build_bgsm_v2_bytes(
                "AeroArmor/PowerArmor/CosmosPABody_d.dds",
                "AeroArmor/PowerArmor/CosmosPABody_n.dds",
                "AeroArmor/PowerArmor/CosmosPABody_s.dds",
                envmap_scale=0.58,
                specular_color=(0.86, 0.90, 0.96),
                specular_mult=0.92,
                smoothness=0.96,
            ),
        ),
        (
            "CosmosPAHelmet.BGSM",
            build_bgsm_v2_bytes(
                "AeroArmor/PowerArmor/CosmosPAHelmet_d.dds",
                "AeroArmor/PowerArmor/CosmosPAHelmet_n.dds",
                "AeroArmor/PowerArmor/CosmosPAHelmet_s.dds",
                envmap_scale=0.62,
                specular_color=(0.88, 0.92, 0.98),
                specular_mult=0.95,
                smoothness=0.98,
            ),
        ),
        (
            "CosmosPAArm.BGSM",
            build_bgsm_v2_bytes(
                "AeroArmor/PowerArmor/CosmosPAArm_d.dds",
                "AeroArmor/PowerArmor/CosmosPAArm_n.dds",
                "AeroArmor/PowerArmor/CosmosPAArm_s.dds",
                envmap_scale=0.58,
                specular_color=(0.88, 0.90, 0.96),
                specular_mult=0.92,
                smoothness=0.96,
            ),
        ),
        (
            "CosmosPAPauldron.BGSM",
            build_bgsm_v2_bytes(
                "AeroArmor/PowerArmor/CosmosPAPauldron_d.dds",
                "AeroArmor/PowerArmor/CosmosPAPauldron_n.dds",
                "AeroArmor/PowerArmor/CosmosPAPauldron_s.dds",
                envmap_scale=0.58,
                specular_color=(0.88, 0.90, 0.96),
                specular_mult=0.92,
                smoothness=0.96,
            ),
        ),
        (
            "CosmosPALeg.BGSM",
            build_bgsm_v2_bytes(
                "AeroArmor/PowerArmor/CosmosPALeg_d.dds",
                "AeroArmor/PowerArmor/CosmosPALeg_n.dds",
                "AeroArmor/PowerArmor/CosmosPALeg_s.dds",
                envmap_scale=0.58,
                specular_color=(0.88, 0.90, 0.96),
                specular_mult=0.92,
                smoothness=0.96,
            ),
        ),
        (
            "CosmosPAGold.BGSM",
            build_bgsm_v2_bytes(
                "AeroArmor/PowerArmor/CosmosPAGold_d.dds",
                "AeroArmor/PowerArmor/CosmosPAGold_n.dds",
                "AeroArmor/PowerArmor/CosmosPAGold_s.dds",
                envmap_scale=0.92,
                specular_color=(0.96, 0.80, 0.44),
                specular_mult=1.08,
                smoothness=1.06,
            ),
        ),
        (
            "CosmosPAVisor.BGSM",
            build_bgsm_v2_bytes(
                "AeroArmor/PowerArmor/CosmosPAVisor_d.dds",
                "AeroArmor/PowerArmor/CosmosPAVisor_n.dds",
                "AeroArmor/PowerArmor/CosmosPAVisor_s.dds",
                envmap_scale=1.18,
                specular_color=(0.98, 0.82, 0.42),
                specular_mult=1.28,
                smoothness=1.35,
                cast_shadows=False,  # Permite paso limpio del haz de linterna C-HeadMod
            ),
        ),
        (
            "CosmosPAGlow.BGSM",
            build_bgsm_v2_bytes(
                "AeroArmor/PowerArmor/CosmosPAGlow_d.dds",
                "AeroArmor/PowerArmor/CosmosPAGlow_n.dds",
                "AeroArmor/PowerArmor/CosmosPAGlow_s.dds",
                envmap_scale=0.40,
                specular_color=(0.55, 0.95, 1.00),
                specular_mult=1.00,
                smoothness=1.10,
                emit_enabled=True,
                emit_color=(0.20, 0.86, 0.96),
                emit_mult=2.25,
            ),
        ),
    ]

    for fname, raw_b in bgsm_specs:
        out_p = os.path.join(MAT_OUT_DIR, fname)
        with open(out_p, "wb") as wf:
            wf.write(raw_b)
        chk_m = BGSMaterial(out_p)
        assert chk_m.signature == b"BGSM" and chk_m.version == 2, f"BGSM inválido: {fname}"
        print(f"[BGSM OK] {fname} ({len(raw_b)} B, emit={chk_m.emitEnabled})")


# ==============================================================================
# 3. INYECTOR BINARIO DE BSCONNECTPOINTS (CPA + CPT EXACTOS DE SERVOARMADURA)
# ==============================================================================
def _parse_fo4_nif_blocks(raw: bytes):
    nl = raw.find(b"\n")
    assert nl > 0
    header_prefix = raw[: nl + 1]
    pos = nl + 1
    ver, endian, user_ver, num_blocks, user_ver2 = struct.unpack_from("<IBIII", raw, pos)
    assert user_ver == 12 and user_ver2 == 130
    pos += 17

    exp_start = pos
    for _ in range(4):
        pos += 1 + raw[pos]
    export_info_bytes = raw[exp_start:pos]

    num_types = struct.unpack_from("<H", raw, pos)[0]
    pos += 2
    btypes: list[str] = []
    for _ in range(num_types):
        tlen = struct.unpack_from("<I", raw, pos)[0]
        pos += 4
        btypes.append(raw[pos : pos + tlen].decode("latin1"))
        pos += tlen

    type_idxs = list(struct.unpack_from(f"<{num_blocks}H", raw, pos))
    pos += 2 * num_blocks
    bsizes = list(struct.unpack_from(f"<{num_blocks}I", raw, pos))
    pos += 4 * num_blocks

    num_strings, max_str_len = struct.unpack_from("<II", raw, pos)
    pos += 8
    strs: list[str] = []
    for _ in range(num_strings):
        slen = struct.unpack_from("<I", raw, pos)[0]
        pos += 4
        strs.append(raw[pos : pos + slen].decode("latin1"))
        pos += slen

    num_groups = struct.unpack_from("<I", raw, pos)[0]
    groups_bytes = raw[pos : pos + 4 + 4 * num_groups]
    pos += 4 + 4 * num_groups

    blocks: list[bytearray] = []
    for i in range(num_blocks):
        blocks.append(bytearray(raw[pos : pos + bsizes[i]]))
        pos += bsizes[i]
    footer_bytes = raw[pos:]
    return header_prefix, ver, endian, user_ver, user_ver2, export_info_bytes, btypes, type_idxs, bsizes, strs, max_str_len, groups_bytes, blocks, footer_bytes


def ensure_pa_connect_points_from_template(dst_nif_path: str, tpl_nif_path: str) -> None:
    """
    Copia íntegros los bloques BSConnectPoint::Parents ("CPA") y BSConnectPoint::Children ("CPT",
    incluyendo entradas múltiples como C-BodyMod + C-BatteryMod en Torso o C-HeadMod en Casco)
    desde la plantilla oficial T-51 hacia el .NIF exportado por PyNifly.
    """
    with open(tpl_nif_path, "rb") as rf:
        tpl_raw = rf.read()
    with open(dst_nif_path, "rb") as rf:
        dst_raw = rf.read()

    _, _, _, _, _, _, t_btypes, t_tidxs, _, t_strs, _, _, t_blocks, _ = _parse_fo4_nif_blocks(tpl_raw)
    (
        header_prefix,
        ver,
        endian,
        user_ver,
        user_ver2,
        export_info_bytes,
        btypes,
        type_idxs,
        bsizes,
        strs,
        max_str_len,
        groups_bytes,
        blocks,
        footer_bytes,
    ) = _parse_fo4_nif_blocks(dst_raw)

    cp_types = ("BSConnectPoint::Parents", "BSConnectPoint::Children")
    tpl_cp_blocks = []
    for bi, ti in enumerate(t_tidxs):
        bt = t_btypes[ti]
        if bt in cp_types:
            raw_blk = bytearray(t_blocks[bi])
            old_name_idx = struct.unpack_from("<I", raw_blk, 0)[0]
            cp_name = t_strs[old_name_idx]
            tpl_cp_blocks.append((bt, cp_name, raw_blk))

    if not tpl_cp_blocks:
        return

    # Evitar duplicados si hubiera algún bloque previo en extra_data_list de Block[0]
    b0 = blocks[0]
    n_ex = struct.unpack_from("<I", b0, 4)[0]
    ex_refs = list(struct.unpack_from(f"<{n_ex}i", b0, 8))
    kept_ex_refs = [r for r in ex_refs if r >= 0 and btypes[type_idxs[r]] not in cp_types]

    added_indices = []
    for bt, cp_name, raw_blk in tpl_cp_blocks:
        if bt not in btypes:
            btypes.append(bt)
        t_idx = btypes.index(bt)
        if cp_name not in strs:
            strs.append(cp_name)
            max_str_len = max(max_str_len, len(cp_name))
        s_idx = strs.index(cp_name)
        blk_copy = bytearray(raw_blk)
        struct.pack_into("<I", blk_copy, 0, s_idx)
        new_bi = len(blocks)
        blocks.append(blk_copy)
        bsizes.append(len(blk_copy))
        type_idxs.append(t_idx)
        added_indices.append(new_bi)

    final_ex_refs = added_indices + kept_ex_refs
    old_ctrl, old_flags = struct.unpack_from("<iI", b0, 8 + 4 * n_ex)
    new_flags = old_flags | 0x0000000E
    new_b0 = bytearray()
    new_b0.extend(b0[:4])
    new_b0.extend(struct.pack("<I", len(final_ex_refs)))
    for r in final_ex_refs:
        new_b0.extend(struct.pack("<i", r))
    new_b0.extend(struct.pack("<iI", old_ctrl, new_flags))
    new_b0.extend(b0[16 + 4 * n_ex :])
    blocks[0] = new_b0
    bsizes[0] = len(new_b0)

    out = bytearray()
    out.extend(header_prefix)
    out.extend(struct.pack("<IBIII", ver, endian, user_ver, len(blocks), user_ver2))
    out.extend(export_info_bytes)
    out.extend(struct.pack("<H", len(btypes)))
    for bt in btypes:
        bb = bt.encode("latin1")
        out.extend(struct.pack("<I", len(bb)) + bb)
    out.extend(struct.pack(f"<{len(blocks)}H", *type_idxs))
    out.extend(struct.pack(f"<{len(blocks)}I", *bsizes))
    out.extend(struct.pack("<II", len(strs), max_str_len))
    for s in strs:
        sb = s.encode("latin1")
        out.extend(struct.pack("<I", len(sb)) + sb)
    out.extend(groups_bytes)
    for bdata in blocks:
        out.extend(bdata)
    out.extend(footer_bytes)

    with open(dst_nif_path, "wb") as wf:
        wf.write(out)

    chk = pynifly.NifFile(dst_nif_path)
    print(
        f"[BSConnectPoints Verified] {os.path.basename(dst_nif_path)} "
        f"({os.path.getsize(dst_nif_path):,} B, CP={[c[0].split('::')[-1] for c in tpl_cp_blocks]}, shapes={[s.name for s in chk.shapes]})"
    )


# ==============================================================================
# 4. SCRIPT BLENDER 5.2 + PYNIFLY: ESCULPIDO 3D DE LAS 6 PIEZAS + QA RENDER
# ==============================================================================
BLENDER_PA_SCRIPT = r'''
import math
import os
import sys
from collections import defaultdict
import bpy
import bmesh
from mathutils import Vector
from mathutils.kdtree import KDTree

PA_TPL_DIR = r"__PA_TPL_DIR__"
OUT_DIR = r"__OUT_DIR__"
RENDER_PREVIEW_PATH = r"__RENDER_PREVIEW__"
PYNIFLY_DIR = r"__PYNIFLY_DIR__"

if PYNIFLY_DIR not in sys.path:
    sys.path.insert(0, PYNIFLY_DIR)
from pyn import pynifly


def clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m)
    for arm in list(bpy.data.armatures):
        bpy.data.armatures.remove(arm)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)


def make_fo4_material(
    name: str,
    bgsm_rel: str,
    diff_dds: str,
    norm_dds: str,
    spec_dds: str,
    env_dds: str = r"textures\Shared\Cubemaps\mipblur_DefaultOutside1.dds",
):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat["BS_Shader_Block_Name"] = "BSLightingShaderProperty"
    mat["BSLSP_Shader_Name"] = bgsm_rel
    mat["BSShaderTextureSet_Diffuse"] = diff_dds
    mat["BSShaderTextureSet_Normal"] = norm_dds
    mat["BSShaderTextureSet_Specular"] = spec_dds
    mat["BSShaderTextureSet_EnvMap"] = env_dds
    if hasattr(mat, "pyn_shader"):
        mat.pyn_shader.Shader_Type = ""
    if mat.node_tree:
        for n in mat.node_tree.nodes:
            if n.bl_idname == "ShaderNodeTexImage":
                n.image = None
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf and "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = 1.0
    return mat


def set_obj_single_material(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    for p in obj.data.polygons:
        p.material_index = 0


def build_pa_surface_sampler(ref_obj):
    me = ref_obj.data
    verts_w = [ref_obj.matrix_world @ v.co for v in me.vertices]
    kd = KDTree(len(verts_w))
    for i, co in enumerate(verts_w):
        kd.insert(co, i)
    kd.balance()

    bone_vgs = {vg.index: vg.name for vg in ref_obj.vertex_groups if "Seg" not in vg.name}
    seg_vgs = {vg.index: vg.name for vg in ref_obj.vertex_groups if "Seg" in vg.name}
    all_seg_names = [vg.name for vg in ref_obj.vertex_groups if "Seg" in vg.name]

    vert_bones = []
    vert_seg = []
    for v in me.vertices:
        bd = {}
        best_seg = all_seg_names[0] if all_seg_names else None
        best_sw = -1.0
        for g in v.groups:
            if g.group in bone_vgs and g.weight > 0.001:
                bd[bone_vgs[g.group]] = g.weight
            elif g.group in seg_vgs and g.weight > best_sw:
                best_sw = g.weight
                best_seg = seg_vgs[g.group]
        vert_bones.append(bd)
        vert_seg.append(best_seg)

    def front_y(x: float, z: float, min_y: float = 0.0) -> float:
        best_num = 0.0
        best_den = 0.0
        for co, idx, _ in kd.find_n(Vector((x, 14.0, z)), 28):
            if co.y < min_y:
                continue
            d2 = (co.x - x) ** 2 + (co.z - z) ** 2 + 0.35
            w = 1.0 / (d2 * d2)
            best_num += co.y * w
            best_den += w
        return (best_num / best_den) if best_den > 0.0 else 14.0

    def sample_weights_and_seg(pt_w: Vector, k: int = 6):
        acc = defaultdict(float)
        seg_votes = defaultdict(float)
        for co, idx, dist in kd.find_n(pt_w, k):
            w = 1.0 / (max(dist, 0.15) ** 2)
            for bnm, bw in vert_bones[idx].items():
                acc[bnm] += bw * w
            if vert_seg[idx]:
                seg_votes[vert_seg[idx]] += w
        top4 = sorted(acc.items(), key=lambda kv: kv[1], reverse=True)[:4]
        tot = sum(v for _, v in top4)
        b_out = {bn: v / tot for bn, v in top4} if tot > 1e-6 else {"Chest": 1.0}
        chosen_seg = max(seg_votes.items(), key=lambda kv: kv[1])[0] if seg_votes else None
        return b_out, chosen_seg

    return front_y, sample_weights_and_seg, all_seg_names


def finalize_rigged_pa_mesh(
    name: str,
    bm: bmesh.types.BMesh,
    mat,
    arm_obj,
    root_obj,
    all_seg_names: list[str],
    weight_sampler,
    fixed_bone_weights: dict | None = None,
    fixed_seg_name: str | None = None,
    smooth_shade: bool = True,
):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name + "Mesh")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = smooth_shade
    me.materials.append(mat)

    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = root_obj if root_obj is not None else arm_obj
    if arm_obj is not None:
        mod = obj.modifiers.new(name="Armature", type="ARMATURE")
        mod.object = arm_obj

    vg_cache = {}
    def get_vg(vgn: str):
        if vgn not in vg_cache:
            vg_cache[vgn] = obj.vertex_groups.new(name=vgn)
        return vg_cache[vgn]

    for sname in all_seg_names:
        get_vg(sname)

    for vi, v in enumerate(me.vertices):
        if fixed_bone_weights is not None:
            bdict = fixed_bone_weights
            seg_nm = fixed_seg_name or (all_seg_names[0] if all_seg_names else None)
        else:
            bdict, seg_nm = weight_sampler(v.co)
        top4 = sorted(bdict.items(), key=lambda kv: kv[1], reverse=True)[:4]
        tot = sum(val for _, val in top4)
        for bnm, bw in top4:
            get_vg(bnm).add([vi], float(bw / max(tot, 1e-6)), "REPLACE")
        if seg_nm and seg_nm in vg_cache:
            vg_cache[seg_nm].add([vi], 1.0, "REPLACE")

    return obj


def _assign_tri_planar_uv(face, uv_lay, scale: float = 0.045):
    n = face.normal
    ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
    pts = []
    for lp in face.loops:
        co = lp.vert.co
        if ax >= ay and ax >= az:
            pts.append((co.y * scale, co.z * scale))
        elif az >= ax and az >= ay:
            pts.append((co.x * scale, co.y * scale))
        else:
            pts.append((co.x * scale, co.z * scale))
    u_off = math.floor(sum(p[0] for p in pts) / max(1, len(pts)))
    v_off = math.floor(sum(p[1] for p in pts) / max(1, len(pts)))
    for lp, (u_v, v_v) in zip(face.loops, pts):
        lp[uv_lay].uv = (u_v - u_off, v_v - v_off)


def add_box_or_prism(bm, uv_lay, ring_a: list[Vector], ring_b: list[Vector], cap_a: bool = True, cap_b: bool = True):
    n = len(ring_a)
    va = [bm.verts.new(p) for p in ring_a]
    vb = [bm.verts.new(p) for p in ring_b]
    for i in range(n):
        j = (i + 1) % n
        f = bm.faces.new((va[i], va[j], vb[j], vb[i]))
        f.normal_update()
        _assign_tri_planar_uv(f, uv_lay)
    if cap_a and n >= 3:
        ca = sum(ring_a, Vector((0.0, 0.0, 0.0))) / n
        vc = bm.verts.new(ca)
        for i in range(n):
            j = (i + 1) % n
            f = bm.faces.new((vc, va[j], va[i]))
            f.normal_update()
            _assign_tri_planar_uv(f, uv_lay)
    if cap_b and n >= 3:
        cb = sum(ring_b, Vector((0.0, 0.0, 0.0))) / n
        vc = bm.verts.new(cb)
        for i in range(n):
            j = (i + 1) % n
            f = bm.faces.new((vc, vb[i], vb[j]))
            f.normal_update()
            _assign_tri_planar_uv(f, uv_lay)


def add_lathe_tube(bm, uv_lay, center_axis_pts: list[tuple[Vector, float]], n_seg: int = 16, cap_start: bool = True, cap_end: bool = True):
    rings = []
    for c_pt, rad in center_axis_pts:
        ring = []
        for k in range(n_seg):
            ang = (2.0 * math.pi * k) / n_seg
            p = c_pt + Vector((rad * math.cos(ang), rad * math.sin(ang), 0.0))
            ring.append(bm.verts.new(p))
        rings.append((c_pt, ring))
    for r_i in range(len(rings) - 1):
        r0 = rings[r_i][1]
        r1 = rings[r_i + 1][1]
        for k in range(n_seg):
            kn = (k + 1) % n_seg
            f = bm.faces.new((r0[k], r0[kn], r1[kn], r1[k]))
            for lp in f.loops:
                lp[uv_lay].uv = (k / n_seg, r_i / max(1, len(rings) - 1))
    if cap_start:
        vc = bm.verts.new(rings[0][0])
        r0 = rings[0][1]
        for k in range(n_seg):
            kn = (k + 1) % n_seg
            f = bm.faces.new((vc, r0[kn], r0[k]))
            for lp in f.loops:
                lp[uv_lay].uv = (0.5, 0.5)
    if cap_end:
        vc = bm.verts.new(rings[-1][0])
        r1 = rings[-1][1]
        for k in range(n_seg):
            kn = (k + 1) % n_seg
            f = bm.faces.new((vc, r1[k], r1[kn]))
            for lp in f.loops:
                lp[uv_lay].uv = (0.5, 0.5)


def add_extruded_chest_poly(bm, uv_lay, poly_xz: list[tuple[float, float]], front_y, y_off: float, thick: float):
    cx = sum(p[0] for p in poly_xz) / len(poly_xz)
    cz = sum(p[1] for p in poly_xz) / len(poly_xz)
    ring_f = []
    ring_b = []
    for x, z in poly_xz:
        ys = front_y(x, z, min_y=4.0)
        ring_f.append(Vector((x, ys + y_off + thick, z)))
        ring_b.append(Vector((x, ys + y_off - 0.35, z)))
    add_box_or_prism(bm, uv_lay, ring_b, ring_f, cap_a=False, cap_b=True)


def get_common_materials():
    return {
        "body": make_fo4_material(
            "CosmosPABodyMat",
            r"Materials\AeroArmor\PowerArmor\CosmosPABody.BGSM",
            r"textures\AeroArmor\PowerArmor\CosmosPABody_d.dds",
            r"textures\AeroArmor\PowerArmor\CosmosPABody_n.dds",
            r"textures\AeroArmor\PowerArmor\CosmosPABody_s.dds",
        ),
        "helm": make_fo4_material(
            "CosmosPAHelmMat",
            r"Materials\AeroArmor\PowerArmor\CosmosPAHelmet.BGSM",
            r"textures\AeroArmor\PowerArmor\CosmosPAHelmet_d.dds",
            r"textures\AeroArmor\PowerArmor\CosmosPAHelmet_n.dds",
            r"textures\AeroArmor\PowerArmor\CosmosPAHelmet_s.dds",
        ),
        "arm": make_fo4_material(
            "CosmosPAArmMat",
            r"Materials\AeroArmor\PowerArmor\CosmosPAArm.BGSM",
            r"textures\AeroArmor\PowerArmor\CosmosPAArm_d.dds",
            r"textures\AeroArmor\PowerArmor\CosmosPAArm_n.dds",
            r"textures\AeroArmor\PowerArmor\CosmosPAArm_s.dds",
        ),
        "pauldron": make_fo4_material(
            "CosmosPAPauldronMat",
            r"Materials\AeroArmor\PowerArmor\CosmosPAPauldron.BGSM",
            r"textures\AeroArmor\PowerArmor\CosmosPAPauldron_d.dds",
            r"textures\AeroArmor\PowerArmor\CosmosPAPauldron_n.dds",
            r"textures\AeroArmor\PowerArmor\CosmosPAPauldron_s.dds",
        ),
        "leg": make_fo4_material(
            "CosmosPALegMat",
            r"Materials\AeroArmor\PowerArmor\CosmosPALeg.BGSM",
            r"textures\AeroArmor\PowerArmor\CosmosPALeg_d.dds",
            r"textures\AeroArmor\PowerArmor\CosmosPALeg_n.dds",
            r"textures\AeroArmor\PowerArmor\CosmosPALeg_s.dds",
        ),
        "gold": make_fo4_material(
            "CosmosPAGoldMat",
            r"Materials\AeroArmor\PowerArmor\CosmosPAGold.BGSM",
            r"textures\AeroArmor\PowerArmor\CosmosPAGold_d.dds",
            r"textures\AeroArmor\PowerArmor\CosmosPAGold_n.dds",
            r"textures\AeroArmor\PowerArmor\CosmosPAGold_s.dds",
        ),
        "visor": make_fo4_material(
            "CosmosPAVisorMat",
            r"Materials\AeroArmor\PowerArmor\CosmosPAVisor.BGSM",
            r"textures\AeroArmor\PowerArmor\CosmosPAVisor_d.dds",
            r"textures\AeroArmor\PowerArmor\CosmosPAVisor_n.dds",
            r"textures\AeroArmor\PowerArmor\CosmosPAVisor_s.dds",
        ),
        "glow": make_fo4_material(
            "CosmosPAGlowMat",
            r"Materials\AeroArmor\PowerArmor\CosmosPAGlow.BGSM",
            r"textures\AeroArmor\PowerArmor\CosmosPAGlow_d.dds",
            r"textures\AeroArmor\PowerArmor\CosmosPAGlow_n.dds",
            r"textures\AeroArmor\PowerArmor\CosmosPAGlow_s.dds",
        ),
    }


def export_cosmos_pa_body():
    clear_scene()
    mats = get_common_materials()
    bpy.ops.import_scene.pynifly(
        filepath=os.path.join(PA_TPL_DIR, "pa_t51_body.nif"),
        import_cutpoints=False,
        import_tris=False,
        import_collisions=False,
    )
    root_obj = next((o for o in bpy.data.objects if "pynRoot" in o), None)
    for d_obj in [o for o in list(bpy.data.objects) if o.type == "MESH" and "DECAL" in o.name]:
        bpy.data.objects.remove(d_obj, do_unlink=True)

    body_obj = [o for o in bpy.data.objects if o.type == "MESH"][0]
    arm_obj = next((m.object for m in body_obj.modifiers if m.type == "ARMATURE" and m.object), None)
    set_obj_single_material(body_obj, mats["body"])
    front_y, weight_sampler, all_seg_names = build_pa_surface_sampler(body_obj)

    # 1. Góndolas birreactor dorsales en Azul Cobalto Cósmico (X = ±8.6, dejando libre X=-4.5..+4.5 para el Núcleo de Fusión)
    bm_pods = bmesh.new()
    uv_pods = bm_pods.loops.layers.uv.new("UVMap")
    for sx in (-1.0, 1.0):
        px = sx * 8.6
        pod_profile = [
            (Vector((px, -25.2, 103.8)), 2.95),
            (Vector((px, -26.2, 107.0)), 3.65),
            (Vector((px, -26.8, 114.0)), 3.95),
            (Vector((px, -26.4, 122.5)), 3.80),
            (Vector((px, -25.2, 129.0)), 3.15),
            (Vector((px, -23.8, 132.2)), 2.10),
        ]
        add_lathe_tube(bm_pods, uv_pods, pod_profile, n_seg=18, cap_start=True, cap_end=True)
        # Soporte blindado de anclaje a la espalda de la coraza
        strut_back = [
            Vector((px - sx * 2.2, -16.5, 108.0)),
            Vector((px + sx * 1.2, -17.5, 108.0)),
            Vector((px + sx * 1.2, -16.5, 127.0)),
            Vector((px - sx * 2.2, -15.5, 127.0)),
        ]
        strut_out = [
            Vector((px - sx * 1.8, -25.8, 108.5)),
            Vector((px + sx * 1.5, -25.8, 108.5)),
            Vector((px + sx * 1.5, -25.0, 126.5)),
            Vector((px - sx * 1.8, -25.0, 126.5)),
        ]
        add_box_or_prism(bm_pods, uv_pods, strut_back, strut_out)

    thruster_pods_obj = finalize_rigged_pa_mesh(
        "CosmosPA_ThrusterPods:0",
        bm_pods,
        mats["body"],
        arm_obj,
        root_obj,
        all_seg_names,
        weight_sampler,
        fixed_bone_weights={"Chest": 0.85, "Tank_Armor": 0.15},
        fixed_seg_name="FO4 Seg 000",
    )

    # 2. Aletas Cósmicas Doradas, Toberas Venturi, Arco Superior, Escudo Pectoral Capitán Cosmos y Cinturón en V
    bm_gold = bmesh.new()
    uv_gold = bm_gold.loops.layers.uv.new("UVMap")

    for sx in (-1.0, 1.0):
        px = sx * 8.6
        # Cono superior dorado Art-Deco
        cone_prof = [
            (Vector((px, -23.8, 132.0)), 2.25),
            (Vector((px, -23.2, 134.8)), 1.35),
            (Vector((px, -22.8, 137.2)), 0.25),
        ]
        add_lathe_tube(bm_gold, uv_gold, cone_prof, n_seg=14, cap_start=False, cap_end=True)

        # Anillos de compresión dorados alrededor de cada reactor
        for z_ring, y_ring, r_ring in [(110.5, -26.5, 4.12), (118.5, -26.7, 4.18), (126.0, -25.7, 3.68)]:
            ring_prof = [
                (Vector((px, y_ring, z_ring - 0.75)), r_ring * 0.96),
                (Vector((px, y_ring, z_ring)), r_ring),
                (Vector((px, y_ring, z_ring + 0.75)), r_ring * 0.96),
            ]
            add_lathe_tube(bm_gold, uv_gold, ring_prof, n_seg=16, cap_start=True, cap_end=True)

        # Campana de tobera Venturi inferior dorada
        bell_prof = [
            (Vector((px, -25.2, 104.0)), 2.95),
            (Vector((px, -25.8, 101.8)), 2.45),
            (Vector((px, -26.6, 99.0)), 3.55),
            (Vector((px, -26.8, 98.2)), 3.30),
        ]
        add_lathe_tube(bm_gold, uv_gold, bell_prof, n_seg=18, cap_start=False, cap_end=True)

        # Gran Aleta Estabilizadora Cósmica Barrida (silueta icónica retro-espacial en vuelo)
        fin_in = [
            Vector((px + sx * 2.2, -26.0, 129.8)),
            Vector((px + sx * 2.4, -26.8, 106.8)),
            Vector((px + sx * 9.2, -33.6, 100.5)),
            Vector((px + sx * 9.8, -32.2, 118.5)),
        ]
        fin_out = [p + Vector((0.0, -0.85, 0.0)) if idx in (0, 1) else p + Vector((-sx * 0.65, 0.75, 0.0)) for idx, p in enumerate(fin_in)]
        add_box_or_prism(bm_gold, uv_gold, fin_in, fin_out)

    # Puente dorsal superior en arco sobre Z=125..131 (100% por encima del puerto C-BatteryMod Z=104..116)
    arch_f = [
        Vector((-6.5, -22.5, 125.2)),
        Vector((6.5, -22.5, 125.2)),
        Vector((5.2, -23.0, 130.4)),
        Vector((0.0, -23.8, 132.2)),
        Vector((-5.2, -23.0, 130.4)),
    ]
    arch_b = [p + Vector((0.0, -2.4, 0.0)) for p in arch_f]
    add_box_or_prism(bm_gold, uv_gold, arch_f, arch_b)

    # Escudo Pectoral Pentagonal Capitán Cosmos + Estrella de 5 Puntas + Anillo Atómico (Frontal)
    sh_outer = [(-6.2, 126.0), (6.2, 126.0), (7.6, 121.0), (0.0, 112.8), (-7.6, 121.0)]
    sh_inner = [(-4.9, 124.8), (4.9, 124.8), (6.0, 120.6), (0.0, 114.5), (-6.0, 120.6)]
    for i in range(5):
        j = (i + 1) % 5
        seg_poly = [sh_outer[i], sh_outer[j], sh_inner[j], sh_inner[i]]
        add_extruded_chest_poly(bm_gold, uv_gold, seg_poly, front_y, 0.12, 0.65)

    cz_star = 120.4
    for k in range(5):
        a0 = math.pi / 2.0 + k * (2.0 * math.pi / 5.0)
        am1 = a0 - math.pi / 5.0
        ap1 = a0 + math.pi / 5.0
        tri_ray = [
            (0.0, cz_star),
            (1.65 * math.cos(am1), cz_star + 1.65 * math.sin(am1)),
            (4.35 * math.cos(a0), cz_star + 4.35 * math.sin(a0)),
            (1.65 * math.cos(ap1), cz_star + 1.65 * math.sin(ap1)),
        ]
        add_extruded_chest_poly(bm_gold, uv_gold, tri_ray, front_y, 0.30, 0.75)

    # Anillo orbital atómico inclinado 28° sobre el emblema pectoral
    n_orb = 24
    ct, st = math.cos(math.radians(28.0)), math.sin(math.radians(28.0))
    for k in range(n_orb):
        kn = (k + 1) % n_orb
        t0, t1 = (2.0 * math.pi * k) / n_orb, (2.0 * math.pi * kn) / n_orb
        pts_seg = []
        for tt, rx, rz in [(t0, 5.4, 1.95), (t1, 5.4, 1.95), (t1, 4.55, 1.42), (t0, 4.55, 1.42)]:
            ox, oz = rx * math.cos(tt), rz * math.sin(tt)
            pts_seg.append((ox * ct - oz * st, cz_star + ox * st + oz * ct))
        add_extruded_chest_poly(bm_gold, uv_gold, pts_seg, front_y, 0.48, 0.42)

    # Cinturón Heroico Frontal en V con Hebilla Diamante (Z ≈ 92..99)
    belt_segs = [
        [(-13.5, 99.2), (-6.5, 97.2), (-6.5, 94.4), (-13.5, 96.4)],
        [(-6.5, 97.2), (0.0, 94.0), (0.0, 91.0), (-6.5, 94.4)],
        [(0.0, 94.0), (6.5, 97.2), (6.5, 94.4), (0.0, 91.0)],
        [(6.5, 97.2), (13.5, 99.2), (13.5, 96.4), (6.5, 94.4)],
    ]
    for bseg in belt_segs:
        add_extruded_chest_poly(bm_gold, uv_gold, bseg, front_y, 0.15, 0.70)
    buckle_poly = [(0.0, 97.6), (3.4, 94.2), (0.0, 90.4), (-3.4, 94.2)]
    add_extruded_chest_poly(bm_gold, uv_gold, buckle_poly, front_y, 0.55, 0.75)

    gold_body_obj = finalize_rigged_pa_mesh(
        "CosmosPA_BodyGold:0",
        bm_gold,
        mats["gold"],
        arm_obj,
        root_obj,
        all_seg_names,
        weight_sampler,
        smooth_shade=False,
    )

    # 3. Núcleos de Plasma Cian Autoiluminados (interior de ambas toberas + gema estelar pectoral + hebilla)
    bm_glow = bmesh.new()
    uv_glow = bm_glow.loops.layers.uv.new("UVMap")
    for sx in (-1.0, 1.0):
        px = sx * 8.6
        glow_prof = [
            (Vector((px, -26.7, 99.3)), 2.75),
            (Vector((px, -26.85, 98.35)), 2.55),
            (Vector((px, -26.9, 98.05)), 0.40),
        ]
        add_lathe_tube(bm_glow, uv_glow, glow_prof, n_seg=16, cap_start=True, cap_end=True)

    chest_core = [(1.15 * math.cos(2.0 * math.pi * k / 8.0), cz_star + 1.15 * math.sin(2.0 * math.pi * k / 8.0)) for k in range(8)]
    add_extruded_chest_poly(bm_glow, uv_glow, chest_core, front_y, 0.95, 0.45)
    buckle_core = [(0.0, 95.8), (1.7, 94.2), (0.0, 92.6), (-1.7, 94.2)]
    add_extruded_chest_poly(bm_glow, uv_glow, buckle_core, front_y, 1.05, 0.35)

    glow_body_obj = finalize_rigged_pa_mesh(
        "CosmosPA_BodyGlow:0",
        bm_glow,
        mats["glow"],
        arm_obj,
        root_obj,
        all_seg_names,
        weight_sampler,
        smooth_shade=True,
    )

    all_meshes = [body_obj, thruster_pods_obj, gold_body_obj, glow_body_obj]
    bpy.ops.object.select_all(action="DESELECT")
    if root_obj:
        root_obj.select_set(True)
    for m in all_meshes:
        m.select_set(True)
    bpy.context.view_layer.objects.active = body_obj
    out_p = os.path.join(OUT_DIR, "CosmosPA_Body.nif")
    bpy.ops.export_scene.pynifly(filepath=out_p, target_game="FO4")
    print(f"[Blender Exported] CosmosPA_Body.nif ({len(all_meshes)} shapes)")


def build_captain_cosmos_diver_helmet_bmeshes(offset_vec: Vector):
    """
    Esculpe la Escafandra Circular Presurizada del Capitán Cosmos (estilo buzo espacial retro):
      - Domo esférico parametrizado alrededor del eje frontal +Y para lograr una abertura circular perfecta (sin dientes).
      - Collarín circular bridado de latón envejecido con 12 pernos hexagonales sobre el cuello hermético.
      - Gran bisel ojo de buey remachado con barras protectoras de escafandra y cúpula ámbar abombada.
      - Cápsulas auriculares respiratorias + antenas atómicas laterales + foco superior de telemetría.
    """
    dome_c = Vector((0.0, -2.2, 147.6)) + offset_vec
    neck_c = Vector((0.0, -3.1, 136.8)) + offset_vec
    port_c = Vector((0.0, -2.2, 147.0)) + offset_vec
    R_DOME = 12.6
    ALPHA_PORT = math.radians(38.0)  # R_rim = 12.6 * sin(38°) = 7.76, Y_rim = -2.2 + 9.93 = +7.73

    # ------------------------------------------------------------------
    # 1. DOMO ESFÉRICO PRESURIZADO (bm_dome -> CosmosPAHelmet.BGSM)
    # ------------------------------------------------------------------
    bm_dome = bmesh.new()
    uv_d = bm_dome.loops.layers.uv.new("UVMap")
    n_mer = 36
    n_par = 18
    rings_out = []
    for p_i in range(n_par + 1):
        t = p_i / n_par
        alpha = ALPHA_PORT + t * (math.pi - ALPHA_PORT)
        ca, sa = math.cos(alpha), math.sin(alpha)
        ring = []
        for m_i in range(n_mer):
            theta = (2.0 * math.pi * m_i) / n_mer
            px = dome_c.x + R_DOME * sa * math.cos(theta)
            py = dome_c.y + R_DOME * ca
            pz = dome_c.z + R_DOME * sa * math.sin(theta)
            # Recorte limpio dentro del collarín inferior (Z_local >= 136.4)
            z_floor = 136.4 + offset_vec.z
            if pz < z_floor:
                pz = z_floor
            ring.append(bm_dome.verts.new(Vector((px, py, pz))))
        rings_out.append(ring)

    # Cierre del polo trasero (-Y en alpha=pi)
    v_back = bm_dome.verts.new(Vector((dome_c.x, dome_c.y - R_DOME, dome_c.z)))

    def assign_dome_uv(face):
        pts_az = []
        pts_v = []
        for lp in face.loops:
            rel = lp.vert.co - dome_c
            az = (math.atan2(rel.y, rel.x) + math.pi) / (2.0 * math.pi)
            vz = 1.0 - max(0.0, min(1.0, (rel.z + 11.4) / 24.0))
            pts_az.append(az)
            pts_v.append(vz)
        # Evitar salto de costura U=0..1 dentro de la misma cara
        if max(pts_az) - min(pts_az) > 0.5:
            pts_az = [a + 1.0 if a < 0.5 else a for a in pts_az]
        for lp, au, av in zip(face.loops, pts_az, pts_v):
            lp[uv_d].uv = (au, av)

    for p_i in range(n_par):
        r0 = rings_out[p_i]
        r1 = rings_out[p_i + 1]
        for m_i in range(n_mer):
            mn = (m_i + 1) % n_mer
            if p_i < n_par - 1:
                f = bm_dome.faces.new((r0[m_i], r0[mn], r1[mn], r1[m_i]))
            else:
                f = bm_dome.faces.new((r0[m_i], r0[mn], v_back))
            assign_dome_uv(f)

    # Labio interior corto tras el ojo de buey para dar espesor real al corte circular
    ring_rim = rings_out[0]
    ring_lip = []
    for m_i in range(n_mer):
        theta = (2.0 * math.pi * m_i) / n_mer
        px = dome_c.x + (R_DOME * math.sin(ALPHA_PORT) - 0.85) * math.cos(theta)
        py = dome_c.y + R_DOME * math.cos(ALPHA_PORT) - 1.15
        pz = dome_c.z + (R_DOME * math.sin(ALPHA_PORT) - 0.85) * math.sin(theta)
        ring_lip.append(bm_dome.verts.new(Vector((px, py, max(136.4 + offset_vec.z, pz)))))
    for m_i in range(n_mer):
        mn = (m_i + 1) % n_mer
        f = bm_dome.faces.new((ring_lip[m_i], ring_lip[mn], ring_rim[mn], ring_rim[m_i]))
        assign_dome_uv(f)

    # Costilla trasera de ventilación / regulador de presión en la nuca
    reg_a = [
        Vector((-2.6, dome_c.y - 10.5, dome_c.z - 8.8)),
        Vector(( 2.6, dome_c.y - 10.5, dome_c.z - 8.8)),
        Vector(( 2.1, dome_c.y - 12.9, dome_c.z - 2.0)),
        Vector((-2.1, dome_c.y - 12.9, dome_c.z - 2.0)),
    ]
    reg_b = [
        Vector((-2.6, dome_c.y - 9.0, dome_c.z - 8.8)),
        Vector(( 2.6, dome_c.y - 9.0, dome_c.z - 8.8)),
        Vector(( 2.1, dome_c.y - 10.5, dome_c.z + 4.8)),
        Vector((-2.1, dome_c.y - 10.5, dome_c.z + 4.8)),
    ]
    add_box_or_prism(bm_dome, uv_d, reg_a, reg_b)

    # ------------------------------------------------------------------
    # 2. CÚPULA VISOR ESFÉRICA «OJO DE BUEY» (bm_visor -> CosmosPAVisor.BGSM sin sombras)
    # ------------------------------------------------------------------
    bm_visor = bmesh.new()
    uv_v = bm_visor.loops.layers.uv.new("UVMap")
    n_vrad = 10
    r_port = R_DOME * math.sin(ALPHA_PORT) + 0.15
    y_port = dome_c.y + R_DOME * math.cos(ALPHA_PORT)
    visor_rings = []
    for vi in range(1, n_vrad + 1):
        frac = vi / n_vrad
        th_v = frac * math.radians(58.0)
        rr = r_port * (math.sin(th_v) / math.sin(math.radians(58.0)))
        bulge = 3.2 * (math.cos(th_v) - math.cos(math.radians(58.0))) / (1.0 - math.cos(math.radians(58.0)))
        ring = []
        for m_i in range(n_mer):
            ang = (2.0 * math.pi * m_i) / n_mer
            vx = port_c.x + rr * math.cos(ang)
            vy = y_port + bulge
            vz = port_c.z + rr * math.sin(ang)
            ring.append((bm_visor.verts.new(Vector((vx, vy, vz))), 0.5 + 0.45 * frac * math.cos(ang), 0.5 + 0.45 * frac * math.sin(ang)))
        visor_rings.append(ring)

    v_apex = bm_visor.verts.new(Vector((port_c.x, y_port + 3.2, port_c.z)))
    r0 = visor_rings[0]
    for m_i in range(n_mer):
        mn = (m_i + 1) % n_mer
        f = bm_visor.faces.new((v_apex, r0[mn][0], r0[m_i][0]))
        f.loops[0][uv_v].uv = (0.5, 0.5)
        f.loops[1][uv_v].uv = (r0[mn][1], r0[mn][2])
        f.loops[2][uv_v].uv = (r0[m_i][1], r0[m_i][2])
    for vi in range(len(visor_rings) - 1):
        ra = visor_rings[vi]
        rb = visor_rings[vi + 1]
        for m_i in range(n_mer):
            mn = (m_i + 1) % n_mer
            f = bm_visor.faces.new((ra[m_i][0], ra[mn][0], rb[mn][0], rb[m_i][0]))
            f.loops[0][uv_v].uv = (ra[m_i][1], ra[m_i][2])
            f.loops[1][uv_v].uv = (ra[mn][1], ra[mn][2])
            f.loops[2][uv_v].uv = (rb[mn][1], rb[mn][2])
            f.loops[3][uv_v].uv = (rb[m_i][1], rb[m_i][2])

    # ------------------------------------------------------------------
    # 3. HERRAJES DE ESCAFANDRA EN LATÓN ANTIGUO (bm_gold -> CosmosPAGold.BGSM)
    # ------------------------------------------------------------------
    bm_gold = bmesh.new()
    uv_g = bm_gold.loops.layers.uv.new("UVMap")

    # 3A. Gran Collarín Circular de Escafandra con Brida y 12 Pernos (Z = neck_c.z - 2.0 .. +1.8)
    n_c = 28
    c_bot_out = [Vector((neck_c.x + 11.9 * math.cos(2 * math.pi * k / n_c), neck_c.y + 11.9 * math.sin(2 * math.pi * k / n_c), neck_c.z - 1.9)) for k in range(n_c)]
    c_top_out = [Vector((neck_c.x + 11.2 * math.cos(2 * math.pi * k / n_c), neck_c.y + 11.2 * math.sin(2 * math.pi * k / n_c), neck_c.z + 1.8)) for k in range(n_c)]
    add_box_or_prism(bm_gold, uv_g, c_bot_out, c_top_out)
    for b_i in range(12):
        ang = (2.0 * math.pi * b_i) / 12.0
        bx = neck_c.x + 11.35 * math.cos(ang)
        by = neck_c.y + 11.35 * math.sin(ang)
        bolt_a = [Vector((bx + 0.65 * math.cos(2 * math.pi * s / 6), by + 0.65 * math.sin(2 * math.pi * s / 6), neck_c.z + 1.5)) for s in range(6)]
        bolt_b = [p + Vector((0.0, 0.0, 1.0)) for p in bolt_a]
        add_box_or_prism(bm_gold, uv_g, bolt_a, bolt_b)

    # 3B. Gran Bisel Circular Frontal «Ojo de Buey» (alrededor de port_c en Y_port) + 12 Remaches
    bz_pts = []
    for k in range(n_mer):
        ang = (2.0 * math.pi * k) / n_mer
        ca_b, sa_b = math.cos(ang), math.sin(ang)
        bz_pts.append((ca_b, sa_b))
    # Cuerpo anular grueso de escafandra (R_in=7.35, R_out=9.35, Y=y_port-1.1..y_port+0.95)
    for r_sub_in, r_sub_out, y0, y1 in [(7.35, 9.35, y_port - 1.0, y_port + 0.85)]:
        ring_bi = [Vector((port_c.x + r_sub_in * ca_b, y0, port_c.z + r_sub_in * sa_b)) for ca_b, sa_b in bz_pts]
        ring_bo = [Vector((port_c.x + r_sub_out * ca_b, y0, port_c.z + r_sub_out * sa_b)) for ca_b, sa_b in bz_pts]
        ring_fi = [Vector((port_c.x + r_sub_in * ca_b, y1, port_c.z + r_sub_in * sa_b)) for ca_b, sa_b in bz_pts]
        ring_fo = [Vector((port_c.x + r_sub_out * ca_b, y1, port_c.z + r_sub_out * sa_b)) for ca_b, sa_b in bz_pts]
        vbi = [bm_gold.verts.new(p) for p in ring_bi]
        vbo = [bm_gold.verts.new(p) for p in ring_bo]
        vfi = [bm_gold.verts.new(p) for p in ring_fi]
        vfo = [bm_gold.verts.new(p) for p in ring_fo]
        for k in range(n_mer):
            kn = (k + 1) % n_mer
            for quad in [
                (vbo[k], vfo[k], vfo[kn], vbo[kn]),
                (vfi[k], vbi[k], vbi[kn], vfi[kn]),
                (vfo[k], vfi[k], vfi[kn], vfo[kn]),
                (vbi[k], vbo[k], vbo[kn], vbi[kn]),
            ]:
                f = bm_gold.faces.new(quad)
                f.normal_update()
                _assign_tri_planar_uv(f, uv_g)

    for b_i in range(12):
        ang = (2.0 * math.pi * b_i) / 12.0 + (math.pi / 12.0)
        rx = port_c.x + 8.35 * math.cos(ang)
        rz = port_c.z + 8.35 * math.sin(ang)
        ra = [Vector((rx + 0.42 * math.cos(2 * math.pi * s / 6), y_port + 0.70, rz + 0.42 * math.sin(2 * math.pi * s / 6))) for s in range(6)]
        rb = [p + Vector((0.0, 0.55, 0.0)) for p in ra]
        add_box_or_prism(bm_gold, uv_g, ra, rb)

    # 3C. Rejilla protectora diagonal clásica de buzo (4 barras finas en X / ±45° dejando centro abierto)
    for bar_deg in (40.0, 140.0, 220.0, 320.0):
        ang = math.radians(bar_deg)
        ca_b, sa_b = math.cos(ang), math.sin(ang)
        # Barra corta curva entre R=7.6 (borde visor) y R=4.6 (sin invadir la línea de visión central)
        b_pts = []
        for s_k in range(5):
            u_s = s_k / 4.0
            rad_s = 7.65 - u_s * 2.55
            bul_s = 0.75 + 2.25 * math.sin(u_s * math.pi * 0.5)
            b_pts.append(Vector((port_c.x + rad_s * ca_b, y_port + bul_s, port_c.z + rad_s * sa_b)))
        for s_k in range(len(b_pts) - 1):
            p0, p1 = b_pts[s_k], b_pts[s_k + 1]
            tang = Vector((-sa_b, 0.0, ca_b)) * 0.24
            fy = Vector((0.0, 0.24, 0.0))
            add_box_or_prism(
                bm_gold, uv_g,
                [p0 - tang - fy, p0 + tang - fy, p0 + tang + fy, p0 - tang + fy],
                [p1 - tang - fy, p1 + tang - fy, p1 + tang + fy, p1 - tang + fy],
            )
    # Aro protector interior concéntrico delgado (R=5.15, muy fino para estética clásica sin tapar la vista)
    n_ir = 28
    r_in_g, r_out_g = 4.95, 5.25
    y_ig = y_port + 2.65
    v_iga = [bm_gold.verts.new(Vector((port_c.x + r_in_g * math.cos(2 * math.pi * k / n_ir), y_ig, port_c.z + r_in_g * math.sin(2 * math.pi * k / n_ir)))) for k in range(n_ir)]
    v_igb = [bm_gold.verts.new(Vector((port_c.x + r_out_g * math.cos(2 * math.pi * k / n_ir), y_ig, port_c.z + r_out_g * math.sin(2 * math.pi * k / n_ir)))) for k in range(n_ir)]
    v_igc = [bm_gold.verts.new(Vector((port_c.x + r_out_g * math.cos(2 * math.pi * k / n_ir), y_ig + 0.38, port_c.z + r_out_g * math.sin(2 * math.pi * k / n_ir)))) for k in range(n_ir)]
    v_igd = [bm_gold.verts.new(Vector((port_c.x + r_in_g * math.cos(2 * math.pi * k / n_ir), y_ig + 0.38, port_c.z + r_in_g * math.sin(2 * math.pi * k / n_ir)))) for k in range(n_ir)]
    for k in range(n_ir):
        kn = (k + 1) % n_ir
        for quad in [
            (v_igb[k], v_igc[k], v_igc[kn], v_igb[kn]),
            (v_igd[k], v_iga[k], v_iga[kn], v_igd[kn]),
            (v_igc[k], v_igd[k], v_igd[kn], v_igc[kn]),
            (v_iga[k], v_igb[k], v_igb[kn], v_iga[kn]),
        ]:
            f = bm_gold.faces.new(quad)
            f.normal_update()
            _assign_tri_planar_uv(f, uv_g)

    # 3D. Válvulas Auriculares Circulares + Antenas Atómicas Gemelas del Capitán Cosmos
    for sx in (-1.0, 1.0):
        pod_c = Vector((dome_c.x + sx * 12.1, dome_c.y - 0.2, dome_c.z - 0.4))
        n_s = 16
        r_in = [Vector((pod_c.x - sx * 0.9, pod_c.y + 3.4 * math.cos(2 * math.pi * k / n_s), pod_c.z + 3.4 * math.sin(2 * math.pi * k / n_s))) for k in range(n_s)]
        r_mid = [Vector((pod_c.x + sx * 1.1, pod_c.y + 2.9 * math.cos(2 * math.pi * k / n_s), pod_c.z + 2.9 * math.sin(2 * math.pi * k / n_s))) for k in range(n_s)]
        r_cap = [Vector((pod_c.x + sx * 1.9, pod_c.y + 1.9 * math.cos(2 * math.pi * k / n_s), pod_c.z + 1.9 * math.sin(2 * math.pi * k / n_s))) for k in range(n_s)]
        add_box_or_prism(bm_gold, uv_g, r_in, r_mid)
        add_box_or_prism(bm_gold, uv_g, r_mid, r_cap)
        # Antena atómica inclinada hacia atrás
        ant_b = [
            Vector((pod_c.x + sx * 0.7, pod_c.y - 0.45, pod_c.z + 2.1)),
            Vector((pod_c.x + sx * 1.25, pod_c.y - 0.45, pod_c.z + 2.1)),
            Vector((pod_c.x + sx * 1.25, pod_c.y + 0.45, pod_c.z + 2.1)),
            Vector((pod_c.x + sx * 0.7, pod_c.y + 0.45, pod_c.z + 2.1)),
        ]
        ant_t = [Vector((p.x + sx * 0.4, p.y - 2.9, p.z + 9.2)) for p in ant_b]
        add_box_or_prism(bm_gold, uv_g, ant_b, ant_t)
        # Esfera/cápsula en la punta de cada antena
        tip_c = Vector((pod_c.x + sx * 1.38, pod_c.y - 2.9, pod_c.z + 11.4))
        tip_a = [tip_c + Vector((0.75 * math.cos(2 * math.pi * k / 10), 0.75 * math.sin(2 * math.pi * k / 10), -0.6)) for k in range(10)]
        tip_b = [tip_c + Vector((0.75 * math.cos(2 * math.pi * k / 10), 0.75 * math.sin(2 * math.pi * k / 10), +0.6)) for k in range(10)]
        add_box_or_prism(bm_gold, uv_g, tip_a, tip_b)

    # 3E. Foco Auxiliar Superior de Escafandra (frente arriba en Z=dome_c.z+9.6, Y=y_port-1.8) + Lente Glow
    lamp_c = Vector((dome_c.x, y_port - 1.8, dome_c.z + 9.8))
    l_a = [Vector((lamp_c.x + 1.85 * math.cos(2 * math.pi * k / 16), lamp_c.y - 1.5, lamp_c.z + 1.85 * math.sin(2 * math.pi * k / 16))) for k in range(16)]
    l_b = [Vector((lamp_c.x + 1.65 * math.cos(2 * math.pi * k / 16), lamp_c.y + 1.2, lamp_c.z + 1.65 * math.sin(2 * math.pi * k / 16))) for k in range(16)]
    add_box_or_prism(bm_gold, uv_g, l_a, l_b)

    bm_glow = bmesh.new()
    uv_gl = bm_glow.loops.layers.uv.new("UVMap")
    gl_a = [Vector((lamp_c.x + 1.32 * math.cos(2 * math.pi * k / 16), lamp_c.y + 0.9, lamp_c.z + 1.32 * math.sin(2 * math.pi * k / 16))) for k in range(16)]
    gl_b = [Vector((lamp_c.x + 1.15 * math.cos(2 * math.pi * k / 16), lamp_c.y + 1.4, lamp_c.z + 1.15 * math.sin(2 * math.pi * k / 16))) for k in range(16)]
    add_box_or_prism(bm_glow, uv_gl, gl_a, gl_b)

    return bm_dome, bm_gold, bm_visor, bm_glow


def export_cosmos_pa_helmet():
    clear_scene()
    mats = get_common_materials()
    bpy.ops.import_scene.pynifly(
        filepath=os.path.join(PA_TPL_DIR, "pa_t51_helmet.nif"),
        import_cutpoints=False,
        import_tris=False,
        import_collisions=False,
    )
    root_obj = next((o for o in bpy.data.objects if "pynRoot" in o), None)
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    helm_obj = next(o for o in meshes if "Helmet:3" in o.name or "Neck" not in o.name)
    neck_objs = [o for o in meshes if o != helm_obj]
    arm_obj = next((m.object for m in helm_obj.modifiers if m.type == "ARMATURE" and m.object), None)

    for nk in neck_objs:
        set_obj_single_material(nk, mats["leg"])

    _, weight_sampler, all_seg_names = build_pa_surface_sampler(helm_obj)
    # Reemplazar el casco angular T-51 por nuestra Escafandra Circular del Capitán Cosmos
    bpy.data.objects.remove(helm_obj, do_unlink=True)

    bm_dome, bm_gold, bm_visor, bm_glow = build_captain_cosmos_diver_helmet_bmeshes(Vector((0.0, 0.0, 0.0)))

    dome_obj = finalize_rigged_pa_mesh(
        "CosmosPA_DiverDome:0",
        bm_dome,
        mats["helm"],
        arm_obj,
        root_obj,
        all_seg_names,
        weight_sampler,
        fixed_bone_weights={"Helmet_Armor": 1.0},
        fixed_seg_name="FO4 Seg 001",
        smooth_shade=True,
    )
    gold_obj = finalize_rigged_pa_mesh(
        "CosmosPA_HelmGold:0",
        bm_gold,
        mats["gold"],
        arm_obj,
        root_obj,
        all_seg_names,
        weight_sampler,
        fixed_bone_weights={"Helmet_Armor": 1.0},
        fixed_seg_name="FO4 Seg 001",
        smooth_shade=False,
    )
    visor_obj = finalize_rigged_pa_mesh(
        "CosmosPA_Visor:0",
        bm_visor,
        mats["visor"],
        arm_obj,
        root_obj,
        all_seg_names,
        weight_sampler,
        fixed_bone_weights={"Helmet_Armor": 1.0},
        fixed_seg_name="FO4 Seg 001",
        smooth_shade=True,
    )
    glow_obj = finalize_rigged_pa_mesh(
        "CosmosPA_HelmGlow:0",
        bm_glow,
        mats["glow"],
        arm_obj,
        root_obj,
        all_seg_names,
        weight_sampler,
        fixed_bone_weights={"Helmet_Armor": 1.0},
        fixed_seg_name="FO4 Seg 001",
        smooth_shade=True,
    )

    all_meshes = neck_objs + [dome_obj, gold_obj, visor_obj, glow_obj]
    bpy.ops.object.select_all(action="DESELECT")
    if root_obj:
        root_obj.select_set(True)
    for m in all_meshes:
        m.select_set(True)
    bpy.context.view_layer.objects.active = dome_obj
    out_p = os.path.join(OUT_DIR, "CosmosPA_Helmet.nif")
    bpy.ops.export_scene.pynifly(filepath=out_p, target_game="FO4")
    print(f"[Blender Exported] CosmosPA_Helmet.nif ({len(all_meshes)} shapes)")


def export_cosmos_pa_arm(is_right: bool, is_1st: bool):
    clear_scene()
    mats = get_common_materials()
    side_tok = "rarm" if is_right else "larm"
    SideTok = "RArm" if is_right else "LArm"
    sx = 1.0 if is_right else -1.0
    src_name = f"pa_t51_{side_tok}{'_1st' if is_1st else ''}.nif"
    dst_name = f"CosmosPA_{SideTok}{'_1st' if is_1st else ''}.nif"

    bpy.ops.import_scene.pynifly(
        filepath=os.path.join(PA_TPL_DIR, src_name),
        import_cutpoints=False,
        import_tris=False,
        import_collisions=False,
    )
    root_obj = next((o for o in bpy.data.objects if "pynRoot" in o), None)
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    forearm_obj = next(o for o in meshes if o.name.endswith(":1"))
    arm_obj = next((m.object for m in forearm_obj.modifiers if m.type == "ARMATURE" and m.object), None)

    for m in meshes:
        if m.name.endswith(":0"):
            set_obj_single_material(m, mats["gold"])
        elif m.name.endswith(":2"):
            set_obj_single_material(m, mats["pauldron"])
        else:
            set_obj_single_material(m, mats["arm"])

    _, weight_sampler_fa, all_seg_names = build_pa_surface_sampler(forearm_obj)

    extra_objs = []
    if not is_1st:
        # Aleta dorsal en latón antiguo únicamente en 3ª persona (despejada en 1ª persona para no flotar ni tapar la mira)
        wverts = [forearm_obj.matrix_world @ v.co for v in forearm_obj.data.vertices]
        zmin_fa = min(v.z for v in wverts)
        zmax_fa = max(v.z for v in wverts)
        z_mid = zmin_fa + 0.36 * (zmax_fa - zmin_fa)
        sub_vs = [v for v in wverts if abs(v.z - z_mid) < 4.5]
        cx_fa = sum(v.x for v in sub_vs) / max(1, len(sub_vs))
        cy_fa = sum(v.y for v in sub_vs) / max(1, len(sub_vs))
        rx_out = max(abs(v.x - cx_fa) for v in sub_vs) if sub_vs else 5.2

        bm_g = bmesh.new()
        uv_g = bm_g.loops.layers.uv.new("UVMap")
        fin_base = [
            Vector((cx_fa + sx * (rx_out - 0.6), cy_fa - 0.7, zmin_fa + 6.0)),
            Vector((cx_fa + sx * (rx_out - 0.4), cy_fa - 0.7, zmin_fa + 19.5)),
            Vector((cx_fa + sx * (rx_out + 2.6), cy_fa - 1.6, zmin_fa + 22.5)),
            Vector((cx_fa + sx * (rx_out + 1.8), cy_fa - 1.2, zmin_fa + 8.5)),
        ]
        fin_side = [p + Vector((0.0, 1.3, 0.0)) for p in fin_base]
        add_box_or_prism(bm_g, uv_g, fin_base, fin_side)
        extra_objs.append(
            finalize_rigged_pa_mesh(
                f"CosmosPA_{SideTok}Fin:0",
                bm_g,
                mats["gold"],
                arm_obj,
                root_obj,
                all_seg_names,
                weight_sampler_fa,
                smooth_shade=False,
            )
        )

        pauldron_obj = next((o for o in meshes if o.name.endswith(":2")), None)
        if pauldron_obj is not None:
            pverts = [pauldron_obj.matrix_world @ v.co for v in pauldron_obj.data.vertices]
            pz_mid = 0.5 * (min(v.z for v in pverts) + max(v.z for v in pverts)) - 1.5

            def pauldron_outer_pt(py: float, pz: float, out_off: float) -> Vector:
                num_x, num_z, den = 0.0, 0.0, 0.0
                for pv in pverts:
                    d2 = (pv.y - py) ** 2 + (pv.z - pz) ** 2 + 1.2
                    if abs(pv.x) < 18.0:
                        continue
                    w = 1.0 / (d2 * d2)
                    num_x += abs(pv.x) * w
                    num_z += pv.z * w
                    den += w
                ax = (num_x / den) if den > 0.0 else 25.0
                return Vector((sx * (ax + out_off), py, pz + out_off * 0.45))

            chev_yz = [(4.2, pz_mid + 2.4), (0.0, pz_mid - 2.8), (-4.2, pz_mid + 2.4), (0.0, pz_mid + 4.8)]
            chev_in = [pauldron_outer_pt(py, pz, -0.35) for py, pz in chev_yz]
            chev_out = [pauldron_outer_pt(py, pz, 0.65) for py, pz in chev_yz]
            bm_p = bmesh.new()
            uv_p = bm_p.loops.layers.uv.new("UVMap")
            add_box_or_prism(bm_p, uv_p, chev_in, chev_out)
            _, weight_sampler_pl, p_segs = build_pa_surface_sampler(pauldron_obj)
            p_bone = "R_Pauldron" if is_right else "L_Pauldron"
            extra_objs.append(
                finalize_rigged_pa_mesh(
                    f"CosmosPA_{SideTok}PauldronCrest:0",
                    bm_p,
                    mats["gold"],
                    arm_obj,
                    root_obj,
                    p_segs,
                    weight_sampler_pl,
                    fixed_bone_weights={p_bone: 1.0},
                    fixed_seg_name="FO4 Seg 002" if "FO4 Seg 002" in p_segs else None,
                    smooth_shade=False,
                )
            )

    all_meshes = meshes + extra_objs
    bpy.ops.object.select_all(action="DESELECT")
    if root_obj:
        root_obj.select_set(True)
    for m in all_meshes:
        m.select_set(True)
    bpy.context.view_layer.objects.active = forearm_obj
    out_p = os.path.join(OUT_DIR, dst_name)
    bpy.ops.export_scene.pynifly(filepath=out_p, target_game="FO4")
    print(f"[Blender Exported] {dst_name} ({len(all_meshes)} shapes)")


def export_cosmos_pa_leg(is_right: bool):
    clear_scene()
    mats = get_common_materials()
    side_tok = "rleg" if is_right else "lleg"
    SideTok = "RLeg" if is_right else "LLeg"
    sx = 1.0 if is_right else -1.0

    bpy.ops.import_scene.pynifly(
        filepath=os.path.join(PA_TPL_DIR, f"pa_t51_{side_tok}.nif"),
        import_cutpoints=False,
        import_tris=False,
        import_collisions=False,
    )
    root_obj = next((o for o in bpy.data.objects if "pynRoot" in o), None)
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    leg_obj = next(o for o in meshes if o.name.endswith(":2"))
    arm_obj = next((m.object for m in leg_obj.modifiers if m.type == "ARMATURE" and m.object), None)

    for m in meshes:
        if m.name.endswith(":0"):
            set_obj_single_material(m, mats["gold"])
        else:
            set_obj_single_material(m, mats["leg"])

    _, weight_sampler, all_seg_names = build_pa_surface_sampler(leg_obj)
    wverts = [leg_obj.matrix_world @ v.co for v in leg_obj.data.vertices]
    calf_vs = [v for v in wverts if 20.0 <= v.z <= 36.0]
    cx_leg = sum(v.x for v in calf_vs) / max(1, len(calf_vs))
    cy_leg = sum(v.y for v in calf_vs) / max(1, len(calf_vs))
    rx_out = max(abs(v.x - cx_leg) for v in calf_vs) if calf_vs else 6.5

    bm_l = bmesh.new()
    uv_l = bm_l.loops.layers.uv.new("UVMap")
    # Aleta estabilizadora retro-cohete en el exterior de la greba (Z = 18..38)
    fin_a = [
        Vector((cx_leg + sx * (rx_out - 0.8), cy_leg - 1.0, 18.0)),
        Vector((cx_leg + sx * (rx_out - 0.6), cy_leg - 0.8, 36.5)),
        Vector((cx_leg + sx * (rx_out + 3.2), cy_leg - 3.2, 40.0)),
        Vector((cx_leg + sx * (rx_out + 2.4), cy_leg - 2.6, 20.5)),
    ]
    fin_b = [p + Vector((0.0, 1.35, 0.0)) for p in fin_a]
    add_box_or_prism(bm_l, uv_l, fin_a, fin_b)

    # Escudo dorado en V sobre la rodilla (Z = 46..54)
    knee_vs = [v for v in wverts if 46.0 <= v.z <= 54.0]
    ky_max = max(v.y for v in knee_vs) if knee_vs else 10.5
    knee_a = [
        Vector((cx_leg - 3.2, ky_max - 0.6, 53.5)),
        Vector((cx_leg + 3.2, ky_max - 0.6, 53.5)),
        Vector((cx_leg + 2.2, ky_max + 0.4, 47.5)),
        Vector((cx_leg, ky_max + 1.2, 45.2)),
        Vector((cx_leg - 2.2, ky_max + 0.4, 47.5)),
    ]
    knee_b = [p + Vector((0.0, 0.95, 0.0)) for p in knee_a]
    add_box_or_prism(bm_l, uv_l, knee_a, knee_b)

    calf_bone = "RLeg_Calf_Armor2" if is_right else "LLeg_Calf_Armor2"
    leg_trim_obj = finalize_rigged_pa_mesh(
        f"CosmosPA_{SideTok}Gold:0",
        bm_l,
        mats["gold"],
        arm_obj,
        root_obj,
        all_seg_names,
        weight_sampler,
        fixed_bone_weights={calf_bone: 1.0},
        fixed_seg_name="FO4 Seg 003" if "FO4 Seg 003" in all_seg_names else None,
        smooth_shade=False,
    )

    all_meshes = meshes + [leg_trim_obj]
    bpy.ops.object.select_all(action="DESELECT")
    if root_obj:
        root_obj.select_set(True)
    for m in all_meshes:
        m.select_set(True)
    bpy.context.view_layer.objects.active = leg_obj
    dst_name = f"CosmosPA_{SideTok}.nif"
    out_p = os.path.join(OUT_DIR, dst_name)
    bpy.ops.export_scene.pynifly(filepath=out_p, target_game="FO4")
    print(f"[Blender Exported] {dst_name} ({len(all_meshes)} shapes)")


def export_cosmos_pa_go(src_nif: str, dst_nif: str, mat_key: str):
    clear_scene()
    mats = get_common_materials()
    bpy.ops.import_scene.pynifly(
        filepath=os.path.join(PA_TPL_DIR, src_nif),
        import_cutpoints=False,
        import_tris=False,
        import_collisions=True,
    )
    root_obj = next((o for o in bpy.data.objects if "pynRoot" in o), None)
    for d_obj in [o for o in list(bpy.data.objects) if o.type == "MESH" and "DECAL" in o.name]:
        bpy.data.objects.remove(d_obj, do_unlink=True)
    meshes = [o for o in bpy.data.objects if o.type == "MESH" and not o.name.startswith("bhk")]

    if dst_nif == "GO_CosmosPA_Helmet.nif":
        # Sustituir la malla GO angular T-51 por nuestra Escafandra Circular del Capitán Cosmos conservando la colisión Havok
        for m in meshes:
            bpy.data.objects.remove(m, do_unlink=True)
        meshes = []
        bm_dome, bm_gold, bm_visor, bm_glow = build_captain_cosmos_diver_helmet_bmeshes(Vector((0.0, 2.2, -135.0)))
        for sname, bm_s, mat_s, sm_s in [
            ("GO_CosmosPA_DiverDome:0", bm_dome, mats["helm"], True),
            ("GO_CosmosPA_HelmGold:0", bm_gold, mats["gold"], False),
            ("GO_CosmosPA_Visor:0", bm_visor, mats["visor"], True),
            ("GO_CosmosPA_HelmGlow:0", bm_glow, mats["glow"], True),
        ]:
            bmesh.ops.recalc_face_normals(bm_s, faces=bm_s.faces)
            me = bpy.data.meshes.new(sname + "Mesh")
            bm_s.to_mesh(me)
            bm_s.free()
            for p in me.polygons:
                p.use_smooth = sm_s
            me.materials.append(mat_s)
            ob = bpy.data.objects.new(sname, me)
            bpy.context.scene.collection.objects.link(ob)
            if root_obj:
                ob.parent = root_obj
            meshes.append(ob)
    else:
        for m in meshes:
            if m.name.endswith(":0") and len(m.data.vertices) < 100 and len(meshes) > 1:
                set_obj_single_material(m, mats["gold"])
            elif mat_key == "arm" and m.name.endswith(":2"):
                set_obj_single_material(m, mats["pauldron"])
            else:
                set_obj_single_material(m, mats[mat_key])

        # Insignia pentagonal en latón antiguo en la parte superior para distinguir la pieza en el Pip-Boy / mundo
        if meshes:
            base_m = meshes[0]
            wvs = [base_m.matrix_world @ v.co for v in base_m.data.vertices]
            cx = 0.5 * (min(v.x for v in wvs) + max(v.x for v in wvs))
            cy = 0.5 * (min(v.y for v in wvs) + max(v.y for v in wvs))
            top_z = max(v.z for v in wvs)
            bm = bmesh.new()
            uv_l = bm.loops.layers.uv.new("UVMap")
            pts = [(-2.6, 2.2), (2.6, 2.2), (3.4, 0.5), (0.0, -2.9), (-3.4, 0.5)]
            ra = [Vector((cx + px, cy + py, top_z - 0.5)) for px, py in pts]
            rb = [Vector((cx + px, cy + py, top_z + 0.55)) for px, py in pts]
            add_box_or_prism(bm, uv_l, ra, rb)
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            me = bpy.data.meshes.new("CosmosPAGOEmblemMesh")
            bm.to_mesh(me)
            bm.free()
            me.materials.append(mats["gold"])
            em_obj = bpy.data.objects.new("CosmosPAGOEmblem:0", me)
            bpy.context.scene.collection.objects.link(em_obj)
            if root_obj:
                em_obj.parent = root_obj
            meshes.append(em_obj)

    bpy.ops.object.select_all(action="DESELECT")
    for o in bpy.data.objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    out_p = os.path.join(OUT_DIR, dst_nif)
    bpy.ops.export_scene.pynifly(filepath=out_p, target_game="FO4")
    print(f"[Blender Exported GO] {dst_nif}")


def render_full_assembly_qa(out_png: str):
    if not out_png:
        return
    clear_scene()
    assets_root = os.path.abspath(os.path.join(OUT_DIR, "..", "..", ".."))
    png_map = {
        "cosmospabody_d.dds": os.path.join(assets_root, "preview_body_d.png"),
        "cosmospahelmet_d.dds": os.path.join(assets_root, "preview_helmet_d.png"),
        "cosmospaarm_d.dds": os.path.join(assets_root, "preview_arm_d.png"),
        "cosmospapauldron_d.dds": os.path.join(assets_root, "preview_pauldron_d.png"),
        "cosmospaleg_d.dds": os.path.join(assets_root, "preview_leg_d.png"),
        "cosmospagold_d.dds": os.path.join(assets_root, "preview_gold_d.png"),
        "cosmospavisor_d.dds": os.path.join(assets_root, "preview_visor_d.png"),
        "cosmospaglow_d.dds": os.path.join(assets_root, "preview_glow_d.png"),
    }

    part_nifs = [
        "CosmosPA_Body.nif",
        "CosmosPA_Helmet.nif",
        "CosmosPA_LArm.nif",
        "CosmosPA_RArm.nif",
        "CosmosPA_LLeg.nif",
        "CosmosPA_RLeg.nif",
    ]
    loaded_meshes = []
    for pn in part_nifs:
        before = set(bpy.data.objects)
        bpy.ops.import_scene.pynifly(
            filepath=os.path.join(OUT_DIR, pn),
            import_cutpoints=False,
            import_tris=False,
            import_collisions=False,
        )
        after = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
        loaded_meshes.extend(after)

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "TEXTURE"
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1000
    scene.render.filepath = out_png

    img_cache = {}
    for dx, rot_z in [(-82.0, math.pi), (0.0, 0.0), (82.0, math.radians(-142.0))]:
        for src in loaded_meshes:
            c = src.copy()
            c.data = src.data.copy()
            c.data.transform(src.matrix_world)
            c.modifiers.clear()
            c.parent = None
            c.display_type = "TEXTURED"
            orig_mat = src.data.materials[0] if src.data.materials else None
            c.data.materials.clear()
            pmat = bpy.data.materials.new(name="QA_" + src.name)
            pmat.use_nodes = True
            nt = pmat.node_tree
            bsdf = nt.nodes.get("Principled BSDF")
            d_rel = orig_mat.get("BSShaderTextureSet_Diffuse", "") if orig_mat else ""
            png_p = png_map.get(os.path.basename(d_rel).lower(), "")
            if bsdf and png_p and os.path.exists(png_p):
                if png_p not in img_cache:
                    img_cache[png_p] = bpy.data.images.load(png_p)
                tn = nt.nodes.new("ShaderNodeTexImage")
                tn.image = img_cache[png_p]
                nt.links.new(tn.outputs["Color"], bsdf.inputs["Base Color"])
                bsdf.inputs["Alpha"].default_value = 1.0
            c.data.materials.append(pmat)
            c.location = Vector((dx, 0.0, 0.0))
            c.rotation_euler = (0.0, 0.0, rot_z)
            scene.collection.objects.link(c)

    for src in loaded_meshes:
        src.hide_render = True

    cam_data = bpy.data.cameras.new("QACam")
    cam_data.lens = 48
    cam_obj = bpy.data.objects.new("QACam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = Vector((0.0, 310.0, 82.0))
    cam_obj.rotation_euler = (math.radians(89.0), 0.0, math.radians(180.0))
    bpy.ops.render.render(write_still=True)
    print(f"[QA Render Saved] {out_png}")


export_cosmos_pa_body()
export_cosmos_pa_helmet()
export_cosmos_pa_arm(is_right=False, is_1st=False)
export_cosmos_pa_arm(is_right=True, is_1st=False)
export_cosmos_pa_arm(is_right=False, is_1st=True)
export_cosmos_pa_arm(is_right=True, is_1st=True)
export_cosmos_pa_leg(is_right=False)
export_cosmos_pa_leg(is_right=True)
export_cosmos_pa_go("go_t51_body.nif", "GO_CosmosPA_Body.nif", "body")
export_cosmos_pa_go("go_t51_helmet.nif", "GO_CosmosPA_Helmet.nif", "helm")
export_cosmos_pa_go("go_t51_larm.nif", "GO_CosmosPA_Arm.nif", "arm")
export_cosmos_pa_go("go_t51_lleg.nif", "GO_CosmosPA_Leg.nif", "leg")
render_full_assembly_qa(RENDER_PREVIEW_PATH)
'''


def run_blender_sculpt_and_inject_connect_points() -> str:
    os.makedirs(MESH_OUT_DIR, exist_ok=True)
    qa_png = os.path.join(PA_ASSETS_DIR, "qa_render_cosmos_pa_3views.png")
    bscript_path = os.path.join(PA_ASSETS_DIR, "_blender_build_cosmos_pa.py")

    code = (
        BLENDER_PA_SCRIPT.replace("__PA_TPL_DIR__", PA_TPL_DIR)
        .replace("__OUT_DIR__", MESH_OUT_DIR)
        .replace("__RENDER_PREVIEW__", qa_png)
        .replace("__PYNIFLY_DIR__", PYNIFLY_DIR)
    )
    with open(bscript_path, "w", encoding="utf-8") as wf:
        wf.write(code)

    cmd = [BLENDER_EXE, "--background", "--python", bscript_path]
    print("Ejecutando Blender 5.2 + PyNifly para esculpir las 12 mallas .NIF de la Servoarmadura Astro-Cosmos...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print(res.stderr, file=sys.stderr)
        raise RuntimeError(f"Blender devolvió código {res.returncode}")

    # Inyectar BSConnectPoints exactos en las 8 mallas equipadas (3ª y 1ª persona)
    cp_pairs = [
        ("CosmosPA_Body.nif", "pa_t51_body.nif"),
        ("CosmosPA_Helmet.nif", "pa_t51_helmet.nif"),
        ("CosmosPA_LArm.nif", "pa_t51_larm.nif"),
        ("CosmosPA_RArm.nif", "pa_t51_rarm.nif"),
        ("CosmosPA_LArm_1st.nif", "pa_t51_larm_1st.nif"),
        ("CosmosPA_RArm_1st.nif", "pa_t51_rarm_1st.nif"),
        ("CosmosPA_LLeg.nif", "pa_t51_lleg.nif"),
        ("CosmosPA_RLeg.nif", "pa_t51_rleg.nif"),
    ]
    for dst_fn, tpl_fn in cp_pairs:
        ensure_pa_connect_points_from_template(
            os.path.join(MESH_OUT_DIR, dst_fn),
            os.path.join(PA_TPL_DIR, tpl_fn),
        )
    return qa_png


def deploy_cosmos_pa_assets() -> None:
    # Desplegar a Fallout 4\Data y a copia local del workspace
    targets = [
        (TEX_OUT_DIR, os.path.join(FO4_DATA_DIR, "Textures", "AeroArmor", "PowerArmor")),
        (MAT_OUT_DIR, os.path.join(FO4_DATA_DIR, "Materials", "AeroArmor", "PowerArmor")),
        (MESH_OUT_DIR, os.path.join(FO4_DATA_DIR, "Meshes", "AeroArmor", "PowerArmor")),
        (MESH_OUT_DIR, os.path.join(THIS_DIR, "meshes", "AeroArmor", "PowerArmor")),
    ]
    for src_d, dst_d in targets:
        os.makedirs(dst_d, exist_ok=True)
        for fn in os.listdir(src_d):
            sp = os.path.join(src_d, fn)
            if os.path.isfile(sp):
                shutil.copy2(sp, os.path.join(dst_d, fn))
        print(f"[Deployed] {dst_d} ({len(os.listdir(src_d))} archivos)")


def main() -> None:
    print("=== 1. Generando texturas PBR 2K y materiales BGSM v2 de la Servoarmadura Astro-Cosmos ===")
    generate_all_pa_textures_and_materials()
    print("\n=== 2. Esculpiendo modelos 3D .NIF e inyectando BSConnectPoints ===")
    qa_png = run_blender_sculpt_and_inject_connect_points()
    print("\n=== 3. Desplegando activos en Fallout 4\\Data ===")
    deploy_cosmos_pa_assets()
    print(f"\n[COMPLETADO] Vista previa QA generada en: {qa_png}")


if __name__ == "__main__":
    main()
