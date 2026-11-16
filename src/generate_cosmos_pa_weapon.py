#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
generate_cosmos_pa_weapon.py
============================
Genera de forma 100 % autónoma (cero dependencias de Creation Club / terceros,
solo plantillas de nodos/BSConnectPoints de Fallout4 - Meshes.ba2) todos los
activos 3D PBR del arma aérea pesada exclusiva para la Servoarmadura Astro-Cosmos:
«Cañón Orbital Gauss Astro-Cosmos» (AeroArmor_CosmosPACannon):

  - Texturas 2048x2048 BC1/DXT1 (12 mipmaps) y mapas normales/especulares BC5/ATI2:
      * CosmosPAWeapArmor_d.dds / _n.dds / _s.dds     (Blindaje Hexagonal Azul-Acero Orbital con remaches)
      * CosmosPAWeapTitanium_d.dds / _n.dds / _s.dds  (Titanio Oscuro Hidráulico y Carmesí Táctico)
      * CosmosPAWeapGold_d.dds / _n.dds / _s.dds      (Oro-Bronce Aeroespacial Bruñido 24k para bobinas y rieles)
      * CosmosPAWeapSolarGlow_d.dds / _n.dds / _s.dds (Núcleo de Plasma Solar-Dorado Incandescente autoiluminado)
      * CosmosPAWeapLens_d.dds / _n.dds / _s.dds      (Lente Óptica de Observatorio Orbital Zafiro-Iridio)
  - Materiales binarios BGSM v2 en Materials\AeroArmor\PAWeapon\:
      * CosmosPAWeapArmor.BGSM, CosmosPAWeapTitanium.BGSM, CosmosPAWeapGold.BGSM,
        CosmosPAWeapSolarGlow.BGSM (emitEnabled=True), CosmosPAWeapLens.BGSM
  - 6 Piezas Modulares 3D .NIF esculpidas desde cero en Blender 5.2 LTS + PyNifly 30.2.0
    en Meshes\Weapons\AeroArmor\PACannon\ (preservando nodos animados y BSConnectPoints):
      * CosmosPACannonBase.nif    (Chasis hexagonal pesado de doble lomo + trinchera de plasma solar + escudos alados Capitán Cosmos + cerrojo/tambor animados)
      * CosmosPABarrelShroud.nif  (3 Anillos Magnéticos de Saturno + góndolas criogénicas laterales + núcleo acelerador solar)
      * CosmosPACapacitorMag.nif  (6 Condensadores Solares Tokamak laterales con ventanillas de plasma y abrazaderas de oro)
      * CosmosPAGauntletStock.nif (Culata hidráulica acorazada para guantelete de Servoarmadura con doble pistón amortiguador)
      * CosmosPAOrbitalScope.nif  (Visor telescópico hexagonal orbital 8x de reconocimiento + telémetros gemelos + Screen024 intacto)
      * CosmosPASolarMuzzle.nif   (Acelerador cuadrupolar en voladizo de 4 rieles magnéticos + doble halo de contención solar)
"""

import math
import os
import shutil
import struct
import subprocess
import sys
import zlib
import numpy as np
from PIL import Image

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_MESHES_DIR = os.path.join(THIS_DIR, "tools_3d", "test_meshes")
FO4_DATA_DIR = r"C:\Program Files (x86)\Steam\steamapps\common\Fallout 4\Data"
FO4_MESHES_BA2 = os.path.join(FO4_DATA_DIR, "Fallout4 - Meshes.ba2")

WEAP_ASSETS_DIR = os.path.join(THIS_DIR, "cosmos_pa_weapon_assets")
REF_SCAFFOLDS_DIR = os.path.join(WEAP_ASSETS_DIR, "ref_scaffolds")
TEX_OUT_DIR = os.path.join(WEAP_ASSETS_DIR, "textures", "AeroArmor", "PAWeapon")
MAT_OUT_DIR = os.path.join(WEAP_ASSETS_DIR, "materials", "AeroArmor", "PAWeapon")
MESH_OUT_DIR = os.path.join(WEAP_ASSETS_DIR, "meshes", "Weapons", "AeroArmor", "PACannon")

BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
PYNIFLY_DIR = r"C:\Users\educa\AppData\Roaming\Blender Foundation\Blender\5.2\scripts\addons\io_scene_nifly"

if PYNIFLY_DIR not in sys.path:
    sys.path.insert(0, PYNIFLY_DIR)
from pyn import pynifly

# Importar codificadores DDS BC1/BC5, generador BGSM v2 e inyector BSConnectPoint verificados
from generate_cosmos_hero_weapon import (
    write_bc1_dds_from_image,
    write_bc5_dds_from_rg_arrays,
    build_bgsm_v2_bytes,
    _height_to_normal_rg,
    ensure_connect_points_from_scaffold,
)
from fallout_pbr_weathering import (
    tileable_fbm,
    cellular_chip_mask,
    directional_scratches_and_drips,
    height_to_bc5_normal,
    weather_painted_metal,
    weather_antique_brass,
)


# ==============================================================================
# 0. EXTRACCIÓN DE PLANTILLAS DE NODOS DESDE FALLOUT4 - MESHES.BA2
# ==============================================================================
def extract_vanilla_scaffolds() -> None:
    """Extrae las 6 mallas modulares de GaussRifle únicamente como andamiaje de nodos y BSConnectPoints."""
    os.makedirs(REF_SCAFFOLDS_DIR, exist_ok=True)
    needed = {
        r"meshes\weapons\gaussrifle\gaussrifle.nif": "gaussrifle.nif",
        r"meshes\weapons\gaussrifle\gaussriflebarrelshroud.nif": "GaussRifleBarrelShroud.nif",
        r"meshes\weapons\gaussrifle\gaussriflemagsmall.nif": "gaussriflemagsmall.nif",
        r"meshes\weapons\gaussrifle\gaussriflerecoilgrip.nif": "GaussRifleRecoilGrip.nif",
        r"meshes\weapons\reconscope\pistol_scope_gauss.nif": "pistol_scope_gauss.nif",
        r"meshes\weapons\gaussrifle\gaussriflesuppressorshort.nif": "GaussRifleSuppressorShort.nif",
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
            print(f"[PA Scaffold Extracted] {out_name} ({len(raw):,} B)")


# ==============================================================================
# 1. GENERACIÓN PROCEDURAL DE TEXTURAS PBR 2048x2048 Y MATERIALES BGSM V2
# ==============================================================================
def generate_pa_weapon_textures_and_materials() -> None:
    os.makedirs(TEX_OUT_DIR, exist_ok=True)
    os.makedirs(MAT_OUT_DIR, exist_ok=True)

    N = 2048
    rng = np.random.default_rng(20771023)
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    u = xx / float(N)
    v = yy / float(N)

    # Desgaste Fallout 4 realista: ruido fBm acoplado, arañazos y escorrentías de suciedad
    fbm_macro = tileable_fbm(N, N, base_cells=8, octaves=4, persistence=0.54, seed=20771023)
    scratch, drip = directional_scratches_and_drips(N, N, seed=20771024)

    # 1. CosmosPAWeapArmor: Blindaje Pesado Azul Pizarra Aeroespacial Curtido con remaches y desconchados de acero
    plate_seams = (
        (np.abs(((u * 6.0) % 1.0) - 0.5) > 0.486)
        | (np.abs(((v * 6.0) % 1.0) - 0.5) > 0.486)
    ).astype(np.float32)
    seam_rim = (
        (np.abs(((u * 6.0) % 1.0) - 0.5) > 0.466)
        | (np.abs(((v * 6.0) % 1.0) - 0.5) > 0.466)
    ).astype(np.float32) * (1.0 - plate_seams)
    hx = (u * 24.0) % 1.0 - 0.5
    hy = (v * 24.0) % 1.0 - 0.5
    rivets = ((hx * hx + hy * hy) < 0.0055).astype(np.float32) * (1.0 - plate_seams)
    seam_grime = np.clip(plate_seams * 0.90 + seam_rim * 0.42 + drip * 0.48, 0.0, 1.0)

    armor_rgb, armor_dh, armor_spec_r, armor_gloss_g = weather_painted_metal(
        base_rgb=(30.0, 52.0, 86.0),
        edge_wear_mask=np.clip(seam_rim * 0.65 + rivets * 0.85, 0.0, 1.0),
        cavity_mask=seam_grime,
        h=N,
        w=N,
        seed=20771023,
        chip_amount=0.34,
        grime_amount=0.40,
        rust_amount=0.22,
    )
    armor_d = np.clip(armor_rgb, 6.0, 232.0).astype(np.uint8)
    armor_h = armor_dh + fbm_macro * 0.35 - plate_seams * 2.6 + rivets * 1.7
    armor_img = Image.fromarray(armor_d, mode="RGB")
    armor_img.save(os.path.join(WEAP_ASSETS_DIR, "preview_pa_armor_d.png"))
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "CosmosPAWeapArmor_d.dds"), armor_img)

    an_r, an_g = height_to_bc5_normal(armor_h, strength=2.6)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosPAWeapArmor_n.dds"), an_r, an_g)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosPAWeapArmor_s.dds"), armor_spec_r, armor_gloss_g)

    # 2. CosmosPAWeapTitanium: Carmesí Táctico Esmaltado Curtido y Estriado Hidráulico con grasa de taller
    rib = np.sin(v * math.pi * 48.0)
    rib_top = np.clip((rib - 0.15) * 1.15, 0.0, 1.0)
    rib_trough = np.clip((-rib - 0.10) * 1.15, 0.0, 1.0)
    ti_rgb, ti_dh, ti_spec_r, ti_gloss_g = weather_painted_metal(
        base_rgb=(112.0, 24.0, 26.0),
        edge_wear_mask=rib_top * 0.45,
        cavity_mask=np.clip(rib_trough * 0.65 + drip * 0.35, 0.0, 1.0),
        h=N,
        w=N,
        seed=20771024,
        chip_amount=0.30,
        grime_amount=0.42,
        rust_amount=0.16,
    )
    ti_d = np.clip(ti_rgb, 6.0, 224.0).astype(np.uint8)
    ti_h = ti_dh + rib * 1.6 + fbm_macro * 0.25
    ti_img = Image.fromarray(ti_d, mode="RGB")
    ti_img.save(os.path.join(WEAP_ASSETS_DIR, "preview_pa_titanium_d.png"))
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "CosmosPAWeapTitanium_d.dds"), ti_img)

    tn_r, tn_g = height_to_bc5_normal(ti_h, strength=2.6)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosPAWeapTitanium_n.dds"), tn_r, tn_g)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosPAWeapTitanium_s.dds"), ti_spec_r, ti_gloss_g)

    # 3. CosmosPAWeapGold: Latón/Bronce Antiguo Envejecido de Pre-Guerra (cero amarillo plástico)
    coil_line = 0.45 * np.sin(xx * 0.65) + 0.25 * np.sin(yy * 0.35)
    gold_rgb, gold_dh, gold_spec_r, gold_gloss_g = weather_antique_brass(
        h=N,
        w=N,
        cavity_mask=np.clip(drip * 0.40, 0.0, 1.0),
        seed=20771025,
    )
    gold_d = np.clip(gold_rgb, 12.0, 212.0).astype(np.uint8)
    gold_h = gold_dh + coil_line * 0.28 + fbm_macro * 0.25 - scratch * 0.25
    gold_img = Image.fromarray(gold_d, mode="RGB")
    gold_img.save(os.path.join(WEAP_ASSETS_DIR, "preview_pa_gold_d.png"))
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "CosmosPAWeapGold_d.dds"), gold_img)

    gn_r, gn_g = height_to_bc5_normal(gold_h, strength=1.9)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosPAWeapGold_n.dds"), gn_r, gn_g)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosPAWeapGold_s.dds"), gold_spec_r, gold_gloss_g)

    # 4. CosmosPAWeapSolarGlow: Núcleo de Plasma Solar con desgaste térmico en los bordes del ánodo
    pulse = 0.5 + 0.5 * np.cos(v * math.pi * 16.0)
    core_band = np.exp(-((u - 0.5) ** 2) / 0.08)
    burn_edge = np.clip((fbm_macro - 0.52) * 1.4 + np.abs(u - 0.5) * 0.45, 0.0, 1.0)
    sw_r = np.clip((218.0 + pulse * 26.0) * (1.0 - 0.28 * burn_edge), 130, 248)
    sw_g = np.clip((144.0 + pulse * 46.0 + core_band * 18.0) * (1.0 - 0.36 * burn_edge), 76, 214)
    sw_b = np.clip((34.0 + pulse * 52.0 + core_band * 46.0) * (1.0 - 0.40 * burn_edge), 18, 138)
    solar_img = Image.fromarray(np.stack([sw_r, sw_g, sw_b], axis=2).astype(np.uint8), mode="RGB")
    solar_img.save(os.path.join(WEAP_ASSETS_DIR, "preview_pa_solar_d.png"))
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "CosmosPAWeapSolarGlow_d.dds"), solar_img)

    sn_r, sn_g = height_to_bc5_normal(pulse * 0.45 + fbm_macro * 0.20, strength=1.4)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosPAWeapSolarGlow_n.dds"), sn_r, sn_g)
    ss_spec = np.clip(148.0 - burn_edge * 55.0, 65.0, 162.0)
    ss_gloss = np.clip(160.0 - burn_edge * 60.0, 72.0, 174.0)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosPAWeapSolarGlow_s.dds"), ss_spec, ss_gloss)

    # 5. CosmosPAWeapLens: Lente óptica zafiro antirreflejos con retícula fina y polvo perimetral del Yermo
    dx = u - 0.5
    dy = v - 0.5
    rad = np.sqrt(dx * dx + dy * dy) * 2.0
    edge_dust = np.clip((rad - 0.68) * 2.2 + (fbm_macro - 0.5) * 0.45, 0.0, 1.0)
    ring_etch = ((np.abs(rad - 0.48) < 0.008) | (np.abs(rad - 0.74) < 0.007)).astype(np.float32)
    radial_fade = 1.0 - np.clip(rad, 0.0, 1.0)
    ln_r = np.clip(28.0 + radial_fade * 28.0 + ring_etch * 56.0 + edge_dust * 18.0 - scratch * 8.0, 16, 118)
    ln_g = np.clip(44.0 + radial_fade * 42.0 + ring_etch * 66.0 + edge_dust * 14.0 - scratch * 8.0, 24, 138)
    ln_b = np.clip(82.0 + radial_fade * 64.0 + ring_etch * 48.0 - edge_dust * 24.0 - scratch * 12.0, 38, 172)
    lens_img = Image.fromarray(np.stack([ln_r, ln_g, ln_b], axis=2).astype(np.uint8), mode="RGB")
    lens_img.save(os.path.join(WEAP_ASSETS_DIR, "preview_pa_lens_d.png"))
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "CosmosPAWeapLens_d.dds"), lens_img)

    ln_nr, ln_ng = height_to_bc5_normal(ring_etch * 0.25 + edge_dust * 0.30 - scratch * 0.35, strength=1.2)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosPAWeapLens_n.dds"), ln_nr, ln_ng)
    ls_spec = np.clip(186.0 - edge_dust * 120.0 - scratch * 45.0, 40.0, 198.0)
    ls_gloss = np.clip(198.0 - edge_dust * 130.0 - scratch * 50.0, 45.0, 210.0)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "CosmosPAWeapLens_s.dds"), ls_spec, ls_gloss)

    bgsm_specs = [
        (
            "CosmosPAWeapArmor.BGSM",
            dict(
                diffuse_path="AeroArmor/PAWeapon/CosmosPAWeapArmor_d.dds",
                normal_path="AeroArmor/PAWeapon/CosmosPAWeapArmor_n.dds",
                specular_path="AeroArmor/PAWeapon/CosmosPAWeapArmor_s.dds",
                envmap_path="Shared/Cubemaps/mipblur_DefaultOutside1.dds",
                envmap_scale=0.62,
                specular_color=(0.86, 0.90, 0.96),
                specular_mult=1.05,
                smoothness=0.95,
            ),
        ),
        (
            "CosmosPAWeapTitanium.BGSM",
            dict(
                diffuse_path="AeroArmor/PAWeapon/CosmosPAWeapTitanium_d.dds",
                normal_path="AeroArmor/PAWeapon/CosmosPAWeapTitanium_n.dds",
                specular_path="AeroArmor/PAWeapon/CosmosPAWeapTitanium_s.dds",
                envmap_path="Shared/Cubemaps/mipblur_DefaultOutside1.dds",
                envmap_scale=0.38,
                specular_color=(0.94, 0.86, 0.84),
                specular_mult=0.92,
                smoothness=0.88,
            ),
        ),
        (
            "CosmosPAWeapGold.BGSM",
            dict(
                diffuse_path="AeroArmor/PAWeapon/CosmosPAWeapGold_d.dds",
                normal_path="AeroArmor/PAWeapon/CosmosPAWeapGold_n.dds",
                specular_path="AeroArmor/PAWeapon/CosmosPAWeapGold_s.dds",
                envmap_path="Shared/Cubemaps/mipblur_DefaultOutside1.dds",
                envmap_scale=0.84,
                specular_color=(0.96, 0.80, 0.44),
                specular_mult=1.18,
                smoothness=1.04,
            ),
        ),
        (
            "CosmosPAWeapSolarGlow.BGSM",
            dict(
                diffuse_path="AeroArmor/PAWeapon/CosmosPAWeapSolarGlow_d.dds",
                normal_path="AeroArmor/PAWeapon/CosmosPAWeapSolarGlow_n.dds",
                specular_path="AeroArmor/PAWeapon/CosmosPAWeapSolarGlow_s.dds",
                envmap_path="Shared/Cubemaps/mipblur_DefaultOutside1.dds",
                envmap_scale=0.60,
                specular_color=(0.96, 0.84, 0.56),
                specular_mult=1.05,
                smoothness=1.10,
                emit_enabled=True,
                emit_color=(0.95, 0.66, 0.16),
                emit_mult=1.55,
            ),
        ),
        (
            "CosmosPAWeapLens.BGSM",
            dict(
                diffuse_path="AeroArmor/PAWeapon/CosmosPAWeapLens_d.dds",
                normal_path="AeroArmor/PAWeapon/CosmosPAWeapLens_n.dds",
                specular_path="AeroArmor/PAWeapon/CosmosPAWeapLens_s.dds",
                envmap_path="Shared/Cubemaps/shinyglass_e.dds",
                envmap_scale=1.25,
                specular_color=(0.68, 0.86, 0.98),
                specular_mult=1.35,
                smoothness=1.45,
                emit_enabled=True,
                emit_color=(0.14, 0.42, 0.78),
                emit_mult=0.28,
            ),
        ),
    ]
    for bgsm_name, kw in bgsm_specs:
        raw_b = build_bgsm_v2_bytes(**kw)
        with open(os.path.join(MAT_OUT_DIR, bgsm_name), "wb") as wf:
            wf.write(raw_b)
        print(f"[PA BGSM Created] {bgsm_name} ({len(raw_b)} B)")


# ==============================================================================
# 2. SCRIPT BLENDER 5.2 LTS + PYNIFLY: ESCULPIDO PESADO DE 6 PIEZAS + QA 4 VISTAS
# ==============================================================================
BLENDER_PA_CANNON_SCRIPT = r'''
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
    for lt in list(bpy.data.lights):
        bpy.data.lights.remove(lt)
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


def create_pa_cannon_materials() -> dict:
    return {
        "armor": make_fo4_material(
            "CosmosPAWeapArmor",
            r"Materials\AeroArmor\PAWeapon\CosmosPAWeapArmor.BGSM",
            r"textures\AeroArmor\PAWeapon\CosmosPAWeapArmor_d.dds",
            r"textures\AeroArmor\PAWeapon\CosmosPAWeapArmor_n.dds",
            r"textures\AeroArmor\PAWeapon\CosmosPAWeapArmor_s.dds",
        ),
        "titanium": make_fo4_material(
            "CosmosPAWeapTitanium",
            r"Materials\AeroArmor\PAWeapon\CosmosPAWeapTitanium.BGSM",
            r"textures\AeroArmor\PAWeapon\CosmosPAWeapTitanium_d.dds",
            r"textures\AeroArmor\PAWeapon\CosmosPAWeapTitanium_n.dds",
            r"textures\AeroArmor\PAWeapon\CosmosPAWeapTitanium_s.dds",
        ),
        "gold": make_fo4_material(
            "CosmosPAWeapGold",
            r"Materials\AeroArmor\PAWeapon\CosmosPAWeapGold.BGSM",
            r"textures\AeroArmor\PAWeapon\CosmosPAWeapGold_d.dds",
            r"textures\AeroArmor\PAWeapon\CosmosPAWeapGold_n.dds",
            r"textures\AeroArmor\PAWeapon\CosmosPAWeapGold_s.dds",
            r"textures\Shared\Cubemaps\mipblur_DefaultOutside1.dds",
        ),
        "solar": make_fo4_material(
            "CosmosPAWeapSolarGlow",
            r"Materials\AeroArmor\PAWeapon\CosmosPAWeapSolarGlow.BGSM",
            r"textures\AeroArmor\PAWeapon\CosmosPAWeapSolarGlow_d.dds",
            r"textures\AeroArmor\PAWeapon\CosmosPAWeapSolarGlow_n.dds",
            r"textures\AeroArmor\PAWeapon\CosmosPAWeapSolarGlow_s.dds",
            r"textures\Shared\Cubemaps\mipblur_DefaultOutside1.dds",
        ),
        "lens": make_fo4_material(
            "CosmosPAWeapLens",
            r"Materials\AeroArmor\PAWeapon\CosmosPAWeapLens.BGSM",
            r"textures\AeroArmor\PAWeapon\CosmosPAWeapLens_d.dds",
            r"textures\AeroArmor\PAWeapon\CosmosPAWeapLens_n.dds",
            r"textures\AeroArmor\PAWeapon\CosmosPAWeapLens_s.dds",
            r"textures\Shared\Cubemaps\shinyglass_e.dds",
        ),
    }


def finalize_bmesh_object(bm: bmesh.types.BMesh, obj_name: str, mat, parent_obj, smooth: bool = True):
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    uv_layer = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = f.normal
        ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
        face_uvs = []
        for lp in f.loops:
            co = lp.vert.co
            if ax >= ay and ax >= az:
                face_uvs.append((co.y * 0.032, co.z * 0.032))
            elif az >= ax and az >= ay:
                face_uvs.append((co.x * 0.032, co.y * 0.032))
            else:
                face_uvs.append((co.x * 0.032, co.z * 0.032))
        u_off = math.floor(sum(uv[0] for uv in face_uvs) / len(face_uvs))
        v_off = math.floor(sum(uv[1] for uv in face_uvs) / len(face_uvs))
        for lp, (fu, fv) in zip(f.loops, face_uvs):
            lp[uv_layer].uv = (fu - u_off, fv - v_off)

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
    n_seg: int = 24,
    cap_start: bool = True,
    cap_end: bool = True,
    superellipse_p: float = 2.0,
    rail_trench: bool = False,
):
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
            # Trinchera electromagnética central superior abierta entre Y=11..53
            if rail_trench and (10.5 <= y <= 53.5) and abs(px) < 1.75 and pz > 6.6:
                pz = 6.2
            ring.append(bm.verts.new((px, y, pz)))
        rings.append(ring)

    for r_idx in range(len(rings) - 1):
        r0 = rings[r_idx]
        r1 = rings[r_idx + 1]
        for i in range(n_seg):
            ni = (i + 1) % n_seg
            bm.faces.new((r0[i], r0[ni], r1[ni], r1[i]))

    if cap_start and rings:
        c0 = stations[0]
        vc0 = bm.verts.new((c0[0], c0[1], c0[2]))
        r0 = rings[0]
        for i in range(n_seg):
            ni = (i + 1) % n_seg
            bm.faces.new((vc0, r0[ni], r0[i]))

    if cap_end and rings:
        ce = stations[-1]
        vce = bm.verts.new((ce[0], ce[1], ce[2]))
        re = rings[-1]
        for i in range(n_seg):
            ni = (i + 1) % n_seg
            bm.faces.new((vce, re[i], re[ni]))


def add_cylinder_z(
    bm: bmesh.types.BMesh,
    cx: float,
    cy: float,
    z0: float,
    z1: float,
    rx: float,
    ry: float,
    n_seg: int = 24,
    superellipse_p: float = 2.2,
):
    rings = []
    for z in (z0, 0.5 * (z0 + z1), z1):
        ring = []
        sh = 1.0 if z == 0.5 * (z0 + z1) else 0.93
        for i in range(n_seg):
            ang = (2.0 * math.pi * i) / n_seg
            ca, sa = math.cos(ang), math.sin(ang)
            sx = math.copysign(abs(ca) ** (2.0 / superellipse_p), ca) * rx * sh
            sy = math.copysign(abs(sa) ** (2.0 / superellipse_p), sa) * ry * sh
            ring.append(bm.verts.new((cx + sx, cy + sy, z)))
        rings.append(ring)
    for ri in range(2):
        for i in range(n_seg):
            ni = (i + 1) % n_seg
            bm.faces.new((rings[ri][i], rings[ri][ni], rings[ri + 1][ni], rings[ri + 1][i]))
    vb = bm.verts.new((cx, cy, z0))
    vt = bm.verts.new((cx, cy, z1))
    for i in range(n_seg):
        ni = (i + 1) % n_seg
        bm.faces.new((vb, rings[0][ni], rings[0][i]))
        bm.faces.new((vt, rings[-1][i], rings[-1][ni]))


def add_torus_ring_y(
    bm: bmesh.types.BMesh,
    cx: float,
    cy: float,
    cz: float,
    major_r: float,
    minor_r_x: float,
    minor_r_y: float,
    n_major: int = 32,
    n_minor: int = 14,
):
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


def add_swept_fin(
    bm: bmesh.types.BMesh,
    profile_yz: list,
    half_thick_base: float,
    half_thick_tip: float,
    x_offset: float = 0.0,
    tilt_rad: float = 0.0,
):
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


def add_winged_cosmos_crest_x(
    bm: bmesh.types.BMesh,
    x_base: float,
    cy: float,
    cz: float,
    sign_x: float,
):
    """Escudo alado 3D en alto relieve de la Flota Orbital del Capitán Cosmos en los flancos pesados."""
    # Estrella central de 8 puntas + alas barridas hacia adelante/atrás
    pts = 16
    base_ring = []
    top_ring = []
    for i in range(pts):
        ang = (2.0 * math.pi * i) / pts
        rad = 2.05 if (i % 2 == 0) else 0.78
        if i in (0, 8):
            rad *= 2.15  # Grandes alas horizontales de crucero orbital
        elif i in (2, 6, 10, 14):
            rad *= 1.18
        py = cy + rad * math.cos(ang)
        pz = cz + rad * math.sin(ang)
        base_ring.append(bm.verts.new((x_base, py, pz)))
        top_ring.append(bm.verts.new((x_base + sign_x * 0.24, cy + rad * 0.76 * math.cos(ang), cz + rad * 0.76 * math.sin(ang))))

    apex = bm.verts.new((x_base + sign_x * 0.38, cy, cz))
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
        import_animations=False,
        import_cutpoints=False,
        import_tris=False,
        import_collisions=False,
    )
    for obj in list(bpy.data.objects):
        if obj.type == "MESH" and obj.name not in keep_mesh_names:
            bpy.data.objects.remove(obj, do_unlink=True)
        elif obj.type == "LIGHT" or obj.name.startswith("GaussNixieLight"):
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
    print(f"[Blender PA Exported] {dst_fn}")


# ------------------------------------------------------------------------------
# PIEZA 1: CHASIS ORBITAL PESADO DE DOBLE RIEL (CosmosPACannonBase.nif)
# ------------------------------------------------------------------------------
def build_cosmos_pa_cannon_base():
    import_scaffold_and_prune("gaussrifle.nif")
    mats = create_pa_cannon_materials()

    rec_node = bpy.data.objects["GaussRifleReceiver"]
    bolt_node = bpy.data.objects["WeaponBolt"]
    mag_node = bpy.data.objects["WeaponMagazine"]
    trig_node = bpy.data.objects["WeaponTrigger"]

    # 1A. Chasis Hexagonal Acorazado Pesado (Y = -4.9 .. +53.3, Z = -3.8 .. +10.5)
    #     Con trinchera electromagnética central abierta en el lomo para exponer el plasma solar.
    bm_hull = bmesh.new()
    hull_stations = [
        (0.0, -4.90, 4.10, 2.65, 3.80),
        (0.0, -2.50, 4.65, 3.85, 5.15),
        (0.0,  2.50, 5.10, 4.75, 5.55),
        (0.0,  9.80, 4.95, 4.95, 5.35),
        (0.0, 18.00, 4.75, 4.65, 5.05),
        (0.0, 30.00, 4.85, 4.45, 4.85),
        (0.0, 44.00, 5.15, 4.05, 4.35),
        (0.0, 53.30, 5.45, 3.45, 3.65),
    ]
    add_lofted_tube(bm_hull, hull_stations, n_seg=24, superellipse_p=3.5, rail_trench=True)

    # Puente dorsal de telemetría bajo P-Scope (Y = -3.8 .. +5.2, Z = 9.0 .. 10.72)
    add_lofted_tube(
        bm_hull,
        [
            (0.0, -3.85, 10.05, 1.85, 0.72),
            (0.0, -0.16, 10.18, 2.05, 0.68),
            (0.0,  3.80, 10.12, 1.95, 0.68),
            (0.0,  6.20,  9.45, 1.55, 0.55),
        ],
        n_seg=16,
        superellipse_p=3.8,
    )

    # Guardamanos inferior pesado para guantelete izquierdo de Servoarmadura (Y = +10 .. +34, Z = -2.8 .. +1.2)
    add_lofted_tube(
        bm_hull,
        [
            (0.0,  8.50, -0.35, 2.55, 1.65),
            (0.0, 13.50, -1.35, 3.15, 2.35),
            (0.0, 25.50, -1.45, 3.15, 2.35),
            (0.0, 33.50, -0.45, 2.45, 1.55),
        ],
        n_seg=20,
        superellipse_p=3.2,
    )
    obj_hull = finalize_bmesh_object(bm_hull, "CosmosPAHull:0", mats["armor"], rec_node)

    # 1B. Rieles Colectores Gemelos en Oro 24k + Escudos Alados Capitán Cosmos + Arcos Dorsales
    bm_gold = bmesh.new()
    for sx in (-1.0, 1.0):
        # Barra colectora electromagnética longitudinal (Y = +10.5 .. +53.6, Z = +8.55)
        add_lofted_tube(
            bm_gold,
            [
                (sx * 2.35, 10.20, 8.45, 0.62, 0.68),
                (sx * 2.28, 32.00, 8.55, 0.58, 0.65),
                (sx * 2.15, 53.65, 8.55, 0.52, 0.60),
            ],
            n_seg=16,
            superellipse_p=3.4,
        )
        # Moldura dorada de flanco y escudo alado del Capitán Cosmos en X = ±4.92, Y = +8.2, Z = +4.4
        add_winged_cosmos_crest_x(bm_gold, sx * 4.86, 6.80, 4.45, sx)

    # 4 Costillas de contención magnética doradas sobre la trinchera (Z_max = +9.85, muy por debajo del visor Z=13.54)
    for cy_rib in (16.5, 25.5, 35.5, 46.5):
        add_lofted_tube(
            bm_gold,
            [(0.0, cy_rib - 0.65, 8.95, 2.95, 0.62), (0.0, cy_rib + 0.65, 8.95, 2.95, 0.62)],
            n_seg=16,
            superellipse_p=3.4,
        )
    finalize_bmesh_object(bm_gold, "CosmosPAGoldRails:0", mats["gold"], rec_node)

    # 1C. Paneles Tácticos Carmesí en la Recámara Trasera y Guardamanos de Guantelete PA
    bm_tit = bmesh.new()
    add_lofted_tube(
        bm_tit,
        [
            (0.0, 14.20, -2.55, 2.65, 1.25),
            (0.0, 24.80, -2.55, 2.65, 1.25),
        ],
        n_seg=18,
        superellipse_p=3.2,
    )
    for sx in (-1.0, 1.0):
        add_lofted_tube(
            bm_tit,
            [
                (sx * 4.65, -2.20, 3.85, 0.42, 1.75),
                (sx * 4.78,  2.20, 3.95, 0.42, 1.85),
            ],
            n_seg=14,
            superellipse_p=3.0,
        )
    finalize_bmesh_object(bm_tit, "CosmosPATitaniumTrim:0", mats["titanium"], rec_node)

    # 1D. Conducto Central de Plasma Solar-Dorado Incandescente (Y = -1.5 .. +53.7, eje de cañón Z = +6.98)
    bm_solar = bmesh.new()
    add_lofted_tube(
        bm_solar,
        [
            (0.0, -1.20, 6.98, 1.38, 1.25),
            (0.0, 18.00, 6.98, 1.32, 1.22),
            (0.0, 38.00, 6.98, 1.22, 1.15),
            (0.0, 53.72, 6.98, 1.05, 1.05),
        ],
        n_seg=24,
    )
    # Indicador holográfico solar trasero para el artillero (sustituye los tubos nixie rotos por panel solar limpio)
    add_lofted_tube(
        bm_solar,
        [(0.0, -4.98, 6.95, 1.65, 0.95), (0.0, -4.45, 6.95, 1.75, 1.02)],
        n_seg=18,
        superellipse_p=3.0,
    )
    finalize_bmesh_object(bm_solar, "CosmosPASolarCore:0", mats["solar"], rec_node)

    # 1E. Carro Electromagnético Animado bajo WeaponBolt (-0.002, 43.908, 10.015)
    bm_bolt = bmesh.new()
    add_lofted_tube(
        bm_bolt,
        [
            (0.0, -33.50, -1.85, 1.25, 0.95),
            (0.0,  -8.00, -1.85, 1.25, 0.95),
            (0.0,   6.80, -1.85, 1.05, 0.80),
        ],
        n_seg=16,
        superellipse_p=3.0,
    )
    finalize_bmesh_object(bm_bolt, "CosmosPABolt:0", mats["gold"], bolt_node)

    # 1F. Tambor Nuclear Solar Animado bajo WeaponMagazine (-0.009, 6.561, 11.150)
    bm_mag = bmesh.new()
    add_cylinder_z(bm_mag, 0.0, -2.25, -3.75, 0.28, rx=3.15, ry=3.15, n_seg=24, superellipse_p=2.2)
    finalize_bmesh_object(bm_mag, "CosmosPAAnimDrum:0", mats["gold"], mag_node)

    bm_mag_glow = bmesh.new()
    add_cylinder_z(bm_mag_glow, 0.0, -2.25, -3.15, 0.40, rx=2.25, ry=2.25, n_seg=20, superellipse_p=2.0)
    finalize_bmesh_object(bm_mag_glow, "CosmosPAAnimDrumCore:0", mats["solar"], mag_node)

    # 1G. Gatillo Pesado Animado bajo WeaponTrigger (0.020, 2.140, 0.741)
    bm_trig = bmesh.new()
    add_swept_fin(
        bm_trig,
        [(-0.25, -0.05), (0.48, -0.05), (0.28, -1.82), (-0.22, -1.68)],
        half_thick_base=0.24,
        half_thick_tip=0.16,
    )
    finalize_bmesh_object(bm_trig, "CosmosPATrigger:0", mats["gold"], trig_node)

    export_current_nif("CosmosPACannonBase.nif", obj_hull)


# ------------------------------------------------------------------------------
# PIEZA 2: BLINDAJE MAGNÉTICO DE ANILLOS DE SATURNO (CosmosPABarrelShroud.nif)
#          Anclado en P-Barrel = (-0.002, 43.908, 10.015); eje del cañón en Z_local = -3.033
# ------------------------------------------------------------------------------
def build_cosmos_pa_barrel_shroud():
    import_scaffold_and_prune("GaussRifleBarrelShroud.nif")
    mats = create_pa_cannon_materials()
    root_node = get_root_or_node("GaussRifleBarrelShroud")

    bz = -3.033  # Eje exacto de P-Muzzle (Z_world = 6.982)

    # 2A. Góndolas Criogénicas Laterales Gemelas en Blindaje Azul-Acero (X = ±4.35, Y = -28.0 .. +2.5)
    bm_shroud = bmesh.new()
    for sx in (-1.0, 1.0):
        add_lofted_tube(
            bm_shroud,
            [
                (sx * 4.35, -28.20, bz, 1.15, 1.85),
                (sx * 4.55, -22.00, bz, 1.45, 2.25),
                (sx * 4.45,  -8.00, bz, 1.38, 2.10),
                (sx * 4.05,   2.40, bz, 0.95, 1.55),
            ],
            n_seg=18,
            superellipse_p=3.2,
        )
    # Quilla inferior acorazada que une ambas góndolas
    add_lofted_tube(
        bm_shroud,
        [
            (0.0, -27.50, bz - 2.65, 3.45, 0.95),
            (0.0,  -6.00, bz - 2.45, 3.25, 0.90),
            (0.0,   2.20, bz - 2.15, 2.65, 0.78),
        ],
        n_seg=18,
        superellipse_p=3.4,
    )
    obj_shroud = finalize_bmesh_object(bm_shroud, "CosmosPABarrelNacelles:0", mats["armor"], root_node)

    # 2B. 3 Grandes Anillos Toroidales de Saturno en Oro 24k (Z_world_max = 6.98 + 4.55 = 11.53 < 12.33 visor!)
    bm_rings = bmesh.new()
    for cy_r, maj_r, mx, my in [
        (-23.50, 4.55, 0.44, 0.78),
        (-13.50, 4.28, 0.42, 0.74),
        ( -3.50, 3.98, 0.40, 0.70),
    ]:
        add_torus_ring_y(bm_rings, 0.0, cy_r, bz, major_r=maj_r, minor_r_x=mx, minor_r_y=my, n_major=36, n_minor=16)
    finalize_bmesh_object(bm_rings, "CosmosPASaturnRings:0", mats["gold"], root_node)

    # 2C. Filamentos Solares Laterales en las Góndolas
    bm_glow = bmesh.new()
    for sx in (-1.0, 1.0):
        add_lofted_tube(
            bm_glow,
            [
                (sx * 5.65, -24.50, bz, 0.36, 0.68),
                (sx * 5.55,  -5.50, bz, 0.34, 0.62),
            ],
            n_seg=14,
            superellipse_p=2.6,
        )
    finalize_bmesh_object(bm_glow, "CosmosPABarrelGlow:0", mats["solar"], root_node)

    export_current_nif("CosmosPABarrelShroud.nif", obj_shroud)


# ------------------------------------------------------------------------------
# PIEZA 3: BATERÍA DE CONDENSADORES SOLARES TOKAMAK (CosmosPACapacitorMag.nif)
#          Anclada en P-Mag = (-0.009, 26.702, 6.756)
# ------------------------------------------------------------------------------
def build_cosmos_pa_capacitor_mag():
    import_scaffold_and_prune("gaussriflemagsmall.nif")
    mats = create_pa_cannon_materials()
    root_node = get_root_or_node("GaussRifleMagSmall")

    # 3 pares (6 cápsulas) de Condensadores Solares Tokamak flanqueando el chasis (X = ±4.25, Y = -12.5 .. +8.5)
    bm_caps = bmesh.new()
    bm_gold = bmesh.new()
    bm_solar = bmesh.new()

    for sx in (-1.0, 1.0):
        # Colector blindado longitudinal que soporta las 3 botellas Tokamak
        add_lofted_tube(
            bm_caps,
            [
                (sx * 3.65, -14.20, -1.65, 0.95, 1.55),
                (sx * 3.75,   9.20, -1.65, 0.95, 1.55),
            ],
            n_seg=16,
            superellipse_p=3.2,
        )
        for cy_pod in (-11.00, -2.50, 6.00):
            # Carcasa blindada superior e inferior de cada botella vertical
            add_cylinder_z(bm_caps, sx * 4.55, cy_pod, -3.20, -1.85, rx=1.45, ry=2.65, n_seg=22, superellipse_p=2.3)
            add_cylinder_z(bm_caps, sx * 4.55, cy_pod,  1.25,  2.55, rx=1.45, ry=2.65, n_seg=22, superellipse_p=2.3)
            # Núcleo incandescente de plasma solar visible en el centro de cada botella
            add_cylinder_z(bm_solar, sx * 4.55, cy_pod, -1.95, 1.35, rx=1.28, ry=2.35, n_seg=22, superellipse_p=2.1)
            # Anillos colectores de oro 24k
            add_cylinder_z(bm_gold, sx * 4.55, cy_pod, -1.90, -1.45, rx=1.54, ry=2.76, n_seg=22, superellipse_p=2.3)
            add_cylinder_z(bm_gold, sx * 4.55, cy_pod,  0.85,  1.30, rx=1.54, ry=2.76, n_seg=22, superellipse_p=2.3)

    obj_caps = finalize_bmesh_object(bm_caps, "CosmosPATokamakPods:0", mats["armor"], root_node)
    finalize_bmesh_object(bm_gold, "CosmosPATokamakGold:0", mats["gold"], root_node)
    finalize_bmesh_object(bm_solar, "CosmosPATokamakCore:0", mats["solar"], root_node)

    export_current_nif("CosmosPACapacitorMag.nif", obj_caps)


# ------------------------------------------------------------------------------
# PIEZA 4: CULATA HIDRÁULICA ACORAZADA PARA SERVOARMADURA (CosmosPAGauntletStock.nif)
#          Anclada en P-Grip = (0.000, -4.922, 3.826)
# ------------------------------------------------------------------------------
def build_cosmos_pa_gauntlet_stock():
    import_scaffold_and_prune("GaussRifleRecoilGrip.nif")
    mats = create_pa_cannon_materials()
    root_node = get_root_or_node("GaussRifleRecoilGrip")

    # 4A. Estructura Acorazada Trasera de Doble Viga (Y = -19.2 .. +9.5, Z = -11.2 .. +2.8)
    bm_stock = bmesh.new()
    # Viga superior de hombro
    add_lofted_tube(
        bm_stock,
        [
            (0.0, -18.80,  0.15, 1.55, 2.05),
            (0.0, -12.50,  0.65, 1.72, 1.95),
            (0.0,  -4.50,  1.05, 1.95, 2.05),
            (0.0,   1.80,  0.65, 2.15, 1.85),
        ],
        n_seg=20,
        superellipse_p=3.2,
    )
    # Viga inferior reforzada que enlaza cantonera con base del pistolete PA
    add_lofted_tube(
        bm_stock,
        [
            (0.0, -18.80, -7.85, 1.35, 1.45),
            (0.0, -11.00, -9.25, 1.35, 1.15),
            (0.0,  -1.80, -10.35, 1.55, 1.15),
            (0.0,   2.80, -10.45, 1.65, 1.05),
        ],
        n_seg=18,
        superellipse_p=3.2,
    )
    # Bloque macizo trasero de cantonera hidráulica
    add_lofted_tube(
        bm_stock,
        [(0.0, -19.35, -3.85, 1.68, 4.95), (0.0, -17.40, -3.85, 1.58, 4.65)],
        n_seg=22,
        superellipse_p=3.4,
    )
    obj_stock = finalize_bmesh_object(bm_stock, "CosmosPAStockFrame:0", mats["armor"], root_node)

    # 4B. Pistolete Sobredimensionado para Guantelete PA + Carrillera Táctica Carmesí
    bm_grip = bmesh.new()
    grip_rings = []
    # En coordenadas locales P-Grip (0, -4.922, 3.826), el gatillo está en Y_local ≈ +7.06, Z_local ≈ -3.08
    # y la mano derecha de PA agarra Y_local = [+0.5 .. +5.5], Z_local = [-10.8 .. -2.5]
    for cy_g, cz_g, rx_g, ry_g in [
        (1.65, -10.85, 1.52, 2.15),
        (2.15,  -8.60, 1.62, 2.25),
        (2.85,  -5.90, 1.66, 2.30),
        (3.45,  -3.20, 1.58, 2.15),
        (3.85,  -1.35, 1.52, 2.05),
    ]:
        ring = [
            bm_grip.verts.new(
                (rx_g * math.cos(2 * math.pi * i / 24), cy_g + ry_g * math.sin(2 * math.pi * i / 24), cz_g)
            )
            for i in range(24)
        ]
        grip_rings.append(ring)
    for ri in range(len(grip_rings) - 1):
        for i in range(24):
            ni = (i + 1) % 24
            bm_grip.faces.new((grip_rings[ri][i], grip_rings[ri][ni], grip_rings[ri + 1][ni], grip_rings[ri + 1][i]))
    vgb = bm_grip.verts.new((0.0, 1.65, -10.95))
    vgt = bm_grip.verts.new((0.0, 3.85, -1.25))
    for i in range(24):
        ni = (i + 1) % 24
        bm_grip.faces.new((vgb, grip_rings[0][ni], grip_rings[0][i]))
        bm_grip.faces.new((vgt, grip_rings[-1][i], grip_rings[-1][ni]))

    # Carrillera acorazada Carmesí
    add_lofted_tube(
        bm_grip,
        [
            (0.0, -15.80, 1.95, 1.35, 0.85),
            (0.0,  -6.20, 2.35, 1.45, 0.95),
        ],
        n_seg=18,
        superellipse_p=3.0,
    )
    finalize_bmesh_object(bm_grip, "CosmosPAStockGrip:0", mats["titanium"], root_node)

    # 4C. Doble Pistón Hidráulico Amortiguador, Cantonera y Guardamonte PA en Oro 24k
    bm_gold = bmesh.new()
    # 2 Pistones hidráulicos paralelos en el interior del bastidor de culata
    for zp in (-2.65, -5.25):
        add_lofted_tube(
            bm_gold,
            [(0.0, -17.60, zp, 0.72, 0.72), (0.0, -3.50, zp - 0.65, 0.72, 0.72)],
            n_seg=16,
        )
    # Cantonera dorada pesada
    add_lofted_tube(
        bm_gold,
        [(0.0, -20.25, -3.85, 1.76, 5.15), (0.0, -19.30, -3.85, 1.76, 5.05)],
        n_seg=22,
        superellipse_p=3.4,
    )
    # Guardamonte amplio para dedo índice blindado de Servoarmadura (Y_local = +4.8 .. +10.2, Z_local = -6.2 .. -2.0)
    add_lofted_tube(
        bm_gold,
        [
            (0.0,  4.80, -5.85, 0.68, 0.36),
            (0.0,  7.40, -6.15, 0.68, 0.36),
            (0.0,  9.85, -4.85, 0.68, 0.36),
            (0.0, 10.45, -2.15, 0.68, 0.42),
        ],
        n_seg=16,
        superellipse_p=3.0,
    )
    finalize_bmesh_object(bm_gold, "CosmosPAStockHydraulics:0", mats["gold"], root_node)

    export_current_nif("CosmosPAGauntletStock.nif", obj_stock)


# ------------------------------------------------------------------------------
# PIEZA 5: VISOR TELESCÓPICO ORBITAL ASTRO-COSMOS 8X (CosmosPAOrbitalScope.nif)
#          Anclado en P-Scope = WeaponOptics1 (0.000, -0.161, 10.721)
#          CRÍTICO: Preservar Screen024:0 y Screen024:1 intactos en (0.135, -3.901, 2.820)
# ------------------------------------------------------------------------------
def build_cosmos_pa_orbital_scope():
    import_scaffold_and_prune("pistol_scope_gauss.nif", keep_mesh_names={"Screen024:0", "Screen024:1"})
    mats = create_pa_cannon_materials()
    root_node = get_root_or_node("GaussRifleReconScope")

    ox, oz = 0.135, 2.820

    # 5A. Carcasa Hexagonal Acorazada de Observatorio Orbital (tapa trasera sellada delante de Screen024 en Y=-3.901)
    bm_scope = bmesh.new()
    scope_stations = [
        (ox, -3.76, oz, 1.50, 1.46),
        (ox, -2.90, oz, 1.56, 1.52),
        (ox, -1.80, oz, 1.38, 1.38),
        (ox,  2.60, oz, 1.42, 1.42),
        (ox,  3.85, oz, 1.92, 1.88),
        (ox,  6.35, oz, 2.12, 2.06),
    ]
    add_lofted_tube(bm_scope, scope_stations, n_seg=24, cap_start=True, cap_end=True, superellipse_p=3.2)

    # Anillo ocular biselado envolvente alrededor de Screen024 (radio mayor 1.52 > 1.26 de Screen024)
    add_torus_ring_y(bm_scope, ox, -3.92, oz, major_r=1.52, minor_r_x=0.16, minor_r_y=0.24, n_major=32, n_minor=14)

    # 2 Góndolas Laterales de Telémetro Láser Orbital (X = ox ± 2.05)
    for sx in (-1.0, 1.0):
        add_lofted_tube(
            bm_scope,
            [
                (ox + sx * 1.95, -1.40, oz, 0.56, 0.68),
                (ox + sx * 2.08,  3.40, oz, 0.62, 0.75),
                (ox + sx * 1.95,  4.85, oz, 0.48, 0.58),
            ],
            n_seg=16,
            superellipse_p=3.0,
        )

    # Pedestal pesado de anclaje al puente dorsal (Z = -0.15 .. +1.35)
    add_lofted_tube(
        bm_scope,
        [(ox, -2.65, 0.55, 1.45, 0.75), (ox, 3.15, 0.55, 1.45, 0.75)],
        n_seg=18,
        superellipse_p=3.5,
    )
    obj_scope = finalize_bmesh_object(bm_scope, "CosmosPAScopeBody:0", mats["armor"], root_node)

    # 5B. Abrazaderas Hexagonales, Visera Frontal y Torretas Balísticas en Oro 24k
    bm_gold = bmesh.new()
    for cy_clamp in (-1.65, 2.15):
        add_torus_ring_y(bm_gold, ox, cy_clamp, oz, major_r=1.50, minor_r_x=0.18, minor_r_y=0.38, n_major=24, n_minor=12)
    add_torus_ring_y(bm_gold, ox, -4.02, oz, major_r=1.54, minor_r_x=0.13, minor_r_y=0.18, n_major=32, n_minor=12)
    add_torus_ring_y(bm_gold, ox,  6.40, oz, major_r=2.14, minor_r_x=0.18, minor_r_y=0.28, n_major=32, n_minor=14)
    # Torreta balística superior de elevación orbital
    add_cylinder_z(bm_gold, ox, 0.35, oz + 1.35, oz + 2.15, rx=0.68, ry=0.68, n_seg=18, superellipse_p=2.2)
    finalize_bmesh_object(bm_gold, "CosmosPAScopeGold:0", mats["gold"], root_node)

    # 5C. Lente Objetivo Principal Zafiro-Iridio + Lente Ocular Trasera (sellada para hip-fire) + 2 Lentes de Telémetro
    bm_lens = bmesh.new()
    add_lofted_tube(
        bm_lens,
        [(ox, 6.32, oz, 1.92, 1.86), (ox, 6.48, oz, 1.78, 1.72)],
        n_seg=28,
        superellipse_p=3.0,
    )
    add_lofted_tube(
        bm_lens,
        [(ox, -3.80, oz, 1.40, 1.40), (ox, -3.74, oz, 1.44, 1.44)],
        n_seg=24,
        cap_start=True,
        cap_end=False,
        superellipse_p=3.0,
    )
    for sx in (-1.0, 1.0):
        add_lofted_tube(
            bm_lens,
            [(ox + sx * 1.95, 4.82, oz, 0.38, 0.46), (ox + sx * 1.95, 4.96, oz, 0.34, 0.42)],
            n_seg=16,
        )
    finalize_bmesh_object(bm_lens, "CosmosPAScopeLens:0", mats["lens"], root_node)

    # 5D. Emisores Recon Solares en el Lomo de los Telémetros
    bm_solar = bmesh.new()
    for sx in (-1.0, 1.0):
        add_lofted_tube(
            bm_solar,
            [(ox + sx * 2.08, -0.50, oz + 0.72, 0.24, 0.20), (ox + sx * 2.08, 2.80, oz + 0.72, 0.24, 0.20)],
            n_seg=12,
        )
    finalize_bmesh_object(bm_solar, "CosmosPAScopeBeacon:0", mats["solar"], root_node)

    export_current_nif("CosmosPAOrbitalScope.nif", obj_scope)


# ------------------------------------------------------------------------------
# PIEZA 6: ACELERADOR CUADRUPOLAR DE SINGULARIDAD SOLAR (CosmosPASolarMuzzle.nif)
#          Anclado en P-Muzzle = (0.000, 53.742, 6.982); P-ProjectileNode = (0.0, 19.178, 0.0)
# ------------------------------------------------------------------------------
def build_cosmos_pa_solar_muzzle():
    import_scaffold_and_prune("GaussRifleSuppressorShort.nif")
    mats = create_pa_cannon_materials()
    root_node = get_root_or_node("GaussRifleSuppressorShort")

    # 6A. Collar Hexagonal de Acople + 4 Rieles Magnéticos en Voladizo a 45°/135°/225°/315°
    #     dejando el ánima central (0, Y, 0) 100% despejada hasta P-ProjectileNode (Y=19.178)
    #     y Z_world_max = 6.982 + 3.45 = 10.43 (muy por debajo de la línea óptica 13.54!).
    bm_muz = bmesh.new()
    add_lofted_tube(
        bm_muz,
        [
            (0.0, -2.40, 0.0, 3.35, 3.35),
            (0.0,  2.20, 0.0, 3.65, 3.65),
            (0.0,  3.60, 0.0, 2.45, 2.45),
        ],
        n_seg=24,
        superellipse_p=3.4,
    )

    bm_gold = bmesh.new()
    bm_solar = bmesh.new()

    for deg in (45.0, 135.0, 225.0, 315.0):
        rad_a = math.radians(deg)
        ca, sa = math.cos(rad_a), math.sin(rad_a)
        # Brazo blindado exterior de cada riel cuadrupolar (Y = +1.8 .. +18.8)
        rail_outer = []
        rail_gold = []
        for py, r_dist, rx_r in [
            ( 1.80, 3.15, 0.78),
            ( 6.50, 3.05, 0.72),
            (13.50, 2.75, 0.62),
            (18.85, 2.35, 0.45),
        ]:
            rail_outer.append((r_dist * ca, py, r_dist * sa, rx_r, rx_r))
            rail_gold.append(((r_dist - 0.62) * ca, py, (r_dist - 0.62) * sa, rx_r * 0.55, rx_r * 0.55))
        add_lofted_tube(bm_muz, rail_outer, n_seg=14, superellipse_p=3.2)
        add_lofted_tube(bm_gold, rail_gold, n_seg=12, superellipse_p=3.0)

    # 2 Anillos de Contención en Oro 24k + 2 Halos Internos de Plasma Solar
    for cy_h, mr_g, mr_s in [(6.80, 2.95, 2.15), (13.60, 2.68, 1.92)]:
        add_torus_ring_y(bm_gold, 0.0, cy_h, 0.0, major_r=mr_g, minor_r_x=0.24, minor_r_y=0.38, n_major=32, n_minor=14)
        add_torus_ring_y(bm_solar, 0.0, cy_h, 0.0, major_r=mr_s, minor_r_x=0.18, minor_r_y=0.26, n_major=32, n_minor=12)

    obj_muz = finalize_bmesh_object(bm_muz, "CosmosPAMuzzleRails:0", mats["armor"], root_node)
    finalize_bmesh_object(bm_gold, "CosmosPAMuzzleGold:0", mats["gold"], root_node)
    finalize_bmesh_object(bm_solar, "CosmosPAMuzzleSolar:0", mats["solar"], root_node)

    export_current_nif("CosmosPASolarMuzzle.nif", obj_muz)


# ------------------------------------------------------------------------------
# RENDER DE CONTROL DE CALIDAD (QA SHEET 4 VISTAS ENSAMBLADAS POR CONNECTPOINTS)
# ------------------------------------------------------------------------------
def render_assembled_pa_cannon_4views(out_png: str):
    if not out_png:
        return
    clear_scene()
    assets_root = os.path.abspath(os.path.join(OUT_DIR, "..", "..", "..", ".."))
    png_map = {
        "cosmospaweaparmor_d.dds": os.path.join(assets_root, "preview_pa_armor_d.png"),
        "cosmospaweaptitanium_d.dds": os.path.join(assets_root, "preview_pa_titanium_d.png"),
        "cosmospaweapgold_d.dds": os.path.join(assets_root, "preview_pa_gold_d.png"),
        "cosmospaweapsolarglow_d.dds": os.path.join(assets_root, "preview_pa_solar_d.png"),
        "cosmospaweaplens_d.dds": os.path.join(assets_root, "preview_pa_lens_d.png"),
    }

    # Coordenadas exactas BSConnectPoint en espacio WEAPON de gaussrifle.nif:
    # Base Receiver = (0, 0, 0)
    # Barrel Shroud (P-Barrel on WeaponBolt) = (-0.002, 43.908, 10.015)
    # Capacitor Mag (P-Mag on GaussRifleReceiver) = (-0.009, 26.702, 6.756)
    # Gauntlet Stock (P-Grip on GaussRifleReceiver) = (0.000, -4.922, 3.826)
    # Orbital Scope (P-Scope on WeaponOptics1) = (0.000, -0.161, 10.721)
    # Solar Muzzle (P-Muzzle on GaussRifleReceiver) = (0.000, 53.742, 6.982)
    part_transforms = [
        ("CosmosPACannonBase.nif", Vector((0.0, 0.0, 0.0))),
        ("CosmosPABarrelShroud.nif", Vector((-0.002, 43.908, 10.015))),
        ("CosmosPACapacitorMag.nif", Vector((-0.009, 26.702, 6.756))),
        ("CosmosPAGauntletStock.nif", Vector((0.000, -4.922, 3.826))),
        ("CosmosPAOrbitalScope.nif", Vector((0.000, -0.161, 10.721))),
        ("CosmosPASolarMuzzle.nif", Vector((0.000, 53.742, 6.982))),
    ]

    assembled_baked = []
    img_cache = {}

    for nif_fn, cp_offset in part_transforms:
        before = set(bpy.data.objects)
        bpy.ops.import_scene.pynifly(
            filepath=os.path.join(OUT_DIR, nif_fn),
            import_animations=False,
            import_cutpoints=False,
            import_tris=False,
            import_collisions=False,
        )
        new_objs = [o for o in bpy.data.objects if o not in before]
        bpy.context.view_layer.update()
        for o in new_objs:
            if o.type == "MESH" and not o.name.startswith("Screen024"):
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
                        bsdf.inputs["Roughness"].default_value = 0.20
                    elif "armor" in bname:
                        bsdf.inputs["Metallic"].default_value = 0.62
                        bsdf.inputs["Roughness"].default_value = 0.30
                    elif "solar" in bname:
                        bsdf.inputs["Roughness"].default_value = 0.10
                        if "Emission Color" in bsdf.inputs:
                            bsdf.inputs["Emission Color"].default_value = (1.0, 0.76, 0.18, 1.0)
                            bsdf.inputs["Emission Strength"].default_value = 2.8
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

    # Longitud total ensamblada: Y = -25.2 (cantonera) .. +72.6 (boca cuadrupolar) -> centro Y ≈ +23.7, Z ≈ +4.5
    poses = [
        (-54.0,  26.0, (0.0, 0.0, math.radians(-90.0)), 1.00),
        ( 54.0,  26.0, (math.radians(20.0), math.radians(-14.0), math.radians(-50.0)), 1.05),
        (-54.0, -26.0, (math.radians(22.0), math.radians(14.0), math.radians(-132.0)), 1.05),
        ( 54.0, -26.0, (math.radians(80.0), 0.0, math.radians(-90.0)), 1.00),
    ]

    scene = bpy.context.scene
    for idx_p, (gx, gz, rot_e, sc) in enumerate(poses):
        piv = bpy.data.objects.new(f"PosePivot_{idx_p}", None)
        scene.collection.objects.link(piv)
        piv.location = Vector((gx, 0.0, gz))
        piv.rotation_euler = rot_e
        piv.scale = Vector((sc, sc, sc))
        for m_idx, me_src in enumerate(assembled_baked):
            inst = bpy.data.objects.new(f"QAPACannon_{idx_p}_{m_idx}", me_src)
            inst.location = Vector((0.0, -23.7, -4.5))
            inst.parent = piv
            scene.collection.objects.link(inst)

    world = bpy.data.worlds.new("QAWorldPA")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.035, 0.045, 0.075, 1.0)
        bg.inputs[1].default_value = 1.15

    for lname, lpos, lrot, energy, col in [
        ("KeyLight", (-45.0, -135.0, 75.0), (math.radians(58.0), 0.0, math.radians(-18.0)), 4.0, (1.0, 0.97, 0.92)),
        ("FillLight", (75.0, -120.0, 20.0), (math.radians(78.0), 0.0, math.radians(28.0)), 2.2, (0.78, 0.88, 1.0)),
        ("RimLight", (0.0, 95.0, 65.0), (math.radians(-52.0), 0.0, math.radians(180.0)), 2.8, (1.0, 0.86, 0.60)),
    ]:
        ldata = bpy.data.lights.new(lname, type="SUN")
        ldata.energy = energy
        ldata.color = col
        lobj = bpy.data.objects.new(lname, ldata)
        lobj.location = Vector(lpos)
        lobj.rotation_euler = lrot
        scene.collection.objects.link(lobj)

    cam_data = bpy.data.cameras.new("QACamPA")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 222.0
    cam_obj = bpy.data.objects.new("QACamPA", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = Vector((0.0, -180.0, 0.0))
    cam_obj.rotation_euler = (math.radians(90.0), 0.0, 0.0)

    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.filepath = out_png
    bpy.ops.render.render(write_still=True)
    print(f"[QA Render PA Saved] {out_png}")


build_cosmos_pa_cannon_base()
build_cosmos_pa_barrel_shroud()
build_cosmos_pa_capacitor_mag()
build_cosmos_pa_gauntlet_stock()
build_cosmos_pa_orbital_scope()
build_cosmos_pa_solar_muzzle()
render_assembled_pa_cannon_4views(RENDER_PREVIEW_PATH)
'''


def run_blender_and_inject_connect_points() -> str:
    os.makedirs(MESH_OUT_DIR, exist_ok=True)
    qa_png = os.path.join(WEAP_ASSETS_DIR, "qa_render_cosmos_pa_cannon_4views.png")
    bscript_path = os.path.join(WEAP_ASSETS_DIR, "_blender_build_cosmos_pa_cannon.py")

    code = (
        BLENDER_PA_CANNON_SCRIPT.replace("__REF_DIR__", REF_SCAFFOLDS_DIR)
        .replace("__OUT_DIR__", MESH_OUT_DIR)
        .replace("__RENDER_PREVIEW__", qa_png)
        .replace("__PYNIFLY_DIR__", PYNIFLY_DIR)
    )
    with open(bscript_path, "w", encoding="utf-8") as wf:
        wf.write(code)

    cmd = [BLENDER_EXE, "--background", "--python-exit-code", "1", "--python", bscript_path]
    print("Ejecutando Blender 5.2 LTS + PyNifly para esculpir las 6 piezas .NIF del Cañón Orbital Astro-Cosmos...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print(res.stderr, file=sys.stderr)
        raise RuntimeError(f"Blender devolvió código {res.returncode}")

    cp_pairs = [
        ("CosmosPACannonBase.nif", "gaussrifle.nif"),
        ("CosmosPABarrelShroud.nif", "GaussRifleBarrelShroud.nif"),
        ("CosmosPACapacitorMag.nif", "gaussriflemagsmall.nif"),
        ("CosmosPAGauntletStock.nif", "GaussRifleRecoilGrip.nif"),
        ("CosmosPAOrbitalScope.nif", "pistol_scope_gauss.nif"),
        ("CosmosPASolarMuzzle.nif", "GaussRifleSuppressorShort.nif"),
    ]
    for dst_fn, tpl_fn in cp_pairs:
        ensure_connect_points_from_scaffold(
            os.path.join(MESH_OUT_DIR, dst_fn),
            os.path.join(REF_SCAFFOLDS_DIR, tpl_fn),
        )
    return qa_png


def deploy_cosmos_pa_weapon_assets() -> None:
    targets = [
        (TEX_OUT_DIR, os.path.join(FO4_DATA_DIR, "Textures", "AeroArmor", "PAWeapon")),
        (MAT_OUT_DIR, os.path.join(FO4_DATA_DIR, "Materials", "AeroArmor", "PAWeapon")),
        (MESH_OUT_DIR, os.path.join(FO4_DATA_DIR, "Meshes", "Weapons", "AeroArmor", "PACannon")),
        (MESH_OUT_DIR, os.path.join(THIS_DIR, "meshes", "Weapons", "AeroArmor", "PACannon")),
    ]
    for src_d, dst_d in targets:
        os.makedirs(dst_d, exist_ok=True)
        for fn in os.listdir(src_d):
            sp = os.path.join(src_d, fn)
            if os.path.isfile(sp):
                shutil.copy2(sp, os.path.join(dst_d, fn))
        print(f"[PA Deployed] {dst_d} ({len(os.listdir(src_d))} archivos)")


def main() -> None:
    print("=== 0. Extrayendo plantillas de nodos de GaussRifle desde Fallout4 - Meshes.ba2 ===")
    extract_vanilla_scaffolds()
    print("\n=== 1. Generando texturas PBR 2K (BC1/BC5) y materiales BGSM v2 para Servoarmadura ===")
    generate_pa_weapon_textures_and_materials()
    print("\n=== 2. Esculpiendo las 6 piezas 3D en Blender 5.2 LTS + inyectando BSConnectPoints ===")
    qa_png = run_blender_and_inject_connect_points()
    print("\n=== 3. Desplegando activos en Fallout 4\\Data ===")
    deploy_cosmos_pa_weapon_assets()
    print(f"\n[COMPLETADO] Hoja QA 4 vistas del Cañón Orbital lista en: {qa_png}")


if __name__ == "__main__":
    main()
