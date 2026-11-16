#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_aero_esp.py
==================
Actualiza `AeroArmorMod.esp` (manteniendo HEDR v0.95 para compatibilidad
universal 1.10.163 + Next-Gen/AE) añadiendo:
  1. GRUP KYWD:
     - 0x01000812: AeroArmor_FlightArchetypeKw  (TNAM = 7 AnimArchetype)
     - 0x01000813: AeroArmor_DescentArchetypeKw (TNAM = 7 AnimArchetype)
     - 0x01000816: AeroArmor_FlightFlavorKw     (TNAM = 13 AnimFlavor)
     - 0x01000817: AeroArmor_DescentFlavorKw    (TNAM = 13 AnimFlavor)
  2. GRUP RACE (Additive Subgraph Races vía SADD, cero conflictos con otros mods):
     - 0x01000814: AeroArmor_HumanSubGraphAdditive (SADD -> 0x00166729 HumanRaceSubGraphData)
     - 0x01000815: AeroArmor_PowerArmorSubGraphAdditive (SADD -> 0x0001D31E PowerArmorRace)
"""

import argparse
import os
import shutil
import struct

from build_hubris_orbita7_quest import build_orbita7_esp_grups, count_esp_items

FO4_DATA_DIR = r"C:\Program Files (x86)\Steam\steamapps\common\Fallout 4\Data"
FO4_ESM_PATH = os.path.join(FO4_DATA_DIR, "Fallout4.esm")
WORKSPACE_ESP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "AeroArmorMod.esp")
DATA_ESP = os.path.join(FO4_DATA_DIR, "AeroArmorMod.esp")

# FormIDs de Fallout4.esm
FID_HUMAN_SUBGRAPH_RACE = 0x00166729
FID_POWER_ARMOR_RACE = 0x0001D31E
FID_ANIM_ARCHETYPE_PLAYER = 0x0006B508
FID_FEMALE_KW = 0x00084486
FID_ANIM_FLAVOR_MILITARY = 0x0015F755
FID_ANIM_FLAVOR_BOMB_REACTION = 0x00160496
FID_ANIM_FLAVOR_BOMB_BABY = 0x00178A65

# Nuevos FormIDs en AeroArmorMod.esp
FID_HERO_SUIT_ARMO = 0x01000800
FID_FLIGHT_RING_ARMO = 0x01000801
FID_FLIGHT_ENCH = 0x01000802
FID_COBJ_SUIT = 0x01000805
FID_FLIGHT_ARCH_KW = 0x01000812
FID_DESCENT_ARCH_KW = 0x01000813
FID_HUMAN_ADD_RACE = 0x01000814
FID_PA_ADD_RACE = 0x01000815
FID_FLIGHT_FLAV_KW = 0x01000816
FID_DESCENT_FLAV_KW = 0x01000817
FID_HERO_SUIT_AA = 0x01000818
FID_HERO_GLOVES_AA = 0x01000819
FID_COSMIC_RAD_MGEF = 0x0100081A
FID_COSMIC_RAD_PERK = 0x0100081B

# Nuevos FormIDs de la Servoarmadura Astro-Cosmos (6 piezas + 6 OMODs + 6 COBJs + Keyword Torso)
FID_COSMOS_PA_TORSO_KW = 0x0100081F
FID_COSMOS_PA_TORSO = 0x01000820
FID_COSMOS_PA_HELM = 0x01000821
FID_COSMOS_PA_LARM = 0x01000822
FID_COSMOS_PA_RARM = 0x01000823
FID_COSMOS_PA_LLEG = 0x01000824
FID_COSMOS_PA_RLEG = 0x01000825

FID_OMOD_PA_TORSO = 0x01000826
FID_OMOD_PA_HELM = 0x01000827
FID_OMOD_PA_LARM = 0x01000828
FID_OMOD_PA_RARM = 0x01000829
FID_OMOD_PA_LLEG = 0x0100082A
FID_OMOD_PA_RLEG = 0x0100082B

FID_COBJ_PA_TORSO = 0x0100082C
FID_COBJ_PA_HELM = 0x0100082D
FID_COBJ_PA_LARM = 0x0100082E
FID_COBJ_PA_RARM = 0x0100082F
FID_COBJ_PA_LLEG = 0x01000830
FID_COBJ_PA_RLEG = 0x01000831

# Nuevos FormIDs de la Carabina de Rayos Astro-Cosmos (Arma Aérea Exclusiva del Traje de Superhéroe)
FID_COSMOS_HERO_WEAP = 0x01000840
FID_OMOD_HERO_RECEIVER = 0x01000841
FID_OMOD_HERO_BARREL = 0x01000842
FID_OMOD_HERO_STOCK = 0x01000843
FID_OMOD_HERO_SCOPE = 0x01000844
FID_OMOD_HERO_FOCUSER = 0x01000845
FID_COSMOS_SCOPE_ZOOM = 0x01000846
FID_COSMOS_HERO_WEAP_KW = 0x01000847
FID_COSMOS_CARBINE_ENCH = 0x01000848
FID_COSMOS_CARBINE_MGEF = 0x01000849
FID_COBJ_HERO_WEAP = 0x0100084A
FID_MA_COSMOS_CARBINE_KW = 0x0100084B
FID_COSMOS_WEAP_TRNS = 0x0100084C
FID_COSMOS_HERO_AMDL = 0x0100084D

FID_ESM_WEAP_LASERGUN = 0x0009983B
FID_ESM_OMOD_LG_REC = 0x001877F9
FID_ESM_OMOD_LG_BAR = 0x00091FB5
FID_ESM_OMOD_LG_STK = 0x001877ED
FID_ESM_OMOD_LG_SCP = 0x00187802
FID_ESM_OMOD_LG_FOC = 0x001877EF
FID_ESM_MGEF_SHOCK = 0x000856FC
FID_ESM_MA_LASERGUN = 0x000D1052

# Nuevos FormIDs del Cañón Orbital Gauss Astro-Cosmos (Arma Aérea Pesada Exclusiva de Servoarmadura)
FID_COSMOS_PA_WEAP = 0x01000850
FID_OMOD_PA_WEAP_BARREL = 0x01000851
FID_OMOD_PA_WEAP_MAG = 0x01000852
FID_OMOD_PA_WEAP_STOCK = 0x01000853
FID_OMOD_PA_WEAP_SCOPE = 0x01000854
FID_OMOD_PA_WEAP_MUZZLE = 0x01000855
FID_COSMOS_PA_SCOPE_ZOOM = 0x01000856
FID_COSMOS_PA_WEAP_KW = 0x01000857
FID_COSMOS_PA_CANNON_ENCH = 0x01000858
FID_COSMOS_PA_CANNON_MGEF = 0x01000859
FID_COBJ_PA_WEAP = 0x0100085A
FID_MA_COSMOS_PA_CANNON_KW = 0x0100085B
FID_COSMOS_PA_WEAP_TRNS = 0x0100085C
FID_COSMOS_PA_AMDL = 0x0100085D

FID_ESM_WEAP_GAUSSRIFLE = 0x000D1EB0
FID_ESM_OMOD_GR_BAR = 0x00179B52
FID_ESM_OMOD_GR_MAG = 0x001AC252
FID_ESM_OMOD_GR_STK = 0x00179B4F
FID_ESM_OMOD_GR_SCP = 0x001C34A6
FID_ESM_OMOD_GR_MUZ = 0x00179B50
FID_ESM_MA_GAUSSRIFLE = 0x001889EC

# Plantillas vanilla en Fallout4.esm para ARMA / ARMO del Traje y Servoarmadura Astro-Cosmos
FID_ESM_ARMA_SYNTH_UNIFORM = 0x0012B91C
FID_ESM_ARMA_BOS_GLOVES = 0x0020DCDA
FID_ESM_ARMO_BOS_BLACK = 0x00134294

FID_ESM_PA_T51_TORSO = 0x00140C51
FID_ESM_PA_T51_HELM = 0x00140C4E
FID_ESM_PA_T51_LARM = 0x00140C4C
FID_ESM_PA_T51_RARM = 0x00140C4D
FID_ESM_PA_T51_LLEG = 0x00140C4F
FID_ESM_PA_T51_RLEG = 0x00140C50

FID_ESM_OMOD_T51_TORSO = 0x001739BC
FID_ESM_OMOD_T51_HELM = 0x001739BD
FID_ESM_OMOD_T51_LARM = 0x001739BE
FID_ESM_OMOD_T51_RARM = 0x001739C0
FID_ESM_OMOD_T51_LLEG = 0x001739BF
FID_ESM_OMOD_T51_RLEG = 0x001739C1


def subrec(tag: bytes, payload: bytes) -> bytes:
    return struct.pack("<4sH", tag, len(payload)) + payload


def subrec_cstr(tag: bytes, text: str) -> bytes:
    return subrec(tag, text.encode("utf-8") + b"\x00")


def _loc(lang: str, es_txt: str, en_txt: str) -> str:
    """Devuelve `en_txt` cuando `lang == 'en'` o `es_txt` en caso contrario."""
    return en_txt if lang == "en" else es_txt


def _rewrite_record_cstrs(rec_bytes: bytes, updates: dict[bytes, str]) -> bytes:
    """Reescribe subregistros C-string de un registro binario manteniendo su cabecera intacta."""
    rec_type, rds, flags, fid, vc1, fver, v2 = struct.unpack_from("<4sIIIIHH", rec_bytes, 0)
    body = rec_bytes[24 : 24 + rds]
    out_body = bytearray()
    sp = 0
    while sp + 6 <= len(body):
        tag = body[sp : sp + 4]
        sz = struct.unpack_from("<H", body, sp + 4)[0]
        if tag in updates:
            out_body += subrec_cstr(tag, updates[tag])
        else:
            out_body += body[sp : sp + 6 + sz]
        sp += 6 + sz
    return struct.pack("<4sIIIIHH", rec_type, len(out_body), flags, fid, vc1, fver, v2) + bytes(out_body)


def make_record(rec_type: bytes, form_id: int, body: bytes, flags: int = 0) -> bytes:
    # VC1 = 0x000037B4 (standard FO4), FormVersion = 131 (0x0083), VC2 = 0
    return struct.pack("<4sIIIIHH", rec_type, len(body), flags, form_id, 0x000037B4, 131, 0) + body


def make_grup(label: bytes, records_bytes: bytes) -> bytes:
    return struct.pack("<4sI4sIII", b"GRUP", 24 + len(records_bytes), label, 0, 0, 0) + records_bytes


def make_kywd_record(form_id: int, edid: str, tnam_type: int) -> bytes:
    body = (
        subrec_cstr(b"EDID", edid)
        + subrec(b"CNAM", bytes.fromhex("ffffff00"))
        + subrec(b"TNAM", struct.pack("<I", tnam_type))
    )
    return make_record(b"KYWD", form_id, body)


def build_simple_vmad(script_name: str) -> bytes:
    sname = script_name.encode("ascii")
    return struct.pack("<HHHH", 6, 2, 1, len(sname)) + sname + struct.pack("<BH", 0, 0)


def build_subgraph_block(
    sakd_list: list,
    stkd_list: list,
    sgnm: str,
    sapt_list: list,
    sraf_bytes: bytes,
) -> bytes:
    out = bytearray()
    for kw in sakd_list:
        out += subrec(b"SAKD", struct.pack("<I", kw))
    for kw in stkd_list:
        out += subrec(b"STKD", struct.pack("<I", kw))
    out += subrec_cstr(b"SGNM", sgnm)
    for pt in sapt_list:
        out += subrec_cstr(b"SAPT", pt)
    out += subrec(b"SRAF", sraf_bytes)
    return bytes(out)


def extract_weapon_blocks_from_esm() -> tuple:
    """Extrae los bloques de armas (SRAF=1) de HumanRaceSubGraphData y PowerArmorRace."""
    with open(FO4_ESM_PATH, "rb") as f:
        data = f.read()

    human_w_blocks = []
    pa_w_blocks = []
    inj = {0x00030B00, 0x00030B01, 0x000345AD, 0x000345AE}

    pos = 0
    while pos < len(data):
        rt, ds = data[pos : pos + 4], struct.unpack_from("<I", data, pos + 4)[0]
        if rt == b"GRUP" and data[pos + 8 : pos + 12] == b"RACE":
            p = pos + 24
            while p < pos + ds:
                _, rds, fl, fid, _, _ = struct.unpack_from("<4sIIIII", data, p)
                if fid in (FID_HUMAN_SUBGRAPH_RACE, FID_POWER_ARMOR_RACE):
                    rb = data[p + 24 : p + 24 + rds]
                    sp = 0
                    cur = []
                    while sp < len(rb):
                        st, sz = rb[sp : sp + 4], struct.unpack_from("<H", rb, sp + 4)[0]
                        val = rb[sp + 6 : sp + 6 + sz]
                        sp += 6 + sz
                        if st in (b"SAKD", b"STKD", b"SGNM", b"SAPT", b"SRAF", b"SPED"):
                            cur.append((st, val))
                            if st == b"SRAF":
                                if val == b"\x01\x00\x00\x00":
                                    sakds = [struct.unpack("<I", v)[0] for k, v in cur if k == b"SAKD"]
                                    stkds = [struct.unpack("<I", v)[0] for k, v in cur if k == b"STKD"]
                                    sgnm = next(
                                        v[:-1].decode("latin1") for k, v in cur if k == b"SGNM"
                                    )
                                    sapts = [
                                        v[:-1].decode("latin1") for k, v in cur if k == b"SAPT"
                                    ]
                                    if fid == FID_HUMAN_SUBGRAPH_RACE:
                                        if FID_ANIM_ARCHETYPE_PLAYER in sakds and not any(
                                            x in inj for x in sakds
                                        ):
                                            human_w_blocks.append((sakds, stkds, sgnm, sapts))
                                    else:
                                        pa_w_blocks.append((sakds, stkds, sgnm, sapts))
                                cur = []
                p += 24 + rds
            break
        pos += ds if rt == b"GRUP" else (24 + ds)

    return human_w_blocks, pa_w_blocks


def build_minimal_race_prefix(edid: str, sadd_target_fid: int) -> bytes:
    """Construye el prefijo mínimo oficial de un RACE Additive Subgraph no localizado (FormVersion=131)."""
    if sadd_target_fid == FID_POWER_ARMOR_RACE:
        skel_path = r"actors\PowerArmor\CharacterAssets\skeleton.nif"
        proj_path = r"Actors\PowerArmor\PowerArmorProject.hkx"
    else:
        skel_path = r"actors\Character\CharacterAssets\skeleton.nif"
        proj_path = r"actors\Character\RaiderProject.hkx"
    modt_20 = bytes.fromhex("04000000" + "00" * 16)

    out = bytearray()
    out += subrec_cstr(b"EDID", edid)
    out += subrec_cstr(b"DESC", "")
    out += subrec(b"BOD2", bytes.fromhex("00000000"))
    out += subrec(
        b"PRPS",
        bytes.fromhex(
            "c202000000000000c302000000000000c402000000000000c502000000000000"
            "c602000000000000c702000000000000c802000000000000d402000000004842"
            "d502000000004842e00200000000803fdc02000000000000d702000000000000"
            "d902000000000000d802000000000000"
        ),
    )
    out += subrec(
        b"DATA",
        bytes.fromhex(
            "0000803f0000803fabaaaa3eabaaaa3eabaaaa3eabaaaa3eabaaaa3eabaaaa3e"
            "000000000000803f0000803f01000000ffffffffffffffff00000000ffffffff"
            "ffffffffffffffff00000000000000000000803e0000a0400000000000000000"
            "000000000000000000000000000000000000000000000000000096c300000000"
            "ffffffff00000000000000000000000000000000000000000000000000000000"
            "0000000000000000000000000000000000000000000000000000000000000000"
            "0000b4420000b442"
        ),
    )
    out += subrec(b"MNAM", b"")
    out += subrec_cstr(b"ANAM", skel_path)
    out += subrec(b"MODT", modt_20)
    out += subrec(b"FNAM", b"")
    out += subrec_cstr(b"ANAM", skel_path)
    out += subrec(b"MODT", modt_20)
    for mtnm in (b"WALK", b"RUN1", b"SNEK", b"BLDO", b"SWIM"):
        out += subrec(b"MTNM", mtnm)
    out += subrec(b"VTCK", bytes.fromhex("2d0000002e000000"))
    out += subrec(b"PNAM", bytes.fromhex("0000a040"))
    out += subrec(b"UNAM", bytes.fromhex("00004040"))
    out += subrec(b"NAM1", b"")
    out += subrec(b"MNAM", b"")
    out += subrec(b"INDX", bytes.fromhex("00000000"))
    out += subrec(b"FNAM", b"")
    out += subrec(b"INDX", bytes.fromhex("00000000"))
    out += subrec(b"GNAM", bytes.fromhex("1d000000"))
    out += subrec(b"NAM3", b"")
    out += subrec(b"MNAM", b"")
    out += subrec_cstr(b"MODL", proj_path)
    out += subrec(b"MODT", modt_20)
    out += subrec(b"FNAM", b"")
    out += subrec_cstr(b"MODL", proj_path)
    out += subrec(b"MODT", modt_20)
    for _ in range(32):
        out += subrec(b"NAME", b"\x00")
    out += subrec(b"RBPC", b"\x00" * 128)
    out += subrec(b"VNAM", bytes.fromhex("ffffffff"))
    out += subrec(b"SADD", struct.pack("<I", sadd_target_fid))
    return bytes(out)


def build_custom_human_mt_blocks() -> bytes:
    """Construye los bloques MTBehavior (3ª y 1ª persona) con hashes verificados en AnimationFileData."""
    body = bytearray()

    # SAPT lists cuyos hashes de 64 bits existen en AnimTextData\AnimationFileData:
    # - 9591542742431070157.txt -> AeroFlight (4 elementos exactos de blk=45)
    # - 18105890810579154893.txt -> AeroDescent (4 elementos exactos de blk=39)
    flight_sapts = [
        r"Actors\Character\Animations\MT\Neutral\Female\BombReactionBaby",
        r"Actors\Character\Animations\MT\Neutral\BombReaction",
        r"Actors\Character\Animations\MT\Neutral",
        r"Actors\Character\Animations",
    ]
    descent_sapts = [
        r"Actors\Character\Animations\MT\Neutral\BombReaction",
        r"Actors\Character\Animations\MT\Neutral\Female",
        r"Actors\Character\Animations\MT\Neutral",
        r"Actors\Character\Animations",
    ]
    fp_sapts = [
        r"Actors\Character\_1stPerson\Animations\Paired",
        r"Actors\Character\_1stPerson\Animations\Furniture\Water",
        r"Actors\Character\_1stPerson\Animations\Loose",
        r"Actors\Character\_1stPerson\Animations\Common",
        r"actors\Character\_1stPerson\Animations\Rifle",
    ]

    for arch_kw, flav_kw, vanilla_flav_kw, target_sapts in [
        (FID_FLIGHT_ARCH_KW, FID_FLIGHT_FLAV_KW, FID_ANIM_FLAVOR_BOMB_BABY, flight_sapts),
        (FID_DESCENT_ARCH_KW, FID_DESCENT_FLAV_KW, FID_ANIM_FLAVOR_BOMB_REACTION, descent_sapts),
    ]:
        for kw_combo_m, kw_combo_f in [
            ([FID_ANIM_ARCHETYPE_PLAYER, arch_kw, flav_kw], [FID_ANIM_ARCHETYPE_PLAYER, FID_FEMALE_KW, arch_kw, flav_kw]),
            ([FID_ANIM_ARCHETYPE_PLAYER, vanilla_flav_kw], [FID_ANIM_ARCHETYPE_PLAYER, FID_FEMALE_KW, vanilla_flav_kw]),
            ([FID_ANIM_ARCHETYPE_PLAYER, flav_kw], [FID_ANIM_ARCHETYPE_PLAYER, FID_FEMALE_KW, flav_kw]),
            ([arch_kw, flav_kw], [arch_kw, FID_FEMALE_KW, flav_kw]),
            ([arch_kw, vanilla_flav_kw], [arch_kw, FID_FEMALE_KW, vanilla_flav_kw]),
            ([arch_kw], [arch_kw, FID_FEMALE_KW]),
            ([flav_kw], [flav_kw, FID_FEMALE_KW]),
            ([vanilla_flav_kw], [vanilla_flav_kw, FID_FEMALE_KW]),
        ]:
            body += build_subgraph_block(
                kw_combo_f,
                [],
                r"Actors\Character\Behaviors\MTBehavior.hkx",
                target_sapts,
                b"\x00\x00\x00\x00",
            )
            body += build_subgraph_block(
                kw_combo_m,
                [],
                r"Actors\Character\Behaviors\MTBehavior.hkx",
                target_sapts,
                b"\x00\x00\x00\x00",
            )

    return bytes(body)


def build_custom_human_aerial_carbine_blocks() -> bytes:
    """
    Construye los bloques WeaponBehavior.hkx (SRAF=1) exclusivos para cuando el jugador
    está en vuelo (BombReactionBaby / BombReaction / FlightFlavorKw) empuñando la
    Carabina de Rayos Astro-Cosmos (STKD incluye FID_COSMOS_HERO_WEAP_KW).
    Resuelve al hash vanilla 8443591340*.txt (LaserRifleGripStraight\\Player\\AeroSky),
    manteniendo las piernas flotando en postura heroica mientras el tren superior apunta,
    dispara por la mira 6x y recarga con normalidad. En tierra no coincide y usa 1506835060*.txt.
    """
    body = bytearray()
    aerial_carbine_sapts = [
        r"Actors\Character\Animations\Weapon\LaserRifleGripStraight\Player",
        r"Actors\Character\Animations\Weapon\LaserRifleGripStraight",
        r"Actors\Character\Animations\Weapon\Rifle\Neutral",
        r"Actors\Character\Animations\Weapon\GripRifleStraight\Injured\Left",
        r"Actors\Character\Animations\Paired",
        r"Actors\Character\Animations\Player",
        r"Actors\Character\Animations",
    ]
    stkd_carbine = [0x000464EF, 0x00099830, FID_COSMOS_HERO_WEAP_KW]

    for sakd_combo in [
        [FID_ANIM_ARCHETYPE_PLAYER, FID_FEMALE_KW, FID_ANIM_FLAVOR_BOMB_BABY],
        [FID_ANIM_ARCHETYPE_PLAYER, FID_ANIM_FLAVOR_BOMB_BABY],
        [FID_ANIM_ARCHETYPE_PLAYER, FID_FEMALE_KW, FID_ANIM_FLAVOR_BOMB_REACTION],
        [FID_ANIM_ARCHETYPE_PLAYER, FID_ANIM_FLAVOR_BOMB_REACTION],
        [FID_ANIM_ARCHETYPE_PLAYER, FID_FEMALE_KW, FID_FLIGHT_FLAV_KW],
        [FID_ANIM_ARCHETYPE_PLAYER, FID_FLIGHT_FLAV_KW],
        [FID_ANIM_ARCHETYPE_PLAYER, FID_FEMALE_KW, FID_DESCENT_FLAV_KW],
        [FID_ANIM_ARCHETYPE_PLAYER, FID_DESCENT_FLAV_KW],
        [FID_FLIGHT_ARCH_KW, FID_FEMALE_KW, FID_FLIGHT_FLAV_KW],
        [FID_FLIGHT_ARCH_KW, FID_FLIGHT_FLAV_KW],
        [FID_ANIM_FLAVOR_BOMB_BABY, FID_FEMALE_KW],
        [FID_ANIM_FLAVOR_BOMB_BABY],
        [FID_ANIM_FLAVOR_BOMB_REACTION, FID_FEMALE_KW],
        [FID_ANIM_FLAVOR_BOMB_REACTION],
    ]:
        body += build_subgraph_block(
            sakd_combo,
            stkd_carbine,
            r"Actors\Character\Behaviors\WeaponBehavior.hkx",
            aerial_carbine_sapts,
            b"\x01\x00\x00\x00",
        )
    return bytes(body)


def build_custom_human_aerial_cannon_blocks() -> bytes:
    """
    Construye los bloques WeaponBehavior.hkx (SRAF=1) exclusivos para cuando el jugador
    está en vuelo (BombReactionBaby / BombReaction / FlightFlavorKw) empuñando el
    Cañón Orbital Gauss Astro-Cosmos (STKD incluye FID_COSMOS_PA_WEAP_KW).
    Resuelve al hash vanilla 13275926613*.txt (GaussRifle\\Player\\AeroSky),
    permitiendo usar el Cañón Orbital en vuelo tanto con el Traje de Vuelo como con Servoarmadura.
    """
    body = bytearray()
    aerial_human_cannon_sapts = [
        r"Actors\Character\Animations\Weapon\GaussRifle\Player",
        r"Actors\Character\Animations\Weapon\GaussRifle",
        r"Actors\Character\Animations\Weapon\Rifle\Injured\Left",
        r"Actors\Character\Animations\Paired",
        r"Actors\Character\Animations\Player",
        r"Actors\Character\Animations",
    ]
    stkd_cannon = [0x000D1EB1, 0x0001F947, FID_COSMOS_PA_WEAP_KW]

    for sakd_combo in [
        [FID_ANIM_ARCHETYPE_PLAYER, FID_FEMALE_KW, FID_ANIM_FLAVOR_BOMB_BABY],
        [FID_ANIM_ARCHETYPE_PLAYER, FID_ANIM_FLAVOR_BOMB_BABY],
        [FID_ANIM_ARCHETYPE_PLAYER, FID_FEMALE_KW, FID_ANIM_FLAVOR_BOMB_REACTION],
        [FID_ANIM_ARCHETYPE_PLAYER, FID_ANIM_FLAVOR_BOMB_REACTION],
        [FID_ANIM_ARCHETYPE_PLAYER, FID_FEMALE_KW, FID_FLIGHT_FLAV_KW],
        [FID_ANIM_ARCHETYPE_PLAYER, FID_FLIGHT_FLAV_KW],
        [FID_ANIM_ARCHETYPE_PLAYER, FID_FEMALE_KW, FID_DESCENT_FLAV_KW],
        [FID_ANIM_ARCHETYPE_PLAYER, FID_DESCENT_FLAV_KW],
        [FID_FLIGHT_ARCH_KW, FID_FEMALE_KW, FID_FLIGHT_FLAV_KW],
        [FID_FLIGHT_ARCH_KW, FID_FLIGHT_FLAV_KW],
        [FID_ANIM_FLAVOR_BOMB_BABY, FID_FEMALE_KW],
        [FID_ANIM_FLAVOR_BOMB_BABY],
        [FID_ANIM_FLAVOR_BOMB_REACTION, FID_FEMALE_KW],
        [FID_ANIM_FLAVOR_BOMB_REACTION],
    ]:
        body += build_subgraph_block(
            sakd_combo,
            stkd_cannon,
            r"Actors\Character\Behaviors\WeaponBehavior.hkx",
            aerial_human_cannon_sapts,
            b"\x01\x00\x00\x00",
        )
    return bytes(body)


def build_custom_pa_mt_blocks() -> bytes:
    """Construye los bloques MTBehavior 3ª persona para Servoarmadura (Vuelo 6102835159731828685.txt y Tierra 14810735168864942029.txt)."""
    body = bytearray()
    pa_flight_sapts = [
        r"Actors\PowerArmor\Animations\MT\Neutral\Military",
        r"Actors\PowerArmor\Animations\MT",
        r"Actors\PowerArmor\Animations\Paired",
    ]
    pa_ground_sapts = [
        r"Actors\PowerArmor\Animations\Deaths",
        r"Actors\PowerArmor\Animations\MT\Sneak",
        r"Actors\PowerArmor\Animations\MT",
        r"Actors\PowerArmor\Animations\Paired",
    ]

    for kw_combo in [
        [FID_ANIM_ARCHETYPE_PLAYER, FID_ANIM_FLAVOR_MILITARY, FID_FEMALE_KW],
        [FID_ANIM_ARCHETYPE_PLAYER, FID_ANIM_FLAVOR_MILITARY],
        [FID_ANIM_FLAVOR_MILITARY, FID_FEMALE_KW],
        [FID_ANIM_FLAVOR_MILITARY],
        [FID_FLIGHT_ARCH_KW, FID_FLIGHT_FLAV_KW, FID_FEMALE_KW],
        [FID_FLIGHT_ARCH_KW, FID_FLIGHT_FLAV_KW],
        [FID_FLIGHT_FLAV_KW, FID_FEMALE_KW],
        [FID_FLIGHT_FLAV_KW],
    ]:
        body += build_subgraph_block(
            kw_combo,
            [],
            r"Actors\Character\Behaviors\MTBehavior.hkx",
            pa_flight_sapts,
            b"\x00\x00\x00\x00",
        )

    for ground_combo in [
        [FID_ANIM_ARCHETYPE_PLAYER, FID_DESCENT_FLAV_KW, FID_FEMALE_KW],
        [FID_ANIM_ARCHETYPE_PLAYER, FID_DESCENT_FLAV_KW],
        [FID_DESCENT_FLAV_KW, FID_FEMALE_KW],
        [FID_DESCENT_FLAV_KW],
    ]:
        body += build_subgraph_block(
            ground_combo,
            [],
            r"Actors\Character\Behaviors\MTBehavior.hkx",
            pa_ground_sapts,
            b"\x00\x00\x00\x00",
        )
    return bytes(body)


def build_human_additive_race(human_w_blocks: list) -> bytes:
    body = bytearray(build_minimal_race_prefix("AeroArmor_HumanSubGraphAdditive", FID_HUMAN_SUBGRAPH_RACE))
    body += build_custom_human_mt_blocks()
    body += build_custom_human_aerial_carbine_blocks()
    body += build_custom_human_aerial_cannon_blocks()

    for arch_kw, flav_kw in [
        (FID_FLIGHT_ARCH_KW, FID_FLIGHT_FLAV_KW),
        (FID_DESCENT_ARCH_KW, FID_DESCENT_FLAV_KW),
    ]:
        for sakds, stkds, sgnm, sapts in human_w_blocks:
            new_sakds_arch = [arch_kw if k == FID_ANIM_ARCHETYPE_PLAYER else k for k in sakds]
            body += build_subgraph_block(
                new_sakds_arch,
                stkds,
                sgnm,
                sapts,
                b"\x01\x00\x00\x00",
            )
            new_sakds_both = new_sakds_arch + [flav_kw]
            body += build_subgraph_block(
                new_sakds_both,
                stkds,
                sgnm,
                sapts,
                b"\x01\x00\x00\x00",
            )

    return make_record(b"RACE", FID_HUMAN_ADD_RACE, bytes(body))


def build_custom_pa_aerial_cannon_blocks() -> bytes:
    """
    Construye los bloques WeaponBehavior.hkx (SRAF=1) exclusivos para cuando el jugador
    está en vuelo en Servoarmadura (AnimFlavorMilitary / FlightFlavorKw) empuñando el
    Cañón Orbital Gauss Astro-Cosmos (STKD incluye FID_COSMOS_PA_WEAP_KW).
    Resuelve al hash 18249293482037677982.txt (sincronizado con RifleBoltChargeState_SM
    y CosmosPACannon\\AeroSky), manteniendo las piernas acorazadas en estela aerodinámica
    mientras el tren superior apunta, carga el proyectil electromagnético, usa la mira 8x
    y recarga con normalidad. Al aterrizar (DescentFlavorKw o None) vuelve al instante al
    subgrafo nativo de tierra de GaussRifle (15964126763214507934.txt).
    """
    body = bytearray()
    aerial_pa_cannon_sapts = [
        r"Actors\PowerArmor\Animations\Grips\RifleStraight",
        r"Actors\PowerArmor\Animations\Grips\Rifle",
        r"Actors\PowerArmor\Animations\Paired",
    ]
    stkd_pa_cannon = [0x000D1EB1, 0x0001F947, FID_COSMOS_PA_WEAP_KW]

    for sakd_combo in [
        [FID_ANIM_ARCHETYPE_PLAYER, FID_ANIM_FLAVOR_MILITARY, FID_FEMALE_KW],
        [FID_ANIM_ARCHETYPE_PLAYER, FID_ANIM_FLAVOR_MILITARY],
        [FID_ANIM_FLAVOR_MILITARY, FID_FEMALE_KW],
        [FID_ANIM_FLAVOR_MILITARY],
        [FID_FLIGHT_ARCH_KW, FID_FLIGHT_FLAV_KW, FID_FEMALE_KW],
        [FID_FLIGHT_ARCH_KW, FID_FLIGHT_FLAV_KW],
        [FID_FLIGHT_FLAV_KW, FID_FEMALE_KW],
        [FID_FLIGHT_FLAV_KW],
    ]:
        body += build_subgraph_block(
            sakd_combo,
            stkd_pa_cannon,
            r"Actors\Character\Behaviors\WeaponBehavior.hkx",
            aerial_pa_cannon_sapts,
            b"\x01\x00\x00\x00",
        )
    return bytes(body)


def build_custom_pa_aerial_carbine_blocks() -> bytes:
    """
    Construye los bloques WeaponBehavior.hkx (SRAF=1) exclusivos para cuando el jugador
    está en vuelo en Servoarmadura (AnimFlavorMilitary / FlightFlavorKw) empuñando la
    Carabina de Rayos Astro-Cosmos (STKD incluye FID_COSMOS_HERO_WEAP_KW).
    Resuelve al hash vanilla 1769963494426611614.txt sincronizado con LaserRifleGripStraight
    (4841667677245476766.txt -> CosmosHeroCarbine\\AeroSky).
    """
    body = bytearray()
    aerial_pa_carbine_sapts = [
        r"Actors\PowerArmor\Animations\Weapons\LaserMusket\AutoCrank",
        r"Actors\PowerArmor\Animations\Weapons\LaserMusket",
        r"Actors\PowerArmor\Animations\Grips\RifleStraight",
        r"Actors\PowerArmor\Animations\Grips\Rifle",
        r"Actors\PowerArmor\Animations\Paired",
    ]
    stkd_pa_carbine = [0x000464EF, 0x00099830, FID_COSMOS_HERO_WEAP_KW]

    for sakd_combo in [
        [FID_ANIM_ARCHETYPE_PLAYER, FID_ANIM_FLAVOR_MILITARY, FID_FEMALE_KW],
        [FID_ANIM_ARCHETYPE_PLAYER, FID_ANIM_FLAVOR_MILITARY],
        [FID_ANIM_FLAVOR_MILITARY, FID_FEMALE_KW],
        [FID_ANIM_FLAVOR_MILITARY],
        [FID_FLIGHT_ARCH_KW, FID_FLIGHT_FLAV_KW, FID_FEMALE_KW],
        [FID_FLIGHT_ARCH_KW, FID_FLIGHT_FLAV_KW],
        [FID_FLIGHT_FLAV_KW, FID_FEMALE_KW],
        [FID_FLIGHT_FLAV_KW],
    ]:
        body += build_subgraph_block(
            sakd_combo,
            stkd_pa_carbine,
            r"Actors\Character\Behaviors\WeaponBehavior.hkx",
            aerial_pa_carbine_sapts,
            b"\x01\x00\x00\x00",
        )
    return bytes(body)


def build_pa_additive_race(pa_w_blocks: list) -> bytes:
    body = bytearray(build_minimal_race_prefix("AeroArmor_PowerArmorSubGraphAdditive", FID_POWER_ARMOR_RACE))
    body += build_custom_pa_mt_blocks()
    body += build_custom_pa_aerial_cannon_blocks()
    body += build_custom_pa_aerial_carbine_blocks()

    for flav_kw in (FID_FLIGHT_FLAV_KW, FID_DESCENT_FLAV_KW):
        for sakds, stkds, sgnm, sapts in pa_w_blocks:
            body += build_subgraph_block(
                sakds + [flav_kw],
                stkds,
                sgnm,
                sapts,
                b"\x01\x00\x00\x00",
            )

    for arch_kw, flav_kw in [
        (FID_FLIGHT_ARCH_KW, FID_FLIGHT_FLAV_KW),
        (FID_DESCENT_ARCH_KW, FID_DESCENT_FLAV_KW),
    ]:
        for sakds, stkds, sgnm, sapts in pa_w_blocks:
            body += build_subgraph_block(
                sakds + [arch_kw],
                stkds,
                sgnm,
                sapts,
                b"\x01\x00\x00\x00",
            )
            body += build_subgraph_block(
                sakds + [arch_kw, flav_kw],
                stkds,
                sgnm,
                sapts,
                b"\x01\x00\x00\x00",
            )

    return make_record(b"RACE", FID_PA_ADD_RACE, bytes(body))


def build_pa_flavor_idle_grup() -> bytes:
    """
    Corrige el bug del juego base en IDLE 0x0001D99F (PowerArmorChangeAnimFlavor, FormVersion=112 en Fallout4.esm):
    - Sustituye ENAM='dyn_NoInterrupt_Manual' por 'g_archetypeChange' (igual que ChangeAnimFlavor humano 0x000B3446),
      ya que dyn_NoInterrupt_Manual nunca emite archetypeChangeEnd y bloqueaba la salida del subgrafo Military a tierra.
    - Elimina CTDA IsWeaponOut == 0 para permitir restaurar el subgrafo de tierra incluso al descender desenfundando un arma.
    - Apunta GNAM a '$(Subgraph)\\To_AeroInstant.hkx' (inexistente) para que BSAnimationGraphManager aplique
      DefaultSubgraphSwitchBlendingTransitionEffect de forma instantánea sin esperar clips de transición.
    """
    idle_body = (
        subrec_cstr(b"EDID", "PowerArmorChangeAnimFlavor")
        + subrec(b"CTDA", bytes.fromhex("00599607000000009f00f43f00000000000000000000000000000000ffffffff"))
        + subrec_cstr(b"DNAM", r"Actors\PowerArmor\Behaviors\PowerArmorBehavior.hkx")
        + subrec_cstr(b"ENAM", "g_archetypeChange")
        + subrec(b"ANAM", bytes.fromhex("9cd9010000000000"))
        + subrec(b"DATA", bytes.fromhex("000000610000"))
        + subrec_cstr(b"GNAM", r"$(Subgraph)\To_AeroInstant.hkx")
    )
    return make_grup(b"IDLE", make_record(b"IDLE", 0x0001D99F, idle_body, 0))


def build_vanilla_race_overrides(lang: str = "es") -> bytes:
    """
    Construye el override directo de 0x00166729 (HumanRaceSubGraphData) convirtiendo
    FULL y DESC a C-strings no localizados e insertando nuestros bloques de vuelo en la
    posición 0 (antes de AnimArchetypePlayer) y al final de la lista de subgrafos.
    Nota: PowerArmorRace (0x0001D31E) en Fallout4.esm YA tiene [AnimFlavorMilitary 0x0015F755]
    -> Actors\\PowerArmor\\Animations\\MT\\Neutral\\Military en la posición 0 de serie, por lo que
    NO se sobreescribe 0x0001D31E (evitando FMRN localizados y garantizando 0 conflictos con mods de PA).
    """
    with open(FO4_ESM_PATH, "rb") as f:
        data = f.read()

    out_records = bytearray()
    pos = 0
    while pos < len(data):
        rt, ds = data[pos : pos + 4], struct.unpack_from("<I", data, pos + 4)[0]
        if rt == b"GRUP" and data[pos + 8 : pos + 12] == b"RACE":
            p = pos + 24
            while p < pos + ds:
                _, rds, fl, fid, _, _ = struct.unpack_from("<4sIIIII", data, p)
                if fid == FID_HUMAN_SUBGRAPH_RACE:
                    rb = data[p + 24 : p + 24 + rds]
                    clean_prefix = bytearray()
                    sp = 0
                    first_sub_off = None
                    last_sraf_end = None
                    while sp < len(rb):
                        st, sz = rb[sp : sp + 4], struct.unpack_from("<H", rb, sp + 4)[0]
                        if st in (b"SAKD", b"STKD", b"SGNM") and first_sub_off is None:
                            first_sub_off = sp
                        if first_sub_off is None:
                            if st == b"FULL":
                                clean_prefix += subrec_cstr(b"FULL", _loc(lang, "Humano", "Human"))
                            elif st == b"DESC":
                                clean_prefix += subrec_cstr(b"DESC", "")
                            else:
                                clean_prefix += rb[sp : sp + 6 + sz]
                        sp += 6 + sz
                        if st in (b"SRAF", b"SPED"):
                            last_sraf_end = sp
                    extra_blocks = (
                        build_custom_human_mt_blocks()
                        + build_custom_human_aerial_carbine_blocks()
                        + build_custom_human_aerial_cannon_blocks()
                    )
                    new_rb = (
                        bytes(clean_prefix)
                        + extra_blocks
                        + rb[first_sub_off:last_sraf_end]
                        + extra_blocks
                        + rb[last_sraf_end:]
                    )
                    out_records += make_record(b"RACE", fid, new_rb, fl)
                p += 24 + rds
            break
        pos += ds if rt == b"GRUP" else (24 + ds)

    return bytes(out_records)


def build_cosmos_hero_arma_and_armo_records(
    existing_arma_grup: bytes, existing_armo_grup: bytes, lang: str = "es"
) -> tuple[bytes, bytes, bytes]:
    """
    Construye GRUP ARMA y GRUP ARMO integrando el «Traje de Vuelo Astro-Cosmos» (0x01000800)
    con sus mallas 3D (traje + emblema 3D + capa 3D + guantes), +180 blindaje balístico/energético
    y +1.000 resistencia a radiación para volar libremente por toda la Commonwealth.
    """
    with open(FO4_ESM_PATH, "rb") as f:
        esm = f.read()

    esm_raw = {}
    pos = 0
    while pos < len(esm):
        rt, ds = esm[pos : pos + 4], struct.unpack_from("<I", esm, pos + 4)[0]
        if rt == b"GRUP":
            lbl = esm[pos + 8 : pos + 12]
            if lbl in (b"ARMA", b"ARMO"):
                p = pos + 24
                while p < pos + ds:
                    rrt = esm[p : p + 4]
                    rds, fl, fid = struct.unpack_from("<III", esm, p + 4)
                    if fid in (FID_ESM_ARMA_SYNTH_UNIFORM, FID_ESM_ARMA_BOS_GLOVES, FID_ESM_ARMO_BOS_BLACK):
                        esm_raw[fid] = esm[p + 24 : p + 24 + rds]
                    p += 24 + rds
            pos += ds
        else:
            pos += 24 + ds

    # 1. ARMA 0x01000818: Cuerpo + Escudo 3D + Cinturón + Capa 3D (1ª y 3ª persona M/F)
    arma_suit_raw = esm_raw[FID_ESM_ARMA_SYNTH_UNIFORM]
    arma_suit_subs = bytearray(subrec_cstr(b"EDID", "AeroArmor_CosmosHeroSuitAA"))
    sp = 0
    added_ghoul_race = False
    while sp + 6 <= len(arma_suit_raw):
        st = arma_suit_raw[sp : sp + 4].decode("latin1")
        ss = struct.unpack_from("<H", arma_suit_raw, sp + 4)[0]
        if st in ("EDID", "MO2T", "MO3T", "MO4T", "MO5T", "MO2S", "MO3S", "ONAM"):
            pass
        elif st == "BOD2":
            arma_suit_subs += subrec(b"BOD2", struct.pack("<I", 0x000007C8))
        elif st == "MOD2":
            arma_suit_subs += subrec_cstr(b"MOD2", r"AeroArmor\Hero\CosmosHeroSuitM.nif")
        elif st == "MOD3":
            arma_suit_subs += subrec_cstr(b"MOD3", r"AeroArmor\Hero\CosmosHeroSuitF.nif")
        elif st == "MOD4":
            arma_suit_subs += subrec_cstr(b"MOD4", r"AeroArmor\Hero\CosmosHeroSuit1stM.nif")
        elif st == "MOD5":
            arma_suit_subs += subrec_cstr(b"MOD5", r"AeroArmor\Hero\CosmosHeroSuit1stF.nif")
        elif st == "MODL" and ss == 4 and not added_ghoul_race:
            arma_suit_subs += arma_suit_raw[sp : sp + 6 + ss]
            arma_suit_subs += subrec(b"MODL", struct.pack("<I", 0x0010BD65))
            added_ghoul_race = True
        else:
            arma_suit_subs += arma_suit_raw[sp : sp + 6 + ss]
        sp += 6 + ss
    rec_arma_suit = make_record(b"ARMA", FID_HERO_SUIT_AA, bytes(arma_suit_subs))

    # 2. ARMA 0x01000819: Guanteletes Heroicos Carmesí (1ª y 3ª persona M/F)
    arma_gloves_raw = esm_raw[FID_ESM_ARMA_BOS_GLOVES]
    arma_gloves_subs = bytearray(subrec_cstr(b"EDID", "AeroArmor_CosmosHeroGlovesAA"))
    sp = 0
    while sp + 6 <= len(arma_gloves_raw):
        st = arma_gloves_raw[sp : sp + 4].decode("latin1")
        ss = struct.unpack_from("<H", arma_gloves_raw, sp + 4)[0]
        if st in ("EDID", "MO2T", "MO3T", "MO4T", "MO5T", "MO2S", "MO3S", "MOD4", "MOD5"):
            pass
        elif st == "MOD2":
            arma_gloves_subs += subrec_cstr(b"MOD2", r"AeroArmor\Hero\CosmosHeroGlovesM.nif")
        elif st == "MOD3":
            arma_gloves_subs += subrec_cstr(b"MOD3", r"AeroArmor\Hero\CosmosHeroGlovesF.nif")
            arma_gloves_subs += subrec_cstr(b"MOD4", r"AeroArmor\Hero\CosmosHeroGlovesM.nif")
            arma_gloves_subs += subrec_cstr(b"MOD5", r"AeroArmor\Hero\CosmosHeroGlovesF.nif")
        else:
            arma_gloves_subs += arma_gloves_raw[sp : sp + 6 + ss]
        sp += 6 + ss
    rec_arma_gloves = make_record(b"ARMA", FID_HERO_GLOVES_AA, bytes(arma_gloves_subs))

    # Conservar 0x01000807 (AeroArmor_FlightRingAA) para compatibilidad con partidas previas
    kept_arma = bytearray()
    if existing_arma_grup:
        p = 24
        while p < len(existing_arma_grup):
            rds, _, fid = struct.unpack_from("<III", existing_arma_grup, p + 4)
            if fid not in (FID_HERO_SUIT_AA, FID_HERO_GLOVES_AA):
                kept_arma += existing_arma_grup[p : p + 24 + rds]
            p += 24 + rds
    grup_arma = make_grup(b"ARMA", bytes(kept_arma) + rec_arma_suit + rec_arma_gloves)

    # 3. ARMO 0x01000800: Traje de Vuelo Astro-Cosmos (180 Balístico, 180 Energía, 1000 Radiación)
    armo_suit_raw = esm_raw[FID_ESM_ARMO_BOS_BLACK]
    suit_subs = bytearray(subrec_cstr(b"EDID", "AeroArmor_FlightSuit"))
    sp = 0
    while sp + 6 <= len(armo_suit_raw):
        st = armo_suit_raw[sp : sp + 4].decode("latin1")
        ss = struct.unpack_from("<H", armo_suit_raw, sp + 4)[0]
        sv = armo_suit_raw[sp + 6 : sp + 6 + ss]
        if st in ("EDID", "MO2T", "MO2S", "INRD", "APPR"):
            pass
        elif st == "MOD2":
            suit_subs += subrec_cstr(b"MOD2", r"AeroArmor\Hero\CosmosHeroSuitGO.nif")
        elif st == "FULL":
            suit_subs += subrec_cstr(b"FULL", _loc(lang, "Traje de Vuelo Astro-Cosmos", "Astro-Cosmos Flight Suit"))
            suit_subs += subrec(b"EITM", struct.pack("<I", FID_FLIGHT_ENCH))
        elif st == "DESC":
            suit_subs += subrec_cstr(
                b"DESC",
                _loc(
                    lang,
                    "Prototipo aeroespacial inspirado en el Capitan Cosmos. Permite volar en 1a y 3a persona "
                    "(compatible en combate aereo con la Carabina de Rayos Astro-Cosmos), e incorpora blindaje "
                    "balistico/energetico (+180) y escudo antirradiacion cosmico total (inmunidad 100%, +1.000 RAD).",
                    "Aerospace prototype inspired by Captain Cosmos. Grants free flight in 1st and 3rd person "
                    "(compatible in aerial combat with the Astro-Cosmos Ray Carbine and Orbital Gauss Cannon), "
                    "with +180 ballistic/energy armor and a total cosmic rad shield (100% immunity, +1,000 RAD).",
                ),
            )
        elif st == "MODL" and ss == 4:
            orig_modl = struct.unpack("<I", sv)[0]
            if orig_modl == 0x00134293:
                suit_subs += subrec(b"MODL", struct.pack("<I", FID_HERO_SUIT_AA))
            elif orig_modl == 0x0020DCDA:
                suit_subs += subrec(b"MODL", struct.pack("<I", FID_HERO_GLOVES_AA))
            else:
                suit_subs += armo_suit_raw[sp : sp + 6 + ss]
        elif st == "DATA" and ss == 12:
            suit_subs += subrec(b"DATA", struct.pack("<IfI", 4500, 2.5, 0))
        elif st == "FNAM" and ss == 8:
            suit_subs += subrec(b"FNAM", struct.pack("<II", 180, 0))
            suit_subs += subrec(b"DAMA", struct.pack("<IIII", 0x00060A81, 180, 0x00060A85, 1000))
        elif st == "DAMA":
            pass
        else:
            suit_subs += armo_suit_raw[sp : sp + 6 + ss]
        sp += 6 + ss
    rec_armo_suit = make_record(b"ARMO", FID_HERO_SUIT_ARMO, bytes(suit_subs))

    # Conservar 0x01000801 (Anillo antiguo) pero retirando EITM para que el vuelo sea exclusivo del Traje y del Torso PA
    pa_armo_fids = {
        FID_COSMOS_PA_TORSO,
        FID_COSMOS_PA_HELM,
        FID_COSMOS_PA_LARM,
        FID_COSMOS_PA_RARM,
        FID_COSMOS_PA_LLEG,
        FID_COSMOS_PA_RLEG,
    }
    kept_armo = bytearray()
    if existing_armo_grup:
        p = 24
        while p < len(existing_armo_grup):
            rds, fl, fid = struct.unpack_from("<III", existing_armo_grup, p + 4)
            if fid != FID_HERO_SUIT_ARMO and fid not in pa_armo_fids:
                rb = existing_armo_grup[p + 24 : p + 24 + rds]
                if fid == FID_FLIGHT_RING_ARMO:
                    clean_rb = bytearray()
                    rsp = 0
                    while rsp + 6 <= len(rb):
                        rst = rb[rsp : rsp + 4]
                        rsz = struct.unpack_from("<H", rb, rsp + 4)[0]
                        if rst != b"EITM":
                            clean_rb += rb[rsp : rsp + 6 + rsz]
                        rsp += 6 + rsz
                    ring_rec = make_record(b"ARMO", fid, bytes(clean_rb), fl)
                    kept_armo += _rewrite_record_cstrs(
                        ring_rec,
                        {
                            b"FULL": _loc(lang, "Anillo Propulsor Aero-Mk-I", "Aero-Mk-I Thruster Ring (Legacy)"),
                            b"DESC": _loc(
                                lang,
                                "Modulo de vuelo en ranura libre (Slot 55). El vuelo tambien esta activo de forma innata con cualquier armadura.",
                                "Legacy prototype ring (Slot 55). Free flight is now exclusively powered by the Astro-Cosmos Flight Suit and Power Armor Torso.",
                            ),
                        },
                    )
                else:
                    kept_armo += existing_armo_grup[p : p + 24 + rds]
            p += 24 + rds

    pa_omod_grup, pa_armo_records = build_cosmos_pa_omod_and_armo_records(lang)
    grup_armo = make_grup(b"ARMO", rec_armo_suit + pa_armo_records + bytes(kept_armo))
    return grup_arma, grup_armo, pa_omod_grup


def build_cosmos_pa_omod_and_armo_records(lang: str = "es") -> tuple[bytes, bytes]:
    """
    Construye GRUP OMOD (6 modificaciones base 3D) y los 6 registros ARMO de la
    «Servoarmadura Astro-Cosmos». Únicamente el Torso (0x01000820) otorga la capacidad
    intrínseca de vuelo y el escudo antirradiación cósmico (100% inmunidad), permitiendo
    combinarlo libremente con otras piezas o llevar la servoarmadura completa a juego.
    """
    esm_targets = {
        FID_ESM_PA_T51_TORSO,
        FID_ESM_PA_T51_HELM,
        FID_ESM_PA_T51_LARM,
        FID_ESM_PA_T51_RARM,
        FID_ESM_PA_T51_LLEG,
        FID_ESM_PA_T51_RLEG,
        FID_ESM_OMOD_T51_TORSO,
        FID_ESM_OMOD_T51_HELM,
        FID_ESM_OMOD_T51_LARM,
        FID_ESM_OMOD_T51_RARM,
        FID_ESM_OMOD_T51_LLEG,
        FID_ESM_OMOD_T51_RLEG,
    }
    with open(FO4_ESM_PATH, "rb") as f:
        esm = f.read()

    esm_raw = {}
    pos = 0
    while pos < len(esm):
        rt, ds = esm[pos : pos + 4], struct.unpack_from("<I", esm, pos + 4)[0]
        if rt == b"GRUP":
            if esm[pos + 8 : pos + 12] in (b"ARMO", b"OMOD"):
                p = pos + 24
                while p < pos + ds:
                    rds, _, fid = struct.unpack_from("<III", esm, p + 4)
                    if fid in esm_targets:
                        esm_raw[fid] = esm[p + 24 : p + 24 + rds]
                    p += 24 + rds
            pos += ds
        else:
            pos += 24 + ds

    pa_specs = [
        (
            FID_COSMOS_PA_TORSO,
            FID_OMOD_PA_TORSO,
            FID_ESM_PA_T51_TORSO,
            FID_ESM_OMOD_T51_TORSO,
            "AeroArmor_CosmosPA_Torso",
            "PA_Cosmos_Torso",
            _loc(lang, "Torso Propulsor Astro-Cosmos", "Astro-Cosmos Jetpack Torso"),
            _loc(
                lang,
                "Coraza central birreactor de la Servoarmadura Astro-Cosmos (Hubris Comics). "
                "Equipa este torso en cualquier armazon de Servoarmadura para activar el vuelo fluido "
                "en 1a y 3a persona (compatible en combate aereo con el Canon Orbital Gauss Astro-Cosmos) "
                "y el escudo antirradiacion cosmico total (100% inmunidad).",
                "Twin-reactor central chestplate of the Astro-Cosmos Power Armor (Hubris Comics). "
                "Equip this torso on any Power Armor frame to unlock smooth 1st- and 3rd-person flight "
                "(compatible in aerial combat with the Astro-Cosmos Orbital Gauss Cannon and Ray Carbine) "
                "and a total cosmic rad shield (100% immunity).",
            ),
            r"AeroArmor\PowerArmor\CosmosPA_Body.nif",
            r"AeroArmor\PowerArmor\GO_CosmosPA_Body.nif",
            420,
            400,
            500,
            True,
        ),
        (
            FID_COSMOS_PA_HELM,
            FID_OMOD_PA_HELM,
            FID_ESM_PA_T51_HELM,
            FID_ESM_OMOD_T51_HELM,
            "AeroArmor_CosmosPA_Helm",
            "PA_Cosmos_Helmet",
            _loc(lang, "Casco Astro-Cosmos", "Astro-Cosmos Helmet"),
            _loc(
                lang,
                "Escafandra esferica presurizada de buzo espacial estilo Capitan Cosmos con mirilla circular "
                "acorazada de cristal ambar, collarin de bronce remachado, antenas gemelas y faro frontal integrado.",
                "Pressurized spherical Captain Cosmos space-diver dome with an armored circular amber-glass "
                "viewport, riveted bronze neck ring, twin antennae, and integrated headlamp.",
            ),
            r"AeroArmor\PowerArmor\CosmosPA_Helmet.nif",
            r"AeroArmor\PowerArmor\GO_CosmosPA_Helmet.nif",
            220,
            200,
            250,
            False,
        ),
        (
            FID_COSMOS_PA_LARM,
            FID_OMOD_PA_LARM,
            FID_ESM_PA_T51_LARM,
            FID_ESM_OMOD_T51_LARM,
            "AeroArmor_CosmosPA_ArmLeft",
            "PA_Cosmos_LArm",
            _loc(lang, "Brazo Izquierdo Astro-Cosmos", "Astro-Cosmos Left Arm"),
            _loc(
                lang,
                "Hombrera cobalto con chevron alado dorado y guantelete espacial carmesi Astro-Cosmos (brazo izquierdo).",
                "Cobalt pauldron with gilded winged chevron and crimson Astro-Cosmos space gauntlet (left arm).",
            ),
            r"AeroArmor\PowerArmor\CosmosPA_LArm.nif",
            r"AeroArmor\PowerArmor\GO_CosmosPA_Arm.nif",
            210,
            200,
            250,
            False,
        ),
        (
            FID_COSMOS_PA_RARM,
            FID_OMOD_PA_RARM,
            FID_ESM_PA_T51_RARM,
            FID_ESM_OMOD_T51_RARM,
            "AeroArmor_CosmosPA_ArmRight",
            "PA_Cosmos_RArm",
            _loc(lang, "Brazo Derecho Astro-Cosmos", "Astro-Cosmos Right Arm"),
            _loc(
                lang,
                "Hombrera cobalto con chevron alado dorado y guantelete espacial carmesi Astro-Cosmos (brazo derecho).",
                "Cobalt pauldron with gilded winged chevron and crimson Astro-Cosmos space gauntlet (right arm).",
            ),
            r"AeroArmor\PowerArmor\CosmosPA_RArm.nif",
            r"AeroArmor\PowerArmor\GO_CosmosPA_Arm.nif",
            210,
            200,
            250,
            False,
        ),
        (
            FID_COSMOS_PA_LLEG,
            FID_OMOD_PA_LLEG,
            FID_ESM_PA_T51_LLEG,
            FID_ESM_OMOD_T51_LLEG,
            "AeroArmor_CosmosPA_LegLeft",
            "PA_Cosmos_LLeg",
            _loc(lang, "Pierna Izquierda Astro-Cosmos", "Astro-Cosmos Left Leg"),
            _loc(
                lang,
                "Muslera cobalto y bota espacial carmesi con escudo de rodilla en V y aleta estabilizadora dorada (pierna izquierda).",
                "Cobalt thigh guard and crimson space boot with V-crested knee shield and golden stabilizer fin (left leg).",
            ),
            r"AeroArmor\PowerArmor\CosmosPA_LLeg.nif",
            r"AeroArmor\PowerArmor\GO_CosmosPA_Leg.nif",
            210,
            200,
            250,
            False,
        ),
        (
            FID_COSMOS_PA_RLEG,
            FID_OMOD_PA_RLEG,
            FID_ESM_PA_T51_RLEG,
            FID_ESM_OMOD_T51_RLEG,
            "AeroArmor_CosmosPA_LegRight",
            "PA_Cosmos_RLeg",
            _loc(lang, "Pierna Derecha Astro-Cosmos", "Astro-Cosmos Right Leg"),
            _loc(
                lang,
                "Muslera cobalto y bota espacial carmesi con escudo de rodilla en V y aleta estabilizadora dorada (pierna derecha).",
                "Cobalt thigh guard and crimson space boot with V-crested knee shield and golden stabilizer fin (right leg).",
            ),
            r"AeroArmor\PowerArmor\CosmosPA_RLeg.nif",
            r"AeroArmor\PowerArmor\GO_CosmosPA_Leg.nif",
            210,
            200,
            250,
            False,
        ),
    ]

    omod_records = bytearray()
    armo_records = bytearray()

    for (
        armo_fid,
        omod_fid,
        esm_armo_fid,
        esm_omod_fid,
        armo_edid,
        omod_edid,
        full_name,
        desc_text,
        rig_nif_rel,
        go_nif_rel,
        ballistic_dr,
        energy_dr,
        rad_dr,
        is_torso,
    ) in pa_specs:
        # 1. Construir OMOD base
        src_omod = esm_raw[esm_omod_fid]
        omod_data_payload = None
        omod_mnam_payload = None
        omod_lnam_payload = None
        osp = 0
        while osp + 6 <= len(src_omod):
            ost = src_omod[osp : osp + 4]
            osz = struct.unpack_from("<H", src_omod, osp + 4)[0]
            ov = src_omod[osp + 6 : osp + 6 + osz]
            if ost == b"DATA":
                omod_data_payload = ov
            elif ost == b"MNAM":
                omod_mnam_payload = ov
            elif ost == b"LNAM":
                omod_lnam_payload = ov
            osp += 6 + osz
        assert omod_data_payload is not None
        omod_body = (
            subrec_cstr(b"EDID", omod_edid)
            + subrec_cstr(b"FULL", full_name)
            + subrec_cstr(b"DESC", desc_text)
            + subrec_cstr(b"MODL", rig_nif_rel)
            + subrec(b"DATA", omod_data_payload)
        )
        if omod_mnam_payload is not None:
            omod_body += subrec(b"MNAM", omod_mnam_payload)
        if omod_lnam_payload is not None:
            omod_body += subrec(b"LNAM", omod_lnam_payload)
        omod_records += make_record(b"OMOD", omod_fid, omod_body)

        # 2. Construir ARMO con plantilla OBTE -> OBTS -> OBTF -> STOP limpia (FormVersion 131)
        src_armo = esm_raw[esm_armo_fid]
        if is_torso:
            default_omods = [omod_fid, 0x00077D3B, 0x00077D3A, 0x00077D9D]
        elif armo_fid == FID_COSMOS_PA_HELM:
            default_omods = [omod_fid, 0x00077D3B, 0x00077D3A, 0x00077D45, 0x0016B6E6]
        elif armo_fid in (FID_COSMOS_PA_LARM, FID_COSMOS_PA_RARM):
            default_omods = [omod_fid, 0x00077D3B, 0x00077D3A, 0x00077D44]
        else:
            default_omods = [omod_fid, 0x00077D3B, 0x00077D3A, 0x00077D9C]

        pa_obts = bytearray.fromhex("000000000000000000000000ffff01000000")
        pa_obts[0] = len(default_omods)
        for mod_id in default_omods:
            pa_obts.extend(struct.pack("<I", mod_id) + b"\x00\x00\x01")

        armo_subs = bytearray(subrec_cstr(b"EDID", armo_edid))
        asp = 0
        while asp + 6 <= len(src_armo):
            ast = src_armo[asp : asp + 4].decode("latin1")
            asz = struct.unpack_from("<H", src_armo, asp + 4)[0]
            asv = src_armo[asp + 6 : asp + 6 + asz]
            if ast == "OBTE":
                break
            if ast in ("EDID", "MO2T", "MO2S", "INRD", "DAMA"):
                pass
            elif ast == "FULL":
                armo_subs += subrec_cstr(b"FULL", full_name)
            elif ast == "MOD2":
                armo_subs += subrec_cstr(b"MOD2", go_nif_rel)
            elif ast == "KSIZ" and is_torso:
                old_k = struct.unpack("<I", asv)[0]
                armo_subs += subrec(b"KSIZ", struct.pack("<I", old_k + 1))
            elif ast == "KWDA" and is_torso:
                armo_subs += subrec(b"KWDA", asv + struct.pack("<I", FID_COSMOS_PA_TORSO_KW))
            elif ast == "DESC":
                armo_subs += subrec_cstr(b"DESC", desc_text)
            elif ast == "DATA" and asz == 12:
                armo_subs += subrec(b"DATA", struct.pack("<IfI", 3500, 1.5, 1800))
            elif ast == "FNAM" and asz == 8:
                armo_subs += subrec(b"FNAM", struct.pack("<II", ballistic_dr, 0))
                armo_subs += subrec(
                    b"DAMA",
                    struct.pack("<IIII", 0x00060A81, energy_dr, 0x00060A85, rad_dr),
                )
            else:
                armo_subs += src_armo[asp : asp + 6 + asz]
            asp += 6 + asz

        armo_subs += (
            subrec(b"OBTE", struct.pack("<I", 1))
            + subrec(b"OBTS", bytes(pa_obts))
            + subrec(b"OBTF", b"")
            + subrec(b"STOP", b"")
        )
        armo_records += make_record(b"ARMO", armo_fid, bytes(armo_subs))

    return bytes(omod_records), bytes(armo_records)


def build_cosmos_aim_model_grup() -> bytes:
    """
    Construye GRUP AMDL con modelos de puntería aeroespaciales estabilizados por giroscopio:
      - 0x0100084D (`AeroArmor_CosmosHeroCarbine_AM`)
      - 0x0100085D (`AeroArmor_CosmosPACannon_AM`)
    """
    specs = (
        (
            FID_COSMOS_HERO_AMDL,
            "AeroArmor_CosmosHeroCarbine_AM",
            (0.03, 0.20, 0.03, 12.0, 60, 0.50, 320.0, 1.50, 0.45, 0.25, 0.75, 12, 25.0, 0.0, 0.02, 4.5),
        ),
        (
            FID_COSMOS_PA_AMDL,
            "AeroArmor_CosmosPACannon_AM",
            (0.02, 0.18, 0.04, 12.0, 60, 0.50, 320.0, 1.50, 1.60, 1.00, 0.75, 12, 20.0, 0.0, 0.02, 4.5),
        ),
    )
    recs = bytearray()
    for amdl_fid, edid, vals in specs:
        dnam = struct.pack("<ffffIffffffIffff", *vals)
        assert len(dnam) == 64
        recs += make_record(b"AMDL", amdl_fid, subrec_cstr(b"EDID", edid) + subrec(b"DNAM", dnam))
    return make_grup(b"AMDL", bytes(recs))


def build_cosmos_hero_carbine_records(lang: str = "es") -> tuple[bytes, bytes, bytes, bytes, bytes]:
    """
    Construye todos los registros de la «Carabina de Rayos Astro-Cosmos» (arma aérea
    exclusiva para el Traje de Vuelo Astro-Cosmos):
      - MGEF 0x01000849 (`mgef_CosmosHeroCarbineHit` -> `AeroCosmosCarbineEffect.pex`)
      - ENCH 0x01000848 (`ench_CosmosHeroCarbine` -> +25 daño fotónico/eléctrico + Pulso Cósmico cada 4 impactos)
      - 5 OMODs 0x01000841..0x01000845 (Condensador, Cañón de Anillos, Culata Espacial, Mira Reconocimiento 6x, Corona Atómica)
      - ZOOM 0x01000846 (`ZM_Cosmos_Recon_Scope_x6` -> 6.0x aumento + HUD Reconocimiento)
      - WEAP 0x01000840 (`AeroArmor_CosmosHeroCarbine` -> Rayos fotónicos azul-cian + desintegración azul)
    """
    esm_targets = {
        FID_ESM_WEAP_LASERGUN,
        FID_ESM_OMOD_LG_REC,
        FID_ESM_OMOD_LG_BAR,
        FID_ESM_OMOD_LG_STK,
        FID_ESM_OMOD_LG_SCP,
        FID_ESM_OMOD_LG_FOC,
        FID_ESM_MGEF_SHOCK,
    }
    with open(FO4_ESM_PATH, "rb") as f:
        esm = f.read()

    esm_raw = {}
    pos = 0
    while pos < len(esm):
        rt, ds = esm[pos : pos + 4], struct.unpack_from("<I", esm, pos + 4)[0]
        if rt == b"GRUP":
            if esm[pos + 8 : pos + 12] in (b"WEAP", b"OMOD", b"MGEF"):
                p = pos + 24
                while p < pos + ds:
                    rds, _, fid = struct.unpack_from("<III", esm, p + 4)
                    if fid in esm_targets:
                        esm_raw[fid] = esm[p + 24 : p + 24 + rds]
                    p += 24 + rds
            pos += ds
        else:
            pos += 24 + ds

    # 1. MGEF 0x01000849: Pulso Fotónico Astro-Cosmos (Script Archetype -> AeroCosmosCarbineEffect)
    shock_raw = esm_raw[FID_ESM_MGEF_SHOCK]
    mgef_subs = bytearray(
        subrec_cstr(b"EDID", "mgef_CosmosHeroCarbineHit")
        + subrec(b"VMAD", build_simple_vmad("AeroCosmosCarbineEffect"))
    )
    sp = 0
    while sp + 6 <= len(shock_raw):
        st = shock_raw[sp : sp + 4].decode("latin1")
        ss = struct.unpack_from("<H", shock_raw, sp + 4)[0]
        sv = bytearray(shock_raw[sp + 6 : sp + 6 + ss])
        if st in ("EDID", "VMAD"):
            pass
        elif st == "FULL":
            mgef_subs += subrec_cstr(b"FULL", _loc(lang, "Pulso Fotonico Astro-Cosmos", "Astro-Cosmos Photonic Pulse"))
        elif st == "DNAM":
            mgef_subs += subrec_cstr(
                b"DNAM",
                _loc(
                    lang,
                    "Cada 4 impactos desata un Pulso Fotonico Cosmico (+25 PA, +15 PS y descarga estelar).",
                    "Every 4 hits unleashes a Cosmic Photonic Pulse (+25 AP, +15 HP, and stellar discharge).",
                ),
            )
        elif st == "DATA" and ss == 152:
            flags = struct.unpack_from("<I", sv, 0)[0] & ~0x00000200  # permitir duración 1s
            struct.pack_into("<I", sv, 0, flags)
            struct.pack_into("<II", sv, 64, 1, 0)  # Archetype = 1 (Script), ActorVal = None
            struct.pack_into("<II", sv, 80, 1, 1)  # Fire and Forget (1), Contact (1)
            mgef_subs += subrec(b"DATA", bytes(sv))
        else:
            mgef_subs += shock_raw[sp : sp + 6 + ss]
        sp += 6 + ss
    rec_carbine_mgef = make_record(b"MGEF", FID_COSMOS_CARBINE_MGEF, bytes(mgef_subs))

    # 2. ENCH 0x01000848: Descarga Fotónica Astro-Cosmos (+25 daño energético/eléctrico + script MGEF)
    carbine_ench_body = (
        subrec_cstr(b"EDID", "ench_CosmosHeroCarbine")
        + subrec(b"OBND", b"\x00" * 12)
        + subrec_cstr(b"FULL", _loc(lang, "Descarga Fotonica Astro-Cosmos", "Astro-Cosmos Photonic Discharge"))
        + subrec(
            b"ENIT",
            bytes.fromhex("000000000400000001000000000000000100000006000000000000000000000000000000"),
        )
        + subrec(b"EFID", struct.pack("<I", FID_ESM_MGEF_SHOCK))
        + subrec(b"EFIT", struct.pack("<fII", 25.0, 0, 0))
        + subrec(b"EFID", struct.pack("<I", FID_COSMOS_CARBINE_MGEF))
        + subrec(b"EFIT", struct.pack("<fII", 0.0, 0, 1))
    )
    rec_carbine_ench = make_record(b"ENCH", FID_COSMOS_CARBINE_ENCH, carbine_ench_body)

    # 3. ZOOM 0x01000846: Mira Telescópica de Reconocimiento 6x (HUD Recon + 6.0x aumento)
    zoom_body = (
        subrec_cstr(b"EDID", "ZM_Cosmos_Recon_Scope_x6")
        + subrec(b"GNAM", bytes.fromhex("0000c04010000000b6412000000000000000a0c000000000"))
    )
    grup_zoom = make_grup(b"ZOOM", make_record(b"ZOOM", FID_COSMOS_SCOPE_ZOOM, zoom_body))

    # 4. 5 OMODs exclusivos de la Carabina de Rayos Astro-Cosmos (MNAM -> ma_CosmosHeroCarbine 0x0100084B)
    weap_omod_specs = [
        (
            FID_OMOD_HERO_RECEIVER,
            FID_ESM_OMOD_LG_REC,
            "omod_CosmosHeroCarbine_Receiver",
            _loc(lang, "Condensador Fotonico Astro-Cosmos", "Astro-Cosmos Photonic Capacitor"),
            _loc(
                lang,
                "Camara de condensacion fotonica azul-cobalto y oro de Hubris Comics con nucleo luminescente.",
                "Cobalt-blue and gold Hubris Comics photonic condensation chamber with luminescent core.",
            ),
            r"Weapons\AeroArmor\HeroCarbine\CosmosReceiver.nif",
            [],
        ),
        (
            FID_OMOD_HERO_BARREL,
            FID_ESM_OMOD_LG_BAR,
            "omod_CosmosHeroCarbine_Barrel",
            _loc(lang, "Canon Acelerador de Anillos Atomicos", "Atomic Ring Accelerator Barrel"),
            _loc(
                lang,
                "Canon aerodinamico de precision con anillos aceleradores dorados y aletas radiadoras.",
                "Aerodynamic precision barrel with golden accelerator rings and radiator fins.",
            ),
            r"Weapons\AeroArmor\HeroCarbine\CosmosBarrel.nif",
            [],
        ),
        (
            FID_OMOD_HERO_STOCK,
            FID_ESM_OMOD_LG_STK,
            "omod_CosmosHeroCarbine_Stock",
            _loc(lang, "Culata Aerodinamica Espacial Astro-Cosmos", "Astro-Cosmos Aerospace Stock"),
            _loc(
                lang,
                "Culata ergonomica para estabilizacion giroscopica en combate aereo y apuntado telescopico.",
                "Ergonomic stock for gyroscopic stabilization in aerial combat and scoped aiming.",
            ),
            r"Weapons\AeroArmor\HeroCarbine\CosmosStock.nif",
            [],
        ),
        (
            FID_OMOD_HERO_SCOPE,
            FID_ESM_OMOD_LG_SCP,
            "omod_CosmosHeroCarbine_ReconScope",
            _loc(lang, "Mira Telescopica de Reconocimiento Astro-Cosmos 6x", "Astro-Cosmos 6x Recon Scope"),
            _loc(
                lang,
                "Visor torpedo de laton y cobalto con aumento 6x y marcado automatico de objetivos hostiles.",
                "Brass-and-cobalt torpedo sight with 6x magnification and automatic hostile target tracking.",
            ),
            r"Weapons\AeroArmor\HeroCarbine\CosmosReconScope.nif",
            [
                (
                    b"\x43\x00\x00\x00\x24\x7a\x24\x00",
                    b"\x43\x00\x00\x00" + struct.pack("<I", FID_COSMOS_SCOPE_ZOOM),
                ),
            ],
        ),
        (
            FID_OMOD_HERO_FOCUSER,
            FID_ESM_OMOD_LG_FOC,
            "omod_CosmosHeroCarbine_Focuser",
            _loc(lang, "Corona Focalizadora Atomica de 3 Puntas", "3-Prong Atomic Crown Focuser"),
            _loc(
                lang,
                "Focalizador trifasico que proyecta haces de fotones azul-cian de alta velocidad.",
                "Three-phase focuser projecting high-velocity cyan-blue photon beams.",
            ),
            r"Weapons\AeroArmor\HeroCarbine\CosmosFocuser.nif",
            [
                (
                    b"\x3c\x00\x00\x00\xcd\x2f\x02\x00",
                    b"\x3c\x00\x00\x00" + struct.pack("<I", 0x00126029),  # Destello azul
                ),
                (
                    b"\x50\x00\x00\x00\xf9\x8b\x0c\x00",
                    b"\x50\x00\x00\x00" + struct.pack("<I", 0x0012602F),  # Haz LaserBeamFocusLtBlue
                ),
            ],
        ),
    ]

    weap_omod_records = bytearray()
    for omod_fid, esm_omod_fid, omod_edid, full_name, desc_text, nif_rel, data_patches in weap_omod_specs:
        src_omod = esm_raw[esm_omod_fid]
        omod_data = None
        osp = 0
        while osp + 6 <= len(src_omod):
            ost = src_omod[osp : osp + 4]
            osz = struct.unpack_from("<H", src_omod, osp + 4)[0]
            if ost == b"DATA":
                omod_data = src_omod[osp + 6 : osp + 6 + osz]
                break
            osp += 6 + osz
        assert omod_data is not None
        for old_seq, new_seq in data_patches:
            assert old_seq in omod_data, f"No se encontro secuencia {old_seq.hex()} en OMOD 0x{esm_omod_fid:08X}"
            omod_data = omod_data.replace(old_seq, new_seq, 1)

        omod_body = (
            subrec_cstr(b"EDID", omod_edid)
            + subrec_cstr(b"FULL", full_name)
            + subrec_cstr(b"DESC", desc_text)
            + subrec_cstr(b"MODL", nif_rel)
            + subrec(b"DATA", omod_data)
            + subrec(b"MNAM", struct.pack("<I", FID_MA_COSMOS_CARBINE_KW))
        )
        weap_omod_records += make_record(b"OMOD", omod_fid, omod_body)

    # 5. WEAP 0x01000840: Carabina de Rayos Astro-Cosmos
    lg_raw = esm_raw[FID_ESM_WEAP_LASERGUN]
    default_weap_omods = [
        FID_OMOD_HERO_RECEIVER,
        FID_OMOD_HERO_BARREL,
        FID_OMOD_HERO_STOCK,
        FID_OMOD_HERO_SCOPE,
        FID_OMOD_HERO_FOCUSER,
    ]
    weap_obts = bytearray.fromhex("050000000000000000000000ffff01000000")
    for mod_id in default_weap_omods:
        weap_obts.extend(struct.pack("<I", mod_id) + b"\x00\x00\x01")

    weap_subs = bytearray(subrec_cstr(b"EDID", "AeroArmor_CosmosHeroCarbine"))
    wsp = 0
    in_obte_block = False
    while wsp + 6 <= len(lg_raw):
        wst = lg_raw[wsp : wsp + 4].decode("latin1")
        wsz = struct.unpack_from("<H", lg_raw, wsp + 4)[0]
        wsv = bytearray(lg_raw[wsp + 6 : wsp + 6 + wsz])

        if wst == "OBTE":
            in_obte_block = True
            weap_subs += (
                subrec(b"OBTE", struct.pack("<I", 1))
                + subrec(b"OBTF", b"")
                + subrec_cstr(b"FULL", "Default")
                + subrec(b"OBTS", bytes(weap_obts))
                + subrec(b"STOP", b"")
            )
            wsp += 6 + wsz
            continue
        if in_obte_block:
            if wst == "STOP":
                in_obte_block = False
            wsp += 6 + wsz
            continue

        if wst in ("EDID", "INRD"):
            pass
        elif wst == "PTRN":
            weap_subs += subrec(b"PTRN", struct.pack("<I", FID_COSMOS_WEAP_TRNS))
        elif wst == "FULL":
            weap_subs += subrec_cstr(b"FULL", _loc(lang, "Carabina de Rayos Astro-Cosmos", "Astro-Cosmos Ray Carbine"))
            weap_subs += subrec(b"EITM", struct.pack("<I", FID_COSMOS_CARBINE_ENCH))
        elif wst == "KSIZ":
            old_k = struct.unpack_from("<I", wsv, 0)[0]
            weap_subs += subrec(b"KSIZ", struct.pack("<I", old_k + 1))
        elif wst == "KWDA":
            kws = list(struct.unpack(f"<{wsz // 4}I", wsv))
            kws = [FID_MA_COSMOS_CARBINE_KW if k == FID_ESM_MA_LASERGUN else k for k in kws]
            kws.append(FID_COSMOS_HERO_WEAP_KW)
            weap_subs += subrec(b"KWDA", struct.pack(f"<{len(kws)}I", *kws))
        elif wst == "DESC":
            weap_subs += subrec_cstr(
                b"DESC",
                _loc(
                    lang,
                    "Carabina aeroespacial de rayos fotonicos azules inspirada en el Capitan Cosmos con mira "
                    "telescopica de reconocimiento 6x. Compatible en vuelo tanto con el Traje de Vuelo como con la "
                    "Servoarmadura Astro-Cosmos. Cada 4 impactos desata un Pulso Fotonico Cosmico (+25 PA, +15 PS).",
                    "Aerospace blue photonic ray carbine inspired by Captain Cosmos with a 6x recon scope. "
                    "Flight-compatible with both the Astro-Cosmos Flight Suit and Power Armor. Every 4 hits "
                    "unleashes a Cosmic Photonic Pulse (+25 AP, +15 HP).",
                ),
            )
        elif wst == "WAMD" and wsz == 4:
            weap_subs += subrec(b"WAMD", struct.pack("<I", FID_COSMOS_HERO_AMDL))
        elif wst == "DNAM" and wsz == 132:
            struct.pack_into("<ff", wsv, 16, 400.0, 520.0)
            struct.pack_into("<f", wsv, 32, 0.85)
            struct.pack_into("<I", wsv, 63, 4800)  # Valor = 4800 chapas
            weap_subs += subrec(b"DNAM", bytes(wsv))
        elif wst == "CRDT" and wsz == 12:
            # 2.0x multiplicador crítico + desintegración cósmica azul (0x001E4506)
            weap_subs += subrec(b"CRDT", bytes.fromhex("000000400000803f06451e00"))
        elif wst == "INAM" and wsz == 4:
            weap_subs += subrec(b"INAM", struct.pack("<I", 0x0012602A))  # Impactos fotónicos azules
        elif wst == "DAMA":
            weap_subs += subrec(b"DAMA", struct.pack("<II", 0x00060A81, 68))  # 68 daño energético base (+25 ENCH)
        else:
            weap_subs += lg_raw[wsp : wsp + 6 + wsz]
        wsp += 6 + wsz

    rec_carbine_weap = make_record(b"WEAP", FID_COSMOS_HERO_WEAP, bytes(weap_subs))
    rec_carbine_zoom = make_record(b"ZOOM", FID_COSMOS_SCOPE_ZOOM, zoom_body)
    return rec_carbine_mgef, rec_carbine_ench, bytes(weap_omod_records), rec_carbine_weap, rec_carbine_zoom


def build_cosmos_pa_cannon_records(lang: str = "es") -> tuple[bytes, bytes, bytes, bytes, bytes]:
    """
    Construye todos los registros del «Cañón Orbital Gauss Astro-Cosmos» (arma aérea pesada
    exclusiva para la Servoarmadura Astro-Cosmos):
      - MGEF 0x01000859 (`mgef_CosmosPACannonHit` -> `AeroCosmosCannonEffect.pex`)
      - ENCH 0x01000858 (`ench_CosmosPACannon` -> +35 daño electromagnético + Supernova Solar cada 3 impactos)
      - 5 OMODs 0x01000851..0x01000855 (Cañón Hexagonal de Bobinas Saturno, Tambor Condensador Solar,
        Culata Acorazada de Guantelete, Mira de Observatorio Orbital 8x, Freno Solar de 4 Rieles)
      - ZOOM 0x01000856 (`ZM_Cosmos_PA_OrbitalScope_x8` -> 8.0x aumento + HUD Reconocimiento)
      - WEAP 0x01000850 (`AeroArmor_CosmosPACannon` -> 168 balístico + 45 energía + 35 eléctrico)
    """
    esm_targets = {
        FID_ESM_WEAP_GAUSSRIFLE,
        FID_ESM_OMOD_GR_BAR,
        FID_ESM_OMOD_GR_MAG,
        FID_ESM_OMOD_GR_STK,
        FID_ESM_OMOD_GR_SCP,
        FID_ESM_OMOD_GR_MUZ,
        FID_ESM_MGEF_SHOCK,
    }
    with open(FO4_ESM_PATH, "rb") as f:
        esm = f.read()

    esm_raw = {}
    pos = 0
    while pos < len(esm):
        rt, ds = esm[pos : pos + 4], struct.unpack_from("<I", esm, pos + 4)[0]
        if rt == b"GRUP":
            if esm[pos + 8 : pos + 12] in (b"WEAP", b"OMOD", b"MGEF"):
                p = pos + 24
                while p < pos + ds:
                    rds, _, fid = struct.unpack_from("<III", esm, p + 4)
                    if fid in esm_targets:
                        esm_raw[fid] = esm[p + 24 : p + 24 + rds]
                    p += 24 + rds
            pos += ds
        else:
            pos += 24 + ds

    # 1. MGEF 0x01000859: Supernova Gravitatoria Solar (Script Archetype -> AeroCosmosCannonEffect)
    shock_raw = esm_raw[FID_ESM_MGEF_SHOCK]
    mgef_subs = bytearray(
        subrec_cstr(b"EDID", "mgef_CosmosPACannonHit")
        + subrec(b"VMAD", build_simple_vmad("AeroCosmosCannonEffect"))
    )
    sp = 0
    while sp + 6 <= len(shock_raw):
        st = shock_raw[sp : sp + 4].decode("latin1")
        ss = struct.unpack_from("<H", shock_raw, sp + 4)[0]
        sv = bytearray(shock_raw[sp + 6 : sp + 6 + ss])
        if st in ("EDID", "VMAD"):
            pass
        elif st == "FULL":
            mgef_subs += subrec_cstr(b"FULL", _loc(lang, "Supernova Gravitatoria Solar", "Solar Gravity Supernova"))
        elif st == "DNAM":
            mgef_subs += subrec_cstr(
                b"DNAM",
                _loc(
                    lang,
                    "Cada 3 impactos desata una Supernova Gravitatoria Solar (+35 PA, +25 PS y onda expansiva estelar).",
                    "Every 3 hits unleashes a Solar Gravity Supernova (+35 AP, +25 HP, and stellar shockwave).",
                ),
            )
        elif st == "DATA" and ss == 152:
            flags = struct.unpack_from("<I", sv, 0)[0] & ~0x00000200
            struct.pack_into("<I", sv, 0, flags)
            struct.pack_into("<II", sv, 64, 1, 0)  # Archetype = 1 (Script), ActorVal = None
            struct.pack_into("<II", sv, 80, 1, 1)  # Fire and Forget (1), Contact (1)
            mgef_subs += subrec(b"DATA", bytes(sv))
        else:
            mgef_subs += shock_raw[sp : sp + 6 + ss]
        sp += 6 + ss
    rec_cannon_mgef = make_record(b"MGEF", FID_COSMOS_PA_CANNON_MGEF, bytes(mgef_subs))

    # 2. ENCH 0x01000858: Plasma Electromagnético Solar (+35 daño eléctrico + script MGEF)
    cannon_ench_body = (
        subrec_cstr(b"EDID", "ench_CosmosPACannon")
        + subrec(b"OBND", b"\x00" * 12)
        + subrec_cstr(b"FULL", _loc(lang, "Plasma Electromagnetico Solar", "Solar Electromagnetic Plasma"))
        + subrec(
            b"ENIT",
            bytes.fromhex("000000000400000001000000000000000100000006000000000000000000000000000000"),
        )
        + subrec(b"EFID", struct.pack("<I", FID_ESM_MGEF_SHOCK))
        + subrec(b"EFIT", struct.pack("<fII", 35.0, 0, 0))
        + subrec(b"EFID", struct.pack("<I", FID_COSMOS_PA_CANNON_MGEF))
        + subrec(b"EFIT", struct.pack("<fII", 0.0, 0, 1))
    )
    rec_cannon_ench = make_record(b"ENCH", FID_COSMOS_PA_CANNON_ENCH, cannon_ench_body)

    # 3. ZOOM 0x01000856: Mira de Observatorio Orbital 8x (HUD Recon + 8.0x aumento)
    pa_zoom_body = (
        subrec_cstr(b"EDID", "ZM_Cosmos_PA_OrbitalScope_x8")
        + subrec(b"GNAM", bytes.fromhex("0000004110000000b6412000000000000000a0c000000000"))
    )
    rec_cannon_zoom = make_record(b"ZOOM", FID_COSMOS_PA_SCOPE_ZOOM, pa_zoom_body)

    # 4. 5 OMODs exclusivos del Cañón Orbital Gauss Astro-Cosmos (MNAM -> ma_CosmosPACannon 0x0100085B)
    pa_weap_omod_specs = [
        (
            FID_OMOD_PA_WEAP_BARREL,
            FID_ESM_OMOD_GR_BAR,
            "omod_CosmosPACannon_BarrelShroud",
            _loc(lang, "Carenado Hexagonal de Bobinas Saturno", "Hexagonal Saturn Coil Shroud"),
            _loc(
                lang,
                "Canon electromagnetico pesado con cuatro bobinas toroidales doradas y nucleo de plasma solar.",
                "Heavy electromagnetic barrel with four golden toroidal coils and a solar plasma core.",
            ),
            r"Weapons\AeroArmor\PACannon\CosmosPABarrelShroud.nif",
            [],
        ),
        (
            FID_OMOD_PA_WEAP_MAG,
            FID_ESM_OMOD_GR_MAG,
            "omod_CosmosPACannon_CapacitorMag",
            _loc(lang, "Tambor Condensador de Plasma Solar", "Solar Plasma Capacitor Drum"),
            _loc(
                lang,
                "Bateria cilindrica gemela de alta densidad energetica para municion electromagnetica de 2 mm.",
                "High-density twin cylindrical battery pack for 2mm electromagnetic cartridges.",
            ),
            r"Weapons\AeroArmor\PACannon\CosmosPACapacitorMag.nif",
            [],
        ),
        (
            FID_OMOD_PA_WEAP_STOCK,
            FID_ESM_OMOD_GR_STK,
            "omod_CosmosPACannon_GauntletStock",
            _loc(lang, "Culata Acorazada de Servoarmadura Astro-Cosmos", "Astro-Cosmos Power Armor Stock"),
            _loc(
                lang,
                "Empunadura sobredimensionada con guardamonte amplio para guanteletes de Servoarmadura y amortiguador giroscopico.",
                "Oversized grip with enlarged trigger guard for Power Armor gauntlets and gyroscopic recoil damper.",
            ),
            r"Weapons\AeroArmor\PACannon\CosmosPAGauntletStock.nif",
            [],
        ),
        (
            FID_OMOD_PA_WEAP_SCOPE,
            FID_ESM_OMOD_GR_SCP,
            "omod_CosmosPACannon_OrbitalScope",
            _loc(lang, "Mira Telescopica de Observatorio Orbital 8x", "8x Orbital Observatory Scope"),
            _loc(
                lang,
                "Telescopio balistico orbital con lente de zafiro-iridio, aumento 8x y marcado de objetivos hostiles.",
                "Orbital ballistic telescope with sapphire-iridium lens, 8x magnification, and hostile target tracking.",
            ),
            r"Weapons\AeroArmor\PACannon\CosmosPAOrbitalScope.nif",
            [
                (
                    b"\x43\x00\x00\x00\x24\x7a\x24\x00",
                    b"\x43\x00\x00\x00" + struct.pack("<I", FID_COSMOS_PA_SCOPE_ZOOM),
                ),
            ],
        ),
        (
            FID_OMOD_PA_WEAP_MUZZLE,
            FID_ESM_OMOD_GR_MUZ,
            "omod_CosmosPACannon_SolarMuzzle",
            _loc(lang, "Acelerador Cuadruple de Rieles Solares", "Quadruple Solar Rail Accelerator"),
            _loc(
                lang,
                "Horquilla aceleradora de cuatro rieles magneticos en X con corona de enfoque incandescente.",
                "X-shaped four-rail magnetic accelerator fork with incandescent focusing crown.",
            ),
            r"Weapons\AeroArmor\PACannon\CosmosPASolarMuzzle.nif",
            [
                (
                    b"\x01\x00\x00\x00\x01\x00\x00\x00\x03\x00\x00\x00\x00\x00\x80\xbf",
                    b"\x01\x00\x00\x00\x01\x00\x00\x00\x03\x00\x00\x00" + struct.pack("<f", 6.0),
                ),
                (
                    b"\x01\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\xbf",
                    b"\x01\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00" + struct.pack("<f", 4.0),
                ),
            ],
        ),
    ]

    pa_weap_omod_records = bytearray()
    for omod_fid, esm_omod_fid, omod_edid, full_name, desc_text, nif_rel, data_patches in pa_weap_omod_specs:
        src_omod = esm_raw[esm_omod_fid]
        omod_data = None
        osp = 0
        while osp + 6 <= len(src_omod):
            ost = src_omod[osp : osp + 4]
            osz = struct.unpack_from("<H", src_omod, osp + 4)[0]
            if ost == b"DATA":
                omod_data = src_omod[osp + 6 : osp + 6 + osz]
                break
            osp += 6 + osz
        assert omod_data is not None
        for old_seq, new_seq in data_patches:
            assert old_seq in omod_data, f"No se encontro secuencia {old_seq.hex()} en OMOD 0x{esm_omod_fid:08X}"
            omod_data = omod_data.replace(old_seq, new_seq, 1)

        omod_body = (
            subrec_cstr(b"EDID", omod_edid)
            + subrec_cstr(b"FULL", full_name)
            + subrec_cstr(b"DESC", desc_text)
            + subrec_cstr(b"MODL", nif_rel)
            + subrec(b"DATA", omod_data)
            + subrec(b"MNAM", struct.pack("<I", FID_MA_COSMOS_PA_CANNON_KW))
        )
        pa_weap_omod_records += make_record(b"OMOD", omod_fid, omod_body)

    # 5. WEAP 0x01000850: Cañón Orbital Gauss Astro-Cosmos
    gr_raw = esm_raw[FID_ESM_WEAP_GAUSSRIFLE]
    default_pa_weap_omods = [
        FID_OMOD_PA_WEAP_BARREL,
        FID_OMOD_PA_WEAP_MAG,
        FID_OMOD_PA_WEAP_STOCK,
        FID_OMOD_PA_WEAP_SCOPE,
        FID_OMOD_PA_WEAP_MUZZLE,
    ]
    pa_weap_obts = bytearray.fromhex("050000000000000000000000ffff01000000")
    for mod_id in default_pa_weap_omods:
        pa_weap_obts.extend(struct.pack("<I", mod_id) + b"\x00\x00\x01")

    pa_weap_subs = bytearray(subrec_cstr(b"EDID", "AeroArmor_CosmosPACannon"))
    wsp = 0
    in_obte_block = False
    while wsp + 6 <= len(gr_raw):
        wst = gr_raw[wsp : wsp + 4].decode("latin1")
        wsz = struct.unpack_from("<H", gr_raw, wsp + 4)[0]
        wsv = bytearray(gr_raw[wsp + 6 : wsp + 6 + wsz])

        if wst == "OBTE":
            in_obte_block = True
            pa_weap_subs += (
                subrec(b"OBTE", struct.pack("<I", 1))
                + subrec(b"OBTF", b"")
                + subrec_cstr(b"FULL", "Default")
                + subrec(b"OBTS", bytes(pa_weap_obts))
                + subrec(b"STOP", b"")
            )
            wsp += 6 + wsz
            continue
        if in_obte_block:
            if wst == "STOP":
                in_obte_block = False
            wsp += 6 + wsz
            continue

        if wst in ("EDID", "INRD", "MODT", "MO4T", "DAMA"):
            pass
        elif wst == "PTRN":
            pa_weap_subs += subrec(b"PTRN", struct.pack("<I", FID_COSMOS_PA_WEAP_TRNS))
        elif wst == "FULL":
            pa_weap_subs += subrec_cstr(b"FULL", _loc(lang, "Canon Orbital Gauss Astro-Cosmos", "Astro-Cosmos Orbital Gauss Cannon"))
            pa_weap_subs += subrec(b"EITM", struct.pack("<I", FID_COSMOS_PA_CANNON_ENCH))
        elif wst == "MODL":
            pa_weap_subs += subrec_cstr(b"MODL", r"Weapons\AeroArmor\PACannon\CosmosPACannonBase.nif")
        elif wst == "MOD4":
            pa_weap_subs += subrec_cstr(b"MOD4", r"Weapons\AeroArmor\PACannon\CosmosPACannonBase.nif")
        elif wst == "KSIZ":
            old_k = struct.unpack_from("<I", wsv, 0)[0]
            pa_weap_subs += subrec(b"KSIZ", struct.pack("<I", old_k + 1))
        elif wst == "KWDA":
            kws = list(struct.unpack(f"<{wsz // 4}I", wsv))
            kws = [FID_MA_COSMOS_PA_CANNON_KW if k == FID_ESM_MA_GAUSSRIFLE else k for k in kws]
            kws.append(FID_COSMOS_PA_WEAP_KW)
            pa_weap_subs += subrec(b"KWDA", struct.pack(f"<{len(kws)}I", *kws))
        elif wst == "DESC":
            pa_weap_subs += subrec_cstr(
                b"DESC",
                _loc(
                    lang,
                    "Canon electromagnetico orbital de bobinas solares inspirado en el Capitan Cosmos con mira "
                    "telescopica de reconocimiento 8x. Compatible en vuelo tanto con la Servoarmadura como con el "
                    "Traje de Vuelo Astro-Cosmos. Cada 3 impactos desata una Supernova Gravitatoria Solar (+35 PA, +25 PS).",
                    "Orbital solar-coil electromagnetic cannon inspired by Captain Cosmos with an 8x recon scope. "
                    "Flight-compatible with both the Astro-Cosmos Power Armor and Flight Suit. Every 3 hits unleashes "
                    "a Solar Gravity Supernova (+35 AP, +25 HP).",
                ),
            )
        elif wst == "WAMD" and wsz == 4:
            pa_weap_subs += subrec(b"WAMD", struct.pack("<I", FID_COSMOS_PA_AMDL))
        elif wst == "DNAM" and wsz == 132:
            struct.pack_into("<ff", wsv, 16, 420.0, 560.0)
            struct.pack_into("<f", wsv, 32, 0.90)
            struct.pack_into("<I", wsv, 63, 7500)  # Valor = 7500 chapas
            struct.pack_into("<H", wsv, 67, 168)   # Daño balístico base = 168
            pa_weap_subs += subrec(b"DNAM", bytes(wsv))
        elif wst == "FNAM":
            pa_weap_subs += gr_raw[wsp : wsp + 6 + wsz]
            pa_weap_subs += subrec(b"DAMA", struct.pack("<II", 0x00060A81, 45))  # +45 daño energético (+35 ENCH)
        elif wst == "CRDT" and wsz == 12:
            pa_weap_subs += subrec(b"CRDT", bytes.fromhex("000000400000803f06451e00"))
        else:
            pa_weap_subs += gr_raw[wsp : wsp + 6 + wsz]
        wsp += 6 + wsz

    rec_cannon_weap = make_record(b"WEAP", FID_COSMOS_PA_WEAP, bytes(pa_weap_subs))
    return rec_cannon_mgef, rec_cannon_ench, bytes(pa_weap_omod_records), rec_cannon_weap, rec_cannon_zoom


def build_cosmic_rad_shield_grups(
    existing_mgef_grup: bytes,
    existing_ench_grup: bytes,
    extra_mgef_rec: bytes = b"",
    extra_ench_rec: bytes = b"",
    lang: str = "es",
) -> tuple[bytes, bytes, bytes]:
    """
    Construye:
      1. PERK 0x0100081B (`AeroArmor_CosmicRadShieldPerk`): Inmunidad 100% real (0.0 RAD) combinando
         los 4 puntos de entrada del motor de Fallout 4 (`HazmatSuitRadResistancePerk` 0x0014EF46 +
         `ImmuneToRadiation` 0x000A2775, con `Playable=1, Hidden=1` y multiplicador/valor = 0.0f).
      2. MGEF 0x0100081A (`AeroArmor_CosmicRadShieldEffect`): Efecto pasivo estilo Hazmat que aplica
         `AeroArmor_CosmicRadShieldPerk` mientras el jugador viste el Traje de Vuelo Astro-Cosmos.
      3. ENCH 0x01000802 (`AeroArmor_FlightEnch`): Vincula `0x0100081A` directamente al encantamiento
         del traje (además de `0x01000803` y `0x00183314`), más los registros extra del arma aérea.
    """
    # 1. PERK 0x0100081B (AeroArmor_CosmicRadShieldPerk)
    zero_f = struct.pack("<f", 0.0)
    perk_body = (
        subrec_cstr(b"EDID", "AeroArmor_CosmicRadShieldPerk")
        + subrec_cstr(b"FULL", _loc(lang, "Escudo Antirradiacion Cosmico", "Cosmic Anti-Radiation Shield"))
        + subrec_cstr(
            b"DESC",
            _loc(
                lang,
                "Bloquea el 100% de la radiacion ambiental, acuatica y cosmica.",
                "Blocks 100% of environmental, aquatic, and cosmic radiation.",
            ),
        )
        + subrec(b"DATA", b"\x00\x00\x01\x01\x01")  # Trait=0, Level=0, Ranks=1, Playable=1, Hidden=1
        # Entry 1: Mod Incoming Spell Magnitude -> Set Value 0.0 cuando Spell HasKeyword(MagicDamageRadiation 0x000449B9)
        + subrec(b"PRKE", b"\x02\x00\x00")
        + subrec(b"DATA", b"\x29\x01\x02")
        + subrec(b"PRKC", b"\x01")
        + subrec(
            b"CTDA",
            bytes.fromhex("008b8e130000803fb5020000b9490400000000000000000000000000ffffffff"),
        )
        + subrec(b"EPFT", b"\x01")
        + subrec(b"EPFB", b"\x01\x00")
        + subrec(b"EPFD", zero_f)
        + subrec(b"PRKF", b"")
        # Entry 2: Mod Incoming Spell Magnitude -> Set Value 0.0 cuando Spell HasKeyword(DamageTypeRadiation 0x0004B25C)
        + subrec(b"PRKE", b"\x02\x00\x00")
        + subrec(b"DATA", b"\x29\x01\x02")
        + subrec(b"PRKC", b"\x01")
        + subrec(
            b"CTDA",
            bytes.fromhex("00c528050000803fb50200005cb20400000000000000000000000000ffffffff"),
        )
        + subrec(b"EPFT", b"\x01")
        + subrec(b"EPFB", b"\x01\x00")
        + subrec(b"EPFD", zero_f)
        + subrec(b"PRKF", b"")
        # Entry 3: Mod Radiation Damage (0x6A, agua / zonas ambientales / tormentas) -> Set Value 0.0 incondicional
        + subrec(b"PRKE", b"\x02\x00\x00")
        + subrec(b"DATA", b"\x6a\x01\x01")
        + subrec(b"EPFT", b"\x01")
        + subrec(b"EPFB", b"\x00\x00")
        + subrec(b"EPFD", zero_f)
        + subrec(b"PRKF", b"")
        # Entry 4: Mod Incoming Weapon/Hit Radiation (0x71, dtRadiationExposure 0x00060A85) -> Multiply Value 0.0
        + subrec(b"PRKE", b"\x02\x00\x00")
        + subrec(b"DATA", b"\x71\x03\x04")
        + subrec(b"PRKC", b"\x03")
        + subrec(
            b"CTDA",
            bytes.fromhex("00c428050000803fe0020000850a0600000000000000000000000000ffffffff"),
        )
        + subrec(b"EPFT", b"\x01")
        + subrec(b"EPFB", b"\x02\x00")
        + subrec(b"EPFD", zero_f)
        + subrec(b"PRKF", b"")
    )

    def _weap_has_kw_ctda(kw_fid: int) -> bytes:
        return (
            b"\x00\xc4\x28\x05"
            + struct.pack("<f", 1.0)
            + b"\x30\x02\x00\x00"
            + struct.pack("<I", kw_fid)
            + (b"\x00" * 12)
            + b"\xff\xff\xff\xff"
        )

    # Entries 5..8: Estabilizacion giroscopica aerea (Cone of Fire x0.15 y VATS Hit Chance +35%) para armas Astro-Cosmos
    for ep_id, ep_fn, ep_val in ((0x86, 3, 0.15), (0x7A, 2, 0.35)):
        for kw_fid in (FID_COSMOS_HERO_WEAP_KW, FID_COSMOS_PA_WEAP_KW):
            perk_body += (
                subrec(b"PRKE", b"\x02\x00\x00")
                + subrec(b"DATA", bytes((ep_id, ep_fn, 2)))
                + subrec(b"PRKC", b"\x01")
                + subrec(b"CTDA", _weap_has_kw_ctda(kw_fid))
                + subrec(b"EPFT", b"\x01")
                + subrec(b"EPFB", b"\x00\x00")
                + subrec(b"EPFD", struct.pack("<f", ep_val))
                + subrec(b"PRKF", b"")
            )
    grup_perk = make_grup(b"PERK", make_record(b"PERK", FID_COSMIC_RAD_PERK, perk_body))

    # 2. MGEF 0x0100081A (AeroArmor_CosmicRadShieldEffect, basado en HazmatSuitPerkEffect 0x0014EF48)
    mgef_data = bytearray.fromhex(
        "02000000000000000000000000000000000000000000ffff0000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000"
        "00000000ea020000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000803f00000000000000000000000000000000"
        "000000000000000000000000010000000000000000000000"
    )
    assert len(mgef_data) == 152
    struct.pack_into("<I", mgef_data, 136, FID_COSMIC_RAD_PERK)
    rec_rad_mgef = make_record(
        b"MGEF",
        FID_COSMIC_RAD_MGEF,
        subrec_cstr(b"EDID", "AeroArmor_CosmicRadShieldEffect")
        + subrec_cstr(b"FULL", _loc(lang, "Escudo Antirradiacion Cosmico", "Cosmic Anti-Radiation Shield"))
        + subrec(b"DATA", bytes(mgef_data))
        + subrec(b"SNDD", b"")
        + subrec_cstr(
            b"DNAM",
            _loc(
                lang,
                "Escudo energetico Astro-Cosmos que bloquea el 100% de la radiacion ambiental y cosmica.",
                "Astro-Cosmos energy shield that blocks 100% of environmental and cosmic radiation.",
            ),
        ),
    )

    kept_mgef = bytearray()
    if existing_mgef_grup:
        p = 24
        while p < len(existing_mgef_grup):
            rds, _, fid = struct.unpack_from("<III", existing_mgef_grup, p + 4)
            if fid not in (FID_COSMIC_RAD_MGEF, FID_COSMOS_CARBINE_MGEF, FID_COSMOS_PA_CANNON_MGEF):
                rec_chunk = existing_mgef_grup[p : p + 24 + rds]
                if fid == 0x01000803:
                    rec_chunk = _rewrite_record_cstrs(
                        rec_chunk,
                        {
                            b"FULL": _loc(lang, "Sistema de Vuelo Aero-Mk-I", "Astro-Cosmos Flight Control System"),
                            b"DNAM": _loc(
                                lang,
                                "Propulsores de vuelo continuo [Y], estabilizador Hover en aire, descenso [RS/RB] y postquemador [LS en aire].",
                                "Continuous flight thrusters [Y], mid-air hover stabilizer, controlled descent [RS/RB], and turbo afterburner [LS in mid-air].",
                            ),
                        },
                    )
                kept_mgef += rec_chunk
            p += 24 + rds
    grup_mgef = make_grup(b"MGEF", bytes(kept_mgef) + rec_rad_mgef + extra_mgef_rec)

    # 3. ENCH 0x01000802 (AeroArmor_FlightEnch) con el efecto antirradiación 0x0100081A incluido
    ench_body = (
        subrec_cstr(b"EDID", "AeroArmor_FlightEnch")
        + subrec(b"OBND", b"\x00" * 12)
        + subrec_cstr(b"FULL", _loc(lang, "Propulsion y Escudo Astro-Cosmos", "Astro-Cosmos Propulsion & Shield"))
        + subrec(
            b"ENIT",
            bytes.fromhex("000000000000000000000000000000000000000006000000000000000000000000000000"),
        )
        + subrec(b"EFID", struct.pack("<I", 0x01000803))
        + subrec(b"EFIT", struct.pack("<fII", 1.0, 0, 0))
        + subrec(b"EFID", struct.pack("<I", 0x00183314))
        + subrec(b"EFIT", struct.pack("<fII", 100.0, 0, 0))
        + subrec(b"EFID", struct.pack("<I", FID_COSMIC_RAD_MGEF))
        + subrec(b"EFIT", struct.pack("<fII", 0.0, 0, 0))
    )
    kept_ench = bytearray()
    if existing_ench_grup:
        p = 24
        while p < len(existing_ench_grup):
            rds, _, fid = struct.unpack_from("<III", existing_ench_grup, p + 4)
            if fid not in (FID_FLIGHT_ENCH, FID_COSMOS_CARBINE_ENCH, FID_COSMOS_PA_CANNON_ENCH):
                kept_ench += existing_ench_grup[p : p + 24 + rds]
            p += 24 + rds
    grup_ench = make_grup(
        b"ENCH",
        make_record(b"ENCH", FID_FLIGHT_ENCH, ench_body) + bytes(kept_ench) + extra_ench_rec,
    )
    return grup_perk, grup_mgef, grup_ench


def main(lang: str = "es"):
    lang_norm = (lang or "es").strip().lower()
    if lang_norm not in ("es", "en"):
        raise ValueError(f"Idioma no soportado: {lang!r}. Usa 'es' o 'en'.")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    es_snapshot = os.path.join(base_dir, "release_es", "AeroArmorMod.esp")
    src_esp_path = es_snapshot if os.path.isfile(es_snapshot) else WORKSPACE_ESP
    with open(src_esp_path, "rb") as f:
        esp_data = f.read()

    # Conservar todos los GRUP existentes excepto los que se reconstruyen actualizados
    pos = 0
    tes4_rec = bytearray()
    other_grups = bytearray()
    existing_arma_grup = b""
    existing_armo_grup = b""
    existing_mgef_grup = b""
    existing_ench_grup = b""

    while pos < len(esp_data):
        rt, ds = esp_data[pos : pos + 4], struct.unpack_from("<I", esp_data, pos + 4)[0]
        if rt == b"TES4":
            tes4_rec = bytearray(
                _rewrite_record_cstrs(
                    esp_data[pos : pos + 24 + ds],
                    {
                        b"SNAM": _loc(
                            lang_norm,
                            "Mod de Aero-Armadura y Sistema de Vuelo Libre para Fallout 4.",
                            "The Hubris Legacy: Project Astro-Cosmos - Free-Flight System, Suit, Power Armor, and Campaign for Fallout 4.",
                        )
                    },
                )
            )
            pos += 24 + ds
        elif rt == b"GRUP":
            label = esp_data[pos + 8 : pos + 12]
            if label == b"ARMA":
                existing_arma_grup = esp_data[pos : pos + ds]
            elif label == b"ARMO":
                existing_armo_grup = esp_data[pos : pos + ds]
            elif label == b"MGEF":
                existing_mgef_grup = esp_data[pos : pos + ds]
            elif label == b"ENCH":
                existing_ench_grup = esp_data[pos : pos + ds]
            elif label not in (
                b"KYWD", b"TRNS", b"PERK", b"RACE", b"ARTO", b"OMOD", b"IDLE", b"WEAP", b"ZOOM",
                b"GLOB", b"SOUN", b"ACTI", b"BOOK", b"CONT", b"DOOR", b"MISC", b"FURN", b"NPC_",
                b"NOTE", b"TERM", b"NAVI", b"CELL", b"WRLD", b"VTYP", b"LCTN", b"MESG", b"OTFT",
                b"SNDR",
            ):
                grup_chunk = bytearray(esp_data[pos : pos + ds])
                if label == b"STAT":
                    bad_obnd = b"OBND\x0c\x00" + struct.pack("<6h", -2048, -2048, -32, 2048, 2048, 0)
                    clean_obnd = b"OBND\x0c\x00" + struct.pack("<6h", -128, -128, -32, 128, 128, 0)
                    kept_stat = bytearray()
                    sp_stat = 24
                    while sp_stat < len(grup_chunk):
                        sds = struct.unpack_from("<I", grup_chunk, sp_stat + 4)[0]
                        sfid = struct.unpack_from("<I", grup_chunk, sp_stat + 12)[0]
                        if sfid < 0x01001000:
                            kept_stat += bytes(grup_chunk[sp_stat : sp_stat + 24 + sds]).replace(bad_obnd, clean_obnd)
                        sp_stat += 24 + sds
                    grup_chunk = bytearray(make_grup(b"STAT", bytes(kept_stat)))
                elif label == b"QUST":
                    kept_qust = bytearray()
                    qp = 24
                    while qp < len(grup_chunk):
                        qrt = bytes(grup_chunk[qp : qp + 4])
                        qds = struct.unpack_from("<I", grup_chunk, qp + 4)[0]
                        if qrt == b"GRUP":
                            qp += qds
                            continue
                        qfid = struct.unpack_from("<I", grup_chunk, qp + 12)[0]
                        if qfid == 0x01000804:
                            kept_qust += grup_chunk[qp : qp + 24 + qds]
                        qp += 24 + qds
                    if not kept_qust:
                        sname = b"AeroArmorQuestScript"
                        q_vmad = struct.pack("<HHHH", 6, 2, 1, len(sname)) + sname + b"\x00\x00\x00"
                        q_body = (
                            subrec_cstr(b"EDID", "AeroArmorQuest")
                            + subrec(b"VMAD", q_vmad)
                            + subrec(b"DNAM", bytes.fromhex("110100000000000000000000"))
                            + subrec(b"NEXT", b"")
                            + subrec(b"ANAM", struct.pack("<I", 0))
                        )
                        kept_qust += make_record(b"QUST", 0x01000804, q_body)
                    grup_chunk = bytearray(make_grup(b"QUST", bytes(kept_qust)))
                elif label == b"SPEL":
                    new_spel_recs = bytearray()
                    sp_p = 24
                    while sp_p < len(grup_chunk):
                        srds, _, sfid = struct.unpack_from("<III", grup_chunk, sp_p + 4)
                        srec = bytes(grup_chunk[sp_p : sp_p + 24 + srds])
                        if sfid == 0x01000808:
                            srec = _rewrite_record_cstrs(
                                srec,
                                {
                                    b"FULL": _loc(lang_norm, "Capacidad de Vuelo Aero-Mk-I", "Astro-Cosmos Flight Capability"),
                                    b"DESC": _loc(
                                        lang_norm,
                                        "Habilidad permanente de vuelo compatible con cualquier armadura o Servoarmadura.",
                                        "Active free-flight ability granted by the Astro-Cosmos Flight Suit and Jetpack Power Armor Torso.",
                                    ),
                                },
                            )
                        new_spel_recs += srec
                        sp_p += 24 + srds
                    grup_chunk = bytearray(make_grup(b"SPEL", bytes(new_spel_recs)))
                elif label == b"GMST":
                    old_time_sust = b"EDID\x18\x00fJetpackTimeToSustained\x00DATA\x04\x00" + struct.pack("<f", 60.0)
                    new_time_sust = b"EDID\x18\x00fJetpackTimeToSustained\x00DATA\x04\x00" + struct.pack("<f", 0.1)
                    old_thrust_sust = b"EDID\x18\x00fJetpackThrustSustained\x00DATA\x04\x00" + struct.pack("<f", 380.0)
                    new_thrust_sust = b"EDID\x18\x00fJetpackThrustSustained\x00DATA\x04\x00" + struct.pack("<f", 190.0)
                    grup_chunk = bytearray(
                        bytes(grup_chunk)
                        .replace(old_time_sust, new_time_sust)
                        .replace(old_thrust_sust, new_thrust_sust)
                    )
                elif label == b"COBJ":
                    def make_ctda_stage_ge(stage_val: float) -> bytes:
                        # GetStage (func=58) sobre 0x01004000 >= stage_val (op=0x60)
                        return subrec(
                            b"CTDA",
                            struct.pack("<B3sfHHIIIIi", 0x60, b"\x00\x00\x00", float(stage_val), 58, 0, 0x01004000, 0, 0, 0, -1),
                        )

                    pa_cobj_fids = {
                        FID_COBJ_PA_TORSO,
                        FID_COBJ_PA_HELM,
                        FID_COBJ_PA_LARM,
                        FID_COBJ_PA_RARM,
                        FID_COBJ_PA_LLEG,
                        FID_COBJ_PA_RLEG,
                        FID_COBJ_HERO_WEAP,
                        FID_COBJ_PA_WEAP,
                    }
                    new_cobj_recs = bytearray()
                    cp = 24
                    while cp < len(grup_chunk):
                        crds, cfl, cfid = struct.unpack_from("<III", grup_chunk, cp + 4)
                        if cfid == FID_COBJ_SUIT:
                            crb = grup_chunk[cp + 24 : cp + 24 + crds]
                            out_crb = bytearray()
                            csp = 0
                            while csp + 6 <= len(crb):
                                cst = crb[csp : csp + 4]
                                csz = struct.unpack_from("<H", crb, csp + 4)[0]
                                if cst == b"CTDA":
                                    pass
                                elif cst == b"DESC":
                                    out_crb += subrec_cstr(
                                        b"DESC",
                                        _loc(
                                            lang_norm,
                                            "Sintetiza el Traje de Vuelo Astro-Cosmos con capa 3D y escudo antirradiacion (100% inmunidad).",
                                            "Synthesize the Astro-Cosmos Flight Suit with 3D cape and cosmic anti-radiation shield (100% immunity).",
                                        ),
                                    )
                                    out_crb += make_ctda_stage_ge(35.0)
                                else:
                                    out_crb += crb[csp : csp + 6 + csz]
                                csp += 6 + csz
                            new_cobj_recs += make_record(b"COBJ", cfid, bytes(out_crb), cfl)
                        elif cfid == 0x01000806:
                            new_cobj_recs += _rewrite_record_cstrs(
                                bytes(grup_chunk[cp : cp + 24 + crds]),
                                {
                                    b"DESC": _loc(
                                        lang_norm,
                                        "Construye el Anillo Propulsor Aero-Mk-I (Slot 55 compatible con todo).",
                                        "Craft the legacy Aero-Mk-I Thruster Ring (Slot 55).",
                                    )
                                },
                            )
                        elif cfid not in pa_cobj_fids:
                            new_cobj_recs += grup_chunk[cp : cp + 24 + crds]
                        cp += 24 + crds

                    # Añadir recetas de la Servoarmadura Astro-Cosmos y de las Armas Aéreas Astro-Cosmos con bloqueo por etapa de campaña
                    pa_cobj_specs = [
                        (
                            FID_COBJ_PA_TORSO,
                            "co_AeroArmor_CosmosPA_Torso",
                            FID_COSMOS_PA_TORSO,
                            _loc(
                                lang_norm,
                                "Forja el Torso Propulsor Astro-Cosmos (pieza motora de vuelo e inmunidad a radiacion).",
                                "Forge the Astro-Cosmos Jetpack Torso (flight thruster core and full radiation immunity).",
                            ),
                            110.0,
                        ),
                        (
                            FID_COBJ_PA_HELM,
                            "co_AeroArmor_CosmosPA_Helm",
                            FID_COSMOS_PA_HELM,
                            _loc(
                                lang_norm,
                                "Forja el Casco Astro-Cosmos: escafandra esferica de buzo espacial estilo Capitan Cosmos con mirilla circular y faro frontal.",
                                "Forge the Astro-Cosmos Helmet: spherical Captain Cosmos space-diver dome with circular viewport and headlamp.",
                            ),
                            110.0,
                        ),
                        (
                            FID_COBJ_PA_LARM,
                            "co_AeroArmor_CosmosPA_ArmLeft",
                            FID_COSMOS_PA_LARM,
                            _loc(
                                lang_norm,
                                "Forja el Brazo Izquierdo de la Servoarmadura Astro-Cosmos.",
                                "Forge the Astro-Cosmos Power Armor Left Arm.",
                            ),
                            110.0,
                        ),
                        (
                            FID_COBJ_PA_RARM,
                            "co_AeroArmor_CosmosPA_ArmRight",
                            FID_COSMOS_PA_RARM,
                            _loc(
                                lang_norm,
                                "Forja el Brazo Derecho de la Servoarmadura Astro-Cosmos.",
                                "Forge the Astro-Cosmos Power Armor Right Arm.",
                            ),
                            110.0,
                        ),
                        (
                            FID_COBJ_PA_LLEG,
                            "co_AeroArmor_CosmosPA_LegLeft",
                            FID_COSMOS_PA_LLEG,
                            _loc(
                                lang_norm,
                                "Forja la Pierna Izquierda de la Servoarmadura Astro-Cosmos.",
                                "Forge the Astro-Cosmos Power Armor Left Leg.",
                            ),
                            110.0,
                        ),
                        (
                            FID_COBJ_PA_RLEG,
                            "co_AeroArmor_CosmosPA_LegRight",
                            FID_COSMOS_PA_RLEG,
                            _loc(
                                lang_norm,
                                "Forja la Pierna Derecha de la Servoarmadura Astro-Cosmos.",
                                "Forge the Astro-Cosmos Power Armor Right Leg.",
                            ),
                            110.0,
                        ),
                        (
                            FID_COBJ_HERO_WEAP,
                            "co_AeroArmor_CosmosHeroCarbine",
                            FID_COSMOS_HERO_WEAP,
                            _loc(
                                lang_norm,
                                "Sintetiza la Carabina de Rayos Astro-Cosmos con mira de reconocimiento 6x (compatible en vuelo con el Traje y la Servoarmadura Astro-Cosmos).",
                                "Synthesize the Astro-Cosmos Ray Carbine with 6x recon scope (flight-compatible with Astro-Cosmos Suit and Power Armor).",
                            ),
                            65.0,
                        ),
                        (
                            FID_COBJ_PA_WEAP,
                            "co_AeroArmor_CosmosPACannon",
                            FID_COSMOS_PA_WEAP,
                            _loc(
                                lang_norm,
                                "Forja el Canon Orbital Gauss Astro-Cosmos con mira orbital 8x (compatible en vuelo con la Servoarmadura y el Traje Astro-Cosmos).",
                                "Forge the Astro-Cosmos Orbital Gauss Cannon with 8x orbital scope (flight-compatible with Astro-Cosmos Power Armor and Suit).",
                            ),
                            165.0,
                        ),
                    ]
                    for cfid_new, cedid, cnam_fid, cdesc, req_stage in pa_cobj_specs:
                        cbody = (
                            subrec_cstr(b"EDID", cedid)
                            + subrec(b"FVPA", struct.pack("<II", 0x0001FAB4, 2))
                            + subrec_cstr(b"DESC", cdesc)
                            + make_ctda_stage_ge(req_stage)
                            + subrec(b"CNAM", struct.pack("<I", cnam_fid))
                            + subrec(b"BNAM", struct.pack("<I", 0x00102158))
                            + subrec(b"FNAM", struct.pack("<I", 0x0006980C))
                            + subrec(b"INTV", struct.pack("<I", 1))
                        )
                        new_cobj_recs += make_record(b"COBJ", cfid_new, cbody)

                    grup_chunk = bytearray(make_grup(b"COBJ", bytes(new_cobj_recs)))
                other_grups += grup_chunk
            pos += ds
        else:
            pos += 24 + ds

    # Construir GRUP KYWD
    kywd_records = (
        make_kywd_record(FID_FLIGHT_ARCH_KW, "AeroArmor_FlightArchetypeKw", 7)
        + make_kywd_record(FID_DESCENT_ARCH_KW, "AeroArmor_DescentArchetypeKw", 7)
        + make_kywd_record(FID_FLIGHT_FLAV_KW, "AeroArmor_FlightFlavorKw", 13)
        + make_kywd_record(FID_DESCENT_FLAV_KW, "AeroArmor_DescentFlavorKw", 13)
        + make_kywd_record(FID_COSMOS_PA_TORSO_KW, "AeroArmor_CosmosPATorsoKw", 0)
        + make_kywd_record(FID_COSMOS_HERO_WEAP_KW, "AeroArmor_CosmosHeroWeapKw", 0)
        + make_kywd_record(FID_MA_COSMOS_CARBINE_KW, "ma_CosmosHeroCarbine", 5)
        + make_kywd_record(FID_COSMOS_PA_WEAP_KW, "AeroArmor_CosmosPAWeapKw", 0)
        + make_kywd_record(FID_MA_COSMOS_PA_CANNON_KW, "ma_CosmosPACannon", 5)
    )
    grup_kywd = make_grup(b"KYWD", kywd_records)

    # Construir GRUP TRNS (encuadre completo de inspección RS en Pip-Boy para Carabina y Cañón Orbital)
    trns_carbine_body = (
        subrec_cstr(b"EDID", "xTranCosmosHeroCarbine")
        + subrec(
            b"DATA",
            struct.pack("<9f", 10.0, 290.0, -1.5, 0.0, 0.0, 4.712389, 0.92, -1.0, 2.0),
        )
    )
    trns_pa_cannon_body = (
        subrec_cstr(b"EDID", "xTranCosmosPACannon")
        + subrec(
            b"DATA",
            struct.pack("<9f", 23.5, 325.0, -2.0, 0.0, 0.0, 4.712389, 0.86, -1.0, 2.0),
        )
    )
    grup_trns = make_grup(
        b"TRNS",
        make_record(b"TRNS", FID_COSMOS_WEAP_TRNS, trns_carbine_body)
        + make_record(b"TRNS", FID_COSMOS_PA_WEAP_TRNS, trns_pa_cannon_body),
    )

    # Construir registros de la Carabina de Rayos Astro-Cosmos y del Cañón Orbital Gauss Astro-Cosmos
    rec_carbine_mgef, rec_carbine_ench, carbine_omod_records, rec_carbine_weap, rec_carbine_zoom = (
        build_cosmos_hero_carbine_records(lang_norm)
    )
    rec_cannon_mgef, rec_cannon_ench, cannon_omod_records, rec_cannon_weap, rec_cannon_zoom = (
        build_cosmos_pa_cannon_records(lang_norm)
    )
    grup_weap = make_grup(b"WEAP", rec_carbine_weap + rec_cannon_weap)
    grup_amdl = build_cosmos_aim_model_grup()
    grup_zoom = make_grup(b"ZOOM", rec_carbine_zoom + rec_cannon_zoom)

    # Construir GRUP PERK, GRUP MGEF y GRUP ENCH (Escudo Antirradiación + Carabina Fotónica + Cañón Orbital)
    grup_perk, grup_mgef, grup_ench = build_cosmic_rad_shield_grups(
        existing_mgef_grup,
        existing_ench_grup,
        extra_mgef_rec=rec_carbine_mgef + rec_cannon_mgef,
        extra_ench_rec=rec_carbine_ench + rec_cannon_ench,
        lang=lang_norm,
    )

    # Construir GRUP ARMA, GRUP ARMO y GRUP OMOD (Traje + Servoarmadura + Carabina + Cañón Orbital)
    grup_arma, grup_armo, pa_omod_records = build_cosmos_hero_arma_and_armo_records(
        existing_arma_grup, existing_armo_grup, lang=lang_norm
    )
    grup_omod = make_grup(b"OMOD", pa_omod_records + carbine_omod_records + cannon_omod_records)

    # Construir GRUP RACE (HumanRaceSubGraphData + aditivos de Humano y Servoarmadura para vuelo y retorno instantáneo a tierra)
    human_w_blocks, pa_w_blocks = extract_weapon_blocks_from_esm()
    print(f"Bloques de armas extraidos: Human={len(human_w_blocks)}, PowerArmor={len(pa_w_blocks)}")
    race_records = (
        build_vanilla_race_overrides(lang_norm)
        + build_human_additive_race(human_w_blocks)
        + build_pa_additive_race(pa_w_blocks)
    )
    grup_race = make_grup(b"RACE", race_records)
    grup_idle = build_pa_flavor_idle_grup()

    # Extraer GRUPs restantes en mapa por etiqueta y ordenar según el orden canónico de Fallout4.esm
    other_map = {}
    opos = 0
    while opos < len(other_grups):
        ogs = struct.unpack_from("<I", other_grups, opos + 4)[0]
        olbl = bytes(other_grups[opos + 8 : opos + 12])
        other_map[olbl] = bytes(other_grups[opos : opos + ogs])
        opos += ogs

    orbita7_grups = build_orbita7_esp_grups(lang=lang_norm)

    # Fusionar GRUP STAT (HoverPlatform + estáticos de Órbita-7) y GRUP QUST (AeroArmorQuest + HubrisOrbita7Quest)
    merged_stat_payload = other_map.get(b"STAT", b"")[24:] + orbita7_grups[b"STAT"][24:]
    merged_qust_payload = other_map.get(b"QUST", b"")[24:] + orbita7_grups[b"QUST"][24:]

    grup_map = {
        b"GMST": other_map.get(b"GMST", b""),
        b"KYWD": grup_kywd,
        b"TRNS": grup_trns,
        b"GLOB": orbita7_grups[b"GLOB"],
        b"SOUN": orbita7_grups[b"SOUN"],
        b"RACE": grup_race,
        b"MGEF": grup_mgef,
        b"ENCH": grup_ench,
        b"SPEL": other_map.get(b"SPEL", b""),
        b"ACTI": orbita7_grups[b"ACTI"],
        b"ARMO": grup_armo,
        b"BOOK": orbita7_grups[b"BOOK"],
        b"CONT": orbita7_grups[b"CONT"],
        b"DOOR": orbita7_grups[b"DOOR"],
        b"LIGH": orbita7_grups[b"LIGH"],
        b"MISC": orbita7_grups[b"MISC"],
        b"STAT": make_grup(b"STAT", merged_stat_payload),
        b"FURN": orbita7_grups[b"FURN"],
        b"WEAP": grup_weap,
        b"NPC_": orbita7_grups[b"NPC_"],
        b"NOTE": orbita7_grups[b"NOTE"],
        b"TERM": orbita7_grups[b"TERM"],
        b"NAVI": orbita7_grups[b"NAVI"],
        b"CELL": orbita7_grups[b"CELL"],
        b"WRLD": orbita7_grups[b"WRLD"],
        b"QUST": make_grup(b"QUST", merged_qust_payload),
        b"IDLE": grup_idle,
        b"PERK": grup_perk,
        b"VTYP": orbita7_grups[b"VTYP"],
        b"ARMA": grup_arma,
        b"LCTN": orbita7_grups[b"LCTN"],
        b"MESG": orbita7_grups[b"MESG"],
        b"SNDR": orbita7_grups[b"SNDR"],
        b"OTFT": orbita7_grups[b"OTFT"],
        b"AMDL": grup_amdl,
        b"COBJ": other_map.get(b"COBJ", b""),
        b"OMOD": grup_omod,
        b"ZOOM": grup_zoom,
    }
    canonical_order = [
        b"GMST", b"KYWD", b"TRNS", b"GLOB", b"RACE", b"SOUN", b"MGEF", b"ENCH", b"SPEL",
        b"ACTI", b"ARMO", b"BOOK", b"CONT", b"DOOR", b"LIGH", b"MISC", b"STAT", b"FURN",
        b"WEAP", b"NPC_", b"NOTE", b"TERM", b"NAVI", b"CELL", b"WRLD", b"QUST",
        b"IDLE", b"PERK", b"VTYP", b"ARMA", b"LCTN", b"MESG", b"SNDR", b"OTFT", b"ARTO",
        b"AMDL", b"COBJ", b"OMOD", b"ZOOM",
    ]
    for extra_lbl in other_map:
        if extra_lbl not in grup_map:
            grup_map[extra_lbl] = other_map[extra_lbl]
            canonical_order.append(extra_lbl)

    all_grups = b"".join(grup_map[k] for k in canonical_order if grup_map.get(k))
    item_count = count_esp_items(all_grups)

    # En TES4, HEDR está al principio del body (offset 24 + 6) -> Establecer HEDR v1.0 (compatible con 1.10.163 y Next-Gen)
    struct.pack_into("<HH", tes4_rec, 20, 131, 0)
    struct.pack_into("<f", tes4_rec, 30, 1.0)
    hedr_ver = struct.unpack_from("<f", tes4_rec, 30)[0]
    struct.pack_into("<I", tes4_rec, 34, item_count)
    struct.pack_into("<I", tes4_rec, 38, 0x005000)  # Next Object ID

    final_esp = bytes(tes4_rec) + all_grups
    release_dir = os.path.join(base_dir, f"release_{lang_norm}")
    os.makedirs(release_dir, exist_ok=True)
    release_esp = os.path.join(release_dir, "AeroArmorMod.esp")
    with open(release_esp, "wb") as f:
        f.write(final_esp)
    with open(WORKSPACE_ESP, "wb") as f:
        f.write(final_esp)

    # Sincronizar voces, WAV de examen, meshes/materials/textures de Órbita-7 y scripts (.pex/.psc) hacia Data\
    locked_files: list[str] = []
    deployed_count = 0

    def _copy_matching_dir(src_dir: str, dst_dir: str, ext: str, prefix: str = "") -> None:
        nonlocal deployed_count
        if not os.path.isdir(src_dir):
            return
        os.makedirs(dst_dir, exist_ok=True)
        for fn in sorted(os.listdir(src_dir)):
            if prefix and not fn.startswith(prefix):
                continue
            if not fn.lower().endswith(ext.lower()):
                continue
            src_p = os.path.join(src_dir, fn)
            dst_p = os.path.join(dst_dir, fn)
            if not os.path.isfile(src_p):
                continue
            try:
                shutil.copy2(src_p, dst_p)
                deployed_count += 1
            except PermissionError:
                locked_files.append(dst_p)
                print(f"[AVISO] Archivo en uso al copiar {fn} (Fallout 4 abierto).")

    voices_root = os.path.join(base_dir, f"orbita7_voices_{lang_norm}")
    if os.path.isdir(voices_root):
        for vtyp_dir in sorted(os.listdir(voices_root)):
            sub_src = os.path.join(voices_root, vtyp_dir)
            if not os.path.isdir(sub_src):
                continue
            sub_dst = os.path.join(FO4_DATA_DIR, "Sound", "Voice", "AeroArmorMod.esp", vtyp_dir)
            _copy_matching_dir(sub_src, sub_dst, ".fuz")
            _copy_matching_dir(sub_src, sub_dst, ".xwm")

    _copy_matching_dir(
        os.path.join(base_dir, f"orbita7_exam_audio_{lang_norm}"),
        os.path.join(FO4_DATA_DIR, "Sound", "FX", "AeroArmor", "Orbita7"),
        ".wav",
    )
    _copy_matching_dir(
        os.path.join(base_dir, "orbita7_studio_assets", "Meshes", "AeroArmor", "Orbita7"),
        os.path.join(FO4_DATA_DIR, "Meshes", "AeroArmor", "Orbita7"),
        ".nif",
    )
    _copy_matching_dir(
        os.path.join(base_dir, "orbita7_studio_assets", "Materials", "AeroArmor", "Orbita7"),
        os.path.join(FO4_DATA_DIR, "Materials", "AeroArmor", "Orbita7"),
        ".bgsm",
    )
    _copy_matching_dir(
        os.path.join(base_dir, "orbita7_studio_assets", "Textures", "AeroArmor", "Orbita7"),
        os.path.join(FO4_DATA_DIR, "Textures", "AeroArmor", "Orbita7"),
        ".dds",
    )
    if lang_norm == "en":
        _copy_matching_dir(
            os.path.join(base_dir, "orbita7_studio_assets_en", "Textures", "AeroArmor", "Orbita7"),
            os.path.join(FO4_DATA_DIR, "Textures", "AeroArmor", "Orbita7"),
            ".dds",
        )

    _copy_matching_dir(
        os.path.join(base_dir, "meshes", "AeroArmor"),
        os.path.join(FO4_DATA_DIR, "Meshes", "AeroArmor"),
        ".nif",
        prefix="HoverPlatform.nif",
    )

    scripts_dir = os.path.join(base_dir, "scripts_en" if lang_norm == "en" else "scripts")
    for pfx in ("AeroArmor", "AeroCosmos", "HubrisOrbita7"):
        _copy_matching_dir(scripts_dir, os.path.join(FO4_DATA_DIR, "Scripts"), ".pex", prefix=pfx)
        _copy_matching_dir(scripts_dir, os.path.join(FO4_DATA_DIR, "Scripts", "Source", "User"), ".psc", prefix=pfx)

    try:
        shutil.copy2(release_esp, DATA_ESP)
        deployed_count += 1
        print(
            f"[OK:{lang_norm.upper()}] AeroArmorMod.esp actualizado e instalado en Data ({len(final_esp)} bytes, "
            f"HEDR v{hedr_ver:.2f}, {item_count} total items; {deployed_count} archivos sincronizados, "
            f"{len(locked_files)} bloqueados)."
        )
    except PermissionError:
        locked_files.append(DATA_ESP)
        print(
            f"[AVISO:{lang_norm.upper()}] AeroArmorMod.esp generado en {release_esp} ({len(final_esp)} bytes), "
            f"pero Fallout 4 está abierto y bloquea {DATA_ESP}. "
            f"Cierra el juego y vuelve a ejecutar `python update_aero_esp.py --lang {lang_norm}` "
            f"(locked_files={len(locked_files)})."
        )
    if locked_files:
        print(f"[BLOQUEADOS] {len(locked_files)} archivo(s) en uso: {locked_files}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Genera e instala AeroArmorMod.esp (ES / EN).")
    parser.add_argument("--lang", choices=("es", "en"), default="es", help="Idioma objetivo (es | en).")
    args = parser.parse_args()
    main(lang=args.lang)
