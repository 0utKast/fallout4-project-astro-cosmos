#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hubris_orbita7_data_en.py
=========================
Complete English narrative data, voiced dialogues, shrill Camp-McClintock-style
Colonel Gutsy barks and exam tirades, Clara Sterling holotapes, terminals, dossiers,
and 4 exam suites for "The Hubris Legacy: Project Astro-Cosmos" (EN Edition).

Exact structural, FormID, PNAM-chain, flag, and condition parity with `hubris_orbita7_data_es.py`.
"""

# ElevenLabs Voice IDs (eleven_multilingual_v2, language_code="en"):
CORONEL_VTYP = "NPCMCoronelAgallasCosmos"
ARTIE_VTYP = "NPCMArtieVance"
CLARA_VTYP = "NPCFClaraSterlingHolo"
PLAYER_MALE_VTYP = "PlayerVoiceMale01"
PLAYER_FEMALE_VTYP = "PlayerVoiceFemale01"

CORONEL_VOICE_ID = "SOYHLrjzK2X1ezoPC6cr"      # Harry - Fierce Warrior (shrill drill-sergeant Gutsy)
ARTIE_VOICE_ID = "N2lVS1w4EtoT3dr4eOWO"        # Callum - Husky Trickster (gravelly lucid pre-war ghoul)
CLARA_VOICE_ID = "XrExE9yKIg1WjnnlVkGX"        # Matilda - Pre-War Hubris Comics lead writer & producer
PLAYER_MALE_VOICE_ID = "nPczCjzI2devNBz1zQrb"  # Brian - Sole Survivor (Male)
PLAYER_FEMALE_VOICE_ID = "EXAVITQu4vr4xnSDxMaL"  # Sarah - Sole Survivor (Female)

# ==============================================================================
# 1. ARTHUR "ARTIE" VANCE GREETINGS (DIAL 0x01004001, GREE)
# ==============================================================================
ARTIE_GREETING_INFOS = [
    # Stage 15 -> Starts Scene 1 (Welcome to Orbit-7 & Mission 1)
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
                "Well butter my circuits—a human face that isn't shooting at me! Holster that gun, friend, you're in safe territory.",
                "Well butter my circuits, a human face that isn't shooting at me! Holster that gun, friend, you're in safe territory.",
            ),
            (
                "Welcome to Hubris Comics Underground Studio Orbit-7. I'm Arthur Vance... though down here everyone called me Artie.",
                "Welcome to Hubris Comics Underground Studio Orbit Seven. I'm Arthur Vance... though down here everyone called me Artie.",
            ),
        ],
    },
    # Stage 20 -> Mission 1 reminder (2 random variants)
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
                "Check the Captain Cosmos display in the Rotunda, plus Clara's drafting desk and terminal in the East Writers' Wing. Those three clues unlock the Suit.",
                "Check the Captain Cosmos display in the Rotunda, plus Clara's drafting desk and terminal in the East Writers' Wing. Those three clues unlock the Suit.",
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
                "Colonel Gutsy won't forgive a single comma, pal. Read all three clues between the Rotunda and Writers' Room before touching his exam console.",
                "Colonel Gutsy won't forgive a single comma, pal. Read all three clues between the Rotunda and Writers' Room before touching his exam console.",
            ),
        ],
    },
    # Stage 30 -> Exam 1 passed: claim Flight Suit (2 variants)
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
                "The stasis barrier just dropped! Step into the bay, grab your Astro-Cosmos Flight Suit, and take it for a spin.",
                "The stasis barrier just dropped! Step into the bay, grab your Astro-Cosmos Flight Suit, and take it for a spin.",
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
                "Smooth talking with the Colonel! Head over to the stasis pod right off the Rotunda and claim your Astro-Cosmos Flight Suit.",
                "Smooth talking with the Colonel! Head over to the stasis pod right off the Rotunda and claim your Astro-Cosmos Flight Suit.",
            ),
        ],
    },
    # Stage 35 -> Opens Scene 2 (Flight Suit claimed -> Mission 2 Rooftop Patrol)
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
                "Look at you! Two hundred and ten years waiting, and the Astro-Cosmos Flight Suit still gleams like it just left the workshop.",
                "Look at you! Two hundred and ten years waiting, and the Astro-Cosmos Flight Suit still gleams like it just left the workshop.",
            ),
            (
                "Come closer, pilot—now that you've got wings, it's time we woke up the Photonic Weapons Lab.",
                "Come closer, pilot—now that you've got wings, it's time we woke up the Photonic Weapons Lab.",
            ),
        ],
    },
    # Stage 40 (0 coils recovered) -> Mission 2 start (2 variants)
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
                "All three Photonic Coils are sitting atop Hubris Comics, Trinity Plaza, and WRVR. Fly up there, play Clara's tape, and read every dossier.",
                "All three Photonic Coils are sitting atop Hubris Comics, Trinity Plaza, and W. R. V. R. Fly up there, play Clara's tape, and read every dossier.",
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
                "My scanners still show zero Photonic Coils in your pack. Hit the skies over Hubris Comics, Trinity Plaza, and WRVR when you're ready.",
                "My scanners still show zero Photonic Coils in your pack. Hit the skies over Hubris Comics, Trinity Plaza, and W. R. V. R. when you're ready.",
            ),
        ],
    },
    # Stage 40 (1 coil recovered) -> Partial progress (2 variants)
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
                "My sensors already ping one Photonic Coil in your pack! Two more Boston rooftops to sweep before you face the Colonel.",
                "My sensors already ping one Photonic Coil in your pack! Two more Boston rooftops to sweep before you face the Colonel.",
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
                "One coil secured, pilot—nice flying. Two more rooftops left to gather all three components and Clara's dossiers.",
                "One coil secured, pilot—nice flying. Two more rooftops left to gather all three components and Clara's dossiers.",
            ),
        ],
    },
    # Stage 40 (2 coils recovered) -> Only one left (2 variants)
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
                "Two Photonic Coils humming in your pack! Just one last rooftop to conquer and don't forget the Unstoppables code.",
                "Two Photonic Coils humming in your pack! Just one last rooftop to conquer and don't forget the Unstoppables code.",
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
                "One final roof and the whole set is ours, partner. Grab that third coil up there and the Colonel's console awaits.",
                "One final roof and the whole set is ours, partner. Grab that third coil up there and the Colonel's console awaits.",
            ),
        ],
    },
    # Stage 50 -> All 3 Photonic Coils collected: Exam 2 (2 variants)
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
                "You brought back all three Photonic Coils! Review the clues you pulled from those roofs and tackle the second exam at the console.",
                "You brought back all three Photonic Coils! Review the clues you pulled from those roofs and tackle the second exam at the console.",
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
                "With all three coils in hand, your rooftop days are done. Step up to Colonel Gutsy for the Aerial Patrol Exam.",
                "With all three coils in hand, your rooftop days are done. Step up to Colonel Gutsy for the Aerial Patrol Exam.",
            ),
        ],
    },
    # Stage 60 -> Exam 2 passed: claim Carbine (2 variants)
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
                "The Photonic Lab is wide open! Claim your Astro-Cosmos Ray Carbine from the pedestal—it fires mid-flight in both your Suit and Power Armor.",
                "The Photonic Lab is wide open! Claim your Astro-Cosmos Ray Carbine from the pedestal—it fires mid-flight in both your Suit and Power Armor.",
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
                "Second test aced! Head into the Photonic Lab and pick up the Ray Carbine before we launch our next op.",
                "Second test aced! Head into the Photonic Lab and pick up the Ray Carbine before we launch our next op.",
            ),
        ],
    },
    # Stage 65 -> Opens Scene 3 (Carbine claimed -> Mission 3 Operation Star Titan at ArcJet)
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
                "Seeing that Astro-Cosmos Ray Carbine in your hands is music to my old irradiated eyes.",
                "Seeing that Astro-Cosmos Ray Carbine in your hands is music to my old irradiated eyes.",
            ),
            (
                "And you're gonna need its six-power recon scope mid-flight—our next stop is the upper roof deck of ArcJet Systems.",
                "And you're gonna need its six-power recon scope mid-flight—our next stop is the upper roof deck of ArcJet Systems.",
            ),
        ],
    },
    # Stage 70 -> Mission 3 active (2 variants)
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
                "Fly up to ArcJet Systems' highest deck, blast those sentinels out of the sky with your Carbine, and bring back the Synchrotron Core and Issue Fifty.",
                "Fly up to ArcJet Systems' highest deck, blast those sentinels out of the sky with your Carbine, and bring back the Synchrotron Core and Issue Fifty.",
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
                "The Synchrotron Core is still locked up on ArcJet Systems' top roof. Make sure you read the censored Captain Cosmos draft up there too.",
                "The Synchrotron Core is still locked up on ArcJet Systems' top roof. Make sure you read the censored Captain Cosmos draft up there too.",
            ),
        ],
    },
    # Stage 80 -> Synchrotron Core recovered: Exam 3 (2 variants)
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
                "I can hear that Synchrotron Core purring from here! You survived ArcJet—review the Issue Fifty notes and hit the Colonel's console.",
                "I can hear that Synchrotron Core purring from here! You survived ArcJet—review the Issue Fifty notes and hit the Colonel's console.",
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
                "Back from ArcJet in one piece with the Core in tow! Pass the Orbital Pilot Exam now and I'll unseal the North Hangar.",
                "Back from ArcJet in one piece with the Core in tow! Pass the Orbital Pilot Exam now and I'll unseal the North Hangar.",
            ),
        ],
    },
    # Stage 100 -> Exam 3 passed: claim Power Armor (2 variants)
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
                "Hear those bulkhead doors unlatch? The full Astro-Cosmos Power Armor is powered up and waiting in the North Orbital Hangar.",
                "Hear those bulkhead doors unlatch? The full Astro-Cosmos Power Armor is powered up and waiting in the North Orbital Hangar.",
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
                "Mission accomplished, pilot! Step into the North Orbital Hangar and climb inside the Astro-Cosmos Power Armor.",
                "Mission accomplished, pilot! Step into the North Orbital Hangar and climb inside the Astro-Cosmos Power Armor.",
            ),
        ],
    },
    # Stage 110 -> Opens Scene 4 (PA claimed -> Mission 4 Director's Room + Fort Hagen)
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
                "By Jangles' whiskers! Watching the Astro-Cosmos Power Armor stride beneath this dome makes two centuries of loneliness worth every minute.",
                "By Jangles' whiskers! Watching the Astro-Cosmos Power Armor stride beneath this dome makes two centuries of loneliness worth every minute.",
            ),
            (
                "Only one final mystery remains, my friend: Clara Sterling's final mission and the Solar Reliquary.",
                "Only one final mystery remains, my friend: Clara Sterling's final mission and the Solar Reliquary.",
            ),
        ],
    },
    # Stage 120 (Mural NOT yet inspected) -> Director's Room + Fort Hagen (2 variants)
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
                "I unlocked the Director's Suite south of the Writers' Wing—read the oath on the Grand Mural, then fly to Fort Hagen's dish roof for Clara's Master Card.",
                "I unlocked the Director's Suite south of the Writers' Wing—read the oath on the Grand Mural, then fly to Fort Hagen's dish roof for Clara's Master Card.",
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
                "Before launching toward Fort Hagen, duck into the Director's Room and read the Grand Star Guard Mural—you'll need that oath for the final test.",
                "Before launching toward Fort Hagen, duck into the Director's Room and read the Grand Star Guard Mural—you'll need that oath for the final test.",
            ),
        ],
    },
    # Stage 120 (Mural ALREADY inspected) -> Only Fort Hagen left (2 variants)
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
                "You've got the Star Guard Oath memorized from the Mural. Now fly out to Fort Hagen's satellite roof and recover Clara's Master Star Card.",
                "You've got the Star Guard Oath memorized from the Mural. Now fly out to Fort Hagen's satellite roof and recover Clara's Master Star Card.",
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
                "Good, the mural motto's locked in your head. Chart a course for Fort Hagen's roof whenever you're ready—Flight Suit or Power Armor, your call.",
                "Good, the mural motto's locked in your head. Chart a course for Fort Hagen's roof whenever you're ready—Flight Suit or Power Armor, your call.",
            ),
        ],
    },
    # Stage 140 -> Master Card recovered: Exam 4 (2 variants)
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
                "You've got Clara's Master Star Card! Take a quiet moment to listen to her final holotape, then report for Colonel Gutsy's Master Exam.",
                "You've got Clara's Master Star Card! Take a quiet moment to listen to her final holotape, then report for Colonel Gutsy's Master Exam.",
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
                "At last we know Clara Sterling's final sacrifice. Step up to the exam console and earn the rank of Captain of the Cosmos.",
                "At last we know Clara Sterling's final sacrifice. Step up to the exam console and earn the rank of Captain of the Cosmos.",
            ),
        ],
    },
    # Stage 160 -> Exam 4 passed: claim Orbital Gauss Cannon (2 variants)
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
                "The final barrier is down! The Solar Reliquary holds the Astro-Cosmos Orbital Gauss Cannon—tuned for airborne firing in Suit and Power Armor alike.",
                "The final barrier is down! The Solar Reliquary holds the Astro-Cosmos Orbital Gauss Cannon—tuned for airborne firing in Suit and Power Armor alike.",
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
                "A true Captain of the Cosmos! Lift that Orbital Gauss Cannon from the Solar Reliquary and talk to me so I can sign over the studio.",
                "A true Captain of the Cosmos! Lift that Orbital Gauss Cannon from the Solar Reliquary and talk to me so I can sign over the studio.",
            ),
        ],
    },
    # Stage 165 -> Opens Scene 5 (Epilogue: permanent ownership of Orbit-7)
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
                "You actually did it... The Flight Suit, the Carbine, the Orbital Power Armor, and the Gauss Cannon. Clara's whole dream lives on in your hands.",
                "You actually did it... The Flight Suit, the Carbine, the Orbital Power Armor, and the Gauss Cannon. Clara's whole dream lives on in your hands.",
            ),
        ],
    },
    # Stage 200+ -> Permanent resident ally greetings in Orbit-7 HQ (3 variants)
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
                "Welcome home, Captain of the Cosmos. Your workbenches, safe Star Chests, and Spacer Bed are ready—the Colonel and I will keep Orbit-7 safe.",
                "Welcome home, Captain of the Cosmos. Your workbenches, safe Star Chests, and Spacer Bed are ready—the Colonel and I will keep Orbit Seven safe.",
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
                "Great to have you back in Orbit-7, Captain! Anytime you miss Colonel Gutsy's drill-sergeant mouth, run any Free Drill on his terminal.",
                "Great to have you back in Orbit Seven, Captain! Anytime you miss Colonel Gutsy's drill-sergeant mouth, run any Free Drill on his terminal.",
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
                "All crafting benches are tuned up, partner. Remember both the Carbine and the Gauss Cannon are synced to swap seamlessly between Suit and Power Armor!",
                "All crafting benches are tuned up, partner. Remember both the Carbine and the Gauss Cannon are synced to swap seamlessly between Suit and Power Armor!",
            ),
        ],
    },
]

# ==============================================================================
# 2. COLONEL GUTSY "COSMOS" GREETINGS & BARKS (GREE 0x01004002 + CUST 0x01004003)
# ==============================================================================
CORONEL_GREETING_INFOS = [
    # Stage < 20
    {
        "info_fid": 0x01004020,
        "prev_fid": 0x00000000,
        "enam_flags": 0x02,
        "stage_conds": [(0x80, 20.0)],
        "responses": [
            (
                "HALT RIGHT THERE, EARTHWORM! Report to Chief Engineer Vance before you smear your filthy irradiated paws across my exam console!",
                "HALT RIGHT THERE, EARTHWORM! Report to Chief Engineer Vance before you smear your filthy irradiated paws across my exam console!",
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
                "DON'T YOU DARE TOUCH A SINGLE KEY YET, CIVILIAN! Go talk to Artie Vance unless you fancy doing five hundred push-ups in zero-G!",
                "DON'T YOU DARE TOUCH A SINGLE KEY YET, CIVILIAN! Go talk to Artie Vance unless you fancy doing five hundred push-ups in zero gravity!",
            ),
        ],
    },
    # Stage 20 -> Exam 1 pending
    {
        "info_fid": 0x01004021,
        "prev_fid": 0x01004801,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 20.0)],
        "responses": [
            (
                "ATTENTION, SPACE MAGGOT! Memorize all three clues in this bunker, then hit my True Believer Console and prove your skull isn't packed with sawdust!",
                "ATTENTION, SPACE MAGGOT! Memorize all three clues in this bunker, then hit my True Believer Console and prove your skull isn't packed with sawdust!",
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
                "LESS JAW-FLAPPING AND MORE READING THOSE DISPLAYS, RECRUIT! At Camp McClintock we ate live grenades for breakfast—you just have to pass Quiz One!",
                "LESS JAW-FLAPPING AND MORE READING THOSE DISPLAYS, RECRUIT! At Camp McClintock we ate live grenades for breakfast—you just have to pass Quiz One!",
            ),
        ],
    },
    # Stage 30 -> Flight Suit unlocked
    {
        "info_fid": 0x01004803,
        "prev_fid": 0x01004802,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 30.0)],
        "responses": [
            (
                "BARRIER ONE IS DOWN, KNUCKLEHEAD! Quit drooling into my optical sensors and go grab your Astro-Cosmos Flight Suit before I change my mind!",
                "BARRIER ONE IS DOWN, KNUCKLEHEAD! Quit drooling into my optical sensors and go grab your Astro-Cosmos Flight Suit before I change my mind!",
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
                "CONGRATULATIONS ON NOT SHORTING OUT MY TERMINAL WITH YOUR STUPIDITY! Double-time it to the stasis pod and put on that flight suit!",
                "CONGRATULATIONS ON NOT SHORTING OUT MY TERMINAL WITH YOUR STUPIDITY! Double-time it to the stasis pod and put on that flight suit!",
            ),
        ],
    },
    # Stage 35 -> Flight Suit claimed, talk to Artie
    {
        "info_fid": 0x01004805,
        "prev_fid": 0x01004804,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 35.0)],
        "responses": [
            (
                "HA! YOU LOOK ALMOST AS SNAPPY AS A SACK OF SPACE POTATOES, PRIVATE! Report to Vance for your rooftop flight orders over Boston!",
                "HA! YOU LOOK ALMOST AS SNAPPY AS A SACK OF SPACE POTATOES, PRIVATE! Report to Vance for your rooftop flight orders over Boston!",
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
                "STOP STRUTTING AROUND LIKE A COSMIC PEACOCK, CADET! Chief Engineer Vance is waiting to brief you on the coil recovery op!",
                "STOP STRUTTING AROUND LIKE A COSMIC PEACOCK, CADET! Chief Engineer Vance is waiting to brief you on the coil recovery op!",
            ),
        ],
    },
    # Stage 40 (0 coils) -> Rooftop patrol
    {
        "info_fid": 0x01004807,
        "prev_fid": 0x01004806,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 40.0)],
        "global_conds": [(0x00, 0.0, 0x01001003)],
        "responses": [
            (
                "WHY ARE YOU STILL BOLTED TO THE FLOOR LIKE A BROKEN FLOOR LAMP, SWABBIE?! Blast off to Hubris, Trinity, and WRVR for those three coils!",
                "WHY ARE YOU STILL BOLTED TO THE FLOOR LIKE A BROKEN FLOOR LAMP, SWABBIE?! Blast off to Hubris, Trinity, and W. R. V. R. for those three coils!",
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
                "BOSTON'S SKYLINE WON'T CONQUER ITSELF WHILE YOU STARE AT MY BASEMENT CEILING! Full throttle and bring back all three Photonic Coils!",
                "BOSTON'S SKYLINE WON'T CONQUER ITSELF WHILE YOU STARE AT MY BASEMENT CEILING! Full throttle and bring back all three Photonic Coils!",
            ),
        ],
    },
    # Stage 40 (>= 1 coil) -> Partial coils
    {
        "info_fid": 0x01004809,
        "prev_fid": 0x01004808,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 40.0)],
        "global_conds": [(0x60, 1.0, 0x01001003)],
        "responses": [
            (
                "GOOD, YOU BAGGED AT LEAST ONE COIL UP THERE! Too bad Uncle Sam awards zero bottlecaps for half-finished sorties! Fetch all three!",
                "GOOD, YOU BAGGED AT LEAST ONE COIL UP THERE! Too bad Uncle Sam awards zero bottlecaps for half-finished sorties! Fetch all three!",
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
                "WIPE THAT VICTORY SMIRK OFF YOUR FACE, FLYBOY! Until every single Photonic Coil is in your pack, Exam Two stays locked tighter than Fort Knox!",
                "WIPE THAT VICTORY SMIRK OFF YOUR FACE, FLYBOY! Until every single Photonic Coil is in your pack, Exam Two stays locked tighter than Fort Knox!",
            ),
        ],
    },
    # Stage 50 -> 3 coils ready: Exam 2
    {
        "info_fid": 0x01004022,
        "prev_fid": 0x0100480A,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 50.0)],
        "responses": [
            (
                "ALL THREE COILS ACCOUNTED FOR, AIRBORNE MAGGOT! March over to my Exam Console and prove you actually read the Unstoppables code!",
                "ALL THREE COILS ACCOUNTED FOR, AIRBORNE MAGGOT! March over to my Exam Console and prove you actually read the Unstoppables code!",
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
                "THREE COILS ALIGNED AND ZERO EXCUSES! Step up to the terminal and show me you weren't too busy sightseeing to read Clara's scripts!",
                "THREE COILS ALIGNED AND ZERO EXCUSES! Step up to the terminal and show me you weren't too busy sightseeing to read Clara's scripts!",
            ),
        ],
    },
    # Stage 60 -> Carbine unlocked
    {
        "info_fid": 0x0100480C,
        "prev_fid": 0x0100480B,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 60.0)],
        "responses": [
            (
                "PHOTONIC LAB GATE OPEN! Grab that Ray Carbine—and remember, it fires mid-flight in both your Flight Suit and your Power Armor!",
                "PHOTONIC LAB GATE OPEN! Grab that Ray Carbine—and remember, it fires mid-flight in both your Flight Suit and your Power Armor!",
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
                "TWO EXAMS PASSED WITHOUT BLOWING A FUSE! Snatch that Carbine off the pedestal before a radroach learns to use its six-power scope!",
                "TWO EXAMS PASSED WITHOUT BLOWING A FUSE! Snatch that Carbine off the pedestal before a radroach learns to use its six-power scope!",
            ),
        ],
    },
    # Stage 65 -> Carbine claimed, talk to Artie
    {
        "info_fid": 0x0100480E,
        "prev_fid": 0x0100480D,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 65.0)],
        "responses": [
            (
                "GOOD GRIP ON THAT RAY CARBINE, SOLDIER! Now double-time to Artie Vance for your airborne strike coordinates on ArcJet Systems!",
                "GOOD GRIP ON THAT RAY CARBINE, SOLDIER! Now double-time to Artie Vance for your airborne strike coordinates on ArcJet Systems!",
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
                "QUIT ADMIRING YOURSELF IN THE BARREL CHROME! Vance has the hot ArcJet Systems dossier ready for briefing!",
                "QUIT ADMIRING YOURSELF IN THE BARREL CHROME! Vance has the hot ArcJet Systems dossier ready for briefing!",
            ),
        ],
    },
    # Stage 70 -> Mission 3 at ArcJet
    {
        "info_fid": 0x01004810,
        "prev_fid": 0x0100480F,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 70.0)],
        "responses": [
            (
                "NO HALF-MEASURES OVER ARCJET SYSTEMS! Turn into a one-man strafing run, fry those tin-can sentries, and bring me the Synchrotron Core!",
                "NO HALF-MEASURES OVER ARCJET SYSTEMS! Turn into a one-man strafing run, fry those tin-can sentries, and bring me the Synchrotron Core!",
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
                "WHY ARE YOU STILL LOITERING DOWN HERE INSTEAD OF SWEEPING ARCJET'S ROOF?! I want Commie scrap dust and that Synchrotron Core in your pack NOW!",
                "WHY ARE YOU STILL LOITERING DOWN HERE INSTEAD OF SWEEPING ARCJET'S ROOF?! I want Commie scrap dust and that Synchrotron Core in your pack NOW!",
            ),
        ],
    },
    # Stage 80 -> Synchrotron Core ready: Exam 3
    {
        "info_fid": 0x01004023,
        "prev_fid": 0x01004811,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 80.0)],
        "responses": [
            (
                "THAT SYNCHROTRON CORE HUMS LIKE AN ORBITAL FIGHTER, LIEUTENANT! Front and center at the console—ace Quiz Three to open the Power Armor Hangar!",
                "THAT SYNCHROTRON CORE HUMS LIKE AN ORBITAL FIGHTER, LIEUTENANT! Front and center at the console—ace Quiz Three to open the Power Armor Hangar!",
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
                "FINE WORK SCRAPPING THOSE ARCJET SENTINELS! Now prove at my terminal that you can read censored comic books too if you want that Power Armor!",
                "FINE WORK SCRAPPING THOSE ARCJET SENTINELS! Now prove at my terminal that you can read censored comic books too if you want that Power Armor!",
            ),
        ],
    },
    # Stage 100 -> Power Armor Hangar open
    {
        "info_fid": 0x01004813,
        "prev_fid": 0x01004812,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 100.0)],
        "responses": [
            (
                "NORTH HANGAR BLAST DOORS WIDE OPEN! March in there and climb inside six tons of Cobalt-and-Gold American Glory!",
                "NORTH HANGAR BLAST DOORS WIDE OPEN! March in there and climb inside six tons of Cobalt-and-Gold American Glory!",
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
                "YOU'VE GOT FLIGHT POWER ARMOR WAITING IN THE HANGAR AND YOU'RE STANDING STILL?! Go claim Captain Cosmos's orbital plate right now!",
                "YOU'VE GOT FLIGHT POWER ARMOR WAITING IN THE HANGAR AND YOU'RE STANDING STILL?! Go claim Captain Cosmos's orbital plate right now!",
            ),
        ],
    },
    # Stage 110 -> Power Armor claimed, talk to Artie
    {
        "info_fid": 0x01004815,
        "prev_fid": 0x01004814,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 110.0)],
        "responses": [
            (
                "NOW THAT'S MORE LIKE IT, LIEUTENANT! Wrapped in six tons of titanium you almost look like a real soldier! See Vance for the final drop!",
                "NOW THAT'S MORE LIKE IT, LIEUTENANT! Wrapped in six tons of titanium you almost look like a real soldier! See Vance for the final drop!",
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
                "THOSE SERVOS SOUND LIKE THUNDER! Report to Engineer Vance on the double—Miss Sterling's last mission still needs finishing!",
                "THOSE SERVOS SOUND LIKE THUNDER! Report to Engineer Vance on the double—Miss Sterling's last mission still needs finishing!",
            ),
        ],
    },
    # Stage 120 -> Director's Suite + Fort Hagen
    {
        "info_fid": 0x01004817,
        "prev_fid": 0x01004816,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 120.0)],
        "responses": [
            (
                "MEMORIZE THE DIRECTOR'S MURAL WITHOUT DROOLING ON THE PARQUET, THEN LAUNCH FOR FORT HAGEN! I want Clara's Master Star Card before reveille!",
                "MEMORIZE THE DIRECTOR'S MURAL WITHOUT DROOLING ON THE PARQUET, THEN LAUNCH FOR FORT HAGEN! I want Clara's Master Star Card before reveille!",
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
                "MISS STERLING DESERVES A FULL HONOR SALUTE! Pull her Master Card off Fort Hagen's roof—Suit or Power Armor, just don't embarrass the unit!",
                "MISS STERLING DESERVES A FULL HONOR SALUTE! Pull her Master Card off Fort Hagen's roof—Suit or Power Armor, just don't embarrass the unit!",
            ),
        ],
    },
    # Stage 140 -> Master Card ready: Exam 4
    {
        "info_fid": 0x01004024,
        "prev_fid": 0x01004818,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 140.0)],
        "responses": [
            (
                "ATTENTION ON DECK! You recovered Miss Sterling's Star Card... Step to the console for the Captain of the Cosmos Master Exam!",
                "ATTENTION ON DECK! You recovered Miss Sterling's Star Card... Step to the console for the Captain of the Cosmos Master Exam!",
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
                "ONE FINAL EXAM BETWEEN GLORY OR ETERNAL DISGRACE, COMMANDER! Play Miss Sterling's recording and get in front of my console!",
                "ONE FINAL EXAM BETWEEN GLORY OR ETERNAL DISGRACE, COMMANDER! Play Miss Sterling's recording and get in front of my console!",
            ),
        ],
    },
    # Stage 160 -> Orbital Gauss Cannon unlocked
    {
        "info_fid": 0x0100481A,
        "prev_fid": 0x01004819,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 160.0)],
        "responses": [
            (
                "SOLAR RELIQUARY OPEN, CAPTAIN! Claim that Orbital Gauss Cannon—it's tuned to fire mid-flight in both Power Armor and your Flight Suit!",
                "SOLAR RELIQUARY OPEN, CAPTAIN! Claim that Orbital Gauss Cannon—it's tuned to fire mid-flight in both Power Armor and your Flight Suit!",
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
                "GET TO THE NORTH HANGAR AND HEFT THAT ORBITAL GAUSS CANNON! And you'd better NOT aim it at my basement ceiling during test-fire!",
                "GET TO THE NORTH HANGAR AND HEFT THAT ORBITAL GAUSS CANNON! And you'd better NOT aim it at my basement ceiling during test-fire!",
            ),
        ],
    },
    # Stage 165 -> Studio handover with Artie
    {
        "info_fid": 0x0100481C,
        "prev_fid": 0x0100481B,
        "enam_flags": 0x02,
        "stage_conds": [(0x00, 165.0)],
        "responses": [
            (
                "ARSENAL AT ONE HUNDRED PERCENT CAPACITY, SIR! Vance wants to hand over the permanent keys to Orbit-7 before I start leaking oil!",
                "ARSENAL AT ONE HUNDRED PERCENT CAPACITY, SIR! Vance wants to hand over the permanent keys to Orbit Seven before I start leaking oil!",
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
                "ALL FOUR PROTOTYPES IN THE HANDS OF A REAL AMERICAN HERO! Speak with Artie to finalize transfer of command!",
                "ALL FOUR PROTOTYPES IN THE HANDS OF A REAL AMERICAN HERO! Speak with Artie to finalize transfer of command!",
            ),
        ],
    },
    # Stage 200+ -> 4 post-campaign greetings (Camp McClintock spirit + Free Drills reminder)
    {
        "info_fid": 0x01004025,
        "prev_fid": 0x0100481D,
        "enam_flags": 0x02,
        "stage_conds": [(0x60, 200.0)],
        "responses": [
            (
                "AT YOUR COMMAND, CAPTAIN OF THE COSMOS! Perimeter clear of lunar Commies and mutant moths, sir!",
                "AT YOUR COMMAND, CAPTAIN OF THE COSMOS! Perimeter clear of lunar Commies and mutant moths, sir!",
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
                "ITCHING FOR SOME ORBITAL BOOT CAMP DISCIPLINE, CAPTAIN? All four Free Drills are unlocked on my console whenever you want to test those reflexes!",
                "ITCHING FOR SOME ORBITAL BOOT CAMP DISCIPLINE, CAPTAIN? All four Free Drills are unlocked on my console whenever you want to test those reflexes!",
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
                "ALL QUIET IN THE ROTUNDA, SIR! Well, except Vance trying to scrape rust off the pipes with a soup spoon... Hit a Free Drill if you miss my yelling!",
                "ALL QUIET IN THE ROTUNDA, SIR! Well, except Vance trying to scrape rust off the pipes with a soup spoon... Hit a Free Drill if you miss my yelling!",
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
                "SERVOS GREASED AND READY TO RAIN ALL-AMERICAN JUSTICE FROM THE CLOUDS, SIR! Both weapons are calibrated for Flight Suit and Power Armor!",
                "SERVOS GREASED AND READY TO RAIN ALL-AMERICAN JUSTICE FROM THE CLOUDS, SIR! Both weapons are calibrated for Flight Suit and Power Armor!",
            ),
        ],
    },
    # Emergency fallback
    {
        "info_fid": 0x01004026,
        "prev_fid": 0x01004820,
        "enam_flags": 0x00,
        "stage_conds": [(0x60, 15.0)],
        "responses": [
            (
                "MOVE THAT COSMIC BACKSIDE, RECRUIT! Not a single barrier drops until you finish your flight objectives and face my console!",
                "MOVE THAT COSMIC BACKSIDE, RECRUIT! Not a single barrier drops until you finish your flight objectives and face my console!",
            ),
        ],
    },
]

# Dynamic 3D barks (DIAL 0x01004003, CUST) fired via PlayCoronelBark(bark_id)
CORONEL_BARK_INFOS = [
    # 1..4: Intros to the 4 exams
    {
        "info_fid": 0x01004031,
        "prev_fid": 0x00000000,
        "bark_id": 1,
        "responses": [(
            "EYES FRONT, SPACE LARVA! Level One Recruit Exam! One wrong answer and you'll be scrubbing lunar craters with a toothbrush!",
            "EYES FRONT, SPACE LARVA! Level One Recruit Exam! One wrong answer and you'll be scrubbing lunar craters with a toothbrush!",
        )],
    },
    {
        "info_fid": 0x01004032,
        "prev_fid": 0x01004031,
        "bark_id": 2,
        "responses": [(
            "STAND AT ATTENTION AT THAT MONITOR, CADET! Aerial Patrol Exam on The Unstoppables! Prove you can read more than Nuka-Cola bottle labels!",
            "STAND AT ATTENTION AT THAT MONITOR, CADET! Aerial Patrol Exam on The Unstoppables! Prove you can read more than Nuka-Cola bottle labels!",
        )],
    },
    {
        "info_fid": 0x01004033,
        "prev_fid": 0x01004032,
        "bark_id": 3,
        "responses": [(
            "SILENCE IN THE ROTUNDA! Orbital Pilot Exam for Power Armor clearance! Let's see if you've got titanium guts or mashed potatoes for brains!",
            "SILENCE IN THE ROTUNDA! Orbital Pilot Exam for Power Armor clearance! Let's see if you've got titanium guts or mashed potatoes for brains!",
        )],
    },
    {
        "info_fid": 0x01004034,
        "prev_fid": 0x01004033,
        "bark_id": 4,
        "responses": [(
            "MOMENT OF TRUTH, CANDIDATE! Master Exam on the Star Guard Oath! Honor Clara Sterling's legacy or crawl back topside crying!",
            "MOMENT OF TRUTH, CANDIDATE! Master Exam on the Star Guard Oath! Honor Clara Sterling's legacy or crawl back topside crying!",
        )],
    },
    # 5..9: 5 Camp McClintock drill-sergeant insults on failure
    {
        "info_fid": 0x01004035,
        "prev_fid": 0x01004034,
        "bark_id": 5,
        "responses": [(
            "SWEET JUMPING SATURN, YOU RADIOACTIVE KNUCKLEHEAD! Even Jangles the Moon Monkey could answer that wearing his helmet backwards!",
            "SWEET JUMPING SATURN, YOU RADIOACTIVE KNUCKLEHEAD! Even Jangles the Moon Monkey could answer that wearing his helmet backwards!",
        )],
    },
    {
        "info_fid": 0x01004036,
        "prev_fid": 0x01004035,
        "bark_id": 6,
        "responses": [(
            "NEGATIVE, YOU GALACTIC DIRTBAG! You're dimmer than a dead firefly inside a black hole! Go back and actually read the clues!",
            "NEGATIVE, YOU GALACTIC DIRTBAG! You're dimmer than a dead firefly inside a black hole! Go back and actually read the clues!",
        )],
    },
    {
        "info_fid": 0x01004037,
        "prev_fid": 0x01004036,
        "bark_id": 7,
        "responses": [(
            "WHAT IN SAM HILL WAS THAT, YOU MOLERAT-BRAINED DOOFUS?! It's a miracle you don't lace your combat boots onto your ears! FAILED!",
            "WHAT IN SAM HILL WAS THAT, YOU MOLERAT-BRAINED DOOFUS?! It's a miracle you don't lace your combat boots onto your ears! FAILED!",
        )],
    },
    {
        "info_fid": 0x01004038,
        "prev_fid": 0x01004037,
        "bark_id": 8,
        "responses": [(
            "BLATANT FAILURE, YOU OUTER-SPACE COMMIE IMPOSTOR! Pull another stunt like that and I'll vaporize your official fan club card!",
            "BLATANT FAILURE, YOU OUTER-SPACE COMMIE IMPOSTOR! Pull another stunt like that and I'll vaporize your official fan club card!",
        )],
    },
    {
        "info_fid": 0x01004039,
        "prev_fid": 0x01004038,
        "bark_id": 9,
        "responses": [(
            "BY GROGNAK'S AXE, WHAT A PATHETIC EXCUSE FOR A RECRUIT! About face, open your mole-rat eyes, and come back when you learn to read!",
            "BY GROGNAK'S AXE, WHAT A PATHETIC EXCUSE FOR A RECRUIT! About face, open your mole-rat eyes, and come back when you learn to read!",
        )],
    },
    # 10..13: Barked congratulations when passing 3/3 on each exam
    {
        "info_fid": 0x0100403A,
        "prev_fid": 0x01004039,
        "bark_id": 10,
        "responses": [(
            "THREE FOR THREE, MAGGOT! Maybe you aren't quite as dense as you look! Dropping Stasis Barrier One—go grab your Flight Suit!",
            "THREE FOR THREE, MAGGOT! Maybe you aren't quite as dense as you look! Dropping Stasis Barrier One—go grab your Flight Suit!",
        )],
    },
    {
        "info_fid": 0x0100403B,
        "prev_fid": 0x0100403A,
        "bark_id": 11,
        "responses": [(
            "DEAD-EYE SCORE, CADET FIRST CLASS! Dropping the Photonic Lab shield! Grab that Ray Carbine and turn the bad guys into cosmic confetti!",
            "DEAD-EYE SCORE, CADET FIRST CLASS! Dropping the Photonic Lab shield! Grab that Ray Carbine and turn the bad guys into cosmic confetti!",
        )],
    },
    {
        "info_fid": 0x0100403C,
        "prev_fid": 0x0100403B,
        "bark_id": 12,
        "responses": [(
            "OUTSTANDING, STAR LIEUTENANT! Unsealing the North Orbital Hangar gates! That Astro-Cosmos Power Armor is officially yours!",
            "OUTSTANDING, STAR LIEUTENANT! Unsealing the North Orbital Hangar gates! That Astro-Cosmos Power Armor is officially yours!",
        )],
    },
    {
        "info_fid": 0x0100403D,
        "prev_fid": 0x0100403C,
        "bark_id": 13,
        "responses": [(
            "FULL DRESS SALUTE TO OUR NEW CAPTAIN OF THE COSMOS! Miss Clara would be mighty proud of you, soldier! Solar Reliquary unlocked!",
            "FULL DRESS SALUTE TO OUR NEW CAPTAIN OF THE COSMOS! Miss Clara would be mighty proud of you, soldier! Solar Reliquary unlocked!",
        )],
    },
    # 14..17: Cheers upon physically claiming each prototype
    {
        "info_fid": 0x0100403E,
        "prev_fid": 0x0100403D,
        "bark_id": 14,
        "responses": [(
            "NOW THAT'S A HERO'S UNIFORM, NOT THOSE STREET RAGS YOU DRAGGED IN! Report to Vance for your first flight sortie!",
            "NOW THAT'S A HERO'S UNIFORM, NOT THOSE STREET RAGS YOU DRAGGED IN! Report to Vance for your first flight sortie!",
        )],
    },
    {
        "info_fid": 0x0100403F,
        "prev_fid": 0x0100403E,
        "bark_id": 15,
        "responses": [(
            "LOOK AT THAT PHOTONIC CARBINE SHINE! Six-power zoom of pure All-American Justice straight from the clouds!",
            "LOOK AT THAT PHOTONIC CARBINE SHINE! Six-power zoom of pure All-American Justice straight from the clouds!",
        )],
    },
    {
        "info_fid": 0x01004040,
        "prev_fid": 0x0100403F,
        "bark_id": 16,
        "responses": [(
            "ATOMIC THRUSTERS ONLINE! With that reactor torso on your back, no dirt-hugging worm can hide from you!",
            "ATOMIC THRUSTERS ONLINE! With that reactor torso on your back, no dirt-hugging worm can hide from you!",
        )],
    },
    {
        "info_fid": 0x01004041,
        "prev_fid": 0x01004040,
        "bark_id": 17,
        "responses": [(
            "THE ORBITAL GAUSS CANNON IS IN THE CAPTAIN'S HANDS! Let every tyrant across the galaxy shake in their boots!",
            "THE ORBITAL GAUSS CANNON IS IN THE CAPTAIN'S HANDS! Let every tyrant across the galaxy shake in their boots!",
        )],
    },
    # 18..20: Epilogue salute & console warnings
    {
        "info_fid": 0x01004042,
        "prev_fid": 0x01004041,
        "bark_id": 18,
        "responses": [(
            "UNDERGROUND STUDIO ORBIT-7 TRANSFERRED TO COMMAND OF CAPTAIN OF THE COSMOS! For Truth, the Stars, and Tomorrow, sir!",
            "UNDERGROUND STUDIO ORBIT SEVEN TRANSFERRED TO COMMAND OF CAPTAIN OF THE COSMOS! For Truth, the Stars, and Tomorrow, sir!",
        )],
    },
    {
        "info_fid": 0x01004043,
        "prev_fid": 0x01004042,
        "bark_id": 19,
        "responses": [(
            "HOLD YOUR HORSES, RECRUIT! You don't have the hardware or clearance for the next test yet! Finish your field mission first!",
            "HOLD YOUR HORSES, RECRUIT! You don't have the hardware or clearance for the next test yet! Finish your field mission first!",
        )],
    },
    {
        "info_fid": 0x01004044,
        "prev_fid": 0x01004043,
        "bark_id": 20,
        "responses": [(
            "QUIT MASHING MY BUTTONS, BLOCKHEAD! You already passed that test—double-time over and claim your unlocked prototype!",
            "QUIT MASHING MY BUTTONS, BLOCKHEAD! You already passed that test—double-time over and claim your unlocked prototype!",
        )],
    },
]

# ==============================================================================
# 3. THE 5 INTERACTIVE DIALOGUE-WHEEL SCENES WITH ARTIE VANCE
# ==============================================================================
ARTIE_SCENES = [
    # SCENE 1 (0x01004100): Stage 15 -> 20 (Welcome & Mission 1)
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
                        "rnam": "Agree to help",
                        "p_dial": 0x01004111, "p_info": 0x01004121,
                        "n_dial": 0x01004112, "n_info": 0x01004122,
                        "p_sub": "I picked up your radio signal near Hubris Comics. What is this bunker, and how can I help?",
                        "p_tts": "I picked up your radio signal near Hubris Comics. What is this bunker, and how can I help?",
                        "tiqs_stage": 20,
                        "n_responses": [
                            (
                                "Back in '77, Hubris Comics and a rogue team of engineers built real Captain Cosmos tech down here: a Flight Suit, Power Armor, and two airborne weapons.",
                                "Back in seventy-seven, Hubris Comics and a rogue team of engineers built real Captain Cosmos tech down here: a Flight Suit, Power Armor, and two airborne weapons.",
                            ),
                            (
                                "Our lead writer, Clara Sterling, programmed Colonel Gutsy so no crooked brass could seize them—only someone who knows our heroes' lore can drop the barriers.",
                                "Our lead writer, Clara Sterling, programmed Colonel Gutsy so no crooked brass could seize them—only someone who knows our heroes' lore can drop the barriers.",
                            ),
                            (
                                "Find the first three clues right here in the Rotunda and East Writers' Room, then pass the Colonel's test to claim the Astro-Cosmos Flight Suit.",
                                "Find the first three clues right here in the Rotunda and East Writers' Room, then pass the Colonel's test to claim the Astro-Cosmos Flight Suit.",
                            ),
                        ],
                    },
                    {
                        "rnam": "Joke about the bot",
                        "p_dial": 0x01004113, "p_info": 0x01004123,
                        "n_dial": 0x01004114, "n_info": 0x01004124,
                        "p_sub": "Did a military combat robot just threaten me with a comic-book fan club card?",
                        "p_tts": "Did a military combat robot just threaten me with a comic-book fan club card?",
                        "tiqs_stage": 20,
                        "n_responses": [
                            (
                                "Haha! That's Colonel Gutsy 'Cosmos.' Clara crossed an Army drill instructor matrix with forty years of Hubris Comics back issues.",
                                "Haha! That's Colonel Gutsy 'Cosmos.' Clara crossed an Army drill instructor matrix with forty years of Hubris Comics back issues.",
                            ),
                            (
                                "He'll scream blue murder if you miss a question, sure—but deep down the old tin can loves guarding the four real Astro-Cosmos prototypes.",
                                "He'll scream blue murder if you miss a question, sure—but deep down the old tin can loves guarding the four real Astro-Cosmos prototypes.",
                            ),
                            (
                                "Inspect the Rotunda showcase, Clara's drafting desk, and her terminal in the Writers' Wing, then take his quiz at the console for your Flight Suit.",
                                "Inspect the Rotunda showcase, Clara's drafting desk, and her terminal in the Writers' Wing, then take his quiz at the console for your Flight Suit.",
                            ),
                        ],
                    },
                    {
                        "rnam": "Cut to the chase",
                        "p_dial": 0x01004115, "p_info": 0x01004125,
                        "n_dial": 0x01004116, "n_info": 0x01004126,
                        "p_sub": "I see armored pods behind laser fields. Tell me what's inside and how we open them.",
                        "p_tts": "I see armored pods behind laser fields. Tell me what's inside and how we open them.",
                        "tiqs_stage": 20,
                        "n_responses": [
                            (
                                "Straight to business, I respect that. Those bays hold four working wonders: the Astro-Cosmos Flight Suit, Ray Carbine, Power Armor, and Orbital Gauss Cannon.",
                                "Straight to business, I respect that. Those bays hold four working wonders: the Astro-Cosmos Flight Suit, Ray Carbine, Power Armor, and Orbital Gauss Cannon.",
                            ),
                            (
                                "Colonel Gutsy only lowers each barrier for a 'True Believer' who passes his trivia exams on Hubris Comics history.",
                                "Colonel Gutsy only lowers each barrier for a True Believer who passes his trivia exams on Hubris Comics history.",
                            ),
                            (
                                "Read the Rotunda showcase and step into the East Writers' Wing to inspect the drafting desk and terminal, then take the exam on his console.",
                                "Read the Rotunda showcase and step into the East Writers' Wing to inspect the drafting desk and terminal, then take the exam on his console.",
                            ),
                        ],
                    },
                    {
                        "rnam": "Who was Clara?",
                        "p_dial": 0x01004117, "p_info": 0x01004127,
                        "n_dial": 0x01004118, "n_info": 0x01004128,
                        "p_sub": "Who built an underground studio like this beneath Hubris Comics?",
                        "p_tts": "Who built an underground studio like this beneath Hubris Comics?",
                        "tiqs_stage": 20,
                        "n_responses": [
                            (
                                "It was built for the live-action Captain Cosmos TV series slated to premiere November 2077, spearheaded by our head writer, Clara Sterling.",
                                "It was built for the live-action Captain Cosmos T.V. series slated to premiere November twenty seventy-seven, spearheaded by our head writer, Clara Sterling.",
                            ),
                            (
                                "When the Pentagon tried to hijack our flight thrusters as strike weapons, Clara locked the prototypes behind trivia riddles from her own comics.",
                                "When the Pentagon tried to hijack our flight thrusters as strike weapons, Clara locked the prototypes behind trivia riddles from her own comics.",
                            ),
                            (
                                "Everything starts at the Rotunda display and Clara's desk and terminal in the east wing. Gather those three clues and ace the Colonel's first test.",
                                "Everything starts at the Rotunda display and Clara's desk and terminal in the east wing. Gather those three clues and ace the Colonel's first test.",
                            ),
                        ],
                    },
                ],
            }
        ],
    },
    # SCENE 2 (0x01004200): Stage 35 -> 40 (Mission 2: Rooftop Patrol)
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
                        "rnam": "Ready to fly!",
                        "p_dial": 0x01004211, "p_info": 0x01004221, "p_info_f": 0x01004231,
                        "n_dial": 0x01004212, "n_info": 0x01004222,
                        "p_sub": "I'm ready to take wing, Artie. Where am I headed?",
                        "p_tts": "I'm ready to take wing, Artie. Where am I headed?",
                        "p_sub_f": "I'm ready to take wing, Artie. Where am I headed?",
                        "p_tts_f": "I'm ready to take wing, Artie. Where am I headed?",
                        "rnam_f": "Ready to fly!",
                        "tiqs_stage": 40,
                        "n_responses": [
                            (
                                "Inside the West Photonic Lab rests the Astro-Cosmos Ray Carbine—the only gyro-stabilized weapon built to aim and fire accurately mid-flight.",
                                "Inside the West Photonic Lab rests the Astro-Cosmos Ray Carbine—the only gyro-stabilized weapon built to aim and fire accurately mid-flight.",
                            ),
                            (
                                "To power its pedestal we need three Photonic Coils Clara hid on three Boston rooftops: Hubris Comics, Trinity Plaza, and WRVR Radio.",
                                "To power its pedestal we need three Photonic Coils Clara hid on three Boston rooftops: Hubris Comics, Trinity Plaza, and W. R. V. R. Radio.",
                            ),
                            (
                                "Suit up outside, fly to all three sky-caches, and study Clara's holotape and The Unstoppables dossiers for Colonel Gutsy's second quiz.",
                                "Suit up outside, fly to all three sky-caches, and study Clara's holotape and The Unstoppables dossiers for Colonel Gutsy's second quiz.",
                            ),
                        ],
                    },
                    {
                        "rnam": "Superhero joke",
                        "p_dial": 0x01004213, "p_info": 0x01004223,
                        "n_dial": 0x01004214, "n_info": 0x01004224,
                        "p_sub": "With a suit like this, all I need now is to patrol Boston rooftops like the Silver Shroud.",
                        "p_tts": "With a suit like this, all I need now is to patrol Boston rooftops like the Silver Shroud.",
                        "tiqs_stage": 40,
                        "n_responses": [
                            (
                                "You hit the nail on the head—because patrolling Boston rooftops is literally your next assignment!",
                                "You hit the nail on the head—because patrolling Boston rooftops is literally your next assignment!",
                            ),
                            (
                                "Clara stashed the Ray Carbine's three Photonic Coils atop Hubris Comics, Trinity Plaza, and WRVR Radio where no ground-bound raider could reach them.",
                                "Clara stashed the Ray Carbine's three Photonic Coils atop Hubris Comics, Trinity Plaza, and W. R. V. R. Radio where no ground-bound raider could reach them.",
                            ),
                            (
                                "Bring back those coils along with Clara's first tape and The Unstoppables files, and the Colonel will unlock the Carbine pedestal.",
                                "Bring back those coils along with Clara's first tape and The Unstoppables files, and the Colonel will unlock the Carbine pedestal.",
                            ),
                        ],
                    },
                    {
                        "rnam": "About the Carbine",
                        "p_dial": 0x01004215, "p_info": 0x01004225,
                        "n_dial": 0x01004216, "n_info": 0x01004226,
                        "p_sub": "Tell me about that Ray Carbine in the west lab. What makes it so special?",
                        "p_tts": "Tell me about that Ray Carbine in the west lab. What makes it so special?",
                        "tiqs_stage": 40,
                        "n_responses": [
                            (
                                "Conventional guns destabilize the suit's anti-grav field, so I engineered the Astro-Cosmos Carbine with harmonic balancers and a six-power recon scope.",
                                "Conventional guns destabilize the suit's anti-grav field, so I engineered the Astro-Cosmos Carbine with harmonic balancers and a six-power recon scope.",
                            ),
                            (
                                "Its three Photonic Coils are waiting atop Hubris Comics, Trinity Plaza, and WRVR Radio alongside clues on The Unstoppables.",
                                "Its three Photonic Coils are waiting atop Hubris Comics, Trinity Plaza, and W. R. V. R. Radio alongside clues on The Unstoppables.",
                            ),
                            (
                                "Head topside, kick on your thrusters, and bring all three coils home for the second exam.",
                                "Head topside, kick on your thrusters, and bring all three coils home for the second exam.",
                            ),
                        ],
                    },
                    {
                        "rnam": "What happened to Clara?",
                        "p_dial": 0x01004217, "p_info": 0x01004227,
                        "n_dial": 0x01004218, "n_info": 0x01004228,
                        "p_sub": "Did Clara Sterling leave recordings up on those rooftops before the bombs dropped?",
                        "p_tts": "Did Clara Sterling leave recordings up on those rooftops before the bombs dropped?",
                        "tiqs_stage": 40,
                        "n_responses": [
                            (
                                "Yes... On the night of October 22nd she climbed those roofs alone to scatter the coils and hide her holotapes from federal agents.",
                                "Yes... On the night of October twenty-second she climbed those roofs alone to scatter the coils and hide her holotapes from federal agents.",
                            ),
                            (
                                "I marked Hubris Comics, Trinity Plaza, and WRVR Radio on your Pip-Boy. Fly up there, snag all three coils, and hear her voice for yourself.",
                                "I marked Hubris Comics, Trinity Plaza, and W. R. V. R. Radio on your Pip-Boy. Fly up there, snag all three coils, and hear her voice for yourself.",
                            ),
                        ],
                    },
                ],
            }
        ],
    },
    # SCENE 3 (0x01004300): Stage 65 -> 70 (Mission 3: Operation Star Titan at ArcJet)
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
                        "rnam": "Headed to ArcJet",
                        "p_dial": 0x01004311, "p_info": 0x01004321,
                        "n_dial": 0x01004312, "n_info": 0x01004322,
                        "p_sub": "Tell me what's waiting on the ArcJet Systems roof and I'll bring that Core home.",
                        "p_tts": "Tell me what's waiting on the ArcJet Systems roof and I'll bring that Core home.",
                        "tiqs_stage": 70,
                        "n_responses": [
                            (
                                "Behind the North Hangar barrier waits our armored crown jewel: full Astro-Cosmos Power Armor with twin free-flight reactors and 100%% radiation shielding.",
                                "Behind the North Hangar barrier waits our armored crown jewel: full Astro-Cosmos Power Armor with twin free-flight reactors and one hundred percent radiation shielding.",
                            ),
                            (
                                "ArcJet Systems forged its thruster nozzles, but their execs locked the Test Synchrotron Core in a sky-vault on their upper roof guarded by combat bots.",
                                "ArcJet Systems forged its thruster nozzles, but their execs locked the Test Synchrotron Core in a sky-vault on their upper roof guarded by combat bots.",
                            ),
                            (
                                "Soar over ArcJet's highest deck, drop those sentries mid-air with your new Carbine, and recover the Core, Clara's second tape, and Issue 50.",
                                "Soar over ArcJet's highest deck, drop those sentries mid-air with your new Carbine, and recover the Core, Clara's second tape, and Issue Fifty.",
                            ),
                        ],
                    },
                    {
                        "rnam": "Aerial target practice",
                        "p_dial": 0x01004313, "p_info": 0x01004323,
                        "n_dial": 0x01004314, "n_info": 0x01004324,
                        "p_sub": "Those ArcJet security bots will make great target practice from three hundred feet up.",
                        "p_tts": "Those ArcJet security bots will make great target practice from three hundred feet up.",
                        "tiqs_stage": 70,
                        "n_responses": [
                            (
                                "That's the Captain Cosmos spirit! Hovering overhead with your Carbine's recon scope gives you total air superiority.",
                                "That's the Captain Cosmos spirit! Hovering overhead with your Carbine's recon scope gives you total air superiority.",
                            ),
                            (
                                "Crack the armored vault on ArcJet Systems' top deck, grab the Synchrotron Core, and read Clara's tape and the censored Issue 50 draft for Quiz Three.",
                                "Crack the armored vault on ArcJet Systems' top deck, grab the Synchrotron Core, and read Clara's tape and the censored Issue Fifty draft for Quiz Three.",
                            ),
                        ],
                    },
                    {
                        "rnam": "About the Power Armor",
                        "p_dial": 0x01004315, "p_info": 0x01004325,
                        "n_dial": 0x01004316, "n_info": 0x01004326,
                        "p_sub": "Full Power Armor that sustains true flight—not just short jetpack hops?",
                        "p_tts": "Full Power Armor that sustains true flight—not just short jetpack hops?",
                        "tiqs_stage": 70,
                        "n_responses": [
                            (
                                "True sustained flight, partner. Its twin-reactor torso holds altitude effortlessly, and its six cobalt-and-gold pieces shrug off the Glowing Sea at zero rads.",
                                "True sustained flight, partner. Its twin-reactor torso holds altitude effortlessly, and its six cobalt-and-gold pieces shrug off the Glowing Sea at zero rads.",
                            ),
                            (
                                "Bring back the Synchrotron Core from ArcJet's outer roof, pass Colonel Gutsy's third test, and the North Hangar opens wide.",
                                "Bring back the Synchrotron Core from ArcJet's outer roof, pass Colonel Gutsy's third test, and the North Hangar opens wide.",
                            ),
                        ],
                    },
                    {
                        "rnam": "Censored Issue #50",
                        "p_dial": 0x01004317, "p_info": 0x01004327,
                        "n_dial": 0x01004318, "n_info": 0x01004328,
                        "p_sub": "On her last tape, Clara mentioned a censored special issue. Is it at ArcJet?",
                        "p_tts": "On her last tape, Clara mentioned a censored special issue. Is it at ArcJet?",
                        "tiqs_stage": 70,
                        "n_responses": [
                            (
                                "Sharp memory. Clara slipped onto ArcJet's roof to reclaim the printing plates for Captain Cosmos Special #50 after defense contractors seized them.",
                                "Sharp memory. Clara slipped onto ArcJet's roof to reclaim the printing plates for Captain Cosmos Special Number Fifty after defense contractors seized them.",
                            ),
                            (
                                "You'll find the draft, her second holotape, and the Synchrotron Core waiting on ArcJet Systems' highest outer deck. Happy hunting up there.",
                                "You'll find the draft, her second holotape, and the Synchrotron Core waiting on ArcJet Systems' highest outer deck. Happy hunting up there.",
                            ),
                        ],
                    },
                ],
            }
        ],
    },
    # SCENE 4 (0x01004400): Stage 110 -> 120 (Mission 4: Director's Room + Fort Hagen)
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
                        "rnam": "For Clara Sterling",
                        "p_dial": 0x01004411, "p_info": 0x01004421,
                        "n_dial": 0x01004412, "n_info": 0x01004422,
                        "p_sub": "Let's finish what Clara started, Artie. Open the Director's Suite and tell me where she went that day.",
                        "p_tts": "Let's finish what Clara started, Artie. Open the Director's Suite and tell me where she went that day.",
                        "tiqs_stage": 120,
                        "n_responses": [
                            (
                                "I've just dropped the barrier to the Director's Projection Suite south of the Writers' Wing. Step inside and inspect the Grand Star Guard Mural.",
                                "I've just dropped the barrier to the Director's Projection Suite south of the Writers' Wing. Step inside and inspect the Grand Star Guard Mural.",
                            ),
                            (
                                "On the morning of October 23, 2077, Clara flew to Fort Hagen's satellite relay roof to wipe Orbit-7's coordinates from the Pentagon grid.",
                                "On the morning of October twenty-third, twenty seventy-seven, Clara flew to Fort Hagen's satellite relay roof to wipe Orbit Seven's coordinates from the Pentagon grid.",
                            ),
                            (
                                "Take your Power Armor to the bunker roof beneath Fort Hagen's northeast dish, scrap the Pentagon automatons, and recover her Master Card and last tape.",
                                "Take your Power Armor to the bunker roof beneath Fort Hagen's northeast dish, scrap the Pentagon automatons, and recover her Master Card and last tape.",
                            ),
                        ],
                    },
                    {
                        "rnam": "Smash bots in PA",
                        "p_dial": 0x01004413, "p_info": 0x01004423,
                        "n_dial": 0x01004414, "n_info": 0x01004424,
                        "p_sub": "Time to christen this flying Power Armor. Who's holding the key to the Solar Reliquary?",
                        "p_tts": "Time to christen this flying Power Armor. Who's holding the key to the Solar Reliquary?",
                        "tiqs_stage": 120,
                        "n_responses": [
                            (
                                "Pentagon contractor automatons still guarding the roof beneath Fort Hagen's northeast satellite dish, where Clara flew her final mission on Bombs Day.",
                                "Pentagon contractor automatons still guarding the roof beneath Fort Hagen's northeast satellite dish, where Clara flew her final mission on Bombs Day.",
                            ),
                            (
                                "Before you launch, step into the Director's Suite south of the east wing and memorize the Grand Mural oath—you'll need it plus Clara's tape for the Cannon.",
                                "Before you launch, step into the Director's Suite south of the east wing and memorize the Grand Mural oath—you'll need it plus Clara's tape for the Cannon.",
                            ),
                        ],
                    },
                    {
                        "rnam": "About the Gauss Cannon",
                        "p_dial": 0x01004415, "p_info": 0x01004425,
                        "n_dial": 0x01004416, "n_info": 0x01004426,
                        "p_sub": "What kind of monster is locked inside that Solar Reliquary?",
                        "p_tts": "What kind of monster is locked inside that Solar Reliquary?",
                        "tiqs_stage": 120,
                        "n_responses": [
                            (
                                "Our magnum opus: the Orbital Gauss Cannon—a quad-ring Saturn accelerator with an 8x observatory scope and mid-flight solar supernova blasts.",
                                "Our magnum opus: the Orbital Gauss Cannon—a quad-ring Saturn accelerator with an eight-power observatory scope and mid-flight solar supernova blasts.",
                            ),
                            (
                                "Check the Grand Mural inside the newly opened Director's Suite first, then soar to Fort Hagen's satellite roof for Clara's Master Star Card.",
                                "Check the Grand Mural inside the newly opened Director's Suite first, then soar to Fort Hagen's satellite roof for Clara's Master Star Card.",
                            ),
                        ],
                    },
                    {
                        "rnam": "Clara's sacrifice",
                        "p_dial": 0x01004417, "p_info": 0x01004427,
                        "n_dial": 0x01004418, "n_info": 0x01004428,
                        "p_sub": "She never made it back to Orbit-7 on October 23rd, did she?",
                        "p_tts": "She never made it back to Orbit Seven on October twenty-third, did she?",
                        "tiqs_stage": 120,
                        "n_responses": [
                            (
                                "No... Because she purged our satellite uplink at Fort Hagen as the sirens wailed, the Pentagon never tracked down Orbit-7.",
                                "No... Because she purged our satellite uplink at Fort Hagen as the sirens wailed, the Pentagon never tracked down Orbit Seven.",
                            ),
                            (
                                "I've unlocked her Projection Suite and Quarters in the southeast wing. Inspect the mural, fly out to Fort Hagen's dish, and bring back her last tape.",
                                "I've unlocked her Projection Suite and Quarters in the southeast wing. Inspect the mural, fly out to Fort Hagen's dish, and bring back her last tape.",
                            ),
                        ],
                    },
                ],
            }
        ],
    },
    # SCENE 5 (0x01004500): Stage 165 -> 200 (Epilogue: Studio Orbit-7 Permanent Player Home)
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
                        "rnam": "Proud to be Captain",
                        "p_dial": 0x01004511, "p_info": 0x01004521,
                        "n_dial": 0x01004512, "n_info": 0x01004522,
                        "p_sub": "Clara saved this place so science would protect innocent lives. I'll live up to that.",
                        "p_tts": "Clara saved this place so science would protect innocent lives. I'll live up to that.",
                        "tiqs_stage": 200,
                        "n_responses": [
                            (
                                "You already have, my friend. That's why I'm handing you the permanent Deed of Stewardship for Underground Studio Orbit-7.",
                                "You already have, my friend. That's why I'm handing you the permanent Deed of Stewardship for Underground Studio Orbit Seven.",
                            ),
                            (
                                "The Director's Quarters, Captain's Spacer Bed, safe Star Chests, and every engineering bench are now yours—and the Colonel and I will guard it always.",
                                "The Director's Quarters, Captain's Spacer Bed, safe Star Chests, and every engineering bench are now yours—and the Colonel and I will guard it always.",
                            ),
                        ],
                    },
                    {
                        "rnam": "Miss his yelling?",
                        "p_dial": 0x01004513, "p_info": 0x01004523,
                        "n_dial": 0x01004514, "n_info": 0x01004524,
                        "p_sub": "Funny thing is, I might actually miss Colonel Gutsy screaming insults at me.",
                        "p_tts": "Funny thing is, I might actually miss Colonel Gutsy screaming insults at me.",
                        "tiqs_stage": 200,
                        "n_responses": [
                            (
                                "Haha! Now that he's promoted you to Captain of the Cosmos, he'll snap his pincers into a full salute every time you walk through the door.",
                                "Haha! Now that he's promoted you to Captain of the Cosmos, he'll snap his pincers into a full salute every time you walk through the door.",
                            ),
                            (
                                "Take the Orbit-7 Studio Deed and reserve supplies—the Spacer Bed, safe Star Chests, and full workshops are your permanent base from today on.",
                                "Take the Orbit Seven Studio Deed and reserve supplies—the Spacer Bed, safe Star Chests, and full workshops are your permanent base from today on.",
                            ),
                        ],
                    },
                    {
                        "rnam": "A safe new home",
                        "p_dial": 0x01004515, "p_info": 0x01004525,
                        "n_dial": 0x01004516, "n_info": 0x01004526,
                        "p_sub": "An Art-Deco fortress bunker right beneath downtown Boston will come in handy. What about you?",
                        "p_tts": "An Art-Deco fortress bunker right beneath downtown Boston will come in handy. What about you?",
                        "tiqs_stage": 200,
                        "n_responses": [
                            (
                                "I'll stay right here keeping the reactors, workshops, and planetarium humming whenever you swoop home from patrolling the Commonwealth skies.",
                                "I'll stay right here keeping the reactors, workshops, and planetarium humming whenever you swoop home from patrolling the Commonwealth skies.",
                            ),
                            (
                                "Here are the master keys and spare rations—catch a rested nap in the Captain's Spacer Bed and stash your gear in the Star Chests anytime.",
                                "Here are the master keys and spare rations—catch a rested nap in the Captain's Spacer Bed and stash your gear in the Star Chests anytime.",
                            ),
                        ],
                    },
                    {
                        "rnam": "To the stars!",
                        "p_dial": 0x01004517, "p_info": 0x01004527,
                        "n_dial": 0x01004518, "n_info": 0x01004528,
                        "p_sub": "For Truth, the Stars, and Tomorrow, Artie! It's been one hell of a flight.",
                        "p_tts": "For Truth, the Stars, and Tomorrow, Artie! It's been one hell of a flight.",
                        "tiqs_stage": 200,
                        "n_responses": [
                            (
                                "For Truth, the Stars, and Tomorrow, Captain! Hubris Comics wrote the legend, and you just brought it soaring to life above Boston.",
                                "For Truth, the Stars, and Tomorrow, Captain! Hubris Comics wrote the legend, and you just brought it soaring to life above Boston.",
                            ),
                            (
                                "Underground Studio Orbit-7 is officially your permanent sanctuary. Clear skies up there, hero!",
                                "Underground Studio Orbit Seven is officially your permanent sanctuary. Clear skies up there, hero!",
                            ),
                        ],
                    },
                ],
            }
        ],
    },
]

# ==============================================================================
# 4. CLARA STERLING VOICED HOLOTAPES (NOTE 0x01001401..0x01001403)
# ==============================================================================
CLARA_HOLOTAPES = [
    {
        "note_fid": 0x01001401,
        "note_edid": "NoteOrbita7HoloClara1",
        "note_full": "Clara Sterling Holotape #1: The True Unstoppables",
        "scen_fid": 0x01004601,
        "scen_edid": "Orbita7HoloScene1_Clara",
        "dial_fid": 0x01004611,
        "info_fid": 0x01004621,
        "responses": [
            (
                "Clara Sterling logging in, October 22, 2077, atop Hubris Comics. If you flew up here, Artie finally found someone worthy of the Astro-Cosmos Suit.",
                "Clara Sterling logging in, October twenty-second, twenty seventy-seven, atop Hubris Comics. If you flew up here, Artie finally found someone worthy of the Astro-Cosmos Suit.",
            ),
            (
                "I've scattered the three Photonic Coils across Boston's skyline. Keep this sharp for our loudmouthed Colonel Gutsy's second quiz:",
                "I've scattered the three Photonic Coils across Boston's skyline. Keep this sharp for our loudmouthed Colonel Gutsy's second quiz:",
            ),
            (
                "Everyone remembers the Silver Shroud, Grognak, Manta Man, and Mistress of Mystery—but the fifth founder of The Unstoppables is the master illusionist with top hat and wand: The Inspector!",
                "Everyone remembers the Silver Shroud, Grognak, Manta Man, and Mistress of Mystery—but the fifth founder of The Unstoppables is the master illusionist with top hat and wand: The Inspector!",
            ),
        ],
    },
    {
        "note_fid": 0x01001402,
        "note_edid": "NoteOrbita7HoloClara2",
        "note_full": "Clara Sterling Holotape #2: Sabotage at ArcJet",
        "scen_fid": 0x01004602,
        "scen_edid": "Orbita7HoloScene2_Clara",
        "dial_fid": 0x01004612,
        "info_fid": 0x01004622,
        "responses": [
            (
                "Clara Sterling, slipping onto ArcJet Systems' upper roof. An hour ago Defense Department contractors moved in to confiscate the entire project.",
                "Clara Sterling, slipping onto ArcJet Systems' upper roof. An hour ago Defense Department contractors moved in to confiscate the entire project.",
            ),
            (
                "It was ArcJet Systems itself—the aerospace giant—that quietly built the twin sustained-flight nozzles for our Astro-Cosmos Power Armor.",
                "It was ArcJet Systems itself—the aerospace giant—that quietly built the twin sustained-flight nozzles for our Astro-Cosmos Power Armor.",
            ),
            (
                "I sealed the Synchrotron Core and my Special Issue #50 draft inside this vault. If the Colonel asks which contractor forged our thrusters, remember: ArcJet Systems.",
                "I sealed the Synchrotron Core and my Special Issue Fifty draft inside this vault. If the Colonel asks which contractor forged our thrusters, remember: ArcJet Systems.",
            ),
        ],
    },
    {
        "note_fid": 0x01001403,
        "note_edid": "NoteOrbita7HoloClara3",
        "note_full": "Clara Sterling Holotape #3: Final Transmission (Oct 23, 2077)",
        "scen_fid": 0x01004603,
        "scen_edid": "Orbita7HoloScene3_Clara",
        "dial_fid": 0x01004613,
        "info_fid": 0x01004623,
        "responses": [
            (
                "October 23, 2077... Air-raid sirens are screaming across Boston's skyline, but I just purged Orbit-7's coordinates from this Fort Hagen relay dish.",
                "October twenty-third, twenty seventy-seven... Air-raid sirens are screaming across Boston's skyline, but I just purged Orbit Seven's coordinates from this Fort Hagen relay dish.",
            ),
            (
                "Whoever finds this in tomorrow's world: to unlock the Solar Reliquary, remember our Orbital Gauss Cannon fires 2mm EC electromagnetic cartridges.",
                "Whoever finds this in tomorrow's world: to unlock the Solar Reliquary, remember our Orbital Gauss Cannon fires two millimeter E. C. electromagnetic cartridges.",
            ),
            (
                "I won't make it to a shelter... My last wish is that someday a decent soul uses our science to protect the innocent. Tell Artie and my grumpy Colonel it was worth reaching for the stars.",
                "I won't make it to a shelter... My last wish is that someday a decent soul uses our science to protect the innocent. Tell Artie and my grumpy Colonel it was worth reaching for the stars.",
            ),
        ],
    },
]

# ==============================================================================
# 5. INTERACTIVE PLAQUES, TERMINALS, DOSSIERS & 4 EXAMS (12 QUESTIONS)
# ==============================================================================
CLUE_MESSAGES = [
    (
        0x01001301,
        "MesgOrbita7VitrineCosmos",
        "Commemorative Showcase — Captain Cosmos #1 (March 2063)",
        (
            "Behind armored glass gleams an original mint issue of 'Adventures of Captain Cosmos #1' beside its curatorial plaque:\r\n\r\n"
            "• LOYAL CO-PILOT: 'Jangles the Moon Monkey,' the astronaut chimp who pulled the Captain free from Venusian gravity mines.\r\n"
            "• SECRET HEADQUARTERS: The hidden Star Citadel beneath 'Tycho Crater' on the Moon.\r\n\r\n"
            "[Handwritten margin note]: \"Never let a recruit forget Jangles or Tycho Crater before stepping up to the Colonel!\""
        ),
        ["Close"],
    ),
    (
        0x01001302,
        "MesgOrbita7VitrineUnstoppables",
        "Commemorative Showcase — The League of Unstoppables",
        (
            "A collector's edition of 'The Unstoppables vs. the Brain Mutants!' displays all five Hubris Comics champions:\r\n\r\n"
            "• The Silver Shroud (Avenger of the Night)\r\n"
            "• Grognak the Barbarian (Lord of the Prehistoric Wastes)\r\n"
            "• Manta Man (Defender of the Deep)\r\n"
            "• The Mistress of Mystery (Lady of Shadows)\r\n"
            "• The fifth member is hidden beneath a classified seal: \"See Clara Sterling Holotape #1 atop Hubris Comics.\""
        ),
        ["Close"],
    ),
    (
        0x01001303,
        "MesgOrbita7DraftingDesk",
        "Inking & Drafting Desk — Clara Sterling (Head Writer)",
        (
            "Three glass pigment inkwells rest atop the backlit drafting glass beside the Official Project Astro-Cosmos Color Spec:\r\n\r\n"
            "• OFFICIAL CAPTAIN COSMOS CHROMATIC TRIAD:\r\n"
            "  1. 'Cobalt Blue' for the pressurized starflight chassis.\r\n"
            "  2. 'Crimson Red' for the heroic cape, gauntlets, and flight boots.\r\n"
            "  3. 'Solar Gold' for the eight-pointed star crest and accelerator rings.\r\n\r\n"
            "[Clara's ink note]: \"Artie wanted military olive drab. Over my dead body! Cobalt Blue, Crimson Red, and Solar Gold.\""
        ),
        ["Close"],
    ),
    (
        0x01001304,
        "MesgOrbita7DirectorMural",
        "Grand Star Guard Oath Mural — Director's Suite",
        (
            "A monumental backlit oil painting in gold and cobalt dominates Hubris Comics' private screening suite.\r\n\r\n"
            "Beneath the silhouette of Captain Cosmos soaring toward the rings of Saturn, the Supreme Oath of the Star Guard shines in engraved bronze letters:\r\n\r\n"
            "\"FOR TRUTH, THE STARS, AND TOMORROW!\""
        ),
        ["Memorize the Star Guard Oath"],
    ),
]

EXAM_QUESTIONS = [
    # --- EXAM 1 (0x01001311..0x01001313) ---
    (
        0x01001311,
        "MesgOrbita7Exam1Q1",
        "RECRUIT EXAM (1/3) — Colonel Gutsy 'Cosmos'",
        "\"FIRST QUESTION, EARTHWORM!\r\n\r\nWhat is the name of Captain Cosmos's heroic simian co-pilot, and inside which lunar crater does his secret headquarters hide?\"",
        [
            "Bobo the Atomic Chimp, in the Sea of Tranquility",
            "Jangles the Moon Monkey, in Tycho Crater",
            "Sergeant Banana, around the Rings of Jupiter",
            "[Step back and review the clues first]",
        ],
    ),
    (
        0x01001312,
        "MesgOrbita7Exam1Q2",
        "RECRUIT EXAM (2/3) — Colonel Gutsy 'Cosmos'",
        "\"SECOND QUESTION, TADPOLE!\r\n\r\nAccording to Clara Sterling's official drafting table, what is the exact three-color scheme of the Astro-Cosmos uniform?\"",
        [
            "Army Olive Green, Lead Gray, and Mustard Yellow",
            "Bubblegum Pink, Mutant Purple, and Chrome Silver",
            "Cobalt Blue, Crimson Red, and Solar Gold",
            "[Step back and review the clues first]",
        ],
    ),
    (
        0x01001313,
        "MesgOrbita7Exam1Q3",
        "RECRUIT EXAM (3/3) — Colonel Gutsy 'Cosmos'",
        "\"THIRD AND FINAL QUESTION FOR THE SUIT, ROOKIE!\r\n\r\nPer the TV Production Terminal, what date and station were locked in for Captain Cosmos's grand television premiere?\"",
        [
            "November 15, 2077, on Boston Channel 5",
            "July 4, 2076, on Radio Freedom",
            "October 31, 2077, on the Vault-Tec Network",
            "[Step back and review the clues first]",
        ],
    ),
    # --- EXAM 2 (0x01001314..0x01001316) ---
    (
        0x01001314,
        "MesgOrbita7Exam2Q1",
        "AERIAL PATROL EXAM (1/3) — Colonel Gutsy 'Cosmos'",
        "\"EYES FRONT, FLYING CADET!\r\n\r\nAlongside the Silver Shroud, Grognak, Manta Man, and Mistress of Mystery, who completes the five founding members of The Unstoppables?\"",
        [
            "Captain Dogmeat of Concord",
            "The Masked Plumber of Nuka-World",
            "The Inspector, master illusionist with top hat and wand",
            "[Step back and review the clues first]",
        ],
    ),
    (
        0x01001315,
        "MesgOrbita7Exam2Q2",
        "AERIAL PATROL EXAM (2/3) — Colonel Gutsy 'Cosmos'",
        "\"SECOND PATROL QUESTION!\r\n\r\nAccording to the Editorial Dossier recovered at Trinity Plaza, who is Grognak the Barbarian's sworn arch-nemesis?\"",
        [
            "The Kurse-Maker",
            "The Sinister IRS Auditor",
            "The Giant Mudcrab of the Charles River",
            "[Step back and review the clues first]",
        ],
    ),
    (
        0x01001316,
        "MesgOrbita7Exam2Q3",
        "AERIAL PATROL EXAM (3/3) — Colonel Gutsy 'Cosmos'",
        "\"THIRD QUESTION TO UNLOCK THE RAY CARBINE!\r\n\r\nPer the WRVR radio script, what is the Golden Maxim of The Unstoppables' Code?\"",
        [
            "Shoot first and collect royalties later",
            "Brains beat brawn when heroes stand united",
            "Never iron your cape over an active fusion reactor",
            "[Step back and review the clues first]",
        ],
    ),
    # --- EXAM 3 (0x01001317..0x01001319) ---
    (
        0x01001317,
        "MesgOrbita7Exam3Q1",
        "ORBITAL PILOT EXAM (1/3) — Colonel Gutsy 'Cosmos'",
        "\"STAND AT ATTENTION, STAR TITAN CANDIDATE!\r\n\r\nWhich Boston aerospace contractor secretly built the twin sustained-flight thrusters for the Astro-Cosmos Power Armor?\"",
        [
            "Longneck Lukowski's Cannery",
            "ArcJet Systems",
            "Super Duper Mart Rocketry Division",
            "[Step back and review the clues first]",
        ],
    ),
    (
        0x01001318,
        "MesgOrbita7Exam3Q2",
        "ORBITAL PILOT EXAM (2/3) — Colonel Gutsy 'Cosmos'",
        "\"SECOND ORBITAL QUESTION!\r\n\r\nIn the censored draft of Captain Cosmos Special #50, which galactic tyrant attempts to scorch Earth with radiation storms?\"",
        [
            "Baron Meatball of Planet Pluto",
            "The Molerat Queen of the Asteroid Belt",
            "Emperor Quasar",
            "[Step back and review the clues first]",
        ],
    ),
    (
        0x01001319,
        "MesgOrbita7Exam3Q3",
        "ORBITAL PILOT EXAM (3/3) — Colonel Gutsy 'Cosmos'",
        "\"THIRD QUESTION TO UNSEAL THE POWER ARMOR HANGAR!\r\n\r\nBeyond continuous flight, what legendary defense is built into the Astro-Cosmos Torso in both Issue #50 and our real prototype?\"",
        [
            "Total Cosmic Immunity Shield against radiation",
            "Automatic boiling-coffee dispenser inside the helmet",
            "Stealth plating scented with space lavender",
            "[Step back and review the clues first]",
        ],
    ),
    # --- MASTER EXAM 4 (0x0100131A..0x0100131C) ---
    (
        0x0100131A,
        "MesgOrbita7Exam4Q1",
        "MASTER EXAM: 'CAPTAIN OF THE COSMOS' (1/3)",
        "\"ATTENTION ON DECK! FIRST QUESTION OF THE SUPREME EXAM!\r\n\r\nWhat is the Supreme Oath engraved beneath the Grand Mural in the Director's Suite?\"",
        [
            "Faster than a tax bill and tougher than a brick!",
            "For bottlecaps, bacon, and Sunday naps!",
            "For Truth, the Stars, and Tomorrow!",
            "[Step back and review the clues first]",
        ],
    ),
    (
        0x0100131B,
        "MesgOrbita7Exam4Q2",
        "MASTER EXAM: 'CAPTAIN OF THE COSMOS' (2/3)",
        "\"SECOND SUPREME QUESTION!\r\n\r\nPer Clara Sterling's final transmission from Fort Hagen, what caliber ammunition does the Astro-Cosmos Orbital Gauss Cannon fire?\"",
        [
            "Signed Diamond City Swatters",
            "2mm EC electromagnetic cartridges",
            "Rusted Sunset Sarsaparilla star caps",
            "[Step back and review the clues first]",
        ],
    ),
    (
        0x0100131C,
        "MesgOrbita7Exam4Q3",
        "MASTER EXAM: 'CAPTAIN OF THE COSMOS' (3/3)",
        "\"FINAL QUESTION TO EARN THE RANK OF CAPTAIN OF THE COSMOS!\r\n\r\nAs the bombs fell on October 23, 2077, what was Clara Sterling's dying wish when she saved Orbit-7?\"",
        [
            "That someday a decent soul would use their science to protect the innocent",
            "That the prototypes be auctioned off to Pentagon contractors",
            "That nobody in the Commonwealth would ever read a comic again",
            "[Step back and review the clues first]",
        ],
    ),
]

# ==============================================================================
# 6. CAMPAIGN MESSAGES, TERMINALS, DOSSIERS & QUEST STAGES / OBJECTIVES
# ==============================================================================
EXTRA_MESSAGES = [
    (
        0x01001300,
        "MesgOrbita7RadioIntercept",
        "[PROJECT ASTRO-COSMOS — HUBRIS FREQUENCY INTERCEPTED]",
        (
            "Your Pip-Boy has locked onto a civilian shortwave carrier pulsing from beneath downtown Boston, "
            "directly under the back alley behind Hubris Comics HQ:\r\n\r\n"
            "\"...This is Arthur 'Artie' Vance, Chief Special Effects and Aerospace Propulsion Engineer "
            "at Hubris Comics, broadcasting from Underground Studio Orbit-7.\r\n\r\n"
            "If anyone with a Pip-Boy and a hero's heart hears this: the studio reactors "
            "just woke up after two hundred and ten years. Down here we're safeguarding Captain Cosmos's "
            "four working flight and cosmic-combat prototypes... alongside a reprogrammed Colonel Gutsy "
            "who refuses to unseal a single vault until someone passes his quizzes on Hubris Comics lore.\r\n\r\n"
            "I've unlatched the outer armored hatch in the alley behind Hubris Comics and pushed the map "
            "marker to your Pip-Boy. Come down and see me when you're ready, friend!\""
        ),
        ["Log coordinates for Underground Studio Orbit-7"],
    ),
    (
        0x01001323,
        "MesgOrbita7ExamNotReady",
        "True Believer Protocol Console — Standing By",
        (
            "The console's CRT flickers in warm starfield amber:\r\n\r\n"
            "\"SYSTEM STATUS: Active field phase in progress.\r\n"
            "Complete your current field objectives or brief Chief Engineer Artie Vance "
            "to authorize Colonel Gutsy's next regulation interrogation.\""
        ),
        ["Understood"],
    ),
    (
        0x01001324,
        "MesgOrbita7HomeUnlocked",
        "Permanent Sanctuary Unlocked: Underground Studio Orbit-7!",
        (
            "Congratulations, Captain of the Cosmos! You have completed 'The Hubris Legacy: Project Astro-Cosmos' "
            "and united all four working aerospace prototypes:\r\n\r\n"
            "• Astro-Cosmos Flight Suit (Free Flight [Y] + 100%% radiation immunity)\r\n"
            "• Astro-Cosmos Ray Carbine (6x recon scope, mid-flight compatible with Suit & PA)\r\n"
            "• Astro-Cosmos Power Armor (6 orbital pieces with sustained flight)\r\n"
            "• Astro-Cosmos Orbital Gauss Cannon (8x observatory scope, mid-flight compatible with PA & Suit)\r\n\r\n"
            "Underground Studio Orbit-7 is now your permanent player home beneath downtown Boston:\r\n"
            "• Captain Cosmos Spacer Bed granting the 'Well Rested' bonus.\r\n"
            "• 100%% safe armored Star Chests (containers never respawn).\r\n"
            "• Full Power Armor Station, Weapons Workbench, Armor Workbench, and Chemistry Station.\r\n"
            "• Direct Fast Travel enabled and guarded permanently by Artie Vance and Colonel Gutsy."
        ),
        ["For Truth, the Stars, and Tomorrow!"],
    ),
]

TERMINAL_PRODUCTION_TV = {
    "fid": 0x01001140,
    "edid": "TermOrbita7ProductionTV",
    "full": "TV Production Terminal — Clara Sterling",
    "header": (
        "HUBRIS COMICS TELEVISION & UNDERGROUND STUDIO ORBIT-7\r\n"
        "Writers' Suite — Clara Sterling's Terminal (Head Writer)\r\n"
        "Select an editorial archive entry:"
    ),
    "entries": [
        (
            "1. Official TV Broadcast Schedule (Fall 2077)",
            (
                "INTERNAL MEMO — HUBRIS COMICS BROADCAST DIVISION\r\n"
                "From: Clara Sterling, Executive Producer & Head Writer\r\n"
                "Subject: LIVE-ACTION PREMIERE DATE LOCKED IN!\r\n\r\n"
                "We pulled it off, team! After Artie's live sustained-flight demo beneath the "
                "Planetarium dome, the regional affiliate signed our prime-time broadcast slot:\r\n\r\n"
                "- PREMIERE DATE: November 15, 2077\r\n"
                "- OFFICIAL NETWORK: Boston Channel 5 (WGBH / Metro Feed)\r\n"
                "- PILOT TITLE: 'Captain Cosmos and the Citadel of Tycho Crater'\r\n\r\n"
                "Commit that date and station to memory (November 15, 2077, on Boston Channel 5): "
                "our cranky Colonel Gutsy just hard-coded it as Question Three of the mandatory "
                "Recruit Exam."
            ),
        ),
        (
            "2. Regarding Our New Head of Security: Colonel Gutsy 'Cosmos'",
            (
                "PRODUCTION LOG — SEPTEMBER 14, 2077\r\n\r\n"
                "The Defense Department loaned us a surplus Army Mister Gutsy to stand watch over "
                "our prototype stasis bays. Artie then had the brilliant, reckless idea to upload "
                "all 420 Hubris Comics issues straight into its neural core.\r\n\r\n"
                "The result? It insists on being addressed as 'Colonel Gutsy Cosmos,' calls every "
                "civilian an 'uncultured earthworm,' and wired the photonic barriers to its True "
                "Believer Console. Miss one answer and he'll chew your ears off—yet somehow the "
                "loudmouthed tin can has grown on us."
            ),
        ),
        (
            "3. Confidential Alert: Pentagon Movements (Oct 21, 2077)",
            (
                "ENCRYPTED NOTE — EYES ONLY: ARTHUR VANCE\r\n\r\n"
                "Artie: the Pentagon liaisons plan to cancel the TV premiere and commandeer all "
                "four of our prototypes as orbital assault hardware. I won't let them.\r\n\r\n"
                "Tonight I'm scaling Boston's rooftops to scatter the Ray Carbine's Photonic Coils, "
                "locking the Synchrotron Core atop ArcJet Systems, and hiding my Master Star Card "
                "at the Fort Hagen satellite relay. Only a hero who flies like Captain Cosmos and "
                "knows our stories will ever reunite them."
            ),
        ),
    ],
}

TERMINAL_ARTIE_LAB = {
    "fid": 0x01001141,
    "edid": "TermOrbita7ArtieLab",
    "full": "Photonic Engineering Terminal — Arthur 'Artie' Vance",
    "header": (
        "UNDERGROUND STUDIO ORBIT-7 — PROPULSION & WEAPONS LAB\r\n"
        "Chief Engineer: Dr. Arthur 'Artie' Vance\r\n"
        "Select a technical dossier:"
    ),
    "entries": [
        (
            "1. Spec Sheet I: Astro-Cosmos Flight Suit",
            (
                "PROTOTYPE #1 — ASTRO-COSMOS FLIGHT SUIT\r\n\r\n"
                "- Propulsion: Atomic-resonance vector micro-thrusters (toggle flight mid-air or on "
                "ground with Jump [Y] / [Triangle] / [Space]).\r\n"
                "- Shielding: Cobalt Blue, Crimson Red, and Solar Gold weave featuring the legendary "
                "Total Cosmic Immunity Shield against radiation (0.0 RADS even inside the Glowing Sea) "
                "plus orbital impact dampers."
            ),
        ),
        (
            "2. Spec Sheet II: Astro-Cosmos Ray Carbine (6x Recon Scope)",
            (
                "PROTOTYPE #2 — ASTRO-COSMOS RAY CARBINE\r\n\r\n"
                "- Gyro-stabilized photonic carbine synced for seamless mid-flight firing with BOTH "
                "the Astro-Cosmos Flight Suit and the Astro-Cosmos Power Armor.\r\n"
                "- Optics: 6x Astro-Cosmos Recon Scope with high-altitude automatic target tagging.\r\n"
                "- Cosmic Surge: Every 4th hit releases a Cosmic Photonic Pulse (+25 AP, +15 HP)."
            ),
        ),
        (
            "3. Spec Sheet III: Astro-Cosmos Power Armor (ArcJet Pact)",
            (
                "PROTOTYPE #3 — ASTRO-COSMOS POWER ARMOR (ORBITAL SERIES)\r\n\r\n"
                "- Co-engineered with propulsion specialists at ArcJet Systems, who secretly machined "
                "the twin continuous-thrust dorsal nozzles.\r\n"
                "- Full six-piece cobalt-and-gold orbital armor housing an integrated Torso Total "
                "Cosmic Immunity Shield against radiation."
            ),
        ),
        (
            "4. Spec Sheet IV: Astro-Cosmos Orbital Gauss Cannon (8x Scope)",
            (
                "PROTOTYPE #4 — ASTRO-COSMOS ORBITAL GAUSS CANNON\r\n\r\n"
                "- Heavy long-range cannon engineered for mid-flight firing with BOTH the Astro-Cosmos "
                "Power Armor and the Astro-Cosmos Flight Suit.\r\n"
                "- Caliber: Accelerates 2mm EC electromagnetic cartridges to orbital velocity across "
                "four toroidal Saturn accelerator coils.\r\n"
                "- Optics & Surge: 8x Orbital Observatory Scope; every 3rd hit triggers a Solar "
                "Gravitational Supernova (+35 AP, +25 HP, shockwave blast)."
            ),
        ),
    ],
}


def _build_exam_terminal_defs() -> list[dict]:
    """Builds the contiguous hierarchy of 21 TERM records (`0x01001500..0x01001514`)."""
    exams_meta = [
        (
            1,
            "Orbital Recruit Exam",
            "Astro-Cosmos Flight Suit",
            "Showcase #1, Clara Sterling's Drafting Desk, and the TV Production Terminal",
            (1, 2, 0),
        ),
        (
            2,
            "Aerial Patrol Exam",
            "Astro-Cosmos Ray Carbine",
            "The Unstoppables Showcase #2, the Trinity Plaza Dossier, and the WRVR Script",
            (2, 0, 1),
        ),
        (
            3,
            "Orbital Pilot Exam",
            "Astro-Cosmos Power Armor",
            "Artie's Engineering Terminal and the Censored Issue #50 Draft from ArcJet Systems",
            (1, 2, 0),
        ),
        (
            4,
            "Master Exam: 'Captain of the Cosmos'",
            "Astro-Cosmos Orbital Gauss Cannon",
            "the Director's Grand Mural and Clara's final Holotape from Fort Hagen",
            (2, 1, 0),
        ),
    ]

    main_term = {
        "fid": 0x01001500,
        "edid": "TermOrbita7ExamMain",
        "full": "'Cosmic Challenge!' Exam Console",
        "header": (
            "HUBRIS COMICS — UNDERGROUND STUDIO ORBIT-7\r\n"
            "'COSMIC CHALLENGE!' EVALUATION SYSTEM — COLONEL GUTSY\r\n"
            "Answer all 3 questions in a row without a mistake to drop the photonic shield:"
        ),
        "entries": [
            {
                "itxt": "[Access Locked — Register with Dr. Artie Vance]",
                "anam": 0x08,
                "itid": 10,
                "conds": [("stage", 0x80, 20.0)],
                "unam": (
                    "TERMINAL AWAITING CONTESTANT REGISTRATION.\r\n\r\n"
                    "Speak with Dr. Arthur 'Artie' Vance right here in the Central Rotunda "
                    "to initialize Colonel Gutsy's official examination circuit."
                ),
            },
            {
                "itxt": "Start Exam 1: Orbital Recruit (Flight Suit)",
                "anam": 0x04,
                "itid": 101,
                "tnam": 0x01001501,
                "conds": [("stage", 0x00, 20.0)],
            },
            {
                "itxt": "Start Exam 2: Aerial Patrol (Ray Carbine)",
                "anam": 0x04,
                "itid": 102,
                "tnam": 0x01001506,
                "conds": [("stage", 0x00, 50.0)],
            },
            {
                "itxt": "Start Exam 3: Orbital Pilot (Power Armor)",
                "anam": 0x04,
                "itid": 103,
                "tnam": 0x0100150B,
                "conds": [("stage", 0x00, 80.0)],
            },
            {
                "itxt": "Start Exam 4: Captain of the Cosmos (Gauss Cannon)",
                "anam": 0x04,
                "itid": 104,
                "tnam": 0x01001510,
                "conds": [("stage", 0x00, 140.0)],
            },
            {
                "itxt": "[Exam Passed — Claim your unlocked prototype]",
                "anam": 0x08,
                "itid": 110,
                "conds": [
                    ("stage", 0x01, 30.0),
                    ("stage", 0x01, 60.0),
                    ("stage", 0x01, 100.0),
                    ("stage", 0x00, 160.0),
                ],
                "unam": (
                    "PHOTONIC BARRIER DEACTIVATED!\r\n\r\n"
                    "Your latest exam already shows PASSED in Colonel Gutsy's military log. "
                    "Head over to the unsealed chamber to claim your new Astro-Cosmos prototype."
                ),
            },
            {
                "itxt": "[Field Op Active — Complete objective or see Artie]",
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
                    "FIELD OPERATION CURRENTLY UNDERWAY.\r\n\r\n"
                    "The next exam stays locked until you complete your active exterior "
                    "mission or brief Dr. Artie Vance on your latest findings."
                ),
            },
            {
                "itxt": "[Supreme Rank: Captain of the Cosmos — All Cleared]",
                "anam": 0x08,
                "itid": 120,
                "conds": [("stage", 0x60, 200.0)],
                "unam": (
                    "HONOR DOSSIER — COLONEL GUTSY 'COSMOS':\r\n\r\n"
                    "You cleared all four regulation exams and united the entire Astro-Cosmos "
                    "arsenal. Underground Studio Orbit-7 is permanently yours.\r\n"
                    "For Truth, the Stars, and Tomorrow!"
                ),
            },
            {
                "itxt": "[Free Drill I: Orbital Recruit Trial]",
                "anam": 0x04,
                "itid": 101,
                "tnam": 0x01001501,
                "conds": [("stage", 0x60, 200.0)],
            },
            {
                "itxt": "[Free Drill II: Aerial Patrol & Marksmanship]",
                "anam": 0x04,
                "itid": 102,
                "tnam": 0x01001506,
                "conds": [("stage", 0x60, 200.0)],
            },
            {
                "itxt": "[Free Drill III: Heavy Chassis Engineering]",
                "anam": 0x04,
                "itid": 103,
                "tnam": 0x0100150B,
                "conds": [("stage", 0x60, 200.0)],
            },
            {
                "itxt": "[Free Drill IV: Captain of the Cosmos Master Exam]",
                "anam": 0x04,
                "itid": 104,
                "tnam": 0x01001510,
                "conds": [("stage", 0x60, 200.0)],
            },
            {
                "itxt": "'Cosmic Challenge!' Official Quiz Regulations",
                "anam": 0x08,
                "itid": 130,
                "conds": [],
                "unam": (
                    "COLONEL GUTSY'S OFFICIAL QUIZ REGULATIONS:\r\n\r\n"
                    "1. Each exam runs 3 consecutive questions inside this terminal.\r\n"
                    "2. A right answer automatically advances to the next question.\r\n"
                    "3. A single mistake voids the attempt and resets the quiz to zero.\r\n"
                    "4. Every answer can be found in the studio showcases, drafting desk, "
                    "terminals, recovered dossiers, and Clara Sterling's holotapes."
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
                q_clean = raw_body.split("\r\n\r\n", 1)[1].rstrip("\"").strip()
            else:
                q_clean = raw_body.strip("\"").strip()

            progress_banner = ""
            if q_idx == 1:
                progress_banner = "[✓ QUESTION 1 CLEARED]\r\n"
            elif q_idx == 2:
                progress_banner = "[✓ QUESTIONS 1 & 2 CLEARED — FINAL QUESTION]\r\n"

            q_header = (
                f"{e_title.upper()} — QUESTION {q_idx + 1} OF 3\r\n"
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
                    "itxt": "[Step back to review the studio clues]",
                    "anam": 0x05,
                    "itid": 90,
                }
            )
            terms.append(
                {
                    "fid": q_fid,
                    "edid": f"TermOrbita7Exam{e_idx}Q{q_idx + 1}",
                    "full": f"Exam {e_idx} — Question {q_idx + 1}/3",
                    "header": q_header,
                    "entries": q_entries,
                }
            )

        # Pass Screen (3/3)
        terms.append(
            {
                "fid": pass_fid,
                "edid": f"TermOrbita7Exam{e_idx}Pass",
                "full": f"Exam {e_idx} — Passed!",
                "header": (
                    f"3 OUT OF 3 CORRECT — {e_title.upper()} PASSED!!\r\n\r\n"
                    f"Colonel Gutsy's Log:\r\n"
                    f"\"Unbelievable... the photonic barrier just dropped.\r\n"
                    f"Double-time over and claim your {reward_name}.\""
                ),
                "entries": [
                    {
                        "itxt": "[Exit console and go claim your unlocked prototype]",
                        "anam": 0x05,
                        "itid": 99,
                    }
                ],
            }
        )

        # Fail Screen (Reset)
        terms.append(
            {
                "fid": fail_fid,
                "edid": f"TermOrbita7Exam{e_idx}Fail",
                "full": f"Exam {e_idx} — Incorrect Answer",
                "header": (
                    f"WRONG ANSWER — {e_title.upper()} VOIDED!\r\n\r\n"
                    f"Colonel Gutsy's tribunal demands 3 straight correct answers.\r\n"
                    f"Study tip: check {clues_hint}."
                ),
                "entries": [
                    {
                        "itxt": "Retry this exam from Question 1",
                        "anam": 0x04,
                        "itid": 104 + e_idx,
                        "tnam": base_fid,
                    },
                    {
                        "itxt": "[Exit console to double-check the clues]",
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
        "Hubris Dossier: Arch-Enemies of Grognak",
        (
            "HUBRIS COMICS EDITORIAL ARCHIVE — CLASSIC CHARACTER DOSSIER\r\n"
            "Series: 'Grognak the Barbarian' (Created by Rod Gamber)\r\n\r\n"
            "Out of every prehistoric beast and warlord to clash with Grognak's double-bladed axe, "
            "only one holds the official title of SWORN ARCH-NEMESIS:\r\n\r\n"
            "• 'THE KURSE-MAKER', dark sorcerer of forbidden curses who swore to break the "
            "Barbarian's untamed spirit.\r\n\r\n"
            "[Clara Sterling's handwritten note]:\r\n"
            "\"If you're reading this on Trinity Plaza's high terrace, nice flight! Stash the second "
            "Photonic Coil and keep 'The Kurse-Maker' front and center for Colonel Gutsy's second quiz.\""
        ),
    ),
    (
        0x01001161,
        "BookOrbita7WRVRScript",
        "WRVR Radio Script: The Code of The Unstoppables",
        (
            "WRVR BOSTON BROADCAST — SPECIAL GALA SCRIPT (OCTOBER 2077)\r\n"
            "Episode: 'The Eternal Alliance of The Unstoppables!'\r\n\r\n"
            "ANNOUNCER (with heroic echo):\r\n"
            "\"When darkness blankets the metropolis and villainy raises its claws, five voices "
            "proclaim the GOLDEN MAXIM OF THE UNSTOPPABLES' CODE!\"\r\n\r\n"
            "ALL FIVE HEROES IN UNISON:\r\n"
            "\"BRAINS BEAT BRAWN WHEN HEROES STAND UNITED!\"\r\n\r\n"
            "[Clara Sterling's handwritten note at the footer]:\r\n"
            "\"My favorite line in the entire series! Grab the third Photonic Coil off WRVR's roof "
            "and recite that exact maxim to Colonel Gutsy to unlock the Ray Carbine.\""
        ),
    ),
    (
        0x01001162,
        "BookOrbita7Cosmos50Draft",
        "Censored Draft: Captain Cosmos Special #50",
        (
            "HUBRIS COMICS — UNCUT ORIGINAL SCRIPT (CLARA STERLING'S COPY)\r\n"
            "Title: 'Captain Cosmos Special #50: Siege from the Black Star!'\r\n\r\n"
            "OFFICIAL SYNOPSIS:\r\n"
            "From his dreadnought in the outer nebula, the ruthless galactic tyrant known as "
            "'EMPEROR QUASAR' unleashes a lethal radiation storm to scorch Earth's atmosphere.\r\n\r\n"
            "To breach the atomic firestorm without a scratch, Captain Cosmos dons his titanic "
            "Orbital Power Armor equipped with the legendary 'TOTAL COSMIC IMMUNITY SHIELD AGAINST "
            "RADIATION', co-developed in the real world with engineers at ArcJet Systems.\r\n\r\n"
            "[Clara's note]: \"The Pentagon tried to redact this issue because it described our real "
            "prototype specs too accurately. Remember 'Emperor Quasar' and the 'Total Cosmic Immunity "
            "Shield against radiation' at the Colonel's console.\""
        ),
    ),
    (
        0x01001163,
        "BookOrbita7StudioDeed",
        "Deed of Stewardship: Underground Studio Orbit-7",
        (
            "DEED OF PERPETUAL STEWARDSHIP — UNDERGROUND STUDIO ORBIT-7\r\n"
            "Granted by: Dr. Arthur 'Artie' Vance & Colonel Gutsy 'Cosmos'\r\n\r\n"
            "This instrument certifies that the bearer has passed all four tiers of the True "
            "Believer Protocol with honor, united all four aerospace prototypes of Project "
            "Astro-Cosmos, and fulfilled Clara Sterling's final wish.\r\n\r\n"
            "From this day forward, all of Underground Studio Orbit-7—including the Director's "
            "Quarters with Captain Cosmos's Spacer Bed, safe Star Chests, the Orbital Hangar, and "
            "every engineering workbench—is vested in the bearer as a Permanent Sanctuary.\r\n\r\n"
            "\"FOR TRUTH, THE STARS, AND TOMORROW!\""
        ),
    ),
]

QUEST_STAGES = [
    (
        15,
        0,
        "My Pip-Boy intercepted a shortwave signal from Arthur 'Artie' Vance, former Hubris Comics aerospace engineer, broadcasting from Underground Studio Orbit-7. I should look for the armored hatch in the back alley behind Hubris Comics and head downstairs.",
    ),
    (
        20,
        0,
        "Artie Vance welcomed me to Underground Studio Orbit-7. To convince the loudmouthed Colonel Gutsy 'Cosmos' to unlock the Astro-Cosmos Flight Suit bay, I need to examine three clues across the Rotunda and Writers' Room (the Captain Cosmos #1 Showcase, Clara Sterling's Drafting Desk, and the TV Production Terminal) and pass the Recruit Exam at the central console.",
    ),
    (
        30,
        0,
        "I passed Colonel Gutsy's Recruit Exam! The photonic barrier on Stasis Bay One has powered down, so I can claim the Astro-Cosmos Flight Suit.",
    ),
    (
        35,
        0,
        "The Astro-Cosmos Flight Suit is in my hands. I should equip it and talk to Artie Vance about the next prototype.",
    ),
    (
        40,
        0,
        "To reactivate the Astro-Cosmos Ray Carbine pedestal, I need to use the Suit's flight thrusters to reach three high Boston rooftops—Hubris Comics' upper roof, Trinity Plaza's elevated terrace, and WRVR Radio's rooftop—recover the three Photonic Coils, and read the clues Clara Sterling left behind.",
    ),
    (
        50,
        0,
        "I've gathered all three Photonic Coils across Boston's skyline along with Clara's first holotape and The Unstoppables dossiers. Time to return to Orbit-7 and take Colonel Gutsy's Aerial Patrol Exam.",
    ),
    (
        60,
        0,
        "Second exam cleared! Colonel Gutsy dropped the Photonic Lab shield, leaving the Astro-Cosmos Ray Carbine open for pickup.",
    ),
    (
        65,
        0,
        "I'm armed with the Astro-Cosmos Ray Carbine, tuned for mid-flight shooting with a 6x recon scope. Next, I should speak with Artie Vance to launch Operation Star Titan.",
    ),
    (
        70,
        0,
        "Artie needs the Synchrotron Core locked on the upper exterior roof of ArcJet Systems to unseal the North Orbital Hangar. I must fly up to ArcJet's roof, clear the security bots from the air with my Carbine, and retrieve the Core and Clara's clues.",
    ),
    (
        80,
        0,
        "I recovered the Synchrotron Core, Clara Sterling's second holotape, and the censored draft of Captain Cosmos Special #50 on ArcJet Systems' roof. Time to head back to Orbit-7 for the Orbital Pilot Exam.",
    ),
    (
        100,
        0,
        "The blast barriers of the North Orbital Hangar are wide open! The full Astro-Cosmos Power Armor awaits on its orbital gantry.",
    ),
    (
        110,
        0,
        "I claimed the towering Astro-Cosmos Power Armor with integrated sustained-flight thrusters. I should talk to Artie Vance about Clara Sterling's final mystery and the Solar Reliquary.",
    ),
    (
        120,
        0,
        "Artie unsealed the Director's Projection Suite in the southeast wing of the studio. I need to memorize the Supreme Oath on its Grand Mural, then fly with my Power Armor to Fort Hagen's satellite roof to retrieve Clara Sterling's Master Star Card and final recording.",
    ),
    (
        140,
        0,
        "I recovered the Master Star Card and listened to Clara Sterling's final holotape from October 23, 2077. Now I'll return to Studio Orbit-7 to face Colonel Gutsy's Master Exam for the title of Captain of the Cosmos.",
    ),
    (
        160,
        0,
        "Colonel Gutsy awarded me the rank of Captain of the Cosmos and unlocked the North Hangar's Solar Reliquary! I can now claim the Astro-Cosmos Orbital Gauss Cannon.",
    ),
    (
        165,
        0,
        "The Astro-Cosmos Orbital Gauss Cannon is mine. I should speak with Artie Vance to celebrate completing Clara Sterling's legacy.",
    ),
    (
        200,
        1,
        "I united all four Astro-Cosmos prototypes and honored Clara Sterling's dying wish. Artie Vance and Colonel Gutsy granted me permanent stewardship of Underground Studio Orbit-7 as my safe home base beneath downtown Boston.",
    ),
]

QUEST_OBJECTIVES = [
    (15, "Check the Orbit-7 hatch behind Hubris Comics and talk to Artie Vance", 0),
    (20, "Inspect the 3 studio clues and pass the Recruit Exam at the console", 3),
    (30, "Claim the Astro-Cosmos Flight Suit from its stasis pod", 4),
    (35, "Equip the Astro-Cosmos Flight Suit and speak with Artie Vance", 0),
    (41, "Fly atop Hubris Comics and recover Photonic Coil #1", 5),
    (42, "Fly to Trinity Plaza's elevated terrace and recover Photonic Coil #2", 6),
    (43, "Fly to WRVR Radio's rooftop and recover Photonic Coil #3", 7),
    (50, "Review the recovered clues and pass the Aerial Patrol Exam in Orbit-7", 3),
    (60, "Claim the Astro-Cosmos Ray Carbine in the Photonic Lab", 8),
    (65, "Speak with Artie Vance to begin Operation Star Titan", 0),
    (70, "Fly to ArcJet Systems' upper roof and recover the Synchrotron Core", 9),
    (80, "Review the ArcJet clues and pass the Orbital Pilot Exam in Orbit-7", 3),
    (100, "Enter the North Orbital Hangar and claim the Astro-Cosmos Power Armor", 10),
    (110, "Talk to Artie Vance about Clara Sterling's final fate", 0),
    (121, "Inspect the Grand Star Guard Mural in the Director's Suite", 11),
    (122, "Fly to Fort Hagen's satellite roof and recover the Master Star Card", 12),
    (140, "Play Clara's Holotape #3 and pass the Master Exam in Orbit-7", 3),
    (160, "Claim the Astro-Cosmos Orbital Gauss Cannon from the Solar Reliquary", 13),
    (165, "Speak with Artie Vance to receive permanent keys to Studio Orbit-7", 0),
]

# ==============================================================================
# 7. SHRILL CAMP-MCCLINTOCK COLONEL GUTSY EXAM VOICES & SFX (UI / MENU-SAFE)
# ==============================================================================
EXAM_AUDIO_VOICES = [
    # 12 Spoken Quiz Questions (SNDR 0x01001801..0x0100180C -> SOUN 0x01001901..0x0100190C)
    {
        "name": "orbita7_exam_q01",
        "sndr_fid": 0x01001801,
        "soun_fid": 0x01001901,
        "sndr_edid": "SNDROrbita7ExamQ01",
        "soun_edid": "SOUNOrbita7ExamQ01",
        "tts": "EYES FRONT AT THE CONSOLE, CLUMSY MAGGOT! Recruit Exam Question One! What is the name of Captain Cosmos's heroic simian co-pilot, and inside which lunar crater does his secret headquarters hide?!",
    },
    {
        "name": "orbita7_exam_q02",
        "sndr_fid": 0x01001802,
        "soun_fid": 0x01001902,
        "sndr_edid": "SNDROrbita7ExamQ02",
        "soun_edid": "SOUNOrbita7ExamQ02",
        "tts": "QUESTION TWO, WORM! According to Clara Sterling's official drafting table, what is the exact three-color scheme of the regulation Astro-Cosmos uniform?!",
    },
    {
        "name": "orbita7_exam_q03",
        "sndr_fid": 0x01001803,
        "soun_fid": 0x01001903,
        "sndr_edid": "SNDROrbita7ExamQ03",
        "soun_edid": "SOUNOrbita7ExamQ03",
        "tts": "THIRD AND FINAL QUESTION FOR THE SUIT, ROOKIE! Per the T.V. Production Terminal, what exact date and station were locked in for Captain Cosmos's grand television premiere?!",
    },
    {
        "name": "orbita7_exam_q04",
        "sndr_fid": 0x01001804,
        "soun_fid": 0x01001904,
        "sndr_edid": "SNDROrbita7ExamQ04",
        "soun_edid": "SOUNOrbita7ExamQ04",
        "tts": "ATTENTION IN THE BARRACKS, FLYING CADET! Aerial Patrol Question One! Alongside the Silver Shroud, Grognak, Manta Man, and Mistress of Mystery, who completes the five founding members of The Unstoppables?!",
    },
    {
        "name": "orbita7_exam_q05",
        "sndr_fid": 0x01001805,
        "soun_fid": 0x01001905,
        "sndr_edid": "SNDROrbita7ExamQ05",
        "soun_edid": "SOUNOrbita7ExamQ05",
        "tts": "PATROL QUESTION TWO, BUTTERFINGERS! According to the Editorial Dossier recovered at Trinity Plaza, who is Grognak the Barbarian's sworn arch-nemesis?!",
    },
    {
        "name": "orbita7_exam_q06",
        "sndr_fid": 0x01001806,
        "soun_fid": 0x01001906,
        "sndr_edid": "SNDROrbita7ExamQ06",
        "soun_edid": "SOUNOrbita7ExamQ06",
        "tts": "QUESTION THREE TO UNLOCK THE RAY CARBINE! Per the radio script from station W. R. V. R., what is the Golden Maxim of The Unstoppables' Code?!",
    },
    {
        "name": "orbita7_exam_q07",
        "sndr_fid": 0x01001807,
        "soun_fid": 0x01001907,
        "sndr_edid": "SNDROrbita7ExamQ07",
        "soun_edid": "SOUNOrbita7ExamQ07",
        "tts": "SQUARE YOUR SHOULDERS, STAR TITAN CANDIDATE! Orbital Pilot Question One! Which Boston aerospace contractor secretly built the twin sustained-flight thrusters on the Astro-Cosmos Power Armor?!",
    },
    {
        "name": "orbita7_exam_q08",
        "sndr_fid": 0x01001808,
        "soun_fid": 0x01001908,
        "sndr_edid": "SNDROrbita7ExamQ08",
        "soun_edid": "SOUNOrbita7ExamQ08",
        "tts": "ORBITAL QUESTION TWO, RECRUIT! In the censored draft of Captain Cosmos Special Number Fifty, which galactic tyrant attempts to scorch Earth with radiation storms?!",
    },
    {
        "name": "orbita7_exam_q09",
        "sndr_fid": 0x01001809,
        "soun_fid": 0x01001909,
        "sndr_edid": "SNDROrbita7ExamQ09",
        "soun_edid": "SOUNOrbita7ExamQ09",
        "tts": "QUESTION THREE TO UNSEAL THE POWER ARMOR HANGAR! Beyond continuous flight, what legendary defense is built into the Astro-Cosmos Torso in both Issue Fifty and our real prototype?!",
    },
    {
        "name": "orbita7_exam_q10",
        "sndr_fid": 0x0100180A,
        "soun_fid": 0x0100190A,
        "sndr_edid": "SNDROrbita7ExamQ10",
        "soun_edid": "SOUNOrbita7ExamQ10",
        "tts": "SILENCE ACROSS THE WHOLE COMPANY! Master Exam Question One! What is the Supreme Oath engraved beneath the Grand Mural in the Director's Suite?!",
    },
    {
        "name": "orbita7_exam_q11",
        "sndr_fid": 0x0100180B,
        "soun_fid": 0x0100190B,
        "sndr_edid": "SNDROrbita7ExamQ11",
        "soun_edid": "SOUNOrbita7ExamQ11",
        "tts": "SUPREME QUESTION TWO, SOLDIER! Per Clara Sterling's final transmission from Fort Hagen, what caliber ammunition does the Astro-Cosmos Orbital Gauss Cannon accelerate?!",
    },
    {
        "name": "orbita7_exam_q12",
        "sndr_fid": 0x0100180C,
        "soun_fid": 0x0100190C,
        "sndr_edid": "SNDROrbita7ExamQ12",
        "soun_edid": "SOUNOrbita7ExamQ12",
        "tts": "FINAL QUESTION FOR THE RANK OF CAPTAIN OF THE COSMOS! As the bombs fell on October twenty-third, twenty seventy-seven, what was Clara Sterling's dying wish when she saved Orbit Seven?!",
    },
    # 12 Sarcastic Individual Hit Responses (SNDR 0x01001811..0x0100181C -> SOUN 0x01001911..0x0100191C)
    {
        "name": "orbita7_exam_hit01",
        "sndr_fid": 0x01001811,
        "soun_fid": 0x01001911,
        "sndr_edid": "SNDROrbita7ExamHit01",
        "soun_edid": "SOUNOrbita7ExamHit01",
        "tts": "WELL SLAP MY CHASSIS! You actually got one right without moving your lips when you read! Don't tell me that puddle of irradiated mush in your skull finally sparked a synapse!",
    },
    {
        "name": "orbita7_exam_hit02",
        "sndr_fid": 0x01001812,
        "soun_fid": 0x01001912,
        "sndr_edid": "SNDROrbita7ExamHit02",
        "soun_edid": "SOUNOrbita7ExamHit02",
        "tts": "CORRECT! Amazing, recruit! Even a busted atomic clock tells the right time right before it detonates! Don't go expecting miracles on the next one!",
    },
    {
        "name": "orbita7_exam_hit03",
        "sndr_fid": 0x01001813,
        "soun_fid": 0x01001913,
        "sndr_edid": "SNDROrbita7ExamHit03",
        "soun_edid": "SOUNOrbita7ExamHit03",
        "tts": "HOT DAMN, YOU HIT THE MARK! Was that actual photographic recall, or did you slam your forehead into the keyboard and get lucky?!",
    },
    {
        "name": "orbita7_exam_hit04",
        "sndr_fid": 0x01001814,
        "soun_fid": 0x01001914,
        "sndr_edid": "SNDROrbita7ExamHit04",
        "soun_edid": "SOUNOrbita7ExamHit04",
        "tts": "AFFIRMATIVE! Mark the date in the Congressional Record: a wasteland scavenger just demonstrated third-grade reading comprehension! You almost got me leaking hydraulic fluid!",
    },
    {
        "name": "orbita7_exam_hit05",
        "sndr_fid": 0x01001815,
        "soun_fid": 0x01001915,
        "sndr_edid": "SNDROrbita7ExamHit05",
        "soun_edid": "SOUNOrbita7ExamHit05",
        "tts": "VALID ANSWER! Easy there, professor—don't puff out your chest yet! Even a blind radscorpion stumbles onto a bottlecap if it bangs its claws around long enough!",
    },
    {
        "name": "orbita7_exam_hit06",
        "sndr_fid": 0x01001816,
        "soun_fid": 0x01001916,
        "sndr_edid": "SNDROrbita7ExamHit06",
        "soun_edid": "SOUNOrbita7ExamHit06",
        "tts": "BINGO, WISEGUY! Somebody's actually been reading the showcases instead of rooting through dumpsters for bent tin cans! Let's see how long that lucky streak holds!",
    },
    {
        "name": "orbita7_exam_hit07",
        "sndr_fid": 0x01001817,
        "soun_fid": 0x01001917,
        "sndr_edid": "SNDROrbita7ExamHit07",
        "soun_edid": "SOUNOrbita7ExamHit07",
        "tts": "BULLSEYE, RECRUIT! Back at Camp McClintock I saw bloatflies pop a range target with more conviction than you, but the point goes on the board!",
    },
    {
        "name": "orbita7_exam_hit08",
        "sndr_fid": 0x01001818,
        "soun_fid": 0x01001918,
        "sndr_edid": "SNDROrbita7ExamHit08",
        "soun_edid": "SOUNOrbita7ExamHit08",
        "tts": "REGULATION HIT! Hold your horses before asking for a Silver Star, sweetheart! Even a two-headed brahmin figures out which bucket holds the feed when its belly's empty!",
    },
    {
        "name": "orbita7_exam_hit09",
        "sndr_fid": 0x01001819,
        "soun_fid": 0x01001919,
        "sndr_edid": "SNDROrbita7ExamHit09",
        "soun_edid": "SOUNOrbita7ExamHit09",
        "tts": "POINT FOR THE CANDIDATE! Who knows—two or three centuries from now you might even make Private First Class in charge of orbital latrines!",
    },
    {
        "name": "orbita7_exam_hit10",
        "sndr_fid": 0x0100181A,
        "soun_fid": 0x0100191A,
        "sndr_edid": "SNDROrbita7ExamHit10",
        "soun_edid": "SOUNOrbita7ExamHit10",
        "tts": "DEAD ON! Somebody log this seismic miracle in the flight recorder: this recruit's lone surviving brain cell just located a second friend!",
    },
    {
        "name": "orbita7_exam_hit11",
        "sndr_fid": 0x0100181B,
        "soun_fid": 0x0100191B,
        "sndr_edid": "SNDROrbita7ExamHit11",
        "soun_edid": "SOUNOrbita7ExamHit11",
        "tts": "SHARP EYES, CARDBOARD SOLDIER! For half a second you sounded like those fresh-faced West Virginia cadets right before they belly-flopped into the Camp McClintock mud pit!",
    },
    {
        "name": "orbita7_exam_hit12",
        "sndr_fid": 0x0100181C,
        "soun_fid": 0x0100191C,
        "sndr_edid": "SNDROrbita7ExamHit12",
        "soun_edid": "SOUNOrbita7ExamHit12",
        "tts": "RIGHT IN THE X-RING! Witness a true miracle of American evolution: a wastelander who actually bothered to read the fine print!",
    },
    # 16 Blistering Camp McClintock Drill-Sergeant Failure Tirades (SNDR 0x01001821..0x01001830 -> SOUN 0x01001921..0x01001930)
    {
        "name": "orbita7_exam_fail01",
        "sndr_fid": 0x01001821,
        "soun_fid": 0x01001921,
        "sndr_edid": "SNDROrbita7ExamFail01",
        "soun_edid": "SOUNOrbita7ExamFail01",
        "tts": "COLOSSAL SCREW-UP, MAGGOT! With intellectual aim that pitiful you couldn't hit water if you fell out of a rowboat! Quiz terminated and wiped to zero—try using your eyeballs next time, genius!",
    },
    {
        "name": "orbita7_exam_fail02",
        "sndr_fid": 0x01001822,
        "soun_fid": 0x01001922,
        "sndr_edid": "SNDROrbita7ExamFail02",
        "soun_edid": "SOUNOrbita7ExamFail02",
        "tts": "DEAD WRONG, DIRTBAG! I've interrogated burnt Pre-War toasters with sharper memory circuits than yours! March right back to those showcases and sound out every syllable nice and slow—it's free!",
    },
    {
        "name": "orbita7_exam_fail03",
        "sndr_fid": 0x01001823,
        "soun_fid": 0x01001923,
        "sndr_edid": "SNDROrbita7ExamFail03",
        "soun_edid": "SOUNOrbita7ExamFail03",
        "tts": "BUZZER! WRONG! Do you even know how to read English, soldier, or are you just mashing glowing keys because pretty lights make you giggle?! Whole quiz voided! Back to square one!",
    },
    {
        "name": "orbita7_exam_fail04",
        "sndr_fid": 0x01001824,
        "soun_fid": 0x01001924,
        "sndr_edid": "SNDROrbita7ExamFail04",
        "soun_edid": "SOUNOrbita7ExamFail04",
        "tts": "BIG FAT ZERO! A breathtaking trainwreck! You just rewrote forty years of Hubris Comics canon through sheer radioactive ignorance! Step to the back of the line and start over, champ!",
    },
    {
        "name": "orbita7_exam_fail05",
        "sndr_fid": 0x01001825,
        "soun_fid": 0x01001925,
        "sndr_edid": "SNDROrbita7ExamFail05",
        "soun_edid": "SOUNOrbita7ExamFail05",
        "tts": "WRONG, DEAD WRONG, KNUCKLEHEAD! If boneheadedness generated wattage, your skull alone could light up all of Boston for a century! Keep your mitts off my prototypes and restart!",
    },
    {
        "name": "orbita7_exam_fail06",
        "sndr_fid": 0x01001826,
        "soun_fid": 0x01001926,
        "sndr_edid": "SNDROrbita7ExamFail06",
        "soun_edid": "SOUNOrbita7ExamFail06",
        "tts": "HISTORIC DISASTER! The sheer nerve of strutting up to pilot aerospace hardware when you can't remember three sentences from a folder! Get lost and go study your ABCs!",
    },
    {
        "name": "orbita7_exam_fail07",
        "sndr_fid": 0x01001827,
        "soun_fid": 0x01001927,
        "sndr_edid": "SNDROrbita7ExamFail07",
        "soun_edid": "SOUNOrbita7ExamFail07",
        "tts": "WHAT AN ABSOLUTE DISGRACE TO UNCLE SAM'S TITANIUM! A squad of one-armed yao guai could clear Camp McClintock's obstacle course faster than you can answer three kindergarten trivia questions! BACK OF THE LINE!",
    },
    {
        "name": "orbita7_exam_fail08",
        "sndr_fid": 0x01001828,
        "soun_fid": 0x01001928,
        "sndr_edid": "SNDROrbita7ExamFail08",
        "soun_edid": "SOUNOrbita7ExamFail08",
        "tts": "DROP AND GIVE ME FIFTY PUSH-UPS IN THE DIRT, YOU SLACKER! You just mixed up official Hubris lore with somebody's grocery list! Quiz reset to zero—NOW MOVE!",
    },
    {
        "name": "orbita7_exam_fail09",
        "sndr_fid": 0x01001829,
        "soun_fid": 0x01001929,
        "sndr_edid": "SNDROrbita7ExamFail09",
        "soun_edid": "SOUNOrbita7ExamFail09",
        "tts": "CONGRATULATIONS, PRIVATE—WELCOME TO THE ORBIT-SEVEN LATRINE DETAIL! With retention that rotten I wouldn't trust you to squeegee bug guts off a busted Vertibird windshield! Start over from scratch!",
    },
    {
        "name": "orbita7_exam_fail10",
        "sndr_fid": 0x0100182A,
        "soun_fid": 0x0100192A,
        "sndr_edid": "SNDROrbita7ExamFail10",
        "soun_edid": "SOUNOrbita7ExamFail10",
        "tts": "CEASE FIRE, YOU WALKING CATASTROPHE! My geriatric Aunt Gertrude in her bathrobe wielding a broomstick has sharper tactical judgment than your empty cranium! Rewind to square one!",
    },
    {
        "name": "orbita7_exam_fail11",
        "sndr_fid": 0x0100182B,
        "soun_fid": 0x0100192B,
        "sndr_edid": "SNDROrbita7ExamFail11",
        "soun_edid": "SOUNOrbita7ExamFail11",
        "tts": "THIS IS RED-COMMUNIST SABOTAGE AGAINST BASIC LITERACY! Did you crawl down here to honor Hubris Comics or mash random keys like a mutant mole rat having a seizure?! GET OUT OF MY SIGHT!",
    },
    {
        "name": "orbita7_exam_fail12",
        "sndr_fid": 0x0100182C,
        "soun_fid": 0x0100192C,
        "sndr_edid": "SNDROrbita7ExamFail12",
        "soun_edid": "SOUNOrbita7ExamFail12",
        "tts": "THANK GOD ALMIGHTY WE AREN'T USING LIVE AMMO LIKE THE WEST VIRGINIA FIRING RANGE! By now you'd have blown up the chow hall, every target dummy, and Old Glory herself! TRY AGAIN, SLIMEBALL!",
    },
    {
        "name": "orbita7_exam_fail13",
        "sndr_fid": 0x0100182D,
        "soun_fid": 0x0100192D,
        "sndr_edid": "SNDROrbita7ExamFail13",
        "soun_edid": "SOUNOrbita7ExamFail13",
        "tts": "GALACTIC-CLASS FAILURE! If I were a flesh-and-blood drill sergeant I'd be having a coronary right now—luckily I'm pure patriotic steel, so I'll just wipe your score and laugh right in your face!",
    },
    {
        "name": "orbita7_exam_fail14",
        "sndr_fid": 0x0100182E,
        "soun_fid": 0x0100192E,
        "sndr_edid": "SNDROrbita7ExamFail14",
        "soun_edid": "SOUNOrbita7ExamFail14",
        "tts": "GOD BLESS AMERICA, BECAUSE WITH YOUR MEMORY EVEN BLOODBUGS COULD INVADE BOSTON! Step back, go read the dossiers letter by letter, and don't return until your brain shows a pulse!",
    },
    {
        "name": "orbita7_exam_fail15",
        "sndr_fid": 0x0100182F,
        "soun_fid": 0x0100192F,
        "sndr_edid": "SNDROrbita7ExamFail15",
        "soun_edid": "SOUNOrbita7ExamFail15",
        "tts": "PATHETIC DOESN'T EVEN COVER IT, SCRAP-FOR-BRAINS! I practically spoon-fed you the answers on a silver platter and you STILL choked on the decoy choice! Back to the starting line!",
    },
    {
        "name": "orbita7_exam_fail16",
        "sndr_fid": 0x01001830,
        "soun_fid": 0x01001930,
        "sndr_edid": "SNDROrbita7ExamFail16",
        "soun_edid": "SOUNOrbita7ExamFail16",
        "tts": "DISMISSED, YOU COSMIC CLOWN! Tomorrow morning you're polishing my jet nozzles with a toothbrush before I ever let you near this keyboard again! GO READ THE CLUES!",
    },
    # 12 Grudging, Ironic Victory Rants (3 per exam: SNDR 0x01001831..34 + 0x01001851..58)
    {
        "name": "orbita7_exam_win01",
        "sndr_fid": 0x01001831,
        "soun_fid": 0x01001931,
        "sndr_edid": "SNDROrbita7ExamWin01",
        "soun_edid": "SOUNOrbita7ExamWin01",
        "tts": "THREE FOR THREE! STOP THE PRESSES! Turns out there was something inside that dusty helmet besides sawdust! Barrier One deactivated—go strut around in your shiny Astro-Cosmos Flight Suit, discount superstar!",
    },
    {
        "name": "orbita7_exam_win02",
        "sndr_fid": 0x01001832,
        "soun_fid": 0x01001932,
        "sndr_edid": "SNDROrbita7ExamWin02",
        "soun_edid": "SOUNOrbita7ExamWin02",
        "tts": "MIRACULOUS CLEAN SWEEP! Who knew you could string three correct answers together without forgetting how to breathe?! Lab gate unlocked—grab that Ray Carbine and try not to shoot your own boots off!",
    },
    {
        "name": "orbita7_exam_win03",
        "sndr_fid": 0x01001833,
        "soun_fid": 0x01001933,
        "sndr_edid": "SNDROrbita7ExamWin03",
        "soun_edid": "SOUNOrbita7ExamWin03",
        "tts": "THREE OUT OF THREE! My cooling fans just iced over in shock, cadet! You proved marginally smarter than a brahmin wearing combat boots! North Hangar open—climb into that Astro-Cosmos Power Armor!",
    },
    {
        "name": "orbita7_exam_win04",
        "sndr_fid": 0x01001834,
        "soun_fid": 0x01001934,
        "sndr_edid": "SNDROrbita7ExamWin04",
        "soun_edid": "SOUNOrbita7ExamWin04",
        "tts": "THREE FOR THREE ON THE SUPREME EXAM! Pinch my pincers—I just promoted a wasteland drifter to Captain of the Cosmos! The Solar Reliquary and Orbital Gauss Cannon are yours... try not to vaporize downtown Boston!",
    },
    {
        "name": "orbita7_exam_win05",
        "sndr_fid": 0x01001851,
        "soun_fid": 0x01001951,
        "sndr_edid": "SNDROrbita7ExamWin05",
        "soun_edid": "SOUNOrbita7ExamWin05",
        "tts": "RECRUIT TRIAL PASSED BY THE SKIN OF YOUR TEETH! Don't pin any medals on yet, birdbrain! In that bright cobalt Flight Suit you'll look like a carnival balloon begging to be shot down from rooftops!",
    },
    {
        "name": "orbita7_exam_win06",
        "sndr_fid": 0x01001852,
        "soun_fid": 0x01001952,
        "sndr_edid": "SNDROrbita7ExamWin06",
        "soun_edid": "SOUNOrbita7ExamWin06",
        "tts": "EXAM ONE CLEARED BY PURE DIVINE INTERVENTION! In my boot camp days we'd make you sprint laps strapping a washing machine to your spine, but the Flight Suit is yours! Try not to dent my ceiling!",
    },
    {
        "name": "orbita7_exam_win07",
        "sndr_fid": 0x01001853,
        "soun_fid": 0x01001953,
        "sndr_edid": "SNDROrbita7ExamWin07",
        "soun_edid": "SOUNOrbita7ExamWin07",
        "tts": "SECOND EXAM PASSED, FAIR-WEATHER FLYBOY! Photonic pedestal unlocked! Go grab that Ray Carbine and let's see if you can hit anything from the clouds smaller than a barn door!",
    },
    {
        "name": "orbita7_exam_win08",
        "sndr_fid": 0x01001854,
        "soun_fid": 0x01001954,
        "sndr_edid": "SNDROrbita7ExamWin08",
        "soun_edid": "SOUNOrbita7ExamWin08",
        "tts": "THREE FOR THREE ON AERIAL PATROL! Who'd have guessed between leaping across rooftops like an alley cat you actually memorized The Unstoppables' Code?! Ray Carbine unlocked, recruit!",
    },
    {
        "name": "orbita7_exam_win09",
        "sndr_fid": 0x01001855,
        "soun_fid": 0x01001955,
        "sndr_edid": "SNDROrbita7ExamWin09",
        "soun_edid": "SOUNOrbita7ExamWin09",
        "tts": "THIRD EXAM PASSED WITH FLYING COLORS... OR FREAKISH DUMB LUCK! Haul your sorry carcass into the North Hangar and strap on that Orbital Power Armor—and DON'T squish Artie on the way out!",
    },
    {
        "name": "orbita7_exam_win10",
        "sndr_fid": 0x01001856,
        "soun_fid": 0x01001956,
        "sndr_edid": "SNDROrbita7ExamWin10",
        "soun_edid": "SOUNOrbita7ExamWin10",
        "tts": "TOTAL MASTERY OF HEAVY ENGINEERING! Damn it, you're starting to remind me of the finest grunts at Camp McClintock—the three who didn't face-plant in the mud after two seconds! Power Armor released!",
    },
    {
        "name": "orbita7_exam_win11",
        "sndr_fid": 0x01001857,
        "soun_fid": 0x01001957,
        "sndr_edid": "SNDROrbita7ExamWin11",
        "soun_edid": "SOUNOrbita7ExamWin11",
        "tts": "PRESENT ARMS, EVERYBODY! We just crowned a brand-new Captain of the Cosmos without a single terminal capacitor exploding! Take the Orbital Gauss Cannon from the Solar Reliquary and make those lunar Commies cry lead!",
    },
    {
        "name": "orbita7_exam_win12",
        "sndr_fid": 0x01001858,
        "soun_fid": 0x01001958,
        "sndr_edid": "SNDROrbita7ExamWin12",
        "soun_edid": "SOUNOrbita7ExamWin12",
        "tts": "SUMMA CUM LAUDE ON THE MASTER EXAM, SIR! Not even the Commanding General at Camp McClintock withstood that much sarcasm without quitting the podium! The Gauss Cannon and Orbit Seven are all yours, Captain!",
    },
    # 4 Ironic Retreat Taunts (SNDR 0x01001835 + 0x01001861..63)
    {
        "name": "orbita7_exam_retreat",
        "sndr_fid": 0x01001835,
        "soun_fid": 0x01001935,
        "sndr_edid": "SNDROrbita7ExamRetreat",
        "soun_edid": "SOUNOrbita7ExamRetreat",
        "tts": "Aha! Tactical retreat! Surprisingly sensible call—better to go peek at the studio clues now than keep humiliating yourself in prime time!",
    },
    {
        "name": "orbita7_exam_retreat02",
        "sndr_fid": 0x01001861,
        "soun_fid": 0x01001961,
        "sndr_edid": "SNDROrbita7ExamRetreat02",
        "soun_edid": "SOUNOrbita7ExamRetreat02",
        "tts": "STRATEGIC BUG-OUT BEFORE BLOWING A FUSE! Smart move, recruit—scurry back to those showcases before I run out of regulation insults in my vocabulary bank!",
    },
    {
        "name": "orbita7_exam_retreat03",
        "sndr_fid": 0x01001862,
        "soun_fid": 0x01001962,
        "sndr_edid": "SNDROrbita7ExamRetreat03",
        "soun_edid": "SOUNOrbita7ExamRetreat03",
        "tts": "THROWING IN THE TOWEL ALREADY?! At Camp McClintock you at least ran until you collapsed—though reading those folders beats watching you crash and burn again!",
    },
    {
        "name": "orbita7_exam_retreat04",
        "sndr_fid": 0x01001863,
        "soun_fid": 0x01001963,
        "sndr_edid": "SNDROrbita7ExamRetreat04",
        "soun_edid": "SOUNOrbita7ExamRetreat04",
        "tts": "ADMITTING YOU DON'T KNOW JACK IS A SOLDIER'S FIRST STEP! Open BOTH eyes, read Clara's notes carefully, and come back ready to pass!",
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
