#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Builder, Packager & Official Binary QA Suite for:
  Project Astro-Cosmos — Fly Over the Commonwealth (AeroArmorMod.esp v1.0.0)

Packages standalone English (`build_en/`) and Spanish (`build_es/`) builds with:
  - AeroArmorMod.esp (HEDR v1.00, Fallout4.esm master only)
  - AeroArmorMod - Main.ba2 (BTDX v1 GNRL: 1,118 files — meshes, HKX, AnimTextData, BGSM, PEX/PSC, FUZ, WAV)
  - AeroArmorMod - Textures.ba2 (BTDX v1 DX10: 90 DDS textures incl. localized EN/ES Orbita-7 art)
And produces Vortex/MO2-ready archives in `release_nexus/`:
  - ProjectAstroCosmos_EN_v1.0.0.zip
  - ProyectoAstroCosmos_ES_v1.0.0.zip

Runs full verification including:
  - ESP header + FormID asset path resolution against BA2 manifests
  - Bethesda official `Archive2.exe -extract` validation on all 4 .ba2 archives
  - Strict forbidden-extension audit inside both .zip packages
"""

from __future__ import annotations

import pathlib
import re
import shutil
import struct
import subprocess
import tempfile
import zipfile
import zlib

THIS_DIR = pathlib.Path(__file__).resolve().parent
WS_DIR = THIS_DIR.parent  # c:\proyectos_python\Mods_Fallout
RELEASE_NEXUS_DIR = THIS_DIR / "release_nexus"
ARCHIVE2_EXE = pathlib.Path(r"C:\Program Files (x86)\Steam\steamapps\common\Fallout 4\Tools\Archive2\Archive2.exe")

ZLIB_EXTS = {"nif", "bgsm", "bgem", "hkx", "txt", "ssf"}
FORBIDDEN_ZIP_EXTS = {".exe", ".dll", ".bat", ".cmd", ".ps1", ".vbs", ".scr", ".com", ".pyc"}

README_EN_TXT = """===============================================================================
PROJECT ASTRO-COSMOS — Fly Over the Commonwealth (v1.0.0 — English Standalone)
The Hubris Legacy: True 3D Free Flight, Custom 3D Suits & Studio Orbit-7 Quest
===============================================================================

1. WHAT IS THIS MOD?
---------------------
Project Astro-Cosmos (AeroArmorMod.esp) brings true 3D superhero flight and a
voiced Hubris Comics expansion into Fallout 4:

- TRUE 3D FREE-FLIGHT ENGINE (8 AERODYNAMIC REGIMES & 714 HAVOK .HKX CLIPS):
  Vertical thruster liftoff, mid-air stationary hover (custom HoverPlatform +
  zero-gravity stabilization), horizontal superhero cruise, supersonic sprint,
  controlled dive/descent, instant landing transitions, smoothed 1st-person
  camera (Track 78), and additive subgraph races (SADD) with zero vanilla
  animation conflicts.
- CUSTOM 3D PBR HERO GEAR & UNOBSTRUCTED AIRBORNE WEAPONRY:
  * Astro-Cosmos Flight Suit (100% rad shielding, articulated cape & gloves)
  * 6-Piece Astro-Cosmos Power Armor (twin sustained repulsion thrusters)
  * Astro-Cosmos Ray Carbine (6x Observatory Scope, >46 deg unobstructed dive
    fire, Cosmic Photonic Pulse: +25 AP / +15 HP on 4th hit)
  * Astro-Cosmos Orbital Gauss Cannon (8x Optics, Quadruple Solar Rail,
    Gravitational Supernova: +35 AP / +25 HP on 3rd hit)
- VOICED QUEST CAMPAIGN & PERMANENT PLAYER HOME ("UNDERGROUND STUDIO ORBIT-7"):
  Enter the secret hatch outside Hubris Comics, speak with voiced R&D Director
  Dr. Arthur 'Artie' Vance and Colonel Gutsy 'Cosmos', recover Clara Sterling's
  2077 holotapes, pass interactive terminal exams, clear combat trials at ArcJet
  and Fort Hagen, and unlock Underground Studio Orbit-7 as a permanent home with
  workbenches, safe Star Chests, and custom Captain Cosmos monuments (197 lip-
  synced .fuz dialogue lines + 60 voiced terminal clips).

2. UNIVERSAL COMPATIBILITY & REQUIREMENTS
------------------------------------------
- Base Fallout 4 ONLY (Fallout4.esm).
- ZERO Creation Club content, ZERO DLCs, ZERO F4SE, ZERO external dependencies.
- Native compatibility with BOTH Fallout 4 1.10.163 (Pre-Next-Gen / GOG) AND
  1.10.980+ (Next-Gen / Anniversary Edition): compiled with HEDR v1.00 and
  BTDX Version 1 BA2 archives (GNRL v1 & DX10 v1).

3. INSTALLATION (VORTEX / MOD ORGANIZER 2 OR MANUAL)
-----------------------------------------------------
Install via Vortex or Mod Organizer 2 (recommended), or extract all three plugin
files directly into your Fallout 4\\Data directory:
  - AeroArmorMod.esp
  - AeroArmorMod - Main.ba2
  - AeroArmorMod - Textures.ba2
Enable AeroArmorMod.esp. Travel to Hubris Comics in downtown Boston and enter
the secret hatch right outside the main entrance to begin.

4. OPEN PERMISSIONS & CREDITS (MIT LICENSE)
--------------------------------------------
Author: 0utKast (https://github.com/0utKast/fallout4-project-astro-cosmos)
Base Engine & Captain Cosmos Lore: Bethesda Game Studios (Fallout4.esm)
100% Free & Open Permissions (modification, asset use, and redistribution
allowed freely with attribution).
===============================================================================
"""

README_ES_TXT = """===============================================================================
PROYECTO ASTRO-COSMOS — Vuela sobre la Commonwealth (v1.0.0 — Español Autónomo)
El Legado de Hubris: Vuelo Libre 3D Real, Equipo 3D Propio y Estudio Órbita-7
===============================================================================

1. ¿QUÉ INCLUYE ESTA EDICIÓN AUTÓNOMA v1.0.0 EN ESPAÑOL?
--------------------------------------------------------
Proyecto Astro-Cosmos (AeroArmorMod.esp) añade un sistema real de vuelo libre en
3D y una expansión narrativa completa inspirada en el Capitán Cosmos:

- MOTOR DE VUELO LIBRE 3D REAL (8 REGÍMENES AERODINÁMICOS Y 714 CLIPS .HKX):
  Despegue vertical con propulsores, flotación estacionaria en pleno aire,
  vuelo horizontal de superhéroe, sprint supersónico, descenso controlado,
  aterrizaje instantáneo, suavizado de cámara en 1.ª persona (Track 78) y
  subgrafos aditivos SADD sin conflictos con otros mods de animación.
- 4 EQUIPOS Y ARMAS 3D PBR PROPIOS DE COMBATE AÉREO:
  * Traje de Vuelo Astro-Cosmos (inmunidad a la radiación, capa y guantes)
  * Servoarmadura Astro-Cosmos completa de 6 piezas (propulsores gemelos)
  * Carabina de Rayos Astro-Cosmos (mira aérea 6x, disparo en picado >46 grados
    sin bloqueo de cámara y Pulso Fotónico Cósmico: +25 PA / +15 Salud)
  * Cañón Gauss Orbital Astro-Cosmos (óptica 8x, acelerador solar cuádruple y
    Supernova Gravitatoria: +35 PA / +25 Salud al 3.er impacto)
- CAMPAÑA CON VOCES EN ESPAÑOL Y HOGAR PERMANENTE («ESTUDIO ÓRBITA-7»):
  Entra por la escotilla secreta frente a Hubris Comics, habla con el director
  Dr. Arthur «Artie» Vance y el Coronel Agallas «Cosmos», recupera las
  holocintas de 2077 de Clara Sterling, supera los exámenes en terminal y las
  pruebas de ArcJet y Fort Hagen, y desbloquea Órbita-7 como base permanente con
  bancos de trabajo y almacenamiento seguro (197 líneas .fuz con Lip-Sync y 60
  locuciones interactivas de terminal).

2. COMPATIBILIDAD UNIVERSAL Y REQUISITOS
-----------------------------------------
- Requiere EXCLUSIVAMENTE Fallout 4 base (Fallout4.esm).
- CERO Creation Club, CERO DLCs, CERO F4SE y CERO dependencias externas.
- Compatible nativamente con Fallout 4 1.10.163 (GOG / Pre-Next-Gen) Y con
  1.10.980+ (Next-Gen / Anniversary Edition): cabecera HEDR v1.00 y archivos
  BA2 versión 1 (GNRL v1 y DX10 v1).

3. INSTALACIÓN (VORTEX / MOD ORGANIZER 2 O MANUAL)
---------------------------------------------------
Instálalo con Vortex o Mod Organizer 2 (recomendado), o extrae estos tres
archivos dentro de tu carpeta Fallout 4\\Data:
  - AeroArmorMod.esp
  - AeroArmorMod - Main.ba2
  - AeroArmorMod - Textures.ba2
Activa AeroArmorMod.esp. Acércate a Hubris Comics en el centro de Boston y baja
por la escotilla secreta junto a la entrada para empezar.

4. PERMISOS 100% ABIERTOS Y CRÉDITOS (LICENCIA MIT)
---------------------------------------------------
Autor: 0utKast (https://github.com/0utKast/fallout4-project-astro-cosmos)
Motor Base y Lore Capitán Cosmos: Bethesda Game Studios (Fallout4.esm)
100% Gratuito y de Permisos Abiertos (modificación, uso de activos y
redistribución libres citando al autor original).
===============================================================================
"""


def _ba2_crc32(data: bytes) -> int:
    """Exact Bethesda BA2 CRC32 hash (initial CRC 0, no final XOR)."""
    crc = 0
    for b in data:
        c = (crc ^ b) & 0xFF
        for _ in range(8):
            c = (c >> 1) ^ 0xEDB88320 if (c & 1) else (c >> 1)
        crc = (crc >> 8) ^ c
    return crc


def collect_main_files(lang: str) -> dict[str, tuple[str, pathlib.Path]]:
    """Collects all 1,118 files for AeroArmorMod - Main.ba2."""
    file_map: dict[str, tuple[str, pathlib.Path]] = {}

    def add(arc_rel: str, src_path: pathlib.Path) -> None:
        norm_bs = arc_rel.replace("/", "\\").lstrip("\\")
        key = norm_bs.lower()
        assert key not in file_map, f"Duplicate Main.ba2 key: {norm_bs} ({src_path} vs {file_map[key][1]})"
        file_map[key] = (norm_bs, src_path)

    # 1. Meshes, Havok animations (.hkx), SSF, AnimTextData from workspace `meshes/` (795 files)
    meshes_root = WS_DIR / "meshes"
    for p in sorted(meshes_root.rglob("*")):
        if not p.is_file():
            continue
        if p.name.lower() == "hoverplatform_orig.nif":
            continue
        rel = p.relative_to(meshes_root)
        arc_rel = str(rel) if rel.parts[0].lower() == "meshes" else str(pathlib.Path("Meshes") / rel)
        add(arc_rel, p)

    # 2. Custom Studio Orbit-7 meshes (15 .nif)
    for p in sorted((WS_DIR / "orbita7_studio_assets" / "Meshes" / "AeroArmor" / "Orbita7").glob("*.nif")):
        add(f"Meshes\\AeroArmor\\Orbita7\\{p.name}", p)

    # 3. Materials (.bgsm) across all 5 asset groups (31 files)
    bgsm_sources = [
        (WS_DIR / "cosmos_hero_assets" / "materials" / "AeroArmor" / "Hero", "Materials\\AeroArmor\\Hero"),
        (WS_DIR / "cosmos_hero_weapon_assets" / "materials" / "AeroArmor" / "HeroWeapon", "Materials\\AeroArmor\\HeroWeapon"),
        (WS_DIR / "orbita7_studio_assets" / "Materials" / "AeroArmor" / "Orbita7", "Materials\\AeroArmor\\Orbita7"),
        (WS_DIR / "cosmos_pa_weapon_assets" / "materials" / "AeroArmor" / "PAWeapon", "Materials\\AeroArmor\\PAWeapon"),
        (WS_DIR / "cosmos_pa_assets" / "materials" / "AeroArmor" / "PowerArmor", "Materials\\AeroArmor\\PowerArmor"),
    ]
    for src_dir, arc_prefix in bgsm_sources:
        for p in sorted(src_dir.glob("*.bgsm")):
            add(f"{arc_prefix}\\{p.name}", p)

    # 4. Papyrus scripts (10 .pex + 10 .psc, top-level only)
    scripts_dir = WS_DIR / ("scripts_en" if lang == "en" else "scripts")
    for p in sorted(scripts_dir.glob("*.pex")):
        add(f"Scripts\\{p.name}", p)
    for p in sorted(scripts_dir.glob("*.psc")):
        add(f"Scripts\\Source\\User\\{p.name}", p)

    # 5. Lip-synced .fuz voices (197 files)
    voices_dir = WS_DIR / f"orbita7_voices_{lang}"
    for p in sorted(voices_dir.rglob("*.fuz")):
        rel = p.relative_to(voices_dir)
        add(f"Sound\\Voice\\AeroArmorMod.esp\\{rel}", p)

    # 6. Terminal interactive audio clips (60 .wav)
    exam_dir = WS_DIR / f"orbita7_exam_audio_{lang}"
    for p in sorted(exam_dir.glob("*.wav")):
        add(f"Sound\\FX\\AeroArmor\\Orbita7\\{p.name}", p)

    assert len(file_map) == 1118, f"Expected 1118 Main.ba2 files for {lang}, got {len(file_map)}"
    return file_map


def collect_texture_files(lang: str) -> dict[str, tuple[str, pathlib.Path]]:
    """Collects all 90 DDS textures for AeroArmorMod - Textures.ba2 (overriding EN localized textures when lang=='en')."""
    tex_map: dict[str, tuple[str, pathlib.Path]] = {}

    base_sources = [
        (WS_DIR / "cosmos_hero_assets" / "textures" / "AeroArmor" / "Hero", "Textures\\AeroArmor\\Hero"),
        (WS_DIR / "cosmos_hero_weapon_assets" / "textures" / "AeroArmor" / "HeroWeapon", "Textures\\AeroArmor\\HeroWeapon"),
        (WS_DIR / "orbita7_studio_assets" / "Textures" / "AeroArmor" / "Orbita7", "Textures\\AeroArmor\\Orbita7"),
        (WS_DIR / "cosmos_pa_weapon_assets" / "textures" / "AeroArmor" / "PAWeapon", "Textures\\AeroArmor\\PAWeapon"),
        (WS_DIR / "cosmos_pa_assets" / "textures" / "AeroArmor" / "PowerArmor", "Textures\\AeroArmor\\PowerArmor"),
    ]
    for src_dir, arc_prefix in base_sources:
        for p in sorted(src_dir.glob("*.dds")):
            norm_bs = f"{arc_prefix}\\{p.name}"
            tex_map[norm_bs.lower()] = (norm_bs, p)

    if lang == "en":
        en_override_dir = WS_DIR / "orbita7_studio_assets_en" / "Textures" / "AeroArmor" / "Orbita7"
        overrides = 0
        for p in sorted(en_override_dir.glob("*.dds")):
            norm_bs = f"Textures\\AeroArmor\\Orbita7\\{p.name}"
            assert norm_bs.lower() in tex_map, f"Unexpected EN texture override not in base set: {norm_bs}"
            tex_map[norm_bs.lower()] = (norm_bs, p)
            overrides += 1
        assert overrides == 6, f"Expected 6 EN localized texture overrides, got {overrides}"

    assert len(tex_map) == 90, f"Expected 90 Textures.ba2 files for {lang}, got {len(tex_map)}"
    return tex_map


def build_gnrl_ba2(dst_ba2: pathlib.Path, file_map: dict[str, tuple[str, pathlib.Path]]) -> tuple[int, int]:
    entries = []
    names = []
    payloads = []
    n_comp = 0

    for key in sorted(file_map.keys()):
        norm_bs, src_path = file_map[key]
        raw_bytes = src_path.read_bytes()
        dir_part, base_part = norm_bs.rsplit("\\", 1)
        stem_part, ext_part = base_part.rsplit(".", 1)
        ext_l = ext_part.lower()
        ext_bytes = ext_l.encode("ascii")[:4].ljust(4, b"\x00")
        unpacked_sz = len(raw_bytes)
        packed_sz = 0
        payload_bytes = raw_bytes

        if ext_l in ZLIB_EXTS and unpacked_sz > 32:
            comp_bytes = zlib.compress(raw_bytes, 6)
            if len(comp_bytes) < unpacked_sz:
                payload_bytes = comp_bytes
                packed_sz = len(comp_bytes)
                n_comp += 1

        entries.append([
            _ba2_crc32(stem_part.lower().encode("ascii")),
            ext_bytes,
            _ba2_crc32(dir_part.lower().encode("ascii")),
            1048832,
            0,
            packed_sz,
            unpacked_sz,
            0xBAADF00D,
        ])
        names.append(norm_bs)
        payloads.append(payload_bytes)

    cur_offset = 24 + 36 * len(entries)
    for i in range(len(entries)):
        entries[i][4] = cur_offset
        cur_offset += len(payloads[i])
    name_tbl_offset = cur_offset

    with open(dst_ba2, "wb") as wf:
        wf.write(b"BTDX")
        wf.write(struct.pack("<I4sIQ", 1, b"GNRL", len(entries), name_tbl_offset))
        for e in entries:
            wf.write(struct.pack("<I4sIIQIII", *e))
        for pl in payloads:
            wf.write(pl)
        for nm in names:
            nb = nm.encode("ascii")
            wf.write(struct.pack("<H", len(nb)) + nb)

    return len(entries), n_comp


def _parse_dds_for_dx10(arc_bs: str, dds_path: pathlib.Path) -> tuple[str, int, int, int, int, list[tuple[int, int, int, int]], bytes]:
    raw = dds_path.read_bytes()
    assert raw[:4] == b"DDS ", f"Invalid DDS magic in {dds_path}"
    h0, w0 = struct.unpack_from("<II", raw, 12)
    mips = struct.unpack_from("<I", raw, 28)[0] or 1
    fourcc = raw[84:88]

    if fourcc == b"DX10":
        dxgi_fmt = struct.unpack_from("<I", raw, 128)[0]
        payload = raw[148:]
    elif fourcc == b"DXT1":
        dxgi_fmt = 71
        payload = raw[128:]
    elif fourcc == b"DXT5":
        dxgi_fmt = 77
        payload = raw[128:]
    elif fourcc in (b"ATI2", b"BC5U"):
        dxgi_fmt = 83
        payload = raw[128:]
    else:
        raise ValueError(f"Unsupported DDS FourCC {fourcc!r} in {dds_path}")

    bpp = 16 if dxgi_fmt in (77, 78, 83, 84, 98, 99) else 8
    mip_spans: list[tuple[int, int, int]] = []
    off = 0
    mw, mh = w0, h0
    for m in range(mips):
        sz = max(1, (mw + 3) // 4) * max(1, (mh + 3) // 4) * bpp
        mip_spans.append((m, off, sz))
        off += sz
        mw = max(1, mw // 2)
        mh = max(1, mh // 2)

    assert len(payload) == off, f"DDS mip byte mismatch in {dds_path.name}: payload={len(payload)} vs expected={off}"

    cdefs: list[tuple[int, int, int, int]] = []
    tail_start: int | None = None
    tail_off = 0
    tail_sz = 0
    for m, m_off, m_sz in mip_spans:
        if m_sz >= 65536 and m < mips - 1:
            cdefs.append((m_off, m_sz, m, m))
        else:
            if tail_start is None:
                tail_start = m
                tail_off = m_off
            tail_sz += m_sz
    if tail_start is not None:
        cdefs.append((tail_off, tail_sz, tail_start, mips - 1))

    return (arc_bs, w0, h0, mips, dxgi_fmt, cdefs, payload)


def build_dx10_ba2(dst_ba2: pathlib.Path, tex_map: dict[str, tuple[str, pathlib.Path]]) -> int:
    tex_records = []
    for key in sorted(tex_map.keys()):
        arc_bs, dds_path = tex_map[key]
        tex_records.append(_parse_dds_for_dx10(arc_bs, dds_path))

    total_chunks = sum(len(r[5]) for r in tex_records)
    hdr_size = 24 + 24 * len(tex_records) + 24 * total_chunks
    cur_ofs = hdr_size
    entry_headers_and_chunks: list[bytes] = []
    payloads: list[bytes] = []
    name_bytes_list: list[bytes] = []

    for norm_bs, w0, h0, mips, dxgi_fmt, cdefs, payload in tex_records:
        dir_part, base_part = norm_bs.rsplit("\\", 1)
        stem_part = base_part.rsplit(".", 1)[0]
        comp_chunks = []
        for st_off, sz_unpk, st_mip, end_mip in cdefs:
            raw_slice = payload[st_off : st_off + sz_unpk]
            comp_slice = zlib.compress(raw_slice)
            comp_chunks.append((comp_slice, sz_unpk, st_mip, end_mip))

        tex_entry_hdr = bytearray(
            struct.pack(
                "<I4sIBBHHHBBH",
                _ba2_crc32(stem_part.lower().encode("ascii")),
                b"dds\x00",
                _ba2_crc32(dir_part.lower().encode("ascii")),
                0,
                len(comp_chunks),
                24,
                h0,
                w0,
                mips,
                dxgi_fmt,
                0x0800,
            )
        )
        for comp_slice, sz_unpk, st_mip, end_mip in comp_chunks:
            tex_entry_hdr.extend(
                struct.pack("<QIIHHI", cur_ofs, len(comp_slice), sz_unpk, st_mip, end_mip, 0xBAADF00D)
            )
            payloads.append(comp_slice)
            cur_ofs += len(comp_slice)

        entry_headers_and_chunks.append(bytes(tex_entry_hdr))
        nb = norm_bs.encode("ascii")
        name_bytes_list.append(struct.pack("<H", len(nb)) + nb)

    name_tbl_ofs = cur_ofs
    with open(dst_ba2, "wb") as wf:
        wf.write(struct.pack("<4sI4sIQ", b"BTDX", 1, b"DX10", len(tex_records), name_tbl_ofs))
        for eh in entry_headers_and_chunks:
            wf.write(eh)
        for pl in payloads:
            wf.write(pl)
        for nb in name_bytes_list:
            wf.write(nb)

    return len(tex_records)


def audit_esp_against_ba2(esp_path: pathlib.Path, main_keys: set[str], tex_keys: set[str]) -> dict:
    data = esp_path.read_bytes()
    assert data[:4] == b"TES4"
    rds = struct.unpack_from("<I", data, 4)[0]
    pos = 24
    hedr = None
    items = None
    masters = []
    while pos < 24 + rds:
        t = data[pos : pos + 4]
        sz = struct.unpack_from("<H", data, pos + 4)[0]
        sd = data[pos + 6 : pos + 6 + sz]
        if t == b"HEDR":
            hedr, items, _ = struct.unpack_from("<fII", sd, 0)
        elif t == b"MAST":
            masters.append(sd.rstrip(b"\x00").decode("utf-8"))
        pos += 6 + sz

    assert abs(hedr - 1.0) < 1e-4, f"Expected HEDR 1.0, got {hedr} in {esp_path}"
    assert masters == ["Fallout4.esm"], f"Expected ['Fallout4.esm'], got {masters}"
    assert items == 669, f"Expected 669 items, got {items}"

    # Verify all custom asset paths embedded inside the ESP exist in Main.ba2 or Textures.ba2
    pat = re.compile(rb"[A-Za-z0-9_./\\ -]{3,140}\.(?:nif|dds|bgsm|bgem|hkx|wav|xwm|fuz|ssf|pex)", re.I)
    all_ba2 = main_keys | tex_keys
    missing = []
    checked = 0
    for m in set(pat.findall(data)):
        p = m.decode("latin1").replace("/", "\\").lstrip("\\")
        low = p.lower()
        if low == "to_aeroinstant.hkx":
            # Intentional virtual $(Subgraph)\To_AeroInstant.hkx trigger in IDLE GNAM (instant subgraph refresh)
            continue
        if not any(k in low for k in ("aero", "cosmos", "orbita", "orbit", "hubris")):
            continue
        if low.startswith("data\\"):
            low = low[5:]
        if low.endswith(".nif") and not low.startswith("meshes\\"):
            low = "meshes\\" + low
        elif low.endswith(".dds") and not low.startswith("textures\\"):
            low = "textures\\" + low
        elif low.endswith(".bgsm") and not low.startswith("materials\\"):
            low = "materials\\" + low
        checked += 1
        if low not in all_ba2:
            missing.append(low)

    assert not missing, f"ESP references assets missing from BA2s: {missing}"
    return {"hedr": hedr, "items": items, "masters": masters, "custom_paths_checked": checked, "size": len(data)}


def verify_ba2_with_archive2(ba2_path: pathlib.Path, expected_kind: str, expected_count: int) -> None:
    hdr = ba2_path.read_bytes()[:24]
    magic, ver, kind, count, _ = struct.unpack_from("<4sI4sIQ", hdr, 0)
    assert magic == b"BTDX" and ver == 1, f"Bad BTDX v1 header in {ba2_path}"
    assert kind.decode("ascii") == expected_kind and count == expected_count

    assert ARCHIVE2_EXE.exists(), f"Missing official Archive2.exe at {ARCHIVE2_EXE}"
    with tempfile.TemporaryDirectory(prefix="a2_verify_") as tmpdir:
        res = subprocess.run(
            [str(ARCHIVE2_EXE), str(ba2_path), f"-extract={tmpdir}", "-quiet"],
            capture_output=True,
            text=True,
        )
        assert res.returncode == 0, f"Archive2.exe failed on {ba2_path.name}: rc={res.returncode}\n{res.stdout}\n{res.stderr}"
        extracted = [p for p in pathlib.Path(tmpdir).rglob("*") if p.is_file()]
        assert len(extracted) == expected_count, (
            f"Archive2 extracted {len(extracted)} files from {ba2_path.name}, expected {expected_count}"
        )


def build_edition(lang: str, zip_name: str, readme_filename: str, readme_body: str) -> dict:
    build_dir = THIS_DIR / f"build_{lang}"
    build_dir.mkdir(parents=True, exist_ok=True)
    RELEASE_NEXUS_DIR.mkdir(parents=True, exist_ok=True)

    src_esp = WS_DIR / f"release_{lang}" / "AeroArmorMod.esp"
    assert src_esp.exists(), f"Missing {src_esp}. Run `python update_aero_esp.py --lang {lang}` first."
    dst_esp = build_dir / "AeroArmorMod.esp"
    shutil.copy2(src_esp, dst_esp)

    main_map = collect_main_files(lang)
    tex_map = collect_texture_files(lang)

    dst_main = build_dir / "AeroArmorMod - Main.ba2"
    dst_tex = build_dir / "AeroArmorMod - Textures.ba2"
    n_main, n_comp = build_gnrl_ba2(dst_main, main_map)
    n_tex = build_dx10_ba2(dst_tex, tex_map)

    esp_info = audit_esp_against_ba2(dst_esp, set(main_map.keys()), set(tex_map.keys()))
    verify_ba2_with_archive2(dst_main, "GNRL", 1118)
    verify_ba2_with_archive2(dst_tex, "DX10", 90)

    zip_path = RELEASE_NEXUS_DIR / zip_name
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for fn in ("AeroArmorMod.esp", "AeroArmorMod - Main.ba2", "AeroArmorMod - Textures.ba2"):
            zf.write(build_dir / fn, arcname=fn)
        zf.writestr(readme_filename, readme_body)

    with zipfile.ZipFile(zip_path, "r") as vzf:
        names = vzf.namelist()
        assert set(names) == {
            "AeroArmorMod.esp",
            "AeroArmorMod - Main.ba2",
            "AeroArmorMod - Textures.ba2",
            readme_filename,
        }
        for nm in names:
            ext = "." + nm.rsplit(".", 1)[-1].lower() if "." in nm else ""
            assert ext not in FORBIDDEN_ZIP_EXTS, f"Forbidden extension {ext} in {nm}"

    stats = {
        "lang": lang.upper(),
        "zip_path": zip_path,
        "zip_mb": round(zip_path.stat().st_size / (1024 * 1024), 2),
        "esp_mb": round(dst_esp.stat().st_size / (1024 * 1024), 2),
        "main_ba2_mb": round(dst_main.stat().st_size / (1024 * 1024), 2),
        "main_files": n_main,
        "main_zlib_compressed": n_comp,
        "tex_ba2_mb": round(dst_tex.stat().st_size / (1024 * 1024), 2),
        "tex_files": n_tex,
        "esp_info": esp_info,
    }
    print(
        f"[{stats['lang']} OK] {zip_path.name} ({stats['zip_mb']:.2f} MB) | "
        f"Main.ba2={stats['main_ba2_mb']:.2f} MB ({n_main} files, {n_comp} zlib) | "
        f"Textures.ba2={stats['tex_ba2_mb']:.2f} MB ({n_tex} DDS) | "
        f"Archive2.exe extract=PASS | ESP HEDR={esp_info['hedr']:.2f} ({esp_info['custom_paths_checked']} paths verified)"
    )
    return stats


def main() -> None:
    print("=== Packaging Project Astro-Cosmos v1.0.0 (EN & ES Standalone Editions) ===\n")
    build_edition("en", "ProjectAstroCosmos_EN_v1.0.0.zip", "README_EN.txt", README_EN_TXT)
    build_edition("es", "ProyectoAstroCosmos_ES_v1.0.0.zip", "LEEME_ES.txt", README_ES_TXT)
    print(f"\n[DONE] Both Nexus/GitHub archives ready in: {RELEASE_NEXUS_DIR}")


if __name__ == "__main__":
    main()
