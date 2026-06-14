"""
birds.garden — kanoniczna lista 35 gatunków.

`slug` = nazwa folderu klasy w datasetcie ORAZ etykieta klasy w wytrenowanym
modelu (musi się zgadzać z nazwami plików SVG w assets/birds/).
`en`   = nazwa zwracana przez klasyfikator (spójna z BIRD_BIO / detections.species).
`sci`  = nazwa naukowa do zapytań GBIF.
"""

SPECIES = [
    {"slug": "eurasian_blackbird",     "sci": "Turdus merula",              "pl": "Kos",               "en": "Eurasian Blackbird"},
    {"slug": "blue_tit",               "sci": "Cyanistes caeruleus",        "pl": "Sikora modra",      "en": "Blue Tit"},
    {"slug": "great_tit",              "sci": "Parus major",                "pl": "Sikora bogatka",    "en": "Great Tit"},
    {"slug": "common_starling",        "sci": "Sturnus vulgaris",           "pl": "Szpak",             "en": "Common Starling"},
    {"slug": "european_robin",         "sci": "Erithacus rubecula",         "pl": "Rudzik",            "en": "European Robin"},
    {"slug": "house_sparrow",          "sci": "Passer domesticus",          "pl": "Wróbel",            "en": "House Sparrow"},
    {"slug": "common_chaffinch",       "sci": "Fringilla coelebs",          "pl": "Zięba",             "en": "Common Chaffinch"},
    {"slug": "european_greenfinch",    "sci": "Chloris chloris",            "pl": "Dzwoniec",          "en": "European Greenfinch"},
    {"slug": "common_wood_pigeon",     "sci": "Columba palumbus",           "pl": "Grzywacz",          "en": "Common Wood Pigeon"},
    {"slug": "eurasian_jay",           "sci": "Garrulus glandarius",        "pl": "Sójka",             "en": "Eurasian Jay"},
    {"slug": "eurasian_magpie",        "sci": "Pica pica",                  "pl": "Sroka",             "en": "Eurasian Magpie"},
    {"slug": "song_thrush",            "sci": "Turdus philomelos",          "pl": "Drozd śpiewak",     "en": "Song Thrush"},
    {"slug": "blackcap",               "sci": "Sylvia atricapilla",         "pl": "Kapturka",          "en": "Blackcap"},
    {"slug": "dunnock",                "sci": "Prunella modularis",         "pl": "Pokrzywnica",       "en": "Dunnock"},
    {"slug": "common_swift",           "sci": "Apus apus",                  "pl": "Jerzyk",            "en": "Common Swift"},
    {"slug": "eurasian_wren",          "sci": "Troglodytes troglodytes",    "pl": "Strzyżyk",          "en": "Eurasian Wren"},
    {"slug": "long-tailed_tit",        "sci": "Aegithalos caudatus",        "pl": "Raniuszek",         "en": "Long-tailed Tit"},
    {"slug": "eurasian_nuthatch",      "sci": "Sitta europaea",             "pl": "Kowalik",           "en": "Eurasian Nuthatch"},
    {"slug": "short-toed_treecreeper", "sci": "Certhia brachydactyla",      "pl": "Pełzacz ogrodowy",  "en": "Short-toed Treecreeper"},
    {"slug": "european_goldfinch",     "sci": "Carduelis carduelis",        "pl": "Szczygieł",         "en": "European Goldfinch"},
    {"slug": "common_linnet",          "sci": "Linaria cannabina",          "pl": "Makolągwa",         "en": "Common Linnet"},
    {"slug": "eurasian_bullfinch",     "sci": "Pyrrhula pyrrhula",          "pl": "Gil",               "en": "Eurasian Bullfinch"},
    {"slug": "hawfinch",               "sci": "Coccothraustes coccothraustes", "pl": "Grubodziób",     "en": "Hawfinch"},
    {"slug": "yellowhammer",           "sci": "Emberiza citrinella",        "pl": "Trznadel",          "en": "Yellowhammer"},
    {"slug": "spotted_flycatcher",     "sci": "Muscicapa striata",          "pl": "Muchołówka szara",  "en": "Spotted Flycatcher"},
    {"slug": "common_redstart",        "sci": "Phoenicurus phoenicurus",    "pl": "Pleszka",           "en": "Common Redstart"},
    {"slug": "barn_swallow",           "sci": "Hirundo rustica",            "pl": "Jaskółka dymówka",  "en": "Barn Swallow"},
    {"slug": "hooded_crow",            "sci": "Corvus cornix",              "pl": "Wrona siwa",        "en": "Hooded Crow"},
    {"slug": "jackdaw",                "sci": "Corvus monedula",            "pl": "Kawka",             "en": "Jackdaw"},
    {"slug": "collared_dove",          "sci": "Streptopelia decaocto",      "pl": "Sierpówka",         "en": "Collared Dove"},
    {"slug": "eurasian_siskin",        "sci": "Spinus spinus",              "pl": "Czyż",              "en": "Eurasian Siskin"},
    {"slug": "fieldfare",              "sci": "Turdus pilaris",             "pl": "Kwiczoł",           "en": "Fieldfare"},
    {"slug": "tree_sparrow",           "sci": "Passer montanus",            "pl": "Mazurek",           "en": "Tree Sparrow"},
    {"slug": "common_redpoll",         "sci": "Acanthis flammea",           "pl": "Czeczotka",         "en": "Common Redpoll"},
    {"slug": "marsh_tit",              "sci": "Poecile palustris",          "pl": "Sikora uboga",      "en": "Marsh Tit"},
]

SLUG_TO_EN = {s["slug"]: s["en"] for s in SPECIES}
SLUG_TO_PL = {s["slug"]: s["pl"] for s in SPECIES}
EN_TO_SLUG = {s["en"]: s["slug"] for s in SPECIES}
