# Credits, Licenses & Open Modding Policy / Créditos, Licencias y Política de Modding Abierto

## 1. Open Modding Commitment / Compromiso de Modding Abierto (100% Open Permissions)
**Project Astro-Cosmos — Fly Over the Commonwealth** (`AeroArmorMod.esp`, both the **English Standalone Edition** and the **Spanish Standalone Edition**) is released under the **MIT License** with **100% Open Modding Permissions**:
- **Modification, Asset Use, Translation & Redistribution:** Explicitly **OPEN**. Any member of the community may inspect, study, modify, translate, port, integrate, or redistribute this mod, its binary Python compilers, Havok animation pipeline, Papyrus scripts, custom 3D `.nif` meshes, `.bgsm` materials, and `.dds` textures freely, provided credit to the original author (`0utKast`) is included.
- **Zero Creation Club / Zero DLC / Zero F4SE / Universal Compatibility (`1.10.163` + Next-Gen/AE):** Built natively with **`HEDR v1.00`** (`FormIDs >= 0x800`) and **`BTDX BA2 v1`** (`GNRL v1` & `DX10 v1`), requiring strictly base `Fallout4.esm`. This project rejects artificial version lock-outs, paid *Creations* gating, or closed modding ecosystems.
- **100% Standalone (Zero Third-Party Mod Dependencies):** All custom interior geometry, flight/combat animations, 3D PBR suits/weapons, Papyrus scripts, and voice acting were built from scratch or derived strictly from base `Fallout4.esm` records, requiring zero external mod downloads.

---

## 2. Full Attribution Table / Tabla Completa de Reconocimiento y Autoría

| Component / Componente | Author / Autor Original | License / Permisos | Notes & Reference / Notas y Referencia |
| :--- | :--- | :--- | :--- |
| **True 3D Free-Flight Engine, `8` Aerodynamic Regimes, `714` Custom 64-bit Havok `.hkx` Clips, Additive Subgraph (`SADD`) Injection & `10` Papyrus Scripts** | **OutKast (`0utKast`)** | **MIT License (100% Open Permissions)** | https://github.com/0utKast/fallout4-project-astro-cosmos (`src/build_aero_animations.py`, `src/aero_flight_animations.xml`, `src/update_aero_esp.py`, `src/papyrus_*/*.psc`) |
| **Custom 3D PBR Equipment, Weapons & Underground Studio Orbit-7 Architecture (`49` `.nif`, `31` `.bgsm`, `90` `.dds` per edition)** | **OutKast (`0utKast`)** | **MIT License (100% Open Permissions)** | Procedural & sculpted 3D assets generated via `src/generate_cosmos_hero_assets.py`, `src/generate_cosmos_hero_weapon.py`, `src/generate_cosmos_pa_assets.py`, `src/generate_cosmos_pa_weapon.py`, and `src/generate_orbita7_studio_assets.py`. |
| **Binary `.esp` / `.ba2` Compiler, `4` Voiced Quests, Interactive Security Exams & Localized Editions (EN & ES)** | **OutKast (`0utKast`)** | **MIT License (100% Open Permissions)** | `src/build_hubris_orbita7_quest.py`, `src/hubris_orbita7_data_en.py`, `src/hubris_orbita7_data_es.py`, and `package_astro_release.py`. |
| **Base Game Engine, Vanilla Skeleton/Behavior Graphs & *Captain Cosmos / Hubris Comics* Universe Lore** | **Bethesda Game Studios** | Official Base Game (`Fallout4.esm` required) | Zero Creation Club (`cc*`) and zero DLC plugins required. Vanilla skeleton/behavior references use base `Fallout4.esm` only. |
| **Studio Neural Voice Acting (`197` Lip-Synced `.fuz` Lines + `60` Terminal Audio Clips per Language)** | **Synthesized by `0utKast`** (via ElevenLabs + `ffmpeg` DSP + `xwmaencode` + LipFuzer) | **100% Open Redistribution in Mod** | Distinct character filtering and lip-sync across Dr. Arthur "Artie" Vance, Colonel Gutsy "Cosmos", Clara Sterling (2077 holotapes), and Player voices in both English and Spanish. |
| **Promotional Trailer Soundtrack (*Project Astro-Cosmos* Official Trailer)** | **Created & Mixed by `0utKast`** (Suno AI *Cosmos* Suite + ElevenLabs announcers) | Trailer Media | Promotional music included in trailer video; not bundled inside the `.ba2` gameplay archives. |
