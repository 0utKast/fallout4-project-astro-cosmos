#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
generate_orbita7_studio_assets.py
=================================
Genera de forma 100 % autónoma (cero dependencias externas ni de Creation Club,
usando únicamente MetalTable01.nif de Fallout4 - Meshes.ba2 como andamiaje de
colisión estática Havok) los 8 materiales PBR 2K (2048x2048 BC1/BC5 + BGSM v2)
y las 12 piezas 3D originales Art-Deco de Hubris Comics para el escenario
subterráneo «Estudio Órbita-7» (El Legado de Hubris — Proyecto Astro-Cosmos):

  1. Orbita7_SaturnPlanetarium.nif       — Planetario colgante monumental de Saturno + luna Tycho + alas estelares
  2. Orbita7_LoreVitrine_Cosmos.nif      — Vitrina retroiluminada #1 (Capitán Cosmos, Jangles y Cráter Tycho + cohete 3D)
  3. Orbita7_LoreVitrine_Unstoppables.nif— Vitrina retroiluminada #2 (Galería Los Imparables + 5 pedestales de emblemas)
  4. Orbita7_ComicDraftingDesk.nif       — Mesa inclinada retroiluminada de historietista + regla T + flexo + tintas
  5. Orbita7_TrueBelieverConsole.nif     — Consola semicircular de exámenes «Protocolo del Verdadero Creyente»
  6. Orbita7_HeroSuitPod.nif             — Cápsula cilíndrica iluminada del Traje de Vuelo Astro-Cosmos (Misión 1)
  7. Orbita7_WeaponPedestal.nif          — Pedestal fotónico acorazado de la Carabina de Rayos Astro-Cosmos (Misión 2)
  8. Orbita7_PAGantryPlatform.nif        — Pórtico orbital transitable para la Servoarmadura Astro-Cosmos (Misión 3)
  9. Orbita7_SolarReliquary.nif          — Relicario solar de triple halo para el Cañón Orbital Gauss (Misión 4)
 10. Orbita7_CosmosBed.nif               — Cama espacial del Capitán Cosmos (geometría exacta PlayerHouseBed01 Z=42)
 11. Orbita7_StarChest.nif               — Baúl acorazado estelar con cierre alado (contenedor seguro sin reseteo)
 12. Orbita7_DirectorMuralFrame.nif      — Gran mural dorado enmarcado con el lema juramentado del Capitán Cosmos
"""

from __future__ import annotations

import math
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from fallout_pbr_weathering import (
    tileable_fbm,
    cellular_chip_mask,
    directional_scratches_and_drips,
    height_to_bc5_normal,
    weather_painted_metal,
    weather_antique_brass,
)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
CRONICAS_DIR = os.path.join(THIS_DIR, "cronicas_refugio_13")
for _p in (THIS_DIR, CRONICAS_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

FO4_DATA_DIR = r"C:\Program Files (x86)\Steam\steamapps\common\Fallout 4\Data"
FO4_MESHES_BA2 = os.path.join(FO4_DATA_DIR, "Fallout4 - Meshes.ba2")

STUDIO_ASSETS_DIR = os.path.join(THIS_DIR, "orbita7_studio_assets")
STUDIO_ASSETS_EN_DIR = os.path.join(THIS_DIR, "orbita7_studio_assets_en")
REF_SCAFFOLDS_DIR = os.path.join(STUDIO_ASSETS_DIR, "ref_scaffolds")
TEX_OUT_DIR = os.path.join(STUDIO_ASSETS_DIR, "Textures", "AeroArmor", "Orbita7")
TEX_OUT_EN_DIR = os.path.join(STUDIO_ASSETS_EN_DIR, "Textures", "AeroArmor", "Orbita7")
MAT_OUT_DIR = os.path.join(STUDIO_ASSETS_DIR, "Materials", "AeroArmor", "Orbita7")
MESH_OUT_DIR = os.path.join(STUDIO_ASSETS_DIR, "Meshes", "AeroArmor", "Orbita7")
QA_PREVIEW_PNG = os.path.join(STUDIO_ASSETS_DIR, "qa_render_orbita7_furniture.png")

BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
PYNIFLY_DIR = r"C:\Users\educa\AppData\Roaming\Blender Foundation\Blender\5.2\scripts\addons\io_scene_nifly"

from generate_cosmos_hero_weapon import (
    write_bc1_dds_from_image,
    write_bc5_dds_from_rg_arrays,
    build_bgsm_v2_bytes,
    _height_to_normal_rg,
)
from generate_v13_junktown_3d_assets import (
    _build_texset_bytes,
    _intern_nif_string,
    _parse_fo4_nif,
    _serialize_fo4_nif,
)

ORBITA7_MODEL_NAMES = [
    "Orbita7_SaturnPlanetarium.nif",
    "Orbita7_LoreVitrine_Cosmos.nif",
    "Orbita7_LoreVitrine_Unstoppables.nif",
    "Orbita7_ComicDraftingDesk.nif",
    "Orbita7_TrueBelieverConsole.nif",
    "Orbita7_HeroSuitPod.nif",
    "Orbita7_WeaponPedestal.nif",
    "Orbita7_PAGantryPlatform.nif",
    "Orbita7_SolarReliquary.nif",
    "Orbita7_CosmosBed.nif",
    "Orbita7_StarChest.nif",
    "Orbita7_DirectorMuralFrame.nif",
    "Orbita7_SecurityBarrier.nif",
    "Orbita7_StudioHallComplex.nif",
    "Orbita7_ExteriorBunkerPlinth.nif",
]


def extract_static_scaffold() -> str:
    """Extrae MetalTable01.nif de Fallout4 - Meshes.ba2 como donante limpio de colisión estática Havok."""
    os.makedirs(REF_SCAFFOLDS_DIR, exist_ok=True)
    out_nif = os.path.join(REF_SCAFFOLDS_DIR, "MetalTable01.nif")
    if os.path.isfile(out_nif):
        return out_nif

    with open(FO4_MESHES_BA2, "rb") as bf:
        magic, _ver, _btype, num_files, name_off = struct.unpack("<4sI4sIQ", bf.read(24))
        assert magic == b"BTDX", f"BA2 inválido: {magic}"
        entries = [struct.unpack("<4IQ3I", bf.read(36)) for _ in range(num_files)]
        bf.seek(name_off)
        names = [bf.read(struct.unpack("<H", bf.read(2))[0]).decode("latin1") for _ in range(num_files)]
        nmap = {n.lower().replace("/", "\\"): i for i, n in enumerate(names)}
        idx = nmap[r"meshes\setdressing\metalfurniture\metaltable01.nif"]
        _, _, _, _, off, psz, usz, _ = entries[idx]
        bf.seek(off)
        raw = zlib.decompress(bf.read(psz)) if psz > 0 else bf.read(usz)
        with open(out_nif, "wb") as wf:
            wf.write(raw)
    print(f"[Scaffold Extracted] MetalTable01.nif ({len(raw):,} B)")
    return out_nif


def _load_font(size: int, bold: bool = True, mono: bool = False) -> ImageFont.FreeTypeFont:
    if mono:
        cands = [r"C:\Windows\Fonts\consolab.ttf", r"C:\Windows\Fonts\courbd.ttf", r"C:\Windows\Fonts\arialbd.ttf"]
    elif bold:
        cands = [r"C:\Windows\Fonts\impact.ttf", r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\calibrib.ttf"]
    else:
        cands = [r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"]
    for p in cands:
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _draw_star_poly(dr: ImageDraw.ImageDraw, cx: float, cy: float, r_out: float, r_in: float, fill, outline=None, width: int = 2):
    pts = []
    for k in range(10):
        ang = -math.pi / 2.0 + k * (math.pi / 5.0)
        rr = r_out if (k % 2 == 0) else r_in
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    dr.polygon(pts, fill=fill, outline=outline)
    if outline and width > 1:
        dr.line(pts + [pts[0]], fill=outline, width=width)


def _build_comics_atlas_image(lang: str = "es") -> Image.Image:
    """
    Construye el atlas gráfico retroiluminado 2048x2048 de Hubris Comics (Orbita7ComicsAtlas_d.dds):
      - Q0 (0..1024, 0..1024): Portada/Panel Vitrina #1 — CAPITÁN COSMOS #1 / JANGLES / CRÁTER TYCHO
      - Q1 (1024..2048, 0..1024): Panel Vitrina #2 — LOS IMPARABLES (5 héroes y armas/alias clave)
      - Q2 (0..1024, 1024..2048): Lámina de Entintado de Clara Sterling (Azul Cobalto, Rojo Carmesí, Oro Solar)
      - Q3 (1024..2048, 1024..2048): Pantalla CRT Consola de Exámenes «VERDADERO CREYENTE» (Coronel Agallas)
    """
    is_en = lang == "en"
    im = Image.new("RGB", (2048, 2048), (18, 26, 48))
    dr = ImageDraw.Draw(im)

    f_hero = _load_font(68, bold=True)
    f_sub = _load_font(42, bold=False)
    f_body = _load_font(30, bold=False)
    f_sm = _load_font(25, bold=False)
    f_crt_lg = _load_font(46, mono=True)
    f_crt = _load_font(30, mono=True)

    # --------------------------------------------------------------------------
    # Q0 (0..1024, 0..1024): CAPITÁN COSMOS #1 — RESCATE EN EL CRÁTER TYCHO
    # --------------------------------------------------------------------------
    dr.rectangle([0, 0, 1023, 1023], fill=(14, 30, 68))
    # Rayos solares Art-Deco desde el centro
    cx0, cy0 = 512, 470
    for k in range(18):
        a0 = k * (2.0 * math.pi / 18.0)
        a1 = a0 + (math.pi / 18.0)
        if k % 2 == 0:
            pts = [
                (cx0, cy0),
                (cx0 + 680 * math.cos(a0), cy0 + 680 * math.sin(a0)),
                (cx0 + 680 * math.cos(a1), cy0 + 680 * math.sin(a1)),
            ]
            dr.polygon(pts, fill=(22, 46, 98))
    dr.rectangle([18, 18, 1005, 1005], outline=(232, 186, 62), width=12)
    dr.rectangle([34, 34, 989, 989], outline=(196, 38, 44), width=5)

    # Cabecera editorial Hubris
    dr.rectangle([42, 42, 981, 186], fill=(178, 30, 36), outline=(238, 194, 72), width=5)
    dr.text((76, 54), "HUBRIS COMICS PRESENTS • ISSUE #1" if is_en else "HUBRIS COMICS PRESENTA • N.º 1", fill=(255, 232, 148), font=f_body)
    dr.text((74, 96), "CAPTAIN COSMOS" if is_en else "EL CAPITÁN COSMOS", fill=(255, 250, 235), font=f_hero)

    # Ilustración espacial central: Saturno + Superficie Lunar Cráter Tycho + Cohete
    dr.ellipse([580, 220, 860, 500], fill=(226, 174, 56), outline=(255, 232, 148), width=5)
    dr.arc([500, 315, 940, 415], start=0, end=360, fill=(255, 236, 168), width=10)
    # Superficie lunar gris-azulada con el Cráter Tycho destacado
    dr.chord([60, 540, 964, 1120], start=180, end=360, fill=(142, 152, 172), outline=(225, 232, 245), width=5)
    dr.ellipse([290, 600, 730, 725], fill=(92, 102, 122), outline=(238, 194, 72), width=6)
    dr.text((372, 642), "TYCHO CRATER" if is_en else "CRÁTER TYCHO", fill=(255, 236, 142), font=f_sub)
    # Cohete retrofuturista rojo y dorado
    dr.polygon([(210, 250), (260, 370), (250, 565), (170, 565), (160, 370)], fill=(214, 44, 48), outline=(250, 212, 92), width=4)
    dr.ellipse([188, 345, 232, 389], fill=(98, 228, 255), outline=(250, 212, 92), width=4)
    _draw_star_poly(dr, 210, 455, 28, 12, fill=(250, 212, 92), outline=(24, 42, 88), width=2)

    # Cartela inferior de archivo (pista nítida Misión 1)
    dr.rectangle([56, 760, 968, 968], fill=(12, 24, 54), outline=(238, 194, 72), width=5)
    dr.text((84, 778), "OFFICIAL EDITORIAL CANON ARCHIVE:" if is_en else "ARCHIVO OFICIAL DE CANON EDITORIAL:", fill=(255, 214, 88), font=f_body)
    dr.text((84, 822), "• LOYAL CO-PILOT: JANGLES THE MOON MONKEY" if is_en else "• COPILOTO FIEL: JANGLES EL MONO LUNAR", fill=(238, 246, 255), font=f_body)
    dr.text((84, 864), "• RESCUE SITE: TYCHO CRATER (THE MOON)" if is_en else "• LUGAR DEL RESCATE: CRÁTER TYCHO (LUNA)", fill=(124, 234, 255), font=f_body)
    dr.text((84, 906), "• FLAGSHIP: STAR CRUISER PEGASUS" if is_en else "• NAVE INSIGNIA: CRUCERO ESTELAR PEGASUS", fill=(238, 246, 255), font=f_body)

    # --------------------------------------------------------------------------
    # Q1 (1024..2048, 0..1024): GALERÍA OFICIAL DE LOS IMPARABLES
    # --------------------------------------------------------------------------
    ox = 1024
    dr.rectangle([ox, 0, ox + 1023, 1023], fill=(24, 18, 46))
    dr.rectangle([ox + 18, 18, ox + 1005, 1005], outline=(232, 186, 62), width=12)
    dr.rectangle([ox + 42, 42, ox + 981, 182], fill=(22, 62, 124), outline=(238, 194, 72), width=5)
    dr.text((ox + 78, 52), "HUBRIS SUPERHERO DIVISION" if is_en else "DIVISIÓN DE SUPERHÉROES HUBRIS", fill=(132, 232, 255), font=f_body)
    dr.text((ox + 76, 94), "THE UNSTOPPABLES" if is_en else "LOS IMPARABLES", fill=(255, 224, 98), font=f_hero)

    if is_en:
        heroes = [
            ("1. THE SILVER SHROUD", "Signature arm: Silver Submachine Gun • Night justice", (188, 198, 214)),
            ("2. MISTRESS OF MYSTERY", "Original radio voice: Actress Shannon Rivers", (186, 118, 238)),
            ("3. GROGNAK THE BARBARIAN", "Double-headed axe • Arch-nemesis: The Kurse-Maker", (228, 126, 64)),
            ("4. MANTA MAN", "Lord of the oceans and Defender of Atlantis", (72, 212, 186)),
            ("5. THE INSPECTOR", "Master illusionist • Top Hat & Enchanted Wand", (246, 204, 84)),
        ]
    else:
        heroes = [
            ("1. LA MORTAJA PLATEADA", "Arma icónica: Subfusil Plateado • Justicia nocturna", (188, 198, 214)),
            ("2. LA DAMA DEL MISTERIO", "Voz radiofónica real: Actriz Shannon Rivers", (186, 118, 238)),
            ("3. GROGNAK EL BÁRBARO", "Hacha de doble filo • Archienemigo: Hechicero Grelok", (228, 126, 64)),
            ("4. EL HOMBRE MANTA", "Señor de los océanos y defensor de la Atlántida", (72, 212, 186)),
            ("5. LA INSPECTORA", "Maestra ilusionista • Chistera y Lupa Mágica", (246, 204, 84)),
        ]
    for idx, (h_title, h_desc, h_col) in enumerate(heroes):
        y0 = 212 + idx * 150
        dr.rectangle([ox + 56, y0, ox + 968, y0 + 132], fill=(34, 28, 66), outline=h_col, width=4)
        _draw_star_poly(dr, ox + 114, y0 + 66, 36, 15, fill=h_col, outline=(255, 255, 255), width=2)
        dr.text((ox + 172, y0 + 22), h_title, fill=h_col, font=f_sub)
        dr.text((ox + 172, y0 + 78), h_desc, fill=(238, 242, 250), font=f_sm)

    # --------------------------------------------------------------------------
    # Q2 (0..1024, 1024..2048): MESA DE LUZ DE CLARA STERLING — CARTA DE COLORES
    # --------------------------------------------------------------------------
    oy = 1024
    # Papel opalino cálido retroiluminado de mesa de dibujo
    dr.rectangle([0, oy, 1023, oy + 1023], fill=(246, 238, 216))
    for gx in range(32, 1000, 48):
        dr.line([(gx, oy + 20), (gx, oy + 1000)], fill=(218, 224, 232), width=1)
    for gy in range(oy + 32, oy + 1000, 48):
        dr.line([(20, gy), (1000, gy)], fill=(218, 224, 232), width=1)
    dr.rectangle([24, oy + 24, 999, oy + 999], outline=(38, 48, 72), width=6)

    dr.text((58, oy + 48), "HUBRIS STUDIO • INKING GUIDE #01" if is_en else "ESTUDIO HUBRIS • GUÍA DE ENTINTADO #01", fill=(24, 38, 76), font=f_sub)
    dr.text((58, oy + 102), "Approved by: Clara Sterling (Head Writer)" if is_en else "Aprobado por: Clara Sterling (Guionista Jefe)", fill=(142, 34, 38), font=f_body)

    # Boceto entintado del traje del Capitán Cosmos a la izquierda
    dr.rectangle([60, oy + 162, 510, oy + 780], outline=(28, 36, 58), width=4)
    # Silueta heroica geométrica entintada
    dr.ellipse([240, oy + 195, 330, oy + 285], fill=(26, 62, 138), outline=(22, 26, 38), width=4)
    dr.polygon([(175, oy + 305), (395, oy + 305), (355, oy + 520), (215, oy + 520)], fill=(26, 62, 138), outline=(22, 26, 38), width=5)
    # Cinturón y botas carmesí + estrella oro solar
    dr.rectangle([212, oy + 485, 358, oy + 525], fill=(196, 34, 42), outline=(22, 26, 38), width=3)
    dr.rectangle([215, oy + 525, 272, oy + 735], fill=(26, 62, 138), outline=(22, 26, 38), width=4)
    dr.rectangle([298, oy + 525, 355, oy + 735], fill=(26, 62, 138), outline=(22, 26, 38), width=4)
    dr.rectangle([210, oy + 655, 276, oy + 745], fill=(196, 34, 42), outline=(22, 26, 38), width=4)
    dr.rectangle([294, oy + 655, 360, oy + 745], fill=(196, 34, 42), outline=(22, 26, 38), width=4)
    _draw_star_poly(dr, 285, oy + 388, 48, 20, fill=(238, 186, 44), outline=(22, 26, 38), width=3)

    # Muestras oficiales de los 3 colores reglamentarios a la derecha (Pista exacta Examen 1)
    f_sw = _load_font(22, bold=False)
    if is_en:
        swatches = [
            ("INK 1: COBALT BLUE", (24, 62, 142), "Pressurized star chassis"),
            ("INK 2: CRIMSON RED", (198, 32, 40), "Boots, cuffs & heroic cape"),
            ("INK 3: SOLAR GOLD", (238, 186, 42), "Winged star & gyro rings"),
        ]
    else:
        swatches = [
            ("TINTA 1: AZUL COBALTO", (24, 62, 142), "Cuerpo presurizado"),
            ("TINTA 2: ROJO CARMESÍ", (198, 32, 40), "Botas, guantes y cuello"),
            ("TINTA 3: ORO SOLAR", (238, 186, 42), "Emblema alado y anillos"),
        ]
    for si, (stitle, scol, sdesc) in enumerate(swatches):
        sy = oy + 175 + si * 195
        dr.rectangle([530, sy, 982, sy + 168], fill=(255, 252, 242), outline=(36, 44, 64), width=3)
        dr.rectangle([546, sy + 22, 654, sy + 146], fill=scol, outline=(24, 28, 36), width=3)
        dr.text((670, sy + 38), stitle, fill=(22, 32, 58), font=f_sw)
        dr.text((670, sy + 92), sdesc, fill=(84, 72, 62), font=f_sw)

    dr.rectangle([52, oy + 812, 982, oy + 965], fill=(236, 224, 192), outline=(142, 34, 38), width=4)
    dr.text((74, oy + 836), "PRINTER NOTE: No olive green or purple allowed." if is_en else "NOTA DE IMPRENTA: Prohibido usar verde o púrpura.", fill=(142, 34, 38), font=f_sm)
    dr.text((74, oy + 890), "OFFICIAL TRIAD: COBALT BLUE + CRIMSON RED + SOLAR GOLD" if is_en else "TRÍADA OFICIAL: AZUL COBALTO + ROJO CARMESÍ + ORO SOLAR", fill=(20, 36, 78), font=f_sm)

    # --------------------------------------------------------------------------
    # Q3 (1024..2048, 1024..2048): CONSOLA CRT «PROTOCOLO VERDADERO CREYENTE»
    # --------------------------------------------------------------------------
    dr.rectangle([ox, oy, ox + 1023, oy + 1023], fill=(8, 28, 24))
    # Líneas de escaneo CRT
    for sy in range(oy, oy + 1024, 8):
        dr.line([(ox, sy), (ox + 1023, sy)], fill=(12, 42, 36), width=2)
    dr.rectangle([ox + 26, oy + 26, ox + 997, oy + 997], outline=(68, 242, 198), width=8)
    dr.rectangle([ox + 48, oy + 48, ox + 975, oy + 190], fill=(14, 58, 52), outline=(68, 242, 198), width=4)
    dr.text((ox + 78, oy + 66), "HUBRIS-DOD SECURITY SYSTEM MK-VII" if is_en else "SISTEMA DE SEGURIDAD HUBRIS-DOD MK-VII", fill=(255, 212, 84), font=f_crt)
    dr.text((ox + 78, oy + 114), "PROTOCOL: TRUE BELIEVER" if is_en else "PROTOCOLO: VERDADERO CREYENTE", fill=(86, 255, 212), font=f_crt_lg)

    # Retícula circular de radar / Saturno en el CRT
    rcx, rcy = ox + 512, oy + 530
    for rr in (240, 175, 110, 48):
        dr.ellipse([rcx - rr, rcy - rr, rcx + rr, rcy + rr], outline=(46, 188, 152), width=3)
    dr.line([(rcx - 270, rcy), (rcx + 270, rcy)], fill=(46, 188, 152), width=2)
    dr.line([(rcx, rcy - 270), (rcx, rcy + 270)], fill=(46, 188, 152), width=2)
    _draw_star_poly(dr, rcx, rcy, 62, 24, fill=(255, 206, 72), outline=(86, 255, 212), width=3)

    dr.rectangle([ox + 58, oy + 812, ox + 965, oy + 960], fill=(16, 48, 42), outline=(255, 206, 72), width=4)
    dr.text((ox + 86, oy + 832), "EXAMINER ON DUTY: COLONEL GUTSY 'COSMOS'" if is_en else "EXAMINADOR ACTIVO: CORONEL AGALLAS «COSMOS»", fill=(255, 212, 84), font=f_crt)
    dr.text((ox + 86, oy + 884), "STATUS: VAULT SEALED — ANSWER INTERROGATION" if is_en else "ESTADO: CÁMARA SELLADA — RESPONDA INTERROGATORIO", fill=(86, 255, 212), font=f_crt)

    return im


def _build_director_mural_image(lang: str = "es") -> Image.Image:
    """
    Construye el atlas 2048x2048 del Gran Mural de la Sala del Director y Placas de Latón
    (Orbita7DirectorMural_d.dds):
      - Mitad superior (y: 0..1024): Gran Mural Art-Deco con el lema juramentado del Capitán Cosmos
        «¡POR LA VERDAD, LAS ESTRELLAS Y EL MAÑANA!» / "FOR TRUTH, THE STARS, AND TOMORROW!".
      - Mitad inferior (y: 1024..2048): Placas de latón grabado para vitrinas, cápsulas y pórticos.
    """
    is_en = lang == "en"
    im = Image.new("RGB", (2048, 2048), (16, 28, 58))
    dr = ImageDraw.Draw(im)

    f_mural_lg = _load_font(76, bold=True)
    f_mural_md = _load_font(46, bold=False)
    f_plaque_lg = _load_font(54, bold=True)
    f_plaque_sm = _load_font(34, bold=False)

    # Mitad superior (0..2048, 0..1024): Gran Mural del Juramento del Capitán Cosmos
    dr.rectangle([0, 0, 2047, 1023], fill=(14, 30, 68))
    for i in range(24):
        ang = -math.pi + i * (math.pi / 12.0)
        x_end = 1024 + 1400 * math.cos(ang)
        y_end = 512 + 900 * math.sin(ang)
        dr.line([(1024, 512), (x_end, y_end)], fill=(26, 54, 112), width=18)

    dr.rectangle([28, 28, 2019, 995], outline=(236, 188, 62), width=16)
    dr.rectangle([52, 52, 1995, 971], outline=(196, 36, 42), width=6)

    # Emblema alado dorado central en la parte superior del mural
    for sgn in (-1, 1):
        for wi in range(4):
            wy = 175 + wi * 34
            wlen = 460 - wi * 72
            dr.polygon(
                [
                    (1024 + sgn * 95, wy),
                    (1024 + sgn * (95 + wlen), wy - 18),
                    (1024 + sgn * (75 + wlen), wy + 20),
                    (1024 + sgn * 95, wy + 24),
                ],
                fill=(236, 188, 62),
                outline=(255, 232, 148),
            )
    dr.ellipse([914, 130, 1134, 350], fill=(188, 32, 38), outline=(245, 204, 82), width=8)
    _draw_star_poly(dr, 1024, 240, 88, 36, fill=(252, 214, 86), outline=(255, 248, 210), width=4)

    dr.text((1024, 420), "OFFICIAL OATH OF THE STAR GUARD" if is_en else "JURAMENTO OFICIAL DE LA GUARDIA ESTELAR", fill=(134, 232, 255), font=f_mural_md, anchor="mm")
    dr.rectangle([110, 475, 1938, 725], fill=(10, 22, 50), outline=(242, 196, 68), width=8)
    dr.text((1024, 552), "\"FOR TRUTH, THE STARS," if is_en else "«¡POR LA VERDAD, LAS ESTRELLAS", fill=(255, 222, 96), font=f_mural_lg, anchor="mm")
    dr.text((1024, 650), "AND TOMORROW!\"" if is_en else "Y EL MAÑANA!»", fill=(255, 222, 96), font=f_mural_lg, anchor="mm")
    dr.text((1024, 808), "HUBRIS COMICS STUDIOS • ORBIT-7 DIVISION • EST. 2065" if is_en else "HUBRIS COMICS STUDIOS • DIVISIÓN ÓRBITA-7 • FUNDADO EN 2065", fill=(235, 240, 250), font=f_mural_md, anchor="mm")

    # Mitad inferior (0..2048, 1024..2048): Placas de latón bruñido grabado (4 bandas horizontales)
    dr.rectangle([0, 1024, 2047, 2047], fill=(198, 152, 52))
    if is_en:
        plaques = [
            ("UNDERGROUND STUDIO ORBIT-7 • PROJECT ASTRO-COSMOS", "CLASSIFIED PROPERTY OF HUBRIS COMICS & D.O.D."),
            ("HISTORIC ARCHIVE #1: CAPTAIN COSMOS & JANGLES", "FIRST APPEARANCE: RESCUE AT TYCHO CRATER"),
            ("HALL OF HONOR: HUBRIS'S FIVE UNSTOPPABLES", "SHROUD • MYSTERY • GROGNAK • MANTA • INSPECTOR"),
            ("AEROSPACE PROTOTYPE STASIS VAULTS", "ACCESS SUBJECT TO THE TRUE BELIEVER PROTOCOL"),
        ]
    else:
        plaques = [
            ("ESTUDIO SUBTERRÁNEO ÓRBITA-7 • PROYECTO ASTRO-COSMOS", "PROPIEDAD CLASIFICADA DE HUBRIS COMICS & D.O.D."),
            ("ARCHIVO HISTÓRICO N.º 1: CAPITÁN COSMOS Y JANGLES", "PRIMERA APARICIÓN: RESCATE EN EL CRÁTER TYCHO"),
            ("GALERÍA DE HONOR: LOS CINCO IMPARABLES DE HUBRIS", "MORTAJA • MISTERIO • GROGNAK • MANTA • INSPECTORA"),
            ("CÁMARA ACORAZADA DE PROTOTIPOS AEROESPACIALES", "APERTURA SUJETA AL PROTOCOLO DEL VERDADERO CREYENTE"),
        ]
    for pi, (pt1, pt2) in enumerate(plaques):
        py0 = 1040 + pi * 248
        dr.rectangle([28, py0, 2019, py0 + 228], fill=(214, 168, 62), outline=(92, 66, 18), width=8)
        dr.rectangle([46, py0 + 18, 2001, py0 + 210], outline=(248, 218, 122), width=3)
        dr.text((96, py0 + 42), pt1, fill=(38, 26, 8), font=f_plaque_lg)
        dr.text((96, py0 + 128), pt2, fill=(68, 46, 14), font=f_plaque_sm)

    return im


def generate_orbita7_textures_and_materials(force: bool = False) -> None:
    """Genera los 8 sets PBR 2048x2048 (_d/_n/_s.dds) y sus 8 archivos .BGSM v2."""
    os.makedirs(TEX_OUT_DIR, exist_ok=True)
    os.makedirs(MAT_OUT_DIR, exist_ok=True)
    os.makedirs(STUDIO_ASSETS_DIR, exist_ok=True)

    expected_bgsm = [
        "Orbita7CobaltSteel.BGSM",
        "Orbita7BrassGold.BGSM",
        "Orbita7CrimsonTrim.BGSM",
        "Orbita7MahoganyWood.BGSM",
        "Orbita7CyanStasis.BGSM",
        "Orbita7SolarGlow.BGSM",
        "Orbita7ComicsAtlas.BGSM",
        "Orbita7DirectorMural.BGSM",
        "Orbita7TerrazzoFloor.BGSM",
    ]
    if not force and all(os.path.isfile(os.path.join(MAT_OUT_DIR, b)) for b in expected_bgsm):
        return

    N = 2048
    rng = np.random.default_rng(20770707)
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    u = xx / float(N)
    v = yy / float(N)
    fbm_macro = tileable_fbm(N, N, base_cells=8, octaves=4, persistence=0.54, seed=20770707)
    scratch, drip = directional_scratches_and_drips(N, N, seed=20770708)

    # 1. Orbita7CobaltSteel: Acero Art-Deco Azul Pizarra Subterráneo con 200 años de humedad, óxido y desconchados
    flute = np.sin(u * math.pi * 64.0)
    seams = ((np.abs(((u * 4.0) % 1.0) - 0.5) > 0.486) | (np.abs(((v * 4.0) % 1.0) - 0.5) > 0.486)).astype(np.float32)
    seam_rim = ((np.abs(((u * 4.0) % 1.0) - 0.5) > 0.464) | (np.abs(((v * 4.0) % 1.0) - 0.5) > 0.464)).astype(np.float32) * (1.0 - seams)
    cs_rgb, cs_dh, cs_spec_r, cs_gloss_g = weather_painted_metal(
        base_rgb=(28.0, 48.0, 80.0),
        edge_wear_mask=np.clip(seam_rim * 0.65, 0.0, 1.0),
        cavity_mask=np.clip(seams * 0.90 + drip * 0.55, 0.0, 1.0),
        h=N,
        w=N,
        seed=20770707,
        chip_amount=0.34,
        grime_amount=0.44,
        rust_amount=0.26,
    )
    cs_d = np.clip(cs_rgb, 6.0, 232.0).astype(np.uint8)
    cs_h = cs_dh + flute * 0.65 - seams * 2.6 + fbm_macro * 0.35
    cs_img = Image.fromarray(cs_d, mode="RGB")
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "Orbita7CobaltSteel_d.dds"), cs_img)
    cn_r, cn_g = height_to_bc5_normal(cs_h, strength=2.5)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "Orbita7CobaltSteel_n.dds"), cn_r, cn_g)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "Orbita7CobaltSteel_s.dds"), cs_spec_r, cs_gloss_g)

    # 2. Orbita7BrassGold: Bronce/Latón Art-Deco Antiguo con pátina subterránea
    brush = 0.45 * np.sin(xx * 0.55) + 0.25 * np.cos(yy * 0.30)
    bg_rgb, bg_dh, bg_spec_r, bg_gloss_g = weather_antique_brass(
        h=N,
        w=N,
        cavity_mask=np.clip(drip * 0.40, 0.0, 1.0),
        seed=20770708,
    )
    bg_d = np.clip(bg_rgb, 12.0, 212.0).astype(np.uint8)
    bg_h = bg_dh + brush * 0.22 + fbm_macro * 0.25
    bg_img = Image.fromarray(bg_d, mode="RGB")
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "Orbita7BrassGold_d.dds"), bg_img)
    bn_r, bn_g = height_to_bc5_normal(bg_h, strength=1.8)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "Orbita7BrassGold_n.dds"), bn_r, bn_g)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "Orbita7BrassGold_s.dds"), bg_spec_r, bg_gloss_g)

    # 3. Orbita7CrimsonTrim: Tapicería Acolchada / Cuero Burdeos Envejecido con polvo en costuras
    d1 = np.abs(((u * 12.0 + v * 12.0) % 1.0) - 0.5)
    d2 = np.abs(((u * 12.0 - v * 12.0) % 1.0) - 0.5)
    stitch = ((d1 < 0.03) | (d2 < 0.03)).astype(np.float32)
    pillow_puff = np.sin(u * math.pi * 12.0) ** 2 + np.sin(v * math.pi * 12.0) ** 2
    leather_wear = np.clip((fbm_macro - 0.38) * 1.25 + stitch * 0.45 + scratch * 0.40, 0.0, 1.0)
    cr_r = np.clip(108.0 + pillow_puff * 10.0 - stitch * 30.0 - leather_wear * 24.0 + scratch * 16.0, 38, 138)
    cr_g = np.clip(22.0 + pillow_puff * 3.0 - stitch * 6.0 + leather_wear * 6.0 + scratch * 10.0, 12, 54)
    cr_b = np.clip(26.0 + pillow_puff * 3.5 - stitch * 8.0 + leather_wear * 4.0 + scratch * 8.0, 14, 56)
    cr_img = Image.fromarray(np.stack([cr_r, cr_g, cr_b], axis=2).astype(np.uint8), mode="RGB")
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "Orbita7CrimsonTrim_d.dds"), cr_img)
    rn_r, rn_g = height_to_bc5_normal(pillow_puff * 0.85 - stitch * 1.8 + fbm_macro * 0.30, strength=2.2)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "Orbita7CrimsonTrim_n.dds"), rn_r, rn_g)
    write_bc5_dds_from_rg_arrays(
        os.path.join(TEX_OUT_DIR, "Orbita7CrimsonTrim_s.dds"),
        np.clip(64.0 - stitch * 26.0 - leather_wear * 18.0, 26, 76),
        np.clip(54.0 - stitch * 24.0 - leather_wear * 16.0, 22, 68),
    )

    # 4. Orbita7MahoganyWood: Madera Noble de Caoba Desgastada y Barniz Envejecido
    wgrain = np.sin(xx * 0.14 + np.sin(yy * 0.018) * 5.5) * 6.5 + np.cos(xx * 0.42) * 2.5 + (fbm_macro - 0.5) * 16.0
    wood_wear = np.clip(scratch * 0.65 + (fbm_macro - 0.52) * 0.90, 0.0, 1.0)
    mw_r = np.clip(78.0 + wgrain * 1.1 - wood_wear * 18.0 + scratch * 12.0, 34, 114)
    mw_g = np.clip(44.0 + wgrain * 0.65 - wood_wear * 10.0 + scratch * 8.0, 20, 68)
    mw_b = np.clip(28.0 + wgrain * 0.42 - wood_wear * 6.0 + scratch * 5.0, 14, 46)
    mw_img = Image.fromarray(np.stack([mw_r, mw_g, mw_b], axis=2).astype(np.uint8), mode="RGB")
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "Orbita7MahoganyWood_d.dds"), mw_img)
    wn_r, wn_g = height_to_bc5_normal(wgrain * 0.16 - scratch * 0.45, strength=1.8)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "Orbita7MahoganyWood_n.dds"), wn_r, wn_g)
    write_bc5_dds_from_rg_arrays(
        os.path.join(TEX_OUT_DIR, "Orbita7MahoganyWood_s.dds"),
        np.clip(98.0 - wood_wear * 38.0, 46, 114),
        np.clip(92.0 - wood_wear * 36.0, 42, 108),
    )

    # 5. Orbita7CyanStasis: Cristal de Estasis Cian con polvo acumulado de 200 años
    cpulse = 0.5 + 0.5 * np.cos(v * math.pi * 14.0)
    glass_dust = np.clip((fbm_macro - 0.44) * 1.15, 0.0, 0.65)
    cy_r = np.clip(48.0 + cpulse * 58.0 + glass_dust * 24.0, 28, 138)
    cy_g = np.clip(148.0 + cpulse * 42.0 - glass_dust * 22.0, 108, 198)
    cy_b = np.clip(182.0 + cpulse * 32.0 - glass_dust * 30.0, 132, 224)
    cy_img = Image.fromarray(np.stack([cy_r, cy_g, cy_b], axis=2).astype(np.uint8), mode="RGB")
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "Orbita7CyanStasis_d.dds"), cy_img)
    cy_n_r, cy_n_g = height_to_bc5_normal(glass_dust * 0.25 + scratch * 0.15, strength=1.1)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "Orbita7CyanStasis_n.dds"), cy_n_r, cy_n_g)
    write_bc5_dds_from_rg_arrays(
        os.path.join(TEX_OUT_DIR, "Orbita7CyanStasis_s.dds"),
        np.clip(164.0 - glass_dust * 65.0, 82, 178),
        np.clip(174.0 - glass_dust * 70.0, 88, 186),
    )

    # 6. Orbita7SolarGlow: Núcleo Solar Dorado con pátina térmica en bordes
    spulse = 0.5 + 0.5 * np.cos(v * math.pi * 12.0)
    soot = np.clip((fbm_macro - 0.48) * 1.15, 0.0, 0.55)
    so_r = np.clip((214.0 + spulse * 22.0) * (1.0 - 0.30 * soot), 130, 240)
    so_g = np.clip((144.0 + spulse * 44.0) * (1.0 - 0.36 * soot), 82, 198)
    so_b = np.clip((38.0 + spulse * 48.0) * (1.0 - 0.40 * soot), 20, 112)
    so_img = Image.fromarray(np.stack([so_r, so_g, so_b], axis=2).astype(np.uint8), mode="RGB")
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "Orbita7SolarGlow_d.dds"), so_img)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "Orbita7SolarGlow_n.dds"), cy_n_r, cy_n_g)
    write_bc5_dds_from_rg_arrays(
        os.path.join(TEX_OUT_DIR, "Orbita7SolarGlow_s.dds"),
        np.clip(148.0 - soot * 55.0, 74, 162),
        np.clip(158.0 - soot * 58.0, 80, 170),
    )

    # 7. Orbita7ComicsAtlas: Paneles ilustrados con pátina de papel/vidrio de 200 años (texto 100 % legible)
    atlas_raw = _build_comics_atlas_image()
    atlas_arr = np.asarray(atlas_raw, dtype=np.float32)
    paper_age = np.clip((fbm_macro - 0.40) * 0.42, 0.0, 0.28)[:, :, None]
    edge_vig = np.clip(np.maximum(np.abs(u - 0.5), np.abs(v - 0.5)) * 2.0 - 0.72, 0.0, 0.28) * 1.15
    age_mix = np.clip(paper_age + edge_vig[:, :, None] * 0.45, 0.0, 0.34)
    sepia_dust = np.array([118.0, 102.0, 76.0], dtype=np.float32).reshape(1, 1, 3)
    atlas_aged = np.clip(atlas_arr * (1.0 - age_mix) + sepia_dust * age_mix, 12, 238).astype(np.uint8)
    atlas_img = Image.fromarray(atlas_aged, mode="RGB")
    atlas_img.save(os.path.join(STUDIO_ASSETS_DIR, "preview_comics_atlas.png"))
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "Orbita7ComicsAtlas_d.dds"), atlas_img)
    an_r, an_g = height_to_bc5_normal(fbm_macro * 0.18 + scratch * 0.12, strength=1.0)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "Orbita7ComicsAtlas_n.dds"), an_r, an_g)
    write_bc5_dds_from_rg_arrays(
        os.path.join(TEX_OUT_DIR, "Orbita7ComicsAtlas_s.dds"),
        np.clip(104.0 - age_mix[:, :, 0] * 110.0, 44, 118),
        np.clip(112.0 - age_mix[:, :, 0] * 120.0, 48, 124),
    )

    # 8. Orbita7DirectorMural: Gran Mural envejecido del Capitán Cosmos (texto juramentado 100 % legible)
    mural_raw = _build_director_mural_image()
    mural_arr = np.asarray(mural_raw, dtype=np.float32)
    mural_aged = np.clip(mural_arr * (1.0 - age_mix) + sepia_dust * age_mix, 12, 236).astype(np.uint8)
    mural_img = Image.fromarray(mural_aged, mode="RGB")
    mural_img.save(os.path.join(STUDIO_ASSETS_DIR, "preview_director_mural.png"))
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "Orbita7DirectorMural_d.dds"), mural_img)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "Orbita7DirectorMural_n.dds"), an_r, an_g)
    write_bc5_dds_from_rg_arrays(
        os.path.join(TEX_OUT_DIR, "Orbita7DirectorMural_s.dds"),
        np.clip(88.0 - age_mix[:, :, 0] * 85.0, 42, 98),
        np.clip(92.0 - age_mix[:, :, 0] * 90.0, 44, 102),
    )

    # 9. Orbita7TerrazzoFloor: Suelo Art-Deco de Terrazo Pizarra desgastado, grietas y juntas de bronce oxidado
    tile_u = (u * 8.0) % 1.0
    tile_v = (v * 8.0) % 1.0
    brass_inlay = ((tile_u < 0.028) | (tile_u > 0.972) | (tile_v < 0.028) | (tile_v > 0.972)).astype(np.float32)
    diag_inlay = (np.abs((tile_u - 0.5)) + np.abs((tile_v - 0.5)) < 0.14) & (
        np.abs((tile_u - 0.5)) + np.abs((tile_v - 0.5)) > 0.115
    )
    inlay = np.clip(brass_inlay + diag_inlay.astype(np.float32), 0.0, 1.0)
    stone_agg = rng.normal(0.0, 5.2, (N, N)).astype(np.float32)
    crack_mask = cellular_chip_mask(N, N, cells=18, threshold=0.16, seed=20770710) * 0.45
    floor_dust = np.clip((fbm_macro - 0.34) * 1.25 + crack_mask, 0.0, 0.82)

    stone_r = (48.0 + stone_agg) * (1.0 - floor_dust * 0.45) + 56.0 * (floor_dust * 0.45) - crack_mask * 22.0
    stone_g = (50.0 + stone_agg) * (1.0 - floor_dust * 0.45) + 50.0 * (floor_dust * 0.45) - crack_mask * 20.0
    stone_b = (56.0 + stone_agg) * (1.0 - floor_dust * 0.45) + 42.0 * (floor_dust * 0.45) - crack_mask * 18.0
    brass_r = 128.0 - floor_dust * 48.0
    brass_g = 96.0 - floor_dust * 36.0
    brass_b = 44.0 - floor_dust * 16.0

    tf_r = np.clip(stone_r * (1.0 - inlay) + brass_r * inlay, 18, 186)
    tf_g = np.clip(stone_g * (1.0 - inlay) + brass_g * inlay, 20, 152)
    tf_b = np.clip(stone_b * (1.0 - inlay) + brass_b * inlay, 20, 112)
    tf_img = Image.fromarray(np.stack([tf_r, tf_g, tf_b], axis=2).astype(np.uint8), mode="RGB")
    write_bc1_dds_from_image(os.path.join(TEX_OUT_DIR, "Orbita7TerrazzoFloor_d.dds"), tf_img)
    tn_r, tn_g = height_to_bc5_normal(inlay * 0.65 - crack_mask * 2.2 + fbm_macro * 0.35 + stone_agg * 0.03, strength=1.8)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_DIR, "Orbita7TerrazzoFloor_n.dds"), tn_r, tn_g)
    write_bc5_dds_from_rg_arrays(
        os.path.join(TEX_OUT_DIR, "Orbita7TerrazzoFloor_s.dds"),
        np.clip((88.0 - floor_dust * 46.0) * (1.0 - inlay) + (118.0 - floor_dust * 35.0) * inlay, 28, 128),
        np.clip((82.0 - floor_dust * 44.0) * (1.0 - inlay) + (108.0 - floor_dust * 32.0) * inlay, 26, 118),
    )

    bgsm_specs = [
        (
            "Orbita7CobaltSteel.BGSM",
            dict(
                diffuse_path="AeroArmor/Orbita7/Orbita7CobaltSteel_d.dds",
                normal_path="AeroArmor/Orbita7/Orbita7CobaltSteel_n.dds",
                specular_path="AeroArmor/Orbita7/Orbita7CobaltSteel_s.dds",
                envmap_path="Shared/Cubemaps/mipblur_DefaultOutside1.dds",
                envmap_scale=0.52,
                specular_color=(0.86, 0.90, 0.96),
                specular_mult=1.00,
                smoothness=0.92,
            ),
        ),
        (
            "Orbita7BrassGold.BGSM",
            dict(
                diffuse_path="AeroArmor/Orbita7/Orbita7BrassGold_d.dds",
                normal_path="AeroArmor/Orbita7/Orbita7BrassGold_n.dds",
                specular_path="AeroArmor/Orbita7/Orbita7BrassGold_s.dds",
                envmap_path="Shared/Cubemaps/mipblur_DefaultOutside1.dds",
                envmap_scale=0.78,
                specular_color=(0.96, 0.80, 0.44),
                specular_mult=1.15,
                smoothness=1.00,
            ),
        ),
        (
            "Orbita7CrimsonTrim.BGSM",
            dict(
                diffuse_path="AeroArmor/Orbita7/Orbita7CrimsonTrim_d.dds",
                normal_path="AeroArmor/Orbita7/Orbita7CrimsonTrim_n.dds",
                specular_path="AeroArmor/Orbita7/Orbita7CrimsonTrim_s.dds",
                envmap_path="Shared/Cubemaps/mipblur_DefaultOutside1.dds",
                envmap_scale=0.22,
                specular_color=(0.92, 0.84, 0.82),
                specular_mult=0.62,
                smoothness=0.72,
            ),
        ),
        (
            "Orbita7MahoganyWood.BGSM",
            dict(
                diffuse_path="AeroArmor/Orbita7/Orbita7MahoganyWood_d.dds",
                normal_path="AeroArmor/Orbita7/Orbita7MahoganyWood_n.dds",
                specular_path="AeroArmor/Orbita7/Orbita7MahoganyWood_s.dds",
                envmap_path="Shared/Cubemaps/mipblur_DefaultOutside1.dds",
                envmap_scale=0.38,
                specular_color=(0.94, 0.88, 0.78),
                specular_mult=0.88,
                smoothness=0.94,
            ),
        ),
        (
            "Orbita7CyanStasis.BGSM",
            dict(
                diffuse_path="AeroArmor/Orbita7/Orbita7CyanStasis_d.dds",
                normal_path="AeroArmor/Orbita7/Orbita7CyanStasis_n.dds",
                specular_path="AeroArmor/Orbita7/Orbita7CyanStasis_s.dds",
                envmap_path="Shared/Cubemaps/mipblur_DefaultOutside1.dds",
                envmap_scale=0.82,
                specular_color=(0.68, 0.90, 0.96),
                specular_mult=1.15,
                smoothness=1.20,
                emit_enabled=True,
                emit_color=(0.18, 0.76, 0.92),
                emit_mult=1.25,
            ),
        ),
        (
            "Orbita7SolarGlow.BGSM",
            dict(
                diffuse_path="AeroArmor/Orbita7/Orbita7SolarGlow_d.dds",
                normal_path="AeroArmor/Orbita7/Orbita7SolarGlow_n.dds",
                specular_path="AeroArmor/Orbita7/Orbita7SolarGlow_s.dds",
                envmap_path="Shared/Cubemaps/mipblur_DefaultOutside1.dds",
                envmap_scale=0.65,
                specular_color=(0.96, 0.84, 0.56),
                specular_mult=1.08,
                smoothness=1.15,
                emit_enabled=True,
                emit_color=(0.94, 0.68, 0.18),
                emit_mult=1.35,
            ),
        ),
        (
            "Orbita7ComicsAtlas.BGSM",
            dict(
                diffuse_path="AeroArmor/Orbita7/Orbita7ComicsAtlas_d.dds",
                normal_path="AeroArmor/Orbita7/Orbita7ComicsAtlas_n.dds",
                specular_path="AeroArmor/Orbita7/Orbita7ComicsAtlas_s.dds",
                envmap_path="Shared/Cubemaps/mipblur_DefaultOutside1.dds",
                envmap_scale=0.24,
                specular_color=(0.92, 0.92, 0.94),
                specular_mult=0.78,
                smoothness=0.92,
                emit_enabled=True,
                emit_color=(0.96, 0.92, 0.84),
                emit_mult=0.42,
            ),
        ),
        (
            "Orbita7DirectorMural.BGSM",
            dict(
                diffuse_path="AeroArmor/Orbita7/Orbita7DirectorMural_d.dds",
                normal_path="AeroArmor/Orbita7/Orbita7DirectorMural_n.dds",
                specular_path="AeroArmor/Orbita7/Orbita7DirectorMural_s.dds",
                envmap_path="Shared/Cubemaps/mipblur_DefaultOutside1.dds",
                envmap_scale=0.28,
                specular_color=(0.94, 0.88, 0.72),
                specular_mult=0.82,
                smoothness=0.90,
                emit_enabled=True,
                emit_color=(0.95, 0.90, 0.80),
                emit_mult=0.24,
            ),
        ),
        (
            "Orbita7TerrazzoFloor.BGSM",
            dict(
                diffuse_path="AeroArmor/Orbita7/Orbita7TerrazzoFloor_d.dds",
                normal_path="AeroArmor/Orbita7/Orbita7TerrazzoFloor_n.dds",
                specular_path="AeroArmor/Orbita7/Orbita7TerrazzoFloor_s.dds",
                envmap_path="Shared/Cubemaps/mipblur_DefaultOutside1.dds",
                envmap_scale=0.36,
                specular_color=(0.94, 0.90, 0.80),
                specular_mult=0.86,
                smoothness=0.92,
            ),
        ),
    ]
    for bgsm_fn, kw in bgsm_specs:
        raw = build_bgsm_v2_bytes(**kw)
        with open(os.path.join(MAT_OUT_DIR, bgsm_fn), "wb") as wf:
            wf.write(raw)
        print(f"[Orbita7 BGSM] {bgsm_fn} ({len(raw)} B)")


# ==============================================================================
# 2. SCRIPT BLENDER 5.2 LTS + PYNIFLY 30.2.0: 12 MODELOS ART-DECO + RENDER QA
# ==============================================================================
BLENDER_ORBITA7_SCRIPT = r'''
import math
import os
import sys
import bpy
import bmesh
from mathutils import Vector, Matrix, Euler

DONOR_NIF = r"__DONOR_NIF__"
OUT_DIR = r"__OUT_DIR__"
TEX_DIR = r"__TEX_DIR__"
PREVIEW_PNG = r"__PREVIEW_PNG__"
PYNIFLY_DIR = r"__PYNIFLY_DIR__"
FORCE_REBUILD = "__FORCE__"

if PYNIFLY_DIR not in sys.path:
    sys.path.insert(0, PYNIFLY_DIR)

MAT_DEFS = {
    "cobalt":   ("Orbita7CobaltSteel",   (0.11, 0.19, 0.31, 1.0), 0.54, 0.65, 0.0),
    "brass":    ("Orbita7BrassGold",     (0.46, 0.35, 0.16, 1.0), 0.46, 0.82, 0.0),
    "crimson":  ("Orbita7CrimsonTrim",   (0.42, 0.09, 0.10, 1.0), 0.72, 0.06, 0.0),
    "wood":     ("Orbita7MahoganyWood",  (0.31, 0.17, 0.11, 1.0), 0.62, 0.05, 0.0),
    "cyan":     ("Orbita7CyanStasis",    (0.19, 0.58, 0.71, 1.0), 0.34, 0.15, 1.25),
    "solar":    ("Orbita7SolarGlow",     (0.84, 0.56, 0.15, 1.0), 0.36, 0.15, 1.35),
    "atlas":    ("Orbita7ComicsAtlas",   (0.92, 0.88, 0.80, 1.0), 0.58, 0.05, 0.42),
    "mural":    ("Orbita7DirectorMural", (0.92, 0.88, 0.80, 1.0), 0.60, 0.12, 0.24),
    "terrazzo": ("Orbita7TerrazzoFloor", (0.20, 0.20, 0.22, 1.0), 0.62, 0.12, 0.0),
}


def clear_scene():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)
    for lt in list(bpy.data.lights):
        bpy.data.lights.remove(lt)
    for cam in list(bpy.data.cameras):
        bpy.data.cameras.remove(cam)


class PartBuilder:
    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")

    def quad(self, p0, p1, p2, p3, uvr=(0.05, 0.05, 0.95, 0.95)):
        v0 = self.bm.verts.new(p0)
        v1 = self.bm.verts.new(p1)
        v2 = self.bm.verts.new(p2)
        v3 = self.bm.verts.new(p3)
        f = self.bm.faces.new((v0, v1, v2, v3))
        u0, t0, u1, t1 = uvr
        f.loops[0][self.uv].uv = (u0, t0)
        f.loops[1][self.uv].uv = (u1, t0)
        f.loops[2][self.uv].uv = (u1, t1)
        f.loops[3][self.uv].uv = (u0, t1)
        return f

    def box(self, x0, x1, y0, y1, z0, z1, uvr=(0.05, 0.05, 0.95, 0.95), uvr_front=None, uvr_top=None):
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        if z0 > z1:
            z0, z1 = z1, z0
        uf = uvr_front or uvr
        ut = uvr_top or uvr
        self.quad((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1), uf)
        self.quad((x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1), uvr)
        self.quad((x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1), uvr)
        self.quad((x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1), uvr)
        self.quad((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1), ut)
        self.quad((x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0), ut)

    def frustum(self, bx0, bx1, by0, by1, tx0, tx1, ty0, ty1, z0, z1, uvr=(0.05, 0.05, 0.95, 0.95), uvr_front=None, uvr_top=None):
        uf = uvr_front or uvr
        ut = uvr_top or uvr
        self.quad((bx0, by0, z0), (bx1, by0, z0), (tx1, ty0, z1), (tx0, ty0, z1), uf)
        self.quad((bx1, by1, z0), (bx0, by1, z0), (tx0, ty1, z1), (tx1, ty1, z1), uvr)
        self.quad((bx0, by1, z0), (bx0, by0, z0), (tx0, ty0, z1), (tx0, ty1, z1), uvr)
        self.quad((bx1, by0, z0), (bx1, by1, z0), (tx1, ty1, z1), (tx1, ty0, z1), uvr)
        self.quad((tx0, ty0, z1), (tx1, ty0, z1), (tx1, ty1, z1), (tx0, ty1, z1), ut)
        self.quad((bx0, by1, z0), (bx1, by1, z0), (bx1, by0, z0), (bx0, by0, z0), ut)

    def cylinder(self, cx, cy, z0, z1, r0, r1, sides=16, uvr=(0.05, 0.05, 0.95, 0.95), xform=None):
        u0, t0, u1, t1 = uvr
        ring0, ring1 = [], []
        for i in range(sides):
            a = (2.0 * math.pi * i) / sides
            p0 = Vector((cx + r0 * math.cos(a), cy + r0 * math.sin(a), z0))
            p1 = Vector((cx + r1 * math.cos(a), cy + r1 * math.sin(a), z1))
            if xform is not None:
                p0 = xform @ p0
                p1 = xform @ p1
            ring0.append(self.bm.verts.new(p0))
            ring1.append(self.bm.verts.new(p1))
        for i in range(sides):
            ni = (i + 1) % sides
            ua = u0 + (u1 - u0) * (i / sides)
            ub = u0 + (u1 - u0) * ((i + 1) / sides)
            f = self.bm.faces.new((ring0[i], ring0[ni], ring1[ni], ring1[i]))
            f.loops[0][self.uv].uv = (ua, t0)
            f.loops[1][self.uv].uv = (ub, t0)
            f.loops[2][self.uv].uv = (ub, t1)
            f.loops[3][self.uv].uv = (ua, t1)
        c0 = Vector((cx, cy, z0))
        c1 = Vector((cx, cy, z1))
        if xform is not None:
            c0 = xform @ c0
            c1 = xform @ c1
        vc0 = self.bm.verts.new(c0)
        vc1 = self.bm.verts.new(c1)
        for i in range(sides):
            ni = (i + 1) % sides
            ft = self.bm.faces.new((vc1, ring1[i], ring1[ni]))
            ft.loops[0][self.uv].uv = (0.5, 0.5)
            ft.loops[1][self.uv].uv = (0.8, 0.5)
            ft.loops[2][self.uv].uv = (0.5, 0.8)
            fb = self.bm.faces.new((vc0, ring0[ni], ring0[i]))
            fb.loops[0][self.uv].uv = (0.5, 0.5)
            fb.loops[1][self.uv].uv = (0.8, 0.5)
            fb.loops[2][self.uv].uv = (0.5, 0.8)

    def sphere(self, cx, cy, cz, radius, segs=20, rings=12, uvr=(0.05, 0.05, 0.95, 0.95)):
        m = Matrix.Translation((cx, cy, cz))
        ret = bmesh.ops.create_uvsphere(self.bm, u_segments=segs, v_segments=rings, radius=radius, matrix=m)
        u0, t0, u1, t1 = uvr
        for v in ret["verts"]:
            for lp in v.link_loops:
                rel = (v.co - Vector((cx, cy, cz))).normalized()
                uu = 0.5 + math.atan2(rel.y, rel.x) / (2.0 * math.pi)
                vv = 0.5 + math.asin(max(-1.0, min(1.0, rel.z))) / math.pi
                lp[self.uv].uv = (u0 + (u1 - u0) * uu, t0 + (t1 - t0) * vv)

    def flat_ring(self, cx, cy, cz, r_in, r_out, thickness=3.0, sides=28, tilt_euler=(0.0, 0.0, 0.0), uvr=(0.05, 0.05, 0.95, 0.95)):
        xf = Matrix.Translation((cx, cy, cz)) @ Euler(tilt_euler, "XYZ").to_matrix().to_4x4()
        hz = thickness * 0.5
        in_top, in_bot, out_top, out_bot = [], [], [], []
        for i in range(sides):
            a = (2.0 * math.pi * i) / sides
            ca, sa = math.cos(a), math.sin(a)
            in_top.append(self.bm.verts.new(xf @ Vector((r_in * ca, r_in * sa, hz))))
            in_bot.append(self.bm.verts.new(xf @ Vector((r_in * ca, r_in * sa, -hz))))
            out_top.append(self.bm.verts.new(xf @ Vector((r_out * ca, r_out * sa, hz))))
            out_bot.append(self.bm.verts.new(xf @ Vector((r_out * ca, r_out * sa, -hz))))
        for i in range(sides):
            ni = (i + 1) % sides
            for vs in (
                (in_top[i], out_top[i], out_top[ni], in_top[ni]),
                (out_bot[i], in_bot[i], in_bot[ni], out_bot[ni]),
                (out_bot[i], out_bot[ni], out_top[ni], out_top[i]),
                (in_top[i], in_top[ni], in_bot[ni], in_bot[i]),
            ):
                f = self.bm.faces.new(vs)
                f.loops[0][self.uv].uv = (uvr[0], uvr[1])
                f.loops[1][self.uv].uv = (uvr[2], uvr[1])
                f.loops[2][self.uv].uv = (uvr[2], uvr[3])
                f.loops[3][self.uv].uv = (uvr[0], uvr[3])

    def star_3d(self, cx, cy, cz, r_out, r_in, depth=4.0, facing_y=True, uvr=(0.1, 0.1, 0.9, 0.9)):
        pts_f, pts_b = [], []
        hd = depth * 0.5
        for k in range(10):
            a = math.pi / 2.0 + k * (math.pi / 5.0)
            rr = r_out if (k % 2 == 0) else r_in
            if facing_y:
                pts_f.append(self.bm.verts.new((cx + rr * math.cos(a), cy - hd, cz + rr * math.sin(a))))
                pts_b.append(self.bm.verts.new((cx + rr * math.cos(a), cy + hd, cz + rr * math.sin(a))))
            else:
                pts_f.append(self.bm.verts.new((cx + rr * math.cos(a), cy + rr * math.sin(a), cz + hd)))
                pts_b.append(self.bm.verts.new((cx + rr * math.cos(a), cy + rr * math.sin(a), cz - hd)))
        cf = self.bm.verts.new((cx, cy - hd, cz) if facing_y else (cx, cy, cz + hd))
        cb = self.bm.verts.new((cx, cy + hd, cz) if facing_y else (cx, cy, cz - hd))
        for k in range(10):
            nk = (k + 1) % 10
            # Tanto +Z (XY) como -Y (XZ) conservan determinante +1, así que el bobinado coincide
            f1 = self.bm.faces.new((cf, pts_f[k], pts_f[nk]))
            f2 = self.bm.faces.new((cb, pts_b[nk], pts_b[k]))
            fs = self.bm.faces.new((pts_b[k], pts_b[nk], pts_f[nk], pts_f[k]))
            for ff in (f1, f2):
                ff.loops[0][self.uv].uv = (0.5, 0.5)
                ff.loops[1][self.uv].uv = (0.85, 0.5)
                ff.loops[2][self.uv].uv = (0.5, 0.85)
            fs.loops[0][self.uv].uv = (uvr[0], uvr[1])
            fs.loops[1][self.uv].uv = (uvr[2], uvr[1])
            fs.loops[2][self.uv].uv = (uvr[2], uvr[3])
            fs.loops[3][self.uv].uv = (uvr[0], uvr[3])

    def has_geom(self) -> bool:
        return len(self.bm.faces) > 0

    def finish(self, mesh_obj, smooth_angle_deg=32.0):
        # Todas las primitivas construyen bobinado CCW hacia el exterior; recalcular aquí invierte cajas adyacentes
        bmesh.ops.triangulate(self.bm, faces=list(self.bm.faces))
        self.bm.to_mesh(mesh_obj.data)
        self.bm.free()
        mesh_obj.data.update()


class MultiMatModel:
    def __init__(self):
        self.parts = {k: PartBuilder() for k in MAT_DEFS}
        self.col = PartBuilder()

    def p(self, key: str) -> PartBuilder:
        return self.parts[key]


# Coordenadas UV en Orbita7ComicsAtlas_d.dds (Blender V=1 arriba, V=0 abajo):
UV_ATLAS_COSMOS      = (0.01, 0.51, 0.49, 0.99)   # Q0: Capitán Cosmos #1 / Jangles / Cráter Tycho
UV_ATLAS_UNSTOPPABLE = (0.51, 0.51, 0.99, 0.99)   # Q1: Los Imparables
UV_ATLAS_DRAFTING    = (0.01, 0.01, 0.49, 0.49)   # Q2: Lámina de Entintado Clara Sterling
UV_ATLAS_CRT         = (0.51, 0.01, 0.99, 0.49)   # Q3: CRT Consola Verdadero Creyente

# Coordenadas UV en Orbita7DirectorMural_d.dds:
UV_MURAL_TOP         = (0.01, 0.51, 0.99, 0.99)   # Lema juramentado del Capitán Cosmos
UV_PLAQUE_1          = (0.02, 0.38, 0.98, 0.49)   # Placa Órbita-7
UV_PLAQUE_COSMOS     = (0.02, 0.26, 0.98, 0.37)   # Placa Vitrina Cosmos
UV_PLAQUE_UNSTOP     = (0.02, 0.14, 0.98, 0.25)   # Placa Vitrina Imparables
UV_PLAQUE_VAULT      = (0.02, 0.02, 0.98, 0.13)   # Placa Cámara Prototipos


def build_saturn_planetarium(m: MultiMatModel):
    # Suspendido del techo (Z = 0 anclaje superior -> desciende hasta Z = -196)
    m.p("brass").cylinder(0, 0, -14, 0, 48, 56, 20)
    m.p("cobalt").cylinder(0, 0, -24, -14, 34, 46, 20)
    m.p("brass").cylinder(0, 0, -118, -24, 6.5, 6.5, 14)
    # Globo central de Saturno (centro Z = -126, radio = 54)
    m.p("cobalt").sphere(0, 0, -126, 52.0, segs=24, rings=14)
    m.p("solar").cylinder(0, 0, -134, -118, 53.8, 53.8, 24)
    # Doble anillo inclinado de Saturno en latón bruñido y halo fotónico
    tilt = (math.radians(21.0), math.radians(-11.0), 0.0)
    m.p("brass").flat_ring(0, 0, -126, 72.0, 108.0, thickness=3.5, sides=32, tilt_euler=tilt)
    m.p("cyan").flat_ring(0, 0, -126, 113.0, 124.0, thickness=2.5, sides=32, tilt_euler=tilt)
    m.p("brass").flat_ring(0, 0, -126, 128.0, 152.0, thickness=3.0, sides=32, tilt_euler=tilt)
    # Luna orbital Tycho en soporte curvo
    m.p("brass").box(52, 168, -3, 3, -98, -93)
    m.p("brass").sphere(174, 0, -95, 14.0, segs=16, rings=10)
    # Alas Art-Deco del Capitán Cosmos en el mástil superior + estrella frontal y trasera
    for sgn in (-1, 1):
        for wi in range(4):
            wz = -44 - wi * 11
            wlen = 96 - wi * 16
            m.p("brass").box(sgn * 10, sgn * (10 + wlen), -3.5, 3.5, wz - 6, wz)
    m.p("crimson").cylinder(0, 0, -76, -42, 16, 16, 16)
    m.p("brass").star_3d(0, -17, -59, 18, 7.5, depth=4.0, facing_y=True)
    m.p("brass").star_3d(0, 17, -59, 18, 7.5, depth=4.0, facing_y=True)
    # Remate inferior
    m.p("brass").cylinder(0, 0, -196, -176, 2.0, 14.0, 14)
    m.col.box(-145, 182, -145, 145, -196, 0)


def _build_vitrine_shell(m: MultiMatModel, uv_panel, uv_plaque):
    # Plinto escalonado Art-Deco (Z = 0..42)
    m.p("cobalt").box(-58, 58, -28, 28, 0, 14)
    m.p("brass").box(-55, 55, -26, 26, 14, 18)
    m.p("cobalt").box(-52, 52, -24, 24, 18, 42)
    # Placa inclinada de latón legible en el frontal (-Y)
    m.p("mural").frustum(-42, 42, -31, -24, -42, 42, -26, -24, 20, 38, uvr_front=uv_plaque)
    # Pilares acanalados laterales y trasera blindada (Z = 42.0..172.0, asentados sin solape coplanar)
    m.p("cobalt").box(-42, 42, 16, 24, 42.0, 172.0)
    for sx in (-1, 1):
        x0, x1 = (-52, -42) if sx < 0 else (42, 52)
        m.p("cobalt").box(x0, x1, -22, 24, 42.0, 172.0)
        bx0, bx1 = (-42.0, -38.6) if sx < 0 else (38.6, 42.0)
        m.p("brass").box(bx0, bx1, -23.2, -19.2, 42.4, 171.6)
        m.p("cyan").box(bx0, bx1, -18.8, 15.6, 44.0, 170.0)
    # Base de terciopelo carmesí interior
    m.p("crimson").box(-41.6, 41.6, -19.8, 15.8, 42.0, 46.0)
    # Gran panel gráfico retroiluminado al fondo de la vitrina (orientado hacia -Y)
    m.p("atlas").box(-41, 41, 12, 15.5, 48, 168, uvr_front=uv_panel)
    # Cornisa escalonada superior + cresta estelar (Z = 172..196)
    m.p("brass").box(-55, 55, -26, 26, 172, 177)
    m.p("cobalt").box(-50, 50, -24, 24, 177, 188)
    m.p("crimson").box(-24, 24, -25, 22, 184, 196)
    m.p("brass").star_3d(0, -26, 188, 13, 5.5, depth=3.5, facing_y=True)
    m.col.box(-58, 58, -31, 28, 0, 196)


def build_vitrine_cosmos(m: MultiMatModel):
    _build_vitrine_shell(m, UV_ATLAS_COSMOS, UV_PLAQUE_COSMOS)
    # Diorama 3D interior: Cráter lunar Tycho + Cohete Pegasus en miniatura
    m.p("brass").cylinder(-16, -2, 46, 52, 13, 10, 16)
    m.p("crimson").cylinder(-16, -2, 52, 82, 5.5, 4.2, 14)
    m.p("brass").cylinder(-16, -2, 82, 96, 4.2, 0.6, 14)
    # Anillo del Cráter Tycho a la derecha
    m.p("brass").flat_ring(16, -3, 48, 7.0, 14.0, thickness=3.5, sides=18)
    m.p("solar").sphere(16, -3, 52, 4.5, segs=12, rings=8)


def build_vitrine_unstoppables(m: MultiMatModel):
    _build_vitrine_shell(m, UV_ATLAS_UNSTOPPABLE, UV_PLAQUE_UNSTOP)
    # 5 Pedestales escalonados con insignias 3D de Los Imparables
    xs = [-30, -15, 0, 15, 30]
    hs = [58, 66, 74, 66, 58]
    for xi, hi in zip(xs, hs):
        m.p("cobalt").cylinder(xi, -3, 46, hi, 4.5, 3.8, 12)
        m.p("brass").star_3d(xi, -3, hi + 6.5, 5.5, 2.3, depth=2.2, facing_y=True)


def build_comic_drafting_desk(m: MultiMatModel):
    # Caballetes laterales en acero cobalto + cajonera de caoba + tablero inclinado retroiluminado
    for sx in (-56, 50):
        m.p("cobalt").box(sx, sx + 6, -30, 30, 0, 6)
        m.p("cobalt").frustum(sx + 0.5, sx + 5.5, -26, -18, sx + 0.5, sx + 5.5, -18, -10, 6, 72)
        m.p("cobalt").frustum(sx + 0.5, sx + 5.5, 18, 26, sx + 0.5, sx + 5.5, 10, 18, 6, 72)
        m.p("brass").box(sx - 0.5, sx + 6.5, -24, 24, 22, 26)
    # Cajonera derecha de caoba para plumillas y guiones
    m.p("wood").box(20, 49, -24, 24, 28, 70)
    for dz in (34, 46, 58):
        m.p("brass").box(26, 43, -25.5, -24, dz, dz + 3)
    # Travesaño y bandeja frontal portamateriales
    m.p("wood").box(-58, 58, -26, 26, 70, 74)
    # Tablero de dibujo inclinado (de Z=74 en frontal Y=-28 hasta Z=92 en trasera Y=+24)
    tilt_xf = Matrix.Translation((0, -2, 83)) @ Euler((math.radians(19.0), 0, 0), "XYZ").to_matrix().to_4x4()
    # Marco de caoba del tablero inclinado (aproximado con frustum limpio + lámina retroiluminada)
    m.p("wood").frustum(-62, 62, -30, 26, -62, 62, -28, 28, 74, 80)
    # Superficie caja de luz con la lámina de entintado de Clara Sterling (Q2 del Atlas)
    m.p("atlas").quad((-46, -26, 79.8), (18, -26, 79.8), (18, 22, 91.5), (-46, 22, 91.5), UV_ATLAS_DRAFTING)
    m.p("wood").quad((-62, -28, 79.2), (62, -28, 79.2), (62, 24, 91.8), (-62, 24, 91.8))
    # Regla en T de latón sobre la lámina
    m.p("brass").quad((-50, -8, 84.4), (20, -8, 84.4), (20, -4.5, 85.3), (-50, -4.5, 85.3))
    # 3 Botes de tinta reglamentarios (Azul Cobalto, Rojo Carmesí y Oro Solar) en repisa derecha
    m.p("wood").box(24, 58, 12, 26, 80, 93)
    m.p("cobalt").cylinder(31, 19, 93, 100, 3.2, 2.8, 12)
    m.p("crimson").cylinder(41, 19, 93, 100, 3.2, 2.8, 12)
    m.p("brass").cylinder(51, 19, 93, 100, 3.2, 2.8, 12)
    # Flexo articulado de latón en esquina superior izquierda
    m.p("brass").cylinder(-50, 20, 91, 114, 1.8, 1.5, 10)
    m.p("brass").box(-51, -24, 4, 21, 112, 115)
    m.p("cobalt").cylinder(-24, 6, 105, 114, 9.5, 4.0, 14)
    m.p("solar").cylinder(-24, 6, 104, 105.5, 8.5, 8.5, 14)
    m.col.box(-62, 62, -30, 28, 0, 96)


def build_true_believer_console(m: MultiMatModel):
    # Podio semicircular Art-Deco para exámenes del Coronel Agallas
    m.p("cobalt").cylinder(0, 4, 0, 12, 62, 58, 20)
    m.p("brass").cylinder(0, 4, 12, 16, 58, 56, 20)
    m.p("cobalt").box(-52, 52, -26, 28, 16, 78)
    m.p("crimson").box(-46, 46, -28, -25, 22, 72)
    m.p("brass").star_3d(0, -29, 47, 16, 6.5, depth=3.5, facing_y=True)
    # Pupitre inclinado de mandos y botones (Z = 78..94)
    m.p("brass").box(-56, 56, -32, 30, 78, 82)
    m.p("cobalt").frustum(-54, 54, -30, 28, -50, 50, -10, 28, 82, 96)
    # Filas de teclas en latón y carmesí
    for kx in range(-36, 40, 12):
        m.p("brass").box(kx - 4, kx + 4, -26, -18, 86, 89)
        m.p("crimson").box(kx - 3, kx + 3, -16, -11, 90, 93)
    # Torreta CRT superior con pantalla «PROTOCOLO VERDADERO CREYENTE»
    m.p("cobalt").box(-38, 38, -8.9, 26, 96.1, 134)
    m.p("brass").box(-40, 40, -12, -9.0, 96.1, 136)
    m.p("atlas").box(-34, 34, -12.6, -11.5, 100, 132, uvr_front=UV_ATLAS_CRT)
    # Dos pilones laterales luminosos de estado
    for sx in (-46, 46):
        m.p("brass").cylinder(sx, 8, 96, 126, 4.5, 4.0, 12)
        m.p("cyan").sphere(sx, 8, 131, 6.0, segs=14, rings=10)
    m.col.box(-58, 58, -32, 30, 0, 136)


def build_hero_suit_pod(m: MultiMatModel):
    # Cápsula cilíndrica iluminada del Traje de Vuelo Astro-Cosmos (Z = 0..224)
    m.p("cobalt").cylinder(0, 0, 0, 16, 58, 54, 20)
    m.p("brass").cylinder(0, 0, 16, 22, 54, 50, 20)
    m.p("cobalt").cylinder(0, 0, 22, 34, 48, 46, 20)
    m.p("mural").box(-32, 32, -52, -46, 18, 32, uvr_front=UV_PLAQUE_VAULT)
    # Disco luminoso inferior/superior + respaldo luminoso de estasis cian dejando visible el maniquí heroico frontal!
    m.p("cyan").cylinder(0, 0, 34.1, 38.0, 40, 40, 20)
    m.p("cyan").cylinder(0, 0, 188.0, 191.9, 40, 40, 20)
    m.p("cyan").box(-28, 28, 18, 26, 38.1, 187.9)
    m.p("brass").cylinder(0, 0, 38.1, 85.9, 4.5, 4.5, 14)
    # Maniquí heroico 3D del Traje Astro-Cosmos completamente visible en el centro
    m.p("cobalt").box(-13, -3, 0, 10, 48, 86)
    m.p("cobalt").box(3, 13, 0, 10, 48, 86)
    m.p("crimson").box(-14, -2, -1, 11, 46, 62)
    m.p("crimson").box(2, 14, -1, 11, 46, 62)
    m.p("crimson").box(-16, 16, -9, 13, 86.1, 94)
    m.p("cobalt").frustum(-15, 15, -8, 12, -23, 23, -10, 14, 94, 146)
    m.p("crimson").cylinder(0, 2, 146, 154, 11, 9, 14)
    m.p("cobalt").sphere(0, 2, 164, 10.5, segs=16, rings=12)
    m.p("brass").star_3d(0, -11, 124, 12, 5.0, depth=3.5, facing_y=True)
    # Anillos de contención magnética y 3 costillas acorazadas traseras/laterales
    m.p("cyan").flat_ring(0, 0, 74, 39, 43, thickness=2.5, sides=24)
    m.p("cyan").flat_ring(0, 0, 156, 39, 43, thickness=2.5, sides=24)
    for ang_deg in (30.0, 90.0, 150.0):
        rad = math.radians(ang_deg)
        rx, ry = 44.0 * math.cos(rad), 44.0 * math.sin(rad)
        m.p("cobalt").box(rx - 5, rx + 5, ry - 5, ry + 5, 34.2, 191.8)
        m.p("brass").box(rx - 6, rx + 6, ry - 6, ry + 6, 108, 118)
    # Corona superior Art-Deco
    m.p("brass").cylinder(0, 0, 192, 198, 50, 54, 20)
    m.p("cobalt").cylinder(0, 0, 198, 214, 52, 36, 20)
    m.p("crimson").cylinder(0, 0, 214, 224, 24, 10, 16)
    m.col.cylinder(0, 0, 0, 224, 56, 56, 16)


def build_weapon_pedestal(m: MultiMatModel):
    # Pedestal Fotónico Acorazado para la Carabina de Rayos Astro-Cosmos (Misión 2)
    m.p("cobalt").box(-48, 48, -32, 32, 0, 14)
    m.p("brass").box(-44, 44, -28, 28, 14, 18)
    m.p("cobalt").frustum(-40, 40, -25, 25, -32, 32, -20, 20, 18, 76)
    m.p("crimson").box(-28, 28, -26, -21, 26, 68)
    m.p("brass").star_3d(0, -27, 47, 13, 5.2, depth=3.0, facing_y=True)
    # Plataforma energética superior + doble horquilla magnética para el rifle
    m.p("brass").box(-38, 38, -24, 24, 76, 82)
    m.p("cyan").box(-32, 32, -16, 16, 82, 86)
    for fx in (-22, 22):
        m.p("brass").box(fx - 3, fx + 3, -4, 4, 86, 108)
        m.p("brass").box(fx - 3, fx + 3, -10, -4, 102, 114)
        m.p("brass").box(fx - 3, fx + 3, 4, 10, 102, 114)
    # Anillo fotónico trasero
    m.p("cyan").flat_ring(0, 14, 104, 24, 30, thickness=3.0, sides=24, tilt_euler=(math.radians(90.0), 0, 0))
    m.col.box(-48, 48, -32, 32, 0, 114)


def build_pa_gantry_platform(m: MultiMatModel):
    # Pórtico Orbital Transitable para la Servoarmadura Astro-Cosmos (Misión 3)
    # Plataforma baja (Z = 0..12) con rampa frontal suave para que el jugador suba y entre en la PA!
    m.p("cobalt").cylinder(0, 0, 0, 10, 104, 100, 24)
    m.p("brass").cylinder(0, 0, 10, 12, 98, 96, 24)
    m.p("solar").flat_ring(0, 0, 12.2, 54, 62, thickness=1.5, sides=24)
    # Rampa frontal (-Y) separada 0.2u en Z para evitar caras coplanares con la peana circular
    m.p("brass").frustum(-46, 46, -124, -88, -46, 46, -98, -82, 0.2, 11.8)
    # Dos grandes torres laterales fuera del vano central X=[-68..+68]
    for sgn in (-1, 1):
        cx = sgn * 84.0
        m.p("cobalt").box(cx - 14, cx + 14, -24, 28, 12, 224)
        m.p("brass").box(cx - 16, cx + 16, -26, 30, 88, 96)
        m.p("brass").box(cx - 16, cx + 16, -26, 30, 168, 176)
        m.p("cyan").box(cx - 4, cx + 4, -27, -23, 24, 212)
        # Brazo grúa articulado superior apuntando hacia los hombros del bastidor PA (Z > 196, libre de cabezas)
        bx0, bx1 = (cx - 48, cx) if sgn > 0 else (cx, cx + 48)
        m.p("brass").box(bx0, bx1, -6, 12, 198, 208)
    # Arco puente superior coronado con estrella alada (Z = 224..252)
    m.p("cobalt").box(-102, 102, -26, 30, 224, 244)
    m.p("brass").box(-106, 106, -28, 32, 244, 250)
    m.p("crimson").box(-36, 36, -30, 28, 232, 256)
    m.p("brass").star_3d(0, -31, 244, 16, 6.5, depth=4.0, facing_y=True)

    # Colisión EXACTA transitable: plataforma baja + 2 torres laterales + puente alto (vano central 100% abierto!)
    m.col.box(-98, 98, -98, 98, 0, 12)
    m.col.frustum(-46, 46, -124, -96, -46, 46, -98, -94, 0, 12)
    m.col.box(-98, -70, -26, 30, 12, 224)
    m.col.box(70, 98, -26, 30, 12, 224)
    m.col.box(-104, 104, -28, 32, 224, 254)


def build_solar_reliquary(m: MultiMatModel):
    # Relicario Solar de Triple Halo para el Cañón Orbital Gauss (Misión 4)
    m.p("cobalt").cylinder(0, 0, 0, 16, 66, 62, 24)
    m.p("brass").cylinder(0, 0, 16, 22, 62, 58, 24)
    m.p("cobalt").frustum(-48, 48, -30, 30, -40, 40, -24, 24, 22, 82)
    m.p("crimson").box(-34, 34, -31, -24, 30, 74)
    m.p("mural").box(-30, 30, -33, -30, 38, 64, uvr_front=UV_PLAQUE_1)
    # Cuna pesada de oro solar para el Cañón Orbital Gauss
    m.p("brass").box(-46, 46, -26, 26, 82, 88)
    m.p("solar").box(-38, 38, -14, 14, 88, 93)
    for fx in (-28, 28):
        m.p("brass").box(fx - 4, fx + 4, -6, 6, 93, 118)
        m.p("brass").box(fx - 4, fx + 4, -14, -6, 110, 126)
        m.p("brass").box(fx - 4, fx + 4, 6, 14, 110, 126)
    # Triple halo solar concéntrico detrás del arma (Z centro = 122)
    m.p("brass").flat_ring(0, 18, 122, 46, 54, thickness=4.0, sides=28, tilt_euler=(math.radians(90.0), 0, 0))
    m.p("solar").flat_ring(0, 18, 122, 34, 41, thickness=3.5, sides=28, tilt_euler=(math.radians(90.0), 0, 0))
    m.p("brass").star_3d(0, 18, 178, 14, 5.5, depth=4.0, facing_y=True)
    m.col.box(-58, 58, -34, 34, 0, 168)


def build_cosmos_bed(m: MultiMatModel):
    # Cama Espacial del Capitán Cosmos (dimensiones exactas PlayerHouseBed01: X[-70..70], Y[-100..96], colchón Z=42, cabecero +Y)
    # Bastidor aerodinámico en acero cobalto y latón con aletas traseras
    m.p("cobalt").box(-68, 68, -98, 81.9, 0.1, 26)
    m.p("brass").box(-70.2, 70.2, -99.8, 81.8, 24, 29)
    # Colchón acolchado carmesí imperial (superficie exacta Z = 42.0 para animación de dormir!)
    m.p("crimson").box(-64, 64, -94, 81.9, 29.05, 42)
    # Emblema dorado tejido a los pies de la colcha y almohadas dobles en +Y
    m.p("brass").box(-64.4, 64.4, -52, -46, 29.4, 42.4)
    m.p("cobalt").box(-56, -8, 48, 78, 42, 49)
    m.p("cobalt").box(8, 56, 48, 78, 42, 49)
    # Piecero redondeado bajo (-Y)
    m.p("cobalt").box(-69.8, 69.8, -101, -94.2, 4, 43.9)
    m.p("brass").box(-71, 71, -102, -93, 44.0, 48.0)
    # Cabecero monumental Art-Deco en +Y (Z = 0..84) con lámparas de lectura y estrella de Saturno
    m.p("cobalt").box(-72, 72, 82, 96, 0, 78)
    m.p("brass").box(-74, 74, 80, 97, 76, 82)
    m.p("crimson").box(-44, 44, 79, 83, 44, 74)
    m.p("brass").flat_ring(0, 78, 60, 15, 22, thickness=2.5, sides=24, tilt_euler=(math.radians(90.0), 0, math.radians(18.0)))
    m.p("brass").star_3d(0, 78, 60, 12, 5.0, depth=3.0, facing_y=True)
    for lx in (-58, 58):
        m.p("cyan").box(lx - 6, lx + 6, 79, 82, 52, 68)
    m.col.box(-70, 70, -100, 96, 0, 42)
    m.col.box(-72, 72, 82, 96, 42, 82)


def build_star_chest(m: MultiMatModel):
    # Baúl Acorazado Estelar (contenedor seguro sin reseteo del jugador: X[-46..46], Y[-26..26], Z[0..54])
    m.p("brass").box(-46, 46, -26, 26, 0, 5)
    m.p("cobalt").box(-44, 44, -24, 24, 5, 36)
    # Tapa abovedada superior
    m.p("cobalt").frustum(-45, 45, -25, 25, -40, 40, -18, 18, 36, 52)
    # Paneles frontales carmesí alojados limpiamente entre las tres costillas de latón
    m.p("crimson").box(-27.5, -4.5, -25.0, -24.0, 10, 32)
    m.p("crimson").box(4.5, 27.5, -25.0, -24.0, 10, 32)
    # Costillas de refuerzo en latón (cuerpo 5.2..35.8 + tapa 36.2..53.0 con junta sin solape) + estrella alada
    for bx in (-32, 0, 32):
        m.p("brass").box(bx - 3, bx + 3, -25.8, 25.8, 5.2, 35.8)
        m.p("brass").frustum(bx - 3, bx + 3, -25.8, 25.8, bx - 3, bx + 3, -18.8, 18.8, 36.2, 53.0)
    m.p("brass").star_3d(0, -27.5, 35, 10, 4.2, depth=3.0, facing_y=True)
    m.col.box(-46, 46, -26, 26, 0, 53)


def build_director_mural_frame(m: MultiMatModel):
    # Gran Mural Enmarcado del Juramento del Capitán Cosmos para la Sala del Director
    # Dimensiones: X[-165..165] (330 ancho!), Y[-8..8], Z[0..176]
    m.p("brass").box(-168, 168, -8, 8, 0, 10)
    m.p("brass").box(-168, 168, -8, 8, 166, 176)
    m.p("brass").box(-168, -156, -8, 8, 10, 166)
    m.p("brass").box(156, 168, -8, 8, 10, 166)
    m.p("cobalt").box(-156, 156, -5, 8, 10, 166)
    # Lienzo retroiluminado con el lema «¡POR LA VERDAD, LAS ESTRELLAS Y EL MAÑANA!» en la cara -Y
    m.p("mural").box(-152, 152, -6.5, -4.5, 14, 162, uvr_front=UV_MURAL_TOP)
    m.p("brass").star_3d(0, -9, 176, 18, 7.5, depth=4.0, facing_y=True)
    m.col.box(-168, 168, -8, 8, 0, 178)


def build_security_barrier(m: MultiMatModel):
    # Barrera Láser / Fotónica de Seguridad (240 ancho x 236 alto) que sella cada cámara hasta superar el examen del Coronel Agallas
    for sx in (-122, 114):
        m.p("cobalt").box(sx, sx + 8, -8, 8, 16.05, 219.95)
        m.p("brass").box(sx - 1, sx + 9, -9, 9, 0.1, 16.0)
        m.p("brass").box(sx - 1, sx + 9, -9, 9, 220.0, 235.9)
    for hz in (36, 78, 120, 162, 204):
        m.p("cyan").box(-114, 114, -2.0, 2.0, hz, hz + 5.5)
    m.p("crimson").box(-36, 36, -4.5, 4.5, 112, 134)
    m.p("brass").star_3d(0, -5.5, 123, 9.5, 4.0, depth=2.5, facing_y=True)
    m.col.box(-122, 122, -8, 8, 0, 236)


def build_studio_hall_complex(m: MultiMatModel):
    """
    Escenario arquitectónico subterráneo 100% propio en Blender para «Estudio Órbita-7» (5 salas Art-Deco conectadas en Z=0):
      1. Rotonda Central del Planetario:     X[-640..+640],   Y[-640..+640],   Z[0..420]
      2. Sala de Guionistas (Ala Este):      X[+664..+1440],  Y[-416..+416],   Z[0..320] (vano X=640..664, Y[-120..+120], Z[0..240])
      3. Laboratorio Fotónico (Ala Oeste):   X[-1440..-664],  Y[-416..+416],   Z[0..320] (vano X=-664..-640, Y[-120..+120], Z[0..240])
      4. Hangar Orbital y Relicario (Norte): X[-768..+768],   Y[+664..+1792],  Z[0..384] (vano Y=640..664, X[-140..+140], Z[0..260])
      5. Sala Director y Refugio (Sureste):  X[+664..+1440],  Y[-1248..-448],  Z[0..320] (vano Y=-448..-416, X[+920..+1160], Z[0..240])
    Cero caras coplanares entre materiales/muros y portal empotrado limpio para HitDoorSm01Load en el muro Sur.
    """
    W = 24.0  # Espesor de muros y losas estancas

    def add_cobalt_block(x0, x1, y0, y1, z0, z1):
        ux = max(1.0, abs(x1 - x0) / 256.0)
        uy = max(1.0, abs(y1 - y0) / 256.0)
        uz = max(1.0, abs(z1 - z0) / 256.0)
        m.p("cobalt").box(x0, x1, y0, y1, z0, z1, uvr=(0.0, 0.0, max(ux, uy), uz))
        m.col.box(x0, x1, y0, y1, z0, z1)

    def add_trim(face, u0, u1, plane_coord, z_ceil, wainscot=True):
        """Añade zócalo carmesí + moldura de latón + cornisa superior exclusivamente hacia la cara interior indicada."""
        u_span = max(1.0, abs(u1 - u0) / 256.0)
        # Crown molding superior (de z_ceil-12 a z_ceil-0.2)
        if face == "N":
            m.p("brass").box(u0, u1, plane_coord, plane_coord + 2.8, z_ceil - 12.0, z_ceil - 0.2)
            if wainscot:
                m.p("crimson").box(u0, u1, plane_coord, plane_coord + 1.8, 0.5, 62.0, uvr=(0.0, 0.0, u_span * 2.0, 0.5))
                m.p("brass").box(u0, u1, plane_coord, plane_coord + 2.8, 62.05, 68.0)
        elif face == "S":
            m.p("brass").box(u0, u1, plane_coord - 2.8, plane_coord, z_ceil - 12.0, z_ceil - 0.2)
            if wainscot:
                m.p("crimson").box(u0, u1, plane_coord - 1.8, plane_coord, 0.5, 62.0, uvr=(0.0, 0.0, u_span * 2.0, 0.5))
                m.p("brass").box(u0, u1, plane_coord - 2.8, plane_coord, 62.05, 68.0)
        elif face == "E":
            m.p("brass").box(plane_coord, plane_coord + 2.8, u0, u1, z_ceil - 12.0, z_ceil - 0.2)
            if wainscot:
                m.p("crimson").box(plane_coord, plane_coord + 1.8, u0, u1, 0.5, 62.0, uvr=(0.0, 0.0, u_span * 2.0, 0.5))
                m.p("brass").box(plane_coord, plane_coord + 2.8, u0, u1, 62.05, 68.0)
        elif face == "W":
            m.p("brass").box(plane_coord - 2.8, plane_coord, u0, u1, z_ceil - 12.0, z_ceil - 0.2)
            if wainscot:
                m.p("crimson").box(plane_coord - 1.8, plane_coord, u0, u1, 0.5, 62.0, uvr=(0.0, 0.0, u_span * 2.0, 0.5))
                m.p("brass").box(plane_coord - 2.8, plane_coord, u0, u1, 62.05, 68.0)

    def add_floor_and_ceiling(x0, x1, y0, y1, z_ceil, skylight_r=0.0):
        tx = max(1.0, (x1 - x0) / 512.0)
        ty = max(1.0, (y1 - y0) / 512.0)
        m.p("terrazzo").box(x0, x1, y0, y1, -W, 0.0, uvr_top=(0.0, 0.0, tx, ty))
        m.col.box(x0, x1, y0, y1, -W, 0.0)
        m.p("cobalt").box(x0, x1, y0, y1, z_ceil, z_ceil + W, uvr=(0.0, 0.0, tx * 2.0, ty * 2.0))
        m.col.box(x0, x1, y0, y1, z_ceil, z_ceil + W)
        # Moldura perimetral luminosa escalonada sin caras coplanares con el techo ni entre sí
        cx = 0.5 * (x0 + x1)
        cy = 0.5 * (y0 + y1)
        rx = 0.36 * (x1 - x0)
        ry = 0.36 * (y1 - y0)
        if skylight_r > 0.0:
            m.p("brass").flat_ring(cx, cy, z_ceil - 3.2, skylight_r, skylight_r + 22.0, thickness=5.6, sides=28)
            m.p("cyan").cylinder(cx, cy, z_ceil - 4.5, z_ceil - 0.8, skylight_r - 0.4, skylight_r - 0.4, 28)
        else:
            m.p("brass").box(cx - rx - 8, cx + rx + 8, cy - ry - 8, cy + ry + 8, z_ceil - 5.0, z_ceil - 0.3)
            m.p("solar").box(cx - rx, cx + rx, cy - ry, cy + ry, z_ceil - 7.0, z_ceil - 5.5)

    def add_portal_frame(x0, x1, y0, y1, z_open, along_x=True):
        # Jamba dorada Art-Deco ligeramente sobresaliente hacia el vano para cero caras coplanares
        if along_x:
            m.p("brass").box(x0 - 12.0, x0 + 1.5, y0 - 4.0, y1 + 4.0, 0.3, z_open - 0.05)
            m.p("brass").box(x1 - 1.5, x1 + 12.0, y0 - 4.0, y1 + 4.0, 0.3, z_open - 0.05)
            m.p("brass").box(x0 - 14.0, x1 + 14.0, y0 - 5.0, y1 + 5.0, z_open - 1.5, z_open + 14.0)
        else:
            m.p("brass").box(x0 - 4.0, x1 + 4.0, y0 - 12.0, y0 + 1.5, 0.3, z_open - 0.05)
            m.p("brass").box(x0 - 4.0, x1 + 4.0, y1 - 1.5, y1 + 12.0, 0.3, z_open - 0.05)
            m.p("brass").box(x0 - 5.0, x1 + 5.0, y0 - 14.0, y1 + 14.0, z_open - 1.5, z_open + 14.0)

    def add_pilaster(px, py, z_h):
        m.p("brass").box(px - 18, px + 18, py - 18, py + 18, 0.3, 14.0)
        m.p("cobalt").box(px - 14, px + 14, py - 14, py + 14, 14.05, z_h - 16.05)
        m.p("brass").box(px - 6, px + 6, py - 15.5, py + 15.5, 20.0, z_h - 22.0)
        m.p("brass").box(px - 19, px + 19, py - 19, py + 19, z_h - 16.0, z_h - 0.3)
        m.col.box(px - 16, px + 16, py - 16, py + 16, 0.0, z_h)

    # --- 1. ROTONDA CENTRAL DEL PLANETARIO (X[-640..640], Y[-640..640], Z[0..420]) ---
    add_floor_and_ceiling(-640, 640, -640, 640, 420.0, skylight_r=195.0)
    # Medallón estelar escalonado limpio sobre Z=0.0 sin solapamientos
    m.p("crimson").cylinder(0, 0, 0.5, 1.5, 164.8, 164.8, 32)
    m.p("brass").flat_ring(0, 0, 1.15, 166.0, 185.0, thickness=1.3, sides=32)
    m.p("brass").star_3d(0, 0, 2.05, 138, 56, depth=1.0, facing_y=False)

    # Muro Sur de la Rotonda con pórtico Art-Deco exacto para UtilMetalDoorLoad01 en (0, -624, 0)
    add_cobalt_block(-640, -58.0, -664, -640, 0, 420)
    add_cobalt_block(58.0, 639.0, -664, -640, 0, 420)
    add_cobalt_block(-58.0, 58.0, -664, -640, 186.5, 420)
    # Umbral y cierre trasero retranqueado a Y=-652 (12u detrás del plano Y=-640 de la puerta -> 0 Z-fighting en float16)
    m.p("terrazzo").box(-57.5, 57.5, -652.0, -640.5, -W, -0.25)
    m.col.box(-58.0, 58.0, -664.0, -640.0, -W, 0.0)
    m.p("cobalt").box(-57.5, 57.5, -663.5, -652.0, 0.25, 185.5)
    m.col.box(-58.0, 58.0, -664.0, -652.0, 0.0, 186.0)
    # Jambas y dintel de latón que ocultan al 100% el reborde negro [-56..56]x[0..176] respetando la hoja [-48..48]x[1..168]
    m.p("brass").box(-70.0, -48.5, -651.0, -618.0, 0.25, 168.0)
    m.p("brass").box(48.5, 70.0, -651.0, -618.0, 0.25, 168.0)
    m.col.box(-70.0, -49.5, -652.0, -618.0, 0.0, 168.5)
    m.col.box(49.5, 70.0, -652.0, -618.0, 0.0, 168.5)
    m.p("brass").box(-73.0, 73.0, -650.5, -617.5, 168.5, 186.0)
    m.p("crimson").box(-40.0, 40.0, -617.0, -615.5, 171.0, 183.5)
    m.p("brass").star_3d(0, -614.0, 177.25, 8.0, 3.5, depth=2.0, facing_y=True)
    # Zócalos y cornisa Sur hacia +Y (separados de las jambas ±70.0 y esquinas E/O en float16)
    add_trim("N", -636.5, -71.0, -640, 420, wainscot=True)
    add_trim("N", 71.0, 636.5, -640, 420, wainscot=True)
    m.p("brass").box(-70.5, 70.5, -640, -637.2, 408.0, 419.8)

    # Muro Norte de la Rotonda con gran pórtico hacia el Hangar Orbital (X[-140..+140], Z[0..260])
    add_cobalt_block(-640, -140, 640, 664, 0, 420)
    add_cobalt_block(140, 640, 640, 664, 0, 420)
    add_cobalt_block(-140, 140, 640, 664, 274.05, 420)
    m.p("terrazzo").box(-140, 140, 640, 664, -W, 0.0)
    m.col.box(-140, 140, 640, 664, -W, 0.0)
    add_portal_frame(-140, 140, 640, 664, 260, along_x=True)
    add_trim("S", -640, -152.2, 640, 420, wainscot=True)
    add_trim("S", 152.2, 640, 640, 420, wainscot=True)
    m.p("brass").box(-152.1, 152.1, 637.2, 640, 408.0, 419.8)
    # Zócalo del lado Norte (Hangar) de este mismo muro divisorio
    add_trim("N", -640, -152.2, 664, 384, wainscot=True)
    add_trim("N", 152.2, 640, 664, 384, wainscot=True)
    m.p("brass").box(-152.1, 152.1, 664, 666.8, 372.0, 383.8)

    # Muro Este de la Rotonda (X[640..664], prolongado hasta Y=-664 para sellar esquina con Sala Director)
    add_cobalt_block(640, 664, -664, -120, 0, 420)
    add_cobalt_block(640, 664, 120, 640, 0, 420)
    add_cobalt_block(640, 664, -120, 120, 254.05, 420)
    m.p("terrazzo").box(640, 664, -120, 120, -W, 0.0)
    m.col.box(640, 664, -120, 120, -W, 0.0)
    add_portal_frame(640, 664, -120, 120, 240, along_x=False)
    add_trim("W", -637.0, -132.2, 640, 420, wainscot=True)
    add_trim("W", 132.2, 637.0, 640, 420, wainscot=True)
    m.p("brass").box(637.2, 640, -132.1, 132.1, 408.0, 419.8)
    # Zócalos del lado Este de este muro (Ala Este Y[-413..413])
    add_trim("E", -413.0, -132.2, 664, 320, wainscot=True)
    add_trim("E", 132.2, 413.0, 664, 320, wainscot=True)
    m.p("brass").box(664, 666.8, -132.1, 132.1, 308.0, 319.8)

    # Muro Oeste de la Rotonda con pórtico hacia el Laboratorio Fotónico (Y[-120..+120], Z[0..240])
    add_cobalt_block(-664, -640, -640, -120, 0, 420)
    add_cobalt_block(-664, -640, 120, 640, 0, 420)
    add_cobalt_block(-664, -640, -120, 120, 254.05, 420)
    m.p("terrazzo").box(-664, -640, -120, 120, -W, 0.0)
    m.col.box(-664, -640, -120, 120, -W, 0.0)
    add_portal_frame(-664, -640, -120, 120, 240, along_x=False)
    add_trim("E", -637.0, -132.2, -640, 420, wainscot=True)
    add_trim("E", 132.2, 637.0, -640, 420, wainscot=True)
    m.p("brass").box(-640, -637.2, -132.1, 132.1, 408.0, 419.8)
    # Zócalos del lado Oeste de este muro (Ala Oeste Y[-413..413])
    add_trim("W", -413.0, -132.2, -664, 320, wainscot=True)
    add_trim("W", 132.2, 413.0, -664, 320, wainscot=True)
    m.p("brass").box(-666.8, -664, -132.1, 132.1, 308.0, 319.8)

    for px in (-608, 608):
        for py in (-608, -260, 260, 608):
            add_pilaster(px, py, 420)

    # --- 2. SALA DE GUIONISTAS Y ENTINTADO (X[664..1440], Y[-416..+416], Z[0..320]) ---
    add_floor_and_ceiling(664, 1440, -416, 416, 320.0)
    add_cobalt_block(1440, 1464, -416, 416, 0, 320)
    add_trim("W", -413.0, 413.0, 1440, 320, wainscot=True)
    add_cobalt_block(664, 1440, 416, 440, 0, 320)
    add_trim("S", 664, 1440, 416, 320, wainscot=True)
    # Muro Sur divisorio entre Ala Este y Sala del Director (Y[-448..-416], paso X[920..1160], Z[0..240])
    add_cobalt_block(664, 920, -448, -416, 0, 320)
    add_cobalt_block(1160, 1440, -448, -416, 0, 320)
    add_cobalt_block(920, 1160, -448, -416, 254.05, 320)
    m.p("terrazzo").box(920, 1160, -448, -416, -W, 0.0)
    m.col.box(920, 1160, -448, -416, -W, 0.0)
    add_portal_frame(920, 1160, -448, -416, 240, along_x=True)
    add_trim("N", 664, 907.8, -416, 320, wainscot=True)
    add_trim("N", 1172.2, 1440, -416, 320, wainscot=True)
    m.p("brass").box(907.9, 1172.1, -416, -413.2, 308.0, 319.8)
    # Zócalo del lado Sur (Sala Director) en este mismo muro divisorio
    add_trim("S", 664, 907.8, -448, 320, wainscot=True)
    add_trim("S", 1172.2, 1440, -448, 320, wainscot=True)
    m.p("brass").box(907.9, 1172.1, -450.8, -448, 308.0, 319.8)

    # --- 3. LABORATORIO FOTÓNICO (X[-1440..-664], Y[-416..+416], Z[0..320]) ---
    add_floor_and_ceiling(-1440, -664, -416, 416, 320.0)
    add_cobalt_block(-1464, -1440, -416, 416, 0, 320)
    add_trim("E", -413.0, 413.0, -1440, 320, wainscot=True)
    add_cobalt_block(-1440, -664, 416, 440, 0, 320)
    add_trim("S", -1440, -664, 416, 320, wainscot=True)
    add_cobalt_block(-1440, -664, -440, -416, 0, 320)
    add_trim("N", -1440, -664, -416, 320, wainscot=True)

    # --- 4. HANGAR ORBITAL Y RELICARIO SOLAR (X[-768..+768], Y[664..1792], Z[0..384]) ---
    add_floor_and_ceiling(-768, 768, 664, 1792, 384.0, skylight_r=220.0)
    add_cobalt_block(-792, -768, 664, 1792, 0, 384)
    add_trim("E", 667.0, 1789.0, -768, 384, wainscot=True)
    add_cobalt_block(768, 792, 664, 1792, 0, 384)
    add_trim("W", 667.0, 1789.0, 768, 384, wainscot=True)
    add_cobalt_block(-768, 768, 1792, 1816, 0, 384)
    add_trim("S", -768, 768, 1792, 384, wainscot=True)
    # Cerramientos laterales Sur del Hangar donde sobresale respecto a la Rotonda
    add_cobalt_block(-768, -640.05, 640, 664, 0, 384)
    add_trim("N", -768, -640.1, 664, 384, wainscot=True)
    add_cobalt_block(640.05, 768, 640, 664, 0, 384)
    add_trim("N", 640.1, 768, 664, 384, wainscot=True)
    for py_h in (960, 1380, 1740):
        add_pilaster(-736, py_h, 384)
        add_pilaster(736, py_h, 384)

    # --- 5. SALA DE PROYECCIÓN DEL DIRECTOR Y APOSENTOS (X[664..1440], Y[-1248..-448], Z[0..320]) ---
    add_floor_and_ceiling(664, 1440, -1248, -448, 320.0)
    add_cobalt_block(640, 664, -1248, -664.05, 0, 320)
    add_trim("E", -1245.0, -451.0, 664, 320, wainscot=True)
    add_cobalt_block(1440, 1464, -1248, -416.05, 0, 320)
    add_trim("W", -1245.0, -451.0, 1440, 320, wainscot=True)
    add_cobalt_block(664, 1440, -1272, -1248, 0, 320)
    add_trim("N", 664, 1440, -1248, 320, wainscot=True)


def build_exterior_bunker_plinth(m: MultiMatModel):
    """Brocal/zócalo exterior Art-Deco bajo MetalTrapdoor01 en el callejón trasero de Hubris Comics."""
    # Falda de cimentación biselada que sella -14 unidades bajo Z=0 contra la acera del callejón
    m.p("terrazzo").frustum(-70, 70, -78, 78, -56, 56, -64, 64, -14.0, 5.5)
    # Plataforma central de acero cobalto donde apoya a ras MetalTrapdoor01 (Z=6.0)
    m.p("cobalt").box(-52, 52, -60, 60, 0.0, 6.0)
    # Marco perimetral biselado de latón dorado alrededor de MetalTrapdoor01 (-38..38 x -46..46)
    m.p("brass").box(-46, -39, -46.9, 46.9, 5.5, 8.0)
    m.p("brass").box(39, 46, -46.9, 46.9, 5.5, 8.0)
    m.p("brass").box(-46, 46, -54, -47, 5.5, 8.0)
    m.p("brass").box(-46, 46, 47, 54, 5.5, 8.0)
    # Placas carmesí Hubris Comics en los frentes norte y sur del brocal (sobresalen 0.6u para evitar Z-fighting)
    m.p("crimson").box(-24, 24, -60.6, -54.5, 6.0, 7.5)
    m.p("crimson").box(-24, 24, 54.5, 60.6, 6.0, 7.5)
    # Estrellas doradas en las esquinas
    for sx, sy in ((-42.5, -50.5), (42.5, -50.5), (-42.5, 50.5), (42.5, 50.5)):
        m.p("brass").box(sx - 3.0, sx + 3.0, sy - 3.0, sy + 3.0, 7.8, 9.2)
    # Tiras cian sutiles de balizamiento en los flancos
    m.p("cyan").box(-55, -52.5, -44, 44, 4.5, 6.4)
    m.p("cyan").box(52.5, 55, -44, 44, 4.5, 6.4)
    # Colisión estática baja transitable sin escalón brusco
    m.col.frustum(-68, 68, -76, 76, -52, 52, -60, 60, -12.0, 6.0)


PREVIEW_BUILDERS = [
    ("Orbita7_SaturnPlanetarium.nif",        build_saturn_planetarium),
    ("Orbita7_LoreVitrine_Cosmos.nif",       build_vitrine_cosmos),
    ("Orbita7_LoreVitrine_Unstoppables.nif", build_vitrine_unstoppables),
    ("Orbita7_ComicDraftingDesk.nif",        build_comic_drafting_desk),
    ("Orbita7_TrueBelieverConsole.nif",      build_true_believer_console),
    ("Orbita7_HeroSuitPod.nif",              build_hero_suit_pod),
    ("Orbita7_WeaponPedestal.nif",           build_weapon_pedestal),
    ("Orbita7_PAGantryPlatform.nif",         build_pa_gantry_platform),
    ("Orbita7_SolarReliquary.nif",           build_solar_reliquary),
    ("Orbita7_CosmosBed.nif",                build_cosmos_bed),
    ("Orbita7_StarChest.nif",                build_star_chest),
    ("Orbita7_DirectorMuralFrame.nif",       build_director_mural_frame),
]

MODEL_BUILDERS = PREVIEW_BUILDERS + [
    ("Orbita7_SecurityBarrier.nif",          build_security_barrier),
    ("Orbita7_StudioHallComplex.nif",        build_studio_hall_complex),
    ("Orbita7_ExteriorBunkerPlinth.nif",     build_exterior_bunker_plinth),
]


def setup_fo4_mat(template_mat, key: str):
    stem, rgba, rough, metal, emit_s = MAT_DEFS[key]
    mat = template_mat.copy()
    mat.name = stem
    mat["BS_Shader_Block_Name"] = "BSLightingShaderProperty"
    mat["BSLSP_Shader_Name"] = f"Materials\\AeroArmor\\Orbita7\\{stem}.BGSM"
    mat["BSShaderTextureSet_Diffuse"] = f"textures\\AeroArmor\\Orbita7\\{stem}_d.dds"
    mat["BSShaderTextureSet_Normal"] = f"textures\\AeroArmor\\Orbita7\\{stem}_n.dds"
    mat["BSShaderTextureSet_Specular"] = f"textures\\AeroArmor\\Orbita7\\{stem}_s.dds"
    for k in ["NiAlphaProperty_flags", "NiAlphaProperty_threshold", "BSShaderTextureSet_EnvMap", "BSShaderTextureSet_EnvMapMask", "BSLSP_Shader_Type"]:
        if k in mat:
            del mat[k]
    return mat


def export_all_orbita7_models():
    os.makedirs(OUT_DIR, exist_ok=True)
    for nif_fn, fn_builder in MODEL_BUILDERS:
        dst_path = os.path.join(OUT_DIR, nif_fn)
        if FORCE_REBUILD == "0" and os.path.isfile(dst_path):
            print(f"[Orbita7 Skip Existing] {nif_fn}")
            continue
        clear_scene()
        bpy.ops.import_scene.pynifly(
            filepath=DONOR_NIF,
            import_cutpoints=False,
            import_tris=False,
            import_collisions=True,
        )
        root_obj = [o for o in bpy.data.objects if o.type == "EMPTY" and o.get("pynRoot")][0]
        donor_vis = [o for o in bpy.data.objects if o.type == "MESH" and not o.name.startswith("bhk")][0]
        col_obj = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("bhk")][0]
        tmpl_mat = donor_vis.data.materials[0]

        root_name = os.path.splitext(nif_fn)[0]
        root_obj.name = f"{root_name}:ROOT"
        root_obj["pynNodeName"] = root_name

        mm = MultiMatModel()
        fn_builder(mm)

        mm.col.finish(col_obj)
        col_obj["pynRigidBody"] = "bhkPhysicsSystem"
        col_obj["pynCollisionShapeType"] = "compressed_mesh"

        vis_objs = []
        first_used = False
        for key, pb in mm.parts.items():
            if not pb.has_geom():
                continue
            mat = setup_fo4_mat(tmpl_mat, key)
            if not first_used:
                first_used = True
                donor_vis.name = f"{root_name}_{key}"
                donor_vis["pynNodeName"] = f"{root_name}_{key}"
                donor_vis.data.materials.clear()
                donor_vis.data.materials.append(mat)
                pb.finish(donor_vis)
                vis_objs.append(donor_vis)
            else:
                mdata = bpy.data.meshes.new(f"{root_name}_{key}_m")
                vobj = bpy.data.objects.new(f"{root_name}_{key}", mdata)
                bpy.context.scene.collection.objects.link(vobj)
                vobj.parent = root_obj
                vobj["pynBlockName"] = "BSTriShape"
                vobj["pynNodeName"] = f"{root_name}_{key}"
                vobj.data.materials.append(mat)
                pb.finish(vobj)
                vis_objs.append(vobj)

        bpy.ops.object.select_all(action="DESELECT")
        for vo in vis_objs:
            vo.select_set(True)
        bpy.context.view_layer.objects.active = vis_objs[0]

        dst_path = os.path.join(OUT_DIR, nif_fn)
        bpy.ops.export_scene.pynifly(filepath=dst_path, target_game="FO4")
        print(f"[Orbita7 Exported] {nif_fn} ({os.path.getsize(dst_path):,} B, {len(vis_objs)} BSTriShapes)")

    if FORCE_REBUILD == "0" and os.path.isfile(PREVIEW_PNG):
        return

    # --------------------------------------------------------------------------
    # Renderizar lámina QA de estudio (4x3 de las 12 piezas Art-Deco texturizadas)
    # --------------------------------------------------------------------------
    clear_scene()
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 2200
    scene.render.resolution_y = 1480

    if scene.world is None:
        scene.world = bpy.data.worlds.new("Orbita7World")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.055, 0.075, 0.125, 1.0)
        bg.inputs[1].default_value = 1.15

    # Iluminación de estudio cálida y contra-luz cian espacial
    for lname, energy, col, rot in [
        ("KeyLight",  4.2, (1.00, 0.96, 0.88), (math.radians(52), math.radians(-20), math.radians(28))),
        ("FillLight", 2.0, (0.72, 0.88, 1.00), (math.radians(64), math.radians(22), math.radians(-132))),
        ("RimLight",  2.4, (1.00, 0.82, 0.45), (math.radians(-42), math.radians(15), math.radians(165))),
    ]:
        ld = bpy.data.lights.new(lname, type="SUN")
        ld.energy = energy
        ld.color = col
        lo = bpy.data.objects.new(lname, ld)
        scene.collection.objects.link(lo)
        lo.rotation_euler = rot

    preview_mats = {}
    for key, (stem, rgba, rough, metal, emit_s) in MAT_DEFS.items():
        pm = bpy.data.materials.new(f"Prev_{stem}")
        pm.use_nodes = True
        nt = pm.node_tree
        bsdf = nt.nodes.get("Principled BSDF")
        dds_p = os.path.join(TEX_DIR, f"{stem}_d.dds")
        if os.path.isfile(dds_p):
            tn = nt.nodes.new("ShaderNodeTexImage")
            tn.image = bpy.data.images.load(dds_p)
            nt.links.new(tn.outputs["Color"], bsdf.inputs["Base Color"])
            if emit_s > 0.0 and "Emission Color" in bsdf.inputs:
                nt.links.new(tn.outputs["Color"], bsdf.inputs["Emission Color"])
                bsdf.inputs["Emission Strength"].default_value = emit_s * 0.45
        else:
            bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
        preview_mats[key] = pm

    for idx, (nif_fn, fn_builder) in enumerate(PREVIEW_BUILDERS):
        mm = MultiMatModel()
        fn_builder(mm)
        mm.col.bm.free()

        grp = bpy.data.objects.new(f"Grp_{idx}", None)
        scene.collection.objects.link(grp)

        min_v = Vector((1e9, 1e9, 1e9))
        max_v = Vector((-1e9, -1e9, -1e9))
        sub_objs = []
        for key, pb in mm.parts.items():
            if not pb.has_geom():
                pb.bm.free()
                continue
            md = bpy.data.meshes.new(f"PM_{idx}_{key}")
            ob = bpy.data.objects.new(f"PO_{idx}_{key}", md)
            scene.collection.objects.link(ob)
            ob.parent = grp
            ob.data.materials.append(preview_mats[key])
            pb.finish(ob)
            sub_objs.append(ob)
            for v in ob.data.vertices:
                min_v.x = min(min_v.x, v.co.x)
                min_v.y = min(min_v.y, v.co.y)
                min_v.z = min(min_v.z, v.co.z)
                max_v.x = max(max_v.x, v.co.x)
                max_v.y = max(max_v.y, v.co.y)
                max_v.z = max(max_v.z, v.co.z)

        span = max(max_v.x - min_v.x, max_v.y - min_v.y, max_v.z - min_v.z, 1.0)
        scl = 6.6 / span
        center = (min_v + max_v) * 0.5
        for ob in sub_objs:
            ob.location = (-center.x, -center.y, -min_v.z)

        col_i = idx % 4
        row_i = idx // 4  # 0..2
        grp.scale = (scl, scl, scl)
        grp.location = ((col_i - 1.5) * 11.4, (1.0 - row_i) * 13.2, 0.0)
        grp.rotation_euler = (0.0, 0.0, math.radians(-22.0))

    cam_d = bpy.data.cameras.new("QACam")
    cam_d.lens = 30.0
    cam_o = bpy.data.objects.new("QACam", cam_d)
    scene.collection.objects.link(cam_o)
    cam_o.location = (0.0, -42.5, 34.5)
    cam_o.rotation_euler = (math.radians(52.0), 0.0, 0.0)
    scene.camera = cam_o
    scene.render.filepath = PREVIEW_PNG
    bpy.ops.render.render(write_still=True)
    print(f"[Orbita7 QA Sheet Rendered] {PREVIEW_PNG}")


export_all_orbita7_models()
'''


def verify_and_fix_orbita7_nifs() -> None:
    """Verifica BSXFlags=0x82, colisión Havok bhkNPCollisionObject + bhkPhysicsSystem y rutas BGSM/DDS en los 12 NIFs."""
    for nif_fn in ORBITA7_MODEL_NAMES:
        nif_path = os.path.join(MESH_OUT_DIR, nif_fn)
        if not os.path.isfile(nif_path):
            raise RuntimeError(f"Falta NIF exportado: {nif_path}")
        with open(nif_path, "rb") as rf:
            nif = _parse_fo4_nif(rf.read())

        has_bsx = False
        has_coll = False
        has_phys = False
        changed = False

        for bi, (bt, blk) in enumerate(nif["blocks"]):
            if bt == "BSXFlags" and len(blk) >= 8:
                has_bsx = True
                if struct.unpack_from("<I", blk, 4)[0] != 0x82:
                    struct.pack_into("<I", blk, 4, 0x82)
                    changed = True
            elif bt == "bhkNPCollisionObject":
                has_coll = True
            elif bt == "bhkPhysicsSystem" and len(blk) > 64:
                has_phys = True
            elif bt == "BSLightingShaderProperty":
                s_idx = struct.unpack_from("<i", blk, 4)[0]
                bgsm_rel = nif["strings"][s_idx] if 0 <= s_idx < len(nif["strings"]) else ""
                stem = os.path.splitext(os.path.basename(bgsm_rel.replace("/", "\\")))[0]
                if stem.startswith("Orbita7"):
                    clean_bgsm = f"Materials\\AeroArmor\\Orbita7\\{stem}.BGSM"
                    new_idx = _intern_nif_string(nif["strings"], clean_bgsm)
                    if s_idx != new_idx:
                        struct.pack_into("<i", blk, 4, new_idx)
                        changed = True
                    tref = struct.unpack_from("<i", blk, 40)[0]
                    if 0 <= tref < len(nif["blocks"]) and nif["blocks"][tref][0] == "BSShaderTextureSet":
                        tex_list = [
                            f"Textures\\AeroArmor\\Orbita7\\{stem}_d.dds",
                            f"Textures\\AeroArmor\\Orbita7\\{stem}_n.dds",
                            "",
                            "",
                            "",
                            "",
                            "",
                            f"Textures\\AeroArmor\\Orbita7\\{stem}_s.dds",
                            "",
                            "",
                        ]
                        nif["blocks"][tref] = ("BSShaderTextureSet", _build_texset_bytes(tex_list))
                        changed = True

        if changed:
            with open(nif_path, "wb") as wf:
                wf.write(_serialize_fo4_nif(nif))

        assert has_bsx and has_coll and has_phys, (
            f"{nif_fn} sin colisión Havok completa (bsx={has_bsx}, coll={has_coll}, phys={has_phys})"
        )
        print(f"  [Verified Havok + PBR] {nif_fn}")


def deploy_orbita7_assets_to_fo4_data() -> None:
    """Despliega mallas, materiales y texturas de Órbita-7 en Fallout 4\\Data para pruebas locales."""
    pairs = [
        (MESH_OUT_DIR, os.path.join(FO4_DATA_DIR, "Meshes", "AeroArmor", "Orbita7")),
        (MAT_OUT_DIR,  os.path.join(FO4_DATA_DIR, "Materials", "AeroArmor", "Orbita7")),
        (TEX_OUT_DIR,  os.path.join(FO4_DATA_DIR, "Textures", "AeroArmor", "Orbita7")),
    ]
    copied = 0
    locked = []
    for src_d, dst_d in pairs:
        os.makedirs(dst_d, exist_ok=True)
        for fn in os.listdir(src_d):
            try:
                shutil.copy2(os.path.join(src_d, fn), os.path.join(dst_d, fn))
                copied += 1
            except PermissionError:
                locked.append(os.path.join(dst_d, fn))
    print(f"[Deployed to Fallout 4\\Data] {copied} archivos de Órbita-7 copiados ({len(locked)} bloqueados por proceso activo).")
    if locked:
        print("  Archivos bloqueados (se sincronizarán al cerrar Fallout 4):", locked[:6])


def generate_orbita7_english_text_textures(force: bool = False) -> None:
    """Generates English-localized `Orbita7ComicsAtlas_{d,n,s}.dds` and `Orbita7DirectorMural_{d,n,s}.dds`."""
    os.makedirs(TEX_OUT_EN_DIR, exist_ok=True)
    os.makedirs(STUDIO_ASSETS_EN_DIR, exist_ok=True)
    expected = [
        "Orbita7ComicsAtlas_d.dds",
        "Orbita7ComicsAtlas_n.dds",
        "Orbita7ComicsAtlas_s.dds",
        "Orbita7DirectorMural_d.dds",
        "Orbita7DirectorMural_n.dds",
        "Orbita7DirectorMural_s.dds",
    ]
    if not force and all(os.path.isfile(os.path.join(TEX_OUT_EN_DIR, fn)) for fn in expected):
        return

    N = 2048
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    u = xx / float(N)
    v = yy / float(N)
    fbm_macro = tileable_fbm(N, N, base_cells=8, octaves=4, persistence=0.54, seed=20770707)
    scratch, _drip = directional_scratches_and_drips(N, N, seed=20770708)

    paper_age = np.clip((fbm_macro - 0.40) * 0.42, 0.0, 0.28)[:, :, None]
    edge_vig = np.clip(np.maximum(np.abs(u - 0.5), np.abs(v - 0.5)) * 2.0 - 0.72, 0.0, 0.28) * 1.15
    age_mix = np.clip(paper_age + edge_vig[:, :, None] * 0.45, 0.0, 0.34)
    sepia_dust = np.array([118.0, 102.0, 76.0], dtype=np.float32).reshape(1, 1, 3)

    atlas_raw = _build_comics_atlas_image(lang="en")
    atlas_arr = np.asarray(atlas_raw, dtype=np.float32)
    atlas_aged = np.clip(atlas_arr * (1.0 - age_mix) + sepia_dust * age_mix, 12, 238).astype(np.uint8)
    atlas_img = Image.fromarray(atlas_aged, mode="RGB")
    atlas_img.save(os.path.join(STUDIO_ASSETS_EN_DIR, "preview_comics_atlas_en.png"))
    write_bc1_dds_from_image(os.path.join(TEX_OUT_EN_DIR, "Orbita7ComicsAtlas_d.dds"), atlas_img)
    an_r, an_g = height_to_bc5_normal(fbm_macro * 0.18 + scratch * 0.12, strength=1.0)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_EN_DIR, "Orbita7ComicsAtlas_n.dds"), an_r, an_g)
    write_bc5_dds_from_rg_arrays(
        os.path.join(TEX_OUT_EN_DIR, "Orbita7ComicsAtlas_s.dds"),
        np.clip(104.0 - age_mix[:, :, 0] * 110.0, 44, 118),
        np.clip(112.0 - age_mix[:, :, 0] * 120.0, 48, 124),
    )

    mural_raw = _build_director_mural_image(lang="en")
    mural_arr = np.asarray(mural_raw, dtype=np.float32)
    mural_aged = np.clip(mural_arr * (1.0 - age_mix) + sepia_dust * age_mix, 12, 236).astype(np.uint8)
    mural_img = Image.fromarray(mural_aged, mode="RGB")
    mural_img.save(os.path.join(STUDIO_ASSETS_EN_DIR, "preview_director_mural_en.png"))
    write_bc1_dds_from_image(os.path.join(TEX_OUT_EN_DIR, "Orbita7DirectorMural_d.dds"), mural_img)
    write_bc5_dds_from_rg_arrays(os.path.join(TEX_OUT_EN_DIR, "Orbita7DirectorMural_n.dds"), an_r, an_g)
    write_bc5_dds_from_rg_arrays(
        os.path.join(TEX_OUT_EN_DIR, "Orbita7DirectorMural_s.dds"),
        np.clip(88.0 - age_mix[:, :, 0] * 85.0, 42, 98),
        np.clip(92.0 - age_mix[:, :, 0] * 90.0, 44, 102),
    )
    print(f"[EN Textures Ready] {TEX_OUT_EN_DIR}")


def main() -> None:
    force = "--force" in sys.argv
    lang = "en" if ("--lang" in sys.argv and sys.argv[sys.argv.index("--lang") + 1] == "en") or "--lang=en" in sys.argv else "es"
    if lang == "en":
        generate_orbita7_english_text_textures(force=True if force else True)
        return

    donor_nif = extract_static_scaffold()
    generate_orbita7_textures_and_materials(force=force)

    need_blender = force or not all(os.path.isfile(os.path.join(MESH_OUT_DIR, m)) for m in ORBITA7_MODEL_NAMES)
    if need_blender or not os.path.isfile(QA_PREVIEW_PNG):
        script_src = (
            BLENDER_ORBITA7_SCRIPT
            .replace("__DONOR_NIF__", donor_nif)
            .replace("__OUT_DIR__", MESH_OUT_DIR)
            .replace("__TEX_DIR__", TEX_OUT_DIR)
            .replace("__PREVIEW_PNG__", QA_PREVIEW_PNG)
            .replace("__PYNIFLY_DIR__", PYNIFLY_DIR)
            .replace("__FORCE__", "1" if force else "0")
        )
        with tempfile.NamedTemporaryFile("w", suffix="_orbita7_blender.py", delete=False, encoding="utf-8") as tf:
            tf.write(script_src)
            tmp_py = tf.name
        try:
            proc = subprocess.run(
                [BLENDER_EXE, "--background", "--python", tmp_py],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            print(proc.stdout[-3500:])
            if proc.returncode != 0:
                print(proc.stderr[-3500:])
                raise RuntimeError(f"Blender 5.2 falló con código {proc.returncode}")
        finally:
            try:
                os.remove(tmp_py)
            except OSError:
                pass

    verify_and_fix_orbita7_nifs()
    deploy_orbita7_assets_to_fo4_data()


if __name__ == "__main__":
    main()
