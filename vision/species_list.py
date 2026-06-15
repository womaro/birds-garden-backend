"""
birds.garden — kanoniczna lista gatunków (v2, 79 gatunków).

`slug` = nazwa folderu klasy w datasetcie ORAZ etykieta klasy w wytrenowanym
modelu (musi się zgadzać z nazwami plików SVG w assets/birds/).
`en`   = nazwa zwracana przez klasyfikator (spójna z BIRD_BIO / detections.species).
`sci`  = nazwa naukowa do zapytań GBIF.

Klasa "other" (OTHER_CLASS) jest klasą śmietnikową dla ptaków spoza listy —
trenowana z mieszanki innych gatunków, NIE występuje w SPECIES (brak sci/pl/en).
Klasyfikator zwracający "other" lub pewność < próg → species = None ("Nieznany ptak").
"""

SPECIES = [
    # ── Sikory + raniuszek ──────────────────────────────────────────────────
    {"slug": "great_tit",              "sci": "Parus major",                 "pl": "Sikora bogatka",     "en": "Great Tit"},
    {"slug": "blue_tit",               "sci": "Cyanistes caeruleus",         "pl": "Sikora modra",       "en": "Blue Tit"},
    {"slug": "marsh_tit",              "sci": "Poecile palustris",           "pl": "Sikora uboga",       "en": "Marsh Tit"},
    {"slug": "willow_tit",             "sci": "Poecile montanus",            "pl": "Czarnogłówka",       "en": "Willow Tit"},
    {"slug": "coal_tit",               "sci": "Periparus ater",              "pl": "Sosnówka",           "en": "Coal Tit"},
    {"slug": "crested_tit",            "sci": "Lophophanes cristatus",       "pl": "Czubatka",           "en": "Crested Tit"},
    {"slug": "long-tailed_tit",        "sci": "Aegithalos caudatus",         "pl": "Raniuszek",          "en": "Long-tailed Tit"},
    # ── Łuszczaki ────────────────────────────────────────────────────────────
    {"slug": "common_chaffinch",       "sci": "Fringilla coelebs",           "pl": "Zięba",              "en": "Common Chaffinch"},
    {"slug": "brambling",              "sci": "Fringilla montifringilla",    "pl": "Jer",                "en": "Brambling"},
    {"slug": "european_greenfinch",    "sci": "Chloris chloris",             "pl": "Dzwoniec",           "en": "European Greenfinch"},
    {"slug": "european_goldfinch",     "sci": "Carduelis carduelis",         "pl": "Szczygieł",          "en": "European Goldfinch"},
    {"slug": "common_linnet",          "sci": "Linaria cannabina",           "pl": "Makolągwa",          "en": "Common Linnet"},
    {"slug": "eurasian_siskin",        "sci": "Spinus spinus",               "pl": "Czyż",               "en": "Eurasian Siskin"},
    {"slug": "common_redpoll",         "sci": "Acanthis flammea",            "pl": "Czeczotka",          "en": "Common Redpoll"},
    {"slug": "eurasian_bullfinch",     "sci": "Pyrrhula pyrrhula",           "pl": "Gil",                "en": "Eurasian Bullfinch"},
    {"slug": "hawfinch",               "sci": "Coccothraustes coccothraustes", "pl": "Grubodziób",       "en": "Hawfinch"},
    {"slug": "european_serin",         "sci": "Serinus serinus",             "pl": "Kulczyk",            "en": "European Serin"},
    # ── Wróble ─────────────────────────────────────────────────────────────
    {"slug": "house_sparrow",          "sci": "Passer domesticus",           "pl": "Wróbel",             "en": "House Sparrow"},
    {"slug": "tree_sparrow",           "sci": "Passer montanus",             "pl": "Mazurek",            "en": "Tree Sparrow"},
    # ── Drozdy ───────────────────────────────────────────────────────────────
    {"slug": "eurasian_blackbird",     "sci": "Turdus merula",               "pl": "Kos",                "en": "Eurasian Blackbird"},
    {"slug": "song_thrush",            "sci": "Turdus philomelos",           "pl": "Drozd śpiewak",      "en": "Song Thrush"},
    {"slug": "mistle_thrush",          "sci": "Turdus viscivorus",           "pl": "Paszkot",            "en": "Mistle Thrush"},
    {"slug": "fieldfare",              "sci": "Turdus pilaris",              "pl": "Kwiczoł",            "en": "Fieldfare"},
    {"slug": "redwing",                "sci": "Turdus iliacus",              "pl": "Droździk",           "en": "Redwing"},
    # ── Muchołówki, rudzik, pleszka i krewni ─────────────────────────────────
    {"slug": "european_robin",         "sci": "Erithacus rubecula",          "pl": "Rudzik",             "en": "European Robin"},
    {"slug": "common_redstart",        "sci": "Phoenicurus phoenicurus",     "pl": "Pleszka",            "en": "Common Redstart"},
    {"slug": "black_redstart",         "sci": "Phoenicurus ochruros",        "pl": "Kopciuszek",         "en": "Black Redstart"},
    {"slug": "spotted_flycatcher",     "sci": "Muscicapa striata",           "pl": "Muchołówka szara",   "en": "Spotted Flycatcher"},
    {"slug": "pied_flycatcher",        "sci": "Ficedula hypoleuca",          "pl": "Muchołówka żałobna", "en": "European Pied Flycatcher"},
    {"slug": "thrush_nightingale",     "sci": "Luscinia luscinia",           "pl": "Słowik szary",       "en": "Thrush Nightingale"},
    # ── Pokrzewki i świstunki ────────────────────────────────────────────────
    {"slug": "blackcap",               "sci": "Sylvia atricapilla",          "pl": "Kapturka",           "en": "Blackcap"},
    {"slug": "garden_warbler",         "sci": "Sylvia borin",                "pl": "Gajówka",            "en": "Garden Warbler"},
    {"slug": "common_whitethroat",     "sci": "Curruca communis",            "pl": "Cierniówka",         "en": "Common Whitethroat"},
    {"slug": "lesser_whitethroat",     "sci": "Curruca curruca",             "pl": "Piegża",             "en": "Lesser Whitethroat"},
    {"slug": "common_chiffchaff",      "sci": "Phylloscopus collybita",      "pl": "Pierwiosnek",        "en": "Common Chiffchaff"},
    {"slug": "willow_warbler",         "sci": "Phylloscopus trochilus",      "pl": "Piecuszek",          "en": "Willow Warbler"},
    # ── Mysikróliki ──────────────────────────────────────────────────────────
    {"slug": "goldcrest",              "sci": "Regulus regulus",             "pl": "Mysikrólik",         "en": "Goldcrest"},
    {"slug": "firecrest",              "sci": "Regulus ignicapilla",         "pl": "Zniczek",            "en": "Common Firecrest"},
    # ── Kowalik + pełzacze ─────────────────────────────────────────────────
    {"slug": "eurasian_nuthatch",      "sci": "Sitta europaea",              "pl": "Kowalik",            "en": "Eurasian Nuthatch"},
    {"slug": "short-toed_treecreeper", "sci": "Certhia brachydactyla",       "pl": "Pełzacz ogrodowy",   "en": "Short-toed Treecreeper"},
    {"slug": "eurasian_treecreeper",   "sci": "Certhia familiaris",          "pl": "Pełzacz leśny",      "en": "Eurasian Treecreeper"},
    # ── Strzyżyk + pokrzywnica ───────────────────────────────────────────────
    {"slug": "eurasian_wren",          "sci": "Troglodytes troglodytes",     "pl": "Strzyżyk",           "en": "Eurasian Wren"},
    {"slug": "dunnock",                "sci": "Prunella modularis",          "pl": "Pokrzywnica",        "en": "Dunnock"},
    # ── Krukowate ────────────────────────────────────────────────────────────
    {"slug": "eurasian_jay",           "sci": "Garrulus glandarius",         "pl": "Sójka",              "en": "Eurasian Jay"},
    {"slug": "eurasian_magpie",        "sci": "Pica pica",                   "pl": "Sroka",              "en": "Eurasian Magpie"},
    {"slug": "hooded_crow",            "sci": "Corvus cornix",               "pl": "Wrona siwa",         "en": "Hooded Crow"},
    {"slug": "jackdaw",                "sci": "Corvus monedula",             "pl": "Kawka",              "en": "Jackdaw"},
    {"slug": "rook",                   "sci": "Corvus frugilegus",           "pl": "Gawron",             "en": "Rook"},
    {"slug": "common_raven",           "sci": "Corvus corax",                "pl": "Kruk",               "en": "Northern Raven"},
    # ── Gołębie ──────────────────────────────────────────────────────────────
    {"slug": "common_wood_pigeon",     "sci": "Columba palumbus",            "pl": "Grzywacz",           "en": "Common Wood Pigeon"},
    {"slug": "collared_dove",          "sci": "Streptopelia decaocto",       "pl": "Sierpówka",          "en": "Collared Dove"},
    {"slug": "stock_dove",             "sci": "Columba oenas",               "pl": "Siniak",             "en": "Stock Dove"},
    {"slug": "feral_pigeon",           "sci": "Columba livia",               "pl": "Gołąb miejski",      "en": "Rock Dove"},
    {"slug": "turtle_dove",            "sci": "Streptopelia turtur",         "pl": "Turkawka",           "en": "European Turtle Dove"},
    # ── Jaskółki + jerzyk ────────────────────────────────────────────────────
    {"slug": "barn_swallow",           "sci": "Hirundo rustica",             "pl": "Jaskółka dymówka",   "en": "Barn Swallow"},
    {"slug": "house_martin",           "sci": "Delichon urbicum",            "pl": "Oknówka",            "en": "Common House Martin"},
    {"slug": "common_swift",           "sci": "Apus apus",                   "pl": "Jerzyk",             "en": "Common Swift"},
    # ── Szpaki ───────────────────────────────────────────────────────────────
    {"slug": "common_starling",        "sci": "Sturnus vulgaris",            "pl": "Szpak",              "en": "Common Starling"},
    # ── Trznadle ─────────────────────────────────────────────────────────────
    {"slug": "yellowhammer",           "sci": "Emberiza citrinella",         "pl": "Trznadel",           "en": "Yellowhammer"},
    {"slug": "reed_bunting",           "sci": "Emberiza schoeniclus",        "pl": "Potrzos",            "en": "Reed Bunting"},
    # ── Dzięcioły ────────────────────────────────────────────────────────────
    {"slug": "great_spotted_woodpecker",  "sci": "Dendrocopos major",        "pl": "Dzięcioł duży",      "en": "Great Spotted Woodpecker"},
    {"slug": "lesser_spotted_woodpecker", "sci": "Dryobates minor",          "pl": "Dzięciołek",         "en": "Lesser Spotted Woodpecker"},
    {"slug": "middle_spotted_woodpecker", "sci": "Dendrocoptes medius",      "pl": "Dzięcioł średni",    "en": "Middle Spotted Woodpecker"},
    {"slug": "green_woodpecker",       "sci": "Picus viridis",               "pl": "Dzięcioł zielony",   "en": "European Green Woodpecker"},
    {"slug": "black_woodpecker",       "sci": "Dryocopus martius",           "pl": "Dzięcioł czarny",    "en": "Black Woodpecker"},
    {"slug": "wryneck",                "sci": "Jynx torquilla",              "pl": "Krętogłów",          "en": "Eurasian Wryneck"},
    # ── Pliszki ──────────────────────────────────────────────────────────────
    {"slug": "white_wagtail",          "sci": "Motacilla alba",              "pl": "Pliszka siwa",       "en": "White Wagtail"},
    {"slug": "grey_wagtail",           "sci": "Motacilla cinerea",           "pl": "Pliszka górska",     "en": "Grey Wagtail"},
    {"slug": "yellow_wagtail",         "sci": "Motacilla flava",             "pl": "Pliszka żółta",      "en": "Western Yellow Wagtail"},
    # ── Gąsiorek ─────────────────────────────────────────────────────────────
    {"slug": "red-backed_shrike",      "sci": "Lanius collurio",             "pl": "Gąsiorek",           "en": "Red-backed Shrike"},
    # ── Jemiołuszka ──────────────────────────────────────────────────────────
    {"slug": "waxwing",                "sci": "Bombycilla garrulus",         "pl": "Jemiołuszka",        "en": "Bohemian Waxwing"},
    # ── Kukułka ──────────────────────────────────────────────────────────────
    {"slug": "common_cuckoo",          "sci": "Cuculus canorus",             "pl": "Kukułka",            "en": "Common Cuckoo"},
    # ── Dudek ────────────────────────────────────────────────────────────────
    {"slug": "hoopoe",                 "sci": "Upupa epops",                 "pl": "Dudek",              "en": "Eurasian Hoopoe"},
    # ── Ptaki drapieżne ──────────────────────────────────────────────────────
    {"slug": "sparrowhawk",            "sci": "Accipiter nisus",             "pl": "Krogulec",           "en": "Eurasian Sparrowhawk"},
    {"slug": "kestrel",                "sci": "Falco tinnunculus",           "pl": "Pustułka",           "en": "Common Kestrel"},
    {"slug": "buzzard",                "sci": "Buteo buteo",                 "pl": "Myszołów",           "en": "Common Buzzard"},
    {"slug": "tawny_owl",              "sci": "Strix aluco",                 "pl": "Puszczyk",           "en": "Tawny Owl"},
    # ── Wodne (oczko / park) ─────────────────────────────────────────────────
    {"slug": "grey_heron",             "sci": "Ardea cinerea",               "pl": "Czapla siwa",        "en": "Grey Heron"},
    {"slug": "mallard",                "sci": "Anas platyrhynchos",          "pl": "Krzyżówka",          "en": "Mallard"},
]

# Klasa śmietnikowa — patrz docstring. Nie ma jej w SPECIES.
OTHER_CLASS = "other"

# Pełna lista klas klasyfikatora (gatunki + "other").
CLASSIFIER_CLASSES = [s["slug"] for s in SPECIES] + [OTHER_CLASS]

SLUG_TO_EN = {s["slug"]: s["en"] for s in SPECIES}
SLUG_TO_PL = {s["slug"]: s["pl"] for s in SPECIES}
EN_TO_SLUG = {s["en"]: s["slug"] for s in SPECIES}