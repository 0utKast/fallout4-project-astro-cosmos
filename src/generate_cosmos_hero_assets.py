#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_cosmos_hero_assets.py
==============================
Genera de forma 100 % autónoma (cero dependencias de Creation Club / terceros) todos los
activos 3D PBR del «Traje de Vuelo Astro-Cosmos» para Fallout 4 (1.10.163 y Next-Gen/AE):

  - Texturas 2048x2048 BC1/DXT1 (12 mipmaps) y mapas especulares/normales BC5/ATI2:
      * CosmosHeroSuit_d.dds     (Azul cobalto cósmico + botas altas carmesí con ribete en V dorado + puños dorados)
      * CosmosHeroGloves_d.dds   (Guanteletes heroicos carmesí) + CosmosHeroGloves_s.dds
      * CosmosHeroCape_d.dds     (Capa heroica carmesí con cenefa dorada y astro-emblema) + _n.dds + _s.dds
      * CosmosHeroGold_d.dds     (Atlas metálico: oro bruñido 24k, esmalte rubí y núcleo atómico) + _n.dds + _s.dds
  - Materiales binarios BGSM v2:
      * CosmosHeroSuit.BGSM
      * CosmosHeroGloves.BGSM
      * CosmosHeroCape.BGSM      (twoSided = True + malla cerrada con grosor físico)
      * CosmosHeroGold.BGSM      (Acabado metálico dorado reflectante)
  - Modelos 3D .NIF (+ .SSF) esculpidos y riggeados en Blender 5.2 + PyNifly 30.2.0:
      * CosmosHeroSuitM.nif / CosmosHeroSuitF.nif (Traje ceñido + Emblema pectoral 3D en relieve + Broches hombrera + Cinturón en V + Capa 3D plisada)
      * CosmosHeroSuit1stM.nif / CosmosHeroSuit1stF.nif (Mangas cobalto y puños dorados en 1ª persona)
      * CosmosHeroGlovesM.nif / CosmosHeroGlovesF.nif (Guanteletes carmesí en 1ª y 3ª persona)
      * CosmosHeroSuitGO.nif (Modelo de inventario Pip-Boy / mundo con colisión e insignia 3D)
"""

import json
import math
import os
import shutil
import struct
import subprocess
import sys
import zlib
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

from fallout_pbr_weathering import (
    tileable_fbm,
    cellular_chip_mask,
    directional_scratches_and_drips,
    extract_masked_template_highpass,
    height_to_bc5_normal,
    weather_antique_brass,
)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_MESHES_DIR = os.path.join(THIS_DIR, "tools_3d", "test_meshes")
FO4_DATA_DIR = r"C:\Program Files (x86)\Steam\steamapps\common\Fallout 4\Data"

HERO_ASSETS_DIR = os.path.join(THIS_DIR, "cosmos_hero_assets")
TEX_OUT_DIR = os.path.join(HERO_ASSETS_DIR, "textures", "AeroArmor", "Hero")
MAT_OUT_DIR = os.path.join(HERO_ASSETS_DIR, "materials", "AeroArmor", "Hero")
MESH_OUT_DIR = os.path.join(HERO_ASSETS_DIR, "meshes", "AeroArmor", "Hero")

BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
PYNIFLY_DIR = r"C:\Users\educa\AppData\Roaming\Blender Foundation\Blender\5.2\scripts\addons\io_scene_nifly"


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


def encode_dds_with_12_mips(base_img: Image.Image) -> list[bytes]:
    assert base_img.size == (2048, 2048)
    mips = []
    cur = base_img.convert("RGB")
    for level in range(12):
        arr = np.asarray(cur, dtype=np.uint8)
        mips.append(compress_bc1_level(arr))
        if level < 11:
            nw = max(1, cur.width // 2)
            nh = max(1, cur.height // 2)
            cur = cur.resize((nw, nh), Image.Resampling.LANCZOS)
    return mips


def write_dds_file(dst_path: str, mips: list[bytes], width: int = 2048, height: int = 2048) -> None:
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    flags = 0x00000001 | 0x00000002 | 0x00000004 | 0x00001000 | 0x00020000 | 0x00080000
    pitch_or_linear = len(mips[0])
    mip_count = len(mips)
    pf = struct.pack("<II4sIIIII", 32, 0x00000004, b"DXT1", 0, 0, 0, 0, 0)
    caps = 0x00001000 | 0x00000008 | 0x00400000
    hdr = struct.pack(
        "<4sIIIIIII44s32sIIIII",
        b"DDS ",
        124,
        flags,
        height,
        width,
        pitch_or_linear,
        0,
        mip_count,
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
    """Codifica una matriz 2D uint8/float32 (H x W) en bloques BC4 de 8 bytes."""
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
    """Escribe un archivo DDS BC5_UNORM (FourCC ATI2) completo con cadena de mipmaps a partir de canales R y G."""
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
        chunks.append((blk16.tobytes(), mip_idx, mip_idx))
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
        wf.write(b"DDS " + header + b"".join(c[0] for c in chunks))


def build_bgsm_v2_bytes(
    diffuse_path: str,
    normal_path: str,
    specular_path: str,
    envmap_path: str = "Shared/Cubemaps/mipblur_InstInterior.dds",
    root_material: str = "template/OutfitTemplate_Wet.bgsm",
    envmap_scale: float = 0.85,
    specular_color: tuple[float, float, float] = (0.88, 0.93, 1.00),
    specular_mult: float = 1.20,
    smoothness: float = 1.25,
    subsurface_lighting: int = 1,
    subsurface_rolloff: float = 0.20,
    two_sided: bool = False,
) -> bytes:
    """Construye un archivo binario BGSM v2 válido a partir de la plantilla oficial SynthArmorBlack.BGSM."""
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
    tail_59 = tpl[-59:]
    return bytes(hdr) + tex_block + mid_64 + root_block + tail_59


# ==============================================================================
# 2. GENERACIÓN PROCEDURAL + HIGH-PASS PBR DE TEXTURAS 2K (TRAJE, GUANTES, CAPA, ORO)
# ==============================================================================
def _extract_highpass_detail(src_dds_path: str, detail_gain: float = 0.85, macro_gain: float = 0.14) -> np.ndarray:
    return extract_masked_template_highpass(
        src_dds_path,
        lum_thresh=14.0,
        detail_gain=detail_gain,
        macro_gain=macro_gain,
    )


def build_suit_uv_masks_via_blender(force_rebuild: bool = False) -> tuple[np.ndarray, np.ndarray]:
    """
    Extrae las máscaras exactas de botas altas carmesí (con pico en V frontal estilo superhéroe)
    y ribetes dorados (borde superior de las botas, puños de muñeca y cuello) subdividiendo la
    malla 6x6 en UV/3D para lograr curvas suaves de estudio sin dientes de sierra poligonales.
    """
    cache_boots = os.path.join(HERO_ASSETS_DIR, "_uv_mask_boots.png")
    cache_gold = os.path.join(HERO_ASSETS_DIR, "_uv_mask_gold.png")
    if force_rebuild or not (os.path.exists(cache_boots) and os.path.exists(cache_gold)):
        os.makedirs(HERO_ASSETS_DIR, exist_ok=True)
        uv_json = os.path.join(HERO_ASSETS_DIR, "_suit_uv_polys.json")
        helper_py = os.path.join(HERO_ASSETS_DIR, "_extract_suit_uv_masks.py")
        code = f"""import json, os, sys, bpy, bmesh

PYNIFLY_DIR = r"{PYNIFLY_DIR}"
if PYNIFLY_DIR not in sys.path:
    sys.path.insert(0, PYNIFLY_DIR)
from pyn import pynifly

boot_polys = []
gold_polys = []

for fn in ["SynthUniform.nif", "SynthUniformF.nif"]:
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.ops.import_scene.pynifly(
        filepath=os.path.join(r"{TEST_MESHES_DIR}", fn),
        import_cutpoints=False, import_tris=False, import_collisions=False
    )
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        # Subdividir cada polígono 6x6 (interpolando linealmente UVs y coordenadas 3D) para curvas suaves
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=5, use_grid_fill=True)
        bmesh.ops.triangulate(bm, faces=list(bm.faces))
        uv_lay = bm.loops.layers.uv.active
        mw = obj.matrix_world
        for face in bm.faces:
            wcos = [mw @ v.co for v in face.verts]
            uvs = [[round(lp[uv_lay].uv.x * 2047.0, 2), round((1.0 - lp[uv_lay].uv.y) * 2047.0, 2)] for lp in face.loops]
            # Ignorar triángulos degenerados que crucen costuras UV grandes
            us = [p[0] for p in uvs]
            vs = [p[1] for p in uvs]
            if (max(us) - min(us)) > 160.0 or (max(vs) - min(vs)) > 160.0:
                continue
            avg_z = sum(c.z for c in wcos) / len(wcos)
            avg_y = sum(c.y for c in wcos) / len(wcos)
            avg_x = sum(abs(c.x) for c in wcos) / len(wcos)

            # Pico en V heroico suave en la espinilla delantera (avg_y > 0 sube hasta Z=29.2; gemelo trasero Z=25.0)
            t_front = max(0.0, min(1.0, (avg_y + 3.0) / 10.0))
            v_peak = 4.2 * (t_front * t_front * (3.0 - 2.0 * t_front))
            boot_top = 24.8 + v_peak

            if avg_z < boot_top and avg_x < 23.0:
                boot_polys.append(uvs)
            elif boot_top <= avg_z <= (boot_top + 2.6) and avg_x < 23.0:
                gold_polys.append(uvs)

            avg_u = sum(us) / (len(us) * 2047.0)
            avg_v = sum(vs) / (len(vs) * 2047.0)
            if 0.310 <= avg_v <= 0.398 and ((0.722 <= avg_u <= 0.810) or (0.914 <= avg_u <= 0.998)):
                gold_polys.append(uvs)
            if avg_z >= 115.8 and avg_x < 9.5:
                gold_polys.append(uvs)
        bm.free()

with open(r"{uv_json}", "w", encoding="utf-8") as wf:
    json.dump({{"boots": boot_polys, "gold": gold_polys}}, wf)
"""
        with open(helper_py, "w", encoding="utf-8") as wf:
            wf.write(code)
        subprocess.run([BLENDER_EXE, "--background", "--python", helper_py], check=True)

        with open(uv_json, "r", encoding="utf-8") as rf:
            poly_data = json.load(rf)

        boots_im = Image.new("L", (2048, 2048), 0)
        gold_im = Image.new("L", (2048, 2048), 0)
        draw_b = ImageDraw.Draw(boots_im)
        draw_g = ImageDraw.Draw(gold_im)
        for pts in poly_data["boots"]:
            draw_b.polygon([tuple(p) for p in pts], fill=255)
        for pts in poly_data["gold"]:
            draw_g.polygon([tuple(p) for p in pts], fill=255)
        draw_b.rectangle([0, 0, int(0.502 * 2047), int(0.220 * 2047)], fill=255)
        boots_im = boots_im.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(radius=1.6))
        gold_im = gold_im.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(radius=1.4))
        boots_im.save(cache_boots)
        gold_im.save(cache_gold)

    b_mask = np.asarray(Image.open(cache_boots).convert("L"), dtype=np.float32) / 255.0
    g_mask = np.asarray(Image.open(cache_gold).convert("L"), dtype=np.float32) / 255.0
    return b_mask, g_mask


def build_cosmos_suit_texture(force_rebuild: bool = False) -> Image.Image:
    mod = _extract_highpass_detail(
        os.path.join(TEST_MESHES_DIR, "SynthUniform_d.dds"),
        detail_gain=1.02,
        macro_gain=0.22,
    )
    boot_mask, gold_mask = build_suit_uv_masks_via_blender(force_rebuild=force_rebuild)

    N = 2048
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    fbm = tileable_fbm(N, N, base_cells=8, octaves=4, persistence=0.54, seed=20770801)
    scratch, drip = directional_scratches_and_drips(N, N, seed=20770802)

    # Trama táctica envejecida y polvo del Yermo sobre tela y cuero
    weave = (np.sin(xx * 0.52) * np.sin((xx * 0.26 + yy * 0.45)) * np.sin((xx * 0.26 - yy * 0.45))) * 1.5
    grime = np.clip((fbm - 0.34) * 1.25 + drip * 0.45, 0.0, 1.0)
    scuff = np.clip(scratch * 0.55 + np.clip(fbm - 0.58, 0.0, 0.42), 0.0, 1.0)

    # 1. Azul Pizarra Aeroespacial Curtido (cuerpo, piernas y mangas)
    blue_rgb = np.stack(
        [
            28.0 + mod * 0.65 + weave * 0.4 + grime * 16.0 + scuff * 18.0,
            52.0 + mod * 0.90 + weave * 0.6 + grime * 11.0 + scuff * 16.0,
            92.0 + mod * 1.15 + weave * 0.9 - grime * 14.0 + scuff * 14.0,
        ],
        axis=2,
    )
    # 2. Cuero Carmesí Envejecido de Pre-Guerra (botas altas con rozaduras y polvo)
    red_rgb = np.stack(
        [
            112.0 + mod * 1.15 - grime * 26.0 + scuff * 16.0,
            24.0 + mod * 0.45 - grime * 4.0 + scuff * 18.0,
            26.0 + mod * 0.45 - grime * 4.0 + scuff * 14.0,
        ],
        axis=2,
    )
    # 3. Latón/Bronce Antiguo Envejecido (ribete en V de botas, puños de 1ª/3ª persona y cuello)
    gold_rgb = np.stack(
        [
            136.0 + mod * 0.95 - grime * 36.0,
            102.0 + mod * 0.80 - grime * 28.0,
            46.0 + mod * 0.45 - grime * 14.0,
        ],
        axis=2,
    )

    bm = boot_mask[:, :, None]
    gm = np.clip(gold_mask[:, :, None], 0.0, 1.0)
    out = blue_rgb * (1.0 - bm) + red_rgb * bm
    out = out * (1.0 - gm) + gold_rgb * gm
    return Image.fromarray(np.clip(out, 12.0, 224.0).astype(np.uint8))


def build_cosmos_gloves_texture() -> Image.Image:
    mod = _extract_highpass_detail(
        os.path.join(TEST_MESHES_DIR, "KnightGloves_d.dds"),
        detail_gain=0.98,
        macro_gain=0.20,
    )
    fbm = tileable_fbm(2048, 2048, base_cells=8, octaves=4, persistence=0.54, seed=20770803)
    scratch, drip = directional_scratches_and_drips(2048, 2048, seed=20770804)
    grime = np.clip((fbm - 0.36) * 1.25 + drip * 0.40, 0.0, 1.0)
    scuff = np.clip(scratch * 0.50, 0.0, 1.0)
    out = np.stack(
        [
            110.0 + mod * 1.15 - grime * 28.0 + scuff * 18.0,
            24.0 + mod * 0.48 - grime * 4.0 + scuff * 20.0,
            26.0 + mod * 0.50 - grime * 4.0 + scuff * 16.0,
        ],
        axis=2,
    )
    return Image.fromarray(np.clip(out, 14.0, 212.0).astype(np.uint8))


def build_cosmos_cape_textures() -> tuple[Image.Image, np.ndarray, np.ndarray]:
    """
    Genera:
      - CosmosHeroCape_d.dds (2048x2048): Capa carmesí imperial con tejido diagonal fino, doble cenefa
        dorada perimetral y astro-estrella del Capitán Cosmos bordada en hilo de oro en la espalda.
      - CosmosHeroCape_n.dds (1024x1024 R/G): Relieve de trama textil y bordado dorado.
      - CosmosHeroCape_s.dds (1024x1024 R/G): Brillo satinado en la tela y brillo metálico en el bordado de oro.
    """
    im = Image.new("RGB", (2048, 2048), (138, 18, 22))
    gold_mask_im = Image.new("L", (2048, 2048), 0)
    dg = ImageDraw.Draw(gold_mask_im)

    # Doble cenefa dorada a lo largo de los bordes laterales e inferior (UV: u en [0..1], v_img=0 arriba hombros, v_img=1 dobladillo inferior)
    margin_outer = 46
    margin_inner = 78
    # Cenefa exterior gruesa (laterales e inferior)
    dg.line([(margin_outer, 60), (margin_outer, 2048 - margin_outer), (2048 - margin_outer, 2048 - margin_outer), (2048 - margin_outer, 60)], fill=255, width=22)
    # Filete interior fino con esquinas biseladas estilo cómic clásico
    dg.line([(margin_inner, 90), (margin_inner, 2048 - margin_inner - 36), (margin_inner + 36, 2048 - margin_inner), (2048 - margin_inner - 36, 2048 - margin_inner), (2048 - margin_inner, 2048 - margin_inner - 36), (2048 - margin_inner, 90)], fill=235, width=8)

    # Insignia Astro-Cosmos bordada en oro en el centro-alto de la espalda (cx=1024, cy=560)
    # Pre-compensada en Y (escala 0.40) respecto a la proporción alto/ancho 3D de la capa para verse 100% circular
    cx, cy = 1024, 560
    aspect_y = 0.40
    dg.ellipse([cx - 260, int(cy - 260 * aspect_y), cx + 260, int(cy + 260 * aspect_y)], outline=255, width=16)
    dg.ellipse([cx - 220, int(cy - 220 * aspect_y), cx + 220, int(cy + 220 * aspect_y)], outline=190, width=6)

    for angle_deg in (-36.0, 36.0):
        orbit_pts = []
        rad = math.radians(angle_deg)
        ca, sa = math.cos(rad), math.sin(rad)
        for k in range(96):
            t = (2.0 * math.pi * k) / 96.0
            ox = 330.0 * math.cos(t)
            oy = 110.0 * math.sin(t)
            rx = cx + ox * ca - oy * sa
            ry = cy + (ox * sa + oy * ca) * aspect_y
            orbit_pts.append((rx, ry))
        orbit_pts.append(orbit_pts[0])
        dg.line(orbit_pts, fill=245, width=11)

    # Estrella cósmica de 4 puntas / cohete central estilo Capitán Cosmos
    star_pts = [
        (cx, cy - 320 * aspect_y),
        (cx + 52, cy - 64 * aspect_y),
        (cx + 280, cy),
        (cx + 52, cy + 64 * aspect_y),
        (cx, cy + 305 * aspect_y),
        (cx - 52, cy + 64 * aspect_y),
        (cx - 280, cy),
        (cx - 52, cy - 64 * aspect_y),
    ]
    dg.polygon(star_pts, fill=255)

    gmask_2k = np.asarray(gold_mask_im.filter(ImageFilter.GaussianBlur(radius=1.2)), dtype=np.float32) / 255.0

    fbm_cape = tileable_fbm(2048, 2048, base_cells=8, octaves=4, persistence=0.54, seed=20770805)
    yy, xx = np.mgrid[0:2048, 0:2048].astype(np.float32)
    # Paño grueso de lana curada con desgaste y polvo del Yermo en el dobladillo inferior
    twill = (np.sin((xx + yy) * 0.65) * 2.4 + np.sin((xx - yy) * 0.32) * 1.5)
    v_frac = yy / 2048.0
    hem_dust = np.clip((np.maximum(0.0, (v_frac - 0.52) / 0.48) ** 1.3) * 0.65 + (fbm_cape - 0.44) * 0.95, 0.0, 0.88)
    thread_wear = np.clip((fbm_cape - 0.38) * 1.15, 0.0, 1.0)

    red_r = (114.0 * (1.0 - 0.22 * v_frac)) * (1.0 - 0.38 * hem_dust) + 64.0 * (0.38 * hem_dust) + twill * 0.95
    red_g = (22.0 * (1.0 - 0.16 * v_frac)) * (1.0 - 0.38 * hem_dust) + 52.0 * (0.38 * hem_dust) + twill * 0.30
    red_b = (24.0 * (1.0 - 0.16 * v_frac)) * (1.0 - 0.38 * hem_dust) + 42.0 * (0.38 * hem_dust) + twill * 0.32

    gold_r = 142.0 - thread_wear * 32.0 + twill * 1.1
    gold_g = 108.0 - thread_wear * 24.0 + twill * 0.9
    gold_b = 46.0 - thread_wear * 12.0 + twill * 0.5

    out = np.stack(
        [
            red_r * (1.0 - gmask_2k) + gold_r * gmask_2k,
            red_g * (1.0 - gmask_2k) + gold_g * gmask_2k,
            red_b * (1.0 - gmask_2k) + gold_b * gmask_2k,
        ],
        axis=2,
    )
    diff_im = Image.fromarray(np.clip(out, 14.0, 212.0).astype(np.uint8))

    # Mapa normal y especular 1024x1024 calibrados a Fallout 4 (paño mate vs hilo de latón)
    gmask_1k = np.asarray(gold_mask_im.resize((1024, 1024), Image.Resampling.LANCZOS), dtype=np.float32) / 255.0
    fbm_1k = tileable_fbm(1024, 1024, base_cells=8, octaves=3, persistence=0.52, seed=20770806)
    yy1, xx1 = np.mgrid[0:1024, 0:1024].astype(np.float32)
    weave_h = np.sin((xx1 + yy1) * 1.1) * 0.10 + gmask_1k * 0.55 + fbm_1k * 0.25
    nx, ny = height_to_bc5_normal(weave_h, strength=1.8)

    spec_r = np.clip(46.0 * (1.0 - gmask_1k) + 126.0 * gmask_1k - fbm_1k * 12.0, 24.0, 145.0)
    spec_g = np.clip(32.0 * (1.0 - gmask_1k) + 114.0 * gmask_1k - fbm_1k * 10.0, 18.0, 134.0)
    return diff_im, np.stack([nx, ny], axis=2), np.stack([spec_r, spec_g], axis=2)


def build_cosmos_gold_textures() -> tuple[Image.Image, np.ndarray, np.ndarray]:
    """
    Atlas metálico 2048x2048 para las piezas rígidas 3D (Escudo Pectoral, Cohete/Átomo en relieve,
    Broches Hombrera y Cinturón Heroico en V):
      - Zona Superior (V_img = 0.00..0.55): Latón/Bronce Antiguo curtido de Pre-Guerra
      - Zona Inf-Izq  (U = 0.00..0.50, V_img = 0.55..1.00): Esmalte Rubí Carmesí envejecido
      - Zona Inf-Der  (U = 0.50..1.00, V_img = 0.55..1.00): Cristal Cian-Acero atómico con pátina
    """
    brass_2k, brass_h2k, _, _ = weather_antique_brass(
        h=2048,
        w=2048,
        seed=20770807,
    )
    out = brass_2k.astype(np.float32)

    yy, xx = np.mgrid[0:2048, 0:2048].astype(np.float32)
    fbm_e = tileable_fbm(2048, 2048, base_cells=8, octaves=4, persistence=0.54, seed=20770808)
    brush = np.sin(yy * 0.85) * 1.4 + (fbm_e - 0.5) * 18.0

    # Esmalte rubí carmesí envejecido (abajo-izquierda)
    enamel_mask = (yy >= 1126) & (xx < 1024)
    out[enamel_mask, 0] = 108.0 + brush[enamel_mask] * 0.8
    out[enamel_mask, 1] = 22.0 + brush[enamel_mask] * 0.4
    out[enamel_mask, 2] = 24.0 + brush[enamel_mask] * 0.4

    # Núcleo atómico azul-acero curado (abajo-derecha)
    core_mask = (yy >= 1126) & (xx >= 1024)
    out[core_mask, 0] = 132.0 + brush[core_mask] * 0.6
    out[core_mask, 1] = 168.0 + brush[core_mask] * 0.6
    out[core_mask, 2] = 188.0 + brush[core_mask] * 0.5

    diff_im = Image.fromarray(np.clip(out, 14.0, 224.0).astype(np.uint8))

    brass_1k_h = np.asarray(
        Image.fromarray(np.clip(brass_h2k * 20.0 + 128.0, 0, 255).astype(np.uint8), mode="L").resize((1024, 1024)),
        dtype=np.float32,
    ) / 20.0
    nx, ny = height_to_bc5_normal(brass_1k_h, strength=1.5)
    fbm_1k = tileable_fbm(1024, 1024, base_cells=8, octaves=3, persistence=0.52, seed=20770809)
    spec_r = np.clip(116.0 + (0.5 - fbm_1k) * 44.0, 76.0, 152.0)
    spec_g = np.clip(104.0 + (0.5 - fbm_1k) * 40.0, 68.0, 140.0)
    spec_r[563:, :512] = np.clip(92.0 + (0.5 - fbm_1k[563:, :512]) * 26.0, 68.0, 118.0)
    spec_g[563:, :512] = np.clip(84.0 + (0.5 - fbm_1k[563:, :512]) * 24.0, 60.0, 108.0)
    spec_r[563:, 512:] = 154.0
    spec_g[563:, 512:] = 148.0
    return diff_im, np.stack([nx, ny], axis=2), np.stack([spec_r, spec_g], axis=2)


def build_calibrated_gloves_specular(dst_path: str) -> None:
    """Extrae KnightGloves_s.dds (Fallout4 - Textures3.ba2 idx 172) y calibra el brillo satinado heroico."""
    ba2_path = os.path.join(FO4_DATA_DIR, "Fallout4 - Textures3.ba2")
    with open(ba2_path, "rb") as rf:
        _, _, _, num_files, _ = struct.unpack("<4sI4sIQ", rf.read(24))
        target_hdr = None
        target_chunks = None
        for i in range(num_files):
            hdr = struct.unpack("<I4sIBBHHHBBH", rf.read(24))
            chunks = [struct.unpack("<QIIHHI", rf.read(24)) for _ in range(hdr[4])]
            if i == 172:
                target_hdr = hdr
                target_chunks = chunks
                break
        assert target_hdr is not None and target_chunks is not None
        h, w, nmips = target_hdr[6], target_hdr[7], target_hdr[8]
        out_blobs = []
        for off, psz, usz, _, _, _ in target_chunks:
            rf.seek(off)
            raw_mip = zlib.decompress(rf.read(psz)) if psz > 0 else rf.read(usz)
            out_blobs.append(raw_mip)

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
        wf.write(b"DDS " + header + b"".join(out_blobs))


def extract_ba2_gnrl_entry(ba2_path: str, rel_target: str, dst_path: str) -> str:
    """Extrae un archivo concreto desde un archivo oficial BA2 formato GNRL (p. ej. Fallout4 - Meshes.ba2)."""
    if os.path.exists(dst_path) and os.path.getsize(dst_path) > 1024:
        return dst_path
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    key_norm = rel_target.lower().replace("/", "\\")
    with open(ba2_path, "rb") as rf:
        magic, _ver, btype, num_files, name_table_off = struct.unpack("<4sI4sIQ", rf.read(24))
        assert magic == b"BTDX" and btype == b"GNRL", f"BA2 inválido: {magic} / {btype}"
        entries = [struct.unpack("<4IQ3I", rf.read(36)) for _ in range(num_files)]
        rf.seek(name_table_off)
        target_idx = -1
        for i in range(num_files):
            nlen = struct.unpack("<H", rf.read(2))[0]
            name_str = rf.read(nlen).decode("latin1").lower().replace("/", "\\")
            if name_str == key_norm:
                target_idx = i
                break
        if target_idx < 0:
            raise FileNotFoundError(f"No se encontró {rel_target} dentro de {ba2_path}")
        _, _, _, _, offset, packed_sz, unpacked_sz, _ = entries[target_idx]
        rf.seek(offset)
        raw = zlib.decompress(rf.read(packed_sz)) if packed_sz > 0 else rf.read(unpacked_sz)
    with open(dst_path, "wb") as wf:
        wf.write(raw)
    return dst_path


def _align16(buf: bytearray, pad_byte: int = 0x00) -> int:
    rem = len(buf) % 16
    if rem:
        buf.extend(bytes([pad_byte]) * (16 - rem))
    return len(buf)


def _pack_hk_packed_vec3(v: np.ndarray, is_normal: bool = False) -> bytes:
    """Empaqueta un vector 3D en formato SIMD nativo hkPackedVector3 (8 bytes: int16[3] + uint16 exponent)."""
    if is_normal:
        nv = v / (np.linalg.norm(v) + 1e-12)
        ix = int(np.clip(round(float(nv[0]) * 32767.0), -32767, 32767))
        iy = int(np.clip(round(float(nv[1]) * 32767.0), -32767, 32767))
        iz = int(np.clip(round(float(nv[2]) * 32767.0), -32767, 32767))
        return struct.pack("<hhhH", ix, iy, iz, 0x3000)
    m = max(abs(float(v[0])), abs(float(v[1])), abs(float(v[2])), 1e-6)
    exp_p2 = int(math.ceil(math.log2(m / 32760.0)))
    e_biased = max(1, min(254, exp_p2 + 111))
    u16_exp = e_biased << 7
    scale = struct.unpack("<f", struct.pack("<I", u16_exp << 16))[0] * 65536.0
    ix = int(np.clip(round(float(v[0]) / scale), -32767, 32767))
    iy = int(np.clip(round(float(v[1]) / scale), -32767, 32767))
    iz = int(np.clip(round(float(v[2]) / scale), -32767, 32767))
    return struct.pack("<hhhH", ix, iy, iz, u16_exp)


def _quat_xyzw_from_rot_mat(r_mat: np.ndarray) -> tuple[float, float, float, float]:
    tr = float(r_mat[0, 0] + r_mat[1, 1] + r_mat[2, 2])
    if tr > 0.0:
        s = math.sqrt(tr + 1.0) * 2.0
        qw = 0.25 * s
        qx = (r_mat[2, 1] - r_mat[1, 2]) / s
        qy = (r_mat[0, 2] - r_mat[2, 0]) / s
        qz = (r_mat[1, 0] - r_mat[0, 1]) / s
    elif (r_mat[0, 0] > r_mat[1, 1]) and (r_mat[0, 0] > r_mat[2, 2]):
        s = math.sqrt(1.0 + r_mat[0, 0] - r_mat[1, 1] - r_mat[2, 2]) * 2.0
        qw = (r_mat[2, 1] - r_mat[1, 2]) / s
        qx = 0.25 * s
        qy = (r_mat[0, 1] + r_mat[1, 0]) / s
        qz = (r_mat[0, 2] + r_mat[2, 0]) / s
    elif r_mat[1, 1] > r_mat[2, 2]:
        s = math.sqrt(1.0 + r_mat[1, 1] - r_mat[0, 0] - r_mat[2, 2]) * 2.0
        qw = (r_mat[0, 2] - r_mat[2, 0]) / s
        qx = (r_mat[0, 1] + r_mat[1, 0]) / s
        qy = 0.25 * s
        qz = (r_mat[1, 2] + r_mat[2, 1]) / s
    else:
        s = math.sqrt(1.0 + r_mat[2, 2] - r_mat[0, 0] - r_mat[1, 1]) * 2.0
        qw = (r_mat[1, 0] - r_mat[0, 1]) / s
        qx = (r_mat[0, 2] + r_mat[2, 0]) / s
        qy = (r_mat[1, 2] + r_mat[2, 1]) / s
        qz = 0.25 * s
    n = math.sqrt(qx * qx + qy * qy + qz * qz + qw * qw)
    return (float(qx / n), float(qy / n), float(qz / n), float(qw / n))


def _rot_mat_from_quat_xyzw(qx: float, qy: float, qz: float, qw: float) -> np.ndarray:
    return np.array(
        [
            [1.0 - 2.0 * (qy * qy + qz * qz), 2.0 * (qx * qy - qw * qz), 2.0 * (qx * qz + qw * qy)],
            [2.0 * (qx * qy + qw * qz), 1.0 - 2.0 * (qx * qx + qz * qz), 2.0 * (qy * qz - qw * qx)],
            [2.0 * (qx * qz - qw * qy), 2.0 * (qy * qz + qw * qx), 1.0 - 2.0 * (qx * qx + qy * qy)],
        ],
        dtype=np.float64,
    )


def inject_bscloth_extradata_into_nif(nif_path: str, hkx_bytes: bytes) -> None:
    """
    Inserta binariamente un bloque BSClothExtraData (uint32 num_bytes + hkPackfile v11) en el
    nodo raíz [0] NiNode de un archivo .NIF FO4 (user_ver=12, user_ver2=130) y activa el flag
    0x0080000e (BSCloth / Skinned Outfit Root), verificando la recarga mediante nifly.dll.
    """
    if PYNIFLY_DIR not in sys.path:
        sys.path.insert(0, PYNIFLY_DIR)
    from pyn import pynifly

    with open(nif_path, "rb") as rf:
        raw = rf.read()

    nl = raw.find(b"\n")
    assert nl > 0, f"Cabecera NIF inválida en {nif_path}"
    header_prefix = raw[: nl + 1]
    pos = nl + 1
    ver, endian, user_ver, num_blocks, user_ver2 = struct.unpack_from("<IBIII", raw, pos)
    assert user_ver == 12 and user_ver2 == 130, f"Versión NIF inesperada: {user_ver}/{user_ver2}"
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

    if "BSClothExtraData" not in btypes:
        btypes.append("BSClothExtraData")
    t_cloth = btypes.index("BSClothExtraData")

    cloth_payload = struct.pack("<I", len(hkx_bytes)) + hkx_bytes
    new_cloth_idx = len(blocks)
    blocks.append(bytearray(cloth_payload))
    bsizes.append(len(cloth_payload))
    type_idxs.append(t_cloth)

    b0 = blocks[0]
    n_ex = struct.unpack_from("<I", b0, 4)[0]
    old_ctrl, old_flags = struct.unpack_from("<iI", b0, 8 + 4 * n_ex)
    new_flags = old_flags | 0x0080000E
    new_b0 = bytearray()
    new_b0.extend(b0[:4])
    new_b0.extend(struct.pack("<I", n_ex + 1))
    new_b0.extend(b0[8 : 8 + 4 * n_ex])
    new_b0.extend(struct.pack("<i", new_cloth_idx))
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

    with open(nif_path, "wb") as wf:
        wf.write(out)

    chk = pynifly.NifFile(nif_path)
    assert len(chk.cloth_data) == 1, f"nifly.dll no detectó BSClothExtraData en {nif_path}"
    print(
        f"[BSClothExtraData Injected & Verified] {os.path.basename(nif_path)} "
        f"({os.path.getsize(nif_path):,} bytes, HKX={len(hkx_bytes):,}B, shapes={[s.name for s in chk.shapes]})"
    )


def _extract_hkx_from_cloth_nif(nif_path: str) -> tuple[bytes, int, dict[int, int], list[tuple[int, str]]]:
    with open(nif_path, "rb") as rf:
        raw = rf.read()
    idx = raw.find(b"\x57\xe0\xe0\x57")
    assert idx >= 4, f"No se encontró bloque Havok hkPackfile en {nif_path}"
    sz = struct.unpack_from("<I", raw, idx - 4)[0]
    hkx = raw[idx : idx + sz]

    sec_base = hkx.find(b"__classnames__")
    sections: dict[str, tuple[int, ...]] = {}
    for s in range(3):
        so = sec_base + s * 64
        sname = hkx[so : so + 19].split(b"\x00")[0].decode("latin1")
        sections[sname] = struct.unpack_from("<7I", hkx, so + 20)

    cn_start, cn_loc = sections["__classnames__"][0], sections["__classnames__"][1]
    cls_by_off: dict[int, str] = {}
    p = cn_start
    while p < cn_start + cn_loc:
        if hkx[p] == 0xFF:
            break
        end_s = hkx.find(b"\x00", p + 5)
        cls_by_off[p + 5 - cn_start] = hkx[p + 5 : end_s].decode("latin1")
        p = end_s + 1

    d_start, d_loc, d_glob, d_virt, d_exp = sections["__data__"][:5]
    lmap: dict[int, int] = {}
    lp = d_start + d_loc
    while lp + 8 <= d_start + d_glob:
        src, dst = struct.unpack_from("<II", hkx, lp)
        if src == 0xFFFFFFFF:
            break
        lmap[src] = dst
        lp += 8

    objs: list[tuple[int, str]] = []
    vp = d_start + d_virt
    while vp + 12 <= d_start + d_exp:
        doff, _, coff = struct.unpack_from("<III", hkx, vp)
        if doff == 0xFFFFFFFF:
            break
        objs.append((doff, cls_by_off[coff]))
        vp += 12

    return hkx, d_start, lmap, objs


def build_full_cape_hkx_for_nif(suit_nif_path: str, is_female: bool = False) -> bytes:
    """
    Compila un archivo binario Havok Cloth 2014 (hk_2014.1.0-r1, hkPackfile v11) a medida para la
    capa completa del Traje de Vuelo Astro-Cosmos (CosmosHeroSuitM.nif / CosmosHeroSuitF.nif):
      - Parte del esqueleto humano 186 huesos puro del juego base (heavytorso_0[f].nif sin TempClothBone),
        preservando al 100 % las clavículas y hombros nativos de SynthUniform.
      - Añade los 25 huesos dinámicos de capa Cape_Cloth_{A..E}_{1..5} leyendo sus transformaciones
        exactas de bind mundo desde el propio .NIF exportado por Blender/nifly.dll (error < 1e-5).
      - Malla física de 9x7 = 63 partículas (96 triángulos) desde los omóplatos (Z = 108.6, anclado a
        Chest_Rear_Skin) hasta el dobladillo dorado (Z = 21.0), moviendo orgánicamente toda la capa
        incluido el emblema dorsal del Capitán Cosmos.
      - Anti-clipping doble: hclLocalRangeConstraintSet direccional (m_useMinNormal = 1) + 5 cápsulas
        de colisión (Spine2, muslos y pantorrillas) calibradas tanto para carrera en tierra como para
        vuelo horizontal estilo Superman (inclinación 70°).
    """
    if PYNIFLY_DIR not in sys.path:
        sys.path.insert(0, PYNIFLY_DIR)
    from pyn import pynifly

    meshes_ba2 = os.path.join(FO4_DATA_DIR, "Fallout4 - Meshes.ba2")
    tpl_rel = r"meshes\armor\raiderheavy02\heavytorso_0f.nif" if is_female else r"meshes\armor\raiderheavy02\heavytorso_0.nif"
    tpl_cache = os.path.join(HERO_ASSETS_DIR, "cache", os.path.basename(tpl_rel))
    if not os.path.exists(tpl_cache):
        extract_ba2_gnrl_entry(meshes_ba2, tpl_rel, tpl_cache)

    tpl_hkx, d_s, lmap, objs = _extract_hkx_from_cloth_nif(tpl_cache)
    doff_sk = [o for o, c in objs if c == "hkaSkeleton"][0]
    n_raw = struct.unpack_from("<I", tpl_hkx, d_s + doff_sk + 48)[0]
    pars_raw = struct.unpack_from(f"<{n_raw}h", tpl_hkx, d_s + lmap[doff_sk + 24])
    bones_arr = lmap[doff_sk + 40]
    pose_arr = lmap[doff_sk + 56]

    skip_idx = -1
    raw_names: list[str] = []
    for i in range(n_raw):
        nm_off = lmap[bones_arr + i * 16]
        nm = tpl_hkx[d_s + nm_off : tpl_hkx.find(b"\x00", d_s + nm_off)].decode("latin1")
        raw_names.append(nm)
        if nm == "TempClothBone":
            skip_idx = i
    assert skip_idx >= 0

    skel_names: list[str] = []
    skel_locks: list[int] = []
    skel_parents: list[int] = []
    skel_poses: list[bytes] = []
    old_to_new: dict[int, int] = {}
    for i in range(n_raw):
        if i == skip_idx:
            continue
        new_i = len(skel_names)
        old_to_new[i] = new_i
        skel_names.append(raw_names[i])
        lock_b = struct.unpack_from("<I", tpl_hkx, d_s + bones_arr + i * 16 + 8)[0]
        skel_locks.append(lock_b)
        p_old = pars_raw[i]
        skel_parents.append(-1 if p_old < 0 else old_to_new[p_old])
        skel_poses.append(tpl_hkx[d_s + pose_arr + i * 48 : d_s + pose_arr + (i + 1) * 48])

    assert len(skel_names) == 186

    world_mats: list[np.ndarray] = []
    for bi in range(186):
        tx, ty, tz, _ = struct.unpack_from("<4f", skel_poses[bi], 0)
        qx, qy, qz, qw = struct.unpack_from("<4f", skel_poses[bi], 16)
        m = np.eye(4, dtype=np.float64)
        m[:3, :3] = _rot_mat_from_quat_xyzw(qx, qy, qz, qw)
        m[:3, 3] = [tx, ty, tz]
        p_i = skel_parents[bi]
        world_mats.append(m if p_i < 0 else (world_mats[p_i] @ m))

    name_to_bi = {nm: idx for idx, nm in enumerate(skel_names)}
    bi_com = name_to_bi["COM"]
    bi_crs = name_to_bi["Chest_Rear_Skin"]
    bi_sp2 = name_to_bi["Spine2"]
    bi_sp1 = name_to_bi["Spine1"]
    bi_pel = name_to_bi["Pelvis"]

    n_rows, n_cols = 9, 7
    n_particles = n_rows * n_cols
    top_z, bot_z = 108.6, 21.0

    def cape_rest_center_y(zq: float) -> float:
        s = max(0.0, min(1.0, (109.8 - zq) / (109.8 - 21.0)))
        return -12.65 - 15.15 * (s ** 0.85)

    def cape_half_w(s_body: float) -> float:
        return 9.4 + (19.4 - 9.4) * (s_body ** 0.88)

    particles = np.zeros((n_particles, 3), dtype=np.float64)
    particle_rows: list[int] = []
    for r in range(n_rows):
        s_r = r / (n_rows - 1)
        z_r = top_z * (1.0 - s_r) + bot_z * s_r
        hw = cape_half_w(s_r)
        for c in range(n_cols):
            u = c / (n_cols - 1)
            xn = 2.0 * u - 1.0
            px = xn * hw
            py = cape_rest_center_y(z_r) + 0.45 * (xn ** 2) * (0.20 + 0.80 * s_r)
            pz = z_r - 1.8 * (1.0 - xn ** 2) * (s_r ** 2)
            pi = r * n_cols + c
            particles[pi] = [px, py, pz]
            particle_rows.append(r)

    tris: list[tuple[int, int, int]] = []
    for r in range(n_rows - 1):
        for c in range(n_cols - 1):
            p00 = r * n_cols + c
            p01 = r * n_cols + (c + 1)
            p10 = (r + 1) * n_cols + c
            p11 = (r + 1) * n_cols + (c + 1)
            cand = [(p00, p10, p11), (p00, p11, p01)] if c < (n_cols - 1) // 2 else [(p01, p10, p11), (p00, p10, p01)]
            for ia, ib, ic in cand:
                nrm = np.cross(particles[ib] - particles[ia], particles[ic] - particles[ia])
                if nrm[1] > 0.0:
                    tris.append((ia, ic, ib))
                else:
                    tris.append((ia, ib, ic))
    n_tris = len(tris)

    suit_nf = pynifly.NifFile(suit_nif_path)
    col_specs = [("A", -0.78), ("B", -0.39), ("C", 0.00), ("D", +0.39), ("E", +0.78)]
    bone_z_levels = [100.5, 83.0, 64.5, 45.5, 27.5]
    tri_centroids = np.array([(particles[a] + particles[b] + particles[c]) / 3.0 for a, b, c in tris])

    driven_bone_specs: list[tuple[int, int, np.ndarray]] = []
    for col_lbl, _xn_b in col_specs:
        prev_bi = bi_crs
        for j, _zb in enumerate(bone_z_levels, start=1):
            bname = f"Cape_Cloth_{col_lbl}_{j}"
            assert bname in suit_nf.nodes, f"No se encontró el hueso dinámico '{bname}' en {suit_nif_path}"
            xf_g = suit_nf.get_node_xform_to_global(bname)
            m_world_b = np.eye(4, dtype=np.float64)
            for r_i in range(3):
                for c_i in range(3):
                    m_world_b[r_i, c_i] = float(xf_g.rotation[r_i][c_i])
                m_world_b[r_i, 3] = float(xf_g.translation[r_i])
            b_pos = m_world_b[:3, 3]

            m_local_b = np.linalg.inv(world_mats[prev_bi]) @ m_world_b
            qx, qy, qz, qw = _quat_xyzw_from_rot_mat(m_local_b[:3, :3])
            lt = m_local_b[:3, 3]
            pose_bytes = struct.pack(
                "<12f",
                float(lt[0]), float(lt[1]), float(lt[2]), 0.0,
                qx, qy, qz, qw,
                1.0, 1.0, 1.0, 0.0,
            )

            cur_bi = len(skel_names)
            skel_names.append(bname)
            skel_locks.append(0)
            skel_parents.append(prev_bi)
            skel_poses.append(pose_bytes)
            world_mats.append(world_mats[prev_bi] @ m_local_b)
            name_to_bi[bname] = cur_bi

            dists = np.linalg.norm(tri_centroids - b_pos[None, :], axis=1)
            ti = int(np.argmin(dists))
            ia, ib, ic = tris[ti]
            pa, pb, pc = particles[ia], particles[ib], particles[ic]
            ctr = (pa + pb + pc) / 3.0
            f_tri = np.eye(4, dtype=np.float64)
            f_tri[:3, 0] = pa - ctr
            f_tri[:3, 1] = pb - ctr
            f_tri[:3, 2] = np.cross(pa - ctr, pb - ctr)
            f_tri[:3, 3] = ctr
            l_mat = np.linalg.inv(f_tri) @ world_mats[cur_bi]
            driven_bone_specs.append((cur_bi, ti, l_mat.T.astype(np.float32)))

            prev_bi = cur_bi

    n_total_bones = len(skel_names)

    capsule_defs = [
        ("Collidable_Spine2",     name_to_bi["Spine2"],     [0.0, -2.2, 104.0], [0.0, -2.2, 78.0],  9.4),
        ("Collidable_LLeg_Thigh", name_to_bi["LLeg_Thigh"], [-6.6, -0.8, 68.0], [-6.8, -0.8, 43.0], 8.0),
        ("Collidable_RLeg_Thigh", name_to_bi["RLeg_Thigh"], [ 6.6, -0.8, 68.0], [ 6.8, -0.8, 43.0], 8.0),
        ("Collidable_LLeg_Calf",  name_to_bi["LLeg_Calf"],  [-6.8, -1.2, 41.0], [-6.8, -1.8, 16.0], 7.0),
        ("Collidable_RLeg_Calf",  name_to_bi["RLeg_Calf"],  [ 6.8, -1.2, 41.0], [ 6.8, -1.8, 16.0], 7.0),
    ]
    n_collidables = len(capsule_defs)

    for cname, _cbi, ws, we, crad in capsule_defs:
        a_pt = np.array(ws, dtype=np.float64)
        b_pt = np.array(we, dtype=np.float64)
        ab = b_pt - a_pt
        ab2 = float(np.dot(ab, ab))
        for pi in range(n_cols, n_particles):
            t_proj = max(0.0, min(1.0, float(np.dot(particles[pi] - a_pt, ab)) / ab2))
            d_surf = float(np.linalg.norm(particles[pi] - (a_pt + t_proj * ab))) - crad
            assert d_surf > 1.5, f"Cápsula {cname} demasiado próxima a la partícula {pi}: {d_surf:.2f}"

    std_links: list[tuple[int, int, float, float]] = []
    stretch_links: list[tuple[int, int, float, float]] = []
    bend_links: list[tuple[int, int, float, float, float, float]] = []

    def p_dist(a: int, b: int) -> float:
        return float(np.linalg.norm(particles[a] - particles[b]))

    for r in range(n_rows):
        for c in range(n_cols):
            pi = r * n_cols + c
            if r + 1 < n_rows:
                dn = (r + 1) * n_cols + c
                d = p_dist(pi, dn)
                std_links.append((pi, dn, d, 0.95))
                stretch_links.append((pi, dn, d, 0.92))
            if r >= 1 and c + 1 < n_cols:
                rt = r * n_cols + (c + 1)
                std_links.append((pi, rt, p_dist(pi, rt), 0.88))
            if r + 1 < n_rows and c + 1 < n_cols:
                d1 = (r + 1) * n_cols + (c + 1)
                p_rt = r * n_cols + (c + 1)
                d2 = (r + 1) * n_cols + c
                std_links.append((pi, d1, p_dist(pi, d1), 0.65))
                std_links.append((p_rt, d2, p_dist(p_rt, d2), 0.65))
            if r >= 1 and c + 2 < n_cols:
                rt2 = r * n_cols + (c + 2)
                d = p_dist(pi, rt2)
                bend_links.append((pi, rt2, d * 0.88, d * 1.02, 0.26, 0.82))
            if r + 2 < n_rows:
                dn2 = (r + 2) * n_cols + c
                d = p_dist(pi, dn2)
                bend_links.append((pi, dn2, d * 0.90, d * 1.02, 0.28, 0.85))

    ref_normal = np.array([0.0, -0.985, 0.1725], dtype=np.float64)
    ref_normal /= np.linalg.norm(ref_normal)
    lrc_items: list[tuple[int, int, float, float, float]] = []
    for pi in range(n_cols, n_particles):
        r = particle_rows[pi]
        s_r = r / (n_rows - 1)
        max_dist = 3.8 + 15.2 * s_r
        max_norm = 0.85 * max_dist
        min_norm = -(1.2 + 1.8 * s_r)
        lrc_items.append((pi, pi, max_dist, max_norm, min_norm))

    skin_palette = [bi_crs, bi_sp2, bi_sp1, bi_pel]
    row_to_pal = {0: 0, 1: 0, 2: 0, 3: 1, 4: 2, 5: 3, 6: 3, 7: 3, 8: 3}
    n_one_blocks = (n_particles + 15) // 16

    class_entries = [
        (0x33D42383, "hkClass"),
        (0xB0EFA719, "hkClassMember"),
        (0x8A3609CF, "hkClassEnum"),
        (0xCE6F8A6C, "hkClassEnumItem"),
        (0x2772C11E, "hkRootLevelContainer"),
        (0xF943CEA2, "hclClothData"),
        (0xE6105187, "hclSimClothData"),
        (0xF14068BE, "hclCollidable"),
        (0xDD03F524, "hclCapsuleShape"),
        (0x426B3354, "hclStandardLinkConstraintSet"),
        (0x82567805, "hclLocalRangeConstraintSet"),
        (0x426B3354, "hclStretchLinkConstraintSet"),
        (0x26824757, "hclBendLinkConstraintSet"),
        (0x1B254CA1, "hclSimClothPose"),
        (0xA0130A2C, "hclScratchBufferDefinition"),
        (0x7F4A5BFC, "hclBufferDefinition"),
        (0x18FD4565, "hclTransformSetDefinition"),
        (0x84488B96, "hclObjectSpaceSkinPNOperator"),
        (0xE65A701C, "hclMoveParticlesOperator"),
        (0x75C72F0F, "hclSimulateOperator"),
        (0x80D9769F, "hclSimpleMeshBoneDeformOperator"),
        (0xE6DB074C, "hclCopyVerticesOperator"),
        (0x7B02CD1B, "hclClothState"),
        (0xFEC1CEDB, "hkaSkeleton"),
    ]
    cn_buf = bytearray()
    cn_offs: dict[str, int] = {}
    for sig, cname in class_entries:
        cn_buf.extend(struct.pack("<IB", sig, 0x09))
        cn_offs[cname] = len(cn_buf)
        cn_buf.extend(cname.encode("ascii") + b"\x00")
    assert cn_offs["hkRootLevelContainer"] == 0x4B
    _align16(cn_buf, 0xFF)

    data_buf = bytearray()
    local_fixups: list[tuple[int, int]] = []
    global_fixups: list[tuple[int, int, str]] = []
    virt_fixups: list[tuple[int, str]] = []
    obj_offsets: dict[str, int] = {}

    def start_obj(label: str, cname: str) -> int:
        _align16(data_buf, 0x00)
        off = len(data_buf)
        obj_offsets[label] = off
        virt_fixups.append((off, cname))
        return off

    def put_local(src_off: int, dst_off: int) -> None:
        local_fixups.append((src_off, dst_off))

    def put_global(src_off: int, target_label: str) -> None:
        global_fixups.append((src_off, 2, target_label))

    def write_cstr_aligned(s: str) -> int:
        _align16(data_buf, 0x00)
        off = len(data_buf)
        data_buf.extend(s.encode("ascii") + b"\x00")
        _align16(data_buf, 0x00)
        return off

    def pack_hkarray_hdr(buf: bytearray, rel_off: int, count: int) -> None:
        cap = (0x80000000 | count) if count > 0 else 0x80000000
        struct.pack_into("<QII", buf, rel_off, 0, count, cap)

    o_root = start_obj("root", "hkRootLevelContainer")
    hdr = bytearray(16)
    pack_hkarray_hdr(hdr, 0, 2)
    data_buf.extend(hdr)
    arr_variants = _align16(data_buf)
    put_local(o_root + 0, arr_variants)
    data_buf.extend(b"\x00" * 48)
    put_global(arr_variants + 16, "cloth_data")
    put_global(arr_variants + 40, "skeleton")
    s1 = write_cstr_aligned("hclClothData")
    put_local(arr_variants + 0, s1)
    put_local(arr_variants + 8, s1)
    s2 = write_cstr_aligned("hkaSkeleton")
    put_local(arr_variants + 24, s2)
    put_local(arr_variants + 32, s2)

    o_cd = start_obj("cloth_data", "hclClothData")
    hdr = bytearray(0x80)
    pack_hkarray_hdr(hdr, 0x18, 1)
    pack_hkarray_hdr(hdr, 0x28, 2)
    pack_hkarray_hdr(hdr, 0x38, 1)
    pack_hkarray_hdr(hdr, 0x48, 5)
    pack_hkarray_hdr(hdr, 0x58, 2)
    pack_hkarray_hdr(hdr, 0x68, 0)
    struct.pack_into("<I", hdr, 0x78, 2)
    data_buf.extend(hdr)
    put_local(o_cd + 0x10, write_cstr_aligned("Character Bone Deforming Clothing"))

    p_sim_arr = _align16(data_buf); data_buf.extend(b"\x00" * 16); put_local(o_cd + 0x18, p_sim_arr)
    put_global(p_sim_arr, "sim_cloth")
    p_buf_arr = _align16(data_buf); data_buf.extend(b"\x00" * 16); put_local(o_cd + 0x28, p_buf_arr)
    put_global(p_buf_arr + 0, "scratch_buf")
    put_global(p_buf_arr + 8, "sim_buf")
    p_ts_arr = _align16(data_buf); data_buf.extend(b"\x00" * 16); put_local(o_cd + 0x38, p_ts_arr)
    put_global(p_ts_arr, "transform_set")
    p_op_arr = _align16(data_buf); data_buf.extend(b"\x00" * 48); put_local(o_cd + 0x48, p_op_arr)
    for k, lbl in enumerate(["op_skin", "op_move", "op_sim", "op_deform", "op_copy"]):
        put_global(p_op_arr + k * 8, lbl)
    p_st_arr = _align16(data_buf); data_buf.extend(b"\x00" * 16); put_local(o_cd + 0x58, p_st_arr)
    put_global(p_st_arr + 0, "state_sim")
    put_global(p_st_arr + 8, "state_anim")

    o_scd = start_obj("sim_cloth", "hclSimClothData")
    hdr = bytearray(0x180)
    struct.pack_into("<ffff", hdr, 0x10, 0.0, 0.0, -280.0, 1.0)
    struct.pack_into("<ffII", hdr, 0x20, 0.94, 13.99825, 0, 0x00010000)
    n_fixed = n_cols
    n_free = n_particles - n_fixed
    n_flips = (n_tris + 7) // 8
    pack_hkarray_hdr(hdr, 0x38, n_particles)
    pack_hkarray_hdr(hdr, 0x48, n_fixed)
    pack_hkarray_hdr(hdr, 0x58, n_tris * 3)
    pack_hkarray_hdr(hdr, 0x68, n_flips)
    total_mass = sum(1.30 - 0.45 * (particle_rows[pi] / (n_rows - 1)) for pi in range(n_fixed, n_particles))
    struct.pack_into("<fI", hdr, 0x78, float(total_mass), 0)
    pack_hkarray_hdr(hdr, 0x88, n_collidables)
    pack_hkarray_hdr(hdr, 0x98, n_collidables)
    pack_hkarray_hdr(hdr, 0xA8, n_collidables)
    pack_hkarray_hdr(hdr, 0xB8, 4)
    pack_hkarray_hdr(hdr, 0xC8, 0)
    pack_hkarray_hdr(hdr, 0xD8, 1)
    pack_hkarray_hdr(hdr, 0xE8, 0)
    pack_hkarray_hdr(hdr, 0xF8, n_particles)
    pack_hkarray_hdr(hdr, 0x108, n_particles)
    pack_hkarray_hdr(hdr, 0x118, n_collidables)
    struct.pack_into("<IIff", hdr, 0x128, 1, n_free * n_collidables, 1.0, 0.05)
    struct.pack_into("<ff", hdr, 0x138, 0.0, 9.0)
    struct.pack_into("<IIII", hdr, 0x140, 0, 0, 0, 1)
    struct.pack_into("<I", hdr, 0x150, 0)
    struct.pack_into(
        "<IIffffIffff",
        hdr,
        0x154,
        bi_com,
        1,
        15.0,
        850.0,
        0.68,
        0.86,
        1,
        35.0,
        180.0,
        0.20,
        0.55,
    )
    data_buf.extend(hdr)
    put_local(o_scd + 0x30, write_cstr_aligned("Simulation Cloth"))

    p_pdatas = _align16(data_buf); put_local(o_scd + 0x38, p_pdatas)
    for pi in range(n_particles):
        if pi < n_fixed:
            data_buf.extend(struct.pack("<ffff", 0.0, 0.0, 0.25, 0.15))
        else:
            s_r = particle_rows[pi] / (n_rows - 1)
            m_val = 1.30 - 0.45 * s_r
            data_buf.extend(struct.pack("<ffff", float(m_val), float(1.0 / m_val), 0.45, 0.10))
    _align16(data_buf)

    p_fixed = _align16(data_buf); put_local(o_scd + 0x48, p_fixed)
    for pi in range(n_fixed):
        data_buf.extend(struct.pack("<H", pi))
    _align16(data_buf)

    p_tris = _align16(data_buf); put_local(o_scd + 0x58, p_tris)
    for ia, ib, ic in tris:
        data_buf.extend(struct.pack("<HHH", ia, ib, ic))
    _align16(data_buf)

    p_flips = _align16(data_buf); put_local(o_scd + 0x68, p_flips)
    data_buf.extend(b"\x00" * n_flips)
    _align16(data_buf)

    p_col_tis = _align16(data_buf); put_local(o_scd + 0x88, p_col_tis)
    for _, cbi, _, _, _ in capsule_defs:
        data_buf.extend(struct.pack("<I", cbi))
    _align16(data_buf)

    p_col_offs = _align16(data_buf); put_local(o_scd + 0x98, p_col_offs)
    ident_colmajor = np.eye(4, dtype=np.float32).tobytes()
    for _ in range(n_collidables):
        data_buf.extend(ident_colmajor)
    _align16(data_buf)

    p_col_ptrs = _align16(data_buf); put_local(o_scd + 0xA8, p_col_ptrs)
    data_buf.extend(b"\x00" * (8 * n_collidables))
    for ci in range(n_collidables):
        put_global(p_col_ptrs + ci * 8, f"collidable_{ci}")
    _align16(data_buf)

    p_csets = _align16(data_buf); put_local(o_scd + 0xB8, p_csets)
    data_buf.extend(b"\x00" * (8 * 4))
    for ci, clbl in enumerate(["cs_std", "cs_lrc", "cs_stretch", "cs_bend"]):
        put_global(p_csets + ci * 8, clbl)
    _align16(data_buf)

    p_poses = _align16(data_buf); put_local(o_scd + 0xD8, p_poses)
    data_buf.extend(b"\x00" * 16)
    put_global(p_poses, "cloth_pose")

    p_pmask = _align16(data_buf); put_local(o_scd + 0xF8, p_pmask)
    col_bitmask = (1 << n_collidables) - 1
    for pi in range(n_particles):
        data_buf.extend(struct.pack("<I", 0 if pi < n_fixed else col_bitmask))
    _align16(data_buf)

    p_pinch1 = _align16(data_buf); put_local(o_scd + 0x108, p_pinch1)
    data_buf.extend(b"\x00" * n_particles)
    _align16(data_buf)

    p_pinch2 = _align16(data_buf); put_local(o_scd + 0x118, p_pinch2)
    for _ in range(n_collidables):
        data_buf.extend(struct.pack("<If", 0, 0.01))
    _align16(data_buf)

    for ci, (cname, cbi, ws, we, crad) in enumerate(capsule_defs):
        o_col = start_obj(f"collidable_{ci}", "hclCollidable")
        chdr = bytearray(0x90)
        chdr[0x20:0x60] = world_mats[cbi].T.astype(np.float32).tobytes()
        struct.pack_into("<If", chdr, 0x80, 0, 0.01)
        data_buf.extend(chdr)
        put_global(o_col + 0x88, f"capsule_{ci}")
        put_local(o_col + 0x10, write_cstr_aligned(cname))

        inv_b = np.linalg.inv(world_mats[cbi])
        ls = (inv_b @ np.array([ws[0], ws[1], ws[2], 1.0], dtype=np.float64))[:3]
        le = (inv_b @ np.array([we[0], we[1], we[2], 1.0], dtype=np.float64))[:3]
        ldiff = le - ls
        llen = float(np.linalg.norm(ldiff))
        ldir = ldiff / llen
        o_cap = start_obj(f"capsule_{ci}", "hclCapsuleShape")
        cap_hdr = bytearray(0x60)
        struct.pack_into("<4f", cap_hdr, 0x20, float(ls[0]), float(ls[1]), float(ls[2]), 0.0)
        struct.pack_into("<4f", cap_hdr, 0x30, float(le[0]), float(le[1]), float(le[2]), 0.0)
        struct.pack_into("<4f", cap_hdr, 0x40, float(ldir[0]), float(ldir[1]), float(ldir[2]), 0.0)
        struct.pack_into("<4f", cap_hdr, 0x50, float(crad), float(1.0 / (llen * llen)), 0.0, 0.0)
        data_buf.extend(cap_hdr)

    o_std = start_obj("cs_std", "hclStandardLinkConstraintSet")
    shdr = bytearray(0x30)
    pack_hkarray_hdr(shdr, 0x20, len(std_links))
    data_buf.extend(shdr)
    put_local(o_std + 0x10, write_cstr_aligned("standardLinks"))
    p_std_arr = _align16(data_buf); put_local(o_std + 0x20, p_std_arr)
    for pa, pb, rlen, stiff in std_links:
        data_buf.extend(struct.pack("<HHff", pa, pb, rlen, stiff))
    _align16(data_buf)

    o_lrc = start_obj("cs_lrc", "hclLocalRangeConstraintSet")
    lhdr = bytearray(0x40)
    pack_hkarray_hdr(lhdr, 0x20, len(lrc_items))
    struct.pack_into("<ffIBBBB", lhdr, 0x30, 0.0, 0.95, 0, 1, 0, 0, 0)
    data_buf.extend(lhdr)
    put_local(o_lrc + 0x10, write_cstr_aligned("distanceConstraint"))
    p_lrc_arr = _align16(data_buf); put_local(o_lrc + 0x20, p_lrc_arr)
    for pidx, rvidx, max_d, max_n, min_n in lrc_items:
        data_buf.extend(struct.pack("<HHfff", pidx, rvidx, max_d, max_n, min_n))
    _align16(data_buf)

    o_str = start_obj("cs_stretch", "hclStretchLinkConstraintSet")
    sthdr = bytearray(0x30)
    pack_hkarray_hdr(sthdr, 0x20, len(stretch_links))
    data_buf.extend(sthdr)
    put_local(o_str + 0x10, write_cstr_aligned("stretchLinks"))
    p_str_arr = _align16(data_buf); put_local(o_str + 0x20, p_str_arr)
    for pa, pb, rlen, stiff in stretch_links:
        data_buf.extend(struct.pack("<HHff", pa, pb, rlen, stiff))
    _align16(data_buf)

    o_bnd = start_obj("cs_bend", "hclBendLinkConstraintSet")
    bhdr = bytearray(0x30)
    pack_hkarray_hdr(bhdr, 0x20, len(bend_links))
    data_buf.extend(bhdr)
    put_local(o_bnd + 0x10, write_cstr_aligned("Bend Links"))
    p_bnd_arr = _align16(data_buf); put_local(o_bnd + 0x20, p_bnd_arr)
    for pa, pb, min_l, max_l, bstiff, sstiff in bend_links:
        data_buf.extend(struct.pack("<HHffff", pa, pb, min_l, max_l, bstiff, sstiff))
    _align16(data_buf)

    o_pose = start_obj("cloth_pose", "hclSimClothPose")
    phdr = bytearray(0x30)
    pack_hkarray_hdr(phdr, 0x18, n_particles)
    data_buf.extend(phdr)
    put_local(o_pose + 0x10, write_cstr_aligned("DefaultClothPose"))
    p_pose_pts = _align16(data_buf); put_local(o_pose + 0x18, p_pose_pts)
    for pi in range(n_particles):
        px, py, pz = particles[pi]
        data_buf.extend(struct.pack("<ffff", float(px), float(py), float(pz), 1.0))
    _align16(data_buf)

    o_sbuf = start_obj("scratch_buf", "hclScratchBufferDefinition")
    sbhdr = bytearray(0x60)
    struct.pack_into("<IIIIIIIII", sbhdr, 0x18, 6, 0, n_particles, 0, 4096, 69632, 250, 250, 0x10011001)
    struct.pack_into("<II", sbhdr, 0x40, 0x0202, 0)
    pack_hkarray_hdr(sbhdr, 0x48, 0)
    struct.pack_into("<I", sbhdr, 0x58, 1)
    data_buf.extend(sbhdr)
    put_local(o_sbuf + 0x10, write_cstr_aligned("Sim_Mesh"))

    o_buf = start_obj("sim_buf", "hclBufferDefinition")
    bfhdr = bytearray(0x50)
    struct.pack_into("<IIIIIIIII", bfhdr, 0x18, 1, 0, n_particles, n_tris, 4096, 69632, 250, 250, 0x10011001)
    struct.pack_into("<II", bfhdr, 0x40, 0x0102, 0)
    data_buf.extend(bfhdr)
    put_local(o_buf + 0x10, write_cstr_aligned("SimBuf"))

    o_ts = start_obj("transform_set", "hclTransformSetDefinition")
    tshdr = bytearray(0x20)
    struct.pack_into("<II", tshdr, 0x18, 1, n_total_bones)
    data_buf.extend(tshdr)
    put_local(o_ts + 0x10, write_cstr_aligned("Root Transforms"))

    o_skin = start_obj("op_skin", "hclObjectSpaceSkinPNOperator")
    skhdr = bytearray(0xC0)
    pack_hkarray_hdr(skhdr, 0x20, len(skin_palette))
    pack_hkarray_hdr(skhdr, 0x30, len(skin_palette))
    struct.pack_into("<II", skhdr, 0x40, 0, 0)
    for empty_off in (0x48, 0x58, 0x68, 0xB0):
        pack_hkarray_hdr(skhdr, empty_off, 0)
    pack_hkarray_hdr(skhdr, 0x78, n_one_blocks)
    pack_hkarray_hdr(skhdr, 0x88, n_one_blocks)
    struct.pack_into("<HHI", skhdr, 0x98, 0, n_particles - 1, 0x200)
    pack_hkarray_hdr(skhdr, 0xA0, n_one_blocks)
    data_buf.extend(skhdr)
    put_local(o_skin + 0x10, write_cstr_aligned("Skin Simulation"))

    p_b2s = _align16(data_buf); put_local(o_skin + 0x20, p_b2s)
    for bi in skin_palette:
        data_buf.extend(np.linalg.inv(world_mats[bi]).T.astype(np.float32).tobytes())
    _align16(data_buf)

    p_tsub = _align16(data_buf); put_local(o_skin + 0x30, p_tsub)
    for bi in skin_palette:
        data_buf.extend(struct.pack("<H", bi))
    _align16(data_buf)

    p_one = _align16(data_buf); put_local(o_skin + 0x78, p_one)
    for blk in range(n_one_blocks):
        v_list = [min(n_particles - 1, blk * 16 + j) for j in range(16)]
        m_list = [row_to_pal[particle_rows[vi]] for vi in v_list]
        data_buf.extend(struct.pack("<16H", *v_list))
        data_buf.extend(struct.pack("<16H", *m_list))
    _align16(data_buf)

    p_ctrl = _align16(data_buf); put_local(o_skin + 0x88, p_ctrl)
    data_buf.extend(bytes([3] * n_one_blocks))
    _align16(data_buf)

    p_pns = _align16(data_buf); put_local(o_skin + 0xA0, p_pns)
    packed_norm = _pack_hk_packed_vec3(ref_normal, is_normal=True)
    for blk in range(n_one_blocks):
        for j in range(16):
            vi = min(n_particles - 1, blk * 16 + j)
            data_buf.extend(_pack_hk_packed_vec3(particles[vi], is_normal=False))
        for _ in range(16):
            data_buf.extend(packed_norm)
    _align16(data_buf)

    o_move = start_obj("op_move", "hclMoveParticlesOperator")
    mvhdr = bytearray(0x40)
    pack_hkarray_hdr(mvhdr, 0x20, n_fixed)
    struct.pack_into("<II", mvhdr, 0x30, 0, 0)
    data_buf.extend(mvhdr)
    put_local(o_move + 0x10, write_cstr_aligned("Move Particles"))
    p_mv_arr = _align16(data_buf); put_local(o_move + 0x20, p_mv_arr)
    for pi in range(n_fixed):
        data_buf.extend(struct.pack("<HH", pi, pi))
    _align16(data_buf)

    o_sim = start_obj("op_sim", "hclSimulateOperator")
    smhdr = bytearray(0x50)
    struct.pack_into("<IIII", smhdr, 0x20, 0, 2, 1, 0)
    pack_hkarray_hdr(smhdr, 0x30, 5)
    data_buf.extend(smhdr)
    put_local(o_sim + 0x10, write_cstr_aligned("Sim"))
    p_ce_arr = _align16(data_buf); put_local(o_sim + 0x30, p_ce_arr)
    data_buf.extend(struct.pack("<5i", 0, 1, 2, 3, -1))
    _align16(data_buf)

    o_def = start_obj("op_deform", "hclSimpleMeshBoneDeformOperator")
    dfhdr = bytearray(0x50)
    struct.pack_into("<II", dfhdr, 0x20, 1, 0)
    n_driven = len(driven_bone_specs)
    pack_hkarray_hdr(dfhdr, 0x28, n_driven)
    pack_hkarray_hdr(dfhdr, 0x38, n_driven)
    data_buf.extend(dfhdr)
    put_local(o_def + 0x10, write_cstr_aligned("Deform"))
    p_df_map = _align16(data_buf); put_local(o_def + 0x28, p_df_map)
    for cbi, ti, _ in driven_bone_specs:
        data_buf.extend(struct.pack("<HH", cbi * 64, ti * 6))
    _align16(data_buf)
    p_df_xf = _align16(data_buf); put_local(o_def + 0x38, p_df_xf)
    for _, _, lmat_cm in driven_bone_specs:
        data_buf.extend(lmat_cm.tobytes())
    _align16(data_buf)

    o_cpy = start_obj("op_copy", "hclCopyVerticesOperator")
    cphdr = bytearray(0x40)
    struct.pack_into("<IIIIII", cphdr, 0x20, 0, 1, n_particles, 0, 0, 1)
    data_buf.extend(cphdr)
    put_local(o_cpy + 0x10, write_cstr_aligned("VertGather Op"))

    def write_cloth_state(
        lbl: str,
        st_name: str,
        op_indices: list[int],
        buf_access0: int,
        buf_access1: int,
        read_bones: set[int],
        write_bones: set[int],
    ) -> None:
        o_st = start_obj(lbl, "hclClothState")
        st_hdr = bytearray(0x60)
        pack_hkarray_hdr(st_hdr, 0x18, len(op_indices))
        pack_hkarray_hdr(st_hdr, 0x28, 2)
        pack_hkarray_hdr(st_hdr, 0x38, 1)
        pack_hkarray_hdr(st_hdr, 0x48, 1)
        data_buf.extend(st_hdr)
        put_local(o_st + 0x10, write_cstr_aligned(st_name))

        p_ops = _align16(data_buf); put_local(o_st + 0x18, p_ops)
        for oi in op_indices:
            data_buf.extend(struct.pack("<I", oi))
        _align16(data_buf)

        p_ba = _align16(data_buf); put_local(o_st + 0x28, p_ba)
        data_buf.extend(struct.pack("<IIII", 0, buf_access0, 0, 0))
        data_buf.extend(struct.pack("<IIII", 1, buf_access1, 1, 1))
        _align16(data_buf)

        p_tsa = _align16(data_buf); put_local(o_st + 0x38, p_tsa)
        n_words = (n_total_bones + 31) // 32
        tsa_hdr = bytearray(0xB0)
        struct.pack_into("<III", tsa_hdr, 0x00, 0, 0, 0x0B)
        pack_hkarray_hdr(tsa_hdr, 0x10, 2)
        for bf_i in range(6):
            off_bf = 0x20 + bf_i * 0x18
            pack_hkarray_hdr(tsa_hdr, off_bf, n_words)
            struct.pack_into("<II", tsa_hdr, off_bf + 0x10, n_total_bones, 0)
        data_buf.extend(tsa_hdr)
        put_local(p_tsa + 0x10, p_tsa + 0x20)

        for bf_i, bset in enumerate([read_bones, read_bones, write_bones, set(), set(), set()]):
            p_w = _align16(data_buf)
            put_local(p_tsa + 0x20 + bf_i * 0x18, p_w)
            words = [0] * n_words
            for bi in bset:
                words[bi // 32] |= 1 << (bi % 32)
            data_buf.extend(struct.pack(f"<{n_words}I", *words))
            _align16(data_buf)

        p_usc = _align16(data_buf); put_local(o_st + 0x48, p_usc)
        data_buf.extend(struct.pack("<I", 0))
        _align16(data_buf)

    sim_read = set(skin_palette) | {bi_com} | {cbi for _, cbi, _, _, _ in capsule_defs}
    anim_read = set(skin_palette)
    driven_set = {cbi for cbi, _, _ in driven_bone_specs}

    write_cloth_state("state_sim", "Simulate", [0, 1, 2, 3], 0x0607, 0x0009, sim_read, driven_set)
    write_cloth_state("state_anim", "Animate", [0, 4, 3],    0x0707, 0x0607, anim_read, driven_set)

    o_skel = start_obj("skeleton", "hkaSkeleton")
    sk_hdr = bytearray(0x90)
    pack_hkarray_hdr(sk_hdr, 0x18, n_total_bones)
    pack_hkarray_hdr(sk_hdr, 0x28, n_total_bones)
    pack_hkarray_hdr(sk_hdr, 0x38, n_total_bones)
    for empty_off in (0x48, 0x58, 0x68, 0x78):
        pack_hkarray_hdr(sk_hdr, empty_off, 0)
    data_buf.extend(sk_hdr)
    put_local(o_skel + 0x10, write_cstr_aligned("Root"))

    p_pars = _align16(data_buf); put_local(o_skel + 0x18, p_pars)
    data_buf.extend(struct.pack(f"<{n_total_bones}h", *skel_parents))
    _align16(data_buf)

    p_bones = _align16(data_buf); put_local(o_skel + 0x28, p_bones)
    data_buf.extend(b"\x00" * (16 * n_total_bones))
    for bi, lock_v in enumerate(skel_locks):
        struct.pack_into("<I", data_buf, p_bones + bi * 16 + 8, lock_v)
    _align16(data_buf)

    p_rpose = _align16(data_buf); put_local(o_skel + 0x38, p_rpose)
    for pb in skel_poses:
        data_buf.extend(pb)
    _align16(data_buf)

    for bi, bnm in enumerate(skel_names):
        s_off = write_cstr_aligned(bnm)
        put_local(p_bones + bi * 16, s_off)

    d_loc_off = _align16(data_buf)
    loc_buf = bytearray()
    for src_o, dst_o in local_fixups:
        loc_buf.extend(struct.pack("<II", src_o, dst_o))
    _align16(loc_buf, 0xFF)

    d_glob_off = d_loc_off + len(loc_buf)
    glob_buf = bytearray()
    for src_o, sec_i, tgt_lbl in global_fixups:
        glob_buf.extend(struct.pack("<III", src_o, sec_i, obj_offsets[tgt_lbl]))
    _align16(glob_buf, 0xFF)

    d_virt_off = d_glob_off + len(glob_buf)
    virt_buf = bytearray()
    for obj_o, cname in virt_fixups:
        virt_buf.extend(struct.pack("<III", obj_o, 0, cn_offs[cname]))
    _align16(virt_buf, 0xFF)

    d_end_off = d_virt_off + len(virt_buf)

    file_hdr = bytes.fromhex(
        "57e0e05710c0c010000000000b00000008010001030000000200000000000000"
        "000000004b000000686b5f323031342e312e302d723100ff0000000015001000"
        "14000000000000000000000000000000"
    )

    def make_sec_hdr(name: str, abs_start: int, o1: int, o2: int, o3: int, o4: int, o5: int, o6: int) -> bytes:
        nb = name.encode("ascii")
        pad = nb + b"\x00" * (19 - len(nb)) + b"\xff"
        return pad + struct.pack("<7I", abs_start, o1, o2, o3, o4, o5, o6) + b"\xff" * 16

    cn_start_abs = 0x110
    cn_len = len(cn_buf)
    d_start_abs = cn_start_abs + cn_len

    sec0 = make_sec_hdr("__classnames__", cn_start_abs, cn_len, cn_len, cn_len, cn_len, cn_len, cn_len)
    sec1 = make_sec_hdr("__types__", d_start_abs, 0, 0, 0, 0, 0, 0)
    sec2 = make_sec_hdr("__data__", d_start_abs, d_loc_off, d_glob_off, d_virt_off, d_end_off, d_end_off, d_end_off)

    full_hkx = bytes(file_hdr + sec0 + sec1 + sec2 + cn_buf + data_buf + loc_buf + glob_buf + virt_buf)
    assert len(full_hkx) % 16 == 0
    return full_hkx


# ==============================================================================
# 3. SCRIPT BLENDER 5.2 + PYNIFLY 30.2.0: ESCULPIDO 3D DEL TRAJE Y CAPA FÍSICA
# ==============================================================================
BLENDER_HERO_SCRIPT = r'''
import json
import math
import os
import sys
from collections import defaultdict, deque
import bpy
import bmesh
from mathutils import Vector
from mathutils.kdtree import KDTree

TEST_DIR = r"__TEST_DIR__"
PREVIEW_CAPE_JSON = r"__PREVIEW_CAPE_JSON__"
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


def filter_mesh_islands(mesh_obj, keep_predicate):
    bm = bmesh.new()
    bm.from_mesh(mesh_obj.data)
    bm.verts.ensure_lookup_table()
    visited = set()
    to_delete = []
    for v in bm.verts:
        if v.index in visited:
            continue
        q = deque([v])
        visited.add(v.index)
        comp = []
        while q:
            cur = q.popleft()
            comp.append(cur)
            for e in cur.link_edges:
                nb = e.other_vert(cur)
                if nb.index not in visited:
                    visited.add(nb.index)
                    q.append(nb)
        coords = [mesh_obj.matrix_world @ cv.co for cv in comp]
        if not keep_predicate(coords, len(comp)):
            to_delete.extend(comp)
    if to_delete:
        bmesh.ops.delete(bm, geom=to_delete, context="VERTS")
        bm.to_mesh(mesh_obj.data)
        mesh_obj.data.update()
    bm.free()


def seam_aware_smooth(mesh_obj, region_predicate, iterations: int = 20, factor: float = 0.60):
    bm = bmesh.new()
    bm.from_mesh(mesh_obj.data)
    bm.verts.ensure_lookup_table()
    pos_groups = defaultdict(list)
    for v in bm.verts:
        wco = mesh_obj.matrix_world @ v.co
        key = (round(wco.x, 3), round(wco.y, 3), round(wco.z, 3))
        pos_groups[key].append(v.index)
    target_keys = set()
    for key, idxs in pos_groups.items():
        wco = Vector(key)
        if region_predicate(wco):
            target_keys.add(key)
    welded_adj = defaultdict(set)
    vert_to_key = {}
    for key, idxs in pos_groups.items():
        for vi in idxs:
            vert_to_key[vi] = key
    for e in bm.edges:
        k1 = vert_to_key[e.verts[0].index]
        k2 = vert_to_key[e.verts[1].index]
        if k1 != k2:
            welded_adj[k1].add(k2)
            welded_adj[k2].add(k1)
    key_pos = {k: Vector(k) for k in pos_groups}
    mw_inv = mesh_obj.matrix_world.inverted()
    for _ in range(iterations):
        new_pos = {}
        for k in target_keys:
            nbs = welded_adj[k]
            if not nbs:
                continue
            avg = Vector((0.0, 0.0, 0.0))
            for nk in nbs:
                avg += key_pos[nk]
            avg /= len(nbs)
            new_pos[k] = key_pos[k].lerp(avg, factor)
        for k, npv in new_pos.items():
            key_pos[k] = npv
    for k in target_keys:
        local_co = mw_inv @ key_pos[k]
        for vi in pos_groups[k]:
            bm.verts[vi].co = local_co
    bm.normal_update()
    bm.to_mesh(mesh_obj.data)
    mesh_obj.data.update()
    bm.free()


def assign_shader_on_material(
    mat,
    bgsm_rel: str,
    diff_dds: str,
    norm_dds: str,
    spec_dds: str,
    env_dds: str = r"textures\Shared\Cubemaps\mipblur_InstInterior.dds",
):
    mat["BS_Shader_Block_Name"] = "BSLightingShaderProperty"
    mat["BSLSP_Shader_Name"] = bgsm_rel
    mat["BSShaderTextureSet_Diffuse"] = diff_dds
    mat["BSShaderTextureSet_Normal"] = norm_dds
    mat["BSShaderTextureSet_Specular"] = spec_dds
    mat["BSShaderTextureSet_EnvMap"] = env_dds
    for k in [
        "NiAlphaProperty_flags",
        "NiAlphaProperty_threshold",
        "BSShaderTextureSet_EnvMapMask",
        "BSLSP_Shader_Type",
        "pyn_synthetic_alpha_from_bgsm",
    ]:
        if k in mat:
            del mat[k]
    if hasattr(mat, "pyn_shader"):
        mat.pyn_shader.Shader_Type = ""
    if mat.node_tree:
        for n in mat.node_tree.nodes:
            if n.bl_idname == "ShaderNodeTexImage":
                n.image = None
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf and "Alpha" in bsdf.inputs:
            for l in list(bsdf.inputs["Alpha"].links):
                mat.node_tree.links.remove(l)
            bsdf.inputs["Alpha"].default_value = 1.0


def build_surface_sampler(suit_obj):
    """Construye un KDTree y muestreador de superficie (frontal +Y, dorsal -Y y radial cintura) sobre el traje base."""
    me = suit_obj.data
    verts_w = [suit_obj.matrix_world @ v.co for v in me.vertices]
    kd = KDTree(len(verts_w))
    for i, co in enumerate(verts_w):
        kd.insert(co, i)
    kd.balance()

    # Índices de grupos de huesos reales (excluyendo FO4 Seg *)
    bone_vgs = {vg.index: vg.name for vg in suit_obj.vertex_groups if "Seg" not in vg.name}
    vert_weights = []
    for v in me.vertices:
        d = {}
        for g in v.groups:
            if g.group in bone_vgs and g.weight > 0.001:
                d[bone_vgs[g.group]] = g.weight
        vert_weights.append(d)

    def front_y(x: float, z: float) -> float:
        # Buscar los vértices frontales (y > 0) más cercanos en (x, z)
        best_num = 0.0
        best_den = 0.0
        for co, idx, _ in kd.find_n(Vector((x, 8.5, z)), 18):
            if co.y > 0.0:
                d2 = (co.x - x) ** 2 + (co.z - z) ** 2 + 0.35
                w = 1.0 / (d2 * d2)
                best_num += co.y * w
                best_den += w
        return (best_num / best_den) if best_den > 0 else 8.5

    def back_y(x: float, z: float) -> float:
        best_num = 0.0
        best_den = 0.0
        for co, idx, _ in kd.find_n(Vector((x, -9.5, z)), 18):
            if co.y < 0.0:
                d2 = (co.x - x) ** 2 + (co.z - z) ** 2 + 0.35
                w = 1.0 / (d2 * d2)
                best_num += co.y * w
                best_den += w
        return (best_num / best_den) if best_den > 0 else -9.5

    def waist_ring_point(theta: float, z: float) -> Vector:
        # Dirección radial en el plano XY alrededor del eje de cintura (0, 0, z)
        dx = math.cos(theta)
        dy = math.sin(theta)
        probe = Vector((dx * 11.0, dy * 9.5, z))
        best_r = 0.0
        best_den = 0.0
        for co, idx, _ in kd.find_n(probe, 14):
            ang = math.atan2(co.y, co.x)
            da = abs((ang - theta + math.pi) % (2.0 * math.pi) - math.pi)
            dz = abs(co.z - z)
            if da < 0.45 and dz < 4.5:
                r = math.hypot(co.x, co.y)
                w = 1.0 / (da * da * 12.0 + dz * dz * 0.25 + 0.08)
                best_r += r * w
                best_den += w
        r_surf = (best_r / best_den) if best_den > 0 else 9.5
        return Vector((dx * r_surf, dy * r_surf, z))

    def sample_bone_weights(pt: Vector, k: int = 5) -> dict:
        acc = defaultdict(float)
        wsum = 0.0
        for co, idx, dist in kd.find_n(pt, k):
            inv = 1.0 / (dist + 0.15)
            for bname, bw in vert_weights[idx].items():
                acc[bname] += bw * inv
            wsum += inv
        if not acc:
            return {"SPINE2": 1.0}
        # Limitar a los 4 huesos principales y normalizar a 1.0
        top4 = sorted(acc.items(), key=lambda kv: kv[1], reverse=True)[:4]
        tot = sum(v for _, v in top4)
        return {bn: v / tot for bn, v in top4}

    return front_y, back_y, waist_ring_point, sample_bone_weights


def apply_weights_and_torso_seg(obj, arm_obj, per_vert_weights: list[dict], root_obj=None):
    obj.parent = root_obj if root_obj is not None else arm_obj
    mod = obj.modifiers.new(name="Armature", type="ARMATURE")
    mod.object = arm_obj

    vg_map = {}
    for wdict in per_vert_weights:
        for bname in wdict:
            if bname not in vg_map:
                vg_map[bname] = obj.vertex_groups.new(name=bname)

    for vi, wdict in enumerate(per_vert_weights):
        top4 = sorted(wdict.items(), key=lambda kv: kv[1], reverse=True)[:4]
        tot = sum(v for _, v in top4)
        if tot <= 1e-6:
            top4 = [("SPINE2", 1.0)]
            tot = 1.0
        for bname, w in top4:
            vg_map[bname].add([vi], float(w / tot), "REPLACE")

    # Segmentos FO4 idénticos a VaultNumber:0 (100% en FO4 Seg 003 = Torso)
    for seg_name in ["FO4 Seg 000", "FO4 Seg 001", "FO4 Seg 002", "FO4 Seg 003"]:
        svg = obj.vertex_groups.new(name=seg_name)
        if seg_name == "FO4 Seg 003":
            svg.add(list(range(len(per_vert_weights))), 1.0, "REPLACE")


def _smoothstep01(t: float) -> float:
    c = max(0.0, min(1.0, t))
    return c * c * (3.0 - 2.0 * c)


def _blend_weight_dicts(d_a: dict, d_b: dict, alpha_b: float) -> dict:
    tb = _smoothstep01(alpha_b)
    ta = 1.0 - tb
    merged = defaultdict(float)
    for k, v in d_a.items():
        if v * ta > 1e-5:
            merged[k] += v * ta
    for k, v in d_b.items():
        if v * tb > 1e-5:
            merged[k] += v * tb
    top4 = sorted(merged.items(), key=lambda kv: kv[1], reverse=True)[:4]
    s = sum(v for _, v in top4)
    return {k: v / s for k, v in top4} if s > 1e-6 else {"SPINE2": 1.0}


def add_extruded_2d_polygon_on_back(bm, uv_lay, poly_xz: list[tuple[float, float]], back_y, y_base_off: float, thickness: float, uv_rect: tuple[float, float, float, float]):
    """Extruye un polígono 2D en relieve sobre la espalda alta (-Y), orientado limpiamente hacia atrás."""
    u0, v0, u1, v1 = uv_rect
    xs = [p[0] for p in poly_xz]
    zs = [p[1] for p in poly_xz]
    xmin, xmax = min(xs), max(xs)
    zmin, zmax = min(zs), max(zs)
    dx = max(xmax - xmin, 0.001)
    dz = max(zmax - zmin, 0.001)

    cx = sum(xs) / len(xs)
    cz = sum(zs) / len(zs)
    cy_back = back_y(cx, cz) - y_base_off - thickness

    outer_ring = []
    inner_ring = []
    ring_uvs = []
    for x, z in poly_xz:
        ys = back_y(x, z)
        vo = bm.verts.new((x, ys - y_base_off - thickness, z))
        vi = bm.verts.new((x, ys - y_base_off + 0.14, z))
        outer_ring.append(vo)
        inner_ring.append(vi)
        uu = u0 + ((x - xmin) / dx) * (u1 - u0)
        vv = v0 + ((z - zmin) / dz) * (v1 - v0)
        ring_uvs.append((uu, vv))

    v_center = bm.verts.new((cx, cy_back - 0.14, cz))
    uv_center = (0.5 * (u0 + u1), 0.5 * (v0 + v1))

    n = len(poly_xz)
    for i in range(n):
        j = (i + 1) % n
        f_top = bm.faces.new((v_center, outer_ring[i], outer_ring[j]))
        f_top.normal_update()
        if f_top.normal.y > 0.0:
            bm.faces.remove(f_top)
            f_top = bm.faces.new((v_center, outer_ring[j], outer_ring[i]))
            for lp, uv in zip(f_top.loops, [uv_center, ring_uvs[j], ring_uvs[i]]):
                lp[uv_lay].uv = uv
        else:
            for lp, uv in zip(f_top.loops, [uv_center, ring_uvs[i], ring_uvs[j]]):
                lp[uv_lay].uv = uv

        f_side = bm.faces.new((outer_ring[i], outer_ring[j], inner_ring[j], inner_ring[i]))
        f_side.normal_update()
        out_dir = Vector((poly_xz[i][0] - cx, -0.35, poly_xz[i][1] - cz))
        if f_side.normal.dot(out_dir) < 0.0:
            bm.faces.remove(f_side)
            f_side = bm.faces.new((outer_ring[j], outer_ring[i], inner_ring[i], inner_ring[j]))
        for lp in f_side.loops:
            lp[uv_lay].uv = uv_center


def add_extruded_2d_polygon_on_chest(bm, uv_lay, poly_xz: list[tuple[float, float]], front_y, y_base_off: float, thickness: float, uv_rect: tuple[float, float, float, float]):
    """Extruye un polígono convexo/estrellado 2D (en X, Z) adaptándolo exactamente a la curvatura pectoral."""
    u0, v0, u1, v1 = uv_rect
    xs = [p[0] for p in poly_xz]
    zs = [p[1] for p in poly_xz]
    xmin, xmax = min(xs), max(xs)
    zmin, zmax = min(zs), max(zs)
    dx = max(xmax - xmin, 0.001)
    dz = max(zmax - zmin, 0.001)

    cx = sum(xs) / len(xs)
    cz = sum(zs) / len(zs)
    cy_front = front_y(cx, cz) + y_base_off + thickness

    front_ring = []
    back_ring = []
    ring_uvs = []
    for x, z in poly_xz:
        ys = front_y(x, z)
        vf = bm.verts.new((x, ys + y_base_off + thickness, z))
        vb = bm.verts.new((x, ys + y_base_off - 0.12, z))
        front_ring.append(vf)
        back_ring.append(vb)
        uu = u0 + ((x - xmin) / dx) * (u1 - u0)
        vv = v0 + ((z - zmin) / dz) * (v1 - v0)
        ring_uvs.append((uu, vv))

    v_center = bm.verts.new((cx, cy_front + 0.14, cz))
    uv_center = (0.5 * (u0 + u1), 0.5 * (v0 + v1))

    n = len(poly_xz)
    for i in range(n):
        j = (i + 1) % n
        f_top = bm.faces.new((v_center, front_ring[i], front_ring[j]))
        f_top.normal_update()
        if f_top.normal.y < 0.0:
            bm.faces.remove(f_top)
            f_top = bm.faces.new((v_center, front_ring[j], front_ring[i]))
            for lp, uv in zip(f_top.loops, [uv_center, ring_uvs[j], ring_uvs[i]]):
                lp[uv_lay].uv = uv
        else:
            for lp, uv in zip(f_top.loops, [uv_center, ring_uvs[i], ring_uvs[j]]):
                lp[uv_lay].uv = uv

        f_side = bm.faces.new((front_ring[i], front_ring[j], back_ring[j], back_ring[i]))
        f_side.normal_update()
        out_dir = Vector((poly_xz[i][0] - cx, 0.35, poly_xz[i][1] - cz))
        if f_side.normal.dot(out_dir) < 0.0:
            bm.faces.remove(f_side)
            f_side = bm.faces.new((front_ring[j], front_ring[i], back_ring[i], back_ring[j]))
        for lp in f_side.loops:
            lp[uv_lay].uv = uv_center


def create_hero_crest_and_belt_mesh(suit_obj, arm_obj, is_female: bool, root_obj=None):
    """
    Esculpe en 3D:
      1. Escudo Pectoral Pentagonal (estilo Superman × Capitán Cosmos) adaptado al pecho M/F.
      2. Dos Broches / Medallones Dorados Octogonales en las clavículas + Puente Dorsal de Manto en Oro Bruñido.
      3. Cinturón Cósmico en V en Oro Bruñido con Hebilla Diamante en relieve alrededor de la cintura.
    """
    front_y, back_y, waist_ring_point, sample_bone_weights = build_surface_sampler(suit_obj)
    bm = bmesh.new()
    uv_lay = bm.loops.layers.uv.new("UVMap")

    UV_GOLD = (0.08, 0.55, 0.92, 0.94)
    UV_RUBY = (0.06, 0.06, 0.44, 0.40)
    UV_CORE = (0.56, 0.06, 0.94, 0.40)

    z_mid = 102.6 if not is_female else 102.2
    outer_shield = [
        (-4.6, z_mid + 5.0),
        ( 4.6, z_mid + 5.0),
        ( 6.1, z_mid + 1.8),
        ( 0.0, z_mid - 5.4),
        (-6.1, z_mid + 1.8),
    ]
    inner_shield = [
        (-3.65, z_mid + 4.10),
        ( 3.65, z_mid + 4.10),
        ( 4.85, z_mid + 1.55),
        ( 0.00, z_mid - 4.15),
        (-4.85, z_mid + 1.55),
    ]
    add_extruded_2d_polygon_on_chest(bm, uv_lay, outer_shield, front_y, 0.05, 0.28, UV_GOLD)
    add_extruded_2d_polygon_on_chest(bm, uv_lay, inner_shield, front_y, 0.25, 0.14, UV_RUBY)

    cz_star = z_mid + 0.85
    star_poly = [
        ( 0.00, cz_star + 3.05),
        ( 0.72, cz_star + 0.72),
        ( 3.35, cz_star + 0.00),
        ( 0.72, cz_star - 0.72),
        ( 0.00, cz_star - 3.65),
        (-0.72, cz_star - 0.72),
        (-3.35, cz_star + 0.00),
        (-0.72, cz_star + 0.72),
    ]
    add_extruded_2d_polygon_on_chest(bm, uv_lay, star_poly, front_y, 0.34, 0.20, UV_GOLD)

    n_seg = 24
    ang_tilt = math.radians(28.0)
    ct, st = math.cos(ang_tilt), math.sin(ang_tilt)
    orbit_ring_out = []
    orbit_ring_in = []
    for k in range(n_seg):
        t = (2.0 * math.pi * k) / n_seg
        ox, oz = 3.95 * math.cos(t), 1.45 * math.sin(t)
        ix, iz = 3.30 * math.cos(t), 1.05 * math.sin(t)
        rx_o, rz_o = ox * ct - oz * st, cz_star + ox * st + oz * ct
        rx_i, rz_i = ix * ct - iz * st, cz_star + ix * st + iz * ct
        yo = front_y(rx_o, rz_o) + 0.50
        yi = front_y(rx_i, rz_i) + 0.50
        orbit_ring_out.append((bm.verts.new((rx_o, yo, rz_o)), bm.verts.new((rx_o, yo - 0.22, rz_o))))
        orbit_ring_in.append((bm.verts.new((rx_i, yi, rz_i)), bm.verts.new((rx_i, yi - 0.22, rz_i))))
    for k in range(n_seg):
        kn = (k + 1) % n_seg
        vo0, vob0 = orbit_ring_out[k]
        vo1, vob1 = orbit_ring_out[kn]
        vi0, vib0 = orbit_ring_in[k]
        vi1, vib1 = orbit_ring_in[kn]
        for quad in [(vi0, vo0, vo1, vi1), (vo0, vob0, vob1, vo1), (vi1, vib1, vib0, vi0)]:
            f = bm.faces.new(quad)
            f.normal_update()
            for lp in f.loops:
                lp[uv_lay].uv = (0.5, 0.75)

    core_poly = [
        (0.85 * math.cos(2.0 * math.pi * k / 8.0), cz_star + 0.85 * math.sin(2.0 * math.pi * k / 8.0))
        for k in range(8)
    ]
    add_extruded_2d_polygon_on_chest(bm, uv_lay, core_poly, front_y, 0.52, 0.18, UV_CORE)

    # 2A. Broches / Medallones Dorados de Clavícula donde ancla la capa (X = ±7.4, Z = 110.6)
    z_clasp = 110.6 if not is_female else 109.8
    for sx in (-1.0, 1.0):
        cx_c = sx * (7.4 if not is_female else 6.8)
        clasp_outer = [
            (cx_c + 1.75 * math.cos(2.0 * math.pi * k / 10.0), z_clasp + 1.75 * math.sin(2.0 * math.pi * k / 10.0))
            for k in range(10)
        ]
        clasp_inner = [
            (cx_c + 0.98 * math.cos(2.0 * math.pi * k / 10.0), z_clasp + 0.98 * math.sin(2.0 * math.pi * k / 10.0))
            for k in range(10)
        ]
        add_extruded_2d_polygon_on_chest(bm, uv_lay, clasp_outer, front_y, 0.08, 0.38, UV_GOLD)
        add_extruded_2d_polygon_on_chest(bm, uv_lay, clasp_inner, front_y, 0.40, 0.16, UV_RUBY)

    # 2B. Puente Dorsal de Manto en Oro Bruñido sobre los omóplatos superiores (Z = 109.8),
    #     sellando con elegancia la unión entre el canesú de hombro y la capa aerodinámica CosmosHeroCapeAO.nif.
    mantle_bar = [
        (-9.5, 110.65),
        ( 9.5, 110.65),
        ( 9.8, 109.25),
        ( 0.0, 108.55),
        (-9.8, 109.25),
    ]
    mantle_gem = [
        (0.0, 110.35),
        (1.45, 109.60),
        (0.0, 108.85),
        (-1.45, 109.60),
    ]
    add_extruded_2d_polygon_on_back(bm, uv_lay, mantle_bar, lambda _x, _z: -11.65, 0.55, 0.56, UV_GOLD)
    add_extruded_2d_polygon_on_back(bm, uv_lay, mantle_gem, lambda _x, _z: -11.65, 1.06, 0.20, UV_RUBY)

    # 3. Cinturón Heroico en V alrededor de la cintura (Z = 78.2, con caída en V frontal a Z = 75.8)
    z_belt_base = 78.2 if not is_female else 77.8
    n_belt = 40
    belt_h = 1.65
    belt_thick = 0.48
    rings_top_out, rings_bot_out, rings_top_in, rings_bot_in = [], [], [], []
    for k in range(n_belt):
        th = (2.0 * math.pi * k) / n_belt
        frontness = max(0.0, math.sin(th)) ** 3
        zc = z_belt_base - 2.1 * frontness
        p_surf = waist_ring_point(th, zc)
        n_rad = Vector((math.cos(th), math.sin(th), 0.0))
        p_in_top = p_surf + n_rad * 0.06 + Vector((0.0, 0.0, belt_h))
        p_in_bot = p_surf + n_rad * 0.06 - Vector((0.0, 0.0, belt_h))
        p_out_top = p_surf + n_rad * belt_thick + Vector((0.0, 0.0, belt_h * 0.88))
        p_out_bot = p_surf + n_rad * belt_thick - Vector((0.0, 0.0, belt_h * 0.88))
        rings_top_in.append(bm.verts.new(p_in_top))
        rings_bot_in.append(bm.verts.new(p_in_bot))
        rings_top_out.append(bm.verts.new(p_out_top))
        rings_bot_out.append(bm.verts.new(p_out_bot))

    for k in range(n_belt):
        kn = (k + 1) % n_belt
        quads = [
            (rings_bot_out[k], rings_bot_out[kn], rings_top_out[kn], rings_top_out[k]),
            (rings_top_out[k], rings_top_out[kn], rings_top_in[kn], rings_top_in[k]),
            (rings_bot_in[k], rings_bot_in[kn], rings_bot_out[kn], rings_bot_out[k]),
        ]
        for q in quads:
            f = bm.faces.new(q)
            for lp in f.loops:
                lp[uv_lay].uv = (0.5, 0.78)

    z_bk = z_belt_base - 2.0
    buckle_outer = [(0.0, z_bk + 2.55), (2.75, z_bk), (0.0, z_bk - 2.55), (-2.75, z_bk)]
    buckle_inner = [(0.0, z_bk + 1.45), (1.55, z_bk), (0.0, z_bk - 1.45), (-1.55, z_bk)]
    add_extruded_2d_polygon_on_chest(bm, uv_lay, buckle_outer, front_y, 0.42, 0.46, UV_GOLD)
    add_extruded_2d_polygon_on_chest(bm, uv_lay, buckle_inner, front_y, 0.82, 0.20, UV_RUBY)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    me = bpy.data.meshes.new("CosmosHeroCrestMesh")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = False

    crest_obj = bpy.data.objects.new("CosmosHeroCrest:0", me)
    bpy.context.scene.collection.objects.link(crest_obj)

    gold_mat = suit_obj.data.materials[0].copy()
    gold_mat.name = "CosmosHeroGoldMat"
    assign_shader_on_material(
        gold_mat,
        r"Materials\AeroArmor\Hero\CosmosHeroGold.BGSM",
        r"textures\AeroArmor\Hero\CosmosHeroGold_d.dds",
        r"textures\AeroArmor\Hero\CosmosHeroGold_n.dds",
        r"textures\AeroArmor\Hero\CosmosHeroGold_s.dds",
        env_dds=r"textures\Shared\Cubemaps\mipblur_DefaultOutside1.dds",
    )
    me.materials.append(gold_mat)

    weights = [sample_bone_weights(v.co, k=6) for v in me.vertices]
    apply_weights_and_torso_seg(crest_obj, arm_obj, weights, root_obj=root_obj)
    return crest_obj


def create_hero_collar_yoke_mesh(suit_obj, arm_obj, is_female: bool, root_obj=None):
    """
    Esculpe en 3D el Canesú / Esclavina Superior de Hombros (CosmosHeroCollar:0, malla cerrada 12x25):
      - Nace exactamente en los dos broches dorados de clavícula (X = ±7.4 M / ±6.8 F, Z = 110.6),
        remonta con suavidad anatómica sobre los trapecios (Z = 113.4) y desemboca bajo el
        Puente Dorsal Dorado (Z = 109.6, Y = -12.15), donde enlaza sin costuras con CosmosHeroCapeAO.nif.
      - Riggeado 100 % al esqueleto nativo de SynthUniform (cero artefactos en clavículas/hombros).
    """
    front_y, back_y, _, sample_bone_weights = build_surface_sampler(suit_obj)
    rows = 12
    cols = 25
    thickness = 0.30

    bm = bmesh.new()
    uv_lay = bm.loops.layers.uv.new("UVMap")

    outer_grid = []
    inner_grid = []
    uv_grid = []
    w_inner = []
    w_outer = []

    clasp_half_w = 7.4 if not is_female else 6.8
    back_half_w = 9.4

    for r in range(rows):
        s = r / (rows - 1)
        t_uv = 0.075 * s
        half_w = clasp_half_w + (back_half_w - clasp_half_w) * _smoothstep01(s)
        z_front_start = 110.8 if not is_female else 110.0
        z_arch = z_front_start * (1.0 - s) + 109.6 * s + 2.6 * math.sin(s * math.pi)

        row_in = []
        row_out = []
        row_uv = []
        for c in range(cols):
            u = c / (cols - 1)
            xn = 2.0 * u - 1.0
            x = xn * half_w

            neck_cut = (1.0 - min(1.0, abs(xn) / 0.68) ** 2)
            y_front_anchor = front_y(x, z_arch) + 0.38
            y_back_end = -12.55
            arch_s = max(_smoothstep01(s), neck_cut * 0.94)
            y_in = y_front_anchor * (1.0 - arch_s) + y_back_end * arch_s
            z = z_arch - 1.35 * neck_cut * (1.0 - s)

            ny_dir = -1.0 if arch_s > 0.50 else 0.55
            nz_dir = 0.75 if arch_s <= 0.50 else 0.22
            n_vec = Vector((xn * 0.10, ny_dir, nz_dir)).normalized()

            p_in = Vector((x, y_in, z))
            p_out = p_in + n_vec * thickness
            row_in.append(bm.verts.new(p_in))
            row_out.append(bm.verts.new(p_out))
            row_uv.append((u, 1.0 - t_uv))

            if s >= 0.82:
                w_d = _blend_weight_dicts(
                    sample_bone_weights(Vector((x, back_y(x, z), z)), k=6),
                    {"Chest_Rear_Skin": 1.0},
                    (s - 0.82) / 0.18,
                )
            else:
                probe_y = front_y(x, z) if y_in > 0.0 else back_y(x, z)
                w_d = sample_bone_weights(Vector((x, probe_y, z)), k=6)
            w_inner.append(w_d)
            w_outer.append(dict(w_d))

        inner_grid.append(row_in)
        outer_grid.append(row_out)
        uv_grid.append(row_uv)

    for r in range(rows - 1):
        for c in range(cols - 1):
            f_out = bm.faces.new((outer_grid[r][c], outer_grid[r + 1][c], outer_grid[r + 1][c + 1], outer_grid[r][c + 1]))
            for lp, uv in zip(f_out.loops, [uv_grid[r][c], uv_grid[r + 1][c], uv_grid[r + 1][c + 1], uv_grid[r][c + 1]]):
                lp[uv_lay].uv = uv
            f_in = bm.faces.new((inner_grid[r][c + 1], inner_grid[r + 1][c + 1], inner_grid[r + 1][c], inner_grid[r][c]))
            for lp, uv in zip(f_in.loops, [uv_grid[r][c + 1], uv_grid[r + 1][c + 1], uv_grid[r + 1][c], uv_grid[r][c]]):
                lp[uv_lay].uv = (uv[0], uv[1] * 0.44)

    gold_hem_uv = (0.022, 0.50)
    for r in range(rows - 1):
        fl = bm.faces.new((inner_grid[r][0], inner_grid[r + 1][0], outer_grid[r + 1][0], outer_grid[r][0]))
        for lp in fl.loops:
            lp[uv_lay].uv = gold_hem_uv
        cr = cols - 1
        fr = bm.faces.new((outer_grid[r][cr], outer_grid[r + 1][cr], inner_grid[r + 1][cr], inner_grid[r][cr]))
        for lp in fr.loops:
            lp[uv_lay].uv = gold_hem_uv

    for c in range(cols - 1):
        ft = bm.faces.new((outer_grid[0][c], outer_grid[0][c + 1], inner_grid[0][c + 1], inner_grid[0][c]))
        for lp in ft.loops:
            lp[uv_lay].uv = gold_hem_uv
        rb = rows - 1
        fb = bm.faces.new((inner_grid[rb][c], inner_grid[rb][c + 1], outer_grid[rb][c + 1], outer_grid[rb][c]))
        for lp in fb.loops:
            lp[uv_lay].uv = gold_hem_uv

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    all_weights = []
    for r in range(rows):
        for c in range(cols):
            idx = r * cols + c
            all_weights.append(w_inner[idx])
            all_weights.append(w_outer[idx])

    me = bpy.data.meshes.new("CosmosHeroCollarMesh")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True

    collar_obj = bpy.data.objects.new("CosmosHeroCollar:0", me)
    bpy.context.scene.collection.objects.link(collar_obj)

    cape_mat = suit_obj.data.materials[0].copy()
    cape_mat.name = "CosmosHeroCapeMat"
    assign_shader_on_material(
        cape_mat,
        r"Materials\AeroArmor\Hero\CosmosHeroCape.BGSM",
        r"textures\AeroArmor\Hero\CosmosHeroCape_d.dds",
        r"textures\AeroArmor\Hero\CosmosHeroCape_n.dds",
        r"textures\AeroArmor\Hero\CosmosHeroCape_s.dds",
    )
    me.materials.append(cape_mat)

    apply_weights_and_torso_seg(collar_obj, arm_obj, all_weights, root_obj=root_obj)
    return collar_obj


def _cape_rest_center_y(zq: float) -> float:
    s = max(0.0, min(1.0, (109.8 - zq) / (109.8 - 21.0)))
    return -12.65 - 15.15 * (s ** 0.85)


def _cape_half_w(s_body: float) -> float:
    return 9.4 + (19.4 - 9.4) * (s_body ** 0.88)


def add_cape_cloth_bones_to_armature(arm_obj):
    """
    Añade únicamente los 25 huesos dinámicos Cape_Cloth_{A..E}_{1..5} bajo Chest_Rear_Skin
    sin alterar ni un solo hueso nativo del esqueleto de SynthUniform (hombros 100 % intactos).
    """
    bpy.ops.object.select_all(action="DESELECT")
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode="EDIT")

    ebones = arm_obj.data.edit_bones
    crs_eb = ebones.get("Chest_Rear_Skin")
    assert crs_eb is not None, "No se encontró Chest_Rear_Skin en el armature de SynthUniform"
    mw_inv = arm_obj.matrix_world.inverted()

    col_specs = [("A", -0.78), ("B", -0.39), ("C", 0.00), ("D", +0.39), ("E", +0.78)]
    bone_z_levels = [100.5, 83.0, 64.5, 45.5, 27.5]

    for col_lbl, xn_b in col_specs:
        prev_eb = crs_eb
        for j, zb in enumerate(bone_z_levels, start=1):
            bname = f"Cape_Cloth_{col_lbl}_{j}"
            s_b = (109.8 - zb) / (109.8 - 21.0)
            bx = xn_b * _cape_half_w(s_b)
            by = _cape_rest_center_y(zb) + 0.45 * (xn_b ** 2) * (0.20 + 0.80 * s_b)
            bz = zb - 1.8 * (1.0 - xn_b ** 2) * (s_b ** 2)

            eb = ebones.new(bname)
            eb.head = mw_inv @ Vector((bx, by, bz))
            eb.tail = mw_inv @ Vector((bx, by - 3.0, bz))
            eb.roll = 0.0
            eb.use_connect = False
            eb.parent = prev_eb
            prev_eb = eb

    bpy.ops.object.mode_set(mode="OBJECT")


def create_hero_full_cloth_cape_mesh(suit_obj, arm_obj, root_obj=None):
    """
    Esculpe en 3D el manto completo de doble cara cerrada (CosmosHeroCape:0, 38x29, Z = 109.8 -> 21.0):
      - Anclado en Z >= 107.6 a Chest_Rear_Skin bajo el Puente Dorsal Dorado.
      - Interpolado bilinealmente con suavidad C1 en los 25 huesos dinámicos Havok Cloth
        Cape_Cloth_{A..E}_{1..5} desde los omóplatos (incluyendo el emblema dorsal) hasta el dobladillo.
    """
    rows = 38
    cols = 29
    cape_thickness = 0.30
    top_z = 109.8
    bot_z = 21.0
    col_specs = [("A", -0.78), ("B", -0.39), ("C", 0.00), ("D", +0.39), ("E", +0.78)]
    bone_z_levels = [100.5, 83.0, 64.5, 45.5, 27.5]

    def eval_cloth_weights(xw: float, zw: float) -> dict[str, float]:
        if zw >= 107.6:
            return {"Chest_Rear_Skin": 1.0}

        s_span = max(0.0, min(1.0, (top_z - zw) / (top_z - bot_z)))
        hw = _cape_half_w(s_span)
        xn_q = xw / max(hw, 1e-4)

        if xn_q <= col_specs[0][1]:
            h_terms = [(col_specs[0][0], 1.0)]
        elif xn_q >= col_specs[-1][1]:
            h_terms = [(col_specs[-1][0], 1.0)]
        else:
            h_terms = [("C", 1.0)]
            for idx_c in range(len(col_specs) - 1):
                c_lo, x_lo = col_specs[idx_c]
                c_hi, x_hi = col_specs[idx_c + 1]
                if x_lo <= xn_q <= x_hi:
                    tx = _smoothstep01((xn_q - x_lo) / (x_hi - x_lo))
                    h_terms = [(c_lo, 1.0 - tx), (c_hi, tx)]
                    break

        if zw >= bone_z_levels[0]:
            tz = _smoothstep01((107.6 - zw) / (107.6 - bone_z_levels[0]))
            v_terms = {
                clbl: [("Chest_Rear_Skin", 1.0 - tz), (f"Cape_Cloth_{clbl}_1", tz)]
                for clbl, _ in col_specs
            }
        elif zw <= bone_z_levels[-1]:
            tz = _smoothstep01((bone_z_levels[-1] - zw) / (bone_z_levels[-1] - bot_z + 0.5))
            w4 = 0.18 * (1.0 - tz)
            w5 = 1.0 - w4
            v_terms = {
                clbl: ([(f"Cape_Cloth_{clbl}_4", w4), (f"Cape_Cloth_{clbl}_5", w5)] if w4 > 1e-4 else [(f"Cape_Cloth_{clbl}_5", 1.0)])
                for clbl, _ in col_specs
            }
        else:
            v_terms = {}
            for k in range(len(bone_z_levels) - 1):
                z_hi = bone_z_levels[k]
                z_lo = bone_z_levels[k + 1]
                if z_lo <= zw <= z_hi:
                    tz = _smoothstep01((z_hi - zw) / (z_hi - z_lo))
                    for clbl, _ in col_specs:
                        v_terms[clbl] = [
                            (f"Cape_Cloth_{clbl}_{k + 1}", 1.0 - tz),
                            (f"Cape_Cloth_{clbl}_{k + 2}", tz),
                        ]
                    break

        acc = defaultdict(float)
        for clbl, hw_w in h_terms:
            if hw_w <= 1e-5:
                continue
            for bnm, vw_w in v_terms[clbl]:
                w = hw_w * vw_w
                if w > 1e-5:
                    acc[bnm] += w

        top4 = sorted(acc.items(), key=lambda kv: kv[1], reverse=True)[:4]
        tot = sum(v for _, v in top4)
        return {k: v / tot for k, v in top4}

    bm = bmesh.new()
    uv_lay = bm.loops.layers.uv.new("UVMap")

    inner_grid = []
    outer_grid = []
    uv_out_grid = []
    uv_in_grid = []
    all_weights = []

    for r in range(rows):
        s_body = r / (rows - 1)
        half_w = _cape_half_w(s_body)
        z_base = top_z * (1.0 - s_body) + bot_z * s_body
        v_bl_out = 1.0 - (0.065 + 0.935 * s_body)
        v_bl_in = 1.0 - (0.56 + 0.42 * s_body)

        row_in = []
        row_out = []
        row_uv_out = []
        row_uv_in = []
        for c in range(cols):
            u = c / (cols - 1)
            xn = 2.0 * u - 1.0
            x = xn * half_w

            y_center = _cape_rest_center_y(z_base)
            pleat_amp = 1.35 * (s_body ** 1.10)
            pleat = pleat_amp * math.cos(xn * math.pi * 4.0)
            edge_cup = 0.45 * (xn ** 2) * (0.20 + 0.80 * s_body)
            y_in = y_center - pleat + edge_cup
            hem_curve = -1.8 * (1.0 - xn ** 2) * (s_body ** 2)
            z = z_base + hem_curve

            n_out = Vector((xn * 0.12, -1.0, 0.14)).normalized()
            p_in = Vector((x, y_in, z))
            p_out = p_in + n_out * cape_thickness

            w_d = eval_cloth_weights(x, z)
            row_in.append(bm.verts.new(p_in))
            all_weights.append(w_d)
            row_out.append(bm.verts.new(p_out))
            all_weights.append(dict(w_d))
            row_uv_out.append((u, v_bl_out))
            row_uv_in.append((u, v_bl_in))

        inner_grid.append(row_in)
        outer_grid.append(row_out)
        uv_out_grid.append(row_uv_out)
        uv_in_grid.append(row_uv_in)

    for r in range(rows - 1):
        for c in range(cols - 1):
            f_out = bm.faces.new((outer_grid[r][c], outer_grid[r + 1][c], outer_grid[r + 1][c + 1], outer_grid[r][c + 1]))
            for lp, uv in zip(f_out.loops, [uv_out_grid[r][c], uv_out_grid[r + 1][c], uv_out_grid[r + 1][c + 1], uv_out_grid[r][c + 1]]):
                lp[uv_lay].uv = uv
            f_in = bm.faces.new((inner_grid[r][c + 1], inner_grid[r + 1][c + 1], inner_grid[r + 1][c], inner_grid[r][c]))
            for lp, uv in zip(f_in.loops, [uv_in_grid[r][c + 1], uv_in_grid[r + 1][c + 1], uv_in_grid[r][c], uv_in_grid[r][c]]):
                lp[uv_lay].uv = uv

    gold_hem_uv = (0.022, 0.50)
    for r in range(rows - 1):
        fl = bm.faces.new((inner_grid[r][0], inner_grid[r + 1][0], outer_grid[r + 1][0], outer_grid[r][0]))
        for lp in fl.loops:
            lp[uv_lay].uv = gold_hem_uv
        cr = cols - 1
        fr = bm.faces.new((outer_grid[r][cr], outer_grid[r + 1][cr], inner_grid[r + 1][cr], inner_grid[r][cr]))
        for lp in fr.loops:
            lp[uv_lay].uv = gold_hem_uv

    for c in range(cols - 1):
        ft = bm.faces.new((outer_grid[0][c], outer_grid[0][c + 1], inner_grid[0][c + 1], inner_grid[0][c]))
        for lp in ft.loops:
            lp[uv_lay].uv = gold_hem_uv
        rb = rows - 1
        fb = bm.faces.new((inner_grid[rb][c], inner_grid[rb][c + 1], outer_grid[rb][c + 1], outer_grid[rb][c]))
        for lp in fb.loops:
            lp[uv_lay].uv = gold_hem_uv

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("CosmosHeroCapeMesh")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True

    cape_obj = bpy.data.objects.new("CosmosHeroCape:0", me)
    bpy.context.scene.collection.objects.link(cape_obj)

    cape_mat = suit_obj.data.materials[0].copy()
    cape_mat.name = "CosmosHeroCapeBodyMat"
    assign_shader_on_material(
        cape_mat,
        r"Materials\AeroArmor\Hero\CosmosHeroCape.BGSM",
        r"textures\AeroArmor\Hero\CosmosHeroCape_d.dds",
        r"textures\AeroArmor\Hero\CosmosHeroCape_n.dds",
        r"textures\AeroArmor\Hero\CosmosHeroCape_s.dds",
    )
    me.materials.append(cape_mat)

    apply_weights_and_torso_seg(cape_obj, arm_obj, all_weights, root_obj=root_obj)
    return cape_obj


def render_qa_preview(meshes_to_show, out_png: str):
    """Renderiza una vista triple a todo color DESPUÉS de exportar el NIF (sin contaminar los materiales exportados)."""
    if not out_png:
        return
    try:
        scene = bpy.context.scene
        scene.render.engine = "BLENDER_WORKBENCH"
        scene.display.shading.light = "STUDIO"
        scene.display.shading.color_type = "TEXTURE"
        scene.render.resolution_x = 1400
        scene.render.resolution_y = 950
        scene.render.filepath = out_png

        assets_root = os.path.abspath(os.path.join(OUT_DIR, "..", "..", ".."))
        png_map = {
            "cosmosherosuit_d.dds": os.path.join(assets_root, "preview_suit_d.png"),
            "cosmosherocape_d.dds": os.path.join(assets_root, "preview_cape_d.png"),
            "cosmosherogold_d.dds": os.path.join(assets_root, "preview_gold_d.png"),
        }

        cam_data = bpy.data.cameras.new("QACam")
        cam_data.lens = 50
        cam_obj = bpy.data.objects.new("QACam", cam_data)
        scene.collection.objects.link(cam_obj)
        scene.camera = cam_obj

        clones = []
        for dx, rot_z in [(-64.0, math.pi), (0.0, 0.0), (64.0, math.radians(-38.0))]:
            for src in meshes_to_show:
                c = src.copy()
                c.data = src.data.copy()
                c.data.transform(src.matrix_world)
                if "Cape:0" in src.name:
                    # Simular pose de ondeo aerodinámico suave en la copia de previsualización QA
                    for v in c.data.vertices:
                        s_v = max(0.0, min(1.0, (108.0 - v.co.z) / 87.0))
                        wave = math.sin(s_v * 4.2 + v.co.x * 0.09) * (2.6 * s_v)
                        v.co.y -= (1.8 * s_v + wave)
                        v.co.x += math.cos(s_v * 3.1) * (1.1 * s_v)
                    c.data.update()
                c.modifiers.clear()
                c.parent = None
                c.hide_render = False
                c.hide_viewport = False
                c.display_type = "TEXTURED"
                c.data.materials.clear()
                orig_mat = src.data.materials[0]
                pmat = bpy.data.materials.new(name="Preview_" + orig_mat.name)
                pmat.use_nodes = True
                nt = pmat.node_tree
                bsdf = nt.nodes.get("Principled BSDF")
                d_rel = orig_mat.get("BSShaderTextureSet_Diffuse", "")
                png_p = png_map.get(os.path.basename(d_rel).lower(), "")
                if bsdf and png_p and os.path.exists(png_p):
                    tn = nt.nodes.new("ShaderNodeTexImage")
                    tn.image = bpy.data.images.load(png_p)
                    nt.links.new(tn.outputs["Color"], bsdf.inputs["Base Color"])
                    bsdf.inputs["Alpha"].default_value = 1.0
                c.data.materials.append(pmat)
                c.location = Vector((dx, 0.0, 0.0))
                c.rotation_euler = (0.0, 0.0, rot_z)
                scene.collection.objects.link(c)
                clones.append(c)

        for src in meshes_to_show:
            src.hide_render = True

        cam_obj.location = Vector((0.0, 235.0, 62.0))
        cam_obj.rotation_euler = (math.radians(89.0), 0.0, math.radians(180.0))
        bpy.ops.render.render(write_still=True)

        for c in clones:
            bpy.data.objects.remove(c, do_unlink=True)
        bpy.data.objects.remove(cam_obj, do_unlink=True)
        for src in meshes_to_show:
            src.hide_render = False
        print(f"[QA Preview] Render guardado en {out_png}")
    except Exception as exc:
        print(f"[QA Preview Warning] {exc}")


def export_hero_suit_3rd(src_nif: str, dst_nif: str, is_female: bool, preview_png: str = ""):
    """
    Exporta el traje 3ª persona sobre el esqueleto 100 % nativo de SynthUniform (M/F) + 25 huesos
    dinámicos Cape_Cloth_{A..E}_{1..5} y la malla cerrada CosmosHeroCape:0 lista para BSClothExtraData.
    """
    clear_scene()
    bpy.ops.import_scene.pynifly(
        filepath=os.path.join(TEST_DIR, src_nif),
        import_cutpoints=False,
        import_tris=False,
        import_collisions=False,
    )
    suit_root = next((o for o in bpy.data.objects if "pynRoot" in o), None)
    suit_obj = [o for o in bpy.data.objects if o.type == "MESH" and not o.name.startswith("bhk")][0]
    arm_obj = next((m.object for m in suit_obj.modifiers if m.type == "ARMATURE" and m.object), None)

    filter_mesh_islands(suit_obj, lambda coords, n: n >= 26)
    seam_aware_smooth(
        suit_obj,
        lambda wco: abs(wco.x) < 12.5 and abs(wco.y) > 4.5 and 92.0 < wco.z < 114.0,
        iterations=20,
        factor=0.60,
    )
    assign_shader_on_material(
        suit_obj.data.materials[0],
        r"Materials\AeroArmor\Hero\CosmosHeroSuit.BGSM",
        r"textures\AeroArmor\Hero\CosmosHeroSuit_d.dds",
        r"textures\Clothes\SynthUniform\SynthUniform_n.dds",
        r"textures\Clothes\SynthUniform\SynthUniform_s.dds",
    )

    # Primero muestrear y esculpir emblema/cinturón y canesú sobre los huesos nativos puros de SynthUniform
    crest_obj = create_hero_crest_and_belt_mesh(suit_obj, arm_obj, is_female=is_female, root_obj=suit_root)
    collar_obj = create_hero_collar_yoke_mesh(suit_obj, arm_obj, is_female=is_female, root_obj=suit_root)

    # Añadir los 25 huesos dinámicos de capa y construir CosmosHeroCape:0
    add_cape_cloth_bones_to_armature(arm_obj)
    cape_obj = create_hero_full_cloth_cape_mesh(suit_obj, arm_obj, root_obj=suit_root)

    all_meshes = [suit_obj, crest_obj, collar_obj, cape_obj]
    bpy.ops.object.select_all(action="DESELECT")
    if suit_root is not None:
        suit_root.select_set(True)
    for m in all_meshes:
        m.select_set(True)
    bpy.context.view_layer.objects.active = suit_obj
    dst_path = os.path.join(OUT_DIR, dst_nif)
    bpy.ops.export_scene.pynifly(filepath=dst_path, target_game="FO4")

    chk_nf = pynifly.NifFile(dst_path)
    print(f"[Exported FO4 Hero Suit + Cloth Cape Mesh 3rdP] {dst_nif} (shapes={[s.name for s in chk_nf.shapes]})")

    if preview_png:
        render_qa_preview(all_meshes, preview_png)


def export_simple_retextured(src_nif: str, dst_nif: str, bgsm_rel: str, diff_dds: str, norm_dds: str, spec_dds: str, min_island_verts: int = 0, import_collisions: bool = True, add_go_emblem: bool = False):
    clear_scene()
    bpy.ops.import_scene.pynifly(
        filepath=os.path.join(TEST_DIR, src_nif),
        import_cutpoints=False,
        import_tris=False,
        import_collisions=import_collisions,
    )
    meshes = [o for o in bpy.data.objects if o.type == "MESH" and not o.name.startswith("bhk")]
    for obj in meshes:
        if min_island_verts > 0:
            filter_mesh_islands(obj, lambda coords, n: n >= min_island_verts)
        assign_shader_on_material(obj.data.materials[0], bgsm_rel, diff_dds, norm_dds, spec_dds)

    if add_go_emblem and meshes:
        # Añadir insignia pentagonal dorada sobre el traje plegado para la vista previa 3D del Pip-Boy
        base_obj = meshes[0]
        zs = [(base_obj.matrix_world @ v.co).z for v in base_obj.data.vertices]
        xs = [(base_obj.matrix_world @ v.co).x for v in base_obj.data.vertices]
        ys = [(base_obj.matrix_world @ v.co).y for v in base_obj.data.vertices]
        top_z = max(zs) + 0.35
        cx = 0.5 * (min(xs) + max(xs))
        cy = 0.5 * (min(ys) + max(ys))

        bm = bmesh.new()
        uv_lay = bm.loops.layers.uv.new("UVMap")
        pts = [(-3.4, 3.0), (3.4, 3.0), (4.5, 0.9), (0.0, -3.8), (-4.5, 0.9)]
        top_v = [bm.verts.new((cx + px, cy + py, top_z + 0.45)) for px, py in pts]
        bot_v = [bm.verts.new((cx + px, cy + py, top_z - 0.35)) for px, py in pts]
        vc = bm.verts.new((cx, cy, top_z + 0.65))
        for i in range(len(pts)):
            j = (i + 1) % len(pts)
            f1 = bm.faces.new((vc, top_v[i], top_v[j]))
            f2 = bm.faces.new((top_v[i], bot_v[i], bot_v[j], top_v[j]))
            for lp in list(f1.loops) + list(f2.loops):
                lp[uv_lay].uv = (0.5, 0.78)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        em_me = bpy.data.meshes.new("CosmosGOBadgeMesh")
        bm.to_mesh(em_me)
        bm.free()
        em_obj = bpy.data.objects.new("CosmosGOBadge:0", em_me)
        bpy.context.scene.collection.objects.link(em_obj)
        em_obj.parent = base_obj.parent
        gmat = base_obj.data.materials[0].copy()
        gmat.name = "CosmosGOGoldMat"
        assign_shader_on_material(
            gmat,
            r"Materials\AeroArmor\Hero\CosmosHeroGold.BGSM",
            r"textures\AeroArmor\Hero\CosmosHeroGold_d.dds",
            r"textures\AeroArmor\Hero\CosmosHeroGold_n.dds",
            r"textures\AeroArmor\Hero\CosmosHeroGold_s.dds",
            env_dds=r"textures\Shared\Cubemaps\mipblur_DefaultOutside1.dds",
        )
        em_me.materials.append(gmat)
        meshes.append(em_obj)

    bpy.ops.object.select_all(action="DESELECT")
    for m in meshes:
        m.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.export_scene.pynifly(filepath=os.path.join(OUT_DIR, dst_nif), target_game="FO4")
    print(f"[Exported FO4 NIF] {dst_nif}")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    export_hero_suit_3rd("SynthUniform.nif", "CosmosHeroSuitM.nif", is_female=False, preview_png=RENDER_PREVIEW_PATH)
    export_hero_suit_3rd("SynthUniformF.nif", "CosmosHeroSuitF.nif", is_female=True)

    export_simple_retextured(
        "synthunderarmor1st.nif",
        "CosmosHeroSuit1stM.nif",
        r"Materials\AeroArmor\Hero\CosmosHeroSuit.BGSM",
        r"textures\AeroArmor\Hero\CosmosHeroSuit_d.dds",
        r"textures\Clothes\SynthUniform\SynthUniform_n.dds",
        r"textures\Clothes\SynthUniform\SynthUniform_s.dds",
    )
    export_simple_retextured(
        "synthuniformf1st.nif",
        "CosmosHeroSuit1stF.nif",
        r"Materials\AeroArmor\Hero\CosmosHeroSuit.BGSM",
        r"textures\AeroArmor\Hero\CosmosHeroSuit_d.dds",
        r"textures\Clothes\SynthUniform\SynthUniform_n.dds",
        r"textures\Clothes\SynthUniform\SynthUniform_s.dds",
    )
    export_simple_retextured(
        "synthuniformgo.nif",
        "CosmosHeroSuitGO.nif",
        r"Materials\AeroArmor\Hero\CosmosHeroSuit.BGSM",
        r"textures\AeroArmor\Hero\CosmosHeroSuit_d.dds",
        r"textures\Clothes\SynthUniform\SynthUniform_n.dds",
        r"textures\Clothes\SynthUniform\SynthUniform_s.dds",
        import_collisions=True,
        add_go_emblem=True,
    )
    export_simple_retextured(
        "MGloves.nif",
        "CosmosHeroGlovesM.nif",
        r"Materials\AeroArmor\Hero\CosmosHeroGloves.BGSM",
        r"textures\AeroArmor\Hero\CosmosHeroGloves_d.dds",
        r"textures\armor\knightunderarmor\knightgloves_n.dds",
        r"textures\AeroArmor\Hero\CosmosHeroGloves_s.dds",
        min_island_verts=500,
    )
    export_simple_retextured(
        "FGloves.nif",
        "CosmosHeroGlovesF.nif",
        r"Materials\AeroArmor\Hero\CosmosHeroGloves.BGSM",
        r"textures\AeroArmor\Hero\CosmosHeroGloves_d.dds",
        r"textures\armor\knightunderarmor\knightgloves_n.dds",
        r"textures\AeroArmor\Hero\CosmosHeroGloves_s.dds",
        min_island_verts=500,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)
'''


def build_and_deploy_cosmos_hero_assets(force_rebuild: bool = True) -> None:
    os.makedirs(TEX_OUT_DIR, exist_ok=True)
    os.makedirs(MAT_OUT_DIR, exist_ok=True)
    os.makedirs(MESH_OUT_DIR, exist_ok=True)

    # 1. Texturas Difusas BC1 (2048x2048, 12 mipmaps) y Mapas BC5 (1024x1024, 11 mipmaps)
    print("[1/4] Generando texturas PBR 2K BC1/BC5 del Traje de Vuelo Astro-Cosmos...")
    suit_im = build_cosmos_suit_texture(force_rebuild=force_rebuild)
    write_dds_file(os.path.join(TEX_OUT_DIR, "CosmosHeroSuit_d.dds"), encode_dds_with_12_mips(suit_im))

    gloves_im = build_cosmos_gloves_texture()
    write_dds_file(os.path.join(TEX_OUT_DIR, "CosmosHeroGloves_d.dds"), encode_dds_with_12_mips(gloves_im))
    build_calibrated_gloves_specular(os.path.join(TEX_OUT_DIR, "CosmosHeroGloves_s.dds"))

    cape_im, cape_n, cape_s = build_cosmos_cape_textures()
    write_dds_file(os.path.join(TEX_OUT_DIR, "CosmosHeroCape_d.dds"), encode_dds_with_12_mips(cape_im))
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosHeroCape_n.dds"), cape_n[:, :, 0], cape_n[:, :, 1], nmips=11)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosHeroCape_s.dds"), cape_s[:, :, 0], cape_s[:, :, 1], nmips=11)

    gold_im, gold_n, gold_s = build_cosmos_gold_textures()
    write_dds_file(os.path.join(TEX_OUT_DIR, "CosmosHeroGold_d.dds"), encode_dds_with_12_mips(gold_im))
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosHeroGold_n.dds"), gold_n[:, :, 0], gold_n[:, :, 1], nmips=11)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosHeroGold_s.dds"), gold_s[:, :, 0], gold_s[:, :, 1], nmips=11)

    # Guardar copias PNG para previsualización 3D a todo color en Blender
    suit_im.resize((1024, 1024)).save(os.path.join(HERO_ASSETS_DIR, "preview_suit_d.png"))
    cape_im.resize((1024, 1024)).save(os.path.join(HERO_ASSETS_DIR, "preview_cape_d.png"))
    gold_im.resize((1024, 1024)).save(os.path.join(HERO_ASSETS_DIR, "preview_gold_d.png"))

    # 2. Materiales BGSM v2
    print("[2/4] Generando materiales binarios .BGSM v2...")
    mat_specs = [
        (
            "CosmosHeroSuit.BGSM",
            build_bgsm_v2_bytes(
                diffuse_path="AeroArmor/Hero/CosmosHeroSuit_d.dds",
                normal_path="Clothes/SynthUniform/SynthUniform_n.dds",
                specular_path="Clothes/SynthUniform/SynthUniform_s.dds",
                envmap_path="Shared/Cubemaps/mipblur_InstInterior.dds",
                root_material="template/OutfitTemplate_Wet.bgsm",
                envmap_scale=0.36,
                specular_color=(0.86, 0.90, 0.96),
                specular_mult=0.88,
                smoothness=0.92,
            ),
        ),
        (
            "CosmosHeroGloves.BGSM",
            build_bgsm_v2_bytes(
                diffuse_path="AeroArmor/Hero/CosmosHeroGloves_d.dds",
                normal_path="armor/knightunderarmor/knightgloves_n.dds",
                specular_path="AeroArmor/Hero/CosmosHeroGloves_s.dds",
                envmap_path="Shared/Cubemaps/mipblur_InstInterior.dds",
                root_material="template/OutfitTemplate_Wet.bgsm",
                envmap_scale=0.35,
                specular_color=(0.94, 0.86, 0.84),
                specular_mult=0.86,
                smoothness=0.90,
            ),
        ),
        (
            "CosmosHeroCape.BGSM",
            build_bgsm_v2_bytes(
                diffuse_path="AeroArmor/Hero/CosmosHeroCape_d.dds",
                normal_path="AeroArmor/Hero/CosmosHeroCape_n.dds",
                specular_path="AeroArmor/Hero/CosmosHeroCape_s.dds",
                envmap_path="Shared/Cubemaps/mipblur_InstInterior.dds",
                root_material="template/OutfitTemplate_Wet.bgsm",
                envmap_scale=0.20,
                specular_color=(0.94, 0.84, 0.74),
                specular_mult=0.72,
                smoothness=0.84,
                two_sided=True,
            ),
        ),
        (
            "CosmosHeroGold.BGSM",
            build_bgsm_v2_bytes(
                diffuse_path="AeroArmor/Hero/CosmosHeroGold_d.dds",
                normal_path="AeroArmor/Hero/CosmosHeroGold_n.dds",
                specular_path="AeroArmor/Hero/CosmosHeroGold_s.dds",
                envmap_path="Shared/Cubemaps/mipblur_DefaultOutside1.dds",
                root_material="template/ArmorTemplate_Wet.bgsm",
                envmap_scale=0.86,
                specular_color=(0.96, 0.80, 0.44),
                specular_mult=1.15,
                smoothness=1.02,
                subsurface_lighting=0,
                subsurface_rolloff=0.0,
            ),
        ),
    ]
    for mat_fn, mat_bytes in mat_specs:
        with open(os.path.join(MAT_OUT_DIR, mat_fn), "wb") as wf:
            wf.write(mat_bytes)

    # Pre-desplegar materiales y texturas para que nifly.dll los encuentre durante la exportación
    for sub_src, sub_dst in [
        (TEX_OUT_DIR, os.path.join(FO4_DATA_DIR, "Textures", "AeroArmor", "Hero")),
        (MAT_OUT_DIR, os.path.join(FO4_DATA_DIR, "Materials", "AeroArmor", "Hero")),
    ]:
        os.makedirs(sub_dst, exist_ok=True)
        for fn in os.listdir(sub_src):
            src_f = os.path.join(sub_src, fn)
            if os.path.isfile(src_f):
                shutil.copy2(src_f, os.path.join(sub_dst, fn))

    # Eliminar cualquier resto del antiguo experimento ARTO (CosmosHeroCapeAO.nif / .ssf)
    for stale_dir in [
        MESH_OUT_DIR,
        os.path.join(FO4_DATA_DIR, "Meshes", "AeroArmor", "Hero"),
        os.path.join(THIS_DIR, "meshes", "AeroArmor", "Hero"),
    ]:
        for stale_fn in ("CosmosHeroCapeAO.nif", "CosmosHeroCapeAO.ssf"):
            stale_p = os.path.join(stale_dir, stale_fn)
            if os.path.exists(stale_p):
                os.remove(stale_p)

    # 3. Exportar mallas 3D en Blender 5.2 y compilar/inyectar física Havok Cloth (BSClothExtraData) en M/F
    print("[3/4] Exportando mallas 3D en Blender 5.2 e inyectando simulación Havok Cloth de capa completa...")
    preview_render_png = os.path.join(HERO_ASSETS_DIR, "qa_render_cosmos_hero_3views.png")
    blender_py_path = os.path.join(HERO_ASSETS_DIR, "_run_blender_cosmos_hero.py")
    script_code = (
        BLENDER_HERO_SCRIPT.replace("__TEST_DIR__", TEST_MESHES_DIR)
        .replace("__PREVIEW_CAPE_JSON__", "")
        .replace("__OUT_DIR__", MESH_OUT_DIR)
        .replace("__RENDER_PREVIEW__", preview_render_png)
        .replace("__PYNIFLY_DIR__", PYNIFLY_DIR)
    )
    with open(blender_py_path, "w", encoding="utf-8") as wf:
        wf.write(script_code)

    subprocess.run([BLENDER_EXE, "--background", "--python", blender_py_path], check=True)

    for suit_fn, is_fem in [("CosmosHeroSuitM.nif", False), ("CosmosHeroSuitF.nif", True)]:
        suit_p = os.path.join(MESH_OUT_DIR, suit_fn)
        hkx_cape = build_full_cape_hkx_for_nif(suit_p, is_female=is_fem)
        inject_bscloth_extradata_into_nif(suit_p, hkx_cape)

    # 4. Copiar archivos sueltos a Fallout 4\Data y al espejo local del workspace
    print("[4/4] Desplegando mallas, materiales y texturas en Fallout 4\\Data...")
    for sub_src, sub_dst in [
        (TEX_OUT_DIR, os.path.join(FO4_DATA_DIR, "Textures", "AeroArmor", "Hero")),
        (MAT_OUT_DIR, os.path.join(FO4_DATA_DIR, "Materials", "AeroArmor", "Hero")),
        (MESH_OUT_DIR, os.path.join(FO4_DATA_DIR, "Meshes", "AeroArmor", "Hero")),
        (MESH_OUT_DIR, os.path.join(THIS_DIR, "meshes", "AeroArmor", "Hero")),
    ]:
        os.makedirs(sub_dst, exist_ok=True)
        for fn in os.listdir(sub_src):
            src_f = os.path.join(sub_src, fn)
            if os.path.isfile(src_f):
                shutil.copy2(src_f, os.path.join(sub_dst, fn))

    # Verificar binariamente que las rutas .BGSM y bloques BSClothExtraData (hk_2014.1.0-r1) están incrustados
    for nif_chk, req_tokens in [
        (
            "CosmosHeroSuitM.nif",
            [b"CosmosHeroSuit.BGSM", b"CosmosHeroCape.BGSM", b"CosmosHeroGold.BGSM", b"BSClothExtraData", b"hk_2014.1.0-r1", b"Cape_Cloth_C_5"],
        ),
        (
            "CosmosHeroSuitF.nif",
            [b"CosmosHeroSuit.BGSM", b"CosmosHeroCape.BGSM", b"CosmosHeroGold.BGSM", b"BSClothExtraData", b"hk_2014.1.0-r1", b"Cape_Cloth_C_5"],
        ),
        ("CosmosHeroSuit1stM.nif", [b"CosmosHeroSuit.BGSM"]),
        ("CosmosHeroGlovesM.nif", [b"CosmosHeroGloves.BGSM"]),
        ("CosmosHeroSuitGO.nif", [b"CosmosHeroSuit.BGSM", b"CosmosHeroGold.BGSM"]),
    ]:
        with open(os.path.join(FO4_DATA_DIR, "Meshes", "AeroArmor", "Hero", nif_chk), "rb") as rf:
            raw_nif = rf.read()
        for req in req_tokens:
            assert req in raw_nif, f"ERROR: {req} no encontrado dentro de {nif_chk}"
    print("[Verificado] Todos los .NIF en Fallout 4\\Data contienen sus materiales .BGSM y física BSClothExtraData Havok 2014.")
    print("[OK] Todos los activos 3D del Traje de Vuelo Astro-Cosmos han sido generados e instalados.")


if __name__ == "__main__":
    build_and_deploy_cosmos_hero_assets(force_rebuild=False)
