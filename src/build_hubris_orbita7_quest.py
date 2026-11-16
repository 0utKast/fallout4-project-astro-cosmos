"""Generador completo del arco narrativo y escenario «Estudio Subterráneo Órbita-7»
para `AeroArmorMod.esp` (El Legado de Hubris: Proyecto Astro-Cosmos — Versión Local ES).

Contiene dos módulos principales invocables por separado o desde `update_aero_esp.py`:
  1. `synthesize_orbita7_voices()`: sintetiza vía ElevenLabs (`eleven_multilingual_v2`),
     procesa con filtros de carácter en `ffmpeg` (Coronel Agallas radio metálica, Clara
     Sterling holocinta 2077, Artie Vance necrófago cálido y Protagonista Masculino/Femenino),
     codifica con `xwmaencode.exe` y empaqueta `.fuz` + `.xwm` con sincronización labial 30 fps.
  2. `build_orbita7_esp_grups()`: extrae las plantillas base verificadas de `Fallout4.esm`
     (100% standalone, cero dependencias de Creation Club / DLCs) y construye todos los
     `GRUP` de Órbita-7 (`GLOB`, `VTYP`, `LCTN`, `OTFT`, `STAT`, `ACTI`, `DOOR`, `FURN`, `TERM`,
     `MISC`, `BOOK`, `CONT`, `NPC_`, `MESG`, `NOTE`, `QUST`+`DIAL`/`INFO`/`SCEN`, `CELL` interior
     `0x01002000` + `NAVM 0x010020FF`, `NAVI 0x00000FF1` y `WRLD 0x0000003C` celda persistente).

Uso CLI:
  python build_hubris_orbita7_quest.py --voices
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import io
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import wave
import zlib

import hubris_orbita7_data_es as d

ROOT_DIR = Path(__file__).resolve().parent
FALLOUT4_DATA_DIR = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Fallout 4\Data")
FALLOUT4_ESM_PATH = FALLOUT4_DATA_DIR / "Fallout4.esm"
VOICE_CACHE_ROOT = ROOT_DIR / "orbita7_voices_es"
VOICE_DATA_ROOT = FALLOUT4_DATA_DIR / "Sound" / "Voice" / "AeroArmorMod.esp"
EXAM_AUDIO_CACHE_DIR = ROOT_DIR / "orbita7_exam_audio_es"
DATA_SFX_ORBITA7_DIR = FALLOUT4_DATA_DIR / "Sound" / "FX" / "AeroArmor" / "Orbita7"
ESP_NAME = "AeroArmorMod.esp"

EN_CORONEL_SHRILL_AF = (
    "aresample=44100,asetrate=44100*1.18,aresample=44100,atempo=0.88,"
    "highpass=f=580:poles=2,lowpass=f=4400:poles=2,"
    "equalizer=f=1850:width_type=q:width=2.2:g=7.5,"
    "equalizer=f=2950:width_type=q:width=2.5:g=6.5,"
    "aecho=0.8:0.85:11:0.24,"
    "acrusher=level_in=1.35:level_out=1.0:bits=10:mode=log:aa=1,"
    "acompressor=threshold=-20dB:ratio=6:attack=3:release=45:makeup=5.5dB,"
    "alimiter=limit=0.92"
)


def _normalize_lang(lang: str | None) -> str:
    """Normaliza el código de idioma a `'es'` o `'en'`."""
    norm = (lang or "es").strip().lower()
    if norm not in ("es", "en"):
        raise ValueError(f"Idioma no soportado: {lang!r}. Usa 'es' o 'en'.")
    return norm


def _get_data_module(lang: str = "es"):
    """Devuelve el módulo de datos narrativos de Órbita-7 para `'es'` o `'en'`."""
    if _normalize_lang(lang) == "en":
        import hubris_orbita7_data_en as d_en
        return d_en
    return d


def _get_voice_dirs(lang: str = "es") -> tuple[Path, Path]:
    """Devuelve `(voice_cache_root, exam_audio_cache_dir)` según idioma."""
    lang_norm = _normalize_lang(lang)
    return (
        ROOT_DIR / f"orbita7_voices_{lang_norm}",
        ROOT_DIR / f"orbita7_exam_audio_{lang_norm}",
    )

# FormIDs del mod compartidos con Papyrus (`scripts/HubrisOrbita7*.psc`) y `update_aero_esp.py`
FID_FLIGHT_SUIT = 0x01000800
FID_FLIGHT_QUEST = 0x01000803
FID_HERO_CARBINE = 0x01000840
FID_PA_CANNON = 0x01000850
FID_COSMOS_PA_PIECES = (
    0x01000820,  # AeroArmor_CosmosPA_Torso
    0x01000821,  # AeroArmor_CosmosPA_Helm
    0x01000822,  # AeroArmor_CosmosPA_ArmLeft
    0x01000823,  # AeroArmor_CosmosPA_ArmRight
    0x01000824,  # AeroArmor_CosmosPA_LegLeft
    0x01000825,  # AeroArmor_CosmosPA_LegRight
)

FID_GLOB_BARK = 0x01001001
FID_GLOB_EXAM = 0x01001002
FID_GLOB_COILS = 0x01001003
FID_GLOB_PA_RESTORED = 0x01001004
FID_GLOB_MURAL = 0x01001005

FID_VTYP_ARTIE = 0x01001020
FID_VTYP_CORONEL = 0x01001021
FID_VTYP_CLARA = 0x01001022
FID_VTYP_PLAYER_M = 0x00018DF4  # Fallout4.esm PlayerVoiceMale01
FID_VTYP_PLAYER_F = 0x00018DF7  # Fallout4.esm PlayerVoiceFemale01

FID_LCTN_ORBITA7 = 0x01001030
FID_OTFT_ARTIE = 0x01001040

FID_STAT_HALL = 0x01001100
FID_STAT_PLANETARIUM = 0x01001101
FID_STAT_GANTRY = 0x01001102
FID_STAT_DESK = 0x01001103
FID_STAT_BED_SHOW = 0x01001104
FID_STAT_CARB_DISP = 0x01001105
FID_STAT_CANNON_DISP = 0x01001106
FID_STAT_BARRIER = 0x01001107
FID_STAT_EXT_PLINTH = 0x01001058

FID_LIGH_STUDIO_WARM = 0x01001095
FID_LIGH_STUDIO_CLEAN = 0x01001096
FID_LIGH_STUDIO_CYAN = 0x01001097

FID_ACTI_VITRINE1 = 0x01001110
FID_ACTI_VITRINE2 = 0x01001111
FID_ACTI_DESK = 0x01001112
FID_ACTI_MURAL = 0x01001113
FID_ACTI_EXAM_CONSOLE = 0x01001114
FID_ACTI_SUIT_POD = 0x01001115
FID_ACTI_WEAP_PED = 0x01001116
FID_ACTI_SOLAR_REL = 0x01001117

FID_DOOR_EXT_HATCH = 0x01001120
FID_DOOR_INT_EXIT = 0x01001121

FID_FURN_PA_FRAME = 0x01001130
FID_FURN_DIRECTOR_BED = 0x01001131

FID_TERM_PROD_TV = 0x01001140
FID_TERM_ARTIE_LAB = 0x01001141
FID_TERM_EXAM_MAIN = 0x01001500

FID_MISC_COIL1 = 0x01001150
FID_MISC_COIL2 = 0x01001151
FID_MISC_COIL3 = 0x01001152
FID_MISC_GYRO = 0x01001153
FID_MISC_CARD = 0x01001154

FID_CONT_SAFE_CHEST = 0x01001170
FID_CONT_HUBRIS = 0x01001171
FID_CONT_TRINITY = 0x01001172
FID_CONT_WRVR = 0x01001173
FID_CONT_ARCJET = 0x01001174
FID_CONT_FORT_HAGEN = 0x01001175

FID_NPC_CORONEL = 0x01001200
FID_NPC_ARTIE = 0x01001201
FID_NPC_CLARA = 0x01001202
FID_NPC_SENTINEL_AJ = 0x01001203
FID_NPC_GUARDIAN_AJ = 0x01001204
FID_NPC_AUTOMATA_FH = 0x01001205

FID_CELL_INT = 0x01002000
FID_NAVM_INT = 0x010020FF

FID_QUST_ORBITA7 = 0x01004000
FID_DIAL_ARTIE_GREE = 0x01004001
FID_DIAL_CORONEL_GREE = 0x01004002
FID_DIAL_CORONEL_BARK = 0x01004003


# ---------------------------------------------------------------------------
# Utilidades binarias ESP / subregistros / VMAD / CTDA
# ---------------------------------------------------------------------------

def subrec(tag: bytes, payload: bytes) -> bytes:
    """Empaqueta un subregistro Fallout 4 estándar (`uint16` size)."""
    if len(payload) > 0xFFFF:
        return b"XXXX" + struct.pack("<HI", 4, len(payload)) + tag + struct.pack("<H", 0) + payload
    return tag + struct.pack("<H", len(payload)) + payload


def subrec_cstr(tag: bytes, text: str) -> bytes:
    """Empaqueta una cadena terminada en NUL (UTF-8) en un subregistro."""
    return subrec(tag, text.encode("utf-8") + b"\x00")


def make_record(
    rtype: bytes,
    fid: int,
    body: bytes,
    flags: int = 0,
    fver: int = 131,
    v2: int = 0,
) -> bytes:
    """Empaqueta un registro completo Fallout 4."""
    return rtype + struct.pack("<IIIIHH", len(body), flags, fid, 0, fver, v2) + body


def make_grup(label: bytes | int, body: bytes, group_type: int = 0) -> bytes:
    """Empaqueta un contenedor `GRUP` Fallout 4."""
    lbl_bytes = label if isinstance(label, (bytes, bytearray)) else struct.pack("<I", int(label))
    return b"GRUP" + struct.pack("<I", 24 + len(body)) + lbl_bytes + struct.pack("<III", group_type, 0, 0) + body


def parse_subrecords(body: bytes) -> list[tuple[bytes, bytes]]:
    """Deserializa todos los subregistros de un cuerpo de registro, soportando `XXXX`."""
    out: list[tuple[bytes, bytes]] = []
    pos = 0
    ext_sz: int | None = None
    n = len(body)
    while pos + 6 <= n:
        tag = body[pos : pos + 4]
        sz = struct.unpack_from("<H", body, pos + 4)[0]
        pos += 6
        if tag == b"XXXX":
            ext_sz = struct.unpack_from("<I", body, pos)[0]
            pos += sz
            continue
        if ext_sz is not None:
            sz = ext_sz
            ext_sz = None
        out.append((tag, body[pos : pos + sz]))
        pos += sz
    return out


def rebuild_subrecords(subs: list[tuple[bytes, bytes]]) -> bytes:
    """Reconstruye el cuerpo binario de una lista de subregistros."""
    return b"".join(subrec(tag, payload) for tag, payload in subs)


def build_simple_vmad(script_name: str, props: list[tuple[str, int, bytes]] | None = None) -> bytes:
    """Construye un subregistro `VMAD` v6 (formato de objeto v2) con un script Papyrus."""
    prop_list = props or []
    sname_b = script_name.encode("utf-8")
    buf = bytearray(struct.pack("<HHH", 6, 2, 1))
    buf += struct.pack("<H", len(sname_b)) + sname_b + struct.pack("<BH", 0, len(prop_list))
    for pname, ptype, pdata in prop_list:
        pname_b = pname.encode("utf-8")
        buf += struct.pack("<H", len(pname_b)) + pname_b + struct.pack("<BB", ptype, 1) + pdata
    return bytes(buf)


def append_vmad_script(raw_vmad: bytes, script_name: str) -> bytes:
    """Añade un script sin propiedades al `VMAD` v6 existente de un registro plantilla."""
    ver, objfmt, scount = struct.unpack_from("<HHH", raw_vmad, 0)
    sname_b = script_name.encode("utf-8")
    return (
        struct.pack("<HHH", ver, objfmt, scount + 1)
        + raw_vmad[6:]
        + struct.pack("<H", len(sname_b))
        + sname_b
        + struct.pack("<BH", 0, 0)
    )


def make_ctda(
    op_byte: int,
    cmp_val: float,
    func_id: int,
    param1: int = 0,
    param2: int = 0,
    run_on: int = 0,
    ref_fid: int = 0,
) -> bytes:
    """Construye un subregistro `CTDA` de 32 bytes exactos."""
    return struct.pack(
        "<B3sfHHIIiiI" if False else "<B3sfHHIIIIi",
        op_byte & 0xFF,
        b"\x00\x00\x00",
        float(cmp_val),
        func_id & 0xFFFF,
        0,
        param1 & 0xFFFFFFFF,
        param2 & 0xFFFFFFFF,
        run_on & 0xFFFFFFFF,
        ref_fid & 0xFFFFFFFF,
        -1,
    )


def make_ctda_getstage(op_byte: int, stage_val: float, quest_fid: int) -> bytes:
    return make_ctda(op_byte, stage_val, 58, quest_fid, 0, 0, 0)


def make_ctda_getglobalvalue(op_byte: int, val: float, glob_fid: int) -> bytes:
    return make_ctda(op_byte, val, 74, glob_fid, 0, 0, 0)


def make_ctda_getisid(npc_fid: int) -> bytes:
    return make_ctda(0x00, 1.0, 72, npc_fid, 0, 0, 0)


def make_ctda_player_sex(sex_val: int) -> bytes:
    # GetPCIsSex (func 70): 0 = Male, 1 = Female
    return make_ctda(0x00, 1.0, 70, sex_val, 0, 0, 0)


def make_ctda_getincell(equal_val: float, cell_fid: int) -> bytes:
    # GetInCell (func 67) sobre PlayerRef (0x00000014, RunOn=2 Reference)
    return make_ctda(0x00, float(equal_val), 67, cell_fid, 0, 2, 0x00000014)


def make_ctda_getincurrentloc(equal_val: float, lctn_fid: int) -> bytes:
    # GetInCurrentLoc (func 359) sobre PlayerRef (0x00000014, RunOn=2 Reference): fiable para celdas .esp sin depender de EDID
    return make_ctda(0x00, float(equal_val), 359, lctn_fid, 0, 2, 0x00000014)


def make_trda_block(resp_idx: int, sub_txt: str) -> bytes:
    """Construye un bloque `TRDA + NAM1..NAM4 + NAM9` de respuesta `INFO`."""
    trda_bytes = bytearray.fromhex("ffffffff0100000000010000ffffffffffffffff")
    trda_bytes[4] = resp_idx & 0xFF
    return (
        subrec(b"TRDA", bytes(trda_bytes))
        + subrec_cstr(b"NAM1", sub_txt)
        + subrec(b"NAM2", b"\x00")
        + subrec(b"NAM3", b"\x00")
        + subrec(b"NAM4", b"\x00")
        + subrec(b"NAM9", bytes.fromhex("40b4b8279d68d801"))
    )


def count_esp_items(buf: bytes) -> int:
    """Cuenta recursivamente todos los `GRUP` y registros a cualquier profundidad."""
    total = 0
    pos = 0
    n = len(buf)
    while pos + 24 <= n:
        rt = buf[pos : pos + 4]
        sz = struct.unpack_from("<I", buf, pos + 4)[0]
        total += 1
        if rt == b"GRUP":
            total += count_esp_items(buf[pos + 24 : pos + sz])
            pos += sz
        else:
            pos += 24 + sz
    return total


# ---------------------------------------------------------------------------
# 1. Pipeline de Síntesis de Voces (ElevenLabs + FFmpeg + XWMAEncode + .fuz)
# ---------------------------------------------------------------------------

def _load_elevenlabs_api_key() -> str:
    """Obtiene `ELEVENLABS_API_KEY` del entorno o del archivo `.env` de la raíz."""
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if key:
        return key
    env_path = ROOT_DIR / ".env"
    if env_path.is_file():
        for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line.startswith("ELEVENLABS_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("No se encontró `ELEVENLABS_API_KEY` en entorno ni en `.env`.")


def _collect_voice_jobs(lang: str = "es") -> list[tuple[str, str, str, int, int, str, str]]:
    """Recopila todas las líneas habladas de Órbita-7 sin duplicados."""
    data_mod = _get_data_module(lang)
    jobs: list[tuple[str, str, str, int, int, str, str]] = []
    seen: set[tuple[str, int, int]] = set()

    def add_job(vtyp: str, vid: str, fkind: str, info_fid: int, resp_idx: int, sub_txt: str, tts_txt: str) -> None:
        key = (vtyp, info_fid & 0xFFFFFF, resp_idx)
        if key not in seen:
            seen.add(key)
            jobs.append((vtyp, vid, fkind, info_fid, resp_idx, sub_txt, tts_txt))

    for g in data_mod.ARTIE_GREETING_INFOS:
        for idx, (sub_t, tts_t) in enumerate(g["responses"], 1):
            add_job(data_mod.ARTIE_VTYP, data_mod.ARTIE_VOICE_ID, "artie", g["info_fid"], idx, sub_t, tts_t)

    for g in data_mod.CORONEL_GREETING_INFOS:
        for idx, (sub_t, tts_t) in enumerate(g["responses"], 1):
            add_job(data_mod.CORONEL_VTYP, data_mod.CORONEL_VOICE_ID, "coronel", g["info_fid"], idx, sub_t, tts_t)

    for b in data_mod.CORONEL_BARK_INFOS:
        for idx, (sub_t, tts_t) in enumerate(b["responses"], 1):
            add_job(data_mod.CORONEL_VTYP, data_mod.CORONEL_VOICE_ID, "coronel", b["info_fid"], idx, sub_t, tts_t)

    for sdef in data_mod.ARTIE_SCENES:
        for act in sdef["actions"]:
            for opt in act["options"]:
                add_job(data_mod.PLAYER_MALE_VTYP, data_mod.PLAYER_MALE_VOICE_ID, "player", opt["p_info"], 1, opt["p_sub"], opt["p_tts"])
                if opt.get("p_info_f"):
                    add_job(
                        data_mod.PLAYER_FEMALE_VTYP,
                        data_mod.PLAYER_FEMALE_VOICE_ID,
                        "player",
                        opt["p_info_f"],
                        1,
                        opt["p_sub_f"],
                        opt["p_tts_f"],
                    )
                else:
                    # Opciones compartidas por ambos sexos necesitan también la pista en PlayerVoiceFemale01
                    add_job(
                        data_mod.PLAYER_FEMALE_VTYP,
                        data_mod.PLAYER_FEMALE_VOICE_ID,
                        "player",
                        opt["p_info"],
                        1,
                        opt["p_sub"],
                        opt["p_tts"],
                    )
                for idx, (sub_t, tts_t) in enumerate(opt["n_responses"], 1):
                    add_job(data_mod.ARTIE_VTYP, data_mod.ARTIE_VOICE_ID, "artie", opt["n_info"], idx, sub_t, tts_t)

    for h in data_mod.CLARA_HOLOTAPES:
        for idx, (sub_t, tts_t) in enumerate(h["responses"], 1):
            add_job(data_mod.CLARA_VTYP, data_mod.CLARA_VOICE_ID, "clara", h["info_fid"], idx, sub_t, tts_t)

    return jobs


def _elevenlabs_tts_mp3(api_key: str, voice_id: str, tts_text: str, fkind: str, lang: str = "es") -> bytes:
    """Solicita síntesis de voz a ElevenLabs (`eleven_multilingual_v2`) en el idioma indicado."""
    lang_norm = _normalize_lang(lang)
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128"
    if fkind == "coronel" and lang_norm == "en":
        settings = {"stability": 0.28, "similarity_boost": 0.76, "style": 0.82, "use_speaker_boost": True}
    elif fkind == "coronel":
        settings = {"stability": 0.38, "similarity_boost": 0.80, "style": 0.55, "use_speaker_boost": True}
    elif fkind == "clara":
        settings = {"stability": 0.50, "similarity_boost": 0.78, "style": 0.30, "use_speaker_boost": True}
    else:
        settings = {"stability": 0.48, "similarity_boost": 0.78, "style": 0.25, "use_speaker_boost": True}

    payload = json.dumps(
        {
            "text": tts_text,
            "model_id": "eleven_multilingual_v2",
            "language_code": lang_norm,
            "voice_settings": settings,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"ElevenLabs HTTP {exc.code} para {voice_id}: {body}") from exc


def _mp3_to_pcm24_wav(mp3_bytes: bytes, fkind: str, lang: str = "es") -> tuple[bytes, float]:
    """Convierte MP3 a WAV PCM 16-bit mono 24 kHz con ecualización según personaje e idioma."""
    lang_norm = _normalize_lang(lang)
    coronel_af = (
        EN_CORONEL_SHRILL_AF
        if lang_norm == "en"
        else "highpass=f=320,lowpass=f=4200,acompressor=threshold=-16dB:ratio=4:makeup=4dB,alimiter=limit=0.92"
    )
    filters = {
        "coronel": coronel_af,
        "clara": "highpass=f=240,lowpass=f=4800,acompressor=threshold=-18dB:ratio=3:makeup=2dB,alimiter=limit=0.92",
        "artie": "highpass=f=110,acompressor=threshold=-18dB:ratio=2.5:makeup=2dB,alimiter=limit=0.92",
        "player": "highpass=f=90,acompressor=threshold=-18dB:ratio=2:makeup=1.5dB,alimiter=limit=0.92",
    }
    af_str = filters.get(fkind, filters["player"])
    with tempfile.TemporaryDirectory(prefix="orbita7_tts_") as tmpdir:
        tmp = Path(tmpdir)
        mp3_p = tmp / "in.mp3"
        wav_p = tmp / "out.wav"
        mp3_p.write_bytes(mp3_bytes)
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
        res = subprocess.run(
            ["ffmpeg", "-y", "-i", str(mp3_p), "-af", af_str, "-ar", "24000", "-ac", "1", "-sample_fmt", "s16", str(wav_p)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=30,
            creationflags=creationflags,
        )
        if res.returncode != 0 or not wav_p.is_file():
            raise RuntimeError(f"FFmpeg falló ({res.returncode}): {res.stderr.decode('utf-8', errors='ignore')[-300:]}")
        wav_bytes = wav_p.read_bytes()
    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        dur_s = max(0.35, wf.getnframes() / float(max(1, wf.getframerate())))
    return wav_bytes, dur_s


def synthesize_orbita7_voices(lang: str = "es") -> int:
    """Sintetiza y despliega todas las líneas de voz `.fuz` + `.xwm` de Órbita-7 en el idioma indicado."""
    lang_norm = _normalize_lang(lang)
    voice_cache_root, _ = _get_voice_dirs(lang_norm)
    sys.path.insert(0, str(ROOT_DIR / "lucy_companion_fo4_es" / "bridge"))
    import lip_sync  # type: ignore

    jobs = _collect_voice_jobs(lang_norm)
    api_key: str | None = None
    generated = 0
    cached = 0

    def _run_one(job: tuple[str, str, str, int, int, str, str], key: str | None) -> tuple[bool, str]:
        vtyp, vid, fkind, info_fid, resp_idx, sub_txt, tts_txt = job
        fname_base = f"{info_fid & 0xFFFFFF:08X}_{resp_idx}"
        cache_dir = voice_cache_root / vtyp
        data_dir = VOICE_DATA_ROOT / vtyp
        cache_dir.mkdir(parents=True, exist_ok=True)
        data_dir.mkdir(parents=True, exist_ok=True)

        c_fuz = cache_dir / f"{fname_base}.fuz"
        c_xwm = cache_dir / f"{fname_base}.xwm"
        d_fuz = data_dir / f"{fname_base}.fuz"
        d_xwm = data_dir / f"{fname_base}.xwm"

        if c_fuz.is_file() and c_fuz.stat().st_size > 200 and c_xwm.is_file() and c_xwm.stat().st_size > 100:
            if not d_fuz.is_file() or d_fuz.stat().st_size != c_fuz.stat().st_size:
                shutil.copy2(c_fuz, d_fuz)
            if not d_xwm.is_file() or d_xwm.stat().st_size != c_xwm.stat().st_size:
                shutil.copy2(c_xwm, d_xwm)
            return False, f"{vtyp}/{fname_base}"

        if not key:
            raise RuntimeError("Falta ELEVENLABS_API_KEY para sintetizar pistas no cacheadas.")

        mp3_bytes = _elevenlabs_tts_mp3(key, vid, tts_txt, fkind, lang_norm)
        wav_bytes, dur_s = _mp3_to_pcm24_wav(mp3_bytes, fkind, lang_norm)
        fuz_bytes, has_audio = lip_sync._generate_waveform_fuz_bytes(
            wav_bytes, sub_txt, dur_s, prefer_true_fuz=True
        )
        if not fuz_bytes or not has_audio or fuz_bytes[:4] != b"FUZE":
            raise RuntimeError(f"Error empaquetando FUZ con audio real para {vtyp}/{fname_base}")
        lip_len = struct.unpack_from("<I", fuz_bytes, 8)[0]
        xwm_bytes = fuz_bytes[12 + lip_len :]
        if len(xwm_bytes) < 64:
            raise RuntimeError(f"Stream XWMA vacío en {vtyp}/{fname_base}")

        c_fuz.write_bytes(fuz_bytes)
        c_xwm.write_bytes(xwm_bytes)
        shutil.copy2(c_fuz, d_fuz)
        shutil.copy2(c_xwm, d_xwm)
        return True, f"{vtyp}/{fname_base} ({dur_s:.2f}s)"

    # Comprobar si hay trabajos sin cache antes de cargar la clave API
    need_api = False
    for vtyp, _vid, _fk, info_fid, resp_idx, _s, _t in jobs:
        fname_base = f"{info_fid & 0xFFFFFF:08X}_{resp_idx}"
        cf = voice_cache_root / vtyp / f"{fname_base}.fuz"
        cx = voice_cache_root / vtyp / f"{fname_base}.xwm"
        if not (cf.is_file() and cf.stat().st_size > 200 and cx.is_file() and cx.stat().st_size > 100):
            need_api = True
            break

    if need_api:
        api_key = _load_elevenlabs_api_key()

    print(f"[ORBITA7-VOZ:{lang_norm.upper()}] Total líneas de diálogo a verificar/sintetizar: {len(jobs)}")
    with ThreadPoolExecutor(max_workers=3) as pool:
        futs = [pool.submit(_run_one, j, api_key) for j in jobs]
        for idx, fut in enumerate(as_completed(futs), 1):
            was_new, label = fut.result()
            if was_new:
                generated += 1
                print(f"  [{idx}/{len(jobs)}] [NEW] {label}")
            else:
                cached += 1
    print(f"[ORBITA7-VOZ:{lang_norm.upper()}] Completado: {generated} sintetizadas, {cached} desde caché -> {VOICE_DATA_ROOT}")
    return len(jobs)


def _elevenlabs_sfx_mp3(api_key: str, prompt: str, duration_seconds: float) -> bytes:
    """Solicita un efecto de sonido a la API Sound Generation de ElevenLabs."""
    url = "https://api.elevenlabs.io/v1/sound-generation"
    payload = json.dumps(
        {
            "text": prompt,
            "duration_seconds": float(duration_seconds),
            "prompt_influence": 0.45,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"ElevenLabs SFX HTTP {exc.code}: {body}") from exc


def _mp3_to_pcm44_wav(mp3_bytes: bytes, kind: str, lang: str = "es") -> tuple[bytes, float]:
    """Convierte MP3 a WAV PCM 16-bit mono 44.1 kHz bitexact para registros SNDR/SOUN."""
    lang_norm = _normalize_lang(lang)
    ffmpeg_bin = shutil.which("ffmpeg") or r"C:\ProgramData\chocolatey\bin\ffmpeg.EXE"
    if kind == "coronel" and lang_norm == "en":
        af_str = EN_CORONEL_SHRILL_AF
    elif kind == "coronel":
        af_str = "highpass=f=320,lowpass=f=4200,acompressor=threshold=-16dB:ratio=4:makeup=5dB,alimiter=limit=0.95"
    else:
        af_str = "highpass=f=50,lowpass=f=14000,acompressor=threshold=-16dB:ratio=3.0:makeup=3.5dB,alimiter=limit=0.88"
    with tempfile.TemporaryDirectory(prefix="orbita7_exam_") as tmpdir:
        tmp = Path(tmpdir)
        mp3_p = tmp / "in.mp3"
        wav_p = tmp / "out.wav"
        mp3_p.write_bytes(mp3_bytes)
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
        res = subprocess.run(
            [
                ffmpeg_bin,
                "-y",
                "-i",
                str(mp3_p),
                "-af",
                af_str,
                "-bitexact",
                "-map_metadata",
                "-1",
                "-ar",
                "44100",
                "-ac",
                "1",
                "-sample_fmt",
                "s16",
                str(wav_p),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=45,
            creationflags=creationflags,
        )
        if res.returncode != 0 or not wav_p.is_file():
            raise RuntimeError(f"FFmpeg WAV 44.1k falló ({res.returncode}): {res.stderr.decode('utf-8', errors='ignore')[-300:]}")
        wav_bytes = wav_p.read_bytes()
    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        dur_s = wf.getnframes() / float(max(1, wf.getframerate()))
    return wav_bytes, dur_s


def synthesize_orbita7_exam_audio(lang: str = "es") -> dict[str, float]:
    """Sintetiza y despliega todas las locuciones y SFX de examen de Órbita-7 en `Sound/FX/AeroArmor/Orbita7/`."""
    lang_norm = _normalize_lang(lang)
    data_mod = _get_data_module(lang_norm)
    _, exam_audio_cache_dir = _get_voice_dirs(lang_norm)
    exam_audio_cache_dir.mkdir(parents=True, exist_ok=True)
    DATA_SFX_ORBITA7_DIR.mkdir(parents=True, exist_ok=True)

    tasks: list[tuple[str, str, str, float]] = []
    for v in data_mod.EXAM_AUDIO_VOICES:
        tasks.append(("voice", v["name"], v["tts"], 0.0))
    for s in data_mod.EXAM_SFX_DEFS:
        tasks.append(("sfx", s["name"], s["prompt"], float(s["duration"])))

    need_api = False
    for kind, fname, sig_text, _dur_req in tasks:
        wav_c = exam_audio_cache_dir / f"{fname}.wav"
        txt_c = exam_audio_cache_dir / f"{fname}.txt"
        if not wav_c.is_file() or wav_c.stat().st_size <= 10240 or not txt_c.is_file() or txt_c.read_text(encoding="utf-8") != sig_text:
            need_api = True
            break

    api_key = _load_elevenlabs_api_key() if need_api else None
    durations: dict[str, float] = {}
    generated = 0
    cached = 0

    def _process(item: tuple[str, str, str, float]) -> tuple[bool, str, float]:
        kind, fname, sig_text, dur_req = item
        wav_c = exam_audio_cache_dir / f"{fname}.wav"
        txt_c = exam_audio_cache_dir / f"{fname}.txt"
        wav_d = DATA_SFX_ORBITA7_DIR / f"{fname}.wav"

        is_cached = (
            wav_c.is_file()
            and wav_c.stat().st_size > 10240
            and txt_c.is_file()
            and txt_c.read_text(encoding="utf-8") == sig_text
        )
        if is_cached:
            with wave.open(str(wav_c), "rb") as wf:
                dur_s = wf.getnframes() / float(max(1, wf.getframerate()))
            try:
                if not wav_d.is_file() or wav_d.stat().st_size != wav_c.stat().st_size:
                    shutil.copy2(wav_c, wav_d)
            except PermissionError:
                pass
            return False, fname, dur_s

        if not api_key:
            raise RuntimeError("Falta ELEVENLABS_API_KEY para sintetizar audio de examen.")
        if kind == "voice":
            mp3_bytes = _elevenlabs_tts_mp3(api_key, data_mod.CORONEL_VOICE_ID, sig_text, "coronel", lang_norm)
            wav_bytes, dur_s = _mp3_to_pcm44_wav(mp3_bytes, "coronel", lang_norm)
        else:
            mp3_bytes = _elevenlabs_sfx_mp3(api_key, sig_text, dur_req)
            wav_bytes, dur_s = _mp3_to_pcm44_wav(mp3_bytes, "sfx", lang_norm)

        wav_c.write_bytes(wav_bytes)
        txt_c.write_text(sig_text, encoding="utf-8")
        try:
            shutil.copy2(wav_c, wav_d)
        except PermissionError:
            pass
        return True, fname, dur_s

    print(f"[ORBITA7-EXAM-AUDIO:{lang_norm.upper()}] Total pistas de examen (voces + SFX) a verificar/sintetizar: {len(tasks)}")
    with ThreadPoolExecutor(max_workers=3) as pool:
        futs = [pool.submit(_process, t) for t in tasks]
        for fut in as_completed(futs):
            was_new, fname, dur_s = fut.result()
            durations[fname] = dur_s
            tag = "[NEW]" if was_new else "[CACHE]"
            if was_new:
                generated += 1
            else:
                cached += 1
            print(f"  {tag} {fname}.wav -> {dur_s:.2f}s")

    print(f"[ORBITA7-EXAM-AUDIO] Completado: {generated} sintetizadas, {cached} en caché -> {DATA_SFX_ORBITA7_DIR}")
    return durations


# ---------------------------------------------------------------------------
# 2. Extractor de plantillas de Fallout4.esm y constructores de registros
# ---------------------------------------------------------------------------

def extract_orbita7_templates() -> dict[str, tuple[int, int, int, bytes] | bytes]:
    """Extrae únicamente los registros plantilla necesarios desde `Fallout4.esm`."""
    if not FALLOUT4_ESM_PATH.is_file():
        raise FileNotFoundError(f"No existe Fallout4.esm en: {FALLOUT4_ESM_PATH}")

    want_records = {
        (b"DOOR", 0x00018FA9): "door_trapdoor",
        (b"DOOR", 0x00022785): "door_utilmetal",
        (b"DOOR", 0x000E1C42): "door_hightech_sm",
        (b"LIGH", 0x000517B0): "ligh_white_ns",
        (b"FURN", 0x00034309): "furn_pa",
        (b"FURN", 0x000AB567): "furn_bed",
        (b"TERM", 0x00099CD0): "term_desk",
        (b"MISC", 0x00154AD2): "misc_circuit",
        (b"MISC", 0x0014FD7D): "misc_idcard",
        (b"NOTE", 0x00225D7B): "note_holo",
        (b"CONT", 0x00018F7B): "cont_locker",
        (b"NPC_", 0x00146CDF): "npc_gutsy",
        (b"NPC_", 0x0021DDBB): "npc_gutsy_gunner01",
        (b"NPC_", 0x0021DDBD): "npc_gutsy_gunner02",
        (b"NPC_", 0x000228AA): "npc_kent",
        (b"SCEN", 0x001C037F): "scen_holo",
        (b"CELL", 0x000CA260): "cell_v111",
        (b"CELL", 0x00018AA2): "cell_18aa2",
        (b"WRLD", 0x0000003C): "wrld_003c",
    }
    target_rts = {rt for rt, _ in want_records}
    raw_types_keep_compressed = {"cell_18aa2", "wrld_003c"}

    out: dict[str, tuple[int, int, int, bytes] | bytes] = {}
    esm = FALLOUT4_ESM_PATH.read_bytes()
    pos = 0
    n = len(esm)
    while pos + 24 <= n and len(out) < len(want_records):
        rt = esm[pos : pos + 4]
        sz = struct.unpack_from("<I", esm, pos + 4)[0]
        if rt == b"GRUP":
            lbl = esm[pos + 8 : pos + 12]
            gt = struct.unpack_from("<I", esm, pos + 12)[0]
            # Saltar top-level GRUPs que no contienen ninguno de nuestros objetivos
            if gt == 0 and lbl not in target_rts and lbl not in (b"CELL", b"WRLD", b"QUST"):
                pos += sz
                continue
            pos += 24
        else:
            fl, fid, _vr, vc = struct.unpack_from("<IIHH", esm, pos + 8)[0], struct.unpack_from("<I", esm, pos + 12)[0], struct.unpack_from("<H", esm, pos + 16)[0], struct.unpack_from("<H", esm, pos + 20)[0]
            fver = struct.unpack_from("<H", esm, pos + 20)[0]
            v2 = struct.unpack_from("<H", esm, pos + 22)[0]
            key = (rt, fid)
            if key in want_records:
                tname = want_records[key]
                rec_bytes = esm[pos : pos + 24 + sz]
                if tname in raw_types_keep_compressed:
                    raw_rec = bytearray(rec_bytes)
                    # Actualizar FormVersion a 131 en el override del plugin
                    struct.pack_into("<HH", raw_rec, 20, 131, v2)
                    out[tname] = bytes(raw_rec)
                else:
                    body = esm[pos + 24 : pos + 24 + sz]
                    if fl & 0x00040000:
                        body = zlib.decompress(body[4:])
                    out[tname] = (fl & ~0x00040000, fver, v2, body)
            pos += 24 + sz

    missing = [v for v in want_records.values() if v not in out]
    if missing:
        raise RuntimeError(f"Faltan plantillas en Fallout4.esm: {missing}")
    return out


def _build_navm_orbita7(cell_fid: int, navm_fid: int, exit_door_refr: int) -> bytes:
    """Construye `NAVM` (`NVNM v15`) transitable por las 5 salas Art-Deco + enlace a la puerta sur."""
    # Rectángulos conectados en Z=0.5: Rotonda, los 4 portales, Ala Este, Ala Oeste, Hangar Norte, Sala Director.
    # Vértices exactos (ccw vistos desde +Z) y triángulos sin solapamientos con conectividad completa.
    # Usaremos un mallado limpio por franjas convexas que comparten vértices exactos en los portales:
    verts: list[tuple[float, float, float]] = [
        # Rotonda Sur/Puerta [-560..560, -580..-500] (idx 0..3) y centro [-560..560, -500..580] (idx 4..7)
        (-560.0, -580.0, 1.0),  # 0
        (-120.0, -580.0, 1.0),  # 1 (puerta sur izq)
        (120.0, -580.0, 1.0),   # 2 (puerta sur der)
        (560.0, -580.0, 1.0),   # 3
        (-560.0, -100.0, 1.0),  # 4
        (-120.0, -100.0, 1.0),  # 5
        (120.0, -100.0, 1.0),   # 6
        (560.0, -100.0, 1.0),   # 7
        (-560.0, 100.0, 1.0),   # 8
        (560.0, 100.0, 1.0),    # 9
        (-560.0, 580.0, 1.0),   # 10
        (-120.0, 580.0, 1.0),   # 11 (portal norte izq)
        (120.0, 580.0, 1.0),    # 12 (portal norte der)
        (560.0, 580.0, 1.0),    # 13
        # Ala Oeste [-1380..-560, -100..100] -> paso y sala [-1380..-700, -360..360]
        (-700.0, -100.0, 1.0),  # 14
        (-700.0, 100.0, 1.0),   # 15
        (-1380.0, -360.0, 1.0), # 16
        (-700.0, -360.0, 1.0),  # 17
        (-1380.0, 360.0, 1.0),  # 18
        (-700.0, 360.0, 1.0),   # 19
        # Ala Este [560..1380, -360..360] y portal sur a Director [940..1140, -500..-360]
        (700.0, -100.0, 1.0),   # 20
        (700.0, 100.0, 1.0),    # 21
        (700.0, -360.0, 1.0),   # 22
        (940.0, -360.0, 1.0),   # 23
        (1140.0, -360.0, 1.0),  # 24
        (1380.0, -360.0, 1.0),  # 25
        (700.0, 360.0, 1.0),    # 26
        (1380.0, 360.0, 1.0),   # 27
        # Sala del Director [700..1380, -1180..-500] conectado por [940..1140, -500..-360]
        (940.0, -500.0, 1.0),   # 28
        (1140.0, -500.0, 1.0),  # 29
        (700.0, -1180.0, 1.0),  # 30
        (1380.0, -1180.0, 1.0), # 31
        (700.0, -500.0, 1.0),   # 32
        (1380.0, -500.0, 1.0),  # 33
        # Hangar Norte [-700..700, 700..1720] conectado por [-120..120, 580..700]
        (-120.0, 700.0, 1.0),   # 34
        (120.0, 700.0, 1.0),    # 35
        (-700.0, 700.0, 1.0),   # 36
        (700.0, 700.0, 1.0),    # 37
        (-700.0, 1720.0, 1.0),  # 38
        (700.0, 1720.0, 1.0),   # 39
    ]

    # Dividir en pares de triángulos por quad (cada quad usa 4 índices existentes)
    tris: list[tuple[int, int, int]] = []

    def add_quad(a: int, b: int, c: int, d_idx: int) -> None:
        # CCW quads: (a, b, c) y (a, c, d_idx)
        tris.append((a, b, c))
        tris.append((a, c, d_idx))

    # 0..1: Rotonda centro-puerta sur (tri 0 toca borde puerta 1-2!)
    add_quad(1, 2, 6, 5)
    add_quad(0, 1, 5, 4)
    add_quad(2, 3, 7, 6)
    # 6..7: Rotonda banda media Y[-100..100] (tri 6 izquierda conecta con Ala Oeste, tri 9 derecha con Ala Este)
    add_quad(4, 5, 8, 8)  # evitar degenerado: hacer Rotonda banda media completa (4,7,9,8)
    tris.pop(); tris.pop()
    add_quad(4, 5, 6, 8)
    # Más simple y exacto para que las aristas compartan nodos exactos:
    tris.clear()

    # Tira Sur Rotonda Y[-580..-100]
    add_quad(0, 1, 5, 4)    # t0, t1
    add_quad(1, 2, 6, 5)    # t2 (puerta sur en borde 1-2!), t3
    add_quad(2, 3, 7, 6)    # t4, t5
    # Banda Media Rotonda Y[-100..100] (izquierda=4-8, derecha=7-9)
    add_quad(4, 7, 9, 8)    # t6, t7
    # Tira Norte Rotonda Y[100..580] (portal norte 11-12)
    add_quad(8, 9, 13, 10)  # t8, t9 (simplificado con vértices compartidos: añadimos transición limpia)
    tris.clear()

    # Rejilla modular limpia 100% conforme a vértices exactos:
    verts = [
        # Rotonda X[-560..560] x Y[-580..580] en 3 bandas exactas Y[-580,-100,100,580] y X[-560,-120,120,560]
        # fila y=-580 (0..3)
        (-560.0, -580.0, 1.0), (-120.0, -580.0, 1.0), (120.0, -580.0, 1.0), (560.0, -580.0, 1.0),
        # fila y=-100 (4..7)
        (-560.0, -100.0, 1.0), (-120.0, -100.0, 1.0), (120.0, -100.0, 1.0), (560.0, -100.0, 1.0),
        # fila y=+100 (8..11)
        (-560.0, 100.0, 1.0),  (-120.0, 100.0, 1.0),  (120.0, 100.0, 1.0),  (560.0, 100.0, 1.0),
        # fila y=+580 (12..15)
        (-560.0, 580.0, 1.0),  (-120.0, 580.0, 1.0),  (120.0, 580.0, 1.0),  (560.0, 580.0, 1.0),
        # Portal Oeste X=-700, Y=-100..100 (16, 17)
        (-700.0, -100.0, 1.0), (-700.0, 100.0, 1.0),
        # Ala Oeste X[-1380..-700], Y[-360,-100,100,360] (18..23)
        (-1380.0, -360.0, 1.0), (-700.0, -360.0, 1.0),
        (-1380.0, 360.0, 1.0),  (-700.0, 360.0, 1.0),
        # Portal Este X=700, Y=-100..100 (22, 23 -> índices 22,23)
        (700.0, -100.0, 1.0),   (700.0, 100.0, 1.0),
        # Ala Este X[700..1380], Y[-360,360] dividido con puerta a Director [940..1140] (24..31)
        (700.0, -360.0, 1.0), (940.0, -360.0, 1.0), (1140.0, -360.0, 1.0), (1380.0, -360.0, 1.0),
        (700.0, 360.0, 1.0),  (1380.0, 360.0, 1.0),
        # Portal + Sala Director (30..35)
        (940.0, -500.0, 1.0), (1140.0, -500.0, 1.0),
        (700.0, -500.0, 1.0), (1380.0, -500.0, 1.0),
        (700.0, -1180.0, 1.0), (1380.0, -1180.0, 1.0),
        # Portal + Hangar Norte (36..41)
        (-120.0, 700.0, 1.0), (120.0, 700.0, 1.0),
        (-700.0, 700.0, 1.0), (700.0, 700.0, 1.0),
        (-700.0, 1720.0, 1.0), (700.0, 1720.0, 1.0),
    ]

    # Rotonda: 9 quads (3x3) -> puerta sur en quad(1,2,6,5) -> tri 2
    for ry in range(3):
        for rx in range(3):
            b0 = ry * 4 + rx
            add_quad(b0, b0 + 1, b0 + 5, b0 + 4)
    # Portal Oeste (16, 4, 8, 17) y Ala Oeste
    add_quad(16, 4, 8, 17)
    add_quad(18, 19, 16, 17)  # mitad inferior/izquierda oeste
    add_quad(18, 17, 21, 20)  # resto Ala Oeste
    # Portal Este (7, 22, 23, 11) y Ala Este
    add_quad(7, 22, 23, 11)
    add_quad(24, 25, 23, 22)
    add_quad(25, 26, 23, 23)  # no degenerado -> triángulo único (25, 26, 23) + (26, 27, 23)
    tris.pop(); tris.pop()
    tris.append((25, 26, 23))
    tris.append((26, 27, 23))
    add_quad(22, 23, 29, 28)
    tris.append((23, 27, 29))
    # Portal + Sala Director
    add_quad(30, 31, 26, 25)
    add_quad(34, 35, 33, 32)
    # Portal + Hangar Norte
    add_quad(13, 14, 37, 36)
    add_quad(38, 36, 37, 40)
    tris.append((37, 39, 41))
    tris.append((37, 41, 40))

    # Calcular adyacencia real automática de aristas compartidas `(a, b) == (b', a')`
    edge_owner: dict[tuple[int, int], int] = {}
    for ti, (v0, v1, v2) in enumerate(tris):
        edge_owner[(v0, v1)] = ti
        edge_owner[(v1, v2)] = ti
        edge_owner[(v2, v0)] = ti

    door_tri_idx = 2  # tri del borde (1, 2) frente a la puerta de salida sur

    tri_buf = bytearray()
    for ti, (v0, v1, v2) in enumerate(tris):
        e0 = edge_owner.get((v1, v0), -1)
        e1 = edge_owner.get((v2, v1), -1)
        e2 = edge_owner.get((v0, v2), -1)
        t_flags = 0x0840 if ti == door_tri_idx else 0x0800
        # `<3H 3h I B H H` = 21 bytes (cover_data=0x43000000 = 128.0f altura estandar, flags, unk2=0)
        tri_buf += struct.pack("<3H3hIBHH", v0, v1, v2, e0, e1, e2, 0x43000000, 0, t_flags, 0)

    min_x = min(v[0] for v in verts)
    min_y = min(v[1] for v in verts)
    min_z = min(v[2] for v in verts)
    max_x = max(v[0] for v in verts)
    max_y = max(v[1] for v in verts)
    max_z = max(v[2] for v in verts) + 128.0

    nvnm = bytearray()
    nvnm += struct.pack("<IIIII", 15, 0xA5E9A03C, 0, cell_fid, len(verts))
    for vx, vy, vz in verts:
        nvnm += struct.pack("<3f", vx, vy, vz)
    nvnm += struct.pack("<I", len(tris))
    nvnm += tri_buf
    nvnm += struct.pack("<I", 0)  # 0 conexiones externas
    nvnm += struct.pack("<I", 1)  # 1 triángulo de puerta conectado a exit_door_refr
    nvnm += struct.pack("<HII", door_tri_idx, 0xE48B73F3, exit_door_refr)
    nvnm += struct.pack("<III", 0, 0, 0)  # cover edges, cover ranges, precomp waypoints = 0
    # Quadtree maxDepth=1 hoja única con todas las tris
    nvnm += struct.pack(
        "<I2f6fI",
        1,
        max_x - min_x,
        max_y - min_y,
        min_x,
        min_y,
        min_z,
        max_x,
        max_y,
        max_z,
        len(tris),
    )
    nvnm += struct.pack(f"<{len(tris)}H", *range(len(tris)))

    comp = zlib.compress(subrec(b"NVNM", bytes(nvnm)))
    uncomp_body = subrec(b"NVNM", bytes(nvnm))
    return make_record(
        b"NAVM",
        navm_fid,
        struct.pack("<I", len(uncomp_body)) + comp,
        flags=0x00040000,
        fver=131,
        v2=0,
    )


def _clone_npc(
    tpl_entry: tuple[int, int, int, bytes],
    new_fid: int,
    edid: str,
    full_name: str,
    vtck_fid: int | None,
    faction_fids: list[tuple[int, int]],
    aggressive: int,
    confidence: int = 2,
    essential: bool = False,
    doft_fid: int | None = None,
    pkid_fid: int | None = 0x00003641,
) -> bytes:
    """Clona una plantilla `NPC_` respetando `OBTE..STOP`, `TPLT`/`TPTA` y `SNAM` de 5 bytes."""
    _fl, _fver, _v2, body = tpl_entry
    subs = parse_subrecords(body)
    uses_tpta = any(t == b"TPTA" for t, _ in subs)
    out: list[tuple[bytes, bytes]] = []
    in_obte = False
    replaced_snam = False
    has_pkid = False

    for tag, sb in subs:
        if tag == b"OBTE":
            in_obte = True
            out.append((tag, sb))
            continue
        if tag == b"STOP":
            in_obte = False
            out.append((tag, sb))
            continue

        if in_obte:
            # Dentro de OBTE..STOP, FULL es un ID de cadena localizada -> convertir a "Default"
            if tag == b"FULL":
                out.append((b"FULL", b"Default\x00"))
            else:
                out.append((tag, sb))
            continue

        if tag == b"EDID":
            out.append((b"EDID", edid.encode("utf-8") + b"\x00"))
        elif tag == b"OBND":
            if len(sb) == 12 and sb == b"\x00" * 12:
                out.append((b"OBND", struct.pack("<6h", -27, -27, 0, 27, 27, 120)))
            else:
                out.append((b"OBND", sb))
        elif tag == b"FULL":
            out.append((b"FULL", full_name.encode("utf-8") + b"\x00"))
        elif tag in (b"SHRT", b"VMAD"):
            continue
        elif tag == b"ACBS" and len(sb) == 20:
            ab = bytearray(sb)
            acbs_fl = struct.unpack_from("<I", ab, 0)[0]
            acbs_fl &= ~0x00000008  # quitar Respawn
            if essential:
                acbs_fl |= 0x00000002  # Essential
            else:
                acbs_fl &= ~0x00000802  # quitar Essential y Protected en hostiles
            struct.pack_into("<I", ab, 0, acbs_fl)
            if uses_tpta:
                # Offset 14 = templateFlags (uint16): limpiar Use Factions (0x0004), Script (0x0040), Base Data (0x0080)
                tpl_fl = struct.unpack_from("<H", ab, 14)[0]
                tpl_fl &= ~0x00C4
                struct.pack_into("<H", ab, 14, tpl_fl)
            out.append((b"ACBS", bytes(ab)))
        elif tag == b"TPTA" and len(sb) == 52:
            tpta_vals = list(struct.unpack("<13I", sb))
            tpta_vals[2] = 0  # Facciones propias (SNAM)
            tpta_vals[6] = 0  # Sin plantilla de scripts
            tpta_vals[7] = 0  # Nombre propio en español (FULL)
            out.append((b"TPTA", struct.pack("<13I", *tpta_vals)))
        elif tag == b"VTCK" and vtck_fid is not None:
            out.append((b"VTCK", struct.pack("<I", vtck_fid)))
        elif tag == b"DOFT" and doft_fid is not None:
            out.append((b"DOFT", struct.pack("<I", doft_fid)))
        elif tag == b"SNAM":
            if not replaced_snam:
                replaced_snam = True
                for f_fid, f_rank in faction_fids:
                    out.append((b"SNAM", struct.pack("<Ib", f_fid, f_rank)))
        elif tag == b"AIDT" and len(sb) >= 20:
            ai = bytearray(sb)
            ai[0] = aggressive & 0xFF
            ai[1] = confidence & 0xFF
            ai[2] = 2  # EnergyLevel
            ai[3] = 2  # Responsibility
            out.append((b"AIDT", bytes(ai)))
        elif tag == b"PKID":
            if pkid_fid is not None and not has_pkid:
                has_pkid = True
                out.append((b"PKID", struct.pack("<I", pkid_fid)))
        else:
            out.append((tag, sb))

    if not replaced_snam and faction_fids:
        for f_fid, f_rank in faction_fids:
            out.append((b"SNAM", struct.pack("<Ib", f_fid, f_rank)))

    return make_record(b"NPC_", new_fid, rebuild_subrecords(out), flags=0, fver=131, v2=0)


def _clone_terminal(tpl_term: tuple[int, int, int, bytes], new_fid: int, term_data: dict) -> bytes:
    """Clona `TERM 0x00099CD0` soportando texto plano (0x08), submenú (0x04), retorno (0x05) y CTDA."""
    _fl, _fv, v2, body = tpl_term
    subs = parse_subrecords(body)
    strip_tags = {
        b"EDID", b"VMAD", b"FULL", b"BTXT", b"ISIZ",
        b"ITXT", b"ANAM", b"ITID", b"UNAM", b"RNAM", b"TNAM", b"CTDA",
    }
    out: list[tuple[bytes, bytes]] = []
    entries = term_data["entries"]
    for tag, sb in subs:
        if tag in strip_tags:
            continue
        if tag == b"BSIZ":
            out.append((b"EDID", term_data["edid"].encode("utf-8") + b"\x00"))
            out.append((b"FULL", term_data["full"].encode("utf-8") + b"\x00"))
            out.append((b"BSIZ", struct.pack("<I", 1)))
            out.append((b"BTXT", term_data["header"].encode("utf-8") + b"\x00"))
            out.append((b"ISIZ", struct.pack("<I", len(entries))))
            for eidx, item in enumerate(entries, 1):
                if isinstance(item, tuple):
                    itxt_s, unam_s = item
                    out.append((b"ITXT", itxt_s.encode("utf-8") + b"\x00"))
                    out.append((b"ANAM", b"\x08"))
                    out.append((b"ITID", struct.pack("<H", eidx)))
                    out.append((b"UNAM", unam_s.encode("utf-8") + b"\x00"))
                else:
                    anam_b = int(item.get("anam", 0x08)) & 0xFF
                    itid_v = int(item.get("itid", eidx)) & 0xFFFF
                    out.append((b"ITXT", item["itxt"].encode("utf-8") + b"\x00"))
                    out.append((b"ANAM", struct.pack("<B", anam_b)))
                    out.append((b"ITID", struct.pack("<H", itid_v)))
                    if anam_b == 0x04:
                        out.append((b"TNAM", struct.pack("<I", int(item["tnam"]))))
                    elif anam_b == 0x08:
                        out.append((b"UNAM", item.get("unam", "").encode("utf-8") + b"\x00"))
                    for ckind, op_b, val in item.get("conds", ()):
                        if ckind == "stage":
                            out.append((b"CTDA", make_ctda_getstage(op_b, float(val), FID_QUST_ORBITA7)))
        else:
            out.append((tag, sb))
    return make_record(b"TERM", new_fid, rebuild_subrecords(out), flags=0x2010, fver=131, v2=v2)


def _make_simple_acti(
    fid: int,
    edid: str,
    full_name: str,
    nif_path: str,
    obnd: tuple[int, int, int, int, int, int],
    script_name: str | None = None,
    attx_prompt: str | None = None,
) -> bytes:
    """Construye un registro `ACTI` limpio con modelo NIF propio en Blender y script opcional."""
    parts = [subrec_cstr(b"EDID", edid)]
    if script_name:
        parts.append(subrec(b"VMAD", build_simple_vmad(script_name)))
    parts.append(subrec(b"OBND", struct.pack("<6h", *obnd)))
    parts.append(subrec_cstr(b"FULL", full_name))
    parts.append(subrec_cstr(b"MODL", nif_path))
    if attx_prompt:
        parts.append(subrec_cstr(b"ATTX", attx_prompt))
    parts.append(subrec(b"FNAM", b"\x00\x00"))
    return make_record(b"ACTI", fid, b"".join(parts), flags=0, fver=131, v2=0)


def _make_simple_stat(fid: int, edid: str, nif_path: str, obnd: tuple[int, int, int, int, int, int]) -> bytes:
    """Construye un registro `STAT` compatible con Fallout 4 (`fver=131`)."""
    body = (
        subrec_cstr(b"EDID", edid)
        + subrec(b"OBND", struct.pack("<6h", *obnd))
        + subrec_cstr(b"MODL", nif_path)
        + subrec(b"DNAM", struct.pack("<fI", 90.0, 0x00000017))
    )
    return make_record(b"STAT", fid, body, flags=0, fver=131, v2=0)


def _make_mesg_box(fid: int, edid: str, title: str, body: str, buttons: list[str]) -> bytes:
    """Construye un `MESG` cuadro de mensaje con sus botones `ITXT`."""
    buf = bytearray()
    buf += subrec_cstr(b"EDID", edid)
    buf += subrec_cstr(b"DESC", body)
    buf += subrec_cstr(b"FULL", title)
    buf += subrec(b"INAM", struct.pack("<I", 0))
    buf += subrec(b"DNAM", struct.pack("<I", 1))
    for btn in buttons:
        buf += subrec_cstr(b"ITXT", btn)
    return make_record(b"MESG", fid, bytes(buf), flags=0, fver=131, v2=0)


def _make_refr(
    fid: int,
    base_fid: int,
    pos: tuple[float, float, float, float, float, float],
    flags: int = 0,
    scale: float | None = None,
    xtel: bytes | None = None,
    extra_subs: list[tuple[bytes, bytes]] | None = None,
) -> bytes:
    """Construye un registro `REFR` limpio."""
    subs: list[tuple[bytes, bytes]] = [(b"NAME", struct.pack("<I", base_fid))]
    if extra_subs:
        subs.extend(extra_subs)
    if scale is not None:
        subs.append((b"XSCL", struct.pack("<f", scale)))
    if xtel is not None:
        subs.append((b"XTEL", xtel))
    subs.append((b"DATA", struct.pack("<6f", *pos)))
    return make_record(b"REFR", fid, rebuild_subrecords(subs), flags=flags, fver=131, v2=0)


def _make_achr(fid: int, npc_base_fid: int, pos: tuple[float, float, float, float, float, float], flags: int = 0x00000400) -> bytes:
    """Construye un registro `ACHR` limpio."""
    body = subrec(b"NAME", struct.pack("<I", npc_base_fid)) + subrec(b"DATA", struct.pack("<6f", *pos))
    return make_record(b"ACHR", fid, body, flags=flags, fver=131, v2=0)


def build_orbita7_esp_grups(lang: str = "es") -> dict[bytes, bytes]:
    """Construye todos los `GRUP`s top-level del arco «Estudio Subterráneo Órbita-7» (`'es'` o `'en'`)."""
    lang_norm = _normalize_lang(lang)
    data_mod = _get_data_module(lang_norm)
    is_en = lang_norm == "en"

    def _t(es_txt: str, en_txt: str) -> str:
        return en_txt if is_en else es_txt

    tpl = extract_orbita7_templates()

    # 1. GLOB
    def make_glob(fid: int, edid: str, val: float = 0.0) -> bytes:
        return make_record(b"GLOB", fid, subrec_cstr(b"EDID", edid) + subrec(b"FNAM", b"s") + subrec(b"FLTV", struct.pack("<f", val)))

    grup_glob = make_grup(
        b"GLOB",
        make_glob(FID_GLOB_BARK, "Orbita7BarkIndex")
        + make_glob(FID_GLOB_EXAM, "Orbita7ExamProgress")
        + make_glob(FID_GLOB_COILS, "Orbita7CoilsFound")
        + make_glob(FID_GLOB_PA_RESTORED, "Orbita7PAPiecesRestored")
        + make_glob(FID_GLOB_MURAL, "Orbita7MuralInspected"),
    )

    # 2. VTYP
    def make_vtyp(fid: int, edid: str, dnam_b: bytes) -> bytes:
        return make_record(b"VTYP", fid, subrec_cstr(b"EDID", edid) + subrec(b"DNAM", dnam_b), fver=131)

    grup_vtyp = make_grup(
        b"VTYP",
        make_vtyp(FID_VTYP_ARTIE, data_mod.ARTIE_VTYP, b"\x00")
        + make_vtyp(FID_VTYP_CORONEL, data_mod.CORONEL_VTYP, b"\x00")
        + make_vtyp(FID_VTYP_CLARA, data_mod.CLARA_VTYP, b"\x02"),
    )

    # 3. LCTN (desvinculada de HubrisComicsLocation 0x00045610 -> CommonwealthLocation 0x00002CF0)
    lctn_body = (
        subrec_cstr(b"EDID", "LocHubrisOrbita7Studio")
        + subrec(b"KSIZ", struct.pack("<I", 1))
        + subrec(b"KWDA", struct.pack("<I", 0x00231DDD))  # LocTypeClearable
        + subrec_cstr(b"FULL", _t("Estudio Subterráneo Órbita-7", "Underground Studio Orbit-7"))
        + subrec(b"PNAM", struct.pack("<I", 0x00002CF0))  # CommonwealthLocation
        + subrec(b"MNAM", struct.pack("<I", 0x01003002))  # MapMarker
        + subrec(b"RNAM", struct.pack("<I", 0))
    )
    grup_lctn = make_grup(b"LCTN", make_record(b"LCTN", FID_LCTN_ORBITA7, lctn_body, flags=0x00000800))

    # 4. OTFT
    otft_body = subrec_cstr(b"EDID", "OutfitArtieVanceHubris") + subrec(b"INAM", struct.pack("<I", 0x000FC395))
    grup_otft = make_grup(b"OTFT", make_record(b"OTFT", FID_OTFT_ARTIE, otft_body))

    # 5. STAT (7 estáticos de Órbita-7 para fusionarse con HoverPlatform en update_aero_esp.py)
    stat_records = b"".join(
        [
            _make_simple_stat(FID_STAT_HALL, "Orbita7StudioHallComplex", r"AeroArmor\Orbita7\Orbita7_StudioHallComplex.nif", (-1500, -1300, -16, 1500, 1820, 440)),
            _make_simple_stat(FID_STAT_PLANETARIUM, "Orbita7SaturnPlanetarium", r"AeroArmor\Orbita7\Orbita7_SaturnPlanetarium.nif", (-120, -120, -200, 120, 120, 0)),
            _make_simple_stat(FID_STAT_GANTRY, "Orbita7PAGantryPlatform", r"AeroArmor\Orbita7\Orbita7_PAGantryPlatform.nif", (-110, -110, 0, 110, 110, 20)),
            _make_simple_stat(FID_STAT_DESK, "Orbita7DraftingDeskStatic", r"AeroArmor\Orbita7\Orbita7_ComicDraftingDesk.nif", (-60, -34, 0, 60, 34, 90)),
            _make_simple_stat(FID_STAT_BED_SHOW, "Orbita7CosmosBedShowcase", r"AeroArmor\Orbita7\Orbita7_CosmosBed.nif", (-72, -102, 0, 72, 100, 64)),
            _make_simple_stat(FID_STAT_CARB_DISP, "Orbita7HeroCarbineDisplayStat", r"Weapons\AeroArmor\HeroCarbine\CosmosReceiver.nif", (-40, -12, -12, 40, 12, 16)),
            _make_simple_stat(FID_STAT_CANNON_DISP, "Orbita7PACannonDisplayStat", r"Weapons\AeroArmor\PACannon\CosmosPACannonBase.nif", (-56, -18, -18, 56, 18, 22)),
            _make_simple_stat(FID_STAT_BARRIER, "StatOrbita7SecurityBarrier", r"AeroArmor\Orbita7\Orbita7_SecurityBarrier.nif", (-124, -10, 0, 124, 10, 236)),
            _make_simple_stat(FID_STAT_EXT_PLINTH, "Orbita7ExteriorBunkerPlinth", r"Markers\MarkerX.nif", (-16, -16, -16, 16, 16, 16)),
        ]
    )
    grup_stat = make_grup(b"STAT", stat_records)

    # 6. ACTI
    grup_acti = make_grup(
        b"ACTI",
        _make_simple_acti(FID_ACTI_VITRINE1, "ActiOrbita7ClueVitrine1", _t("Vitrina: Capitán Cosmos Nº 1", "Showcase: Captain Cosmos #1"), r"AeroArmor\Orbita7\Orbita7_LoreVitrine_Cosmos.nif", (-60, -35, 0, 60, 35, 190), "HubrisOrbita7CluePlaqueScript", _t("Inspeccionar", "Inspect"))
        + _make_simple_acti(FID_ACTI_VITRINE2, "ActiOrbita7ClueVitrine2", _t("Vitrina: Los Imparables de Hubris", "Showcase: Hubris's The Unstoppables"), r"AeroArmor\Orbita7\Orbita7_LoreVitrine_Unstoppables.nif", (-60, -35, 0, 60, 35, 190), "HubrisOrbita7CluePlaqueScript", _t("Inspeccionar", "Inspect"))
        + _make_simple_acti(FID_ACTI_DESK, "ActiOrbita7ClueDesk", _t("Restirador de Clara Sterling", "Clara Sterling's Drafting Desk"), r"AeroArmor\Orbita7\Orbita7_ComicDraftingDesk.nif", (-60, -34, 0, 60, 34, 90), "HubrisOrbita7CluePlaqueScript", _t("Examinar bocetos", "Examine sketches"))
        + _make_simple_acti(FID_ACTI_MURAL, "ActiOrbita7ClueMural", _t("Gran Mural del Juramento Estelar", "Grand Star Guard Oath Mural"), r"AeroArmor\Orbita7\Orbita7_DirectorMuralFrame.nif", (-168, -10, 0, 168, 10, 176), "HubrisOrbita7CluePlaqueScript", _t("Leer juramento", "Read oath"))
        + _make_simple_acti(FID_ACTI_EXAM_CONSOLE, "ActiOrbita7ExamConsole", _t("Consola de Examen «Verdadero Creyente»", "'True Believer' Exam Console"), r"AeroArmor\Orbita7\Orbita7_TrueBelieverConsole.nif", (-64, -64, 0, 64, 64, 128), "HubrisOrbita7ExamConsoleScript", _t("Realizar examen", "Take exam"))
        + _make_simple_acti(FID_ACTI_SUIT_POD, "ActiOrbita7HeroSuitPod", _t("Cápsula de Estasis: Traje Astro-Cosmos", "Stasis Pod: Astro-Cosmos Flight Suit"), r"AeroArmor\Orbita7\Orbita7_HeroSuitPod.nif", (-60, -60, 0, 60, 60, 224), "HubrisOrbita7RewardPodScript", _t("Reclamar prototipo", "Claim prototype"))
        + _make_simple_acti(FID_ACTI_WEAP_PED, "ActiOrbita7WeaponPedestal", _t("Pedestal Fotónico: Carabina Astro-Cosmos", "Photonic Pedestal: Astro-Cosmos Carbine"), r"AeroArmor\Orbita7\Orbita7_WeaponPedestal.nif", (-50, -34, 0, 50, 34, 82), "HubrisOrbita7RewardPodScript", _t("Reclamar carabina", "Claim carbine"))
        + _make_simple_acti(FID_ACTI_SOLAR_REL, "ActiOrbita7SolarReliquary", _t("Relicario Solar: Cañón Orbital Gauss", "Solar Reliquary: Orbital Gauss Cannon"), r"AeroArmor\Orbita7\Orbita7_SolarReliquary.nif", (-66, -66, 0, 66, 66, 86), "HubrisOrbita7RewardPodScript", _t("Reclamar cañón", "Claim cannon")),
    )

    # 7. DOOR
    def clone_door(tpl_key: str, fid: int, edid: str, full: str) -> bytes:
        fl, _fv, v2, body = tpl[tpl_key]  # type: ignore[misc]
        out_subs = []
        for tag, sb in parse_subrecords(body):
            if tag == b"EDID":
                out_subs.append((b"EDID", edid.encode("utf-8") + b"\x00"))
            elif tag == b"FULL":
                out_subs.append((b"FULL", full.encode("utf-8") + b"\x00"))
            elif tag == b"VMAD":
                continue
            else:
                out_subs.append((tag, sb))
        return make_record(b"DOOR", fid, rebuild_subrecords(out_subs), flags=fl, fver=131, v2=v2)

    grup_door = make_grup(
        b"DOOR",
        clone_door("door_trapdoor", FID_DOOR_EXT_HATCH, "DoorOrbita7ExteriorHatch", _t("Escotilla de Estudio Órbita-7", "Studio Orbit-7 Hatch"))
        + clone_door("door_utilmetal", FID_DOOR_INT_EXIT, "DoorOrbita7InteriorExit", _t("Salida al Callejón de Hubris Comics", "Exit to Hubris Comics Alley")),
    )

    # 7b. LIGH (3 luces omnidireccionales amplias sin sombras para iluminar con nitidez el Estudio Órbita-7)
    def clone_ligh(fid: int, edid: str, radius: int, rgb: tuple[int, int, int], fade: float) -> bytes:
        fl, fv, v2, body = tpl["ligh_white_ns"]  # type: ignore[misc]
        lsubs: list[tuple[bytes, bytes]] = []
        for tag, sb in parse_subrecords(body):
            if tag == b"EDID":
                lsubs.append((b"EDID", edid.encode("utf-8") + b"\x00"))
            elif tag == b"DATA" and len(sb) >= 16:
                db = bytearray(sb)
                struct.pack_into("<i", db, 4, int(radius))
                db[8], db[9], db[10], db[11] = rgb[0], rgb[1], rgb[2], 0
                lsubs.append((b"DATA", bytes(db)))
            elif tag == b"FNAM":
                lsubs.append((b"FNAM", struct.pack("<f", float(fade))))
            else:
                lsubs.append((tag, sb))
        return make_record(b"LIGH", fid, rebuild_subrecords(lsubs), flags=fl, fver=fv, v2=v2)

    grup_ligh = make_grup(
        b"LIGH",
        clone_ligh(FID_LIGH_STUDIO_WARM, "LighOrbita7StudioWarmNS", 1050, (250, 234, 206), 1.85)
        + clone_ligh(FID_LIGH_STUDIO_CLEAN, "LighOrbita7StudioCleanNS", 960, (232, 240, 250), 1.65)
        + clone_ligh(FID_LIGH_STUDIO_CYAN, "LighOrbita7StudioCyanNS", 680, (150, 222, 248), 1.35),
    )

    # 8. FURN
    pa_fl, _pa_fv, pa_v2, pa_body = tpl["furn_pa"]  # type: ignore[misc]
    pa_subs_out: list[tuple[bytes, bytes]] = []
    in_obte_pa = False
    wrote_cntos = False
    for tag, sb in parse_subrecords(pa_body):
        if tag == b"OBTE":
            in_obte_pa = True
            continue
        if tag == b"STOP":
            in_obte_pa = False
            continue
        if in_obte_pa:
            continue
        if tag == b"EDID":
            pa_subs_out.append((b"EDID", b"FurnOrbita7CosmosPAFrame\x00"))
        elif tag == b"VMAD":
            pa_subs_out.append((b"VMAD", append_vmad_script(sb, "HubrisOrbita7PAFrameScript")))
        elif tag == b"FULL":
            pa_subs_out.append((b"FULL", _t("Servoarmadura Astro-Cosmos", "Astro-Cosmos Power Armor").encode("utf-8") + b"\x00"))
        elif tag == b"COCT":
            pa_subs_out.append((b"COCT", struct.pack("<I", 1)))
        elif tag == b"CNTO":
            if not wrote_cntos:
                wrote_cntos = True
                pa_subs_out.append((b"CNTO", struct.pack("<II", 0x00075FE4, 1)))  # Núcleo de fusión
        else:
            pa_subs_out.append((tag, sb))
    rec_furn_pa = make_record(b"FURN", FID_FURN_PA_FRAME, rebuild_subrecords(pa_subs_out), flags=pa_fl, fver=131, v2=pa_v2)

    bed_fl, _bed_fv, bed_v2, bed_body = tpl["furn_bed"]  # type: ignore[misc]
    bed_subs_out = []
    for tag, sb in parse_subrecords(bed_body):
        if tag == b"VMAD":
            continue
        elif tag == b"EDID":
            bed_subs_out.append((b"EDID", b"FurnOrbita7DirectorBed\x00"))
        elif tag == b"FULL":
            bed_subs_out.append((b"FULL", _t("Cama de Descanso Órbita-7", "Orbit-7 Spacer Rest Bed").encode("utf-8") + b"\x00"))
        else:
            bed_subs_out.append((tag, sb))
    rec_furn_bed = make_record(b"FURN", FID_FURN_DIRECTOR_BED, rebuild_subrecords(bed_subs_out), flags=bed_fl, fver=131, v2=bed_v2)
    grup_furn = make_grup(b"FURN", rec_furn_pa + rec_furn_bed)

    # 9. TERM (Terminales de pistas + jerarquía continua 0x01001500..0x01001514 ordenados por FormID)
    term_items: list[tuple[int, bytes]] = [
        (FID_TERM_PROD_TV, _clone_terminal(tpl["term_desk"], FID_TERM_PROD_TV, data_mod.TERMINAL_PRODUCTION_TV)),  # type: ignore[arg-type]
        (FID_TERM_ARTIE_LAB, _clone_terminal(tpl["term_desk"], FID_TERM_ARTIE_LAB, data_mod.TERMINAL_ARTIE_LAB)),  # type: ignore[arg-type]
    ]
    for t_def in data_mod.EXAM_TERMINAL_DEFS:
        t_fid = int(t_def["fid"])
        term_items.append((t_fid, _clone_terminal(tpl["term_desk"], t_fid, t_def)))  # type: ignore[arg-type]
    term_items.sort(key=lambda x: x[0])
    grup_term = make_grup(b"TERM", b"".join(rec for _, rec in term_items))

    # 10. MISC
    def clone_misc(tpl_key: str, fid: int, edid: str, full: str) -> bytes:
        fl, _fv, v2, body = tpl[tpl_key]  # type: ignore[misc]
        out_subs: list[tuple[bytes, bytes]] = []
        vmad_added = False
        for tag, sb in parse_subrecords(body):
            if tag in (b"VMAD", b"CVPA", b"PTRN"):
                continue
            if tag == b"EDID":
                out_subs.append((b"EDID", edid.encode("utf-8") + b"\x00"))
                out_subs.append((b"VMAD", build_simple_vmad("HubrisOrbita7PickupItemScript")))
                vmad_added = True
            elif tag == b"FULL":
                out_subs.append((b"FULL", full.encode("utf-8") + b"\x00"))
            else:
                out_subs.append((tag, sb))
        if not vmad_added:
            out_subs.insert(0, (b"VMAD", build_simple_vmad("HubrisOrbita7PickupItemScript")))
        return make_record(b"MISC", fid, rebuild_subrecords(out_subs), flags=fl, fver=131, v2=v2)

    grup_misc = make_grup(
        b"MISC",
        clone_misc("misc_circuit", FID_MISC_COIL1, "MiscOrbita7CoilHubris", _t("Bobina Fotónica #1 (Azotea Hubris)", "Photonic Coil #1 (Hubris Roof)"))
        + clone_misc("misc_circuit", FID_MISC_COIL2, "MiscOrbita7CoilTrinity", _t("Bobina Fotónica #2 (Trinity Plaza)", "Photonic Coil #2 (Trinity Plaza)"))
        + clone_misc("misc_circuit", FID_MISC_COIL3, "MiscOrbita7CoilWRVR", _t("Bobina Fotónica #3 (Emisora WRVR)", "Photonic Coil #3 (WRVR Station)"))
        + clone_misc("misc_circuit", FID_MISC_GYRO, "MiscOrbita7ArcJetGyroCore", _t("Núcleo Giroscópico Sincrotrón ArcJet", "ArcJet Synchrotron Gyro Core"))
        + clone_misc("misc_idcard", FID_MISC_CARD, "MiscOrbita7ClaraStarCard", _t("Tarjeta Estelar Maestra de Clara Sterling", "Clara Sterling's Master Star Card")),
    )

    # 11. BOOK
    def make_dossier_book(fid: int, edid: str, full_name: str, desc_txt: str) -> bytes:
        book_body = (
            subrec_cstr(b"EDID", edid)
            + subrec(b"OBND", struct.pack("<6h", -13, -19, 0, 14, 0, 0))
            + subrec_cstr(b"FULL", full_name)
            + subrec_cstr(b"MODL", r"SetDressing\Office\FolderPapers02.nif")
            + subrec_cstr(b"DESC", desc_txt)
            + subrec(b"DATA", struct.pack("<B3sIf", 0, b"\x00\x00\x00", 25, 0.2))
            + subrec(b"DNAM", b"\x00" * 13)
            + subrec(b"INAM", struct.pack("<I", 0))
        )
        return make_record(b"BOOK", fid, book_body, fver=131)

    grup_book = make_grup(
        b"BOOK",
        b"".join(make_dossier_book(fid, edid, full, desc) for fid, edid, full, desc in data_mod.BOOK_DOSSIERS),
    )

    # 12. NOTE
    note_fl, _note_fv, note_v2, note_body = tpl["note_holo"]  # type: ignore[misc]
    note_recs = bytearray()
    for h in data_mod.CLARA_HOLOTAPES:
        nsubs = []
        for tag, sb in parse_subrecords(note_body):
            if tag in (b"VMAD", b"PTRN"):
                continue
            elif tag == b"EDID":
                nsubs.append((b"EDID", h["note_edid"].encode("utf-8") + b"\x00"))
            elif tag == b"FULL":
                nsubs.append((b"FULL", h["note_full"].encode("utf-8") + b"\x00"))
            elif tag == b"SNAM":
                nsubs.append((b"SNAM", struct.pack("<I", h["scen_fid"])))
            else:
                nsubs.append((tag, sb))
        note_recs += make_record(b"NOTE", h["note_fid"], rebuild_subrecords(nsubs), flags=note_fl, fver=131, v2=note_v2)
    grup_note = make_grup(b"NOTE", bytes(note_recs))

    # 13. CONT
    _c_fl, _c_fv, c_v2, c_body = tpl["cont_locker"]  # type: ignore[misc]

    def make_cont(
        fid: int,
        edid: str,
        full: str,
        items: list[tuple[int, int]],
        custom_nif: str | None = None,
        custom_obnd: tuple[int, int, int, int, int, int] | None = None,
    ) -> bytes:
        csubs: list[tuple[bytes, bytes]] = []
        wrote_items = False
        for tag, sb in parse_subrecords(c_body):
            if tag in (b"PTRN", b"MODT"):
                continue
            if tag == b"EDID":
                csubs.append((b"EDID", edid.encode("utf-8") + b"\x00"))
            elif tag == b"OBND" and custom_obnd:
                csubs.append((b"OBND", struct.pack("<6h", *custom_obnd)))
            elif tag == b"FULL":
                csubs.append((b"FULL", full.encode("utf-8") + b"\x00"))
            elif tag == b"MODL" and custom_nif:
                csubs.append((b"MODL", custom_nif.encode("utf-8") + b"\x00"))
            elif tag == b"COCT":
                if items:
                    csubs.append((b"COCT", struct.pack("<I", len(items))))
            elif tag == b"CNTO":
                if not wrote_items:
                    wrote_items = True
                    for item_fid, qty in items:
                        csubs.append((b"CNTO", struct.pack("<II", item_fid, qty)))
            elif tag == b"DATA":
                csubs.append((b"DATA", b"\x00\x00\x00\x00\x00"))  # Flags = 0 (Sin Respawn)
            else:
                csubs.append((tag, sb))
        return make_record(b"CONT", fid, rebuild_subrecords(csubs), flags=0, fver=131, v2=c_v2)

    grup_cont = make_grup(
        b"CONT",
        make_cont(
            FID_CONT_SAFE_CHEST,
            "ContOrbita7PlayerSafeChest",
            _t("Baúl Acorazado Estelar (Almacén Seguro)", "Armored Star Chest (Safe Storage)"),
            [],
            custom_nif=r"AeroArmor\Orbita7\Orbita7_StarChest.nif",
            custom_obnd=(-46, -26, 0, 46, 26, 54),
        )
        + make_cont(
            FID_CONT_HUBRIS,
            "ContOrbita7StashHubris",
            _t("Alijo Fotónico Hubris #1", "Hubris Photonic Cache #1"),
            [(FID_MISC_COIL1, 1), (data_mod.CLARA_HOLOTAPES[0]["note_fid"], 1)],
        )
        + make_cont(
            FID_CONT_TRINITY,
            "ContOrbita7StashTrinity",
            _t("Alijo Fotónico Hubris #2", "Hubris Photonic Cache #2"),
            [(FID_MISC_COIL2, 1), (0x01001160, 1)],
        )
        + make_cont(
            FID_CONT_WRVR,
            "ContOrbita7StashWRVR",
            _t("Alijo Fotónico Hubris #3", "Hubris Photonic Cache #3"),
            [(FID_MISC_COIL3, 1), (0x01001161, 1)],
        )
        + make_cont(
            FID_CONT_ARCJET,
            "ContOrbita7VaultArcJet",
            _t("Arca Blindada Sincrotrón (ArcJet)", "Armored Synchrotron Vault (ArcJet)"),
            [(FID_MISC_GYRO, 1), (data_mod.CLARA_HOLOTAPES[1]["note_fid"], 1), (0x01001162, 1)],
        )
        + make_cont(
            FID_CONT_FORT_HAGEN,
            "ContOrbita7VaultFortHagen",
            _t("Bóveda Satelital del Pentágono", "Pentagon Satellite Vault"),
            [(FID_MISC_CARD, 1), (data_mod.CLARA_HOLOTAPES[2]["note_fid"], 1)],
        ),
    )

    # 14. NPC_
    FACT_PLAYER_ALLY = 0x00106C30
    FACT_ROBOT = 0x00058304
    FACT_GUNNER = 0x00058303
    grup_npc = make_grup(
        b"NPC_",
        _clone_npc(tpl["npc_gutsy"], FID_NPC_CORONEL, "NPC_CoronelAgallasCosmos", _t("Coronel Agallas «Cosmos»", "Colonel Gutsy 'Cosmos'"), FID_VTYP_CORONEL, [(FACT_PLAYER_ALLY, 0)], aggressive=0, confidence=4, essential=True)  # type: ignore[arg-type]
        + _clone_npc(tpl["npc_kent"], FID_NPC_ARTIE, "NPC_ArtieVance", _t("Dr. Arturo «Artie» Vance", "Dr. Arthur 'Artie' Vance"), FID_VTYP_ARTIE, [(FACT_PLAYER_ALLY, 0)], aggressive=0, confidence=3, essential=True, doft_fid=FID_OTFT_ARTIE)  # type: ignore[arg-type]
        + _clone_npc(tpl["npc_kent"], FID_NPC_CLARA, "NPC_ClaraSterlingHolo", _t("Clara Sterling (Grabación 2077)", "Clara Sterling (2077 Recording)"), FID_VTYP_CLARA, [(FACT_PLAYER_ALLY, 0)], aggressive=0, confidence=2, essential=True, pkid_fid=None)  # type: ignore[arg-type]
        + _clone_npc(tpl["npc_gutsy_gunner01"], FID_NPC_SENTINEL_AJ, "NPC_SentinelArcJet", _t("Centinela de Seguridad ArcJet", "ArcJet Security Sentinel"), None, [(FACT_ROBOT, 0), (FACT_GUNNER, 0)], aggressive=2, confidence=4, essential=False, pkid_fid=None)  # type: ignore[arg-type]
        + _clone_npc(tpl["npc_gutsy_gunner02"], FID_NPC_GUARDIAN_AJ, "NPC_GuardianSincrotron", _t("Guardián del Sincrotrón ArcJet", "ArcJet Synchrotron Guardian"), None, [(FACT_ROBOT, 0), (FACT_GUNNER, 0)], aggressive=2, confidence=4, essential=False, pkid_fid=None)  # type: ignore[arg-type]
        + _clone_npc(tpl["npc_gutsy_gunner02"], FID_NPC_AUTOMATA_FH, "NPC_AutomataContratista", _t("Autómata Contratista del Pentágono", "Pentagon Contractor Automaton"), None, [(FACT_ROBOT, 0), (FACT_GUNNER, 0)], aggressive=2, confidence=4, essential=False, pkid_fid=None),  # type: ignore[arg-type]
    )

    # 15. MESG (ordenados por FormID)
    mesg_items: list[tuple[int, bytes]] = []
    for fid, edid, title, body, btns in data_mod.EXTRA_MESSAGES + data_mod.CLUE_MESSAGES + data_mod.EXAM_QUESTIONS:
        mesg_items.append((fid, _make_mesg_box(fid, edid, title, body, list(btns))))
    mesg_items.sort(key=lambda x: x[0])
    grup_mesg = make_grup(b"MESG", b"".join(rec for _, rec in mesg_items))

    # 16. QUST 0x01004000 + DIAL / INFO / SCEN
    q_subs = bytearray()
    q_subs += subrec_cstr(b"EDID", "HubrisOrbita7Quest")
    q_subs += subrec(b"VMAD", build_simple_vmad("HubrisOrbita7QuestScript"))
    q_subs += subrec_cstr(b"FULL", _t("El Legado de Hubris: Proyecto Astro-Cosmos", "The Hubris Legacy: Project Astro-Cosmos"))
    q_subs += subrec(b"DNAM", bytes.fromhex("11013c000000000007000000"))
    q_subs += subrec(b"XNAM", bytes.fromhex("588d1700"))
    q_subs += subrec(b"NEXT", b"")

    # Etapa 0 Start-Up (flag 0x02) + todas las etapas de QUEST_STAGES
    q_subs += subrec(b"INDX", struct.pack("<HBB", 0, 2, 0))
    q_subs += subrec(b"QSDT", b"\x00")
    for stg_id, qsdt_fl, cnam_txt in data_mod.QUEST_STAGES:
        q_subs += subrec(b"INDX", struct.pack("<HBB", stg_id, 0, 0))
        q_subs += subrec(b"QSDT", struct.pack("<B", qsdt_fl))
        q_subs += subrec_cstr(b"CNAM", cnam_txt)

    INTERIOR_ALIASES = {0, 1, 3, 4, 8, 10, 11, 13}
    for obj_id, obj_txt, obj_alias in data_mod.QUEST_OBJECTIVES:
        q_subs += subrec(b"QOBJ", struct.pack("<H", obj_id))
        q_subs += subrec(b"FNAM", struct.pack("<I", 0))
        q_subs += subrec_cstr(b"NNAM", obj_txt)
        if obj_id == 121:
            # Dentro de HubrisOrbita7Interior marca el Mural; fuera no marca la escotilla para no desviar el vuelo a Fort Hagen
            q_subs += subrec(b"QSTA", struct.pack("<III", obj_alias, 0, 0))
            q_subs += subrec(b"CTDA", make_ctda_getincurrentloc(1.0, FID_LCTN_ORBITA7))
        elif obj_alias in INTERIOR_ALIASES:
            # Fuera de LocHubrisOrbita7Studio -> marcar directamente la escotilla exterior (Alias 2)
            q_subs += subrec(b"QSTA", struct.pack("<III", 2, 0, 0))
            q_subs += subrec(b"CTDA", make_ctda_getincurrentloc(0.0, FID_LCTN_ORBITA7))
            # Dentro de LocHubrisOrbita7Studio -> marcar el objetivo interior real
            q_subs += subrec(b"QSTA", struct.pack("<III", obj_alias, 0, 0))
            q_subs += subrec(b"CTDA", make_ctda_getincurrentloc(1.0, FID_LCTN_ORBITA7))
        else:
            q_subs += subrec(b"QSTA", struct.pack("<III", obj_alias, 0, 0))

    aliases = [
        (0, "Alias_ArtieVance", 0x01002011),
        (1, "Alias_CoronelAgallas", 0x01002010),
        (2, "Alias_ExteriorHatch", 0x01003001),
        (3, "Alias_ExamConsole", 0x01002018),
        (4, "Alias_SuitPod", 0x01002015),
        (5, "Alias_StashHubris", 0x01003010),
        (6, "Alias_StashTrinity", 0x01003011),
        (7, "Alias_StashWRVR", 0x01003012),
        (8, "Alias_CarbinePedestal", 0x01002016),
        (9, "Alias_VaultArcJet", 0x01003020),
        (10, "Alias_PAFrame", 0x01002043),
        (11, "Alias_DirectorMural", 0x01002013),
        (12, "Alias_VaultFortHagen", 0x01003030),
        (13, "Alias_SolarReliquary", 0x01002017),
    ]
    q_subs += subrec(b"ANAM", struct.pack("<I", len(aliases)))
    for al_idx, al_name, al_refr in aliases:
        q_subs += subrec(b"ALST", struct.pack("<I", al_idx))
        q_subs += subrec_cstr(b"ALID", al_name)
        q_subs += subrec(b"FNAM", struct.pack("<I", 0x0000008A))
        q_subs += subrec(b"ALFR", struct.pack("<I", al_refr))
        q_subs += subrec(b"VTCK", struct.pack("<I", 0))
        q_subs += subrec(b"ALED", b"")

    qust_rec = make_record(b"QUST", FID_QUST_ORBITA7, bytes(q_subs), fver=131)

    # Helper para saludos GREE
    def build_gree_dial(dial_fid: int, edid: str, npc_fid: int, infos: list[dict]) -> bytes:
        d_subs = (
            subrec_cstr(b"EDID", edid)
            + subrec_cstr(b"FULL", "Greetings")
            + subrec(b"PNAM", struct.pack("<f", 75.0))
            + subrec(b"QNAM", struct.pack("<I", FID_QUST_ORBITA7))
            + subrec(b"DATA", bytes.fromhex("01077600"))
            + subrec(b"SNAM", b"GREE")
            + subrec(b"TIFC", struct.pack("<I", len(infos)))
        )
        d_rec = make_record(b"DIAL", dial_fid, d_subs, fver=131)
        i_recs = bytearray()
        for i_idx, gdef in enumerate(infos):
            expected_prev = 0 if i_idx == 0 else infos[i_idx - 1]["info_fid"]
            assert gdef["prev_fid"] == expected_prev, (
                f"Cadena PNAM rota en {edid}[{i_idx}] ({hex(gdef['info_fid'])}): "
                f"esperado {hex(expected_prev)}, recibido {hex(gdef['prev_fid'])}"
            )
            ib = bytearray()
            ib += subrec(b"ENAM", struct.pack("<I", gdef.get("enam_flags", 0)))
            ib += subrec(b"PNAM", struct.pack("<I", gdef["prev_fid"]))
            for r_idx, (sub_t, _tts_t) in enumerate(gdef["responses"], 1):
                ib += make_trda_block(r_idx, sub_t)
            for op_b, stg_f in gdef.get("stage_conds", []):
                ib += subrec(b"CTDA", make_ctda_getstage(op_b, stg_f, FID_QUST_ORBITA7))
            for op_b, g_val, g_fid in gdef.get("global_conds", []):
                ib += subrec(b"CTDA", make_ctda_getglobalvalue(op_b, g_val, g_fid))
            ib += subrec(b"CTDA", make_ctda_getisid(npc_fid))
            ib += subrec(b"ANAM", struct.pack("<I", npc_fid))
            if gdef.get("tsce_fid") is not None:
                ib += subrec(b"TSCE", struct.pack("<I", gdef["tsce_fid"]))
            if gdef.get("intv_phase") is not None:
                ib += subrec(b"INTV", struct.pack("<I", gdef["intv_phase"]))
            if gdef.get("tiqs_stage") is not None:
                ib += subrec(b"TIQS", struct.pack("<HH", 0xFFFF, gdef["tiqs_stage"]))
            ib += subrec_cstr(b"NAM0", gdef.get("nam0_phase", ""))
            ib += subrec(b"INAM", struct.pack("<I", 1))
            i_recs += make_record(b"INFO", gdef["info_fid"], bytes(ib), fver=131)
        return d_rec + make_grup(dial_fid, bytes(i_recs), group_type=7)

    artie_gree_block = build_gree_dial(FID_DIAL_ARTIE_GREE, "Orbita7ArtieGreeting", FID_NPC_ARTIE, data_mod.ARTIE_GREETING_INFOS)
    coronel_gree_block = build_gree_dial(FID_DIAL_CORONEL_GREE, "Orbita7CoronelGreeting", FID_NPC_CORONEL, data_mod.CORONEL_GREETING_INFOS)

    # CUST DIAL 0x01004003 (Barks del Coronel Agallas controlados por Global `0x01001001`)
    bark_dial_subs = (
        subrec_cstr(b"EDID", "Orbita7CoronelBarkTopic")
        + subrec(b"PNAM", struct.pack("<f", 50.0))
        + subrec(b"QNAM", struct.pack("<I", FID_QUST_ORBITA7))
        + subrec(b"DATA", bytes.fromhex("00000000"))
        + subrec(b"SNAM", b"CUST")
        + subrec(b"TIFC", struct.pack("<I", len(data_mod.CORONEL_BARK_INFOS)))
    )
    bark_dial_rec = make_record(b"DIAL", FID_DIAL_CORONEL_BARK, bark_dial_subs, fver=112)
    bark_infos = bytearray()
    for bdef in data_mod.CORONEL_BARK_INFOS:
        ib = bytearray()
        ib += subrec(b"ENAM", struct.pack("<I", 0))
        ib += subrec(b"PNAM", struct.pack("<I", bdef["prev_fid"]))
        for r_idx, (sub_t, _tts_t) in enumerate(bdef["responses"], 1):
            ib += make_trda_block(r_idx, sub_t)
        ib += subrec(b"CTDA", make_ctda_getglobalvalue(0x00, float(bdef["bark_id"]), FID_GLOB_BARK))
        ib += subrec(b"CTDA", make_ctda_getisid(FID_NPC_CORONEL))
        ib += subrec(b"ANAM", struct.pack("<I", FID_NPC_CORONEL))
        ib += subrec(b"NAM0", b"\x00")
        ib += subrec(b"INAM", struct.pack("<I", 1))
        bark_infos += make_record(b"INFO", bdef["info_fid"], bytes(ib), fver=131)
    coronel_bark_block = bark_dial_rec + make_grup(FID_DIAL_CORONEL_BARK, bytes(bark_infos), group_type=7)

    # Escenas interactivas con Artie Vance (ARTIE_SCENES)
    def make_scene_dial_grup(dial_fid: int, info_bytes: bytes, num_infos: int = 1, data_hex: str = "00020e00", fv: int = 48) -> bytes:
        d_subs = (
            subrec(b"PNAM", struct.pack("<f", 50.0))
            + subrec(b"QNAM", struct.pack("<I", FID_QUST_ORBITA7))
            + subrec(b"DATA", bytes.fromhex(data_hex))
            + subrec(b"SNAM", b"SCEN")
            + subrec(b"TIFC", struct.pack("<I", num_infos))
        )
        return make_record(b"DIAL", dial_fid, d_subs, fver=fv) + make_grup(dial_fid, info_bytes, group_type=7)

    scene_dials_buf = bytearray()
    scene_recs_buf = bytearray()

    for sdef in data_mod.ARTIE_SCENES:
        scen_fid = sdef["scen_fid"]
        sb = bytearray()
        sb += subrec_cstr(b"EDID", sdef["edid"])
        sb += subrec(b"FNAM", bytes.fromhex("24100000"))
        for ph_name in sdef["phases"]:
            sb += subrec(b"HNAM", b"")
            sb += subrec_cstr(b"NAM0", ph_name)
            sb += subrec(b"NEXT", b"")
            sb += subrec(b"NEXT", b"")
            sb += subrec(b"WNAM", struct.pack("<I", 450))
            sb += subrec(b"HNAM", b"")
        sb += subrec(b"ALID", struct.pack("<I", 0))
        sb += subrec(b"LNAM", struct.pack("<I", 0x00000004))
        sb += subrec(b"DNAM", struct.pack("<I", 0x0000000A))

        max_aidx = 1
        for act in sdef["actions"]:
            a_idx = act["action_idx"]
            if a_idx > max_aidx:
                max_aidx = a_idx
            ph_idx = act["phase_idx"]
            opts = act["options"]
            sb += subrec(b"ANAM", struct.pack("<H", 3))
            sb += subrec(b"NAM0", b"\x00")
            sb += subrec(b"ALID", struct.pack("<I", 0))
            sb += subrec(b"INAM", struct.pack("<I", a_idx))
            sb += subrec(b"FNAM", bytes.fromhex("00802200"))
            sb += subrec(b"SNAM", struct.pack("<I", ph_idx))
            sb += subrec(b"ENAM", struct.pack("<I", ph_idx))
            for k_tag, opt_i, field in (
                (b"PTOP", 0, "p_dial"), (b"NTOP", 1, "p_dial"), (b"NETO", 2, "p_dial"), (b"QTOP", 3, "p_dial"),
                (b"NPOT", 0, "n_dial"), (b"NNGT", 1, "n_dial"), (b"NNUT", 2, "n_dial"), (b"NQUT", 3, "n_dial"),
            ):
                sb += subrec(k_tag, struct.pack("<I", opts[opt_i][field]))
            sb += subrec(b"DTGT", struct.pack("<I", 0))
            sb += subrec(b"ANAM", b"")

            for opt in opts:
                if opt.get("p_info_f"):
                    pm = (
                        subrec(b"ENAM", struct.pack("<I", 0))
                        + subrec(b"PNAM", struct.pack("<I", 0))
                        + make_trda_block(1, opt["p_sub"])
                        + subrec(b"CTDA", make_ctda_player_sex(0))
                        + subrec_cstr(b"RNAM", opt["rnam"])
                        + subrec(b"NAM0", b"\x00")
                        + subrec(b"INAM", struct.pack("<I", 1))
                    )
                    pf = (
                        subrec(b"ENAM", struct.pack("<I", 0))
                        + subrec(b"PNAM", struct.pack("<I", opt["p_info"]))
                        + make_trda_block(1, opt["p_sub_f"])
                        + subrec(b"CTDA", make_ctda_player_sex(1))
                        + subrec_cstr(b"RNAM", opt["rnam_f"])
                        + subrec(b"NAM0", b"\x00")
                        + subrec(b"INAM", struct.pack("<I", 1))
                    )
                    prec = make_record(b"INFO", opt["p_info"], pm, fver=131) + make_record(b"INFO", opt["p_info_f"], pf, fver=131)
                    scene_dials_buf += make_scene_dial_grup(opt["p_dial"], prec, num_infos=2)
                else:
                    pm = (
                        subrec(b"ENAM", struct.pack("<I", 0))
                        + subrec(b"PNAM", struct.pack("<I", 0))
                        + make_trda_block(1, opt["p_sub"])
                        + subrec_cstr(b"RNAM", opt["rnam"])
                        + subrec(b"NAM0", b"\x00")
                        + subrec(b"INAM", struct.pack("<I", 1))
                    )
                    scene_dials_buf += make_scene_dial_grup(opt["p_dial"], make_record(b"INFO", opt["p_info"], pm, fver=131), num_infos=1)

                nb = bytearray()
                nb += subrec(b"ENAM", struct.pack("<I", 0))
                nb += subrec(b"PNAM", struct.pack("<I", 0))
                for r_idx, (sub_t, _tts_t) in enumerate(opt["n_responses"], 1):
                    nb += make_trda_block(r_idx, sub_t)
                if "tiqs_stage" in opt:
                    nb += subrec(b"TIQS", struct.pack("<HH", 0xFFFF, opt["tiqs_stage"]))
                nb += subrec(b"NAM0", b"\x00")
                nb += subrec(b"INAM", struct.pack("<I", 1))
                scene_dials_buf += make_scene_dial_grup(opt["n_dial"], make_record(b"INFO", opt["n_info"], bytes(nb), fver=131), num_infos=1)

        sb += subrec(b"PNAM", struct.pack("<I", FID_QUST_ORBITA7))
        sb += subrec(b"INAM", struct.pack("<I", max_aidx))
        sb += subrec(b"VNAM", struct.pack("<4I", 3, 3, 3, 3))
        sb += subrec(b"XNAM", struct.pack("<I", 0))
        scene_recs_buf += make_record(b"SCEN", scen_fid, bytes(sb), fver=119, v2=9)

    # Holocintas de Clara Sterling (NOTE -> SCEN Radio/Holotape basado en 0x001C037F)
    holo_dials_buf = bytearray()
    holo_scens_buf = bytearray()
    for h in data_mod.CLARA_HOLOTAPES:
        hb = bytearray()
        hb += subrec(b"ENAM", struct.pack("<I", 0))
        hb += subrec(b"PNAM", struct.pack("<I", 0))
        for r_idx, (sub_t, _tts_t) in enumerate(h["responses"], 1):
            hb += make_trda_block(r_idx, sub_t)
        hb += subrec(b"ANAM", struct.pack("<I", FID_NPC_CLARA))
        hb += subrec(b"NAM0", b"\x00")
        hb += subrec(b"INAM", struct.pack("<I", 1))
        h_info_rec = make_record(b"INFO", h["info_fid"], bytes(hb), fver=131, v2=3)
        holo_dials_buf += make_scene_dial_grup(h["dial_fid"], h_info_rec, num_infos=1, data_hex="00021100", fv=120)

        hs = bytearray()
        hs += subrec_cstr(b"EDID", h["scen_edid"])
        hs += subrec(b"FNAM", bytes.fromhex("04010000"))
        hs += subrec(b"HNAM", b"")
        hs += subrec(b"NAM0", b"\x00")
        hs += subrec(b"NEXT", b"")
        hs += subrec(b"NEXT", b"")
        hs += subrec(b"WNAM", struct.pack("<I", 350))
        hs += subrec(b"HNAM", b"")
        hs += subrec(b"ALID", struct.pack("<i", -2))
        hs += subrec(b"LNAM", struct.pack("<I", 0))
        hs += subrec(b"DNAM", struct.pack("<I", 0))
        hs += subrec(b"ANAM", struct.pack("<H", 6))  # Action Start Radio/Holotape Topic
        hs += subrec(b"NAM0", b"\x00")
        hs += subrec(b"ALID", struct.pack("<i", -2))
        hs += subrec(b"INAM", struct.pack("<I", 1))
        hs += subrec(b"SNAM", struct.pack("<I", 0))
        hs += subrec(b"ENAM", struct.pack("<I", 0))
        hs += subrec(b"DATA", struct.pack("<I", h["dial_fid"]))
        hs += subrec(b"HTID", struct.pack("<I", 0))
        hs += subrec(b"DMAX", struct.pack("<I", 0x00073265))  # SOMDialogue2D_Holotape
        hs += subrec(b"ANAM", b"")
        hs += subrec(b"PNAM", struct.pack("<I", FID_QUST_ORBITA7))
        hs += subrec(b"INAM", struct.pack("<I", 1))
        hs += subrec(b"VNAM", struct.pack("<4I", 3, 3, 3, 3))
        hs += subrec(b"XNAM", struct.pack("<I", 0))
        holo_scens_buf += make_record(b"SCEN", h["scen_fid"], bytes(hs), fver=120, v2=0)

    q_children = (
        artie_gree_block
        + coronel_gree_block
        + coronel_bark_block
        + bytes(scene_dials_buf)
        + bytes(holo_dials_buf)
        + bytes(scene_recs_buf)
        + bytes(holo_scens_buf)
    )
    qust_block = qust_rec + make_grup(FID_QUST_ORBITA7, q_children, group_type=10)
    grup_qust = make_grup(b"QUST", qust_block)

    # 17. Interior CELL 0x01002000 (Block 2, SubBlock 9) — Iluminación limpia sin niebla densa
    _v111_fl, _v111_fv, _v111_v2, v111_body = tpl["cell_v111"]  # type: ignore[misc]
    clean_xcll = bytearray(136)
    clean_xcll[0:4] = bytes([84, 80, 72, 0])          # Ambient cálido luminoso
    clean_xcll[4:8] = bytes([110, 104, 92, 0])        # Directional limpio
    clean_xcll[8:12] = bytes([36, 40, 48, 0])         # Fog Near Color
    struct.pack_into("<ffIIff", clean_xcll, 12, 12000.0, 32000.0, 0, 225, 1.0, 32000.0)
    struct.pack_into("<f", clean_xcll, 36, 1.0)       # Fog Power
    for off_d, rgba_d in ((40, (66, 63, 58, 0)), (44, (66, 63, 58, 0)), (48, (66, 63, 58, 0)), (52, (66, 63, 58, 0)), (56, (50, 48, 44, 0)), (60, (82, 78, 70, 0))):
        clean_xcll[off_d : off_d + 4] = bytes(rgba_d)
    struct.pack_into("<f", clean_xcll, 68, 1.0)       # Fresnel Power
    clean_xcll[72:76] = bytes([36, 40, 48, 0])        # Fog Far Color
    struct.pack_into("<fffII", clean_xcll, 76, 0.02, 14000.0, 16000.0, 0, 0)  # FogMax=0.02, LightFade=14000..16000, InheritFlags=0
    struct.pack_into("<f", clean_xcll, 96, 30000.0)
    clean_xcll[100:104] = bytes([36, 40, 48, 0])
    clean_xcll[104:108] = bytes([36, 40, 48, 0])
    struct.pack_into("<7f", clean_xcll, 108, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 30000.0)

    cell_subs: list[tuple[bytes, bytes]] = [
        (b"EDID", b"HubrisOrbita7Interior\x00"),
        (b"FULL", _t("Estudio Subterráneo Órbita-7", "Underground Studio Orbit-7").encode("utf-8") + b"\x00"),
        (b"DATA", b"\x01\x00"),  # Is Interior Cell (sin flag Public ni Respawn para refugio seguro)
        (b"XCLL", bytes(clean_xcll)),
        (b"LTMP", struct.pack("<I", 0x000300E2)),  # DefaultLightingTemplate (sin niebla criogénica)
    ]
    for tag, sb in parse_subrecords(v111_body):
        if tag in (b"XCLW", b"XCAS", b"XCMO"):
            cell_subs.append((tag, sb))
    cell_subs.append((b"XCIM", struct.pack("<I", 0x0017161E)))  # DefaultImageSpaceF4LUT (colores nítidos sin tinte azul)
    cell_subs.append((b"XLCN", struct.pack("<I", FID_LCTN_ORBITA7)))
    cell_rec = make_record(b"CELL", FID_CELL_INT, rebuild_subrecords(cell_subs), flags=0, fver=131, v2=0)

    # Referencias persistentes interiores (type=8)
    PI = 3.14159265
    HP = 1.57079633
    pers_int = bytearray()
    # Puerta de salida sur hacia el callejón trasero de Hubris Comics + portal navmesh XNDP + marcador COC
    pers_int += _make_refr(
        0x01002001,
        FID_DOOR_INT_EXIT,
        (0.0, -624.0, 0.0, 0.0, 0.0, 0.0),
        flags=0x00000400,
        xtel=struct.pack("<I6fII", 0x01003001, 7255.0, -18050.0, 885.0, 0.0, 0.0, -HP, 0, 0),
        extra_subs=[(b"XNDP", struct.pack("<II", FID_NAVM_INT, 2))],
    )
    pers_int += _make_refr(0x01002002, 0x00000032, (0.0, -480.0, 4.0, 0.0, 0.0, 0.0), flags=0x00000400)

    # Coronel Agallas y Artie Vance en la Rotonda Central
    pers_int += _make_achr(0x01002010, FID_NPC_CORONEL, (-150.0, 190.0, 4.0, 0.0, 0.0, PI))
    pers_int += _make_achr(0x01002011, FID_NPC_ARTIE, (170.0, 140.0, 4.0, 0.0, 0.0, PI))

    # Interactivos con scripts (mural en Sala del Director, consola heredada deshabilitada, nueva Terminal continua + mesa, y cápsulas/pedestales)
    pers_int += _make_refr(0x01002013, FID_ACTI_MURAL, (1040.0, -1236.0, 80.0, 0.0, 0.0, PI), flags=0x00000400)
    pers_int += _make_refr(0x01002014, FID_ACTI_EXAM_CONSOLE, (0.0, 280.0, 0.0, 0.0, 0.0, 0.0), flags=0x00000C00)
    pers_int += _make_refr(0x01002019, 0x0001820C, (0.0, 280.0, 0.0, 0.0, 0.0, 0.0), flags=0x00000400)
    pers_int += _make_refr(0x01002018, FID_TERM_EXAM_MAIN, (0.0, 280.0, 1.1, 0.0, 0.0, 0.0), flags=0x00000400)
    pers_int += _make_refr(0x01002015, FID_ACTI_SUIT_POD, (1350.0, 0.0, 0.0, 0.0, 0.0, HP), flags=0x00000400)
    pers_int += _make_refr(0x01002016, FID_ACTI_WEAP_PED, (-1040.0, 0.0, 0.0, 0.0, 0.0, -HP), flags=0x00000400)
    pers_int += _make_refr(0x01002017, FID_ACTI_SOLAR_REL, (560.0, 1620.0, 0.0, 0.0, 0.0, 0.0), flags=0x00000400)

    # 5 Barreras fotónicas progresivas (`0x01002021..2025`, habilitadas al inicio y desactivadas por Etapa)
    pers_int += _make_refr(0x01002021, FID_STAT_BARRIER, (1240.0, 0.0, 0.0, 0.0, 0.0, HP), flags=0x00000400)
    pers_int += _make_refr(0x01002022, FID_STAT_BARRIER, (-656.0, 0.0, 0.0, 0.0, 0.0, HP), flags=0x00000400)
    pers_int += _make_refr(0x01002023, FID_STAT_BARRIER, (0.0, 656.0, 0.0, 0.0, 0.0, 0.0), flags=0x00000400, scale=1.16)
    pers_int += _make_refr(0x01002024, FID_STAT_BARRIER, (560.0, 1500.0, 0.0, 0.0, 0.0, 0.0), flags=0x00000400)
    pers_int += _make_refr(0x01002025, FID_STAT_BARRIER, (1040.0, -432.0, 0.0, 0.0, 0.0, 0.0), flags=0x00000400)

    # Displays de armas 3D y Chasis Servoarmadura Astro-Cosmos (`0x01002042..2044`)
    pers_int += _make_refr(0x01002042, FID_STAT_CARB_DISP, (-1040.0, 0.0, 82.0, 0.0, 0.0, 0.0), flags=0x00000400, scale=1.15)
    pers_int += _make_refr(0x01002043, FID_FURN_PA_FRAME, (0.0, 1380.0, 12.5, 0.0, 0.0, 0.0), flags=0x00000C00)
    pers_int += _make_refr(0x01002044, FID_STAT_CANNON_DISP, (560.0, 1620.0, 88.0, 0.0, 0.0, 0.0), flags=0x00000400, scale=1.15)

    # Referencias temporales interiores (`0x01002050+`): arquitectura, pistas, terminales, muebles, mesas de trabajo, luces y NAVM
    temp_int = bytearray()
    temp_int += _build_navm_orbita7(FID_CELL_INT, FID_NAVM_INT, 0x01002001)
    temp_props: list[tuple[int, int, tuple[float, float, float, float, float, float]]] = [
        (0x01002050, FID_STAT_HALL, (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)),
        (0x01002051, FID_STAT_PLANETARIUM, (0.0, 0.0, 418.0, 0.0, 0.0, 0.0)),
        (0x01002052, FID_STAT_GANTRY, (0.0, 1380.0, 0.0, 0.0, 0.0, 0.0)),
        # Vitrinas y restirador de pistas en Rotonda y Ala Este abierta
        (0x01002053, FID_ACTI_VITRINE1, (-420.0, -220.0, 0.0, 0.0, 0.0, -HP)),
        (0x01002054, FID_ACTI_VITRINE2, (420.0, -220.0, 0.0, 0.0, 0.0, HP)),
        (0x01002055, FID_ACTI_DESK, (860.0, 260.0, 0.0, 0.0, 0.0, 0.0)),
        # Terminales sobre MetalTable01 (0x0001820C)
        (0x01002056, 0x0001820C, (1040.0, 270.0, 0.0, 0.0, 0.0, 0.0)),
        (0x01002057, FID_TERM_PROD_TV, (1040.0, 270.0, 1.1, 0.0, 0.0, 0.0)),
        (0x01002058, 0x0001820C, (-380.0, 360.0, 0.0, 0.0, 0.0, 0.0)),
        (0x01002059, FID_TERM_ARTIE_LAB, (-380.0, 360.0, 1.1, 0.0, 0.0, 0.0)),
        # Bancos de trabajo y mobiliario de refugio permanente en Sala del Director y talleres
        (0x0100205A, 0x0012F2F5, (860.0, -280.0, 0.0, 0.0, 0.0, PI)),      # WorkbenchChemistryA
        (0x0100205B, 0x0012EA9B, (-1180.0, -280.0, 0.0, 0.0, 0.0, PI)),    # WorkbenchArmorA
        (0x0100205C, 0x0017B3A4, (-520.0, 1480.0, 0.0, 0.0, 0.0, -HP)),    # workbenchWeaponsA
        (0x0100205D, 0x00157FEB, (-520.0, 1140.0, 0.0, 0.0, 0.0, -HP)),    # WorkbenchPowerArmor
        (0x0100205E, FID_STAT_BED_SHOW, (1280.0, -1060.0, 0.0, 0.0, 0.0, 0.0)),
        (0x0100205F, FID_FURN_DIRECTOR_BED, (820.0, -1060.0, 0.0, 0.0, 0.0, 0.0)),
        (0x01002060, FID_CONT_SAFE_CHEST, (1040.0, -1140.0, 0.0, 0.0, 0.0, PI)),
        (0x01002061, FID_STAT_DESK, (1040.0, -820.0, 0.0, 0.0, 0.0, 0.0)),
        # Flanqueo visual para bahías de barrera #1 (Ala Este) y #4 (Relicario Solar)
        (0x01002062, 0x0008C17D, (1240.0, 175.0, 0.0, 0.0, 0.0, HP)),     # Vault_Locker_01
        (0x01002063, 0x0008C17D, (1240.0, -175.0, 0.0, 0.0, 0.0, HP)),
        (0x01002064, 0x0008C17D, (390.0, 1620.0, 0.0, 0.0, 0.0, 0.0)),
        # Iluminación Art-Deco amplia y nítida (14 puntos de luz de gran radio cubriendo las 5 salas sin niebla)
        (0x01002070, FID_LIGH_STUDIO_CLEAN, (0.0, 0.0, 230.0, 0.0, 0.0, 0.0)),
        (0x01002071, FID_LIGH_STUDIO_WARM, (-340.0, -340.0, 260.0, 0.0, 0.0, 0.0)),
        (0x01002072, FID_LIGH_STUDIO_WARM, (340.0, -340.0, 260.0, 0.0, 0.0, 0.0)),
        (0x01002073, FID_LIGH_STUDIO_WARM, (-340.0, 340.0, 260.0, 0.0, 0.0, 0.0)),
        (0x01002074, FID_LIGH_STUDIO_WARM, (340.0, 340.0, 260.0, 0.0, 0.0, 0.0)),
        (0x01002075, FID_LIGH_STUDIO_CLEAN, (0.0, -520.0, 210.0, 0.0, 0.0, 0.0)),
        (0x01002076, FID_LIGH_STUDIO_WARM, (880.0, 0.0, 230.0, 0.0, 0.0, 0.0)),
        (0x01002077, FID_LIGH_STUDIO_CLEAN, (1260.0, 0.0, 230.0, 0.0, 0.0, 0.0)),
        (0x01002078, FID_LIGH_STUDIO_WARM, (-880.0, 0.0, 230.0, 0.0, 0.0, 0.0)),
        (0x01002079, FID_LIGH_STUDIO_CLEAN, (-1240.0, 0.0, 230.0, 0.0, 0.0, 0.0)),
        (0x0100207A, FID_LIGH_STUDIO_CLEAN, (0.0, 1020.0, 260.0, 0.0, 0.0, 0.0)),
        (0x0100207B, FID_LIGH_STUDIO_WARM, (0.0, 1480.0, 260.0, 0.0, 0.0, 0.0)),
        (0x0100207C, FID_LIGH_STUDIO_CYAN, (560.0, 1580.0, 220.0, 0.0, 0.0, 0.0)),
        (0x0100207D, FID_LIGH_STUDIO_WARM, (1040.0, -960.0, 230.0, 0.0, 0.0, 0.0)),
    ]
    for r_fid, b_fid, r_pos in temp_props:
        temp_int += _make_refr(r_fid, b_fid, r_pos, flags=0)

    cell_g8 = make_grup(FID_CELL_INT, bytes(pers_int), group_type=8)
    cell_g9 = make_grup(FID_CELL_INT, bytes(temp_int), group_type=9)
    cell_g6 = make_grup(FID_CELL_INT, cell_g8 + cell_g9, group_type=6)
    # Bloque 2, SubBloque 9 para FormID 0x01002000 (low = 8192 -> 8192%10=2, (8192//10)%10=9)
    cell_subblock = make_grup(9, cell_rec + cell_g6, group_type=3)
    cell_block = make_grup(2, cell_subblock, group_type=2)
    grup_cell = make_grup(b"CELL", cell_block, group_type=0)

    # 18. NAVI 0x00000FF1
    nvmi_int = (
        struct.pack("<II3fII", FID_NAVM_INT, 0, 0.0, 0.0, 0.0, 0, 0)
        + struct.pack("<IIB", 0, 0, 0)
        + bytes.fromhex("3ca0e9a5")
        + struct.pack("<II", 0, FID_CELL_INT)
    )
    navi_rec = make_record(
        b"NAVI",
        0x00000FF1,
        subrec(b"NVER", struct.pack("<I", 15)) + subrec(b"NVMI", nvmi_int),
        fver=131,
    )
    grup_navi = make_grup(b"NAVI", navi_rec)

    # 19. WRLD 0x0000003C (Commonwealth) -> Celda Persistente 0x00018AA2 (solo refs persistentes, 0 celdas de rejilla)
    ext_refs = bytearray()
    # Callejón trasero plano detrás de Hubris Comics (`SWflat2x4_01` Z=882.3, libre de muros y escombros)
    ext_refs += _make_refr(
        0x01003005,
        FID_STAT_EXT_PLINTH,
        (7165.0, -18095.0, 882.3, 0.0, 0.0, 0.0),
        flags=0x00000C00,
    )
    ext_refs += _make_refr(
        0x01003001,
        FID_DOOR_EXT_HATCH,
        (7165.0, -18095.0, 882.5, 0.0, 0.0, 0.0),
        flags=0x00000C00,
        xtel=struct.pack("<I6fII", 0x01002001, 0.0, -510.0, 4.0, 0.0, 0.0, 0.0, 0, 0),
    )
    ext_refs += _make_refr(
        0x01003004,
        0x00000034,  # FastTravel / HeadingMarker
        (7255.0, -18050.0, 885.0, 0.0, 0.0, -HP),
        flags=0x00000400,
    )
    ext_refs += _make_refr(
        0x01003002,
        0x00000010,  # MapMarker (FNAM=0x00 -> sin viaje rápido hasta visitar el estudio en persona)
        (7165.0, -18095.0, 940.0, 0.0, 0.0, 0.0),
        flags=0x00000C00,
        extra_subs=[
            (b"XMRK", b""),
            (b"FNAM", b"\x00"),
            (b"FULL", _t("Estudio Subterráneo Órbita-7", "Underground Studio Orbit-7").encode("utf-8") + b"\x00"),
            (b"TNAM", struct.pack("<H", 15)),
            (b"XRDS", struct.pack("<f", 950.0)),
            (b"XLKR", struct.pack("<II", 0, 0x01003004)),
        ],
    )
    ext_refs += _make_refr(0x01003003, 0x00056722, (7165.0, -18095.0, 932.0, 0.0, 0.0, 0.0), flags=0x00000C00)

    # Alijos de Misión 2 (azoteas de Boston)
    ext_refs += _make_refr(0x01003010, FID_CONT_HUBRIS, (7710.0, -18260.0, 2400.8, 0.0, 0.0, 0.0), flags=0x00000C00)
    ext_refs += _make_refr(0x01003011, FID_CONT_TRINITY, (3971.2, -24720.0, 1868.3, 0.0, 0.0, 0.0), flags=0x00000C00)
    ext_refs += _make_refr(0x01003012, FID_CONT_WRVR, (-39210.0, -56020.0, 2072.0, 0.0, 0.0, 0.0), flags=0x00000C00)

    # ArcJet Systems exterior + guardias (Misión 3)
    ext_refs += _make_refr(0x01003020, FID_CONT_ARCJET, (-68608.0, 19120.0, 4224.0, 0.0, 0.0, 0.0), flags=0x00000C00)
    ext_refs += _make_achr(0x01003021, FID_NPC_SENTINEL_AJ, (-68460.0, 18980.0, 4228.0, 0.0, 0.0, 0.0), flags=0x00000C00)
    ext_refs += _make_achr(0x01003022, FID_NPC_SENTINEL_AJ, (-68750.0, 18980.0, 4228.0, 0.0, 0.0, 0.0), flags=0x00000C00)
    ext_refs += _make_achr(0x01003023, FID_NPC_GUARDIAN_AJ, (-68608.0, 19280.0, 4228.0, 0.0, 0.0, PI), flags=0x00000C00)

    # Fort Hagen azotea satelital + autómatas (Misión 4)
    ext_refs += _make_refr(0x01003030, FID_CONT_FORT_HAGEN, (-86912.0, -4864.0, 6912.0, 0.0, 0.0, 0.0), flags=0x00000C00)
    ext_refs += _make_achr(0x01003031, FID_NPC_AUTOMATA_FH, (-86760.0, -5010.0, 6916.0, 0.0, 0.0, 0.0), flags=0x00000C00)
    ext_refs += _make_achr(0x01003032, FID_NPC_AUTOMATA_FH, (-87060.0, -5010.0, 6916.0, 0.0, 0.0, 0.0), flags=0x00000C00)
    ext_refs += _make_achr(0x01003033, FID_NPC_GUARDIAN_AJ, (-86912.0, -4710.0, 6916.0, 0.0, 0.0, PI), flags=0x00000C00)

    w_g8 = make_grup(0x00018AA2, bytes(ext_refs), group_type=8)
    w_g6 = make_grup(0x00018AA2, w_g8, group_type=6)
    w_g1 = make_grup(0x0000003C, bytes(tpl["cell_18aa2"]) + w_g6, group_type=1)  # type: ignore[arg-type]
    grup_wrld = make_grup(b"WRLD", bytes(tpl["wrld_003c"]) + w_g1, group_type=0)  # type: ignore[arg-type]

    def _make_ui_sndr(
        fid: int,
        edid: str,
        rel_wav_path: str,
        atten_centidb: int = 0,
        output_model_fid: int = 0x0007EDCA,  # SOMStereo (100% FL/FR 2D; nunca usar SOMUIDefault solo-centro)
    ) -> bytes:
        s_body = (
            subrec_cstr(b"EDID", edid)
            + subrec(b"CNAM", bytes.fromhex("0a54ef1e"))
            + subrec(b"GNAM", struct.pack("<I", 0x00238B2E))  # AudioCategorySFXNoPausing (suena sin pausa dentro de TerminalMenu)
            + subrec_cstr(b"ANAM", rel_wav_path)
            + subrec(b"ONAM", struct.pack("<I", output_model_fid))
            + subrec(b"LNAM", bytes.fromhex("00000000"))
            + subrec(b"BNAM", b"\x00\x00\x80\x00" + struct.pack("<H", atten_centidb))
        )
        return make_record(b"SNDR", fid, s_body, flags=0, fver=131, v2=0)

    def _make_soun(fid: int, edid: str, sndr_fid: int) -> bytes:
        so_body = (
            subrec_cstr(b"EDID", edid)
            + subrec(b"OBND", bytes.fromhex("e5ffe5fff4ff1b001b000c00"))
            + subrec(b"SDSC", struct.pack("<I", sndr_fid))
        )
        return make_record(b"SOUN", fid, so_body, flags=0, fver=131, v2=0)

    sndr_items: list[tuple[int, bytes]] = []
    soun_items: list[tuple[int, bytes]] = []
    for entry in data_mod.EXAM_AUDIO_VOICES:
        rel_wav = f"Data\\Sound\\FX\\AeroArmor\\Orbita7\\{entry['name']}.wav"
        sndr_items.append((entry["sndr_fid"], _make_ui_sndr(entry["sndr_fid"], entry["sndr_edid"], rel_wav, atten_centidb=0, output_model_fid=0x0007EDCA)))
        soun_items.append((entry["soun_fid"], _make_soun(entry["soun_fid"], entry["soun_edid"], entry["sndr_fid"])))
    for sfx_entry in data_mod.EXAM_SFX_DEFS:
        rel_wav = f"Data\\Sound\\FX\\AeroArmor\\Orbita7\\{sfx_entry['name']}.wav"
        sndr_items.append((sfx_entry["sndr_fid"], _make_ui_sndr(sfx_entry["sndr_fid"], sfx_entry["sndr_edid"], rel_wav, atten_centidb=250, output_model_fid=0x000D78B8)))
        soun_items.append((sfx_entry["soun_fid"], _make_soun(sfx_entry["soun_fid"], sfx_entry["soun_edid"], sfx_entry["sndr_fid"])))

    sndr_items.sort(key=lambda x: x[0])
    soun_items.sort(key=lambda x: x[0])
    grup_sndr = make_grup(b"SNDR", b"".join(rec for _, rec in sndr_items))
    grup_soun = make_grup(b"SOUN", b"".join(rec for _, rec in soun_items))

    return {
        b"GLOB": grup_glob,
        b"VTYP": grup_vtyp,
        b"LCTN": grup_lctn,
        b"OTFT": grup_otft,
        b"SOUN": grup_soun,
        b"SNDR": grup_sndr,
        b"STAT": grup_stat,
        b"ACTI": grup_acti,
        b"DOOR": grup_door,
        b"LIGH": grup_ligh,
        b"FURN": grup_furn,
        b"TERM": grup_term,
        b"MISC": grup_misc,
        b"BOOK": grup_book,
        b"NOTE": grup_note,
        b"CONT": grup_cont,
        b"NPC_": grup_npc,
        b"MESG": grup_mesg,
        b"QUST": grup_qust,
        b"CELL": grup_cell,
        b"NAVI": grup_navi,
        b"WRLD": grup_wrld,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Builder de misión Órbita-7 (ES / EN).")
    parser.add_argument("--lang", choices=("es", "en"), default="es", help="Idioma objetivo (es | en).")
    parser.add_argument("--voices", action="store_true", help="Sintetiza voces .fuz/.xwm y audio de examen.")
    parser.add_argument("--exam-audio", action="store_true", help="Sintetiza únicamente el audio del examen.")
    args = parser.parse_args()

    if args.voices:
        synthesize_orbita7_voices(args.lang)
        synthesize_orbita7_exam_audio(args.lang)
    elif args.exam_audio:
        synthesize_orbita7_exam_audio(args.lang)
    else:
        grups = build_orbita7_esp_grups(args.lang)
        print(f"[ORBITA7:{args.lang.upper()}] GRUPs generados:", {k.decode(): len(v) for k, v in grups.items()})
