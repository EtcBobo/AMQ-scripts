#!/usr/bin/env python3
"""
Game Mode Roller - Final Version
- 4v4 bias for Watched Team
- No duplicate game settings across any rounds
- User's allowed_S restrictions preserved
- Player list mode with player selection
- Mastery modes (OPs, EDs, INs, OPEDs, OPINs, EDINs, OPEDINS - all "DNGMC"):
    * each mastery MODE can only appear once across all rounds
    * each has 3 difficulties (Novice / Intermediate / Full), rolled AFTER the player count:
        Novice       -> 1v1 or 2v2
        Intermediate -> 2v2, 3v3 or 4v4
        Full         -> 3v3 or 4v4
    * difficulties are reusable across rounds (only the mode itself is once-only)
- Novice Ranked DNGMC is no longer a mastery mode (it can't roll a difficulty), but is still once-only
- TOP X Random only appears once across all rounds, and is 2v2 only
- 4v4 Grand Prix is ONE entry (4v4 only, once across all rounds); its 8 variants and a Distance (Sprint/Mile/Medium/Long) are rolled only after it is picked
"""

import random
from typing import List, Dict, Tuple, Optional, Set

# ------------------------------------------------------------
# Player list: name -> (profile_url, status)
# status is either "Completed only" or "Watching and Completed"
# ------------------------------------------------------------
PLAYER_LIST: Dict[str, Tuple[str, str]] = {
    "SmartHardyz_": ("https://anilist.co/user/SmartHardyz/", "Completed only"),
    "ange": ("https://anilist.co/user/xAppuruPai/", "Watching and Completed"),
    "nage": ("https://anilist.co/user/nageboshi/", "Watching and Completed"),
    "Floth": ("https://myanimelist.net/profile/Monofly", "Completed only"),
    "Yonakax_": ("https://anilist.co/user/yonakaa/animelist", "Completed only"),
    "Chiabobo": ("https://myanimelist.net/animelist/Chiabobo", "Completed only"),
    "AngelAir": ("https://myanimelist.net/profile/RandomAir", "Completed only"),
    "zxphxr": ("https://myanimelist.net/profile/Zxphxr", "Completed only"),
    "Ireland": ("https://myanimelist.net/profile/IrishandProud", "Watching and Completed"),
    "bofu": ("https://anilist.co/user/bofu/", "Completed only"),
    "Almin41": ("https://anilist.co/user/Almin41/", "Watching and Completed"),
    "CM02": ("https://anilist.co/user/CM02/animelist", "Completed only"),
    "Luna": ("https://myanimelist.net/profile/LysiLuna", "Watching and Completed"),
    "SilenT": ("https://myanimelist.net/profile/SilenTo14", "Completed only"),
    "Tatsuya": ("https://myanimelist.net/profile/Dimension", "Watching and Completed"),
    "Tiut12": ("https://myanimelist.net/profile/Tutalien", "Watching and Completed"),
    "Death_Doc": ("https://myanimelist.net/animelist/DeathDoc", "Completed only"),
    "Soan": ("https://anilist.co/user/Soan30/stats/anime/tags", "Completed only"),
    "whales6978": ("https://anilist.co/user/Whales6978/", "Watching and Completed"),
    "YTK_Bowser": ("https://myanimelist.net/profile/YTK_Bowser", "Watching and Completed"),
    "martwyhuman": ("https://anilist.co/user/martwyhuman/", "Completed only"),
    "Rhummy": ("https://anilist.co/user/Rhummy/", "Completed only"),
    "PXMacaiah": ("https://myanimelist.net/profile/PXMacaiah", "Completed only"),
    "Piovia": ("https://myanimelist.net/profile/Piovia", "Watching and Completed"),
    "Erothaur": ("https://myanimelist.net/profile/Erothaur", "Watching and Completed"),
    "AmamiyaSora": ("https://myanimelist.net/profile/LightningRocks", "Watching and Completed"),
    "Conan": ("https://anilist.co/user/Conan48/animelist", "Watching and Completed"),
    "Thesuperhand": ("https://myanimelist.net/profile/Superhand0", "Watching and Completed"),
    "FumFum": ("https://anilist.co/user/FumFum/", "Watching and Completed"),
    "CipherKai": ("https://anilist.co/user/CipherKai/", "Watching and Completed"),
    "KuroT1": ("https://myanimelist.net/profile/KurohaneT1", "Watching and Completed"),
    "TheNoblesse": ("https://anilist.co/user/TheNoblesse/", "Watching and Completed"),
    "Minty": ("https://myanimelist.net/profile/MintyDude", "Completed only"),
    "Wyatt": ("https://myanimelist.net/profile/MoltenAshes", "Watching and Completed"),
}

# ------------------------------------------------------------
# Top-level modes: name -> (min_S, max_S, weight)
# ------------------------------------------------------------
TOP_LEVEL = {
    "Watched Game Modes (Team) 2v2-4v4": (2, 4, 3),
    "Pad Active Player List Modes": (2, 4, 1),
    "Watched Random Tag (Weighted)": (1, 1, 1),
    "Watched Random Genre (Weighted)": (1, 1, 1),
    "Watched Years (Weighted)": (1, 1, 1),
    # ---- Mastery modes: S range is the union of all difficulties (1-4).
    # The actual allowed S per difficulty lives in SUB_SETTINGS. ----
    "OPs Mastery DNGMC": (1, 4, 1),
    "EDs Mastery DNGMC": (1, 4, 1),
    "INs Mastery DNGMC": (1, 4, 1),
    "OPEDs Mastery DNGMC": (1, 4, 1),
    "OPINs Mastery DNGMC": (1, 4, 1),
    "EDINs Mastery DNGMC": (1, 4, 1),
    "OPEDINS Mastery DNGMC": (1, 4, 1),
    "Random Chanting": (2, 2, 1),
    "Novice Ranked DNGMC": (3, 4, 1),
    "TOP X Random (team vs team)": (2, 2, 1),
    "Random Tags/Genre: (1v1)": (1, 1, 1),
    "Female Artists/Male Artists": (1, 1, 1),
    "Groups": (1, 1, 1),
    "Franchise": (1, 1, 1),
    "Composers": (1, 1, 1),
    "Extras": (1, 1, 1),
}

SPECIAL_MODES = {
    "Female Artists/Male Artists",
    "Groups",
    "Franchise",
    "Composers",
    "Extras",
}

# Mastery modes: each rolls a difficulty (Novice / Intermediate / Full).
# Novice Ranked DNGMC is NOT part of this group (it has no difficulty to roll).
MASTERY_MODES = {
    "OPs Mastery DNGMC",
    "EDs Mastery DNGMC",
    "INs Mastery DNGMC",
    "OPEDs Mastery DNGMC",
    "OPINs Mastery DNGMC",
    "EDINs Mastery DNGMC",
    "OPEDINS Mastery DNGMC",
}

# Modes that can only appear ONCE across all rounds.
# Includes all mastery modes, Novice Ranked, Random Chanting and TOP X Random.
ONCE_ONLY_MODES = MASTERY_MODES | {
    "Novice Ranked DNGMC",
    "Random Chanting",
    "TOP X Random (team vs team)",
}

# Modes where sub-settings (difficulties) are reusable across rounds.
# Only the mode itself is restricted to once across all rounds.
# For these modes, the sub-setting uniqueness check is skipped.
REUSABLE_SUBSETTING_MODES = MASTERY_MODES | {"Novice Ranked DNGMC"}

# 4v4 Grand Prix is a single entry inside Watched Game Modes (Team). It can only be
# rolled once across all rounds (the normal (mode, sub-setting) uniqueness check
# handles that). Only after it has been picked do we roll one of its 8 variants.
GRAND_PRIX_NAME = "4v4 Grand Prix"
GRAND_PRIX_VARIANTS: List[Tuple[str, str]] = [
    ("Firm: OPs 0-100 - Equal Dist",
     "m0g1421111110111314000031000000001411111111111100k011o000000f352143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-111110a1--"),
    ("Firm: OPs 0-100 - Random Dist",
     "m0g1421111110111314000011000000001411111111111100k011o000000f352143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-111110a1--"),
    ("Good: OPEDs 0-100 - Equal Dist",
     "m0g1421111110111314000031100000001411111111111100k011o000000f352143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-111110a1--"),
    ("Good: OPEDs 0-100 - Random Dist",
     "m0g1421111110111314000011100000001411111111111100k011o000000f352143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-111110a1--"),
    ("Soft: OPEDINS 30-60 - Equal Dist",
     "m0g1421111110111314000031110000001411111111111100k011o000000f352143331110000k012r02i0a8c133a110u1o011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-111110a1--"),
    ("Soft: OPEDINS 30-60 - Random Dist",
     "m0g1421111110111314000011110000001411111111111100k011o000000f352143331110000k012r02i0a8c133a110u1o011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-111110a1--"),
    ("Heavy: OPEDINS 25-100 - Equal Dist",
     "m0g1421111110111314000031110000001411111111111100k011o000000f352143331110000k012r02i0a8c133a110p2s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-111110a1--"),
    ("Heavy: OPEDINS 25-100 - Random Dist",
     "m0g1421111110111314000011110000001411111111111100k011o000000f352143331110000k012r02i0a8c133a110p2s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-111110a1--"),
]

# Rolled separately from the variant whenever 4v4 Grand Prix is picked (equal odds).
GRAND_PRIX_DISTANCES: List[Tuple[str, int]] = [
    ("Sprint", 60),
    ("Mile", 70),
    ("Medium", 80),
    ("Long", 90),
]

# ------------------------------------------------------------
# Sub-settings (allowed_S exactly as you set them)
# ------------------------------------------------------------
SUB_SETTINGS: Dict[str, List[Tuple[str, Optional[Set[int]], str]]] = {
    "Watched Game Modes (Team) 2v2-4v4": [
        ("0-60 Watched INs Random Dist DNGMC", {3, 4},
         "m2s0k2111111011130k000011010000000k11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111001o1111002s01a111111111102a111111111050017pr11hg1ka03-11111--"),
        ("0-60 Watched OPs Random Dist DNGMC", {3, 4},
         "m2s0k2111111011130k000011000000000k11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111001o1111002s01a111111111102a111111111050017pr11hg1ka03-11111--"),
        ("0-60 Watched EDs Random Dist DNGMC", {3, 4},
         "m2s0k2111111011130k000010100000000k11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111001o1111002s01a111111111102a111111111050017pr11hg1ka03-11111--"),
        ("Watched 2+8 Random Dist (team mode)", {2, 3},
         "m2s0k3111111011130k000011110000000k111111111111002011o008000f152143331110000k012r02i0a8c133a11002s011111111111001o1111002s01a111111111102a111111111050017pr11hg1ka03-11111--"),
        ("OPs Start & End Samples (team mode)", {2}, "#6610"),
        ("INs Start & End Samples (team mode)", {2}, "#6614"),
        ("EDs Start & End Samples (team mode)", {2}, "#6612"),
        ("Watched Start & End Samples (team mode)", {2}, "#6543"),
        ("Snipaswap 2v2", {2},
         "m2s0k2111111011130k000011110101000i11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111001o1111002s01a111111111102a111111111050017pr11hg1ka03-11111--"),
        ("Raid Boss 4v4", {4},
         "m2s0k3111111011130k000011110000000k11111111111100k011o000000f452143331110000k012r02i0a8c533a11002s011111111111001o1111002s01a111111111102a111111111050017pr11hg1ka03-11111--"),
        ("Top 1k DNGMC", {2, 3},
         "m0g0k2111110010130k000011110000000k11111111101100k011o000000f152143331110000k012r02i0a8c533a11002s011111111111002s0111002s01a111111111102a111111111030017pr11hg1ka03-11111--"),
        ("Top 500 DNGMC", {2, 3},
         "m0g0k2111110010130k000011110000000k11111111101100k011o000000f152143331110000k012r02i0a8c533a11002s011111111111002s0111002s01a111111111102a111111111020017pr11hg1ka03-11111--"),
        ("Top 100 DNGMC", {2, 3},
         "m0g0k2111110010130k000011110000000k11111111101100k011o000000f152143331110000k012r02i0a8c533a11002s011111111111002s0111002s01a111111111102a111111111010017pr11hg1ka03-11111--"),
        ("Sonic Heroes", {3},
         "m080l3111110011130l000011110707070011111111111100k051o000000f152143331110000k012r02i0a46533a11002s011111111111001o0111002s01a111111111102a111111111050017pr11hg1ka03-11111--"),
        ("Guess time 5 seconds (Openings) 2v2", {2},
         "m0g0k4111110011130k000011000000000k111111111111005051o000000f152143331110000k012r02i0a46533a11002s011111111111002s0111002s01a111111111102a111111111050017pr11hg1ka03-11111--"),
        ("0-60 Watched NGMC 4v4", {4},
         "m0g0z2111111000130z000011110000000z11111111111100k011o000000f152143331110000k012r02i0a8c533a11002s011111111111001o0111002s01a111111111102a111111111050017pr11hg1ka03-11111--"),

        # ---- 4v4 Grand Prix: ONE entry here. The 8 variants live in GRAND_PRIX_VARIANTS
        # and are only rolled after this entry has been picked. ----
        (GRAND_PRIX_NAME, {4}, ""),
    ],

    "Pad Active Player List Modes": [
        ("Standard DNGMC", {3, 4},
         "m2s0k2111111011130k000011110101000i11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111001o1111002s01a111111111102a111111111050017pr11hg1ka03-11111--"),
        ("BR 2v2", {2},
         "m2s0k2111011011130k000011110101000i11111111111100k011o000000f1521433321100005012r02i0a8c133a11002s011111111111001o1111002s01a111111111102a111111111050017pr11hg1ka03-11111--"),
    ],

    "Watched Random Tag (Weighted)": [
        ("Idol", None, "m2s0k1111111011130k000021110101000i11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-11111-0371-"),
        ("Shounen", None, "m2s0k1111111011130k000021110101000i11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-11111-01k1-"),
        ("Isekai", None, "m2s0k1111111011130k000021110101000i11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-11111-06s1-"),
        ("Card Battle", None, "m2s0k1111111011130k000021110101000i11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-11111-04y1-"),
        ("Female Harem", None, "m2s0k1111111011130k000021110101000i11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-11111-00n1-"),
        ("Male Harem", None, "m2s0k1111111011130k000021110101000i11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-11111-03f1-"),
        ("CGDCT", None, "m2s0k1111111011130k000021110101000i11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-11111-02k1-"),
        ("CBDCT", None, "m2s0k1111111011130k000021110101000i11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-11111-0tj1-"),
        ("Shoujo", None, "m2s0k1111111011130k000021110101000i11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-11111-01h1-"),
        ("Yuri", None, "m2s0k1111111011130k000021110101000i11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-11111-0241-"),
        ("Yaoi", None, "m2s0k1111111011130k000021110101000i11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-11111-0231-"),
        ("Picked Tag (both players pick a tag each)", None,
         "m2s0k1111111011130k000021110101000i11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-11111-0231-"),
    ],

    "Watched Random Genre (Weighted)": [
        ("Music", None, "m2s0k1111111011130k000021110101000i11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-111110a1--"),
        ("Sports", None, "m2s0k1111111011130k000021110101000i11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-111110g1--"),
        ("Mecha", None, "m2s0k1111111011130k000021110101000i11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-11111091--"),
        ("Mahou Shoujo", None, "m2s0k1111111011130k000021110101000i11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-11111081--"),
        ("Ecchi", None, "m2s0k1111111011130k000021110101000i11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-11111051--"),
        ("Fantasy", None, "m2s0k1111111011130k000021110101000i11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-11111061--"),
        ("Slice of Life", None, "m2s0k1111111011130k000021110101000i11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-111110f1--"),
        ("Picked Genre (both players pick a genre each)", None,
         "m2s0k1111111011130k000021110101000i11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-111110f1--"),
    ],

    "Watched Years (Weighted)": [
        ("x - 2009", None, "m2s0k1111111011130k000021110000000k11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111002s1111001o01a111111111102a111111111050017pr01hg1jt03-11111--"),
        ("2010-2020", None, "m2s0k1111111011130k000021110000000k11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr01ju1k403-11111--"),
        ("2020+", None, "m2s0k1111111011130k000021110000000k11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr01k41ka03-11111--"),
        ("Picked Years (both players pick a year each)", None,
         "m2s0k1111111011130k000021110000000k11111111111100k011o000000f152143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr01k41ka03-11111--"),
    ],

    # ------------------------------------------------------------
    # Mastery modes. Difficulty (and its allowed player count) is
    # rolled AFTER the player count S is chosen:
    #   Novice       -> 1v1, 2v2
    #   Intermediate -> 2v2, 3v3, 4v4
    #   Full         -> 3v3, 4v4
    # Codes are the real mastery codes.
    # ------------------------------------------------------------
    "OPs Mastery DNGMC": [
        ("Novice", {1, 2}, "#5860"),
        ("Intermediate", {2, 3, 4}, "#5889"),
        ("Full", {3, 4}, "#9644"),
    ],

    "EDs Mastery DNGMC": [
        ("Novice", {1, 2}, "#5863"),
        ("Intermediate", {2, 3, 4}, "#5890"),
        ("Full", {3, 4}, "#9645"),
    ],

    "INs Mastery DNGMC": [
        ("Novice", {1, 2}, "#5866"),
        ("Intermediate", {2, 3, 4}, "#5891"),
        ("Full", {3, 4}, "#9646"),
    ],

    "OPEDs Mastery DNGMC": [
        ("Novice", {1, 2}, "#5917"),
        ("Intermediate", {2, 3, 4}, "#5920"),
        ("Full", {3, 4}, "#9647"),
    ],

    "OPINs Mastery DNGMC": [
        ("Novice", {1, 2}, "#5928"),
        ("Intermediate", {2, 3, 4}, "#5929"),
        ("Full", {3, 4}, "#9648"),
    ],

    "EDINs Mastery DNGMC": [
        ("Novice", {1, 2}, "#5932"),
        ("Intermediate", {2, 3, 4}, "#5933"),
        ("Full", {3, 4}, "#9649"),
    ],

    "OPEDINS Mastery DNGMC": [
        ("Novice", {1, 2}, "#5936"),
        ("Intermediate", {2, 3, 4}, "#5937"),
        ("Full", {3, 4}, "#9650"),
    ],

    "Random Chanting": [
        ("Random Chanting 0-100 OPEDINS (Team vs Team)", None,
         "m2s0k21111110111100000k11110000000k01000100010000k011o000000f152143331110000k012r02i0a8c133a11002s011111111111002s1111002s01a111111111102a111111111050017pr11hg1ka03-11111--"),
    ],

    "Novice Ranked DNGMC": [
        ("Novice Ranked DNGMC", None, "#10133"),
    ],

    "TOP X Random (team vs team)": [
        ("Top 1k (team vs team)", {2},
         "m0g0k21111100101100000k11110000000k10111011101100k051o000000f152143331110000k012r02i0a46533a11002s0111111111110u2s0111002s01a111111111102a111111111030017pr11hg1ka03-11111--"),
        ("Top 500 (team vs team)", {2},
         "m0g0k21111100101100000k11110000000k10111011101100k051o000000f152143331110000k012r02i0a46533a11002s0111111111110u2s0111002s01a111111111102a111111111020017pr11hg1ka03-11111--"),
        ("Top 100 (team vs team)", {2},
         "m0g0k21111100101100000k11110000000k10111011101100k051o000000f152143331110000k012r02i0a46533a11002s0111111111110u2s0111002s01a111111111102a111111111020017pr11hg1ka03-11111--"),
    ],


    "Random Tags/Genre: (1v1)": [
        ("Idol 30-100 Random", None, "m0g0k21111100101100000k11110000000k10111011101100k051o000000f152143331110000k012r02i0a46533a11002s0111111111110u2s0111002s01a111111111102a111111111050017pr11hg1ka03-11111-0371-"),
        ("Shounen 30-100 Random", None, "m0g0k21111100101100000k11110000000k10111011101100k051o000000f152143331110000k012r02i0a46533a11002s0111111111110u2s0111002s01a111111111102a111111111050017pr11hg1ka03-11111-01k1-"),
        ("Isekai 30-100 Random", None, "m0g0k21111100101100000k11110000000k10111011101100k051o000000f152143331110000k012r02i0a46533a11002s0111111111110u2s0111002s01a111111111102a111111111050017pr11hg1ka03-11111-06s1-"),
        ("Shoujo 30-100 Random", None, "m0g0k21111100101100000k11110000000k10111011101100k051o000000f152143331110000k012r02i0a46533a11002s0111111111110u2s0111002s01a111111111102a111111111050017pr11hg1ka03-11111-01h1-"),
        ("Music 30-100 Random", None, "m0g0k21111100101100000k11110000000k10111011101100k051o000000f152143331110000k012r02i0a46533a11002s0111111111110u2s0111002s01a111111111102a111111111050017pr11hg1ka03-111110a1--"),
        ("Sports 30-100 Random", None, "m0g0k21111100101100000k11110000000k10111011101100k051o000000f152143331110000k012r02i0a46533a11002s0111111111110u2s0111002s01a111111111102a111111111050017pr11hg1ka03-111110g1--"),
        ("Slice of Life 30-100 Random", None, "m0g0k21111100101100000k11110000000k10111011101100k051o000000f152143331110000k012r02i0a46533a11002s0111111111110u2s0111002s01a111111111102a111111111050017pr11hg1ka03-111110f1--"),
        ("Mahou Shoujo 30-100 Random", None, "m0g0k21111100101100000k11110000000k10111011101100k051o000000f152143331110000k012r02i0a46533a11002s0111111111110u2s0111002s01a111111111102a111111111050017pr11hg1ka03-11111081--"),
    ],

    "Female Artists/Male Artists": [
        ("Saori Hayami", None, "#21472"),
        ("Megumi Nakajima", None, "#202"),
        ("CHiCO", None, "#22165"),
        ("Machico", None, "#14479"),
        ("Aimer", None, "#26936"),
        ("Kana Hanazawa", None, "#27367"),
        ("Iori Nomizu", None, "#460"),
        ("Sora Amamiya", None, "#217"),
        ("Ayaka Oohashi", None, "#1012"),
        ("Nao Touyama", None, "#1983"),
        ("Miku Itou", None, "#18903"),
        ("Chihaya Yoshitake", None, "#987"),
        ("Akari Kitou", None, "#16501"),
        ("Kaori Maeda", None, "#8285"),
        ("Nana Mizuki", None, "#699"),
        ("May'n", None, "#425"),
        ("Minori Suzuki", None, "#1267"),
        ("yanaginagi", None, "#17473"),
        ("Yoshino Nanjou", None, "#1968"),
        ("LiSA", None, "#2612"),
        ("Inori Minase", None, "#25015"),
        ("Rico Sasaki", None, "#1256"),
        ("EGOIST", None, "#1068"),
        ("Yuka Iguchi", None, "#1310"),
        ("Yui Ogura", None, "#1166"),
        ("Yukari Tamura", None, "#466"),
        ("ZAQ", None, "#285"),
        ("angela", None, "#23734"),
        ("ChouCho", None, "#26194"),
        ("Tomori Kusunoki", None, "#27467"),
        ("Risa Taneda", None, "#224"),
        ("Maon Kurosaki", None, "#602"),
        ("Minori Chihara", None, "#7856"),
        ("Konomi Suzuki", None, "#21023"),
        ("Yui Horie", None, "#602"),
        ("KOTOKO", None, "#25507"),
        ("Azusa Tadokoro", None, "#385"),
        ("TRUE", None, "#16507"),
        ("ReoNa", None, "#25198"),
        ("Rie Takahashi", None, "#137"),
        ("Maaya Sakamoto", None, "#14905"),
        ("Kishou Taniyama", None, "#12018"),
        ("Shouta Aoi", None, "#27718"),
        ("Masaaki Endoh", None, "#23553"),
        ("TK", None, "#24754"),
        ("Masayoshi Ooishi", None, "#330"),
        ("Manaka Iwami", None, "#27809"),
    ],

    "Groups": [
        ("TrySail", None, "#17060"),
        ("JAM Project", None, "#23347"),
        ("Kalafina", None, "#225"),
        ("eufonius", None, "#252"),
        ("MYTH&ROID", None, "#16509"),
        ("ClariS", None, "#21994"),
        ("fripSide", None, "#332"),
        ("ALI PROJECT", None, "#18685"),
        ("nano.RIPE", None, "#316"),
        ("sajou no hana", None, "#1296"),
        ("DIALOGUE+", None, "#25458"),
        ("i☆Ris", None, "#4032"),
        ("FLOW", None, "#25386"),
        ("BUMP OF CHICKEN", None, "#588"),
        ("UVERworld", None, "#9374"),
    ],

    "Franchise": [
        ("IM@S", None, "#10162"),
        ("Bandori", None, "#9143"),
        ("Aikatsu!", None, "#226"),
        ("Initial D", None, "#24745"),
        ("IDOLiSH7", None, "#241"),
        ("Pretty Series", None, "#22870"),
        ("HoneyWorks", None, "#27963"),
        ("Pokemon (no dub)", None, "#22105"),
        ("Show by Rock", None, "#1302"),
        ("Gundam", None, "#27334"),
        ("Love Live!", None, "#27502"),
        ("Precure", None, "#13004"),
        ("Cardfight Vanguard", None, "#27505"),
        ("Nasuverse", None, "#379"),
        ("Key", None, "#25359"),
        ("UtaPri", None, "#20038"),
        ("Symphogear", None, "#127"),
        ("Macross", None, "#74"),
    ],

    "Composers": [
        ("livetune (kz)", None, "#20278"),
        ("TeddyLoid", None, "#22124"),
        ("Yuki Kajiura", None, "#21879"),
        ("Hiroyuki Sawano", None, "#18790"),
    ],

    "Extras": [
        ("TRIGGER", None, "#25118"),
        ("Madhouse", None, "#25216"),
        ("CLAMP", None, "#17127"),
    ],
}


def get_possible_S(mode: str) -> List[int]:
    mn, mx, _ = TOP_LEVEL[mode]
    return list(range(mn, mx + 1))


def get_eligible_subsettings(
    mode: str,
    S: int,
    used_settings: Set[Tuple[str, str]],
) -> List[Tuple[str, str]]:
    """
    Return eligible sub-settings for a mode.

    For REUSABLE_SUBSETTING_MODES, sub-settings are always considered eligible
    (they can repeat across rounds). Only the mode itself is restricted to
    once across all rounds (handled in find_valid_combination).

    For all other modes, a sub-setting is excluded if that exact
    (mode, sub-setting) pair was already used in a previous round.

    In both cases the sub-setting's allowed_S must include the rolled S.
    (For mastery modes this is what ties difficulty to player count.)
    """
    options = SUB_SETTINGS.get(mode, [])
    eligible = []

    for name, allowed, code in options:
        # Skip the uniqueness check for reusable sub-setting modes
        if mode in REUSABLE_SUBSETTING_MODES:
            if allowed is None or S in allowed:
                eligible.append((name, code))
        else:
            setting_key = (mode, name)
            if (allowed is None or S in allowed) and setting_key not in used_settings:
                eligible.append((name, code))

    return eligible


def has_eligible_setting(
    mode: str,
    S: int,
    used_settings: Set[Tuple[str, str]],
) -> bool:
    """True if the mode still has at least one rollable setting at player count S."""
    return bool(get_eligible_subsettings(mode, S, used_settings))


def weighted_choice(modes: List[str]) -> str:
    weights = [TOP_LEVEL[m][2] for m in modes]
    return random.choices(modes, weights=weights, k=1)[0]


def find_valid_combination(
    remaining_specials: int,
    target_sum_S: int,
    used_once_only_modes: Set[str],
    used_settings: Set[Tuple[str, str]],
    max_modes: int = 8,
) -> Optional[List[Tuple[str, int]]]:
    all_modes = list(TOP_LEVEL.keys())

    for _ in range(15000):
        chosen = []
        current_sum = 0
        specials_used = 0
        available = all_modes[:]

        while current_sum < target_sum_S and len(chosen) < max_modes and available:
            candidates = []
            for m in available:
                # Any once-only mode (all mastery modes, Novice Ranked,
                # Random Chanting, TOP X Random) can only appear once
                # across all rounds.
                if m in ONCE_ONLY_MODES and m in used_once_only_modes:
                    continue

                possible = [
                    s for s in get_possible_S(m)
                    if current_sum + s <= target_sum_S
                    and has_eligible_setting(m, s, used_settings)
                ]
                if possible:
                    candidates.append(m)
            if not candidates:
                break

            mode = weighted_choice(candidates)
            possible_S = [
                s for s in get_possible_S(mode)
                if current_sum + s <= target_sum_S
                and has_eligible_setting(mode, s, used_settings)
            ]
            if not possible_S:
                available.remove(mode)
                continue

            # Bias toward higher S only for Watched Team
            if mode == "Watched Game Modes (Team) 2v2-4v4":
                weights = []
                for s in possible_S:
                    if s == 2:
                        weights.append(1)
                    elif s == 3:
                        weights.append(2)
                    else:
                        weights.append(4)
                S = random.choices(possible_S, weights=weights, k=1)[0]
            else:
                S = random.choice(possible_S)

            is_special = mode in SPECIAL_MODES
            if is_special and specials_used + 1 > remaining_specials:
                available.remove(mode)
                continue

            chosen.append((mode, S))
            current_sum += S
            if is_special:
                specials_used += 1
            available.remove(mode)

            if current_sum == target_sum_S:
                return chosen

    return None


def roll_round(
    total_players: int,
    remaining_specials: int,
    used_settings: Set[Tuple[str, str]],
    used_once_only_modes: Set[str],
) -> Tuple[List[Tuple[str, int, str, str]], int, Set[Tuple[str, str]], Set[str]]:
    target_S = total_players // 2
    combo = find_valid_combination(
        remaining_specials,
        target_S,
        used_once_only_modes,
        used_settings,
    )

    if combo is None:
        # Fallback: never reuse a once-only mode from a previous round.
        combo = []
        left = target_S

        fallback_modes = [
            "Watched Game Modes (Team) 2v2-4v4",
            "Pad Active Player List Modes",
            "OPEDINS Mastery DNGMC",
            "Novice Ranked DNGMC",
        ]

        for mode in fallback_modes:
            # Respect the once-only restriction even during fallback.
            if mode in ONCE_ONLY_MODES and mode in used_once_only_modes:
                continue

            poss = [
                s for s in get_possible_S(mode)
                if s <= left and has_eligible_setting(mode, s, used_settings)
            ]

            if poss:
                S = max(poss)
                combo.append((mode, S))
                left -= S
                break

        # Fill any remaining player slots with reusable modes.
        reusable_fallback_modes = [
            "Watched Random Tag (Weighted)",
            "Watched Random Genre (Weighted)",
            "Watched Years (Weighted)",
            "Random Tags/Genre: (1v1)",
        ]

        while left > 0:
            added = False

            for mode in reusable_fallback_modes:
                if left >= 1:
                    combo.append((mode, 1))
                    left -= 1
                    added = True
                    break

            if not added:
                break

    result = []
    specials_used = 0
    newly_used: Set[Tuple[str, str]] = set()
    newly_used_once_only: Set[str] = set()

    for mode, S in combo:
        eligible = get_eligible_subsettings(mode, S, used_settings)
        if not eligible:
            name, code = "(no eligible setting left)", ""
        else:
            name, code = random.choice(eligible)
            # Grand Prix picked -> now roll which of its 8 variants (equal odds).
            # The (mode, GRAND_PRIX_NAME) key is what gets tracked as used below.
            if name == GRAND_PRIX_NAME:
                variant_name, code = random.choice(GRAND_PRIX_VARIANTS)
                dist_name, dist_points = random.choice(GRAND_PRIX_DISTANCES)
                display_name = (
                    f"{GRAND_PRIX_NAME} - {variant_name} | "
                    f"Distance: {dist_name} (Points goal {dist_points})"
                )
                result.append((mode, S, display_name, code))
                newly_used.add((mode, name))
                continue

        result.append((mode, S, name, code))
        # Only track used settings for modes that enforce sub-setting uniqueness
        if mode not in REUSABLE_SUBSETTING_MODES:
            newly_used.add((mode, name))

        # Track all once-only modes so they can't be rolled again
        if mode in ONCE_ONLY_MODES:
            newly_used_once_only.add(mode)

        if mode in SPECIAL_MODES:
            specials_used += 1

    return result, specials_used, newly_used, newly_used_once_only


def parse_player_input(input_str: str) -> List[str]:
    """
    Parse player input like:
    'Chiabobo (A), TheNoblesse (C+), Ducat (C), Death_Doc (B-), Kinji (B), Yonaka (A+)'
    Returns list of player names with brackets and letters removed.
    """
    players = []
    # Split by comma
    parts = input_str.split(',')
    for part in parts:
        part = part.strip()
        # Remove the bracket part
        # Find the first '(' and take everything before it
        if '(' in part:
            name = part[:part.index('(')].strip()
        else:
            name = part.strip()
        if name:
            players.append(name)
    return players


def find_matching_player(name: str) -> Optional[str]:
    """
    Find a matching player in PLAYER_LIST, case-insensitive.
    Returns the canonical player name if found, else None.
    """
    name_lower = name.lower()
    for player in PLAYER_LIST:
        if player.lower() == name_lower:
            return player
    return None


def handle_player_list_mode(
    round_data: List[Tuple[str, int, str, str]],
) -> List[Tuple[str, int, str, str]]:
    """
    For each entry in round_data that is a player list mode,
    prompt the user for input and select a random player.
    Returns the modified round_data.
    """
    player_list_modes = {"Pad Active Player List Modes"}

    for i, (mode, S, sub_name, code) in enumerate(round_data):
        if mode in player_list_modes:
            print(f"\n{'='*60}")
            print(f"  PLAYER LIST MODE DETECTED: {mode}")
            print(f"{'='*60}")
            print(f"\nEnter player names (comma-separated).")
            print(f"Example: Chiabobo (A), TheNoblesse (C+), Ducat (C), Death_Doc (B-)")
            print(f"The brackets and letters will be ignored when matching.")
            print(f"One random player will be chosen from the matched players.")
            print(f"The chosen player cannot be one of the input players.\n")

            while True:
                user_input = input("Enter players: ").strip()
                if not user_input:
                    print("Input cannot be empty. Please try again.")
                    continue

                # Parse the input
                input_players = parse_player_input(user_input)

                # Find matching players in the player list
                matched_players = []
                unmatched = []
                for p in input_players:
                    canonical = find_matching_player(p)
                    if canonical:
                        matched_players.append(canonical)
                    else:
                        unmatched.append(p)

                if unmatched:
                    print(f"\nWarning: Could not find these players in the list: {', '.join(unmatched)}")
                    print("They will be ignored.")
                    print()

                if not matched_players:
                    print("No players from the input matched the player list. Please try again.")
                    continue

                # Get all players from PLAYER_LIST that are NOT in the input
                all_player_names = list(PLAYER_LIST.keys())
                eligible = [p for p in all_player_names if p not in matched_players]

                if not eligible:
                    print("No eligible players left to choose from. Please try again.")
                    continue

                # Randomly select one player
                chosen = random.choice(eligible)
                profile_url, status = PLAYER_LIST[chosen]

                print(f"\n{'='*60}")
                print(f"  PLAYER LIST MODE - RESULT")
                print(f"{'='*60}")
                print(f"\nInput players ({len(matched_players)}):")
                for p in matched_players:
                    url, st = PLAYER_LIST[p]
                    print(f"  • {p} ({st})")
                    print(f"    {url}")
                print(f"\n🎲 RANDOMLY CHOSEN PLAYER: {chosen}")
                print(f"   Profile: {profile_url}")
                print(f"   Status:  {status}")
                print(f"{'='*60}\n")

                # Update the round data with the chosen player
                new_sub_name = f"{sub_name} → Chosen Player: {chosen} ({status}) - {profile_url}"
                round_data[i] = (mode, S, new_sub_name, code)
                break

    return round_data


def main():
    print("=" * 60)
    print("  Game Mode Roller")
    print("=" * 60)

    while True:
        try:
            p = int(input("\nEnter total number of players (even, >= 12): "))
            if p >= 12 and p % 2 == 0:
                break
            print("Must be an even integer >= 12.")
        except ValueError:
            print("Please enter a valid integer.")

    remaining_specials = 2
    used_settings: Set[Tuple[str, str]] = set()
    used_once_only_modes: Set[str] = set()
    all_rounds = []

    for r in range(1, 4):
        round_data, used, newly_used, newly_used_once_only = roll_round(
            p,
            remaining_specials,
            used_settings,
            used_once_only_modes,
        )
        remaining_specials -= used
        used_settings.update(newly_used)
        used_once_only_modes.update(newly_used_once_only)
        all_rounds.append(round_data)

    # ---------- Handle player list modes ----------
    for r in range(len(all_rounds)):
        all_rounds[r] = handle_player_list_mode(all_rounds[r])

    # ---------- Clean version (no codes) ----------
    print("\n" + "=" * 60)
    print("  CLEAN VERSION (no codes)")
    print("=" * 60)

    for r, round_data in enumerate(all_rounds, 1):
        print(f"\n--- Round {r} ---")
        for mode, S, sub_name, code in round_data:
            players = 2 * S
            print(f"• {mode}")
            print(f"  → {S}v{S}  ({players} players)")
            print(f"  → Setting: {sub_name}")
            print()

    # ---------- Full version (with codes) ----------
    print("\n" + "=" * 60)
    print("  FULL VERSION (with codes)")
    print("=" * 60)

    for r, round_data in enumerate(all_rounds, 1):
        print(f"\n--- Round {r} ---")
        for mode, S, sub_name, code in round_data:
            players = 2 * S
            print(f"• {mode}")
            print(f"  → {S}v{S}  ({players} players)")
            print(f"  → Setting: {sub_name}")
            if code:
                print(f"  → Code: `{code}`")
                if "Picked" in sub_name:
                    print("  → Reminder: change the settings inside the game")
            print()

    print("=" * 60)


if __name__ == "__main__":
    main()
