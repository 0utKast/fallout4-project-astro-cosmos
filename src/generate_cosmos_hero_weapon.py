#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
generate_cosmos_hero_weapon.py
==============================
Genera de forma 100 % autónoma (cero dependencias de Creation Club / terceros,
solo plantillas de nodos/BSConnectPoints de Fallout4 - Meshes.ba2) todos los
activos 3D PBR de la «Carabina de Rayos Astro-Cosmos» para el Traje de Superhéroe:

  - Texturas 2048x2048 BC1/DXT1 (12 mipmaps) y mapas normales/especulares BC5/ATI2:
      * CosmosWeapBody_d.dds / _n.dds / _s.dds    (Esmalte espacial Azul Cobalto Cósmico con líneas de panel)
      * CosmosWeapCrimson_d.dds / _n.dds / _s.dds (Empuñadura y guardamanos Carmesí Heroico estriado)
      * CosmosWeapGold_d.dds / _n.dds / _s.dds    (Oro Aeroespacial Bruñido 24k)
      * CosmosWeapGlow_d.dds / _n.dds / _s.dds    (Núcleo Fotónico Cian-Blanco Estelar autoiluminado)
      * CosmosWeapLens_d.dds / _n.dds / _s.dds    (Lente Óptica Telescópica Rubí-Oro reflectante)
  - Materiales binarios BGSM v2 en Materials\AeroArmor\HeroWeapon\:
      * CosmosWeapBody.BGSM, CosmosWeapCrimson.BGSM, CosmosWeapGold.BGSM,
        CosmosWeapGlow.BGSM (emitEnabled=True), CosmosWeapLens.BGSM
  - 5 Piezas Modulares 3D .NIF esculpidas desde cero en Blender 5.2 LTS + PyNifly 30.2.0
    en Meshes\Weapons\AeroArmor\HeroCarbine\ (preservando nodos animados de recarga y BSConnectPoints):
      * CosmosReceiver.nif    (Fuselaje lágrima Art-Deco + núcleo fotónico + emblemas estrella 8 puntas 3D + célula animada)
      * CosmosBarrel.nif      (Cañón acelerador con 4 anillos atómicos dorados + tubo fotónico cian + guardamanos carmesí)
      * CosmosStock.nif       (Culata espacial aerodinámica de doble arco + carrillera y pistolete carmesí + guardamonte oro)
      * CosmosReconScope.nif  (Mira telescópica torpedo 6x de reconocimiento + lente rubí-oro + sensor cian + Screen021 intacto)
      * CosmosFocuser.nif     (Plato parabólico + corona atómica de 3 puntas doradas + cristal focalizador cian)
"""

import math
import os
import shutil
import struct
import subprocess
import sys
import zlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from fallout_pbr_weathering import (
    height_to_bc5_normal,
    tileable_fbm,
    weather_antique_brass,
    weather_painted_metal,
    directional_scratches_and_drips,
)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_MESHES_DIR = os.path.join(THIS_DIR, "tools_3d", "test_meshes")
FO4_DATA_DIR = r"C:\Program Files (x86)\Steam\steamapps\common\Fallout 4\Data"
FO4_MESHES_BA2 = os.path.join(FO4_DATA_DIR, "Fallout4 - Meshes.ba2")

WEAP_ASSETS_DIR = os.path.join(THIS_DIR, "cosmos_hero_weapon_assets")
REF_SCAFFOLDS_DIR = os.path.join(WEAP_ASSETS_DIR, "ref_scaffolds")
TEX_OUT_DIR = os.path.join(WEAP_ASSETS_DIR, "textures", "AeroArmor", "HeroWeapon")
MAT_OUT_DIR = os.path.join(WEAP_ASSETS_DIR, "materials", "AeroArmor", "HeroWeapon")
MESH_OUT_DIR = os.path.join(WEAP_ASSETS_DIR, "meshes", "Weapons", "AeroArmor", "HeroCarbine")

BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
PYNIFLY_DIR = r"C:\Users\educa\AppData\Roaming\Blender Foundation\Blender\5.2\scripts\addons\io_scene_nifly"

if PYNIFLY_DIR not in sys.path:
    sys.path.insert(0, PYNIFLY_DIR)
from pyn import pynifly
from pyn.bgsmaterial import BGSMaterial


# ==============================================================================
# 0. EXTRACCIÓN DE PLANTILLAS DE NODOS DESDE FALLOUT4 - MESHES.BA2
# ==============================================================================
def extract_vanilla_scaffolds() -> None:
    """Extrae las 5 mallas modulares vanilla únicamente como andamiaje de nodos y BSConnectPoints."""
    os.makedirs(REF_SCAFFOLDS_DIR, exist_ok=True)
    needed = {
        r"meshes\weapons\laserweapons\laserreceiver.nif": "laserreceiver.nif",
        r"meshes\weapons\laserweapons\laserriflebarrel.nif": "laserriflebarrel.nif",
        r"meshes\weapons\laserweapons\laserriflemarksmanstock.nif": "laserriflemarksmanstock.nif",
        r"meshes\weapons\reconscope\pistol_scope_laser.nif": "pistol_scope_laser.nif",
        r"meshes\weapons\laserweapons\laserfocuser.nif": "laserfocuser.nif",
    }
    if all(os.path.exists(os.path.join(REF_SCAFFOLDS_DIR, v)) for v in needed.values()):
        return

    with open(FO4_MESHES_BA2, "rb") as bf:
        magic, ver, btype, num_files, name_table_offset = struct.unpack("<4sI4sIQ", bf.read(24))
        assert magic == b"BTDX", f"BA2 inválido: {magic}"
        entries = [struct.unpack("<4IQ3I", bf.read(36)) for _ in range(num_files)]
        bf.seek(name_table_offset)
        names = [bf.read(struct.unpack("<H", bf.read(2))[0]).decode("latin1") for _ in range(num_files)]
        nmap = {n.lower().replace("/", "\\"): i for i, n in enumerate(names)}

        for ba2_rel, out_name in needed.items():
            idx = nmap[ba2_rel]
            _, _, _, _, off, psz, usz, _ = entries[idx]
            bf.seek(off)
            raw = zlib.decompress(bf.read(psz)) if psz > 0 else bf.read(usz)
            with open(os.path.join(REF_SCAFFOLDS_DIR, out_name), "wb") as wf:
                wf.write(raw)
            print(f"[Scaffold Extracted] {out_name} ({len(raw):,} B)")


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
    two_sided: bool = False,
    cast_shadows: bool = True,
    emit_enabled: bool = False,
    emit_color: tuple[float, float, float] = (0.0, 0.0, 0.0),
    emit_mult: float = 1.0,
) -> bytes:
    with open(os.path.join(TEST_MESHES_DIR, "syntharmorblack.bgsm"), "rb") as rf:
        tpl = rf.read()

    hdr = bytearray(tpl[:63])
    hdr[48] = 1 if two_sided else 0
    hdr[57] = 1
    struct.pack_into("<f", hdr, 58, envmap_scale)
    hdr[62] = 0

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
        0,
        0.0,
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
# 2. GENERACIÓN PROCEDURAL DE TEXTURAS PBR 2048x2048 Y MATERIALES BGSM V2
# ==============================================================================
def _height_to_normal_rg(height_map: np.ndarray, strength: float = 2.4) -> tuple[np.ndarray, np.ndarray]:
    gy, gx = np.gradient(height_map.astype(np.float32))
    nx = -gx * strength
    ny = -gy * strength
    nz = np.ones_like(nx)
    inv_len = 1.0 / np.sqrt(nx * nx + ny * ny + nz * nz)
    r = np.clip((nx * inv_len * 0.5 + 0.5) * 255.0, 0.0, 255.0)
    g = np.clip((ny * inv_len * 0.5 + 0.5) * 255.0, 0.0, 255.0)
    return r, g


def generate_weapon_textures_and_materials() -> None:
    os.makedirs(TEX_OUT_DIR, exist_ok=True)
    os.makedirs(MAT_OUT_DIR, exist_ok=True)

    yy, xx = np.mgrid[0:2048, 0:2048].astype(np.float32)
    u = xx / 2048.0
    v = yy / 2048.0

    # 1. CosmosWeapBody: Carcasa azul cobalto pizarra envejecido con desconchones a acero, juntas remachadas y hollín
    seam_u = np.abs(((u * 6.0) % 1.0) - 0.5) > 0.486
    seam_v = np.abs(((v * 6.0) % 1.0) - 0.5) > 0.486
    panel_seams = (seam_u | seam_v).astype(np.float32)
    edge_wear = np.clip(
        ((np.abs(((u * 6.0) % 1.0) - 0.5) > 0.445) | (np.abs(((v * 6.0) % 1.0) - 0.5) > 0.445)).astype(np.float32)
        * (1.0 - panel_seams)
        * 0.85,
        0.0,
        1.0,
    )
    cav_mask = np.clip(panel_seams * 0.92, 0.0, 1.0)

    b_rgb, b_hd, bs_spec, bs_gloss = weather_painted_metal(
        (34.0, 56.0, 96.0), edge_wear, cav_mask, seed=195807,
        chip_amount=0.42, grime_amount=0.45, rust_amount=0.24,
    )
    b_rgb = b_rgb * (1.0 - panel_seams[:, :, None] * 0.65) + np.array([18.0, 20.0, 24.0], dtype=np.float32) * (panel_seams[:, :, None] * 0.65)
    body_img = Image.fromarray(np.clip(b_rgb, 8, 225).astype(np.uint8), mode="RGB")
    body_img.save(os.path.join(WEAP_ASSETS_DIR, "preview_weap_body_d.png"))
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "CosmosWeapBody_d.dds"), body_img)

    body_h = b_hd * 0.85 - panel_seams * 2.1
    bn_r, bn_g = _height_to_normal_rg(body_h, strength=2.4)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosWeapBody_n.dds"), bn_r, bn_g)
    bs_spec = np.clip(bs_spec * (1.0 - panel_seams * 0.65), 18, 175)
    bs_gloss = np.clip(bs_gloss * (1.0 - panel_seams * 0.65), 18, 165)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosWeapBody_s.dds"), bs_spec, bs_gloss)

    # 2. CosmosWeapCrimson: Polímero / baquelita / cuero carmesí oscuro desgastado con estriado ergonómico
    ribs = np.sin(v * 2048.0 * (2.0 * math.pi / 40.0)).astype(np.float32)
    knurl = (np.sin(xx * 0.28 + yy * 0.28) * np.sin(xx * 0.28 - yy * 0.28)).astype(np.float32)
    crim_edge = np.clip((ribs > 0.65).astype(np.float32) * 0.5, 0.0, 1.0)
    crim_cav = np.clip((ribs < -0.55).astype(np.float32) * 0.75, 0.0, 1.0)
    c_rgb, c_hd, cs_spec, cs_gloss = weather_painted_metal(
        (114.0, 26.0, 28.0), crim_edge, crim_cav, seed=195809,
        chip_amount=0.18, grime_amount=0.48, rust_amount=0.10,
    )
    for ch_i, amp_i in ((0, 8.0), (1, 2.5), (2, 2.8)):
        c_rgb[:, :, ch_i] += ribs * amp_i + knurl * (amp_i * 0.4)
    crim_img = Image.fromarray(np.clip(c_rgb, 10, 195).astype(np.uint8), mode="RGB")
    crim_img.save(os.path.join(WEAP_ASSETS_DIR, "preview_weap_crimson_d.png"))
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "CosmosWeapCrimson_d.dds"), crim_img)

    cn_r, cn_g = _height_to_normal_rg(ribs * 0.95 + knurl * 0.45 + c_hd * 0.4, strength=2.2)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosWeapCrimson_n.dds"), cn_r, cn_g)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosWeapCrimson_s.dds"), np.clip(cs_spec * 0.82, 18, 125), np.clip(cs_gloss * 0.78, 18, 110))

    # 3. CosmosWeapGold: Latón / bronce antiguo envejecido (adiós plástico amarillo canario)
    g_rgb, g_hd, gs_spec, gs_gloss = weather_antique_brass(2048, 2048, seed=195811)
    gold_img = Image.fromarray(np.clip(g_rgb, 12, 215).astype(np.uint8), mode="RGB")
    gold_img.save(os.path.join(WEAP_ASSETS_DIR, "preview_weap_gold_d.png"))
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "CosmosWeapGold_d.dds"), gold_img)

    gn_r, gn_g = _height_to_normal_rg(g_hd * 0.9, strength=2.0)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosWeapGold_n.dds"), gn_r, gn_g)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosWeapGold_s.dds"), gs_spec, gs_gloss)

    # 4. CosmosWeapGlow: Núcleo Fotónico Cian-Blanco Estelar autoiluminado
    rad = np.sqrt((u - 0.5) ** 2 + (v - 0.5) ** 2)
    pulse = np.clip(1.0 - rad * 0.85, 0.35, 1.0)
    striations = 0.5 + 0.5 * np.sin(u * math.pi * 24.0)
    gl_r = np.clip(85.0 + 135.0 * pulse + 18.0 * striations, 65, 248)
    gl_g = np.clip(215.0 + 35.0 * pulse, 185, 255)
    gl_b = np.full((2048, 2048), 255.0, dtype=np.float32)
    glow_img = Image.fromarray(np.stack([gl_r, gl_g, gl_b], axis=2).astype(np.uint8), mode="RGB")
    glow_img.save(os.path.join(WEAP_ASSETS_DIR, "preview_weap_glow_d.png"))
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "CosmosWeapGlow_d.dds"), glow_img)

    flat_n = np.full((2048, 2048), 128.0, dtype=np.float32)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosWeapGlow_n.dds"), flat_n, flat_n)
    write_bc5_dds_from_rg_arrays(
        os.path.join(TEX_OUT_DIR, "CosmosWeapGlow_s.dds"),
        np.full((2048, 2048), 165.0, dtype=np.float32),
        np.full((2048, 2048), 155.0, dtype=np.float32),
    )

    # 5. CosmosWeapLens: Lente Óptica Oscura Antirreflejos Azul-Rubí con retícula tenue y polvo en borde
    scratches_l, _ = directional_scratches_and_drips(2048, 2048, seed=195823)
    reticle = ((np.abs(rad * 2.0 - 0.45) < 0.008) | (np.abs(rad * 2.0 - 0.72) < 0.007)).astype(np.float32)
    edge_dust = np.clip((rad * 2.0 - 0.68) * 2.4, 0.0, 0.85)
    lens_r = np.clip(38.0 + (1.0 - np.clip(rad * 1.4, 0, 1)) * 42.0 + reticle * 68.0 - edge_dust * 18.0 + scratches_l * 14.0, 14, 145)
    lens_g = np.clip(28.0 + (1.0 - np.clip(rad * 1.4, 0, 1)) * 34.0 + reticle * 46.0 - edge_dust * 14.0 + scratches_l * 12.0, 12, 120)
    lens_b = np.clip(54.0 + (1.0 - np.clip(rad * 1.4, 0, 1)) * 58.0 + reticle * 54.0 - edge_dust * 24.0 + scratches_l * 16.0, 18, 165)
    lens_img = Image.fromarray(np.stack([lens_r, lens_g, lens_b], axis=2).astype(np.uint8), mode="RGB")
    lens_img.save(os.path.join(WEAP_ASSETS_DIR, "preview_weap_lens_d.png"))
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "CosmosWeapLens_d.dds"), lens_img)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosWeapLens_n.dds"), flat_n, flat_n)
    write_bc5_dds_from_rg_arrays(
        os.path.join(TEX_OUT_DIR, "CosmosWeapLens_s.dds"),
        np.clip(212.0 - edge_dust * 110.0 - scratches_l * 40.0, 45, 225),
        np.clip(200.0 - edge_dust * 105.0 - scratches_l * 35.0, 40, 215),
    )

    # Generar los 5 archivos .BGSM v2 calibrados al estándar Fallout 4
    bgsm_specs = [
        (
            "CosmosWeapBody.BGSM",
            build_bgsm_v2_bytes(
                diffuse_path="AeroArmor/HeroWeapon/CosmosWeapBody_d.dds",
                normal_path="AeroArmor/HeroWeapon/CosmosWeapBody_n.dds",
                specular_path="AeroArmor/HeroWeapon/CosmosWeapBody_s.dds",
                envmap_path="Shared/Cubemaps/mipblur_DefaultOutside1.dds",
                envmap_scale=0.56,
                specular_color=(0.86, 0.90, 0.96),
                specular_mult=0.92,
                smoothness=0.95,
            ),
        ),
        (
            "CosmosWeapCrimson.BGSM",
            build_bgsm_v2_bytes(
                diffuse_path="AeroArmor/HeroWeapon/CosmosWeapCrimson_d.dds",
                normal_path="AeroArmor/HeroWeapon/CosmosWeapCrimson_n.dds",
                specular_path="AeroArmor/HeroWeapon/CosmosWeapCrimson_s.dds",
                envmap_path="Shared/Cubemaps/mipblur_DefaultOutside1.dds",
                envmap_scale=0.30,
                specular_color=(0.94, 0.82, 0.82),
                specular_mult=0.78,
                smoothness=0.88,
            ),
        ),
        (
            "CosmosWeapGold.BGSM",
            build_bgsm_v2_bytes(
                diffuse_path="AeroArmor/HeroWeapon/CosmosWeapGold_d.dds",
                normal_path="AeroArmor/HeroWeapon/CosmosWeapGold_n.dds",
                specular_path="AeroArmor/HeroWeapon/CosmosWeapGold_s.dds",
                envmap_path="Shared/Cubemaps/mipblur_DefaultOutside1.dds",
                envmap_scale=0.88,
                specular_color=(0.96, 0.80, 0.44),
                specular_mult=1.06,
                smoothness=1.05,
            ),
        ),
        (
            "CosmosWeapGlow.BGSM",
            build_bgsm_v2_bytes(
                diffuse_path="AeroArmor/HeroWeapon/CosmosWeapGlow_d.dds",
                normal_path="AeroArmor/HeroWeapon/CosmosWeapGlow_n.dds",
                specular_path="AeroArmor/HeroWeapon/CosmosWeapGlow_s.dds",
                envmap_path="Shared/Cubemaps/mipblur_DefaultOutside1.dds",
                envmap_scale=0.45,
                specular_color=(0.70, 0.95, 1.00),
                specular_mult=1.00,
                smoothness=1.10,
                emit_enabled=True,
                emit_color=(0.24, 0.88, 0.96),
                emit_mult=2.20,
            ),
        ),
        (
            "CosmosWeapLens.BGSM",
            build_bgsm_v2_bytes(
                diffuse_path="AeroArmor/HeroWeapon/CosmosWeapLens_d.dds",
                normal_path="AeroArmor/HeroWeapon/CosmosWeapLens_n.dds",
                specular_path="AeroArmor/HeroWeapon/CosmosWeapLens_s.dds",
                envmap_path="Shared/Cubemaps/shinyglass_e.dds",
                envmap_scale=1.35,
                specular_color=(0.92, 0.72, 0.46),
                specular_mult=1.35,
                smoothness=1.45,
                emit_enabled=True,
                emit_color=(0.28, 0.14, 0.12),
                emit_mult=0.20,
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
# 3. INYECTOR BINARIO DE BSCONNECTPOINTS DESDE LAS PLANTILLAS MODULARES
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


def ensure_connect_points_from_scaffold(dst_nif_path: str, tpl_nif_path: str) -> None:
    """Copia íntegros BSConnectPoint::Parents y BSConnectPoint::Children desde el andamiaje vanilla."""
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

    pynifly.NifFile.Load(os.path.join(PYNIFLY_DIR, "pyn", "NiflyDLL.dll"))
    chk = pynifly.NifFile(dst_nif_path)
    print(
        f"[NIF Verified] {os.path.basename(dst_nif_path)} "
        f"({os.path.getsize(dst_nif_path):,} B, root={chk.rootName}, "
        f"CP_P={[p.name.decode() for p in chk.connect_points_parent]}, "
        f"CP_C={chk.connect_points_child}, shapes={[s.name for s in chk.shapes]})"
    )


# ==============================================================================
# 4. SCRIPT BLENDER 5.2 LTS + PYNIFLY: ESCULPIDO GEOMÉTRICO DESDE CERO + QA 4 VISTAS
# ==============================================================================
BLENDER_WEAPON_SCRIPT = r'''
import math
import os
import sys
import bpy
import bmesh
from mathutils import Vector, Matrix

REF_DIR = r"__REF_DIR__"
OUT_DIR = r"__OUT_DIR__"
RENDER_PREVIEW_PATH = r"__RENDER_PREVIEW__"
PYNIFLY_DIR = r"__PYNIFLY_DIR__"

if PYNIFLY_DIR not in sys.path:
    sys.path.insert(0, PYNIFLY_DIR)


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


def create_cosmos_materials() -> dict:
    return {
        "body": make_fo4_material(
            "CosmosWeapBody",
            r"Materials\AeroArmor\HeroWeapon\CosmosWeapBody.BGSM",
            r"textures\AeroArmor\HeroWeapon\CosmosWeapBody_d.dds",
            r"textures\AeroArmor\HeroWeapon\CosmosWeapBody_n.dds",
            r"textures\AeroArmor\HeroWeapon\CosmosWeapBody_s.dds",
        ),
        "crimson": make_fo4_material(
            "CosmosWeapCrimson",
            r"Materials\AeroArmor\HeroWeapon\CosmosWeapCrimson.BGSM",
            r"textures\AeroArmor\HeroWeapon\CosmosWeapCrimson_d.dds",
            r"textures\AeroArmor\HeroWeapon\CosmosWeapCrimson_n.dds",
            r"textures\AeroArmor\HeroWeapon\CosmosWeapCrimson_s.dds",
        ),
        "gold": make_fo4_material(
            "CosmosWeapGold",
            r"Materials\AeroArmor\HeroWeapon\CosmosWeapGold.BGSM",
            r"textures\AeroArmor\HeroWeapon\CosmosWeapGold_d.dds",
            r"textures\AeroArmor\HeroWeapon\CosmosWeapGold_n.dds",
            r"textures\AeroArmor\HeroWeapon\CosmosWeapGold_s.dds",
            r"textures\Shared\Cubemaps\mipblur_DefaultOutside1.dds",
        ),
        "glow": make_fo4_material(
            "CosmosWeapGlow",
            r"Materials\AeroArmor\HeroWeapon\CosmosWeapGlow.BGSM",
            r"textures\AeroArmor\HeroWeapon\CosmosWeapGlow_d.dds",
            r"textures\AeroArmor\HeroWeapon\CosmosWeapGlow_n.dds",
            r"textures\AeroArmor\HeroWeapon\CosmosWeapGlow_s.dds",
            r"textures\Shared\Cubemaps\mipblur_DefaultOutside1.dds",
        ),
        "lens": make_fo4_material(
            "CosmosWeapLens",
            r"Materials\AeroArmor\HeroWeapon\CosmosWeapLens.BGSM",
            r"textures\AeroArmor\HeroWeapon\CosmosWeapLens_d.dds",
            r"textures\AeroArmor\HeroWeapon\CosmosWeapLens_n.dds",
            r"textures\AeroArmor\HeroWeapon\CosmosWeapLens_s.dds",
            r"textures\Shared\Cubemaps\shinyglass_e.dds",
        ),
    }


# ------------------------------------------------------------------------------
# UTILIDADES GEOMÉTRICAS BMESH DE ALTA DENSIDAD CON UVs CONTINUAS Y SUAVIZADO
# ------------------------------------------------------------------------------
def finalize_bmesh_object(bm: bmesh.types.BMesh, obj_name: str, mat, parent_obj, smooth: bool = True):
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    uv_layer = bm.loops.layers.uv.verify()
    uv_scale = 0.045
    for f in bm.faces:
        n = f.normal
        ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
        pts = []
        for lp in f.loops:
            co = lp.vert.co
            if ax >= ay and ax >= az:
                pts.append((co.y * uv_scale, co.z * uv_scale))
            elif az >= ax and az >= ay:
                pts.append((co.x * uv_scale, co.y * uv_scale))
            else:
                pts.append((co.x * uv_scale, co.z * uv_scale))
        # Desplazamiento entero por cara: mantiene UVs cerca de [0,1] sin saltos % 1.0 dentro del triángulo
        u_off = math.floor(sum(p[0] for p in pts) / max(1, len(pts)))
        v_off = math.floor(sum(p[1] for p in pts) / max(1, len(pts)))
        for lp, (u_val, v_val) in zip(f.loops, pts):
            lp[uv_layer].uv = (u_val - u_off, v_val - v_off)

    me = bpy.data.meshes.new(obj_name + "_Mesh")
    bm.to_mesh(me)
    bm.free()
    for poly in me.polygons:
        poly.use_smooth = smooth
    me.materials.append(mat)
    obj = bpy.data.objects.new(obj_name, me)
    bpy.context.scene.collection.objects.link(obj)
    if parent_obj is not None:
        obj.parent = parent_obj
        obj.matrix_parent_inverse = Matrix.Identity(4)
    return obj


def add_lofted_tube(
    bm: bmesh.types.BMesh,
    stations: list,
    n_seg: int = 32,
    cap_start: bool = True,
    cap_end: bool = True,
    superellipse_p: float = 2.0,
    cut_mag_notch: bool = False,
):
    """
    stations: lista de tuplas (cx, y, cz, rx, rz) a lo largo del eje Y.
    Soporta perfiles superelípticos suaves y rebaje opcional para la célula animada.
    """
    rings = []
    for cx, y, cz, rx, rz in stations:
        ring = []
        for i in range(n_seg):
            ang = (2.0 * math.pi * i) / n_seg
            ca, sa = math.cos(ang), math.sin(ang)
            sx = math.copysign(abs(ca) ** (2.0 / superellipse_p), ca) * rx
            sz = math.copysign(abs(sa) ** (2.0 / superellipse_p), sa) * rz
            px = cx + sx
            pz = cz + sz
            if cut_mag_notch and (4.3 <= y <= 9.2) and (px < -0.35) and (pz > 3.15):
                px = max(px, -1.65)
                pz = min(pz, 4.15)
            ring.append(bm.verts.new((px, y, pz)))
        rings.append(ring)

    for r_idx in range(len(rings) - 1):
        r0 = rings[r_idx]
        r1 = rings[r_idx + 1]
        for i in range(n_seg):
            ni = (i + 1) % n_seg
            bm.faces.new((r0[i], r0[ni], r1[ni], r1[i]))

    if cap_start and len(rings) > 0:
        c0 = stations[0]
        vc0 = bm.verts.new((c0[0], c0[1], c0[2]))
        r0 = rings[0]
        for i in range(n_seg):
            ni = (i + 1) % n_seg
            bm.faces.new((vc0, r0[ni], r0[i]))

    if cap_end and len(rings) > 0:
        ce = stations[-1]
        vce = bm.verts.new((ce[0], ce[1], ce[2]))
        re = rings[-1]
        for i in range(n_seg):
            ni = (i + 1) % n_seg
            bm.faces.new((vce, re[i], re[ni]))


def add_torus_ring_y(
    bm: bmesh.types.BMesh,
    cx: float,
    cy: float,
    cz: float,
    major_r: float,
    minor_r_x: float,
    minor_r_y: float,
    n_major: int = 36,
    n_minor: int = 16,
):
    """Añade un anillo toroidal bruñido perpendicular al eje Y (cañón/mira)."""
    rings = []
    for i in range(n_major):
        theta = (2.0 * math.pi * i) / n_major
        ct, st = math.cos(theta), math.sin(theta)
        sub_ring = []
        for j in range(n_minor):
            phi = (2.0 * math.pi * j) / n_minor
            cp, sp = math.cos(phi), math.sin(phi)
            rr = major_r + minor_r_x * cp
            px = cx + rr * ct
            pz = cz + rr * st
            py = cy + minor_r_y * sp
            sub_ring.append(bm.verts.new((px, py, pz)))
        rings.append(sub_ring)

    for i in range(n_major):
        ni = (i + 1) % n_major
        for j in range(n_minor):
            nj = (j + 1) % n_minor
            bm.faces.new((rings[i][j], rings[ni][j], rings[ni][nj], rings[i][nj]))


def add_swept_fin(bm: bmesh.types.BMesh, profile_yz: list, half_thick_base: float, half_thick_tip: float, x_offset: float = 0.0, tilt_rad: float = 0.0):
    """Crea una aleta Art-Deco biselada con perfil 2D (y, r_dist) rotada por tilt_rad alrededor del eje Y."""
    ct, st = math.cos(tilt_rad), math.sin(tilt_rad)
    n = len(profile_yz)
    r_min = min(r for _, r in profile_yz)
    r_max = max(r for _, r in profile_yz)
    span = max(0.01, r_max - r_min)

    left_v = []
    right_v = []
    for y, r in profile_yz:
        u = (r - r_min) / span
        ht = half_thick_base * (1.0 - u) + half_thick_tip * u
        # Local: perp=(-ht/+ht), radial=r
        lx = x_offset - ht * ct - r * st
        lz = -ht * st + r * ct
        rx = x_offset + ht * ct - r * st
        rz = ht * st + r * ct
        left_v.append(bm.verts.new((lx, y, lz)))
        right_v.append(bm.verts.new((rx, y, rz)))

    bm.faces.new(left_v[::-1])
    bm.faces.new(right_v)
    for i in range(n):
        ni = (i + 1) % n
        bm.faces.new((left_v[i], left_v[ni], right_v[ni], right_v[i]))


def add_starburst_medallion_x(bm: bmesh.types.BMesh, x_base: float, cy: float, cz: float, sign_x: float, outer_r: float = 1.65, inner_r: float = 0.62, height_x: float = 0.28):
    """Emblema 3D en relieve de estrella cósmica de 8 puntas del Capitán Cosmos en los flancos."""
    pts = 16
    base_ring = []
    top_ring = []
    for i in range(pts):
        ang = (2.0 * math.pi * i) / pts
        rad = outer_r if (i % 2 == 0) else inner_r
        if i in (0, 8):
            rad *= 1.28  # Puntas horizontales alargadas estilo cómic espacial
        py = cy + rad * math.cos(ang)
        pz = cz + rad * math.sin(ang)
        base_ring.append(bm.verts.new((x_base, py, pz)))
        top_ring.append(bm.verts.new((x_base + sign_x * height_x * 0.65, cy + rad * 0.72 * math.cos(ang), cz + rad * 0.72 * math.sin(ang))))

    apex = bm.verts.new((x_base + sign_x * height_x, cy, cz))
    back_c = bm.verts.new((x_base, cy, cz))
    for i in range(pts):
        ni = (i + 1) % pts
        if sign_x > 0:
            bm.faces.new((base_ring[i], base_ring[ni], top_ring[ni], top_ring[i]))
            bm.faces.new((top_ring[i], top_ring[ni], apex))
            bm.faces.new((back_c, base_ring[ni], base_ring[i]))
        else:
            bm.faces.new((base_ring[ni], base_ring[i], top_ring[i], top_ring[ni]))
            bm.faces.new((top_ring[ni], top_ring[i], apex))
            bm.faces.new((back_c, base_ring[i], base_ring[ni]))


def import_scaffold_and_prune(scaffold_fn: str, keep_mesh_names: set = None):
    clear_scene()
    keep_mesh_names = keep_mesh_names or set()
    bpy.ops.import_scene.pynifly(
        filepath=os.path.join(REF_DIR, scaffold_fn),
        import_cutpoints=False,
        import_tris=False,
        import_collisions=False,
    )
    for obj in list(bpy.data.objects):
        if obj.type == "MESH" and obj.name not in keep_mesh_names:
            # Si tenía hijos extraños, re-parentarlos; en LaserGun los nodos mesh son hojas
            bpy.data.objects.remove(obj, do_unlink=True)


def get_root_or_node(base_name: str):
    if base_name in bpy.data.objects:
        return bpy.data.objects[base_name]
    if f"{base_name}:ROOT" in bpy.data.objects:
        return bpy.data.objects[f"{base_name}:ROOT"]
    for o in bpy.data.objects:
        if o.name.endswith(":ROOT"):
            return o
    raise KeyError(f"Root node {base_name} not found in {[o.name for o in bpy.data.objects]}")


def export_current_nif(dst_fn: str, active_mesh):
    bpy.ops.object.select_all(action="DESELECT")
    for o in bpy.data.objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = active_mesh
    out_p = os.path.join(OUT_DIR, dst_fn)
    os.makedirs(os.path.dirname(out_p), exist_ok=True)
    bpy.ops.export_scene.pynifly(filepath=out_p, target_game="FO4")
    print(f"[Blender Exported] {dst_fn}")


# ------------------------------------------------------------------------------
# PIEZA 1: RECEPTOR ESPACIAL ASTRO-COSMOS (CosmosReceiver.nif)
# ------------------------------------------------------------------------------
def build_cosmos_receiver():
    import_scaffold_and_prune("laserreceiver.nif")
    mats = create_cosmos_materials()

    rec_node = bpy.data.objects["LaserRifleReceiver"]
    mag_node = bpy.data.objects["WeaponMagazine"]
    latch_node = bpy.data.objects["WeaponExtra1"]
    bolt_node = bpy.data.objects["WeaponBolt"]

    # 1A. Fuselaje lágrima Azul Cobalto Cósmico (Y = -3.0 .. +12.0)
    bm_body = bmesh.new()
    fuselage_stations = [
        (0.0, -3.10, 2.20, 1.35, 1.85),
        (0.0, -2.20, 2.55, 2.15, 2.55),
        (0.0, -0.60, 2.85, 2.85, 3.05),
        (0.0,  1.80, 2.95, 3.10, 3.15),
        (0.0,  4.50, 2.95, 3.08, 3.12),
        (0.0,  7.50, 2.90, 2.98, 3.02),
        (0.0, 10.20, 2.82, 2.82, 2.90),
        (0.0, 11.95, 2.78, 2.62, 2.75),
    ]
    add_lofted_tube(bm_body, fuselage_stations, n_seg=36, superellipse_p=2.35, cut_mag_notch=True)
    obj_body = finalize_bmesh_object(bm_body, "CosmosReceiverBody:0", mats["body"], rec_node)

    # 1B. Cámara central fotónica autoiluminada Cian-Blanco (visible por las troneras laterales)
    bm_glow = bmesh.new()
    for sx in (-1.0, 1.0):
        glow_stations = [
            (sx * 2.55, -0.20, 2.75, 0.62, 0.72),
            (sx * 2.72,  2.50, 2.80, 0.65, 0.82),
            (sx * 2.68,  6.50, 2.78, 0.62, 0.78),
            (sx * 2.48, 10.40, 2.75, 0.55, 0.65),
        ]
        add_lofted_tube(bm_glow, glow_stations, n_seg=20, superellipse_p=2.2)
    obj_glow = finalize_bmesh_object(bm_glow, "CosmosReceiverCore:0", mats["glow"], rec_node)

    # 1C. Espina dorsal Art-Deco en Oro 24k, Riel Óptico Superior y Emblemas Estrella 8 Puntas
    bm_gold = bmesh.new()
    add_swept_fin(
        bm_gold,
        [(-2.6, 4.4), (-1.2, 6.25), (3.8, 6.35), (6.4, 5.75), (6.6, 4.8)],
        half_thick_base=0.52,
        half_thick_tip=0.14,
    )
    # Riel de precisión dorado en P-Scope (Y=7.0..11.8, Z=5.3..5.65)
    rail_stations = [
        (0.0,  6.80, 5.45, 0.95, 0.25),
        (0.0, 11.60, 5.45, 0.95, 0.25),
    ]
    add_lofted_tube(bm_gold, rail_stations, n_seg=16, superellipse_p=3.2)
    # Costillas doradas divisoras en las troneras laterales + emblemas estrella 8 puntas
    for y_rib in (0.8, 4.4, 8.2):
        add_torus_ring_y(bm_gold, 0.0, y_rib, 2.85, major_r=2.92, minor_r_x=0.18, minor_r_y=0.22, n_major=32, n_minor=12)
    add_starburst_medallion_x(bm_gold,  3.06, 2.60, 2.85,  1.0, outer_r=1.55, inner_r=0.58, height_x=0.30)
    add_starburst_medallion_x(bm_gold, -3.06, 2.60, 2.85, -1.0, outer_r=1.55, inner_r=0.58, height_x=0.30)
    obj_gold = finalize_bmesh_object(bm_gold, "CosmosReceiverGold:0", mats["gold"], rec_node)

    # 1D. Célula de Microfusión Astro-Cosmos ANIMADA bajo WeaponMagazine (Z = 0.0 .. 5.68)
    bm_cell_b = bmesh.new()
    # Cilindro a lo largo de Z local de WeaponMagazine
    rings = []
    for zc, rc in [(0.05, 1.48), (0.50, 1.68), (5.15, 1.68), (5.65, 1.42)]:
        ring = [bm_cell_b.verts.new((rc * math.cos(2 * math.pi * i / 24), rc * math.sin(2 * math.pi * i / 24), zc)) for i in range(24)]
        rings.append(ring)
    for ri in range(len(rings) - 1):
        for i in range(24):
            ni = (i + 1) % 24
            bm_cell_b.faces.new((rings[ri][i], rings[ri][ni], rings[ri + 1][ni], rings[ri + 1][i]))
    vc_bot = bm_cell_b.verts.new((0.0, 0.0, 0.02))
    vc_top = bm_cell_b.verts.new((0.0, 0.0, 5.68))
    for i in range(24):
        ni = (i + 1) % 24
        bm_cell_b.faces.new((vc_bot, rings[0][ni], rings[0][i]))
        bm_cell_b.faces.new((vc_top, rings[-1][i], rings[-1][ni]))
    finalize_bmesh_object(bm_cell_b, "LaserRifleMicrofusionCell:0", mats["gold"], mag_node)

    # 1E. Pestillo animado en Oro 24k bajo WeaponExtra1 y Tirador de Carga Carmesí bajo WeaponBolt
    bm_latch = bmesh.new()
    add_lofted_tube(
        bm_latch,
        [(-0.35, -2.2, 1.5, 0.55, 1.45), (-0.35, 2.2, 1.5, 0.55, 1.45)],
        n_seg=16,
        superellipse_p=2.8,
    )
    finalize_bmesh_object(bm_latch, "LaserRifleLatch:0", mats["gold"], latch_node)

    bm_bolt = bmesh.new()
    add_lofted_tube(
        bm_bolt,
        [(-1.25, -0.45, 0.85, 0.95, 0.55), (-1.25, 0.45, 0.85, 0.95, 0.55)],
        n_seg=16,
        superellipse_p=2.5,
    )
    finalize_bmesh_object(bm_bolt, "LaserRifleBolt:0", mats["crimson"], bolt_node)

    export_current_nif("CosmosReceiver.nif", obj_body)


# ------------------------------------------------------------------------------
# PIEZA 2: CAÑÓN ACELERADOR DE ANILLOS ATÓMICOS (CosmosBarrel.nif)
# ------------------------------------------------------------------------------
def build_cosmos_barrel():
    import_scaffold_and_prune("laserriflebarrel.nif")
    mats = create_cosmos_materials()
    root_node = get_root_or_node("LaserRifleBarrel")

    # Eje de P-Muzzle y P-ProjectileNode: (0.0, 21.081, -0.663)
    # 2A. Carenado aerodinámico cónico Azul Cobalto Cósmico
    bm_shroud = bmesh.new()
    shroud_stations = [
        (0.0, -0.40, -0.35, 2.58, 2.68),
        (0.0,  2.50, -0.45, 2.45, 2.52),
        (0.0,  7.00, -0.55, 2.15, 2.22),
        (0.0, 12.50, -0.62, 1.82, 1.90),
        (0.0, 17.50, -0.65, 1.52, 1.58),
        (0.0, 21.15, -0.663, 1.28, 1.32),
    ]
    add_lofted_tube(bm_shroud, shroud_stations, n_seg=32, superellipse_p=2.3)
    obj_shroud = finalize_bmesh_object(bm_shroud, "CosmosBarrelShroud:0", mats["body"], root_node)

    # 2B. Tubo Acelerador Fotónico Cian-Blanco brillante (sobresale entre los anillos)
    bm_core = bmesh.new()
    core_stations = [
        (0.0,  0.50, -0.663, 1.92, 1.05),
        (0.0,  6.00, -0.663, 1.78, 0.98),
        (0.0, 12.00, -0.663, 1.58, 0.92),
        (0.0, 18.00, -0.663, 1.38, 0.88),
        (0.0, 21.40, -0.663, 1.02, 0.85),
    ]
    add_lofted_tube(bm_core, core_stations, n_seg=28)
    finalize_bmesh_object(bm_core, "CosmosBarrelPhotonCore:0", mats["glow"], root_node)

    # 2C. 4 Anillos Aceleradores Atómicos Concéntricos en Oro 24k + Aletas Retro-Espaciales
    bm_gold = bmesh.new()
    ring_specs = [
        ( 4.20, 2.82, 0.36, 0.55),
        ( 8.80, 2.58, 0.34, 0.52),
        (13.40, 2.34, 0.32, 0.48),
        (18.00, 2.10, 0.30, 0.45),
    ]
    for ry, mr, mrx, mry in ring_specs:
        add_torus_ring_y(bm_gold, 0.0, ry, -0.663, major_r=mr, minor_r_x=mrx, minor_r_y=mry, n_major=36, n_minor=16)

    # Aleta dorsal baja (Z_max = +3.05, dejando libre toda la línea visual de la mira en Z_local = +5.92)
    add_swept_fin(
        bm_gold,
        [(0.5, 1.8), (3.2, 3.02), (15.8, 2.55), (20.4, 1.25)],
        half_thick_base=0.34,
        half_thick_tip=0.09,
    )
    # 2 aletas estabilizadoras laterales inclinadas estilo cohete Capitán Cosmos
    for tilt in (math.radians(82.0), math.radians(-82.0)):
        add_swept_fin(
            bm_gold,
            [(1.5, 1.7), (4.5, 2.95), (16.5, 2.35), (20.2, 1.15)],
            half_thick_base=0.28,
            half_thick_tip=0.08,
            tilt_rad=tilt,
        )
    finalize_bmesh_object(bm_gold, "CosmosBarrelAtomicRings:0", mats["gold"], root_node)

    # 2D. Guardamanos Ergonómico Inferior Carmesí Heroico (donde apoya la mano izquierda en Y=+1..+12, Z=-5.4..-2.0)
    bm_grip = bmesh.new()
    foregrip_stations = [
        (0.0, -1.50, -3.15, 1.45, 1.15),
        (0.0,  0.80, -3.75, 1.78, 1.65),
        (0.0,  5.50, -3.85, 1.82, 1.72),
        (0.0, 10.50, -3.65, 1.68, 1.55),
        (0.0, 14.20, -2.85, 1.25, 1.05),
        (0.0, 15.60, -2.05, 0.82, 0.65),
    ]
    add_lofted_tube(bm_grip, foregrip_stations, n_seg=28, superellipse_p=2.6)
    finalize_bmesh_object(bm_grip, "CosmosBarrelForegrip:0", mats["crimson"], root_node)

    export_current_nif("CosmosBarrel.nif", obj_shroud)


# ------------------------------------------------------------------------------
# PIEZA 3: CULATA AERODINÁMICA ESPACIAL Y PISTOLETE (CosmosStock.nif)
# ------------------------------------------------------------------------------
def build_cosmos_stock():
    import_scaffold_and_prune("laserriflemarksmanstock.nif")
    mats = create_cosmos_materials()
    root_node = get_root_or_node("LaserRifleMarksmanStock")

    # 3A. Estructura de Doble Arco Aerodinámico Azul Cobalto Cósmico (Y = -25.0 .. +5.5)
    bm_stock = bmesh.new()
    # Brazo superior (lomo de culata que enlaza suavemente con la cola del receptor en Y=-2.8)
    upper_spar = [
        (0.0, -24.80, -1.65, 0.98, 1.45),
        (0.0, -20.50, -1.15, 1.08, 1.35),
        (0.0, -14.00, -0.55, 1.15, 1.32),
        (0.0,  -7.50,  0.35, 1.28, 1.48),
        (0.0,  -3.20,  1.45, 1.45, 1.72),
        (0.0,   0.80,  0.65, 1.55, 1.15),
    ]
    add_lofted_tube(bm_stock, upper_spar, n_seg=28, superellipse_p=2.4)

    # Arco inferior de unión entre cantonera (Y=-24.8, Z=-6.2) y base del pistolete (Y=-5.0, Z=-7.4)
    lower_spar = [
        (0.0, -24.80, -5.85, 0.85, 1.25),
        (0.0, -20.00, -6.45, 0.82, 0.88),
        (0.0, -13.50, -6.85, 0.85, 0.85),
        (0.0,  -7.80, -7.25, 0.95, 0.88),
        (0.0,  -4.80, -7.35, 1.15, 0.92),
    ]
    add_lofted_tube(bm_stock, lower_spar, n_seg=24, superellipse_p=2.4)

    # Pilar vertical trasero de cantonera + refuerzo central inclinado
    butt_pillar = [
        (0.0, -24.65, -6.60, 0.98, 0.55),
        (0.0, -24.65, -3.80, 1.05, 1.45),
        (0.0, -24.65, -1.10, 0.98, 0.65),
    ]
    # Modelamos el pilar trasero a lo largo de Y corto (-25.0 .. -23.4)
    add_lofted_tube(
        bm_stock,
        [(0.0, -25.05, -3.75, 1.02, 3.25), (0.0, -23.20, -3.75, 0.96, 3.05)],
        n_seg=28,
        superellipse_p=2.8,
    )
    obj_stock = finalize_bmesh_object(bm_stock, "CosmosStockFrame:0", mats["body"], root_node)

    # 3B. Pistolete Ergonómico y Carrillera en Carmesí Heroico
    bm_crim = bmesh.new()
    # Pistolete inclinado (mano derecha agarra Y=[-5.5, -0.5], Z=[-8.3, -0.5])
    grip_rings = []
    grip_profile = [
        (-4.95, -8.10, 1.22, 1.65),
        (-4.55, -6.60, 1.32, 1.82),
        (-3.95, -4.50, 1.36, 1.88),
        (-3.35, -2.30, 1.32, 1.82),
        (-2.85, -0.35, 1.28, 1.75),
    ]
    for cy_g, cz_g, rx_g, ry_g in grip_profile:
        ring = [
            bm_crim.verts.new((rx_g * math.cos(2 * math.pi * i / 28), cy_g + ry_g * math.sin(2 * math.pi * i / 28), cz_g))
            for i in range(28)
        ]
        grip_rings.append(ring)
    for ri in range(len(grip_rings) - 1):
        for i in range(28):
            ni = (i + 1) % 28
            bm_crim.faces.new((grip_rings[ri][i], grip_rings[ri][ni], grip_rings[ri + 1][ni], grip_rings[ri + 1][i]))
    vc_gb = bm_crim.verts.new((0.0, -4.95, -8.20))
    vc_gt = bm_crim.verts.new((0.0, -2.85, -0.25))
    for i in range(28):
        ni = (i + 1) % 28
        bm_crim.faces.new((vc_gb, grip_rings[0][ni], grip_rings[0][i]))
        bm_crim.faces.new((vc_gt, grip_rings[-1][i], grip_rings[-1][ni]))

    # Carrillera acolchada superior Carmesí
    add_lofted_tube(
        bm_crim,
        [
            (0.0, -20.20, 0.15, 0.85, 0.55),
            (0.0, -17.50, 0.55, 1.16, 0.82),
            (0.0, -10.50, 0.95, 1.20, 0.85),
            (0.0,  -8.20, 0.85, 0.88, 0.55),
        ],
        n_seg=24,
        superellipse_p=2.5,
    )
    finalize_bmesh_object(bm_crim, "CosmosStockGripCrimson:0", mats["crimson"], root_node)

    # 3C. Cantonera Curva, Pomo del Pistolete, Guardamonte Art-Deco y Gatillo en Oro 24k
    bm_gold = bmesh.new()
    # Cantonera dorada trasera (Y = -25.85 .. -24.95)
    add_lofted_tube(
        bm_gold,
        [(0.0, -25.85, -3.75, 1.08, 3.45), (0.0, -24.95, -3.75, 1.08, 3.35)],
        n_seg=28,
        superellipse_p=2.8,
    )
    # Pomo dorado en la base del pistolete
    add_lofted_tube(
        bm_gold,
        [(0.0, -6.75, -8.15, 1.38, 0.35), (0.0, -3.15, -8.15, 1.38, 0.35)],
        n_seg=20,
        superellipse_p=2.8,
    )
    # Guardamonte esculpido (Y = -1.6 .. +4.8, Z = -3.8 .. -0.1)
    add_lofted_tube(
        bm_gold,
        [
            (0.0, -1.60, -3.35, 0.52, 0.28),
            (0.0,  1.20, -3.65, 0.52, 0.28),
            (0.0,  3.85, -2.65, 0.52, 0.28),
            (0.0,  4.85, -0.35, 0.52, 0.35),
        ],
        n_seg=16,
        superellipse_p=2.6,
    )
    # Gatillo curvo dorado (Y = +1.35, Z = -2.4 .. -0.3)
    add_swept_fin(
        bm_gold,
        [(0.95, -0.25), (1.55, -0.25), (1.25, -2.45), (0.75, -2.25)],
        half_thick_base=0.22,
        half_thick_tip=0.14,
    )
    finalize_bmesh_object(bm_gold, "CosmosStockGoldTrim:0", mats["gold"], root_node)

    # 3D. Conducto de Energía Fotónico Cian en el interior del arco de la culata
    bm_glow = bmesh.new()
    add_lofted_tube(
        bm_glow,
        [
            (0.0, -22.50, -5.25, 0.42, 0.32),
            (0.0, -14.00, -5.65, 0.42, 0.32),
            (0.0,  -7.80, -6.05, 0.42, 0.32),
        ],
        n_seg=16,
    )
    finalize_bmesh_object(bm_glow, "CosmosStockConduit:0", mats["glow"], root_node)

    export_current_nif("CosmosStock.nif", obj_stock)


# ------------------------------------------------------------------------------
# PIEZA 4: MIRA TELESCÓPICA DE RECONOCIMIENTO 6X (CosmosReconScope.nif)
# ------------------------------------------------------------------------------
def build_cosmos_recon_scope():
    # CRÍTICO: Preservar Screen021:0 y Screen021:1 intactos en (-0.010, -5.227, 3.117)
    import_scaffold_and_prune("pistol_scope_laser.nif", keep_mesh_names={"Screen021:0", "Screen021:1"})
    mats = create_cosmos_materials()
    root_node = get_root_or_node("LaserScope")

    # Eje óptico exacto de Screen021: X = -0.010, Z = +3.117, Ocular en Y = -5.227
    ox, oz = -0.010, 3.117

    # 4A. Tubo Telescópico Torpedo Azul Cobalto Cósmico (tapa trasera sellada delante de Screen021 en Y=-5.227)
    bm_tube = bmesh.new()
    # Cuerpo principal desde justo delante de Screen021 (-5.14) hasta campana frontal (+5.65)
    tube_stations = [
        (ox, -5.14, oz, 1.38, 1.38),
        (ox, -4.10, oz, 1.44, 1.44),
        (ox, -3.35, oz, 1.24, 1.24),
        (ox,  2.40, oz, 1.24, 1.24),
        (ox,  3.50, oz, 1.62, 1.62),
        (ox,  5.65, oz, 1.82, 1.82),
    ]
    add_lofted_tube(bm_tube, tube_stations, n_seg=36, cap_start=True, cap_end=True)
    # Bisel ocular envolvente detrás de Screen021 (Y = -5.45 .. -5.15, radio mayor 1.38)
    add_torus_ring_y(bm_tube, ox, -5.24, oz, major_r=1.38, minor_r_x=0.14, minor_r_y=0.22, n_major=36, n_minor=14)
    # Base de anclaje al riel (Z = -0.25 .. +0.75)
    add_lofted_tube(
        bm_tube,
        [(0.0, -2.85, 0.22, 1.18, 0.48), (0.0, 2.45, 0.22, 1.18, 0.48)],
        n_seg=20,
        superellipse_p=3.0,
    )
    obj_tube = finalize_bmesh_object(bm_tube, "CosmosScopeTube:0", mats["body"], root_node)

    # 4B. Monturas Art-Deco Dobles, Anillos Vernier, Torretas y Bisel Frontal en Oro 24k
    bm_gold = bmesh.new()
    for y_strut in (-2.05, 1.45):
        add_swept_fin(
            bm_gold,
            [(y_strut - 0.65, 0.45), (y_strut + 0.55, 0.45), (y_strut + 0.35, 2.15), (y_strut - 0.85, 2.15)],
            half_thick_base=0.68,
            half_thick_tip=0.48,
        )
        add_torus_ring_y(bm_gold, ox, y_strut - 0.10, oz, major_r=1.32, minor_r_x=0.16, minor_r_y=0.34, n_major=32, n_minor=14)

    # Anillo ocular dorado y visera parasol frontal dorada
    add_torus_ring_y(bm_gold, ox, -5.32, oz, major_r=1.40, minor_r_x=0.12, minor_r_y=0.16, n_major=36, n_minor=12)
    add_torus_ring_y(bm_gold, ox,  5.68, oz, major_r=1.84, minor_r_x=0.15, minor_r_y=0.24, n_major=36, n_minor=14)

    # Torreta lateral de deriva (derecha +X)
    add_lofted_tube(
        bm_gold,
        [(ox + 1.35, -0.65, oz, 0.45, 0.45), (ox + 1.68, -0.15, oz, 0.48, 0.48), (ox + 1.35, 0.35, oz, 0.45, 0.45)],
        n_seg=18,
    )
    finalize_bmesh_object(bm_gold, "CosmosScopeGoldMount:0", mats["gold"], root_node)

    # 4C. Lente Frontal Objetivo + Lente Ocular Trasera (sellada para hip-fire, detrás de Screen021 en Y=-5.227)
    bm_lens = bmesh.new()
    add_lofted_tube(
        bm_lens,
        [(ox, 5.62, oz, 1.66, 1.66), (ox, 5.76, oz, 1.52, 1.52)],
        n_seg=32,
    )
    add_lofted_tube(
        bm_lens,
        [(ox, -5.17, oz, 1.30, 1.30), (ox, -5.13, oz, 1.34, 1.34)],
        n_seg=32,
        cap_start=True,
        cap_end=False,
    )
    finalize_bmesh_object(bm_lens, "CosmosScopeObjectiveLens:0", mats["lens"], root_node)

    # 4D. Módulo Superior de Telemetría Recon Autoiluminado Cian (marca diamantes sobre hostiles)
    bm_sensor = bmesh.new()
    add_lofted_tube(
        bm_sensor,
        [
            (ox, -1.80, oz + 1.48, 0.46, 0.32),
            (ox,  0.50, oz + 1.62, 0.56, 0.40),
            (ox,  3.10, oz + 1.55, 0.42, 0.30),
        ],
        n_seg=20,
        superellipse_p=2.4,
    )
    finalize_bmesh_object(bm_sensor, "CosmosScopeReconSensor:0", mats["glow"], root_node)

    export_current_nif("CosmosReconScope.nif", obj_tube)


# ------------------------------------------------------------------------------
# PIEZA 5: CORONA FOCALIZADORA ATÓMICA DE 3 PUNTAS (CosmosFocuser.nif)
# ------------------------------------------------------------------------------
def build_cosmos_focuser():
    import_scaffold_and_prune("laserfocuser.nif")
    mats = create_cosmos_materials()
    root_node = get_root_or_node("LaserFocuser")

    # P-ProjectileNode está en (0.0, 9.88, 0.0)
    # 5A. Collar de acople y Plato Parabólico Azul Cobalto Cósmico (Y = 0.0 .. +3.6)
    bm_dish = bmesh.new()
    dish_stations = [
        (0.0, 0.00, 0.0, 1.32, 1.32),
        (0.0, 1.40, 0.0, 1.42, 1.42),
        (0.0, 2.55, 0.0, 2.28, 2.28),
        (0.0, 3.45, 0.0, 2.45, 2.45),
        (0.0, 3.85, 0.0, 1.65, 1.65),
    ]
    add_lofted_tube(bm_dish, dish_stations, n_seg=36)
    obj_dish = finalize_bmesh_object(bm_dish, "CosmosFocuserDish:0", mats["body"], root_node)

    # 5B. Cristal Focalizador Fotónico Central Cian-Blanco (Y = +2.8 .. +9.55, justo tras P-ProjectileNode 9.88)
    bm_crys = bmesh.new()
    crys_stations = [
        (0.0, 2.80, 0.0, 0.92, 0.92),
        (0.0, 5.50, 0.0, 0.78, 0.78),
        (0.0, 8.20, 0.0, 0.52, 0.52),
        (0.0, 9.55, 0.0, 0.14, 0.14),
    ]
    add_lofted_tube(bm_crys, crys_stations, n_seg=12)
    finalize_bmesh_object(bm_crys, "CosmosFocuserCrystal:0", mats["glow"], root_node)

    # 5C. Corona Emisora de 3 Puntas Doradas del Capitán Cosmos + Esferas Atómicas + Halo Dorado
    bm_crown = bmesh.new()
    add_torus_ring_y(bm_crown, 0.0, 3.45, 0.0, major_r=2.48, minor_r_x=0.18, minor_r_y=0.24, n_major=36, n_minor=14)
    add_torus_ring_y(bm_crown, 0.0, 6.75, 0.0, major_r=1.88, minor_r_x=0.13, minor_r_y=0.16, n_major=36, n_minor=12)

    for deg in (90.0, 210.0, 330.0):
        rad_ang = math.radians(deg)
        ca, sa = math.cos(rad_ang), math.sin(rad_ang)
        prong_stations = []
        for py, r_pos, p_rad in [
            (2.90, 2.15, 0.34),
            (5.20, 2.02, 0.28),
            (7.80, 1.78, 0.22),
            (10.15, 1.52, 0.15),
        ]:
            prong_stations.append((r_pos * ca, py, r_pos * sa, p_rad, p_rad))
        add_lofted_tube(bm_crown, prong_stations, n_seg=16)

        # Esfera atómica dorada en la punta de cada aguja emisora (Y = 10.35)
        sx, sz = 1.50 * ca, 1.50 * sa
        sph_stations = [
            (sx, 10.00, sz, 0.12, 0.12),
            (sx, 10.18, sz, 0.32, 0.32),
            (sx, 10.38, sz, 0.38, 0.38),
            (sx, 10.58, sz, 0.32, 0.32),
            (sx, 10.74, sz, 0.10, 0.10),
        ]
        add_lofted_tube(bm_crown, sph_stations, n_seg=18)

    finalize_bmesh_object(bm_crown, "CosmosFocuserCrown:0", mats["gold"], root_node)

    export_current_nif("CosmosFocuser.nif", obj_dish)


# ------------------------------------------------------------------------------
# RENDER DE CONTROL DE CALIDAD (QA SHEET 4 VISTAS ENSAMBLADAS POR CONNECTPOINTS)
# ------------------------------------------------------------------------------
def render_assembled_carbine_4views(out_png: str):
    if not out_png:
        return
    clear_scene()
    assets_root = os.path.abspath(os.path.join(OUT_DIR, "..", "..", "..", ".."))
    png_map = {
        "cosmosweapbody_d.dds": os.path.join(assets_root, "preview_weap_body_d.png"),
        "cosmosweapcrimson_d.dds": os.path.join(assets_root, "preview_weap_crimson_d.png"),
        "cosmosweapgold_d.dds": os.path.join(assets_root, "preview_weap_gold_d.png"),
        "cosmosweapglow_d.dds": os.path.join(assets_root, "preview_weap_glow_d.png"),
        "cosmosweaplens_d.dds": os.path.join(assets_root, "preview_weap_lens_d.png"),
    }

    # Offsets exactos de ensamblaje BSConnectPoint en coordenadas WEAPON:
    # Receiver = (0, 0, 0)
    # Stock (P-Grip) = (0, 0, 0)
    # Barrel (P-Barrel) = (0.005, 11.868, 2.784)
    # Scope (P-Scope) = (0.006, 9.685, 5.586)
    # Focuser (P-Barrel + P-Muzzle) = (0.005, 11.868 + 21.081, 2.784 - 0.663) = (0.005, 32.949, 2.121)
    part_transforms = [
        ("CosmosReceiver.nif", Vector((0.0, 0.0, 0.0))),
        ("CosmosStock.nif", Vector((0.0, 0.0, 0.0))),
        ("CosmosBarrel.nif", Vector((0.005, 11.868, 2.784))),
        ("CosmosReconScope.nif", Vector((0.006, 9.685, 5.586))),
        ("CosmosFocuser.nif", Vector((0.005, 32.949, 2.121))),
    ]

    assembled_baked = []
    img_cache = {}

    for nif_fn, cp_offset in part_transforms:
        before = set(bpy.data.objects)
        bpy.ops.import_scene.pynifly(
            filepath=os.path.join(OUT_DIR, nif_fn),
            import_cutpoints=False,
            import_tris=False,
            import_collisions=False,
        )
        new_objs = [o for o in bpy.data.objects if o not in before]
        bpy.context.view_layer.update()
        for o in new_objs:
            if o.type == "MESH" and not o.name.startswith("Screen021"):
                me_copy = o.data.copy()
                mw = Matrix.Translation(cp_offset) @ o.matrix_world
                me_copy.transform(mw)

                orig_mat = o.data.materials[0] if o.data.materials else None
                d_rel = orig_mat.get("BSShaderTextureSet_Diffuse", "") if orig_mat else ""
                bname = os.path.basename(d_rel).lower()
                png_p = png_map.get(bname, "")

                me_copy.materials.clear()
                pmat = bpy.data.materials.new(name="QA_" + o.name)
                pmat.use_nodes = True
                nt = pmat.node_tree
                bsdf = nt.nodes.get("Principled BSDF")
                if bsdf:
                    if "gold" in bname:
                        bsdf.inputs["Metallic"].default_value = 0.92
                        bsdf.inputs["Roughness"].default_value = 0.22
                    elif "body" in bname:
                        bsdf.inputs["Metallic"].default_value = 0.55
                        bsdf.inputs["Roughness"].default_value = 0.28
                    elif "glow" in bname:
                        bsdf.inputs["Roughness"].default_value = 0.10
                        if "Emission Color" in bsdf.inputs:
                            bsdf.inputs["Emission Color"].default_value = (0.22, 0.92, 1.0, 1.0)
                            bsdf.inputs["Emission Strength"].default_value = 2.5
                    elif "lens" in bname:
                        bsdf.inputs["Metallic"].default_value = 0.85
                        bsdf.inputs["Roughness"].default_value = 0.08
                    if png_p and os.path.exists(png_p):
                        if png_p not in img_cache:
                            img_cache[png_p] = bpy.data.images.load(png_p)
                        tn = nt.nodes.new("ShaderNodeTexImage")
                        tn.image = img_cache[png_p]
                        nt.links.new(tn.outputs["Color"], bsdf.inputs["Base Color"])
                me_copy.materials.append(pmat)
                assembled_baked.append(me_copy)

        for o in new_objs:
            bpy.data.objects.remove(o, do_unlink=True)

    # Crear 4 copias del arma completa ensamblada en cuadrícula 2x2 frente a cámara ortográfica en +Y mirando a -Y:
    # 1) Arriba-Izquierda: Perfil Lateral Derecho limpio
    # 2) Arriba-Derecha: Perspectiva Heroica 3/4 Frontal-Superior
    # 3) Abajo-Izquierda: Perspectiva 3/4 Trasera-Ocular (detalle culata + mira Recon + célula fusión)
    # 4) Abajo-Derecha: Vista Cenital / Corona Atómica Frontal
    poses = [
        # (grid_x, grid_z, rot_euler_xyz, scale)
        (-38.0,  18.0, (0.0, 0.0, math.radians(-90.0)), 1.00),
        ( 38.0,  18.0, (math.radians(18.0), math.radians(-14.0), math.radians(-52.0)), 1.05),
        (-38.0, -18.0, (math.radians(20.0), math.radians(14.0), math.radians(-132.0)), 1.05),
        ( 38.0, -18.0, (math.radians(82.0), 0.0, math.radians(-90.0)), 1.00),
    ]

    scene = bpy.context.scene
    for idx_p, (gx, gz, rot_e, sc) in enumerate(poses):
        piv = bpy.data.objects.new(f"PosePivot_{idx_p}", None)
        scene.collection.objects.link(piv)
        piv.location = Vector((gx, 0.0, gz))
        piv.rotation_euler = rot_e
        piv.scale = Vector((sc, sc, sc))
        for m_idx, me_src in enumerate(assembled_baked):
            inst = bpy.data.objects.new(f"QAWeap_{idx_p}_{m_idx}", me_src)
            # Centrar el arma (cuyo Y va de -25.8 a +43.7 -> centro Y ≈ +9.0, Z ≈ +1.5) en el pivote
            inst.location = Vector((0.0, -9.0, -1.5))
            inst.parent = piv
            scene.collection.objects.link(inst)

    # Iluminación de estudio de 3 puntos + fondo oscuro espacial
    world = bpy.data.worlds.new("QAWorld")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.035, 0.045, 0.075, 1.0)
        bg.inputs[1].default_value = 1.1

    for lname, lpos, lrot, energy, col in [
        ("KeyLight", (-35.0, -95.0, 55.0), (math.radians(58.0), 0.0, math.radians(-18.0)), 3.8, (1.0, 0.97, 0.92)),
        ("FillLight", (55.0, -85.0, 15.0), (math.radians(78.0), 0.0, math.radians(28.0)), 2.1, (0.78, 0.88, 1.0)),
        ("RimLight", (0.0, 65.0, 48.0), (math.radians(-52.0), 0.0, math.radians(180.0)), 2.6, (1.0, 0.88, 0.65)),
    ]:
        ldata = bpy.data.lights.new(lname, type="SUN")
        ldata.energy = energy
        ldata.color = col
        lobj = bpy.data.objects.new(lname, ldata)
        lobj.location = Vector(lpos)
        lobj.rotation_euler = lrot
        scene.collection.objects.link(lobj)

    cam_data = bpy.data.cameras.new("QACam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 152.0
    cam_obj = bpy.data.objects.new("QACam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = Vector((0.0, -140.0, 0.0))
    cam_obj.rotation_euler = (math.radians(90.0), 0.0, 0.0)

    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.filepath = out_png
    bpy.ops.render.render(write_still=True)
    print(f"[QA Render Saved] {out_png}")


build_cosmos_receiver()
build_cosmos_barrel()
build_cosmos_stock()
build_cosmos_recon_scope()
build_cosmos_focuser()
render_assembled_carbine_4views(RENDER_PREVIEW_PATH)
'''


def run_blender_and_inject_connect_points() -> str:
    os.makedirs(MESH_OUT_DIR, exist_ok=True)
    qa_png = os.path.join(WEAP_ASSETS_DIR, "qa_render_cosmos_carbine_4views.png")
    bscript_path = os.path.join(WEAP_ASSETS_DIR, "_blender_build_cosmos_carbine.py")

    code = (
        BLENDER_WEAPON_SCRIPT.replace("__REF_DIR__", REF_SCAFFOLDS_DIR)
        .replace("__OUT_DIR__", MESH_OUT_DIR)
        .replace("__RENDER_PREVIEW__", qa_png)
        .replace("__PYNIFLY_DIR__", PYNIFLY_DIR)
    )
    with open(bscript_path, "w", encoding="utf-8") as wf:
        wf.write(code)

    cmd = [BLENDER_EXE, "--background", "--python-exit-code", "1", "--python", bscript_path]
    print("Ejecutando Blender 5.2 LTS + PyNifly para esculpir las 5 piezas .NIF de la Carabina Astro-Cosmos...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print(res.stderr, file=sys.stderr)
        raise RuntimeError(f"Blender devolvió código {res.returncode}")

    cp_pairs = [
        ("CosmosReceiver.nif", "laserreceiver.nif"),
        ("CosmosBarrel.nif", "laserriflebarrel.nif"),
        ("CosmosStock.nif", "laserriflemarksmanstock.nif"),
        ("CosmosReconScope.nif", "pistol_scope_laser.nif"),
        ("CosmosFocuser.nif", "laserfocuser.nif"),
    ]
    for dst_fn, tpl_fn in cp_pairs:
        ensure_connect_points_from_scaffold(
            os.path.join(MESH_OUT_DIR, dst_fn),
            os.path.join(REF_SCAFFOLDS_DIR, tpl_fn),
        )
    return qa_png


def deploy_cosmos_weapon_assets() -> None:
    targets = [
        (TEX_OUT_DIR, os.path.join(FO4_DATA_DIR, "Textures", "AeroArmor", "HeroWeapon")),
        (MAT_OUT_DIR, os.path.join(FO4_DATA_DIR, "Materials", "AeroArmor", "HeroWeapon")),
        (MESH_OUT_DIR, os.path.join(FO4_DATA_DIR, "Meshes", "Weapons", "AeroArmor", "HeroCarbine")),
        (MESH_OUT_DIR, os.path.join(THIS_DIR, "meshes", "Weapons", "AeroArmor", "HeroCarbine")),
    ]
    for src_d, dst_d in targets:
        os.makedirs(dst_d, exist_ok=True)
        for fn in os.listdir(src_d):
            sp = os.path.join(src_d, fn)
            if os.path.isfile(sp):
                shutil.copy2(sp, os.path.join(dst_d, fn))
        print(f"[Deployed] {dst_d} ({len(os.listdir(src_d))} archivos)")


def main() -> None:
    print("=== 0. Extrayendo plantillas de nodos modulares desde Fallout4 - Meshes.ba2 ===")
    extract_vanilla_scaffolds()
    print("\n=== 1. Generando texturas PBR 2K (BC1/BC5) y materiales BGSM v2 ===")
    generate_weapon_textures_and_materials()
    print("\n=== 2. Esculpiendo las 5 piezas 3D en Blender 5.2 LTS + inyectando BSConnectPoints ===")
    qa_png = run_blender_and_inject_connect_points()
    print("\n=== 3. Desplegando activos en Fallout 4\\Data ===")
    deploy_cosmos_weapon_assets()
    print(f"\n[COMPLETADO] Hoja QA 4 vistas lista en: {qa_png}")


if __name__ == "__main__":
    main()
