"""Map product descriptions and Olist categories onto a shared set.

UCI is a UK gift and homeware retailer. It has product names, not categories.
Olist has published English category translations. We map UCI names with
keywords, and Olist categories by a fixed table, onto a shared list where
the match is honest. Categories that only exist in one source stay in that
source and are labelled as such.
"""
from __future__ import annotations

import re

SHARED_CATEGORIES = [
    "Home decor",
    "Kitchen and housewares",
    "Stationery and wrapping",
    "Bags and luggage",
    "Christmas and party",
    "Toys and games",
    "Baby and children",
    "Garden",
    "Jewellery and watches",
    "Health and beauty",
    "Pet",
]

UCI_UNMAPPED = "Giftware (other)"

# First match wins. More specific patterns come first.
# These are judgement calls on gift-retail descriptions, not published labels.
_UCI_RULES = [
    ("Christmas and party",
     r"CHRISTMAS|XMAS|ADVENT|BAUBLE|PARTY BUNTING|BUNTING|BALLOON|HALLOWEEN|"
     r"EASTER|HEN PARTY|BIRTHDAY|PAPER CHAIN|HONEYCOMB|CRACKER|TINSEL|"
     r"STOCKING|NUTCRACKER|SNOW(MAN|FLAKE)|REINDEER|SANTA|\bELF\b|ELVES|"
     r"PARTY INVITE|GLOWING TIARA"),
    ("Baby and children",
     r"\bBABY\b|CHILD(REN|REN'S|ERNS|S')?|NURSERY|DOLLY GIRL|SPACEBOY BABY|"
     r"INFANT|TODDLER|\bBIB\b|NAPPY|CHARLIE (&|AND) LOLA"),
    ("Toys and games",
     r"\bTOY\b|SOFT TOY|TEDDY BEAR|\bDOLL\b|PUPPET|PUZZLE|BOARD GAME|"
     r"PLAYHOUSE|JUMPING BEAN|MAGIC GARDEN|JIGSAW|HELICOPTER|NINJA RABBIT|"
     r"RATTLE|PADDED (MOBILE|SOFT MOBILE)|CIRCULAR MOBILE|MONSTER|"
     r"TATTOOS|PLAY TENT"),
    ("Jewellery and watches",
     r"NECKLACE|BRACELET|EARRING|JEWELLERY|JEWELRY|\bRING\b|WATCH|PENDANT|"
     r"BROOCH|TIARA|MURANO|DIAMANTE|BEADED PEARL"),
    ("Bags and luggage",
     r"JUMBO BAG|LUNCH BAG|CHARLOTTE BAG|AIRLINE BAG|CANDY BAG|GIFT BAG|"
     r"SHOPPER|TOTE|HANDBAG|RUCKSACK|BACKPACK|SUITCASE|LUGGAGE|WASHBAG|"
     r"COSMETIC BAG|VANITY|PURSE|WALLET|SATCHEL|CARRIER|PASSPORT COVER|"
     r"TRAVEL CARD|LUGGAGE TAG"),
    ("Stationery and wrapping",
     r"\bWRAP\b|GIFT WRAP|NOTEBOOK|PENCIL|PENS\b|\bPEN\b|ENVELOPE|STATIONERY|"
     r"PAPER POCKET|\bCARD\b|GREETING|STICKER|RULER|ERASER|SHARPENER|DIARY|"
     r"JOURNAL|CALENDAR|SKETCH|WRAPPING|GIFT TAG|TISSUE PAPER|PACK OF \d+ CARDS|"
     r"VINTAGE SNAP|POSTCARD|POCKET BOOK|MEMO PAD|TAPE DISPENSER|BOOKCOVER|"
     r"SCISSOR|DOILIES|DOILY|PACK OF 12 \w+ TISSUES|FUNKY DIVA PEN|"
     r"COLOURING|LETTER SHAPE"),
    ("Garden",
     r"GARDEN|WATERING CAN|PARASOL|SEED |POTTING|PLANTER|BIRD HOUSE|"
     r"BIRDHOUSE|OUTDOOR|TROWEL|GNOME|HAMMOCK|CACTUS"),
    ("Pet",
     r"DOG BOWL|CAT BOWL|\bPET\b|DOG COLLAR|CAT COLLAR|DOG LEAD|BIRD FEEDER|"
     r"DOG TOY|DOGGY RUBBER"),
    ("Health and beauty",
     r"BATH |SOAP|SPONGE|INCENSE|PERFUME|LOTION|\bBODY\b|COSMETIC|\bHAIR\b|"
     r"\bNAIL\b|\bLIP\b|BATHROOM|TOILET|TOWEL|SCENTED(?! CANDLE)|OIL BURNER|"
     r"DIFFUSER|FRAGRANCE OIL|FIRST AID"),
    ("Kitchen and housewares",
     r"MUG|\bCUP\b|BOWL|PLATE|CAKE|CUTLERY|BAKING|\bTEA\b|COFFEE|KITCHEN|"
     r"\bJUG\b|\bJAR\b|\bTIN\b|\bPAN\b|DISH|SAUCER|SPOON|FORK|KNIFE|NAPKIN|"
     r"COASTER|CHOPPING|OVEN|APRON|TEAPOT|KETTLE|BOTTLE|TUMBLER|\bWINE\b|"
     r"BEAKER|CASSEROLE|FRYING|TRIVET|BREAD|BISCUIT|SUGAR|CREAMER|PICNIC|"
     r"LUNCH BOX|\bEGG\b|CUTTER|MOULD|MOLD|SIEVE|WHISK|SPATULA|PLACE MAT|"
     r"PLACEMAT|TABLECLOTH|TEA TOWEL|TEATOWEL|CAKESTAND|CAKE STAND|FAIRY CAKE|"
     r"CUPCAKE|COOKIE|MILKSHAKE|PETIT FOUR|ESPRESSO|WASHING UP GLOVE|"
     r"FRIDGE MAGNET|\bTRAY\b|CHOPSTICK"),
    ("Home decor",
     r"HANGING|CANDLE|T-LIGHT|TLIGHT|T LIGHT|FRAME|ORNAMENT|WICKER|WREATH|"
     r"DOORMAT|CLOCK|LANTERN|VASE|CUSHION|BLANKET|HOOK|DECORATION|CHANDELIER|"
     r"LAMPSHADE|\bLAMP\b|MIRROR|PICTURE|WALL ART|\bSIGN\b|PLAQUE|HEART OF|"
     r"RUG |\bMAT\b|CANDLESTICK|TEALIGHT|TEA LIGHT|FLOWER|RIBBON|"
     r"CERAMIC|SLATE|CHALKBOARD|WOODEN|BLOCK WORD|PHOTO|ALBUM|BASKET|TRINKET|"
     r"DRAWER|CABINET|SHELF|STOOL|QUILT|\bTHROW\b|PILLOW|CURTAIN|DOORSTOP|"
     r"KNOB|HANGER|CLOTHES PEG|WALL TIDY|WASTEPAPER|MAGAZINE RACK|\bURN\b|"
     r"ZINC HEART|LATTICE|SILK FAN|\bFAN\b|PAPERWEIGHT|GLOBE|"
     r"BUTTERFLY CLIP|INFLATABLE"),
]

# Olist English category -> our shared category, or None if it should stay
# as an Olist-only category under a readable name.
OLIST_TO_SHARED = {
    "housewares": "Kitchen and housewares",
    "la_cuisine": "Kitchen and housewares",
    "kitchen_dining_laundry_garden_furniture": "Kitchen and housewares",
    "furniture_decor": "Home decor",
    "home_confort": "Home decor",
    "home_comfort_2": "Home decor",
    "art": "Home decor",
    "arts_and_craftmanship": "Home decor",
    "stationery": "Stationery and wrapping",
    "christmas_supplies": "Christmas and party",
    "party_supplies": "Christmas and party",
    "toys": "Toys and games",
    # consoles_games stays Olist-only: video games are not gift-shop toys
    "baby": "Baby and children",
    "diapers_and_hygiene": "Baby and children",
    "fashion_childrens_clothes": "Baby and children",
    "garden_tools": "Garden",
    "flowers": "Garden",
    "costruction_tools_garden": "Garden",
    "watches_gifts": "Jewellery and watches",
    "health_beauty": "Health and beauty",
    "perfumery": "Health and beauty",
    "fashion_bags_accessories": "Bags and luggage",
    "luggage_accessories": "Bags and luggage",
    "pet_shop": "Pet",
    "bed_bath_table": "Home decor",
}

# Readable names for Olist-only categories (underscores to words).
_OLIST_ONLY_NAMES = {
    "fashio_female_clothing": "Fashion, women's clothing (marketplace only)",
    "cool_stuff": "Cool stuff (marketplace only)",
    "market_place": "Marketplace general (marketplace only)",
    "costruction_tools_tools": "Construction tools (marketplace only)",
    "home_confort": "Home comfort (marketplace only)",
    "home_comfort_2": "Home comfort (marketplace only)",
}


def _title_olist(raw: str) -> str:
    if raw in _OLIST_ONLY_NAMES:
        return _OLIST_ONLY_NAMES[raw]
    words = raw.replace("_", " ").strip()
    return words[:1].upper() + words[1:] + " (marketplace only)"


def map_uci_description(description: str) -> tuple[str, bool]:
    """Return (category, mapped_to_shared).

    Unmapped giftware is 'Giftware (other)', which is retailer-only, not shared.
    """
    d = re.sub(r"\s+", " ", str(description).upper().strip())
    if not d:
        return UCI_UNMAPPED, False
    for cat, patt in _UCI_RULES:
        if re.search(patt, d):
            return cat, True
    return UCI_UNMAPPED, False


def map_olist_category(english_name: str) -> tuple[str, bool, str]:
    """Return (display category, is_shared, original english name)."""
    raw = str(english_name or "").strip()
    if not raw:
        return "Uncategorised (marketplace only)", False, raw
    if raw in OLIST_TO_SHARED:
        return OLIST_TO_SHARED[raw], True, raw
    return _title_olist(raw), False, raw
