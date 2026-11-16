#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hubris_orbita7_data_es.py
=========================
Datos narrativos, diálogos interactivos con voz, ladridos/insultos chusqueros del
Coronel Agallas «Cosmos», holocintas con voz de Clara Sterling, terminales, dossieres
y preguntas de los 4 exámenes para «El Legado de Hubris: Proyecto Astro-Cosmos» (ES).

Diseñado como diccionario modular por idioma para facilitar la futura generación EN.
"""

# Voces en ElevenLabs (eleven_multilingual_v2):
CORONEL_VTYP = "NPCMCoronelAgallasCosmos"
ARTIE_VTYP = "NPCMArtieVance"
CLARA_VTYP = "NPCFClaraSterlingHolo"
PLAYER_MALE_VTYP = "PlayerVoiceMale01"
PLAYER_FEMALE_VTYP = "PlayerVoiceFemale01"

CORONEL_VOICE_ID = "pqHfZKP75CvOlQylNhV4"      # Bill — sargento chusquero atronador (Mister Gutsy)
ARTIE_VOICE_ID = "N2lVS1w4EtoT3dr4eOWO"        # Callum — ingeniero necrófago lúcido de preguerra
CLARA_VOICE_ID = "XrExE9yKIg1WjnnlVkGX"        # Matilda — guionista jefa Clara Sterling (holocintas 2077)
PLAYER_MALE_VOICE_ID = "cjVigY5qzO86Huf0OWal"  # Eric — Único Superviviente (Nate)
PLAYER_FEMALE_VOICE_ID = "EXAVITQu4vr4xnSDxMaL"  # Sarah — Única Superviviente (Nora)

# ==============================================================================
# 1. SALUDOS INICIALES DE ARTURO «ARTIE» VANCE (DIAL 0x01004001, GREE)
# ==============================================================================
ARTIE_GREETING_INFOS = [
    # Etapa 15 -> Abre Escena 1 (Bienvenida a Órbita-7 y Misión 1)
    {
        "info_fid": 0x01004010,
        "prev_fid": 0x00000000,
        "enam_flags": 0x00,
        "stage_conds": [(0x00, 15.0)],
        "tsce_fid": 0x01004100,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "¡Santo cielo, un rostro humano que no intenta dispararme! Baja el arma, camarada, estás en territorio amigo.",
                "¡Santo cielo, un rostro humano que no intenta dispararme! Baja el arma, camarada, estás en territorio amigo.",
            ),
            (
                "Bienvenido al Estudio Subterráneo Órbita-7 de Hubris Comics. Soy Arturo Vance... aunque aquí abajo todos me llamaban Artie.",
                "Bienvenido al Estudio Subterráneo Órbita Siete de Hubris Comics. Soy Arturo Vance... aunque aquí abajo todos me llamaban Artie.",
            ),
        ],
    },
    # Etapa 20 -> Recordatorio durante Misión 1 (2 variantes aleatorias)
    {
        "info_fid": 0x01004011,
        "prev_fid": 0x01004010,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 20.0)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "Revisa la vitrina del Capitán Cosmos aquí en la Rotonda, y el restirador y el terminal de Clara en la Sala de Guionistas del este. Con esas tres pistas aprobarás el examen del Coronel.",
                "Revisa la vitrina del Capitán Cosmos aquí en la Rotonda, y el restirador y el terminal de Clara en la Sala de Guionistas del este. Con esas tres pistas aprobarás el examen del Coronel.",
            ),
        ],
    },
    {
        "info_fid": 0x01004701,
        "prev_fid": 0x01004011,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 20.0)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "El Coronel Agallas no perdona ni una sola coma, camarada. Lee las tres pistas entre la Rotonda y la Sala de Guionistas antes de abrir su terminal de examen.",
                "El Coronel Agallas no perdona ni una sola coma, camarada. Lee las tres pistas entre la Rotonda y la Sala de Guionistas antes de abrir su terminal de examen.",
            ),
        ],
    },
    # Etapa 30 -> Examen 1 aprobado: reclamar el Traje de Vuelo (2 variantes)
    {
        "info_fid": 0x01004702,
        "prev_fid": 0x01004701,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 30.0)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "¡La barrera de la cápsula acaba de caer! Recoge el Traje de Vuelo Astro-Cosmos de su vitrina y pruébatelo.",
                "¡La barrera de la cápsula acaba de caer! Recoge el Traje de Vuelo Astro-Cosmos de su vitrina y pruébatelo.",
            ),
        ],
    },
    {
        "info_fid": 0x01004703,
        "prev_fid": 0x01004702,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 30.0)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "Bien jugado ante el Coronel. Acércate a la cápsula de estasis aquí en la Rotonda y reclama tu Traje de Vuelo Astro-Cosmos.",
                "Bien jugado ante el Coronel. Acércate a la cápsula de estasis aquí en la Rotonda y reclama tu Traje de Vuelo Astro-Cosmos.",
            ),
        ],
    },
    # Etapa 35 -> Abre Escena 2 (Traje reclamado -> Misión 2 Patrulla sobre los Tejados)
    {
        "info_fid": 0x01004012,
        "prev_fid": 0x01004703,
        "enam_flags": 0x00,
        "stage_conds": [(0x00, 35.0)],
        "tsce_fid": 0x01004200,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "¡Mírate nada más! Doscientos diez años esperando y el Traje de Vuelo Astro-Cosmos sigue brillando como recién salido del taller.",
                "¡Mírate nada más! Doscientos diez años esperando y el Traje de Vuelo Astro-Cosmos sigue brillando como recién salido del taller.",
            ),
            (
                "Acércate, piloto: ahora que puedes volar, ha llegado el momento de despertar el Laboratorio Fotónico.",
                "Acércate, piloto: ahora que puedes volar, ha llegado el momento de despertar el Laboratorio Fotónico.",
            ),
        ],
    },
    # Etapa 40 (0 bobinas recuperadas) -> Misión 2 inicio (2 variantes)
    {
        "info_fid": 0x01004013,
        "prev_fid": 0x01004012,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 40.0)],
        "global_conds": [(0x00, 0.0, 0x01001003)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "Las tres Bobinas Fotónicas siguen en las azoteas de Hubris Comics, Trinity Plaza y la emisora WRVR. Vuela hasta allí, escucha la holocinta de Clara y lee los expedientes antes de examinarte.",
                "Las tres Bobinas Fotónicas siguen en las azoteas de Hubris Comics, Trinity Plaza y la emisora \"uve doble e erre uve erre\",. Vuela hasta allí, escucha la holocinta de Clara y lee los expedientes antes de examinarte.",
            ),
        ],
    },
    {
        "info_fid": 0x01004704,
        "prev_fid": 0x01004013,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 40.0)],
        "global_conds": [(0x00, 0.0, 0x01001003)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "Todavía no detecto ninguna Bobina Fotónica en tu equipo. Surca los tejados de Hubris Comics, Trinity Plaza y WRVR cuando estés listo.",
                "Todavía no detecto ninguna Bobina Fotónica en tu equipo. Surca los tejados de Hubris Comics, Trinity Plaza y la emisora \"uve doble e erre uve erre\", cuando estés listo.",
            ),
        ],
    },
    # Etapa 40 (1 bobina recuperada) -> Avance parcial (2 variantes)
    {
        "info_fid": 0x01004705,
        "prev_fid": 0x01004704,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 40.0)],
        "global_conds": [(0x00, 1.0, 0x01001003)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "¡Mis sensores ya detectan la primera Bobina Fotónica en tu equipo! Aún te quedan dos tejados de Boston por sobrevolar antes del examen.",
                "¡Mis sensores ya detectan la primera Bobina Fotónica en tu equipo! Aún te quedan dos tejados de Boston por sobrevolar antes del examen.",
            ),
        ],
    },
    {
        "info_fid": 0x01004706,
        "prev_fid": 0x01004705,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 40.0)],
        "global_conds": [(0x00, 1.0, 0x01001003)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "Ya llevas una bobina asegurada, piloto. Faltan dos azoteas más para reunir los tres componentes y los dossieres de Clara.",
                "Ya llevas una bobina asegurada, piloto. Faltan dos azoteas más para reunir los tres componentes y los dossieres de Clara.",
            ),
        ],
    },
    # Etapa 40 (2 bobinas recuperadas) -> Falta solo una (2 variantes)
    {
        "info_fid": 0x01004707,
        "prev_fid": 0x01004706,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 40.0)],
        "global_conds": [(0x60, 2.0, 0x01001003)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "¡Dos Bobinas Fotónicas vibran ya en tu mochila! Solo te falta conquistar la última azotea y memorizar el código de Los Imparables.",
                "¡Dos Bobinas Fotónicas vibran ya en tu mochila! Solo te falta conquistar la última azotea y memorizar el código de Los Imparables.",
            ),
        ],
    },
    {
        "info_fid": 0x01004708,
        "prev_fid": 0x01004707,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 40.0)],
        "global_conds": [(0x60, 2.0, 0x01001003)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "Un tejado más y completamos el lote, compañero. Recupera la tercera bobina ahí arriba y el Coronel te estará esperando.",
                "Un tejado más y completamos el lote, compañero. Recupera la tercera bobina ahí arriba y el Coronel te estará esperando.",
            ),
        ],
    },
    # Etapa 50 -> Las 3 Bobinas Fotónicas reunidas: ir al Examen 2 (2 variantes)
    {
        "info_fid": 0x01004709,
        "prev_fid": 0x01004708,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 50.0)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "¡Traes las tres Bobinas Fotónicas contigo! Repasa las pistas que recuperaste allá arriba y supera el segundo examen en la consola.",
                "¡Traes las tres Bobinas Fotónicas contigo! Repasa las pistas que recuperaste allá arriba y supera el segundo examen en la consola.",
            ),
        ],
    },
    {
        "info_fid": 0x0100470A,
        "prev_fid": 0x01004709,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 50.0)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "Con las tres bobinas en tu poder ya no tienes que volver a ningún tejado. Enfréntate al Coronel Agallas en el Examen de Patrulla Aérea.",
                "Con las tres bobinas en tu poder ya no tienes que volver a ningún tejado. Enfréntate al Coronel Agallas en el Examen de Patrulla Aérea.",
            ),
        ],
    },
    # Etapa 60 -> Examen 2 aprobado: reclamar la Carabina (2 variantes)
    {
        "info_fid": 0x0100470B,
        "prev_fid": 0x0100470A,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 60.0)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "El Laboratorio Fotónico ya está abierto. Recoge tu Carabina de Rayos Astro-Cosmos del pedestal; pronto verás que funciona en vuelo con el traje y con la servoarmadura.",
                "El Laboratorio Fotónico ya está abierto. Recoge tu Carabina de Rayos Astro-Cosmos del pedestal; pronto verás que funciona en vuelo con el traje y con la servoarmadura.",
            ),
        ],
    },
    {
        "info_fid": 0x0100470C,
        "prev_fid": 0x0100470B,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 60.0)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "¡Segundo examen superado! Entra al Laboratorio Fotónico y reclama la Carabina de Rayos antes de pasar a la siguiente misión.",
                "¡Segundo examen superado! Entra al Laboratorio Fotónico y reclama la Carabina de Rayos antes de pasar a la siguiente misión.",
            ),
        ],
    },
    # Etapa 65 -> Abre Escena 3 (Carabina reclamada -> Misión 3 Operación Titán Estelar en ArcJet)
    {
        "info_fid": 0x01004014,
        "prev_fid": 0x0100470C,
        "enam_flags": 0x00,
        "stage_conds": [(0x00, 65.0)],
        "tsce_fid": 0x01004300,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "Esa Carabina de Rayos Astro-Cosmos en tus manos es música para mis viejos ojos radiactivos.",
                "Esa Carabina de Rayos Astro-Cosmos en tus manos es música para mis viejos ojos radiactivos.",
            ),
            (
                "Y vas a necesitar su mira de seis aumentos desde el aire, porque el siguiente paso nos lleva directo a la cubierta superior de ArcJet Systems.",
                "Y vas a necesitar su mira de seis aumentos desde el aire, porque el siguiente paso nos lleva directo a la cubierta superior de ArcJet Systems.",
            ),
        ],
    },
    # Etapa 70 -> Misión 3 en curso (2 variantes)
    {
        "info_fid": 0x01004015,
        "prev_fid": 0x01004014,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 70.0)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "Vuela hasta el tejado más alto de ArcJet Systems, abate a los centinelas desde el aire con tu carabina y trae el Núcleo Sincrotrón junto con el borrador del número cincuenta.",
                "Vuela hasta el tejado más alto de ArcJet Systems, abate a los centinelas desde el aire con tu carabina y trae el Núcleo Sincrotrón junto con el borrador del número cincuenta.",
            ),
        ],
    },
    {
        "info_fid": 0x0100470D,
        "prev_fid": 0x01004015,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 70.0)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "El Núcleo Sincrotrón sigue en la cubierta más alta de ArcJet Systems. No te olvides de leer el borrador censurado del Capitán Cosmos que dejaron allí arriba.",
                "El Núcleo Sincrotrón sigue en la cubierta más alta de ArcJet Systems. No te olvides de leer el borrador censurado del Capitán Cosmos que dejaron allí arriba.",
            ),
        ],
    },
    # Etapa 80 -> Núcleo Sincrotrón recuperado: ir al Examen 3 (2 variantes)
    {
        "info_fid": 0x0100470E,
        "prev_fid": 0x0100470D,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 80.0)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "¡Escucho zumbar ese Núcleo Sincrotrón desde aquí! Ya sobreviviste a ArcJet: revisa las notas del número cincuenta y pásate por la consola del Coronel.",
                "¡Escucho zumbar ese Núcleo Sincrotrón desde aquí! Ya sobreviviste a ArcJet: revisa las notas del número cincuenta y pásate por la consola del Coronel.",
            ),
        ],
    },
    {
        "info_fid": 0x0100470F,
        "prev_fid": 0x0100470E,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 80.0)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "Has vuelto de ArcJet de una pieza y con el núcleo a cuestas. Supera ahora el Examen de Piloto Orbital y abriré el Hangar Norte.",
                "Has vuelto de ArcJet de una pieza y con el núcleo a cuestas. Supera ahora el Examen de Piloto Orbital y abriré el Hangar Norte.",
            ),
        ],
    },
    # Etapa 100 -> Examen 3 aprobado: reclamar la Servoarmadura Astro-Cosmos (2 variantes)
    {
        "info_fid": 0x01004710,
        "prev_fid": 0x0100470F,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 100.0)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "¡Escucha esas compuertas ceder! La Servoarmadura Astro-Cosmos te espera completa y operativa en el Hangar Orbital Norte.",
                "¡Escucha esas compuertas ceder! La Servoarmadura Astro-Cosmos te espera completa y operativa en el Hangar Orbital Norte.",
            ),
        ],
    },
    {
        "info_fid": 0x01004711,
        "prev_fid": 0x01004710,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 100.0)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "¡Objetivo logrado, piloto! Entra al Hangar Orbital Norte y enfúndate la Servoarmadura Astro-Cosmos.",
                "¡Objetivo logrado, piloto! Entra al Hangar Orbital Norte y enfúndate la Servoarmadura Astro-Cosmos.",
            ),
        ],
    },
    # Etapa 110 -> Abre Escena 4 (Servoarmadura reclamada -> Misión 4 Sala del Director + Fort Hagen)
    {
        "info_fid": 0x01004016,
        "prev_fid": 0x01004711,
        "enam_flags": 0x00,
        "stage_conds": [(0x00, 110.0)],
        "tsce_fid": 0x01004400,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "¡Por las barbas de Jangles! Ver caminar de nuevo la Servoarmadura Astro-Cosmos bajo esta cúpula hace que hayan valido la pena dos siglos de soledad.",
                "¡Por las barbas de Jangles! Ver caminar de nuevo la Servoarmadura Astro-Cosmos bajo esta cúpula hace que hayan valido la pena dos siglos de soledad.",
            ),
            (
                "Solo queda un último misterio por resolver, amigo mío: el destino final de Clara Sterling y el Relicario Solar.",
                "Solo queda un último misterio por resolver, amigo mío: el destino final de Clara Sterling y el Relicario Solar.",
            ),
        ],
    },
    # Etapa 120 (Mural aún no inspeccionado) -> Sala del Director + Fort Hagen (2 variantes)
    {
        "info_fid": 0x01004017,
        "prev_fid": 0x01004016,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 120.0)],
        "global_conds": [(0x00, 0.0, 0x01001005)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "He abierto la Sala del Director al sur del ala de guionistas: memoriza el lema del gran mural, y luego vuela con tu servoarmadura al tejado satelital de Fort Hagen a por la tarjeta maestra de Clara.",
                "He abierto la Sala del Director al sur del ala de guionistas: memoriza el lema del gran mural, y luego vuela con tu servoarmadura al tejado satelital de Fort Hagen a por la tarjeta maestra de Clara.",
            ),
        ],
    },
    {
        "info_fid": 0x01004712,
        "prev_fid": 0x01004017,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 120.0)],
        "global_conds": [(0x00, 0.0, 0x01001005)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "Antes de despegar rumbo a Fort Hagen, entra en la Sala del Director y lee el Gran Mural del Juramento Estelar; lo necesitarás en la prueba final.",
                "Antes de despegar rumbo a Fort Hagen, entra en la Sala del Director y lee el Gran Mural del Juramento Estelar; lo necesitarás en la prueba final.",
            ),
        ],
    },
    # Etapa 120 (Mural YA inspeccionado) -> Solo Fort Hagen pendiente (2 variantes)
    {
        "info_fid": 0x01004713,
        "prev_fid": 0x01004712,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 120.0)],
        "global_conds": [(0x60, 1.0, 0x01001005)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "Ya memorizaste el Juramento Estelar del Gran Mural. Ahora solo te falta volar hasta el tejado satelital de Fort Hagen a por la Tarjeta Estelar Maestra de Clara.",
                "Ya memorizaste el Juramento Estelar del Gran Mural. Ahora solo te falta volar hasta el tejado satelital de Fort Hagen a por la Tarjeta Estelar Maestra de Clara.",
            ),
        ],
    },
    {
        "info_fid": 0x01004714,
        "prev_fid": 0x01004713,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 120.0)],
        "global_conds": [(0x60, 1.0, 0x01001005)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "Perfecto, el lema del mural ya está en tu memoria. Pon rumbo al tejado de Fort Hagen cuando quieras, ya sea con el traje o con la servoarmadura.",
                "Perfecto, el lema del mural ya está en tu memoria. Pon rumbo al tejado de Fort Hagen cuando quieras, ya sea con el traje o con la servoarmadura.",
            ),
        ],
    },
    # Etapa 140 -> Tarjeta Maestra recuperada: ir al Examen 4 (2 variantes)
    {
        "info_fid": 0x01004715,
        "prev_fid": 0x01004714,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 140.0)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "Ya tienes la Tarjeta Estelar Maestra de Clara. Escucha con calma su última holocinta y preséntate al Examen Maestro ante el Coronel Agallas.",
                "Ya tienes la Tarjeta Estelar Maestra de Clara. Escucha con calma su última holocinta y preséntate al Examen Maestro ante el Coronel Agallas.",
            ),
        ],
    },
    {
        "info_fid": 0x01004716,
        "prev_fid": 0x01004715,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 140.0)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "Por fin conocemos el último sacrificio de Clara Sterling. Acércate a la consola de exámenes para recibir el rango de Capitán del Cosmos.",
                "Por fin conocemos el último sacrificio de Clara Sterling. Acércate a la consola de exámenes para recibir el rango de Capitán del Cosmos.",
            ),
        ],
    },
    # Etapa 160 -> Examen 4 aprobado: reclamar Cañón Orbital Gauss (2 variantes)
    {
        "info_fid": 0x01004717,
        "prev_fid": 0x01004716,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 160.0)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "¡La última barrera ha caído! El Relicario Solar guarda el Cañón Orbital Gauss Astro-Cosmos, listo para disparar en vuelo tanto con el traje como con la servoarmadura.",
                "¡La última barrera ha caído! El Relicario Solar guarda el Cañón Orbital Gauss Astro-Cosmos, listo para disparar en vuelo tanto con el traje como con la servoarmadura.",
            ),
        ],
    },
    {
        "info_fid": 0x01004718,
        "prev_fid": 0x01004717,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 160.0)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "¡Eres todo un Capitán del Cosmos! Recoge el Cañón Orbital Gauss del Relicario Solar y habla conmigo para entregarte el estudio.",
                "¡Eres todo un Capitán del Cosmos! Recoge el Cañón Orbital Gauss del Relicario Solar y habla conmigo para entregarte el estudio.",
            ),
        ],
    },
    # Etapa 165 -> Abre Escena 5 (Epílogo: entrega permanente del Estudio Órbita-7)
    {
        "info_fid": 0x01004018,
        "prev_fid": 0x01004718,
        "enam_flags": 0x00,
        "stage_conds": [(0x00, 165.0)],
        "tsce_fid": 0x01004500,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "Lo has conseguido... El Traje, la Carabina Fotónica, la Servoarmadura Orbital y el Cañón Gauss Solar. El sueño entero de Clara está vivo en tus manos.",
                "Lo has conseguido... El Traje, la Carabina Fotónica, la Servoarmadura Orbital y el Cañón Gauss Solar. El sueño entero de Clara está vivo en tus manos.",
            ),
        ],
    },
    # Etapa 200+ -> Saludos permanentes de aliado residente en tu Refugio Órbita-7 (3 variantes)
    {
        "info_fid": 0x01004019,
        "prev_fid": 0x01004018,
        "enam_flags": 0x02,
        "stage_conds": [(0x60, 200.0)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "Bienvenido a casa, Capitán del Cosmos. Los talleres, los baúles estelares y tu cama espacial están a punto, y el Coronel y yo mantendremos Órbita-7 seguro para ti.",
                "Bienvenido a casa, Capitán del Cosmos. Los talleres, los baúles estelares y tu cama espacial están a punto, y el Coronel y yo mantendremos Órbita Siete seguro para ti.",
            ),
        ],
    },
    {
        "info_fid": 0x01004719,
        "prev_fid": 0x01004019,
        "enam_flags": 0x02,
        "stage_conds": [(0x60, 200.0)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "Qué alegría verte de regreso por Órbita-7, Capitán. Si te apetece escuchar de nuevo el repertorio chusquero del Coronel Agallas, prueba cualquier Simulacro Libre en su consola.",
                "Qué alegría verte de regreso por Órbita Siete, Capitán. Si te apetece escuchar de nuevo el repertorio chusquero del Coronel Agallas, prueba cualquier Simulacro Libre en su consola.",
            ),
        ],
    },
    {
        "info_fid": 0x0100471A,
        "prev_fid": 0x01004719,
        "enam_flags": 0x22,
        "stage_conds": [(0x60, 200.0)],
        "tsce_fid": None,
        "intv_phase": None,
        "tiqs_stage": None,
        "nam0_phase": "",
        "responses": [
            (
                "Los bancos de trabajo siguen impecables, compañero. Y recuerda que dejé calibrados tanto la Carabina Fotónica como el Cañón Gauss para que los intercambies a gusto entre el traje y la servoarmadura.",
                "Los bancos de trabajo siguen impecables, compañero. Y recuerda que dejé calibrados tanto la Carabina Fotónica como el Cañón Gauss para que los intercambies a gusto entre el traje y la servoarmadura.",
            ),
        ],
    },
]

# ==============================================================================
# 2. SALUDOS Y LADRIDOS DEL CORONEL AGALLAS «COSMOS» (GREE 0x01004002 + CUST 0x01004003)
# ==============================================================================
CORONEL_GREETING_INFOS = [
    # Etapa < 20
    {
        "info_fid": 0x01004020,
        "prev_fid": 0x00000000,
        "enam_flags": 0x02,
        "stage_conds": [(0x80, 20.0)],
        "responses": [
            (
                "¡ALTO AHÍ, GUSANO TERRÍCOLA! ¡Habla primero con el ingeniero jefe Vance antes de ensuciar mi consola de examen con tus zarpas radiactivas!",
                "¡ALTO AHÍ, GUSANO TERRÍCOLA! ¡Habla primero con el ingeniero jefe Vance antes de ensuciar mi consola de examen con tus zarpas radiactivas!",
            ),
        ],
    },
    {
        "info_fid": 0x01004801,
        "prev_fid": 0x01004020,
        "enam_flags": 0x22,
        "stage_conds": [(0x80, 20.0)],
        "responses": [
            (
                "¡NI SE TE OCURRA TOCAR UN BOTÓN TODAVÍA, PAISANO! Preséntate primero ante Artie Vance si no quieres hacer cien flexiones en gravedad cero!",
                "¡NI SE TE OCURRA TOCAR UN BOTÓN TODAVÍA, PAISANO! Preséntate primero ante Artie Vance si no quieres hacer cien flexiones en gravedad cero!",
            ),
        ],
    },
    # Etapa 20 -> Examen 1 pendiente
    {
        "info_fid": 0x01004021,
        "prev_fid": 0x01004801,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 20.0)],
        "responses": [
            (
                "¡FIRME, CADETE ESPACIAL! Cuando memorices las tres pistas de esta base, pulsa mi Consola de Verdadero Creyente y demuestra que no tienes serrín en el casco!",
                "¡FIRME, CADETE ESPACIAL! Cuando memorices las tres pistas de esta base, pulsa mi Consola de Verdadero Creyente y demuestra que no tienes serrín en el casco!",
            ),
        ],
    },
    {
        "info_fid": 0x01004802,
        "prev_fid": 0x01004021,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 20.0)],
        "responses": [
            (
                "¡MENOS PARLOTEO Y MÁS LECTURA DE VITRINAS, RECLUTA! En Campamento McClintock masticábamos munición antes de desayunar; ¡tú solo tienes que aprobar mi primer test!",
                "¡MENOS PARLOTEO Y MÁS LECTURA DE VITRINAS, RECLUTA! En Campamento McClintock masticábamos munición antes de desayunar; ¡tú solo tienes que aprobar mi primer test!",
            ),
        ],
    },
    # Etapa 30 -> Traje desbloqueado
    {
        "info_fid": 0x01004803,
        "prev_fid": 0x01004802,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 30.0)],
        "responses": [
            (
                "¡LA BARRERA UNO ESTÁ DESACTIVADA, RECLUTA! Deja de babear ante mis sensores y ve a por tu Traje de Vuelo Astro-Cosmos antes de que cambie de opinión!",
                "¡LA BARRERA UNO ESTÁ DESACTIVADA, RECLUTA! Deja de babear ante mis sensores y ve a por tu Traje de Vuelo Astro-Cosmos antes de que cambie de opinión!",
            ),
        ],
    },
    {
        "info_fid": 0x01004804,
        "prev_fid": 0x01004803,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 30.0)],
        "responses": [
            (
                "¡ENHORABUENA POR NO REVENTAR MI TERMINAL DE LA IGNORANCIA! Ahora corre hacia la cápsula de estasis y ponte ese traje aeroespacial!",
                "¡ENHORABUENA POR NO REVENTAR MI TERMINAL DE LA IGNORANCIA! Ahora corre hacia la cápsula de estasis y ponte ese traje aeroespacial!",
            ),
        ],
    },
    # Etapa 35 -> Traje reclamado, hablar con Artie
    {
        "info_fid": 0x01004805,
        "prev_fid": 0x01004804,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 35.0)],
        "responses": [
            (
                "¡JA! TE QUEDA CASI TAN BIEN COMO UN SACO DE PATATAS ESPACIALES! Preséntate ante Vance para recibir tus órdenes de vuelo sobre Boston!",
                "¡JA! TE QUEDA CASI TAN BIEN COMO UN SACO DE PATATAS ESPACIALES! Preséntate ante Vance para recibir tus órdenes de vuelo sobre Boston!",
            ),
        ],
    },
    {
        "info_fid": 0x01004806,
        "prev_fid": 0x01004805,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 35.0)],
        "responses": [
            (
                "¡NO ME HAGAS DESFILAR POR DELANTE EN CALZONCILLOS CÓSMICOS, CADETE! El ingeniero jefe Vance te espera para asignar la operación de las bobinas!",
                "¡NO ME HAGAS DESFILAR POR DELANTE EN CALZONCILLOS CÓSMICOS, CADETE! El ingeniero jefe Vance te espera para asignar la operación de las bobinas!",
            ),
        ],
    },
    # Etapa 40 (0 bobinas) -> Patrulla por tejados
    {
        "info_fid": 0x01004807,
        "prev_fid": 0x01004806,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 40.0)],
        "global_conds": [(0x00, 0.0, 0x01001003)],
        "responses": [
            (
                "¿QUÉ HACES TODAVÍA ANCLADO AL SUELO COMO UNA LÁMPARA DE PIE, GRUMETE? ¡Despega hacia los tejados de Hubris, Trinity y WRVR a por esas tres bobinas!",
                "¿QUÉ HACES TODAVÍA ANCLADO AL SUELO COMO UNA LÁMPARA DE PIE, GRUMETE? ¡Despega hacia los tejados de Hubris, Trinity y \"uve doble e erre uve erre\", a por esas tres bobinas!",
            ),
        ],
    },
    {
        "info_fid": 0x01004808,
        "prev_fid": 0x01004807,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 40.0)],
        "global_conds": [(0x00, 0.0, 0x01001003)],
        "responses": [
            (
                "¡LOS TEJADOS NO SE VAN A CONQUISTAR SOLOS MIRANDO AL TECHO DE ESTE SÓTANO! ¡Propulsores al máximo y tráeme esas tres Bobinas Fotónicas!",
                "¡LOS TEJADOS NO SE VAN A CONQUISTAR SOLOS MIRANDO AL TECHO DE ESTE SÓTANO! ¡Propulsores al máximo y tráeme esas tres Bobinas Fotónicas!",
            ),
        ],
    },
    # Etapa 40 (>= 1 bobina) -> Avance parcial de bobinas
    {
        "info_fid": 0x01004809,
        "prev_fid": 0x01004808,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 40.0)],
        "global_conds": [(0x60, 1.0, 0x01001003)],
        "responses": [
            (
                "¡BIEN, YA PESCASTE AL MENOS UNA BOBINA ALLÁ ARRIBA! Pero en el ejército las misiones a medias valen exactamente cero chapas! ¡Completa las tres!",
                "¡BIEN, YA PESCASTE AL MENOS UNA BOBINA ALLÁ ARRIBA! Pero en el ejército las misiones a medias valen exactamente cero chapas! ¡Completa las tres!",
            ),
        ],
    },
    {
        "info_fid": 0x0100480A,
        "prev_fid": 0x01004809,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 40.0)],
        "global_conds": [(0x60, 1.0, 0x01001003)],
        "responses": [
            (
                "¡NO ME GUARDES LA CARA DE VICTORIOSO TODAVÍA, PILOTO! Mientras falte una sola Bobina Fotónica en esos tejados, la consola del segundo examen sigue cerrada!",
                "¡NO ME GUARDES LA CARA DE VICTORIOSO TODAVÍA, PILOTO! Mientras falte una sola Bobina Fotónica en esos tejados, la consola del segundo examen sigue cerrada!",
            ),
        ],
    },
    # Etapa 50 -> 3 bobinas listas: Examen 2
    {
        "info_fid": 0x01004022,
        "prev_fid": 0x0100480A,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 50.0)],
        "responses": [
            (
                "¡VEO QUE TRAES LAS BOBINAS, GRUMETE VOLADOR! ¡Activa la Consola de Examen ahora mismo y veamos si te sabes el código de Los Imparables!",
                "¡VEO QUE TRAES LAS BOBINAS, GRUMETE VOLADOR! ¡Activa la Consola de Examen ahora mismo y veamos si te sabes el código de Los Imparables!",
            ),
        ],
    },
    {
        "info_fid": 0x0100480B,
        "prev_fid": 0x01004022,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 50.0)],
        "responses": [
            (
                "¡TRES BOBINAS ALINEADAS Y CERO EXCUSAS! ¡Ponte frente a mi consola de examen y demuestra que leíste los guiones mientras planeabas sobre Boston!",
                "¡TRES BOBINAS ALINEADAS Y CERO EXCUSAS! ¡Ponte frente a mi consola de examen y demuestra que leíste los guiones mientras planeabas sobre Boston!",
            ),
        ],
    },
    # Etapa 60 -> Carabina desbloqueada
    {
        "info_fid": 0x0100480C,
        "prev_fid": 0x0100480B,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 60.0)],
        "responses": [
            (
                "¡COMPUERTA FOTÓNICA ABIERTA! ¡Ve a recoger la Carabina de Rayos y recuerda que puedes dispararla volando tanto con tu traje como con servoarmadura!",
                "¡COMPUERTA FOTÓNICA ABIERTA! ¡Ve a recoger la Carabina de Rayos y recuerda que puedes dispararla volando tanto con tu traje como con servoarmadura!",
            ),
        ],
    },
    {
        "info_fid": 0x0100480D,
        "prev_fid": 0x0100480C,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 60.0)],
        "responses": [
            (
                "¡DOS EXÁMENES SEGUIDOS SIN FUNDIRTE LOS FUSIBLES! Retira esa carabina del pedestal antes de que un mutaracha aprenda a usar la mira de seis aumentos!",
                "¡DOS EXÁMENES SEGUIDOS SIN FUNDIRTE LOS FUSIBLES! Retira esa carabina del pedestal antes de que un mutaracha aprenda a usar la mira de seis aumentos!",
            ),
        ],
    },
    # Etapa 65 -> Carabina recogida, hablar con Artie
    {
        "info_fid": 0x0100480E,
        "prev_fid": 0x0100480D,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 65.0)],
        "responses": [
            (
                "¡BUENA EMPUÑADURA, SOLDADO! Ahora preséntate ante Artie Vance para recibir coordenadas de tiro aéreo en ArcJet Systems!",
                "¡BUENA EMPUÑADURA, SOLDADO! Ahora preséntate ante Artie Vance para recibir coordenadas de tiro aéreo en ArcJet Systems!",
            ),
        ],
    },
    {
        "info_fid": 0x0100480F,
        "prev_fid": 0x0100480E,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 65.0)],
        "responses": [
            (
                "¡DEJA DE ADMIRARTE EN EL REFLEJO DEL CAÑÓN! Vance tiene el dossier caliente de ArcJet Systems listo para ti!",
                "¡DEJA DE ADMIRARTE EN EL REFLEJO DEL CAÑÓN! Vance tiene el dossier caliente de ArcJet Systems listo para ti!",
            ),
        ],
    },
    # Etapa 70 -> Misión 3 en ArcJet
    {
        "info_fid": 0x01004810,
        "prev_fid": 0x0100480F,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 70.0)],
        "responses": [
            (
                "¡EN ARCJET SYSTEMS NO HAY MEDIAS TINTAS! ¡Conviértete en un maldito avión de ataque, fríe a esos robots centinela y tráeme el Núcleo Sincrotrón!",
                "¡EN ARCJET SYSTEMS NO HAY MEDIAS TINTAS! ¡Conviértete en un maldito avión de ataque, fríe a esos robots centinela y tráeme el Núcleo Sincrotrón!",
            ),
        ],
    },
    {
        "info_fid": 0x01004811,
        "prev_fid": 0x01004810,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 70.0)],
        "responses": [
            (
                "¿TODAVÍA AQUÍ ABAJO EN VEZ DE BARRER LA AZOTEA DE ARCJET? ¡Quiero polvo de hojalata comunista y ese Núcleo Sincrotrón en tu mochila ya!",
                "¿TODAVÍA AQUÍ ABAJO EN VEZ DE BARRER LA AZOTEA DE ARCJET? ¡Quiero polvo de hojalata comunista y ese Núcleo Sincrotrón en tu mochila ya!",
            ),
        ],
    },
    # Etapa 80 -> Núcleo Sincrotrón listo: Examen 3
    {
        "info_fid": 0x01004023,
        "prev_fid": 0x01004811,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 80.0)],
        "responses": [
            (
                "¡ESE NÚCLEO SINCROTRÓN ZUMBA COMO UN CAZA ORBITAL, TENIENTE! ¡Frente a la consola: toca el examen para abrir el Hangar de la Servoarmadura!",
                "¡ESE NÚCLEO SINCROTRÓN ZUMBA COMO UN CAZA ORBITAL, TENIENTE! ¡Frente a la consola: toca el examen para abrir el Hangar de la Servoarmadura!",
            ),
        ],
    },
    {
        "info_fid": 0x01004812,
        "prev_fid": 0x01004023,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 80.0)],
        "responses": [
            (
                "¡MUY BIEN CHAFADOS ESOS CENTINELAS EN ARCJET! ¡Ahora demuestra en mi terminal que también sabes leer cómics censurados si quieres la Servoarmadura!",
                "¡MUY BIEN CHAFADOS ESOS CENTINELAS EN ARCJET! ¡Ahora demuestra en mi terminal que también sabes leer cómics censurados si quieres la Servoarmadura!",
            ),
        ],
    },
    # Etapa 100 -> Hangar de Servoarmadura abierto
    {
        "info_fid": 0x01004813,
        "prev_fid": 0x01004812,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 100.0)],
        "responses": [
            (
                "¡COMPUERTAS DEL HANGAR NORTE ABIERTAS DE PAR EN PAR! ¡Entra ahí y enfúndate esa preciosidad de acero cobalto-oro!",
                "¡COMPUERTAS DEL HANGAR NORTE ABIERTAS DE PAR EN PAR! ¡Entra ahí y enfúndate esa preciosidad de acero cobalto-oro!",
            ),
        ],
    },
    {
        "info_fid": 0x01004814,
        "prev_fid": 0x01004813,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 100.0)],
        "responses": [
            (
                "¡TIENES SERVOARMADURA ESPERANDO EN EL HANGAR Y SIGUES AQUÍ PLANTADO! ¡Ve a reclamar el blindaje orbital del Capitán Cosmos!",
                "¡TIENES SERVOARMADURA ESPERANDO EN EL HANGAR Y SIGUES AQUÍ PLANTADO! ¡Ve a reclamar el blindaje orbital del Capitán Cosmos!",
            ),
        ],
    },
    # Etapa 110 -> Servoarmadura reclamada, hablar con Artie
    {
        "info_fid": 0x01004815,
        "prev_fid": 0x01004814,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 110.0)],
        "responses": [
            (
                "¡ASÍ ME GUSTA, TENIENTE! ¡Con esas seis toneladas de blindaje casi pareces un soldado de verdad! Habla con Vance para el último despliegue.",
                "¡ASÍ ME GUSTA, TENIENTE! ¡Con esas seis toneladas de blindaje casi pareces un soldado de verdad! Habla con Vance para el último despliegue.",
            ),
        ],
    },
    {
        "info_fid": 0x01004816,
        "prev_fid": 0x01004815,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 110.0)],
        "responses": [
            (
                "¡VAYA ZANCADAS METÁLICAS! Preséntate ahora mismo ante el ingeniero Vance: queda la misión definitiva de la señorita Sterling.",
                "¡VAYA ZANCADAS METÁLICAS! Preséntate ahora mismo ante el ingeniero Vance: queda la misión definitiva de la señorita Sterling.",
            ),
        ],
    },
    # Etapa 120 -> Sala del Director + Fort Hagen
    {
        "info_fid": 0x01004817,
        "prev_fid": 0x01004816,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 120.0)],
        "responses": [
            (
                "¡MEMORIZA EL GRAN MURAL DE LA SALA DEL DIRECTOR SIN BABEAR EL PARQUÉ Y DESPEGA HACIA FORT HAGEN! ¡Quiero esa Tarjeta Estelar Maestra antes del toque de diana!",
                "¡MEMORIZA EL GRAN MURAL DE LA SALA DEL DIRECTOR SIN BABEAR EL PARQUÉ Y DESPEGA HACIA FORT HAGEN! ¡Quiero esa Tarjeta Estelar Maestra antes del toque de diana!",
            ),
        ],
    },
    {
        "info_fid": 0x01004818,
        "prev_fid": 0x01004817,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 120.0)],
        "responses": [
            (
                "¡LA SEÑORITA STERLING MERECE UN SALUDO REGIO! Recoge su tarjeta en lo alto de Fort Hagen; da igual si vuelas con traje o servoarmadura mientras no hagas el ridículo!",
                "¡LA SEÑORITA STERLING MERECE UN SALUDO REGIO! Recoge su tarjeta en lo alto de Fort Hagen; da igual si vuelas con traje o servoarmadura mientras no hagas el ridículo!",
            ),
        ],
    },
    # Etapa 140 -> Tarjeta Maestra lista: Examen 4
    {
        "info_fid": 0x01004024,
        "prev_fid": 0x01004818,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 140.0)],
        "responses": [
            (
                "¡ATENCIÓN EN CUBIERTA! Traes la tarjeta estelar de la señorita Sterling... ¡Ponte frente a la consola para el Examen Maestro de Capitán del Cosmos!",
                "¡ATENCIÓN EN CUBIERTA! Traes la tarjeta estelar de la señorita Sterling... ¡Ponte frente a la consola para el Examen Maestro de Capitán del Cosmos!",
            ),
        ],
    },
    {
        "info_fid": 0x01004819,
        "prev_fid": 0x01004024,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 140.0)],
        "responses": [
            (
                "¡ÚLTIMA PRUEBA ANTES DE LA GLORIA O EL RIDÍCULO ETERNO, COMANDANTE! Escucha la grabación de la señorita Sterling y pasa por mi consola!",
                "¡ÚLTIMA PRUEBA ANTES DE LA GLORIA O EL RIDÍCULO ETERNO, COMANDANTE! Escucha la grabación de la señorita Sterling y pasa por mi consola!",
            ),
        ],
    },
    # Etapa 160 -> Cañón Orbital Gauss desbloqueado
    {
        "info_fid": 0x0100481A,
        "prev_fid": 0x01004819,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 160.0)],
        "responses": [
            (
                "¡RELICARIO SOLAR ABIERTO, CAPITÁN! Recoge ese Cañón Orbital Gauss; funciona en pleno vuelo tanto en servoarmadura como con tu traje estelar!",
                "¡RELICARIO SOLAR ABIERTO, CAPITÁN! Recoge ese Cañón Orbital Gauss; funciona en pleno vuelo tanto en servoarmadura como con tu traje estelar!",
            ),
        ],
    },
    {
        "info_fid": 0x0100481B,
        "prev_fid": 0x0100481A,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 160.0)],
        "responses": [
            (
                "¡VE AL HANGAR NORTE A EMPUÑAR EL CAÑÓN GAUSS ORBITAL! Y más vale que no apuntes al techo de mi sótano cuando lo pruebes!",
                "¡VE AL HANGAR NORTE A EMPUÑAR EL CAÑÓN GAUSS ORBITAL! Y más vale que no apuntes al techo de mi sótano cuando lo pruebes!",
            ),
        ],
    },
    # Etapa 165 -> Entrega del refugio con Artie
    {
        "info_fid": 0x0100481C,
        "prev_fid": 0x0100481B,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 165.0)],
        "responses": [
            (
                "¡ARSENAL COMPLETO AL CIENTO POR CIENTO, SEÑOR! Vance quiere darte las llaves definitivas de Órbita Siete antes de que me eche a llorar aceite!",
                "¡ARSENAL COMPLETO AL CIENTO POR CIENTO, SEÑOR! Vance quiere darte las llaves definitivas de Órbita Siete antes de que me eche a llorar aceite!",
            ),
        ],
    },
    {
        "info_fid": 0x0100481D,
        "prev_fid": 0x0100481C,
        "enam_flags": 0x22,
        "stage_conds": [(0x00, 165.0)],
        "responses": [
            (
                "¡CUATRO PROTOTIPOS EN LAS MANOS DE UN HÉROE DE VERDAD! Habla con Artie para cerrar el protocolo de transferencia!",
                "¡CUATRO PROTOTIPOS EN LAS MANOS DE UN HÉROE DE VERDAD! Habla con Artie para cerrar el protocolo de transferencia!",
            ),
        ],
    },
    # Etapa 200+ -> 4 saludos variados post-campaña con espíritu de Camp McClintock y aviso de Simulacro Libre
    {
        "info_fid": 0x01004025,
        "prev_fid": 0x0100481D,
        "enam_flags": 0x02,
        "stage_conds": [(0x60, 200.0)],
        "responses": [
            (
                "¡A SUS ÓRDENES, MI CAPITÁN DEL COSMOS! ¡Perímetro despejado de comunistas lunares y polillas mutantes, señor!",
                "¡A SUS ÓRDENES, MI CAPITÁN DEL COSMOS! ¡Perímetro despejado de comunistas lunares y polillas mutantes, señor!",
            ),
        ],
    },
    {
        "info_fid": 0x0100481E,
        "prev_fid": 0x01004025,
        "enam_flags": 0x02,
        "stage_conds": [(0x60, 200.0)],
        "responses": [
            (
                "¿BUSCANDO ALGO DE DISCIPLINA ESPACIAL, CAPITÁN? ¡Mi consola tiene abiertos los cuatro Simulacros Libres para poner a prueba esos reflejos cuando mande!",
                "¿BUSCANDO ALGO DE DISCIPLINA ESPACIAL, CAPITÁN? ¡Mi consola tiene abiertos los cuatro Simulacros Libres para poner a prueba esos reflejos cuando mande!",
            ),
        ],
    },
    {
        "info_fid": 0x0100481F,
        "prev_fid": 0x0100481E,
        "enam_flags": 0x02,
        "stage_conds": [(0x60, 200.0)],
        "responses": [
            (
                "¡SIN NOVEDAD EN LA ROTONDA, SEÑOR! Bueno, salvo Vance intentando limpiar el óxido de las tuberías con una cuchara... ¡Si quiere acción, abra un simulacro en mi terminal!",
                "¡SIN NOVEDAD EN LA ROTONDA, SEÑOR! Bueno, salvo Vance intentando limpiar el óxido de las tuberías con una cuchara... ¡Si quiere acción, abra un simulacro en mi terminal!",
            ),
        ],
    },
    {
        "info_fid": 0x01004820,
        "prev_fid": 0x0100481F,
        "enam_flags": 0x22,
        "stage_conds": [(0x60, 200.0)],
        "responses": [
            (
                "¡SERVOMOTORES REVISADOS Y LISTOS PARA REPARTIR JUSTICIA AMERICANA DESDE LAS NUBES, SEÑOR! Ambos prototipos de arma están calibrados para traje y servoarmadura!",
                "¡SERVOMOTORES REVISADOS Y LISTOS PARA REPARTIR JUSTICIA AMERICANA DESDE LAS NUBES, SEÑOR! Ambos prototipos de arma están calibrados para traje y servoarmadura!",
            ),
        ],
    },
    # Fallback de emergencia
    {
        "info_fid": 0x01004026,
        "prev_fid": 0x01004820,
        "enam_flags": 0x00,
        "stage_conds": [(0x60, 15.0)],
        "responses": [
            (
                "¡MUEVE ESE TRASERO CÓSMICO, RECLUTA! ¡No abriré ni una sola barrera hasta que cumplas los objetivos de vuelo y pases por mi consola!",
                "¡MUEVE ESE TRASERO CÓSMICO, RECLUTA! ¡No abriré ni una sola barrera hasta que cumplas los objetivos de vuelo y pases por mi consola!",
            ),
        ],
    },
]

# Ladridos dinámicos (DIAL 0x01004003, CUST) disparados desde Papyrus con PlayCoronelBark(bark_id)
CORONEL_BARK_INFOS = [
    # 1..4: Intros de los 4 exámenes
    {
        "info_fid": 0x01004031,
        "prev_fid": 0x00000000,
        "bark_id": 1,
        "responses": [(
            "¡ATENCIÓN, LARVA ESPACIAL! ¡Examen de Recluta nivel uno! ¡Un solo fallo y te mando a limpiar cráteres lunares con un cepillo de dientes!",
            "¡ATENCIÓN, LARVA ESPACIAL! ¡Examen de Recluta nivel uno! ¡Un solo fallo y te mando a limpiar cráteres lunares con un cepillo de dientes!",
        )],
    },
    {
        "info_fid": 0x01004032,
        "prev_fid": 0x01004031,
        "bark_id": 2,
        "responses": [(
            "¡FIRME FRENTE AL MONITOR, CADETE! ¡Examen de Patrulla Aérea sobre Los Imparables! ¡Demuestra que sabes leer algo más que etiquetas de Nuka-Cola!",
            "¡FIRME FRENTE AL MONITOR, CADETE! ¡Examen de Patrulla Aérea sobre Los Imparables! ¡Demuestra que sabes leer algo más que etiquetas de Nuka-Cola!",
        )],
    },
    {
        "info_fid": 0x01004033,
        "prev_fid": 0x01004032,
        "bark_id": 3,
        "responses": [(
            "¡SILENCIO EN LA ROTONDA! ¡Examen de Piloto Orbital para acceso a Servoarmadura! ¡A ver si tienes agallas de titanio o puré de patatas en el cráneo!",
            "¡SILENCIO EN LA ROTONDA! ¡Examen de Piloto Orbital para acceso a Servoarmadura! ¡A ver si tienes agallas de titanio o puré de patatas en el cráneo!",
        )],
    },
    {
        "info_fid": 0x01004034,
        "prev_fid": 0x01004033,
        "bark_id": 4,
        "responses": [(
            "¡HORA DE LA VERDAD, ASPIRANTE! ¡Examen Maestro del Juramento Estelar! ¡Honra la memoria de Clara Sterling o lárgate llorando a la superficie!",
            "¡HORA DE LA VERDAD, ASPIRANTE! ¡Examen Maestro del Juramento Estelar! ¡Honra la memoria de Clara Sterling o lárgate llorando a la superficie!",
        )],
    },
    # 5..9: Los 5 insultos cómicos de sargento chusquero al fallar preguntas
    {
        "info_fid": 0x01004035,
        "prev_fid": 0x01004034,
        "bark_id": 5,
        "responses": [(
            "¡MECACHIS EN LOS ANILLOS DE SATURNO, PEDAZO DE ALCORNOQUE RADIACTIVO! ¡Hasta Jangles el Mono Lunar acertaría esa con el casco puesto del revés!",
            "¡MECACHIS EN LOS ANILLOS DE SATURNO, PEDAZO DE ALCORNOQUE RADIACTIVO! ¡Hasta Jangles el Mono Lunar acertaría esa con el casco puesto del revés!",
        )],
    },
    {
        "info_fid": 0x01004036,
        "prev_fid": 0x01004035,
        "bark_id": 6,
        "responses": [(
            "¡NEGATIVO, MEQUETREFE GALÁCTICO! ¡Tienes menos luces que una luciérnaga muerta en un agujero negro! ¡Ve a leer las pistas otra vez!",
            "¡NEGATIVO, MEQUETREFE GALÁCTICO! ¡Tienes menos luces que una luciérnaga muerta en un agujero negro! ¡Ve a leer las pistas otra vez!",
        )],
    },
    {
        "info_fid": 0x01004037,
        "prev_fid": 0x01004036,
        "bark_id": 7,
        "responses": [(
            "¡PERO SERÁS ZOQUETE SIDERAAAAL! ¡Con ese cerebro de mutarrata es un milagro que no te abroches las botas en las orejas! ¡SUSPENSO!",
            "¡PERO SERÁS ZOQUETE SIDERAL! ¡Con ese cerebro de mutarrata es un milagro que no te abroches las botas en las orejas! ¡SUSPENSO!",
        )],
    },
    {
        "info_fid": 0x01004038,
        "prev_fid": 0x01004037,
        "bark_id": 8,
        "responses": [(
            "¡ERROR GARRAFAL, IMPOSTOR COMUNISTA DEL ESPACIO EXTERIOR! ¡Si vuelves a decir semejante burrada te desintegro el carné de club de fans!",
            "¡ERROR GARRAFAL, IMPOSTOR COMUNISTA DEL ESPACIO EXTERIOR! ¡Si vuelves a decir semejante burrada te desintegro el carné de club de fans!",
        )],
    },
    {
        "info_fid": 0x01004039,
        "prev_fid": 0x01004038,
        "bark_id": 9,
        "responses": [(
            "¡POR LAS BARBAS DE GROGNAK, QUÉ DESASTRE DE RECLUTA! ¡Date una vuelta, abre bien esos ojitos de topo y vuelve cuando sepas leer!",
            "¡POR LAS BARBAS DE GROGNAK, QUÉ DESASTRE DE RECLUTA! ¡Date una vuelta, abre bien esos ojitos de topo y vuelve cuando sepas leer!",
        )],
    },
    # 10..13: Felicitaciones militares al aprobar 3/3 en cada examen
    {
        "info_fid": 0x0100403A,
        "prev_fid": 0x01004039,
        "bark_id": 10,
        "responses": [(
            "¡TRES DE TRES, RECLUTA! ¡Igual no eres tan lerdo como pareces! ¡Desactivando barrera de estasis uno: ve a por tu Traje Astro-Cosmos!",
            "¡TRES DE TRES, RECLUTA! ¡Igual no eres tan lerdo como pareces! ¡Desactivando barrera de estasis uno: ve a por tu Traje Astro-Cosmos!",
        )],
    },
    {
        "info_fid": 0x0100403B,
        "prev_fid": 0x0100403A,
        "bark_id": 11,
        "responses": [(
            "¡PLENO AL QUINCE, CADETE DE PRIMERA! ¡Barrera del Laboratorio Fotónico abajo! ¡Reclama esa Carabina de Rayos y haz picadillo a los malos!",
            "¡PLENO AL QUINCE, CADETE DE PRIMERA! ¡Barrera del Laboratorio Fotónico abajo! ¡Reclama esa Carabina de Rayos y haz picadillo a los malos!",
        )],
    },
    {
        "info_fid": 0x0100403C,
        "prev_fid": 0x0100403B,
        "bark_id": 12,
        "responses": [(
            "¡MAGNÍFICO, TENIENTE ESTELAR! ¡Abriendo las compuertas del Hangar Orbital Norte! ¡La Servoarmadura Astro-Cosmos es toda tuya!",
            "¡MAGNÍFICO, TENIENTE ESTELAR! ¡Abriendo las compuertas del Hangar Orbital Norte! ¡La Servoarmadura Astro-Cosmos es toda tuya!",
        )],
    },
    {
        "info_fid": 0x0100403D,
        "prev_fid": 0x0100403C,
        "bark_id": 13,
        "responses": [(
            "¡SALUDO REGLAMENTARIO AL NUEVO CAPITÁN DEL COSMOS! ¡La señorita Clara estaría orgullosa de ti, soldado! ¡Relicario Solar desbloqueado!",
            "¡SALUDO REGLAMENTARIO AL NUEVO CAPITÁN DEL COSMOS! ¡La señorita Clara estaría orgullosa de ti, soldado! ¡Relicario Solar desbloqueado!",
        )],
    },
    # 14..17: Vítores al reclamar físicamente cada uno de los 4 prototipos
    {
        "info_fid": 0x0100403E,
        "prev_fid": 0x0100403D,
        "bark_id": 14,
        "responses": [(
            "¡ESO ES UN UNIFORME HEROICO Y NO LOS HARAPOS QUE TRAÍAS DE LA CALLE! ¡Ahora habla con Vance para tu primera misión de vuelo!",
            "¡ESO ES UN UNIFORME HEROICO Y NO LOS HARAPOS QUE TRAÍAS DE LA CALLE! ¡Ahora habla con Vance para tu primera misión de vuelo!",
        )],
    },
    {
        "info_fid": 0x0100403F,
        "prev_fid": 0x0100403E,
        "bark_id": 15,
        "responses": [(
            "¡MIRA CÓMO RELUCE ESA CARABINA FOTÓNICA! ¡Seis aumentos de pura justicia americana desde las nubes!",
            "¡MIRA CÓMO RELUCE ESA CARABINA FOTÓNICA! ¡Seis aumentos de pura justicia americana desde las nubes!",
        )],
    },
    {
        "info_fid": 0x01004040,
        "prev_fid": 0x0100403F,
        "bark_id": 16,
        "responses": [(
            "¡POTENCIA ATÓMICA EN LÍNEA! ¡Con ese torso propulsor ningún gusano terrestre podrá esconderse de ti!",
            "¡POTENCIA ATÓMICA EN LÍNEA! ¡Con ese torso propulsor ningún gusano terrestre podrá esconderse de ti!",
        )],
    },
    {
        "info_fid": 0x01004041,
        "prev_fid": 0x01004040,
        "bark_id": 17,
        "responses": [(
            "¡EL CAÑÓN ORBITAL GAUSS ESTÁ EN MANOS DEL CAPITÁN DEL COSMOS! ¡Que tiemblen los tiranos de toda la galaxia!",
            "¡EL CAÑÓN ORBITAL GAUSS ESTÁ EN MANOS DEL CAPITÁN DEL COSMOS! ¡Que tiemblen los tiranos de toda la galaxia!",
        )],
    },
    # 18..20: Saludo final de epílogo y avisos de consola
    {
        "info_fid": 0x01004042,
        "prev_fid": 0x01004041,
        "bark_id": 18,
        "responses": [(
            "¡ESTUDIO ÓRBITA SIETE TRANSFERIDO AL MANDO DEL CAPITÁN DEL COSMOS! ¡Por la Verdad, las Estrellas y el Mañana, señor!",
            "¡ESTUDIO ÓRBITA SIETE TRANSFERIDO AL MANDO DEL CAPITÁN DEL COSMOS! ¡Por la Verdad, las Estrellas y el Mañana, señor!",
        )],
    },
    {
        "info_fid": 0x01004043,
        "prev_fid": 0x01004042,
        "bark_id": 19,
        "responses": [(
            "¡ALTO EL CARRO, RECLUTA! ¡Aún no tienes los componentes ni la autorización para el siguiente examen! ¡Completa antes tu misión!",
            "¡ALTO EL CARRO, RECLUTA! ¡Aún no tienes los componentes ni la autorización para el siguiente examen! ¡Completa antes tu misión!",
        )],
    },
    {
        "info_fid": 0x01004044,
        "prev_fid": 0x01004043,
        "bark_id": 20,
        "responses": [(
            "¡DEJA DE APORREAR MIS BOTONES, ZOQUETE! ¡Ya has aprobado este examen, ve de una vez a reclamar tu prototipo desbloqueado!",
            "¡DEJA DE APORREAR MIS BOTONES, ZOQUETE! ¡Ya has aprobado este examen, ve de una vez a reclamar tu prototipo desbloqueado!",
        )],
    },
]

# ==============================================================================
# 3. LAS 5 ESCENAS INTERACTIVAS DE RUEDA DE DIÁLOGO CON ARTIE VANCE
# ==============================================================================
ARTIE_SCENES = [
    # ESCENA 1 (0x01004100): Etapa 15 -> 20 (Bienvenida y Misión 1)
    {
        "scen_fid": 0x01004100,
        "edid": "Orbita7Scene1_Intro",
        "phases": ["Ph1"],
        "actions": [
            {
                "action_idx": 1,
                "phase_idx": 0,
                "options": [
                    {
                        "rnam": "Aceptar ayudar",
                        "p_dial": 0x01004111, "p_info": 0x01004121,
                        "n_dial": 0x01004112, "n_info": 0x01004122,
                        "p_sub": "Capté tu señal junto a Hubris Comics. ¿Qué es este búnker y cómo puedo ayudarte?",
                        "p_tts": "Capté tu señal junto a Hubris Comics. ¿Qué es este búnker y cómo puedo ayudarte?",
                        "tiqs_stage": 20,
                        "n_responses": [
                            (
                                "En 2077, Hubris Comics y un equipo rebelde de ingenieros construimos aquí en secreto tecnología real inspirada en el Capitán Cosmos: un traje de vuelo, una servoarmadura orbital y dos armas aéreas.",
                                "En dos mil setenta y siete, Hubris Comics y un equipo rebelde de ingenieros construimos aquí en secreto tecnología real inspirada en el Capitán Cosmos: un traje de vuelo, una servoarmadura orbital y dos armas aéreas.",
                            ),
                            (
                                "Nuestra guionista jefa, Clara Sterling, programó al Coronel Agallas para que ningún militar corrupto pudiera robarlos: solo alguien que conozca la historia de nuestros héroes puede apagar las barreras.",
                                "Nuestra guionista jefa, Clara Sterling, programó al Coronel Agallas para que ningún militar corrupto pudiera robarlos: solo alguien que conozca la historia de nuestros héroes puede apagar las barreras.",
                            ),
                            (
                                "Busca las tres primeras pistas aquí mismo, en la Rotonda y en la Sala de Guionistas del ala este, y supera el examen del Coronel para reclamar el Traje de Vuelo Astro-Cosmos.",
                                "Busca las tres primeras pistas aquí mismo, en la Rotonda y en la Sala de Guionistas del ala este, y supera el examen del Coronel para reclamar el Traje de Vuelo Astro-Cosmos.",
                            ),
                        ],
                    },
                    {
                        "rnam": "Broma sobre el robot",
                        "p_dial": 0x01004113, "p_info": 0x01004123,
                        "n_dial": 0x01004114, "n_info": 0x01004124,
                        "p_sub": "¿Ese robot militar acaba de amenazarme con el carné de un club de fans de cómics?",
                        "p_tts": "¿Ese robot militar acaba de amenazarme con el carné de un club de fans de cómics?",
                        "tiqs_stage": 20,
                        "n_responses": [
                            (
                                "¡Ja, ja! Ese es el Coronel Agallas «Cosmos». Clara cruzó su matriz de instrucción del Ejército con cuarenta años de tebeos de Hubris.",
                                "¡Ja, ja! Ese es el Coronel Agallas Cosmos. Clara cruzó su matriz de instrucción del Ejército con cuarenta años de tebeos de Hubris.",
                            ),
                            (
                                "Te gritará barbaridades si fallas una pregunta, pero en el fondo es un pedazo de latón adorable y custodia los cuatro prototipos reales del Proyecto Astro-Cosmos.",
                                "Te gritará barbaridades si fallas una pregunta, pero en el fondo es un pedazo de latón adorable y custodia los cuatro prototipos reales del Proyecto Astro-Cosmos.",
                            ),
                            (
                                "Examina la vitrina de la Rotonda, el restirador de Clara y su terminal en la Sala de Guionistas, y usa la consola para ganar tu Traje de Vuelo.",
                                "Examina la vitrina de la Rotonda, el restirador de Clara y su terminal en la Sala de Guionistas, y usa la consola para ganar tu Traje de Vuelo.",
                            ),
                        ],
                    },
                    {
                        "rnam": "Ir al grano",
                        "p_dial": 0x01004115, "p_info": 0x01004125,
                        "n_dial": 0x01004116, "n_info": 0x01004126,
                        "p_sub": "Veo cápsulas blindadas tras barreras láser. Dime qué hay dentro y cómo las abrimos.",
                        "p_tts": "Veo cápsulas blindadas tras barreras láser. Dime qué hay dentro y cómo las abrimos.",
                        "tiqs_stage": 20,
                        "n_responses": [
                            (
                                "Directo al grano, me gusta. Esas barreras guardan cuatro maravillas reales: el Traje de Vuelo Astro-Cosmos, su Carabina de Rayos, la Servoarmadura Orbital y un Cañón Gauss Solar.",
                                "Directo al grano, me gusta. Esas barreras guardan cuatro maravillas reales: el Traje de Vuelo Astro-Cosmos, su Carabina de Rayos, la Servoarmadura Orbital y un Cañón Gauss Solar.",
                            ),
                            (
                                "El Coronel Agallas solo desbloquea cada barrera ante un «Verdadero Creyente» que supere sus pruebas sobre Hubris Comics.",
                                "El Coronel Agallas solo desbloquea cada barrera ante un Verdadero Creyente que supere sus pruebas sobre Hubris Comics.",
                            ),
                            (
                                "Lee la vitrina de esta Rotonda y entra en la Sala de Guionistas al este para revisar la mesa de dibujo y el terminal; después examínate en la consola.",
                                "Lee la vitrina de esta Rotonda y entra en la Sala de Guionistas al este para revisar la mesa de dibujo y el terminal; después examínate en la consola.",
                            ),
                        ],
                    },
                    {
                        "rnam": "¿Quién es Clara?",
                        "p_dial": 0x01004117, "p_info": 0x01004127,
                        "n_dial": 0x01004118, "n_info": 0x01004128,
                        "p_sub": "¿Quién construyó un estudio tan increíble debajo de Hubris Comics?",
                        "p_tts": "¿Quién construyó un estudio tan increíble debajo de Hubris Comics?",
                        "tiqs_stage": 20,
                        "n_responses": [
                            (
                                "Se construyó para la serie de televisión del Capitán Cosmos que iba a estrenarse en noviembre de 2077, bajo la dirección de nuestra guionista jefa, Clara Sterling.",
                                "Se construyó para la serie de televisión del Capitán Cosmos que iba a estrenarse en noviembre de dos mil setenta y siete, bajo la dirección de nuestra guionista jefa, Clara Sterling.",
                            ),
                            (
                                "Cuando el Pentágono quiso convertir nuestros propulsores de vuelo en armas de masacre, Clara selló aquí los prototipos detrás de acertijos sobre sus propios cómics.",
                                "Cuando el Pentágono quiso convertir nuestros propulsores de vuelo en armas de masacre, Clara selló aquí los prototipos detrás de acertijos sobre sus propios cómics.",
                            ),
                            (
                                "Todo empieza en la vitrina de esta Rotonda y en el escritorio y terminal de Clara en el ala este. Reúne esas tres pistas y supera el primer test del Coronel.",
                                "Todo empieza en la vitrina de esta Rotonda y en el escritorio y terminal de Clara en el ala este. Reúne esas tres pistas y supera el primer test del Coronel.",
                            ),
                        ],
                    },
                ],
            }
        ],
    },
    # ESCENA 2 (0x01004200): Etapa 35 -> 40 (Misión 2: Patrulla sobre los Tejados)
    {
        "scen_fid": 0x01004200,
        "edid": "Orbita7Scene2_Rooftops",
        "phases": ["Ph1"],
        "actions": [
            {
                "action_idx": 1,
                "phase_idx": 0,
                "options": [
                    {
                        "rnam": "¡Listo para volar!",
                        "p_dial": 0x01004211, "p_info": 0x01004221, "p_info_f": 0x01004231,
                        "n_dial": 0x01004212, "n_info": 0x01004222,
                        "p_sub": "Estoy listo para alzar el vuelo, Artie. ¿Adónde me dirijo?",
                        "p_tts": "Estoy listo para alzar el vuelo, Artie. ¿Adónde me dirijo?",
                        "p_sub_f": "Estoy lista para alzar el vuelo, Artie. ¿Adónde me dirijo?",
                        "p_tts_f": "Estoy lista para alzar el vuelo, Artie. ¿Adónde me dirijo?",
                        "rnam_f": "¡Lista para volar!",
                        "tiqs_stage": 40,
                        "n_responses": [
                            (
                                "En el Laboratorio Fotónico del oeste reposa la Carabina de Rayos Astro-Cosmos, la única arma giroscópica capaz de disparar con precisión y mira telescópica en pleno vuelo con tu traje.",
                                "En el Laboratorio Fotónico del oeste reposa la Carabina de Rayos Astro-Cosmos, la única arma giroscópica capaz de disparar con precisión y mira telescópica en pleno vuelo con tu traje.",
                            ),
                            (
                                "Para alimentar su pedestal necesitamos tres Bobinas Fotónicas que Clara escondió en lo alto de tres tejados de Boston: la azotea de Hubris Comics, la terraza de Trinity Plaza y el tejado de la emisora WRVR.",
                                "Para alimentar su pedestal necesitamos tres Bobinas Fotónicas que Clara escondió en lo alto de tres tejados de Boston: la azotea de Hubris Comics, la terraza de Trinity Plaza y el tejado de la emisora \"uve doble e erre uve erre\",.",
                            ),
                            (
                                "Equípate el traje en el exterior, vuela hasta esos tres alijos estelares y lee bien la holocinta de Clara y los dossieres de Los Imparables para el segundo examen del Coronel.",
                                "Equípate el traje en el exterior, vuela hasta esos tres alijos estelares y lee bien la holocinta de Clara y los dossieres de Los Imparables para el segundo examen del Coronel.",
                            ),
                        ],
                    },
                    {
                        "rnam": "Broma de superhéroe",
                        "p_dial": 0x01004213, "p_info": 0x01004223,
                        "n_dial": 0x01004214, "n_info": 0x01004224,
                        "p_sub": "Con esta capa ya solo me falta patrullar por las azoteas de Boston como Silver Shroud.",
                        "p_tts": "Con esta capa ya solo me falta patrullar por las azoteas de Boston como Silver Shroud.",
                        "tiqs_stage": 40,
                        "n_responses": [
                            (
                                "¡Pues has dado en el clavo, porque literalmente vas a patrullar las azoteas de Boston!",
                                "¡Pues has dado en el clavo, porque literalmente vas a patrullar las azoteas de Boston!",
                            ),
                            (
                                "Clara ocultó las tres Bobinas Fotónicas de la Carabina de Rayos en los tejados de Hubris Comics, Trinity Plaza y la emisora WRVR, donde ningún saqueador sin alas pudiera alcanzarlas.",
                                "Clara ocultó las tres Bobinas Fotónicas de la Carabina de Rayos en los tejados de Hubris Comics, Trinity Plaza y la emisora \"uve doble e erre uve erre\",, donde ningún saqueador sin alas pudiera alcanzarlas.",
                            ),
                            (
                                "Tráelas junto con la primera holocinta de Clara y los guiones de Los Imparables, y el Coronel te abrirá el pedestal de la Carabina.",
                                "Tráelas junto con la primera holocinta de Clara y los guiones de Los Imparables, y el Coronel te abrirá el pedestal de la Carabina.",
                            ),
                        ],
                    },
                    {
                        "rnam": "Sobre la Carabina",
                        "p_dial": 0x01004215, "p_info": 0x01004225,
                        "n_dial": 0x01004216, "n_info": 0x01004226,
                        "p_sub": "Háblame de esa Carabina de Rayos del laboratorio oeste. ¿Qué la hace especial?",
                        "p_tts": "Háblame de esa Carabina de Rayos del laboratorio oeste. ¿Qué la hace especial?",
                        "tiqs_stage": 40,
                        "n_responses": [
                            (
                                "Las armas convencionales desestabilizan el campo antigravitatorio del traje, pero diseñé la Carabina Astro-Cosmos con compensadores armónicos y mira de reconocimiento de seis aumentos.",
                                "Las armas convencionales desestabilizan el campo antigravitatorio del traje, pero diseñé la Carabina Astro-Cosmos con compensadores armónicos y mira de reconocimiento de seis aumentos.",
                            ),
                            (
                                "Sus tres Bobinas Fotónicas aguardan en los tejados de Hubris Comics, Trinity Plaza y la emisora WRVR, junto con las pistas sobre Los Imparables.",
                                "Sus tres Bobinas Fotónicas aguardan en los tejados de Hubris Comics, Trinity Plaza y la emisora \"uve doble e erre uve erre\",, junto con las pistas sobre Los Imparables.",
                            ),
                            (
                                "Sal a la calle, impulsa el traje hacia el cielo y tráelas de vuelta para superar el segundo examen.",
                                "Sal a la calle, impulsa el traje hacia el cielo y tráelas de vuelta para superar el segundo examen.",
                            ),
                        ],
                    },
                    {
                        "rnam": "¿Qué pasó con Clara?",
                        "p_dial": 0x01004217, "p_info": 0x01004227,
                        "n_dial": 0x01004218, "n_info": 0x01004228,
                        "p_sub": "¿Clara Sterling dejó grabaciones ahí arriba antes de que cayeran las bombas?",
                        "p_tts": "¿Clara Sterling dejó grabaciones ahí arriba antes de que cayeran las bombas?",
                        "tiqs_stage": 40,
                        "n_responses": [
                            (
                                "Sí... La noche del 22 de octubre subió sola a las azoteas para repartir las bobinas y dejar sus holocintas fuera del alcance de los agentes federales.",
                                "Sí... La noche del veintidós de octubre subió sola a las azoteas para repartir las bobinas y dejar sus holocintas fuera del alcance de los agentes federales.",
                            ),
                            (
                                "He marcado en tu Pip-Boy los tejados de Hubris Comics, Trinity Plaza y la emisora WRVR. Vuela hasta allí, recoge las tres bobinas y escucha su voz.",
                                "He marcado en tu Pip-Boy los tejados de Hubris Comics, Trinity Plaza y la emisora \"uve doble e erre uve erre\",. Vuela hasta allí, recoge las tres bobinas y escucha su voz.",
                            ),
                        ],
                    },
                ],
            }
        ],
    },
    # ESCENA 3 (0x01004300): Etapa 65 -> 70 (Misión 3: Operación Titán Estelar en ArcJet)
    {
        "scen_fid": 0x01004300,
        "edid": "Orbita7Scene3_ArcJet",
        "phases": ["Ph1"],
        "actions": [
            {
                "action_idx": 1,
                "phase_idx": 0,
                "options": [
                    {
                        "rnam": "Rumbo a ArcJet",
                        "p_dial": 0x01004311, "p_info": 0x01004321,
                        "n_dial": 0x01004312, "n_info": 0x01004322,
                        "p_sub": "Cuéntame qué hay en la cubierta de ArcJet Systems y traeré ese núcleo.",
                        "p_tts": "Cuéntame qué hay en la cubierta de ArcJet Systems y traeré ese núcleo.",
                        "tiqs_stage": 70,
                        "n_responses": [
                            (
                                "Detrás de la gran barrera del norte aguarda nuestra joya acorazada: la Servoarmadura Astro-Cosmos completa, equipada con reactores gemelos de vuelo libre y escudo cósmico total contra radiación.",
                                "Detrás de la gran barrera del norte aguarda nuestra joya acorazada: la Servoarmadura Astro-Cosmos completa, equipada con reactores gemelos de vuelo libre y escudo cósmico total contra radiación.",
                            ),
                            (
                                "ArcJet Systems fabricó sus toberas, pero sus directivos retuvieron el Núcleo Sincrotrón de Pruebas en un arca en lo más alto del edificio exterior, custodiada por robots centinela.",
                                "ArcJet Systems fabricó sus toberas, pero sus directivos retuvieron el Núcleo Sincrotrón de Pruebas en un arca en lo más alto del edificio exterior, custodiada por robots centinela.",
                            ),
                            (
                                "Vuela sobre la cubierta superior de ArcJet, elimina a los centinelas desde el aire con tu nueva Carabina y recupera el núcleo junto con la segunda holocinta de Clara y el número cincuenta.",
                                "Vuela sobre la cubierta superior de ArcJet, elimina a los centinelas desde el aire con tu nueva Carabina y recupera el núcleo junto con la segunda holocinta de Clara y el número cincuenta.",
                            ),
                        ],
                    },
                    {
                        "rnam": "Probar puntería aérea",
                        "p_dial": 0x01004313, "p_info": 0x01004323,
                        "n_dial": 0x01004314, "n_info": 0x01004324,
                        "p_sub": "Esos robots de ArcJet van a ser unas dianas estupendas desde cien metros de altura.",
                        "p_tts": "Esos robots de ArcJet van a ser unas dianas estupendas desde cien metros de altura.",
                        "tiqs_stage": 70,
                        "n_responses": [
                            (
                                "¡Esa es la actitud del Capitán Cosmos! Con tu traje suspendido en el aire y la mira de reconocimiento de la Carabina tendrás toda la ventaja táctica.",
                                "¡Esa es la actitud del Capitán Cosmos! Con tu traje suspendido en el aire y la mira de reconocimiento de la Carabina tendrás toda la ventaja táctica.",
                            ),
                            (
                                "Abre el arca blindada de la cubierta superior de ArcJet Systems, recoge el Núcleo Sincrotrón y estudia la holocinta de Clara y el guion censurado del número cincuenta para el tercer examen.",
                                "Abre el arca blindada de la cubierta superior de ArcJet Systems, recoge el Núcleo Sincrotrón y estudia la holocinta de Clara y el guion censurado del número cincuenta para el tercer examen.",
                            ),
                        ],
                    },
                    {
                        "rnam": "Sobre la Servoarmadura",
                        "p_dial": 0x01004315, "p_info": 0x01004325,
                        "n_dial": 0x01004316, "n_info": 0x01004326,
                        "p_sub": "¿Una Servoarmadura completa capaz de volar de verdad, no solo dar saltos con propulsor?",
                        "p_tts": "¿Una Servoarmadura completa capaz de volar de verdad, no solo dar saltos con propulsor?",
                        "tiqs_stage": 70,
                        "n_responses": [
                            (
                                "Vuelo sostenido real, socio. Su torso birreactor genera sustentación continua y sus seis piezas cobalto, carmesí y oro resisten hasta el corazón del Mar Resplandeciente sin recibir un solo rad.",
                                "Vuelo sostenido real, socio. Su torso birreactor genera sustentación continua y sus seis piezas cobalto, carmesí y oro resisten hasta el corazón del Mar Resplandeciente sin recibir un solo rad.",
                            ),
                            (
                                "Trae el Núcleo Sincrotrón del tejado exterior de ArcJet Systems, supera el tercer examen del Coronel y el pórtico del Hangar Norte será tuyo.",
                                "Trae el Núcleo Sincrotrón del tejado exterior de ArcJet Systems, supera el tercer examen del Coronel y el pórtico del Hangar Norte será tuyo.",
                            ),
                        ],
                    },
                    {
                        "rnam": "El número 50 censurado",
                        "p_dial": 0x01004317, "p_info": 0x01004327,
                        "n_dial": 0x01004318, "n_info": 0x01004328,
                        "p_sub": "En la holocinta anterior Clara mencionó un número especial censurado. ¿Está en ArcJet?",
                        "p_tts": "En la holocinta anterior Clara mencionó un número especial censurado. ¿Está en ArcJet?",
                        "tiqs_stage": 70,
                        "n_responses": [
                            (
                                "Tienes buena memoria. Clara se coló en la azotea de ArcJet para recuperar las planchas del Especial Número Cincuenta del Capitán Cosmos que los contratistas militares confiscaron.",
                                "Tienes buena memoria. Clara se coló en la azotea de ArcJet para recuperar las planchas del Especial Número Cincuenta del Capitán Cosmos que los contratistas militares confiscaron.",
                            ),
                            (
                                "Encontrarás tanto el borrador como su segunda holocinta y el Núcleo Sincrotrón en la cubierta exterior más alta de ArcJet Systems. Buena caza ahí arriba.",
                                "Encontrarás tanto el borrador como su segunda holocinta y el Núcleo Sincrotrón en la cubierta exterior más alta de ArcJet Systems. Buena caza ahí arriba.",
                            ),
                        ],
                    },
                ],
            }
        ],
    },
    # ESCENA 4 (0x01004400): Etapa 110 -> 120 (Misión 4: Sala del Director + Fort Hagen)
    {
        "scen_fid": 0x01004400,
        "edid": "Orbita7Scene4_FortHagen",
        "phases": ["Ph1"],
        "actions": [
            {
                "action_idx": 1,
                "phase_idx": 0,
                "options": [
                    {
                        "rnam": "Por Clara Sterling",
                        "p_dial": 0x01004411, "p_info": 0x01004421,
                        "n_dial": 0x01004412, "n_info": 0x01004422,
                        "p_sub": "Terminemos lo que Clara empezó, Artie. Abre la Sala del Director y dime dónde fue aquel día.",
                        "p_tts": "Terminemos lo que Clara empezó, Artie. Abre la Sala del Director y dime dónde fue aquel día.",
                        "tiqs_stage": 120,
                        "n_responses": [
                            (
                                "Acabo de desconectar la barrera de la Sala de Proyección del Director y los Aposentos Privados, al sur de la Sala de Guionistas. Entra y contempla el Gran Mural del Juramento Estelar.",
                                "Acabo de desconectar la barrera de la Sala de Proyección del Director y los Aposentos Privados, al sur de la Sala de Guionistas. Entra y contempla el Gran Mural del Juramento Estelar.",
                            ),
                            (
                                "La mañana del 23 de octubre de 2077, Clara fue al complejo de antenas por satélite de Fort Hagen para borrar nuestras coordenadas de la red del Pentágono con su Tarjeta Estelar Maestra.",
                                "La mañana del veintitrés de octubre de dos mil setenta y siete, Clara fue al complejo de antenas por satélite de Fort Hagen para borrar nuestras coordenadas de la red del Pentágono con su Tarjeta Estelar Maestra.",
                            ),
                            (
                                "Vuela en tu Servoarmadura Astro-Cosmos hasta el tejado del búnker bajo la gran antena noreste de Fort Hagen, derrota a los autómatas del Pentágono y trae su tarjeta y su última holocinta.",
                                "Vuela en tu Servoarmadura Astro-Cosmos hasta el tejado del búnker bajo la gran antena noreste de Fort Hagen, derrota a los autómatas del Pentágono y trae su tarjeta y su última holocinta.",
                            ),
                        ],
                    },
                    {
                        "rnam": "Aplastar robots en PA",
                        "p_dial": 0x01004413, "p_info": 0x01004423,
                        "n_dial": 0x01004414, "n_info": 0x01004424,
                        "p_sub": "Es hora de estrenar esta Servoarmadura voladora. ¿Quién tiene la llave del Relicario Solar?",
                        "p_tts": "Es hora de estrenar esta Servoarmadura voladora. ¿Quién tiene la llave del Relicario Solar?",
                        "tiqs_stage": 120,
                        "n_responses": [
                            (
                                "Los autómatas contratistas del Pentágono que aún vigilan el tejado bajo la antena parabólica noreste de Fort Hagen, donde Clara libró su última misión el día de las bombas.",
                                "Los autómatas contratistas del Pentágono que aún vigilan el tejado bajo la antena parabólica noreste de Fort Hagen, donde Clara libró su última misión el día de las bombas.",
                            ),
                            (
                                "Antes de partir, entra en la Sala del Director que acabo de abrirte al sur del ala este y lee el lema del Gran Mural: lo necesitarás junto con la última holocinta de Clara para desbloquear el Cañón Orbital Gauss.",
                                "Antes de partir, entra en la Sala del Director que acabo de abrirte al sur del ala este y lee el lema del Gran Mural: lo necesitarás junto con la última holocinta de Clara para desbloquear el Cañón Orbital Gauss.",
                            ),
                        ],
                    },
                    {
                        "rnam": "Sobre el Cañón Orbital",
                        "p_dial": 0x01004415, "p_info": 0x01004425,
                        "n_dial": 0x01004416, "n_info": 0x01004426,
                        "p_sub": "¿Qué clase de bestia es ese Cañón Orbital Gauss del Relicario Solar?",
                        "p_tts": "¿Qué clase de bestia es ese Cañón Orbital Gauss del Relicario Solar?",
                        "tiqs_stage": 120,
                        "n_responses": [
                            (
                                "Es nuestra obra cumbre para la Servoarmadura Astro-Cosmos: un acelerador cuadrupolar con anillos de Saturno, mira orbital de ocho aumentos y descargas de supernova solar en pleno vuelo.",
                                "Es nuestra obra cumbre para la Servoarmadura Astro-Cosmos: un acelerador cuadrupolar con anillos de Saturno, mira orbital de ocho aumentos y descargas de supernova solar en pleno vuelo.",
                            ),
                            (
                                "Revisa primero el Gran Mural en la Sala del Director recién abierta, y luego vuela al tejado del búnker satelital de Fort Hagen a recuperar la Tarjeta Estelar Maestra de Clara.",
                                "Revisa primero el Gran Mural en la Sala del Director recién abierta, y luego vuela al tejado del búnker satelital de Fort Hagen a recuperar la Tarjeta Estelar Maestra de Clara.",
                            ),
                        ],
                    },
                    {
                        "rnam": "El sacrificio de Clara",
                        "p_dial": 0x01004417, "p_info": 0x01004427,
                        "n_dial": 0x01004418, "n_info": 0x01004428,
                        "p_sub": "Nunca regresó a Órbita-7 aquel 23 de octubre, ¿verdad?",
                        "p_tts": "Nunca regresó a Órbita Siete aquel veintitrés de octubre, ¿verdad?",
                        "tiqs_stage": 120,
                        "n_responses": [
                            (
                                "No... Gracias a que borró nuestro enlace satelital en Fort Hagen cuando ya sonaban las sirenas, el Pentágono jamás encontró Órbita-7.",
                                "No... Gracias a que borró nuestro enlace satelital en Fort Hagen cuando ya sonaban las sirenas, el Pentágono jamás encontró Órbita Siete.",
                            ),
                            (
                                "He abierto para ti su Sala de Proyección y Aposentos en el ala sureste. Contempla su mural, vuela después a la antena noreste de Fort Hagen y trae de vuelta su última grabación.",
                                "He abierto para ti su Sala de Proyección y Aposentos en el ala sureste. Contempla su mural, vuela después a la antena noreste de Fort Hagen y trae de vuelta su última grabación.",
                            ),
                        ],
                    },
                ],
            }
        ],
    },
    # ESCENA 5 (0x01004500): Etapa 165 -> 200 (Epílogo: Estudio Órbita-7 como Refugio Permanente)
    {
        "scen_fid": 0x01004500,
        "edid": "Orbita7Scene5_Epilogue",
        "phases": ["Ph1"],
        "actions": [
            {
                "action_idx": 1,
                "phase_idx": 0,
                "options": [
                    {
                        "rnam": "Un honor ser el Capitán",
                        "p_dial": 0x01004511, "p_info": 0x01004521,
                        "n_dial": 0x01004512, "n_info": 0x01004522,
                        "p_sub": "Clara salvó este lugar para que su ciencia protegiera a la gente. Prometo estar a la altura.",
                        "p_tts": "Clara salvó este lugar para que su ciencia protegiera a la gente. Prometo estar a la altura.",
                        "tiqs_stage": 200,
                        "n_responses": [
                            (
                                "Ya lo estás, amigo mío. Por eso quiero entregarte el Título de Custodia permanente del Estudio Subterráneo Órbita-7.",
                                "Ya lo estás, amigo mío. Por eso quiero entregarte el Título de Custodia permanente del Estudio Subterráneo Órbita Siete.",
                            ),
                            (
                                "Los aposentos del Capitán Cosmos con su cama espacial, los baúles estelares seguros y todos los talleres de ingeniería son ahora tu hogar permanente, y el Coronel y yo cuidaremos siempre de tu base.",
                                "Los aposentos del Capitán Cosmos con su cama espacial, los baúles estelares seguros y todos los talleres de ingeniería son ahora tu hogar permanente, y el Coronel y yo cuidaremos siempre de tu base.",
                            ),
                        ],
                    },
                    {
                        "rnam": "¿No echaré de menos los gritos?",
                        "p_dial": 0x01004513, "p_info": 0x01004523,
                        "n_dial": 0x01004514, "n_info": 0x01004524,
                        "p_sub": "Casi voy a echar de menos que el Coronel Agallas me llame alcornoque radiactivo.",
                        "p_tts": "Casi voy a echar de menos que el Coronel Agallas me llame alcornoque radiactivo.",
                        "tiqs_stage": 200,
                        "n_responses": [
                            (
                                "¡Ja, ja! Ahora que te ha ascendido a Capitán del Cosmos te cuadrará las pinzas cada vez que entres por la puerta.",
                                "¡Ja, ja! Ahora que te ha ascendido a Capitán del Cosmos te cuadrará las pinzas cada vez que entres por la puerta.",
                            ),
                            (
                                "Toma la escritura de propiedad de Órbita-7 y suministros del estudio: la cama del Capitán Cosmos, los baúles seguros y todos los bancos de trabajo son tu refugio permanente desde hoy.",
                                "Toma la escritura de propiedad de Órbita Siete y suministros del estudio: la cama del Capitán Cosmos, los baúles seguros y todos los bancos de trabajo son tu refugio permanente desde hoy.",
                            ),
                        ],
                    },
                    {
                        "rnam": "Un nuevo hogar seguro",
                        "p_dial": 0x01004515, "p_info": 0x01004525,
                        "n_dial": 0x01004516, "n_info": 0x01004526,
                        "p_sub": "Un búnker Art-Deco bajo el corazón de Boston nos vendrá de maravilla. ¿Qué harás tú ahora?",
                        "p_tts": "Un búnker Art-Deco bajo el corazón de Boston nos vendrá de maravilla. ¿Qué harás tú ahora?",
                        "tiqs_stage": 200,
                        "n_responses": [
                            (
                                "Me quedaré aquí manteniendo los reactores, los talleres y el planetario en marcha para cada vez que regreses de patrullar los cielos de la Commonwealth.",
                                "Me quedaré aquí manteniendo los reactores, los talleres y el planetario en marcha para cada vez que regreses de patrullar los cielos de la Commonwealth.",
                            ),
                            (
                                "Aquí tienes las llaves maestras y suministros de reserva: descansa en la cama del Capitán Cosmos y guarda tu equipo en los baúles estelares siempre que quieras.",
                                "Aquí tienes las llaves maestras y suministros de reserva: descansa en la cama del Capitán Cosmos y guarda tu equipo en los baúles estelares siempre que quieras.",
                            ),
                        ],
                    },
                    {
                        "rnam": "¡Hacia las estrellas!",
                        "p_dial": 0x01004517, "p_info": 0x01004527,
                        "n_dial": 0x01004518, "n_info": 0x01004528,
                        "p_sub": "¡Por la Verdad, las Estrellas y el Mañana, Artie! Ha sido un viaje inolvidable.",
                        "p_tts": "¡Por la Verdad, las Estrellas y el Mañana, Artie! Ha sido un viaje inolvidable.",
                        "tiqs_stage": 200,
                        "n_responses": [
                            (
                                "¡Por la Verdad, las Estrellas y el Mañana, Capitán! Hubris Comics escribió la leyenda, pero tú acabas de hacerla realidad sobre el cielo de Boston.",
                                "¡Por la Verdad, las Estrellas y el Mañana, Capitán! Hubris Comics escribió la leyenda, pero tú acabas de hacerla realidad sobre el cielo de Boston.",
                            ),
                            (
                                "El Estudio Subterráneo Órbita-7 es oficialmente tu refugio permanente. ¡Buen vuelo ahí arriba, héroe!",
                                "El Estudio Subterráneo Órbita Siete es oficialmente tu refugio permanente. ¡Buen vuelo ahí arriba, héroe!",
                            ),
                        ],
                    },
                ],
            }
        ],
    },
]

# ==============================================================================
# 4. LAS 3 HOLOCINTAS CON VOZ DE CLARA STERLING (NOTE 0x01001401..0x01001403)
# ==============================================================================
CLARA_HOLOTAPES = [
    {
        "note_fid": 0x01001401,
        "note_edid": "NoteOrbita7HoloClara1",
        "note_full": "Holocinta de Clara Sterling #1: La Identidad de Los Imparables",
        "scen_fid": 0x01004601,
        "scen_edid": "Orbita7HoloScene1_Clara",
        "dial_fid": 0x01004611,
        "info_fid": 0x01004621,
        "responses": [
            (
                "Registro de Clara Sterling, 22 de octubre de 2077, desde la azotea de Hubris Comics. Si has llegado volando hasta aquí, significa que Artie encontró por fin a alguien digno del Traje Astro-Cosmos.",
                "Registro de Clara Sterling, veintidós de octubre de dos mil setenta y siete, desde la azotea de Hubris Comics. Si has llegado volando hasta aquí, significa que Artie encontró por fin a alguien digno del Traje Astro-Cosmos.",
            ),
            (
                "He repartido las tres Bobinas Fotónicas de la Carabina de Rayos por los tejados de Boston. Y toma nota para el segundo examen de nuestro cascarrabias Coronel Agallas:",
                "He repartido las tres Bobinas Fotónicas de la Carabina de Rayos por los tejados de Boston. Y toma nota para el segundo examen de nuestro cascarrabias Coronel Agallas:",
            ),
            (
                "Todo lector recuerda a Silver Shroud, Grognak, Manta Man y la Señora del Misterio, pero el quinto miembro fundador de Los Imparables es la maestra del ilusionismo con chistera y varita: ¡El Inspector!",
                "Todo lector recuerda a Silver Shroud, Grognak, Manta Man y la Señora del Misterio, pero el quinto miembro fundador de Los Imparables es la maestra del ilusionismo con chistera y varita: ¡El Inspector!",
            ),
        ],
    },
    {
        "note_fid": 0x01001402,
        "note_edid": "NoteOrbita7HoloClara2",
        "note_full": "Holocinta de Clara Sterling #2: Sabotaje en ArcJet",
        "scen_fid": 0x01004602,
        "scen_edid": "Orbita7HoloScene2_Clara",
        "dial_fid": 0x01004612,
        "info_fid": 0x01004622,
        "responses": [
            (
                "Aquí Clara Sterling, infiltrada en la cubierta superior de ArcJet Systems. Hace una hora los contratistas del Departamento de Defensa intentaron confiscar el proyecto entero.",
                "Aquí Clara Sterling, infiltrada en la cubierta superior de ArcJet Systems. Hace una hora los contratistas del Departamento de Defensa intentaron confiscar el proyecto entero.",
            ),
            (
                "Fue precisamente ArcJet Systems la corporación aeroespacial que construyó en secreto nuestras toberas gemelas de vuelo para la Servoarmadura Astro-Cosmos.",
                "Fue precisamente ArcJet Systems la corporación aeroespacial que construyó en secreto nuestras toberas gemelas de vuelo para la Servoarmadura Astro-Cosmos.",
            ),
            (
                "He encerrado el Núcleo Sincrotrón y mi borrador del Especial Número Cincuenta en esta arca. Si el Coronel te pregunta qué corporación forjó nuestros propulsores, recuerda ese nombre: ArcJet Systems.",
                "He encerrado el Núcleo Sincrotrón y mi borrador del Especial Número Cincuenta en esta arca. Si el Coronel te pregunta qué corporación forjó nuestros propulsores, recuerda ese nombre: ArcJet Systems.",
            ),
        ],
    },
    {
        "note_fid": 0x01001403,
        "note_edid": "NoteOrbita7HoloClara3",
        "note_full": "Holocinta de Clara Sterling #3: Última Transmisión (23 Oct 2077)",
        "scen_fid": 0x01004603,
        "scen_edid": "Orbita7HoloScene3_Clara",
        "dial_fid": 0x01004613,
        "info_fid": 0x01004623,
        "responses": [
            (
                "23 de octubre de 2077... Están sonando las sirenas antiaéreas por todo el horizonte de Boston, pero acabo de purgar las coordenadas de Órbita-7 de esta antena de Fort Hagen.",
                "Veintitrés de octubre de dos mil setenta y siete... Están sonando las sirenas antiaéreas por todo el horizonte de Boston, pero acabo de purgar las coordenadas de Órbita Siete de esta antena de Fort Hagen.",
            ),
            (
                "Quienquiera que escuche esto en el mañana: para abrir el Relicario Solar, recuerda que el Cañón Orbital Gauss acelera cartuchos electromagnéticos de dos milímetros.",
                "Quienquiera que escuche esto en el mañana: para abrir el Relicario Solar, recuerda que el Cañón Orbital Gauss acelera cartuchos electromagnéticos de dos milímetros.",
            ),
            (
                "No voy a llegar a tiempo al refugio... Mi único deseo final es que algún día un alma decente use nuestra ciencia para proteger a los inocentes. Dile a Artie y a mi gruñón Coronel que valió la pena soñar con las estrellas.",
                "No voy a llegar a tiempo al refugio... Mi único deseo final es que algún día un alma decente use nuestra ciencia para proteger a los inocentes. Dile a Artie y a mi gruñón Coronel que valió la pena soñar con las estrellas.",
            ),
        ],
    },
]

# ==============================================================================
# 5. PLACAS INTERACTIVAS, TERMINALES, DOSSIERES Y LOS 4 EXÁMENES (12 PREGUNTAS)
# ==============================================================================
CLUE_MESSAGES = [
    (
        0x01001301,
        "MesgOrbita7VitrineCosmos",
        "Vitrina Conmemorativa — Capitán Cosmos Nº 1 (Marzo de 2063)",
        (
            "Tras el cristal blindado reluce un ejemplar original de «Las Aventuras del Capitán Cosmos Nº 1» junto a su placa curatorial:\r\n\r\n"
            "• COPILOTO FIEL: «Jangles el Mono Lunar», el chimpancé astronauta que salvó al Capitán de las minas gravitatorias de Venus.\r\n"
            "• CUARTEL GENERAL SECRETO: La Ciudadela Estelar oculta bajo el «Cráter Tycho» en la cara visible de la Luna.\r\n\r\n"
            "[Nota manuscrita al margen]: «¡Que ningún recluta olvide jamás a Jangles ni el Cráter Tycho antes de hablar con el Coronel!»"
        ),
        ["Cerrar"],
    ),
    (
        0x01001302,
        "MesgOrbita7VitrineUnstoppables",
        "Vitrina Conmemorativa — La Liga de Los Imparables",
        (
            "Una edición de coleccionista de «¡Los Imparables contra los Mutantes Cerebrales!» muestra a los cinco campeones de Hubris Comics:\r\n\r\n"
            "• Silver Shroud (El Vengador de la Noche)\r\n"
            "• Grognak el Bárbaro (Señor de las Tierras Yermas Prehistóricas)\r\n"
            "• Manta Man (El Defensor de las Profundidades)\r\n"
            "• La Señora del Misterio (Dama de las Sombras)\r\n"
            "• El quinto miembro aparece cubierto por un sello confidencial: «Ver Holocinta #1 de Clara Sterling en la azotea de Hubris Comics»."
        ),
        ["Cerrar"],
    ),
    (
        0x01001303,
        "MesgOrbita7DraftingDesk",
        "Restirador de Entintado — Clara Sterling (Guionista Jefa)",
        (
            "Sobre el tablero iluminado descansan tres frascos de tinta pigmentada junto a la Ficha Oficial de Color del Proyecto Astro-Cosmos:\r\n\r\n"
            "• TRÍADA CROMÁTICA REGLAMENTARIA DEL CAPITÁN COSMOS:\r\n"
            "  1. «Azul Cobalto» para el fuselaje espacial presurizado.\r\n"
            "  2. «Rojo Carmesí» para la capa heroica, botas y guanteletes.\r\n"
            "  3. «Oro Solar» para el emblema estelar de ocho puntas y los anillos aceleradores.\r\n\r\n"
            "[Nota de Clara]: «Artie quería pintarlo de verde oliva militar. ¡Sobre mi cadáver! Azul Cobalto, Rojo Carmesí y Oro Solar.»"
        ),
        ["Cerrar"],
    ),
    (
        0x01001304,
        "MesgOrbita7DirectorMural",
        "Gran Mural del Juramento Estelar — Sala del Director",
        (
            "Un monumental óleo retroiluminado en oro y cobalto preside la Sala de Proyección Privada de Hubris Comics.\r\n\r\n"
            "Bajo la silueta del Capitán Cosmos alzándose hacia los anillos de Saturno, brilla inscrito en letras de bronce el Juramento Supremo de la Orden Estelar:\r\n\r\n"
            "«¡POR LA VERDAD, LAS ESTRELLAS Y EL MAÑANA!»"
        ),
        ["Memorizar el Juramento Estelar"],
    ),
]

EXAM_QUESTIONS = [
    # --- EXAMEN 1 (0x01001311..0x01001313) ---
    (
        0x01001311,
        "MesgOrbita7Exam1Q1",
        "EXAMEN DE RECLUTA (1/3) — Coronel Agallas «Cosmos»",
        "«¡PRIMERA PREGUNTA, GUSANO TERRÍCOLA!\r\n\r\n¿Cómo se llama el heroico copiloto simio del Capitán Cosmos y en qué cráter lunar se oculta su base secreta?»",
        [
            "Bobo el Chimpancé Atómico, en el Mar de la Tranquilidad",
            "Jangles el Mono Lunar, en el Cráter Tycho",
            "El Sargento Plátano, en los Anillos de Júpiter",
            "[Salir y revisar las pistas primero]",
        ],
    ),
    (
        0x01001312,
        "MesgOrbita7Exam1Q2",
        "EXAMEN DE RECLUTA (2/3) — Coronel Agallas «Cosmos»",
        "«¡SEGUNDA PREGUNTA, RENACUAJO!\r\n\r\nSegún el restirador oficial de Clara Sterling, ¿cuál es la tríada exacta de colores reglamentarios del uniforme Astro-Cosmos?»",
        [
            "Verde Ejército, Gris Plomo y Amarillo Mostaza",
            "Rosa Chicle, Morado Mutante y Plata Cromada",
            "Azul Cobalto, Rojo Carmesí y Oro Solar",
            "[Salir y revisar las pistas primero]",
        ],
    ),
    (
        0x01001313,
        "MesgOrbita7Exam1Q3",
        "EXAMEN DE RECLUTA (3/3) — Coronel Agallas «Cosmos»",
        "«¡TERCERA Y ÚLTIMA PREGUNTA PARA EL TRAJE!\r\n\r\nSegún el Terminal de Producción de TV, ¿qué fecha y canal estaban fijados para el gran estreno televisivo del Capitán Cosmos?»",
        [
            "15 de noviembre de 2077, en el Canal 5 de Boston",
            "4 de julio de 2076, en Radio Libertad",
            "31 de octubre de 2077, en la Red Vault-Tec",
            "[Salir y revisar las pistas primero]",
        ],
    ),
    # --- EXAMEN 2 (0x01001314..0x01001316) ---
    (
        0x01001314,
        "MesgOrbita7Exam2Q1",
        "EXAMEN DE PATRULLA AÉREA (1/3) — Coronel Agallas «Cosmos»",
        "«¡ATENCIÓN, CADETE VOLADOR!\r\n\r\nJunto a Silver Shroud, Grognak, Manta Man y la Señora del Misterio, ¿quién completa el quinteto fundador de Los Imparables?»",
        [
            "El Capitán Albóndiga de Concord",
            "El Fontanero Enmascarado de Nuka-World",
            "El Inspector, maestra del ilusionismo con chistera y varita",
            "[Salir y revisar las pistas primero]",
        ],
    ),
    (
        0x01001315,
        "MesgOrbita7Exam2Q2",
        "EXAMEN DE PATRULLA AÉREA (2/3) — Coronel Agallas «Cosmos»",
        "«¡SEGUNDA PREGUNTA DE PATRULLA!\r\n\r\nSegún el Expediente Editorial recuperado en Trinity Plaza, ¿quién es el archienemigo jurado de Grognak el Bárbaro?»",
        [
            "El Hechicero Maldito (Forjador de Maldiciones)",
            "El Contable Siniestro de Hacienda",
            "El Cangrejo Gigante del Río Charles",
            "[Salir y revisar las pistas primero]",
        ],
    ),
    (
        0x01001316,
        "MesgOrbita7Exam2Q3",
        "EXAMEN DE PATRULLA AÉREA (3/3) — Coronel Agallas «Cosmos»",
        "«¡TERCERA PREGUNTA PARA DESBLOQUEAR LA CARABINA DE RAYOS!\r\n\r\nSegún el guion radiofónico de la emisora WRVR, ¿cuál es la Máxima de Oro del Código de Los Imparables?»",
        [
            "Dispara primero y cobra los derechos de autor después",
            "El cerebro supera al músculo cuando los héroes luchan unidos",
            "Nunca planches tu capa con un reactor de fusión encendido",
            "[Salir y revisar las pistas primero]",
        ],
    ),
    # --- EXAMEN 3 (0x01001317..0x01001319) ---
    (
        0x01001317,
        "MesgOrbita7Exam3Q1",
        "EXAMEN DE PILOTO ORBITAL (1/3) — Coronel Agallas «Cosmos»",
        "«¡FIRME, ASPIRANTE A TITÁN ESTELAR!\r\n\r\n¿Qué corporación aeroespacial de Boston construyó en secreto las toberas gemelas de la Servoarmadura Astro-Cosmos?»",
        [
            "Fábrica de Conservas Longneck Lukowski",
            "ArcJet Systems",
            "Super Duper Mart División Cohetes",
            "[Salir y revisar las pistas primero]",
        ],
    ),
    (
        0x01001318,
        "MesgOrbita7Exam3Q2",
        "EXAMEN DE PILOTO ORBITAL (2/3) — Coronel Agallas «Cosmos»",
        "«¡SEGUNDA PREGUNTA ORBITAL!\r\n\r\nEn el borrador censurado del Especial Número 50 del Capitán Cosmos, ¿qué tirano galáctico intenta incendiar la Tierra con tormentas radiactivas?»",
        [
            "El Barón Albóndiga del Planeta Plutón",
            "La Reina Mutarrata del Cinturón de Asteroides",
            "El Emperador Quásar",
            "[Salir y revisar las pistas primero]",
        ],
    ),
    (
        0x01001319,
        "MesgOrbita7Exam3Q3",
        "EXAMEN DE PILOTO ORBITAL (3/3) — Coronel Agallas «Cosmos»",
        "«¡TERCERA PREGUNTA PARA ABRIR EL HANGAR DE LA SERVOARMADURA!\r\n\r\nAdemás del vuelo sostenido, ¿qué defensa legendaria incorpora el Torso Astro-Cosmos tanto en el cómic Nº 50 como en el prototipo real?»",
        [
            "Escudo de Inmunidad Cósmica total contra la radiación",
            "Dispensador automático de café hirviendo en el casco",
            "Camuflaje con olor a lavanda espacial",
            "[Salir y revisar las pistas primero]",
        ],
    ),
    # --- EXAMEN MAESTRO 4 (0x0100131A..0x0100131C) ---
    (
        0x0100131A,
        "MesgOrbita7Exam4Q1",
        "EXAMEN MAESTRO «CAPITÁN DEL COSMOS» (1/3)",
        "«¡ATENCIÓN EN LA SALA! ¡PRIMERA PREGUNTA DEL EXAMEN SUPREMO!\r\n\r\n¿Cuál es el Juramento Supremo inscrito en el Gran Mural de la Sala del Director?»",
        [
            "¡Más rápido que un impuesto y más duro que un ladrillo!",
            "¡Por las chapas, el tocino y la siesta del domingo!",
            "¡Por la Verdad, las Estrellas y el Mañana!",
            "[Salir y revisar las pistas primero]",
        ],
    ),
    (
        0x0100131B,
        "MesgOrbita7Exam4Q2",
        "EXAMEN MAESTRO «CAPITÁN DEL COSMOS» (2/3)",
        "«¡SEGUNDA PREGUNTA SUPREMA!\r\n\r\nSegún la última transmisión de Clara Sterling desde Fort Hagen, ¿qué calibre acelera el Cañón Orbital Gauss Astro-Cosmos?»",
        [
            "Pelotas de béisbol firmadas de Diamond City",
            "Cartuchos electromagnéticos de 2 mm EC",
            "Chapas de zarzaparrilla oxidada",
            "[Salir y revisar las pistas primero]",
        ],
    ),
    (
        0x0100131C,
        "MesgOrbita7Exam4Q3",
        "EXAMEN MAESTRO «CAPITÁN DEL COSMOS» (3/3)",
        "«¡ÚLTIMA PREGUNTA PARA RECIBIR EL RANGO DE CAPITÁN DEL COSMOS!\r\n\r\nMientras caían las bombas aquel 23 de octubre de 2077, ¿cuál fue el último deseo de Clara Sterling al salvar Órbita-7?»",
        [
            "Que algún día un alma decente usara su ciencia para proteger a los inocentes",
            "Que subastaran los prototipos al mejor postor del Pentágono",
            "Que nadie volviera a leer un cómic jamás en la Commonwealth",
            "[Salir y revisar las pistas primero]",
        ],
    ),
]

# ==============================================================================
# 6. MENSAJES DE CAMPAÑA, TERMINALES, DOSSIERES Y ETAPAS/OBJETIVOS DEL DIARIO
# ==============================================================================
EXTRA_MESSAGES = [
    (
        0x01001300,
        "MesgOrbita7RadioIntercept",
        "[PROYECTO ASTRO-COSMOS — FRECUENCIA HUBRIS INTERCEPTADA]",
        (
            "Tu Pip-Boy ha captado una portadora civil de onda corta procedente del subsuelo de Boston, "
            "justo bajo el callejón contiguo a la sede central de Hubris Comics:\r\n\r\n"
            "«...Aquí Arturo 'Artie' Vance, Ingeniero Jefe de Efectos Especiales y Propulsión Aeroespacial "
            "de Hubris Comics, transmitiendo desde el Estudio Subterráneo Órbita-7.\r\n\r\n"
            "Si algún portador de Pip-Boy con corazón de héroe escucha esto: los reactores del estudio "
            "han despertado tras doscientos diez años. Custodiamos aquí abajo los cuatro prototipos reales "
            "de vuelo y armamento cósmico del Capitán Cosmos... junto con un Coronel Agallas reprogramado "
            "que se niega a abrir las cámaras acorazadas a nadie que no supere sus exámenes sobre la historia "
            "de Hubris Comics.\r\n\r\n"
            "He desbloqueado la escotilla blindada exterior en el callejón trasero de Hubris Comics y enviado "
            "las coordenadas a tu mapa. ¡Baja a verme cuando puedas, camarada!»"
        ),
        ["Sintonizar coordenadas del Estudio Subterráneo Órbita-7"],
    ),
    (
        0x01001323,
        "MesgOrbita7ExamNotReady",
        "Consola «Protocolo del Verdadero Creyente» — Acceso en Espera",
        (
            "La pantalla CRT de la consola parpadea en ámbar estelar:\r\n\r\n"
            "«ESTADO DEL SISTEMA: Fase de misión en curso.\r\n"
            "Completa primero los objetivos de campo o habla con el ingeniero jefe Artie Vance "
            "para habilitar el siguiente interrogatorio reglamentario del Coronel Agallas.»"
        ),
        ["Entendido"],
    ),
    (
        0x01001324,
        "MesgOrbita7HomeUnlocked",
        "¡Refugio Permanente Desbloqueado: Estudio Subterráneo Órbita-7!",
        (
            "¡Enhorabuena, Capitán del Cosmos! Has completado «El Legado de Hubris: Proyecto Astro-Cosmos» "
            "y reunido los cuatro prototipos aeroespaciales:\r\n\r\n"
            "• Traje de Vuelo Astro-Cosmos (vuelo libre [Y] + escudo antirradiación 100%%)\r\n"
            "• Carabina de Rayos Astro-Cosmos (arma aérea para traje y PA con mira 6x)\r\n"
            "• Servoarmadura Astro-Cosmos (6 piezas orbitales con vuelo integrado)\r\n"
            "• Cañón Orbital Gauss Astro-Cosmos (arma aérea pesada para PA y traje con mira 8x)\r\n\r\n"
            "El Estudio Subterráneo Órbita-7 es ahora tu hogar permanente en el corazón de Boston:\r\n"
            "• Cama Espacial del Capitán Cosmos con bonificación de «Bien descansado».\r\n"
            "• Baúles Estelares Acorazados 100%% seguros (nunca se reinician).\r\n"
            "• Estación de Servoarmadura, Banco de Armas, Banco de Armaduras, Química y Cocina.\r\n"
            "• Viaje rápido directo habilitado y custodiado por Artie Vance y el Coronel Agallas."
        ),
        ["¡Por la Verdad, las Estrellas y el Mañana!"],
    ),
]

TERMINAL_PRODUCTION_TV = {
    "fid": 0x01001140,
    "edid": "TermOrbita7ProductionTV",
    "full": "Terminal de Producción de TV — Clara Sterling",
    "header": (
        "HUBRIS COMICS TELEVISION & ESTUDIO SUBTERRÁNEO ÓRBITA-7\r\n"
        "Despacho de Guionistas — Terminal de Clara Sterling (Guionista Jefa)\r\n"
        "Seleccione un registro editorial:"
    ),
    "entries": [
        (
            "1. Calendario Oficial de Estreno en TV (Otoño 2077)",
            (
                "MEMORANDO INTERNO — DIVISIÓN AUDIOVISUAL HUBRIS COMICS\r\n"
                "De: Clara Sterling, Productora Ejecutiva y Guionista Jefa\r\n"
                "Asunto: ¡FECHA CONFIRMADA DE ESTRENO EN ACCIÓN REAL!\r\n\r\n"
                "¡Lo hemos logrado, equipo! Tras la demostración de vuelo real de Artie bajo la "
                "cúpula del Planetario, la cadena regional ha firmado la emisión en horario estelar:\r\n\r\n"
                "- FECHA DE ESTRENO: 15 de noviembre de 2077\r\n"
                "- CADENA OFICIAL: Canal 5 de Boston (WGBH / Red Metropolitana)\r\n"
                "- TÍTULO DEL PILOTO: «El Capitán Cosmos y la Fortaleza del Cráter Tycho»\r\n\r\n"
                "Recordad esta fecha y cadena (15 de noviembre de 2077, en el Canal 5 de Boston): "
                "el gruñón de nuestro Coronel Agallas la ha programado como tercera pregunta "
                "obligatoria del Examen de Recluta."
            ),
        ),
        (
            "2. Sobre nuestro nuevo Jefe de Seguridad: Coronel Agallas «Cosmos»",
            (
                "REGISTRO DE PRODUCCIÓN — 14 DE SEPTIEMBRE DE 2077\r\n\r\n"
                "El Departamento de Defensa nos envió un Mister Gutsy excedente del Ejército para "
                "vigilar las cámaras de estasis de los prototipos. Artie cometió la genial imprudencia "
                "de cargar en su matriz neuronal las 420 revistas de Hubris Comics.\r\n\r\n"
                "¿El resultado? Ahora se hace llamar «Coronel Agallas Cosmos», cree que todo civil es "
                "un 'gusano terrícola sin cultura de viñeta' y ha conectado las barreras fotónicas a su "
                "Consola del Verdadero Creyente. Si fallas una sola pregunta te pone de vuelta y media, "
                "pero en el fondo nos ha cogido un cariño entrañable."
            ),
        ),
        (
            "3. Alerta Confidencial: Movimientos del Pentágono (21 Oct 2077)",
            (
                "NOTA CIFRADA — SOLO PARA OJOS DE ARTURO VANCE\r\n\r\n"
                "Artie: los generales del enlace militar quieren cancelar el estreno de televisión y "
                "llevarse nuestros cuatro prototipos como armas de asalto orbital. No pienso permitirlo.\r\n\r\n"
                "Esta noche subiré a las azoteas de Boston para dispersar las Bobinas Fotónicas de la "
                "Carabina de Rayos, llevaré el Núcleo Sincrotrón a la cubierta superior de ArcJet Systems "
                "y ocultaré mi Tarjeta Estelar Maestra en el nodo satelital de Fort Hagen. Solo alguien "
                "que vuele como el verdadero Capitán Cosmos y conozca nuestras historias podrá reunirlos."
            ),
        ),
    ],
}

TERMINAL_ARTIE_LAB = {
    "fid": 0x01001141,
    "edid": "TermOrbita7ArtieLab",
    "full": "Terminal de Ingeniería Fotónica — Arturo «Artie» Vance",
    "header": (
        "ESTUDIO SUBTERRÁNEO ÓRBITA-7 — LABORATORIO DE PROPULSIÓN Y ARMAMENTO\r\n"
        "Ingeniero Jefe: Dr. Arturo «Artie» Vance\r\n"
        "Seleccione un expediente técnico:"
    ),
    "entries": [
        (
            "1. Ficha Técnica I: Traje de Vuelo Astro-Cosmos",
            (
                "PROTOTIPO N.º 1 — TRAJE DE VUELO ASTRO-COSMOS\r\n\r\n"
                "- Propulsión: Micro-impulsores vectoriales alimentados por resonancia atómica "
                "(activar/desactivar en el aire o en tierra con el botón de salto [Y] / [Triángulo] / [Espacio]).\r\n"
                "- Protección: Tejido trenzado en Azul Cobalto, Rojo Carmesí y Oro Solar equipado con "
                "el legendario Escudo de Inmunidad Cósmica total contra la radiación (0.0 RAD incluso "
                "en el epicentro del Mar Resplandeciente) y amortiguadores de caída orbital."
            ),
        ),
        (
            "2. Ficha Técnica II: Carabina de Rayos Astro-Cosmos (Mira 6x)",
            (
                "PROTOTIPO N.º 2 — CARABINA DE RAYOS ASTRO-COSMOS\r\n\r\n"
                "- Arma fotónica ligera giroscópicamente sincronizada tanto con el Traje de Vuelo "
                "Astro-Cosmos como con la Servoarmadura Astro-Cosmos para disparo sostenido en pleno vuelo.\r\n"
                "- Óptica: Mira Telescópica de Reconocimiento Astro-Cosmos de 6 aumentos con marcado "
                "automático de blancos desde gran altitud.\r\n"
                "- Efecto Cósmico: Cada cuarto impacto libera un Pulso Fotónico Cósmico (+25 PA, +15 PS)."
            ),
        ),
        (
            "3. Ficha Técnica III: Servoarmadura Astro-Cosmos (Convenio ArcJet)",
            (
                "PROTOTIPO N.º 3 — SERVOARMADURA ASTRO-COSMOS (SERIE ORBITAL)\r\n\r\n"
                "- Desarrollada conjuntamente con los ingenieros de propulsión de ArcJet Systems, "
                "quienes fabricaron en secreto las toberas gemelas dorsales de flujo continuo.\r\n"
                "- Incorpora seis piezas acorazadas en aleación cobalto-oro y Escudo de Inmunidad "
                "Cósmica antirradiación integrado en el torso."
            ),
        ),
        (
            "4. Ficha Técnica IV: Cañón Orbital Gauss Astro-Cosmos (Mira 8x)",
            (
                "PROTOTIPO N.º 4 — CAÑÓN ORBITAL GAUSS ASTRO-COSMOS\r\n\r\n"
                "- Arma pesada de largo alcance totalmente compatible en pleno vuelo tanto con la "
                "Servoarmadura Astro-Cosmos como con el Traje de Vuelo Astro-Cosmos.\r\n"
                "- Munición: Acelera cartuchos electromagnéticos de 2 mm EC a velocidades orbitales "
                "a través de cuatro bobinas toroidales Saturno.\r\n"
                "- Óptica y Efecto: Mira de Observatorio Orbital de 8 aumentos; cada tercer impacto "
                "desata una Supernova Gravitatoria Solar (+35 PA, +25 PS y onda expansiva)."
            ),
        ),
    ],
}


def _build_exam_terminal_defs() -> list[dict]:
    """Construye la jerarquía continua de 21 registros TERM (`0x01001500..0x01001514`)."""
    exams_meta = [
        (
            1,
            "Examen de Recluta Orbital",
            "Traje de Vuelo Astro-Cosmos",
            "la Vitrina #1, el Restirador de Clara Sterling y la Terminal de Producción de TV",
            (1, 2, 0),
        ),
        (
            2,
            "Examen de Patrulla Aérea",
            "Carabina de Rayos Astro-Cosmos",
            "la Vitrina #2 de Los Imparables, el Expediente de Trinity Plaza y el Guion de WRVR",
            (2, 0, 1),
        ),
        (
            3,
            "Examen de Piloto Orbital",
            "Servoarmadura Astro-Cosmos",
            "la Terminal de Ingeniería de Artie y el Borrador Censurado recuperado en ArcJet Systems",
            (1, 2, 0),
        ),
        (
            4,
            "Examen Maestro «Capitán del Cosmos»",
            "Cañón Orbital Gauss Astro-Cosmos",
            "el Gran Mural del Director y la última Holocinta de Clara en Fort Hagen",
            (2, 1, 0),
        ),
    ]

    main_term = {
        "fid": 0x01001500,
        "edid": "TermOrbita7ExamMain",
        "full": "Consola de Exámenes «¡Desafío Cósmico!»",
        "header": (
            "HUBRIS COMICS — ESTUDIO SUBTERRÁNEO ÓRBITA-7\r\n"
            "SISTEMA DE EVALUACIÓN «¡DESAFÍO CÓSMICO!» — CORONEL AGALLAS\r\n"
            "Supera las 3 preguntas seguidas sin errores para abrir la barrera fotónica:"
        ),
        "entries": [
            {
                "itxt": "[Acceso Bloqueado — Regístrate con el Dr. Artie Vance]",
                "anam": 0x08,
                "itid": 10,
                "conds": [("stage", 0x80, 20.0)],
                "unam": (
                    "TERMINAL EN ESPERA DE ALTA DE CONCURSANTE.\r\n\r\n"
                    "Habla primero con el Dr. Arturo «Artie» Vance aquí en la Rotonda Central "
                    "para activar el circuito oficial de exámenes del Coronel Agallas."
                ),
            },
            {
                "itxt": "Iniciar Examen 1: Recluta Orbital (Traje de Vuelo)",
                "anam": 0x04,
                "itid": 101,
                "tnam": 0x01001501,
                "conds": [("stage", 0x00, 20.0)],
            },
            {
                "itxt": "Iniciar Examen 2: Patrulla Aérea (Carabina de Rayos)",
                "anam": 0x04,
                "itid": 102,
                "tnam": 0x01001506,
                "conds": [("stage", 0x00, 50.0)],
            },
            {
                "itxt": "Iniciar Examen 3: Piloto Orbital (Servoarmadura)",
                "anam": 0x04,
                "itid": 103,
                "tnam": 0x0100150B,
                "conds": [("stage", 0x00, 80.0)],
            },
            {
                "itxt": "Iniciar Examen 4: Capitán del Cosmos (Cañón Orbital)",
                "anam": 0x04,
                "itid": 104,
                "tnam": 0x01001510,
                "conds": [("stage", 0x00, 140.0)],
            },
            {
                "itxt": "[Examen aprobado — Reclama tu prototipo desbloqueado]",
                "anam": 0x08,
                "itid": 110,
                "conds": [
                    ("stage", 0x01, 30.0),
                    ("stage", 0x01, 60.0),
                    ("stage", 0x01, 100.0),
                    ("stage", 0x00, 160.0),
                ],
                "unam": (
                    "¡BARRERA FOTÓNICA DESACTIVADA!\r\n\r\n"
                    "Tu último examen ya figura como APROBADO en el registro militar del "
                    "Coronel Agallas. Dirígete a la cámara desbloqueada para recoger tu "
                    "nuevo prototipo Astro-Cosmos."
                ),
            },
            {
                "itxt": "[Misión de campo activa — Completa objetivo o habla con Artie]",
                "anam": 0x08,
                "itid": 111,
                "conds": [
                    ("stage", 0x01, 35.0),
                    ("stage", 0x01, 40.0),
                    ("stage", 0x01, 65.0),
                    ("stage", 0x01, 70.0),
                    ("stage", 0x01, 110.0),
                    ("stage", 0x01, 120.0),
                    ("stage", 0x00, 165.0),
                ],
                "unam": (
                    "FASE DE OPERACIÓN DE CAMPO EN CURSO.\r\n\r\n"
                    "El siguiente examen permanecerá cerrado hasta que completes la misión "
                    "exterior actual o informes de tus hallazgos al Dr. Artie Vance."
                ),
            },
            {
                "itxt": "[Rango Supremo: Capitán del Cosmos — Todo superado]",
                "anam": 0x08,
                "itid": 120,
                "conds": [("stage", 0x60, 200.0)],
                "unam": (
                    "EXPEDIENTE DE HONOR DEL CORONEL AGALLAS «COSMOS»:\r\n\r\n"
                    "Has completado los cuatro exámenes reglamentarios y reunido todo el "
                    "arsenal Astro-Cosmos. El Estudio Subterráneo Órbita-7 es tu base permanente.\r\n"
                    "¡Por la Verdad, las Estrellas y el Mañana!"
                ),
            },
            {
                "itxt": "[Simulacro Libre I: Prueba de Recluta Orbital]",
                "anam": 0x04,
                "itid": 101,
                "tnam": 0x01001501,
                "conds": [("stage", 0x60, 200.0)],
            },
            {
                "itxt": "[Simulacro Libre II: Tiro y Patrulla Aérea]",
                "anam": 0x04,
                "itid": 102,
                "tnam": 0x01001506,
                "conds": [("stage", 0x60, 200.0)],
            },
            {
                "itxt": "[Simulacro Libre III: Ingeniería de Chasis Pesado]",
                "anam": 0x04,
                "itid": 103,
                "tnam": 0x0100150B,
                "conds": [("stage", 0x60, 200.0)],
            },
            {
                "itxt": "[Simulacro Libre IV: Examen Maestro Capitán del Cosmos]",
                "anam": 0x04,
                "itid": 104,
                "tnam": 0x01001510,
                "conds": [("stage", 0x60, 200.0)],
            },
            {
                "itxt": "Reglamento del Concurso «¡Desafío Cósmico!»",
                "anam": 0x08,
                "itid": 130,
                "conds": [],
                "unam": (
                    "REGLAMENTO OFICIAL DEL CORONEL AGALLAS:\r\n\r\n"
                    "1. Cada examen consta de 3 preguntas consecutivas dentro de esta terminal.\r\n"
                    "2. Responder correctamente avanza automáticamente a la siguiente pregunta.\r\n"
                    "3. Un solo error anula el intento y requiere reiniciar el examen desde cero.\r\n"
                    "4. Todas las respuestas se encuentran en las vitrinas, restiradores, "
                    "terminales, expedientes y holocintas de Clara Sterling."
                ),
            },
        ],
    }

    terms = [main_term]
    for e_idx, e_title, reward_name, clues_hint, correct_tuple in exams_meta:
        base_fid = 0x01001501 + ((e_idx - 1) * 5)
        pass_fid = base_fid + 3
        fail_fid = base_fid + 4

        for q_idx in range(3):
            q_fid = base_fid + q_idx
            next_fid = base_fid + q_idx + 1 if q_idx < 2 else pass_fid
            _m_fid, _m_edid, _m_title, raw_body, btns = EXAM_QUESTIONS[((e_idx - 1) * 3) + q_idx]
            if "\r\n\r\n" in raw_body:
                q_clean = raw_body.split("\r\n\r\n", 1)[1].rstrip("»").strip()
            else:
                q_clean = raw_body.strip("«»").strip()

            progress_banner = ""
            if q_idx == 1:
                progress_banner = "[✓ PREGUNTA 1 SUPERADA]\r\n"
            elif q_idx == 2:
                progress_banner = "[✓ PREGUNTAS 1 Y 2 SUPERADAS — PREGUNTA FINAL]\r\n"

            q_header = (
                f"{e_title.upper()} — PREGUNTA {q_idx + 1} DE 3\r\n"
                f"{progress_banner}\r\n"
                f"{q_clean}"
            )

            q_entries = []
            wrong_seq = 0
            for b_i in range(3):
                is_right = (b_i == correct_tuple[q_idx])
                if is_right:
                    tgt_fid = next_fid
                    itid = (30 + e_idx) if q_idx == 2 else (11 + q_idx)
                else:
                    tgt_fid = fail_fid
                    itid = 21 + (q_idx * 2) + wrong_seq
                    wrong_seq += 1
                q_entries.append(
                    {
                        "itxt": btns[b_i],
                        "anam": 0x04,
                        "itid": itid,
                        "tnam": tgt_fid,
                    }
                )
            q_entries.append(
                {
                    "itxt": "[Retirarse para consultar las pistas del estudio]",
                    "anam": 0x05,
                    "itid": 90,
                }
            )
            terms.append(
                {
                    "fid": q_fid,
                    "edid": f"TermOrbita7Exam{e_idx}Q{q_idx + 1}",
                    "full": f"Examen {e_idx} — Pregunta {q_idx + 1}/3",
                    "header": q_header,
                    "entries": q_entries,
                }
            )

        # Pantalla de Victoria (3/3)
        terms.append(
            {
                "fid": pass_fid,
                "edid": f"TermOrbita7Exam{e_idx}Pass",
                "full": f"Examen {e_idx} — ¡Aprobado!",
                "header": (
                    f"¡¡3 DE 3 ACERTADAS — {e_title.upper()} APROBADO!!\r\n\r\n"
                    f"Registro del Coronel Agallas:\r\n"
                    f"«Increíble... la barrera fotónica acaba de desactivarse.\r\n"
                    f"Ya puedes dirigirte a recoger tu {reward_name}.»"
                ),
                "entries": [
                    {
                        "itxt": "[Volver al menú principal e ir a recoger prototipo]",
                        "anam": 0x05,
                        "itid": 99,
                    }
                ],
            }
        )

        # Pantalla de Fallo (Reinicio)
        terms.append(
            {
                "fid": fail_fid,
                "edid": f"TermOrbita7Exam{e_idx}Fail",
                "full": f"Examen {e_idx} — Respuesta Incorrecta",
                "header": (
                    f"¡RESPUESTA INCORRECTA — {e_title.upper()} ANULADO!\r\n\r\n"
                    f"El jurado del Coronel Agallas exige 3 aciertos seguidos.\r\n"
                    f"Pista de estudio: revisa con calma {clues_hint}."
                ),
                "entries": [
                    {
                        "itxt": "Reintentar este examen desde la Pregunta 1",
                        "anam": 0x04,
                        "itid": 104 + e_idx,
                        "tnam": base_fid,
                    },
                    {
                        "itxt": "[Volver al menú principal para revisar las pistas]",
                        "anam": 0x05,
                        "itid": 91,
                    },
                ],
            }
        )

    return terms


EXAM_TERMINAL_DEFS = _build_exam_terminal_defs()

BOOK_DOSSIERS = [
    (
        0x01001160,
        "BookOrbita7GrognakDossier",
        "Expediente Hubris: Archienemigos de Grognak",
        (
            "ARCHIVO EDITORIAL DE HUBRIS COMICS — DOSSIER DE PERSONAJES CLÁSICOS\r\n"
            "Serie: «Grognak el Bárbaro» (Creado por Rod Gamber)\r\n\r\n"
            "Entre todos los monstruos prehistóricos y tiranos que se han cruzado con el hacha "
            "de doble filo de Grognak, solo uno ostenta el título oficial de ARCHIENEMIGO JURADO:\r\n\r\n"
            "• «EL HECHICERO MALDITO» (también traducido en las primeras tiradas como el Forjador "
            "de Maldiciones / Kurse-Maker), señor de las artes arcanas oscuras que juró encadenar "
            "el espíritu indomable del Bárbaro.\r\n\r\n"
            "[Nota manuscrita de Clara Sterling]:\r\n"
            "«Si estás leyendo esto en la terraza alta de Trinity Plaza, ¡buen vuelo! Guarda la "
            "segunda Bobina Fotónica y no olvides el nombre de 'El Hechicero Maldito' para el "
            "segundo examen del Coronel Agallas.»"
        ),
    ),
    (
        0x01001161,
        "BookOrbita7WRVRScript",
        "Guion Radiofónico WRVR: El Código de Los Imparables",
        (
            "EMISORA WRVR DE BOSTON — LIBRETO DE GALA ESPECIAL (OCTUBRE DE 2077)\r\n"
            "Episodio: «¡La Alianza Eterna de Los Imparables!»\r\n\r\n"
            "NARRADOR (con eco heroico):\r\n"
            "«Cuando la noche cae sobre la metrópoli y el crimen alza sus tentáculos, cinco voces "
            "pronuncian al unísono la MÁXIMA DE ORO DEL CÓDIGO DE LOS IMPARABLES!»\r\n\r\n"
            "TODOS LOS HÉROES AL UNÍSONO:\r\n"
            "«¡EL CEREBRO SUPERA AL MÚSCULO CUANDO LOS HÉROES LUCHAN UNIDOS!»\r\n\r\n"
            "[Nota manuscrita de Clara Sterling al pie del libreto]:\r\n"
            "«¡Mi frase favorita de toda la serie! Recoge la tercera Bobina Fotónica de esta azotea "
            "de WRVR y recítale esa máxima exacta al Coronel Agallas para desbloquear la Carabina "
            "de Rayos Astro-Cosmos.»"
        ),
    ),
    (
        0x01001162,
        "BookOrbita7Cosmos50Draft",
        "Borrador Censurado: Capitán Cosmos Especial Nº 50",
        (
            "HUBRIS COMICS — GUION ORIGINAL ÍNTEGRO (EJEMPLAR DE CLARA STERLING)\r\n"
            "Título: «Capitán Cosmos Especial N.º 50: ¡Asedio desde la Estrella Negra!»\r\n\r\n"
            "SINOPSIS OFICIAL:\r\n"
            "Desde su acorazado en la nebulosa exterior, el despiadado tirano galáctico conocido como "
            "«EL EMPERADOR QUÁSAR» desata una tormenta de radiación letal para abrasar la atmósfera "
            "de la Tierra.\r\n\r\n"
            "Para atravesar el cinturón de fuego atómico sin sufrir ni un solo rasguño, el Capitán "
            "Cosmos viste por primera vez su titánica Servoarmadura Orbital equipada con el legendario "
            "«ESCUDO DE INMUNIDAD CÓSMICA TOTAL CONTRA LA RADIACIÓN», desarrollado en nuestra realidad "
            "junto a los ingenieros de ArcJet Systems.\r\n\r\n"
            "[Nota de Clara]: «El Pentágono intentó censurar este número porque describía demasiado "
            "bien las prestaciones reales de nuestro prototipo. Recuerda al 'Emperador Quásar' y al "
            "'Escudo de Inmunidad Cósmica total contra la radiación' ante la consola del Coronel.»"
        ),
    ),
    (
        0x01001163,
        "BookOrbita7StudioDeed",
        "Título de Custodia: Estudio Subterráneo Órbita-7",
        (
            "ESCRITURA DE CUSTODIA PERPETUA — ESTUDIO SUBTERRÁNEO ÓRBITA-7\r\n"
            "Otorgada por: Dr. Arturo «Artie» Vance y Coronel Agallas «Cosmos»\r\n\r\n"
            "Por la presente se certifica que el portador ha superado con honores los cuatro grados "
            "del Protocolo del Verdadero Creyente, ha reunido los cuatro prototipos aeroespaciales "
            "del Proyecto Astro-Cosmos y ha honrado la última voluntad de Clara Sterling.\r\n\r\n"
            "Desde este día, la totalidad del Estudio Subterráneo Órbita-7 —incluyendo los Aposentos "
            "del Director con la Cama Espacial del Capitán Cosmos, los Baúles Estelares seguros, el "
            "Hangar Orbital y todos los talleres de ingeniería— queda cedida como su Refugio Permanente.\r\n\r\n"
            "«¡POR LA VERDAD, LAS ESTRELLAS Y EL MAÑANA!»"
        ),
    ),
]

QUEST_STAGES = [
    (
        15,
        0,
        "Mi Pip-Boy ha interceptado una señal de radio enviada por Arturo «Artie» Vance, antiguo ingeniero aeroespacial de Hubris Comics, desde el Estudio Subterráneo Órbita-7. Debería buscar la escotilla blindada en el callejón trasero de Hubris Comics y bajar a hablar con él.",
    ),
    (
        20,
        0,
        "Artie Vance me ha dado la bienvenida al Estudio Subterráneo Órbita-7. Para que el cascarrabias Coronel Agallas «Cosmos» desbloquee la cápsula del Traje de Vuelo Astro-Cosmos, debo investigar tres pistas repartidas entre la Rotonda del Planetario y la Sala de Guionistas (la Vitrina del Capitán Cosmos Nº 1, el Restirador de Clara Sterling y el Terminal de Producción de TV) y superar el Examen de Recluta en la consola central.",
    ),
    (
        30,
        0,
        "¡He superado el Examen de Recluta del Coronel Agallas! La barrera fotónica de la primera cápsula se ha desactivado. Ya puedo reclamar el Traje de Vuelo Astro-Cosmos.",
    ),
    (
        35,
        0,
        "Tengo en mi poder el Traje de Vuelo Astro-Cosmos. Debería equipármelo y hablar con Artie Vance sobre el siguiente prototipo del proyecto.",
    ),
    (
        40,
        0,
        "Para reactivar el pedestal de la Carabina de Rayos Astro-Cosmos, debo usar las capacidades de vuelo del traje para alcanzar tres tejados elevados de Boston —la azotea superior de Hubris Comics, la terraza media de Trinity Plaza y el tejado de la emisora WRVR—, recuperar las tres Bobinas Fotónicas y estudiar las pistas dejadas por Clara Sterling.",
    ),
    (
        50,
        0,
        "He reunido las tres Bobinas Fotónicas sobre los tejados de Boston junto con la primera holocinta de Clara y los expedientes de Los Imparables. Es hora de regresar a Estudio Órbita-7 y superar el Examen de Patrulla Aérea del Coronel Agallas.",
    ),
    (
        60,
        0,
        "¡Segundo examen superado! El Coronel Agallas ha bajado la barrera del Laboratorio Fotónico. Puedo recoger la Carabina de Rayos Astro-Cosmos de su pedestal.",
    ),
    (
        65,
        0,
        "Ya empuño la Carabina de Rayos Astro-Cosmos con mira telescópica de 6 aumentos sincronizada para disparo en vuelo. Hablaré con Artie Vance para preparar la Operación Titán Estelar.",
    ),
    (
        70,
        0,
        "Artie necesita el Núcleo Sincrotrón custodiado en la cubierta superior exterior de ArcJet Systems para abrir el Hangar Orbital Norte. Debo volar hasta el tejado de ArcJet, neutralizar los robots centinelas desde el aire con mi Carabina Astro-Cosmos y recuperar el núcleo y las pistas de Clara.",
    ),
    (
        80,
        0,
        "He recuperado el Núcleo Sincrotrón, la segunda holocinta de Clara Sterling y el borrador censurado del Especial Nº 50 del Capitán Cosmos en la cubierta de ArcJet Systems. Regresaré a Órbita-7 para superar el Examen de Piloto Orbital.",
    ),
    (
        100,
        0,
        "¡Las compuertas energéticas del Hangar Orbital Norte están abiertas! La Servoarmadura Astro-Cosmos completa me aguarda en su pórtico orbital.",
    ),
    (
        110,
        0,
        "He reclamado la imponente Servoarmadura Astro-Cosmos con propulsores orbitales integrados. Hablaré con Artie Vance sobre el misterio final de Clara Sterling y el Relicario Solar.",
    ),
    (
        120,
        0,
        "Artie ha abierto la Sala de Proyección del Director en el ala sureste del estudio. Debo memorizar el Juramento Supremo inscrito en su Gran Mural y después volar con la Servoarmadura Astro-Cosmos hasta el ático satelital de Fort Hagen para recuperar la Tarjeta Estelar Maestra y la última transmisión de Clara Sterling.",
    ),
    (
        140,
        0,
        "Tengo la Tarjeta Estelar Maestra y he escuchado la emotiva última holocinta grabada por Clara Sterling el 23 de octubre de 2077. Volveré al Estudio Órbita-7 para afrontar el Examen Maestro «Capitán del Cosmos» ante el Coronel Agallas.",
    ),
    (
        160,
        0,
        "¡El Coronel Agallas me ha otorgado el rango de Capitán del Cosmos y ha desbloqueado el Relicario Solar del Hangar Norte! Ya puedo reclamar el Cañón Orbital Gauss Astro-Cosmos.",
    ),
    (
        165,
        0,
        "El Cañón Orbital Gauss Astro-Cosmos está en mis manos. Hablaré con Artie Vance para celebrar que el legado de Clara Sterling está completo.",
    ),
    (
        200,
        1,
        "He reunido los cuatro prototipos del Proyecto Astro-Cosmos y honrado la memoria de Clara Sterling. Artie Vance y el Coronel Agallas me han entregado la custodia permanente del Estudio Subterráneo Órbita-7 como mi nuevo hogar y base de operaciones en el corazón de Boston.",
    ),
]

QUEST_OBJECTIVES = [
    (15, "Investiga la escotilla de Órbita-7 en el callejón trasero de Hubris Comics y habla con Artie Vance", 0),
    (20, "Revisa las 3 pistas del estudio y supera el Examen de Recluta en la consola central", 3),
    (30, "Reclama el Traje de Vuelo Astro-Cosmos en su cápsula de estasis", 4),
    (35, "Equipa el Traje Astro-Cosmos y habla con Artie Vance", 0),
    (41, "Vuela a la azotea superior de Hubris Comics y recupera la Bobina Fotónica #1", 5),
    (42, "Vuela a la terraza elevada de Trinity Plaza y recupera la Bobina Fotónica #2", 6),
    (43, "Vuela al tejado de la emisora WRVR y recupera la Bobina Fotónica #3", 7),
    (50, "Lee las pistas recuperadas y aprueba el Examen de Patrulla Aérea en Órbita-7", 3),
    (60, "Reclama la Carabina de Rayos Astro-Cosmos en el Laboratorio Fotónico", 8),
    (65, "Habla con Artie Vance para iniciar la Operación Titán Estelar", 0),
    (70, "Vuela a la cubierta alta de ArcJet Systems y recupera el Núcleo Sincrotrón", 9),
    (80, "Revisa las pistas de ArcJet y aprueba el Examen de Piloto Orbital en Órbita-7", 3),
    (100, "Entra en el Hangar Orbital Norte y reclama la Servoarmadura Astro-Cosmos", 10),
    (110, "Habla con Artie Vance sobre el destino final de Clara Sterling", 0),
    (121, "Inspecciona el Gran Mural del Juramento Estelar en la Sala del Director", 11),
    (122, "Vuela al tejado satelital de Fort Hagen y recupera la Tarjeta Estelar Maestra", 12),
    (140, "Escucha la Holocinta #3 de Clara y supera el Examen Maestro en Órbita-7", 3),
    (160, "Reclama el Cañón Orbital Gauss Astro-Cosmos en el Relicario Solar", 13),
    (165, "Habla con Artie Vance para recibir las llaves permanentes de Estudio Órbita-7", 0),
]

# ==============================================================================
# 7. LOCUCIONES CHUSQUERAS Y EFECTOS DE SONIDO DE EXÁMENES (UI / MENU-SAFE)
# ==============================================================================
EXAM_AUDIO_VOICES = [
    # 12 Preguntas locutadas (SNDR 0x01001801..0x0100180C -> SOUN 0x01001901..0x0100190C)
    {
        "name": "orbita7_exam_q01",
        "sndr_fid": 0x01001801,
        "soun_fid": 0x01001901,
        "sndr_edid": "SNDROrbita7ExamQ01",
        "soun_edid": "SOUNOrbita7ExamQ01",
        "tts": "¡Firme ante la consola, recluta patoso! Primera pregunta del Examen de Recluta: ¿cómo se llama el heroico copiloto simio del Capitán Cosmos y en qué cráter lunar se oculta su base secreta?",
    },
    {
        "name": "orbita7_exam_q02",
        "sndr_fid": 0x01001802,
        "soun_fid": 0x01001902,
        "sndr_edid": "SNDROrbita7ExamQ02",
        "soun_edid": "SOUNOrbita7ExamQ02",
        "tts": "¡Segunda pregunta, bisoño! Según el restirador oficial de Clara Sterling, ¿cuál es la tríada exacta de colores reglamentarios del uniforme Astro-Cosmos?",
    },
    {
        "name": "orbita7_exam_q03",
        "sndr_fid": 0x01001803,
        "soun_fid": 0x01001903,
        "sndr_edid": "SNDROrbita7ExamQ03",
        "soun_edid": "SOUNOrbita7ExamQ03",
        "tts": "¡Tercera y última pregunta para el traje, quinto! Según el Terminal de Producción de televisión, ¿qué fecha y canal estaban fijados para el gran estreno del Capitán Cosmos?",
    },
    {
        "name": "orbita7_exam_q04",
        "sndr_fid": 0x01001804,
        "soun_fid": 0x01001904,
        "sndr_edid": "SNDROrbita7ExamQ04",
        "soun_edid": "SOUNOrbita7ExamQ04",
        "tts": "¡Atención en el barracón, cadete volador! Primera pregunta de Patrulla Aérea: junto a Silver Shroud, Grognak, Manta Man y la Señora del Misterio, ¿quién completa el quinteto fundador de Los Imparables?",
    },
    {
        "name": "orbita7_exam_q05",
        "sndr_fid": 0x01001805,
        "soun_fid": 0x01001905,
        "sndr_edid": "SNDROrbita7ExamQ05",
        "soun_edid": "SOUNOrbita7ExamQ05",
        "tts": "¡Segunda pregunta de patrulla, pistolo! Según el Expediente Editorial de Trinity Plaza, ¿quién es el archienemigo jurado de Grognak el Bárbaro?",
    },
    {
        "name": "orbita7_exam_q06",
        "sndr_fid": 0x01001806,
        "soun_fid": 0x01001906,
        "sndr_edid": "SNDROrbita7ExamQ06",
        "soun_edid": "SOUNOrbita7ExamQ06",
        "tts": "¡Tercera pregunta para desbloquear la Carabina de Rayos! Según el guion radiofónico de la emisora \"uve doble erre uve erre\", ¿cuál es la Máxima de Oro del Código de Los Imparables?",
    },
    {
        "name": "orbita7_exam_q07",
        "sndr_fid": 0x01001807,
        "soun_fid": 0x01001907,
        "sndr_edid": "SNDROrbita7ExamQ07",
        "soun_edid": "SOUNOrbita7ExamQ07",
        "tts": "¡Cuadrarse ahora mismo, aspirante a Titán Estelar! Primera pregunta orbital: ¿qué corporación aeroespacial de Boston construyó en secreto las toberas gemelas de la Servoarmadura Astro-Cosmos?",
    },
    {
        "name": "orbita7_exam_q08",
        "sndr_fid": 0x01001808,
        "soun_fid": 0x01001908,
        "sndr_edid": "SNDROrbita7ExamQ08",
        "soun_edid": "SOUNOrbita7ExamQ08",
        "tts": "¡Segunda pregunta orbital, recluta! En el borrador censurado del Especial Número Cincuenta del Capitán Cosmos, ¿qué tirano galáctico intenta incendiar la Tierra con tormentas radiactivas?",
    },
    {
        "name": "orbita7_exam_q09",
        "sndr_fid": 0x01001809,
        "soun_fid": 0x01001909,
        "sndr_edid": "SNDROrbita7ExamQ09",
        "soun_edid": "SOUNOrbita7ExamQ09",
        "tts": "¡Tercera pregunta para abrir el Hangar de la Servoarmadura! Además del vuelo sostenido, ¿qué defensa legendaria incorpora el Torso Astro-Cosmos tanto en el cómic como en el prototipo real?",
    },
    {
        "name": "orbita7_exam_q10",
        "sndr_fid": 0x0100180A,
        "soun_fid": 0x0100190A,
        "sndr_edid": "SNDROrbita7ExamQ10",
        "soun_edid": "SOUNOrbita7ExamQ10",
        "tts": "¡Silencio en toda la compañía! Primera pregunta del Examen Maestro: ¿cuál es el Juramento Supremo inscrito en el Gran Mural de la Sala del Director?",
    },
    {
        "name": "orbita7_exam_q11",
        "sndr_fid": 0x0100180B,
        "soun_fid": 0x0100190B,
        "sndr_edid": "SNDROrbita7ExamQ11",
        "soun_edid": "SOUNOrbita7ExamQ11",
        "tts": "¡Segunda pregunta suprema, soldado! Según la última transmisión de Clara Sterling desde Fort Hagen, ¿qué calibre acelera el Cañón Orbital Gauss Astro-Cosmos?",
    },
    {
        "name": "orbita7_exam_q12",
        "sndr_fid": 0x0100180C,
        "soun_fid": 0x0100190C,
        "sndr_edid": "SNDROrbita7ExamQ12",
        "soun_edid": "SOUNOrbita7ExamQ12",
        "tts": "¡Última pregunta para recibir el rango de Capitán del Cosmos! Mientras caían las bombas aquel veintitrés de octubre de dos mil setenta y siete, ¿cuál fue el último deseo de Clara Sterling al salvar Órbita Siete?",
    },
    # 6 Frases chusqueras de acierto individual con sarcasmo e ironía (SNDR 0x01001811..0x01001816 -> SOUN 0x01001911..0x01001916)
    {
        "name": "orbita7_exam_hit01",
        "sndr_fid": 0x01001811,
        "soun_fid": 0x01001911,
        "sndr_edid": "SNDROrbita7ExamHit01",
        "soun_edid": "SOUNOrbita7ExamHit01",
        "tts": "¡Vaya, vaya! ¡Has acertado sin mover los labios al leer! No me digas que ese trozo de chatarra que llamas cerebro por fin ha hecho chispa.",
    },
    {
        "name": "orbita7_exam_hit02",
        "sndr_fid": 0x01001812,
        "soun_fid": 0x01001912,
        "sndr_edid": "SNDROrbita7ExamHit02",
        "soun_edid": "SOUNOrbita7ExamHit02",
        "tts": "¡Correcto! Increíble, recluta: incluso un reloj atómico roto da la hora exacta antes de estallar. No te acostumbres a los milagros.",
    },
    {
        "name": "orbita7_exam_hit03",
        "sndr_fid": 0x01001813,
        "soun_fid": 0x01001913,
        "sndr_edid": "SNDROrbita7ExamHit03",
        "soun_edid": "SOUNOrbita7ExamHit03",
        "tts": "¡Mira por dónde, diste en el clavo! ¿Ha sido pura memoria privilegiada o aporreaste la consola con la frente y sonó la flauta?",
    },
    {
        "name": "orbita7_exam_hit04",
        "sndr_fid": 0x01001814,
        "soun_fid": 0x01001914,
        "sndr_edid": "SNDROrbita7ExamHit04",
        "soun_edid": "SOUNOrbita7ExamHit04",
        "tts": "¡Afirmativo! Anoten la fecha en los archivos del Senado: un habitante del yermo acaba de demostrar comprensión lectora elemental. Casi me haces llorar aceite.",
    },
    {
        "name": "orbita7_exam_hit05",
        "sndr_fid": 0x01001815,
        "soun_fid": 0x01001915,
        "sndr_edid": "SNDROrbita7ExamHit05",
        "soun_edid": "SOUNOrbita7ExamHit05",
        "tts": "¡Respuesta válida! Tranquilo, genio, no saques pecho todavía, que hasta un mutascorpio ciego encuentra una chapa si tropieza lo suficiente.",
    },
    {
        "name": "orbita7_exam_hit06",
        "sndr_fid": 0x01001816,
        "soun_fid": 0x01001916,
        "sndr_edid": "SNDROrbita7ExamHit06",
        "soun_edid": "SOUNOrbita7ExamHit06",
        "tts": "¡Bingo, lumbreras! Alguien debe haber estado estudiando las vitrinas en vez de buscar tapones en la basura. Veamos cuánto te dura la racha de suerte.",
    },
    {
        "name": "orbita7_exam_hit07",
        "sndr_fid": 0x01001817,
        "soun_fid": 0x01001917,
        "sndr_edid": "SNDROrbita7ExamHit07",
        "soun_edid": "SOUNOrbita7ExamHit07",
        "tts": "¡Diste en el blanco, recluta! En Campamento McClintock he visto mutarachas reventar una diana con más convicción que tú, pero el punto sube al marcador.",
    },
    {
        "name": "orbita7_exam_hit08",
        "sndr_fid": 0x01001818,
        "soun_fid": 0x01001918,
        "sndr_edid": "SNDROrbita7ExamHit08",
        "soun_edid": "SOUNOrbita7ExamHit08",
        "tts": "¡Acierto reglamentario! No pidas una medalla todavía, guaperas; hasta un brahmán de dos cabezas acierta cuál es el cubo del pienso cuando tiene hambre.",
    },
    {
        "name": "orbita7_exam_hit09",
        "sndr_fid": 0x01001819,
        "soun_fid": 0x01001919,
        "sndr_edid": "SNDROrbita7ExamHit09",
        "soun_edid": "SOUNOrbita7ExamHit09",
        "tts": "¡Punto para el aspirante! Quién sabe, lo mismo dentro de dos o tres siglos llegas a cabo de letrinas orbitales si sigues leyendo antes de apretar botones.",
    },
    {
        "name": "orbita7_exam_hit10",
        "sndr_fid": 0x0100181A,
        "soun_fid": 0x0100191A,
        "sndr_edid": "SNDROrbita7ExamHit10",
        "soun_edid": "SOUNOrbita7ExamHit10",
        "tts": "¡Exacto! Anoten este evento sísmico en el diario de bitácora: la neurona solitaria de este individuo ha encontrado a una compañera.",
    },
    {
        "name": "orbita7_exam_hit11",
        "sndr_fid": 0x0100181B,
        "soun_fid": 0x0100191B,
        "sndr_edid": "SNDROrbita7ExamHit11",
        "soun_edid": "SOUNOrbita7ExamHit11",
        "tts": "¡Bien visto, soldado de cartón piedra! Casi pareces uno de aquellos muchachos de West Virginia antes de que tropezaran todos con la pista de obstáculos.",
    },
    {
        "name": "orbita7_exam_hit12",
        "sndr_fid": 0x0100181C,
        "soun_fid": 0x0100191C,
        "sndr_edid": "SNDROrbita7ExamHit12",
        "soun_edid": "SOUNOrbita7ExamHit12",
        "tts": "¡Justo en la diana! Qué milagro de la evolución americana: un superviviente que realmente se molestó en leer las letras pequeñas del expediente.",
    },
    # 16 Frases mordaces de fallo y reinicio estilo Camp McClintock (SNDR 0x01001821..0x01001830 -> SOUN 0x01001921..0x01001930)
    {
        "name": "orbita7_exam_fail01",
        "sndr_fid": 0x01001821,
        "soun_fid": 0x01001921,
        "sndr_edid": "SNDROrbita7ExamFail01",
        "soun_edid": "SOUNOrbita7ExamFail01",
        "tts": "¡Fallo monumental! Qué maravilla de razonamiento: con esa puntería intelectual no acertarías ni disparando dentro de un cubo de agua. Examen reiniciado, genio.",
    },
    {
        "name": "orbita7_exam_fail02",
        "sndr_fid": 0x01001822,
        "soun_fid": 0x01001922,
        "sndr_edid": "SNDROrbita7ExamFail02",
        "soun_edid": "SOUNOrbita7ExamFail02",
        "tts": "¡Negativo absoluto! He conocido tostadoras quemadas antes de la Gran Guerra con más retentiva que tú. Vuelve a las vitrinas a leer despacito, que es gratis.",
    },
    {
        "name": "orbita7_exam_fail03",
        "sndr_fid": 0x01001823,
        "soun_fid": 0x01001923,
        "sndr_edid": "SNDROrbita7ExamFail03",
        "soun_edid": "SOUNOrbita7ExamFail03",
        "tts": "¡Equivocado! ¿Seguro que sabes leer o solo pulsas botones brillantes porque te gustan los colorines de la pantalla? Todo anulado, vuelta a empezar.",
    },
    {
        "name": "orbita7_exam_fail04",
        "sndr_fid": 0x01001824,
        "soun_fid": 0x01001924,
        "sndr_edid": "SNDROrbita7ExamFail04",
        "soun_edid": "SOUNOrbita7ExamFail04",
        "tts": "¡Cero patatero! Fascinante desastre: acabas de reescribir la historia de Hubris Comics a base de pura ignorancia radiactiva. Repite desde la casilla uno, campeón.",
    },
    {
        "name": "orbita7_exam_fail05",
        "sndr_fid": 0x01001825,
        "soun_fid": 0x01001925,
        "sndr_edid": "SNDROrbita7ExamFail05",
        "soun_edid": "SOUNOrbita7ExamFail05",
        "tts": "¡Mal, rotundamente mal! Si la estupidez generara electricidad, tú solo iluminarías toda Boston durante un siglo. Aléjate de los prototipos y empieza otra vez.",
    },
    {
        "name": "orbita7_exam_fail06",
        "sndr_fid": 0x01001826,
        "soun_fid": 0x01001926,
        "sndr_edid": "SNDROrbita7ExamFail06",
        "soun_edid": "SOUNOrbita7ExamFail06",
        "tts": "¡Descalabro histórico! Qué valor el tuyo presentarse a pilotar tecnología orbital sin recordar tres líneas de un dossier. Vuelve al principio y repasa la cartilla.",
    },
    {
        "name": "orbita7_exam_fail07",
        "sndr_fid": 0x01001827,
        "soun_fid": 0x01001927,
        "sndr_edid": "SNDROrbita7ExamFail07",
        "soun_edid": "SOUNOrbita7ExamFail07",
        "tts": "¡PERO QUÉ VERGÜENZA DE RECLUTA! En Campamento McClintock un pelotón de yao guai mancos superaría mi pista antes que tú tres preguntas de guardería! ¡A LA COLA OTRA VEZ!",
    },
    {
        "name": "orbita7_exam_fail08",
        "sndr_fid": 0x01001828,
        "soun_fid": 0x01001928,
        "sndr_edid": "SNDROrbita7ExamFail08",
        "soun_edid": "SOUNOrbita7ExamFail08",
        "tts": "¡AGÁCHATE Y DAME CINCUENTA FLEXIONES EN EL SÓTANO, PELAGATO! ¡Acabas de confundir un cómic de Hubris con la lista de la compra! ¡Examen reiniciado!",
    },
    {
        "name": "orbita7_exam_fail09",
        "sndr_fid": 0x01001829,
        "soun_fid": 0x01001929,
        "sndr_edid": "SNDROrbita7ExamFail09",
        "soun_edid": "SOUNOrbita7ExamFail09",
        "tts": "¡BIENVENIDO AL SERVICIO DE LIMPIEZA DE LETRINAS DE ÓRBITA SIETE! Con ese nivel de retentiva no te dejo ni limpiar el parabrisas de un eyector roto. ¡Empieza desde cero!",
    },
    {
        "name": "orbita7_exam_fail10",
        "sndr_fid": 0x0100182A,
        "soun_fid": 0x0100192A,
        "sndr_edid": "SNDROrbita7ExamFail10",
        "soun_edid": "SOUNOrbita7ExamFail10",
        "tts": "¡ALTO EL FUEGO, DESASTRE HUMANO! ¡Tu abuela en bata con un palo de escoba dispararía con más criterio que tu cabeza hueca! ¡Rebobina hasta la casilla de salida!",
    },
    {
        "name": "orbita7_exam_fail11",
        "sndr_fid": 0x0100182B,
        "soun_fid": 0x0100192B,
        "sndr_edid": "SNDROrbita7ExamFail11",
        "soun_edid": "SOUNOrbita7ExamFail11",
        "tts": "¡ESTO ES UN ATENTADO COMUNISTA CONTRA LA LECTURA COMPRENSIVA! ¿Has venido a salvar la memoria de Hubris o a pulsar teclas a boleo como un topo radiactivo? ¡FUERA DE AQUÍ!",
    },
    {
        "name": "orbita7_exam_fail12",
        "sndr_fid": 0x0100182C,
        "soun_fid": 0x0100192C,
        "sndr_edid": "SNDROrbita7ExamFail12",
        "soun_edid": "SOUNOrbita7ExamFail12",
        "tts": "¡MENOS MAL QUE NO TE EXAMINAMOS CON MUNICIÓN REAL EN EL CAMPO DE TIRO DE WEST VIRGINIA! A estas alturas habrías volado la cantina, los muñecos de prácticas y hasta la bandera. ¡OTRA VEZ!",
    },
    {
        "name": "orbita7_exam_fail13",
        "sndr_fid": 0x0100182D,
        "soun_fid": 0x0100192D,
        "sndr_edid": "SNDROrbita7ExamFail13",
        "soun_edid": "SOUNOrbita7ExamFail13",
        "tts": "¡SUSPENSO DE CATEGORÍA ESPACIAL! Si fuera un sargento de carne y hueso me daría un infarto, pero como soy acero patriótico me limito a reiniciar el examen y reírme en tus narices!",
    },
    {
        "name": "orbita7_exam_fail14",
        "sndr_fid": 0x0100182E,
        "soun_fid": 0x0100192E,
        "sndr_edid": "SNDROrbita7ExamFail14",
        "soun_edid": "SOUNOrbita7ExamFail14",
        "tts": "¡DIOS SALVE A AMÉRICA PORQUE CON TU MEMORIA NOS INVADEN HASTA LAS SANGUIJUELAS! Toma aire, ve a repasar los dossieres letra por letra y vuelve cuando tengas pulso cerebral!",
    },
    {
        "name": "orbita7_exam_fail15",
        "sndr_fid": 0x0100182F,
        "soun_fid": 0x0100192F,
        "sndr_edid": "SNDROrbita7ExamFail15",
        "soun_edid": "SOUNOrbita7ExamFail15",
        "tts": "¡PATÉTICO ES POCO, ASPIRANTE A CHATARRA! ¡Te he dado las respuestas casi masticadas sobre una mesa y aun así logras atragantarte con la tercera opción! ¡Vuelta al punto de partida!",
    },
    {
        "name": "orbita7_exam_fail16",
        "sndr_fid": 0x01001830,
        "soun_fid": 0x01001930,
        "sndr_edid": "SNDROrbita7ExamFail16",
        "soun_edid": "SOUNOrbita7ExamFail16",
        "tts": "¡ROMPAN FILAS, PAYASO CÓSMICO! Mañana me lustras los propulsores con un cepillo de dientes antes de volver a tocar mi terminal. ¡A repasar las pistas ahora mismo!",
    },
    # 12 Frases irónicas de victoria plena 3/3 (3 variantes por examen: SNDR 0x01001831..34 + 0x01001851..58)
    {
        "name": "orbita7_exam_win01",
        "sndr_fid": 0x01001831,
        "soun_fid": 0x01001931,
        "sndr_edid": "SNDROrbita7ExamWin01",
        "soun_edid": "SOUNOrbita7ExamWin01",
        "tts": "¡Tres de tres! ¡Paren las rotativas! Resulta que bajo ese casco polvoriento había algo más que serrín. Barrera uno desactivada: ve a ponerte tu flamante Traje Astro-Cosmos, estrella de baratillo.",
    },
    {
        "name": "orbita7_exam_win02",
        "sndr_fid": 0x01001832,
        "soun_fid": 0x01001932,
        "sndr_edid": "SNDROrbita7ExamWin02",
        "soun_edid": "SOUNOrbita7ExamWin02",
        "tts": "¡Pleno milagroso! Quién iba a imaginar que sabías hilar tres respuestas seguidas sin perder el aliento. Compuerta del laboratorio abierta: recoge la Carabina de Rayos y procura no apuntarte a los pies.",
    },
    {
        "name": "orbita7_exam_win03",
        "sndr_fid": 0x01001833,
        "soun_fid": 0x01001933,
        "sndr_edid": "SNDROrbita7ExamWin03",
        "soun_edid": "SOUNOrbita7ExamWin03",
        "tts": "¡Tres aciertos de tres! Me dejas con los circuitos helados, cadete. Has demostrado ser ligeramente menos torpe que un brahmán con botas. Hangar Norte desbloqueado: disfruta de la Servoarmadura Astro-Cosmos.",
    },
    {
        "name": "orbita7_exam_win04",
        "sndr_fid": 0x01001834,
        "soun_fid": 0x01001934,
        "sndr_edid": "SNDROrbita7ExamWin04",
        "soun_edid": "SOUNOrbita7ExamWin04",
        "tts": "¡Tres de tres en el Examen Supremo! Increíble pero cierto: acabo de ascender a un buscavidas del yermo a Capitán del Cosmos. El Relicario Solar y el Cañón Orbital son tuyos... intenta no volar Boston por los aires.",
    },
    {
        "name": "orbita7_exam_win05",
        "sndr_fid": 0x01001851,
        "soun_fid": 0x01001951,
        "sndr_edid": "SNDROrbita7ExamWin05",
        "soun_edid": "SOUNOrbita7ExamWin05",
        "tts": "¡PRUEBA DE RECLUTA SUPERADA POR UN PELO! ¡No te pongas medallas todavía, pajarraco: con ese traje azul brillante pareces un globo de feria listo para que te disparen desde tierra!",
    },
    {
        "name": "orbita7_exam_win06",
        "sndr_fid": 0x01001852,
        "soun_fid": 0x01001952,
        "sndr_edid": "SNDROrbita7ExamWin06",
        "soun_edid": "SOUNOrbita7ExamWin06",
        "tts": "¡APROBADO MILAGROSO EN EL EXAMEN UNO! En mis tiempos de instrucción te habrían puesto a correr con una lavadora a la espalda, ¡pero el traje de vuelo es tuyo! ¡No estrelles la cabeza contra el techo!",
    },
    {
        "name": "orbita7_exam_win07",
        "sndr_fid": 0x01001853,
        "soun_fid": 0x01001953,
        "sndr_edid": "SNDROrbita7ExamWin07",
        "soun_edid": "SOUNOrbita7ExamWin07",
        "tts": "¡SEGUNDO EXAMEN DESPACHADO, PILOTO DE AGUA DULCE! ¡Tienes el pedestal fotónico abierto! Ya puedes coger la Carabina de Rayos y probar si desde las nubes aciertas a algo más grande que un granero!",
    },
    {
        "name": "orbita7_exam_win08",
        "sndr_fid": 0x01001854,
        "soun_fid": 0x01001954,
        "sndr_edid": "SNDROrbita7ExamWin08",
        "soun_edid": "SOUNOrbita7ExamWin08",
        "tts": "¡TRES DE TRES EN PATRULLA AÉREA! Quién iba a pensar que además de saltar por los tejados como un gato escaldado sabías recordar el código de Los Imparables. ¡Carabina desbloqueada, recluta!",
    },
    {
        "name": "orbita7_exam_win09",
        "sndr_fid": 0x01001855,
        "soun_fid": 0x01001955,
        "sndr_edid": "SNDROrbita7ExamWin09",
        "soun_edid": "SOUNOrbita7ExamWin09",
        "tts": "¡TERCER EXAMEN SUPERADO CON HONORES... O CON SUERTE DESCOMUNAL! Ya puedes arrastrar ese trasero dentro de la Servoarmadura Orbital del Hangar Norte. ¡Procura no aplastar a Artie al salir!",
    },
    {
        "name": "orbita7_exam_win10",
        "sndr_fid": 0x01001856,
        "soun_fid": 0x01001956,
        "sndr_edid": "SNDROrbita7ExamWin10",
        "soun_edid": "SOUNOrbita7ExamWin10",
        "tts": "¡SOLVENCIA TOTAL EN INGENIERÍA PESADA! ¡Maldita sea, empiezas a recordarme a los mejores alumnos de Campamento McClintock... los únicos que no se cayeron en el barro al tercer segundo! ¡Servoarmadura liberada!",
    },
    {
        "name": "orbita7_exam_win11",
        "sndr_fid": 0x01001857,
        "soun_fid": 0x01001957,
        "sndr_edid": "SNDROrbita7ExamWin11",
        "soun_edid": "SOUNOrbita7ExamWin11",
        "tts": "¡FIRMES TODOS! ¡Acabamos de coronar a un nuevo Capitán del Cosmos sin que explotase ni una válvula del terminal! Toma el Cañón Orbital Gauss del Relicario Solar y haz que esos comunistas lunares lloren plomo!",
    },
    {
        "name": "orbita7_exam_win12",
        "sndr_fid": 0x01001858,
        "soun_fid": 0x01001958,
        "sndr_edid": "SNDROrbita7ExamWin12",
        "soun_edid": "SOUNOrbita7ExamWin12",
        "tts": "¡MATRÍCULA DE HONOR EN EL EXAMEN SUPREMO, SEÑOR! ¡Ni el propio general de Campamento McClintock habría soportado tanto sarcasmo sin abandonar el podio! ¡El Cañón Orbital Gauss y Órbita Siete son suyos, Capitán!",
    },
    # 4 Frases irónicas al retirarse a revisar pistas (SNDR 0x01001835 + 0x01001861..63)
    {
        "name": "orbita7_exam_retreat",
        "sndr_fid": 0x01001835,
        "soun_fid": 0x01001935,
        "sndr_edid": "SNDROrbita7ExamRetreat",
        "soun_edid": "SOUNOrbita7ExamRetreat",
        "tts": "¡Ajá, retirada estratégica! Una decisión sorprendentemente sensata: mejor consultar las pistas del estudio ahora que seguir haciendo el ridículo en horario estelar.",
    },
    {
        "name": "orbita7_exam_retreat02",
        "sndr_fid": 0x01001861,
        "soun_fid": 0x01001961,
        "sndr_edid": "SNDROrbita7ExamRetreat02",
        "soun_edid": "SOUNOrbita7ExamRetreat02",
        "tts": "¡RETIRADA TÁCTICA ANTES DE QUEMAR EL FUSIBLE! Buena jugada, recluta: corre a mirar las vitrinas antes de que me quede sin insultos en el diccionario reglamentario.",
    },
    {
        "name": "orbita7_exam_retreat03",
        "sndr_fid": 0x01001862,
        "soun_fid": 0x01001962,
        "sndr_edid": "SNDROrbita7ExamRetreat03",
        "soun_edid": "SOUNOrbita7ExamRetreat03",
        "tts": "¿YA TIRANDO LA TOALLA EN LA PRIMERA RONDA? En Campamento McClintock al menos corrías hasta desplomarte, pero supongo que repasar los expedientes te ahorrará otro bochorno.",
    },
    {
        "name": "orbita7_exam_retreat04",
        "sndr_fid": 0x01001863,
        "soun_fid": 0x01001963,
        "sndr_edid": "SNDROrbita7ExamRetreat04",
        "soun_edid": "SOUNOrbita7ExamRetreat04",
        "tts": "¡RECONOCER LA IGNORANCIA PROPIA ES EL PRIMER PASO DEL SOLDADO! Lee los apuntes de Clara con los dos ojos abiertos y vuelve aquí a dar la talla.",
    },
]

EXAM_SFX_DEFS = [
    {
        "name": "sfx_orbita7_boo_01",
        "sndr_fid": 0x01001841,
        "soun_fid": 0x01001941,
        "sndr_edid": "SNDROrbita7Boo01",
        "soun_edid": "SOUNOrbita7Boo01",
        "duration": 4.5,
        "prompt": "Retro 1950s television game show studio audience loudly booing, jeering, groaning in disappointment with a comical low brass fail buzzer, reverberant broadcast hall",
    },
    {
        "name": "sfx_orbita7_boo_02",
        "sndr_fid": 0x01001842,
        "soun_fid": 0x01001942,
        "sndr_edid": "SNDROrbita7Boo02",
        "soun_edid": "SOUNOrbita7Boo02",
        "duration": 4.5,
        "prompt": "Rowdy crowd of people booing loudly, shouting boo, whistling in disapproval and groaning after a wrong quiz answer in an underground auditorium",
    },
    {
        "name": "sfx_orbita7_applause_01",
        "sndr_fid": 0x01001843,
        "soun_fid": 0x01001943,
        "sndr_edid": "SNDROrbita7Applause01",
        "soun_edid": "SOUNOrbita7Applause01",
        "duration": 5.5,
        "prompt": "Enthusiastic 1950s television studio audience erupting into loud applause, clapping, cheering, whistling and shouting bravo in a warm broadcast auditorium",
    },
    {
        "name": "sfx_orbita7_applause_02",
        "sndr_fid": 0x01001844,
        "soun_fid": 0x01001944,
        "sndr_edid": "SNDROrbita7Applause02",
        "soun_edid": "SOUNOrbita7Applause02",
        "duration": 5.5,
        "prompt": "Triumphant game show grand prize celebration with loud crowd applause, standing ovation clapping and joyful cheers in a vintage theater hall",
    },
]

