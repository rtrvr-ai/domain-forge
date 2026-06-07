"""
Curated seed corpus.

These are hand-picked, domain-friendly words across many origins and themes.
They serve two purposes:

  1. As Datamuse expansion anchors (each seed pulls in dozens of relatives).
  2. As candidates in their own right.

The corpus is intentionally broad — mythology, science, world languages,
feelings, nature, food, gems, colors, plus *engineered* coinages (invented
short words that tend to be registrable) and abstract "concept" dimensions
that cast a wide associative net when fed to the word graph.

`CATEGORIES` maps a category name -> list of words. `all_words()` returns the
deduped, cleaned union. `select(names)` returns a subset by category.
"""

from __future__ import annotations

import re

# Each list is deduped on load; light overlap between categories is fine and
# is preserved as multi-category membership.
CATEGORIES: dict[str, list[str]] = {
    # ── Ancient Greek ────────────────────────────────────────────────
    "greek": [
        "zeus", "hera", "athena", "apollo", "artemis", "hermes", "ares",
        "poseidon", "hades", "demeter", "persephone", "nike", "iris", "eos",
        "helios", "selene", "nyx", "erebus", "chronos", "nemesis", "tyche",
        "hecate", "proteus", "triton", "morpheus", "hypnos", "atlas",
        "prometheus", "orpheus", "icarus", "daedalus", "perseus", "phoenix",
        "pegasus", "hydra", "chimera", "medusa", "centaur", "olympus",
        "elysium", "arcadia", "delphi", "lethe", "styx", "logos", "cosmos",
        "kairos", "pathos", "ethos", "telos", "nous", "pneuma", "arete",
        "polis", "agora", "kratos", "sophia", "aletheia", "catharsis",
        "thesis", "praxis", "alpha", "delta", "sigma", "omega", "theta",
        "kappa", "lambda",
    ],
    # ── Latin ────────────────────────────────────────────────────────
    "latin": [
        "aether", "lux", "nexus", "apex", "vortex", "animus", "novus",
        "verus", "altus", "magnus", "fortis", "fides", "nova", "terra",
        "mare", "caelum", "stella", "ignis", "aqua", "ventus", "lumen",
        "numen", "umbra", "aurora", "sol", "luna", "ratio", "virtus",
        "veritas", "gloria", "pax", "concordia", "janus", "mars", "venus",
        "mercury", "saturn", "minerva", "diana", "ceres", "flora", "vulcan",
        "fortuna", "nucleus", "radius", "axis", "matrix", "vertex", "corona",
        "nebula", "corpus", "orbis", "anima", "causa", "ordo", "lex",
        "modus", "opus", "lucid", "vivid", "rapid", "fluid", "valid",
        "ardent", "latent", "salient", "vibrant", "felix",
    ],
    # ── Sanskrit ─────────────────────────────────────────────────────
    "sanskrit": [
        "satya", "ananda", "prana", "akasha", "dharma", "karma", "moksha",
        "maya", "nirvana", "mandala", "mantra", "chakra", "sutra", "tantra",
        "soma", "amrita", "veda", "atman", "jnana", "bhakti", "shakti",
        "ahimsa", "mudra", "yantra", "bindu", "nada", "lila", "samsara",
        "samadhi", "prajna", "bodhi", "metta", "viveka", "tapas", "siddhi",
        "vidya", "agni", "vayu", "surya", "chandra", "tara", "indra",
        "varuna", "vishnu", "lakshmi", "saraswati", "durga", "ganesha",
        "deva", "naga", "yoga", "guru", "avatar",
    ],
    # ── Japanese ─────────────────────────────────────────────────────
    "japanese": [
        "wabi", "sabi", "mushin", "zanshin", "kensho", "satori", "kodawari",
        "ikigai", "yugen", "kaizen", "enso", "aware", "komorebi", "sakura",
        "fuji", "sora", "kaze", "hana", "yama", "umi", "mori", "nami",
        "umami", "dashi", "miso", "matcha", "yuzu", "shiso", "wasabi",
        "sake", "koji", "mirin", "nori", "udon", "soba", "tofu", "ramen",
        "kitsune", "tanuki", "tengu", "kappa", "oni", "ryu", "kami",
        "amaterasu", "susanoo", "tsukuyomi", "bushido", "samurai", "ronin",
        "katana", "haiku", "origami", "bonsai", "dojo", "torii", "kintsugi",
        "ikebana", "shokunin", "omotenashi", "kawaii", "senpai", "sensei",
    ],
    # ── Arabic ───────────────────────────────────────────────────────
    "arabic": [
        "aldebaran", "altair", "rigel", "deneb", "fomalhaut", "algol",
        "alnair", "alcyone", "almach", "zenith", "nadir", "azimuth",
        "algebra", "alchemy", "cipher", "almanac", "elixir", "alkali",
        "azure", "jasmine", "saffron", "caravan", "bazaar", "henna",
        "sherbet", "tahini", "zaatar", "harissa", "sumac", "dukkah",
        "halva", "mastic", "nour", "hayat", "jamal", "baraka", "sabr",
        "layla", "zara", "ghazal", "qasida",
    ],
    # ── Norse ────────────────────────────────────────────────────────
    "norse": [
        "odin", "thor", "loki", "freya", "baldur", "tyr", "heimdall",
        "frigg", "skadi", "njord", "freyr", "vidar", "bragi", "idunn",
        "valhalla", "asgard", "midgard", "jotunheim", "niflheim", "alfheim",
        "yggdrasil", "bifrost", "fenrir", "nidhogg", "hugin", "munin",
        "sleipnir", "fafnir", "valkyrie", "einherjar", "draugr", "mjolnir",
        "gungnir", "draupnir", "rune", "skald", "saga", "edda", "ragnarok",
        "wyrd", "norns", "seidr", "galdr", "fjord", "boreal", "frost",
        "mead", "birch", "rowan", "raven",
    ],
    # ── Egyptian / Kemetic ───────────────────────────────────────────
    "egyptian": [
        "osiris", "isis", "horus", "anubis", "thoth", "bastet", "sekhmet",
        "amun", "hathor", "ptah", "sobek", "khnum", "neith", "selket",
        "nephthys", "khonsu", "wadjet", "aten", "nefertum", "ankh",
        "scarab", "djed", "uraeus", "benben", "sistrum", "maat", "sahu",
        "sekhem", "papyrus", "lotus", "obelisk", "sphinx", "karnak",
        "thebes", "memphis", "heliopolis", "ubuntu", "safari", "savanna",
        "baobab", "kente", "djembe", "griot",
    ],
    # ── Celtic / Gaelic ──────────────────────────────────────────────
    "celtic": [
        "lugh", "dagda", "morrigan", "brigid", "cernunnos", "danu",
        "aengus", "nuada", "boann", "aine", "ogma", "medb", "fionn",
        "diarmuid", "grainne", "druid", "bard", "ovate", "ogham",
        "nemeton", "cauldron", "henge", "avalon", "sidhe", "rath", "dun",
        "annwn", "tor", "cairn", "dolmen", "crannog", "samhain", "imbolc",
        "beltane", "rowan", "hawthorn", "elder", "holly", "wren", "hare",
        "salmon", "stag", "raven", "crane", "swan", "selkie", "kelpie",
        "claddagh", "triskelion", "spiral",
    ],
    # ── Mesoamerican / Andean ────────────────────────────────────────
    "mesoamerican": [
        "quetzal", "tlaloc", "coatlicue", "ehecatl", "tonatiuh", "mixcoatl",
        "itzamna", "kukulkan", "chaac", "ixchel", "hunahpu", "chichen",
        "palenque", "uxmal", "tulum", "copan", "tikal", "cenote", "nagual",
        "tonal", "tzolkin", "copal", "cacao", "peyote", "jaguar", "puma",
        "condor", "tapir", "coati", "capybara", "axolotl", "ocelot",
        "caiman", "toucan", "macaw", "quinoa", "guava", "papaya",
    ],
    # ── Science: math, physics, chem, bio, astronomy, geology ────────
    "science": [
        "vector", "tensor", "manifold", "torus", "lattice", "orbit",
        "prime", "axiom", "theorem", "gradient", "fourier", "euler",
        "fibonacci", "pascal", "fractal", "topology", "sheaf", "functor",
        "quark", "boson", "fermion", "photon", "plasma", "quantum",
        "entropy", "fusion", "electron", "neutrino", "muon", "hadron",
        "lepton", "meson", "gluon", "graviton", "tachyon", "resonance",
        "amplitude", "momentum", "velocity", "singularity", "planck",
        "valence", "catalyst", "solvent", "polymer", "isotope", "helium",
        "neon", "argon", "xenon", "krypton", "osmium", "iridium",
        "lithium", "cobalt", "ether", "graphene", "neuron", "axon",
        "cortex", "genome", "zygote", "spore", "mitosis", "dendrite",
        "synapse", "enzyme", "myelin", "quasar", "pulsar", "nebula",
        "nova", "magnetar", "eclipse", "equinox", "solstice", "parallax",
        "parsec", "magma", "basalt", "obsidian", "quartz", "granite",
        "caldera", "mantle", "geode",
    ],
    # ── Engineered math/geometry coinages (invented, registrable) ────
    "math_engineered": [
        "arity", "tuple", "valency", "affine", "parity", "spline", "radix",
        "modulo", "lemma", "quanta", "axio", "tuplo", "affina", "splina",
        "lemmo", "radia", "tensa", "scalo", "vectra", "matria", "normis",
        "logix", "calculi",
    ],
    "geometry_engineered": [
        "plinth", "soffit", "corbel", "lintel", "finial", "cupola",
        "dormer", "gable", "truss", "joist", "strut", "pylon", "spire",
        "vault", "annulus", "apothem", "helix", "torus", "prism", "corba",
        "spira", "toria", "prisma", "vertis",
    ],
    "physics_engineered": [
        "baryon", "axion", "stator", "pinion", "tappet", "fulcrum", "gyro",
        "isobar", "nuclide", "cation", "anion", "cathode", "anode", "hadra",
        "fermia", "stato", "gyra", "isota", "kineti", "inertis", "photis",
    ],
    "chem_engineered": [
        "ester", "amine", "ketone", "alkene", "phenol", "toluene", "xylene",
        "ligand", "chelate", "isomer", "tritium", "halogen", "zeolite",
        "estera", "amina", "ketona", "phenia", "zeoli", "valen",
    ],
    "bio_engineered": [
        "xylem", "phloem", "stoma", "pistil", "stamen", "anther", "sepal",
        "calyx", "bract", "tuber", "rhizome", "stolon", "cambium", "glial",
        "xyla", "phloa", "stomi", "myela", "floris", "faunis",
    ],
    "geo_engineered": [
        "loess", "karst", "cirque", "moraine", "drumlin", "esker", "kame",
        "tarn", "arete", "fjord", "estuary", "delta", "atoll", "guyot",
        "loessa", "cirqua", "moraina", "deltis", "magmis",
    ],
    # ── Short invented brand words (prime registrable coinages) ──────
    "brand_invented": [
        "lumo", "luva", "moki", "melo", "mavi", "mova", "kobi", "pumi",
        "buko", "pova", "mako", "lomi", "navo", "tovi", "kelo", "vori",
        "nimo", "levo", "rovi", "pulo", "teva", "zovi", "nela", "kova",
        "velo", "kovi", "meli", "lova", "kavi", "nomi", "luki", "teli",
        "nevi", "axio", "cupo", "pyla", "dorma", "finia", "linta", "apexa",
        "gabela", "scalo", "lepta", "tachy", "pinea", "loka", "vela",
    ],
    # ── Feelings & states ────────────────────────────────────────────
    "feelings": [
        "bliss", "calm", "cozy", "snug", "mirth", "zest", "glow", "beam",
        "serenity", "euphoria", "clarity", "vitality", "verve", "zeal",
        "ardor", "nimble", "keen", "swift", "agile", "radiant", "vibrant",
        "serene", "tender", "elated", "tranquil", "exuberant", "dauntless",
        "intrepid", "resolute", "tenacious", "valiant", "fervent",
        "sanguine", "ebullient", "buoyant", "stoic", "mercurial", "liminal",
        "sublime", "numinous", "ineffable",
    ],
    # ── Animals & creatures ──────────────────────────────────────────
    "animals": [
        "raven", "falcon", "lynx", "puma", "jaguar", "orca", "narwhal",
        "axolotl", "manta", "cobra", "condor", "osprey", "kestrel",
        "merlin", "ibis", "heron", "pangolin", "okapi", "fossa", "quetzal",
        "shoebill", "kakapo", "tapir", "saiga", "serval", "dugong",
        "wombat", "dingo", "wolf", "hawk", "stag", "bison", "viper",
        "mamba", "caiman", "mantis", "cicada", "scarab", "firefly", "moth",
    ],
    # ── Gemstones & minerals ─────────────────────────────────────────
    "gemstones": [
        "onyx", "opal", "topaz", "garnet", "jasper", "obsidian", "quartz",
        "mica", "pyrite", "fluorite", "citrine", "spinel", "zircon",
        "beryl", "corundum", "chalcedony", "malachite", "selenite",
        "apatite", "sunstone", "moonstone", "azurite", "peridot",
        "tanzanite", "tsavorite", "larimar", "sugilite",
    ],
    # ── Weather & cosmos ─────────────────────────────────────────────
    "weather_cosmos": [
        "aurora", "nimbus", "cirrus", "cumulus", "sirocco", "mistral",
        "zephyr", "gale", "squall", "tempest", "monsoon", "typhoon",
        "cyclone", "vortex", "solstice", "equinox", "corona", "eclipse",
        "nova", "nebula", "quasar", "zenith", "nadir", "meridian",
        "azimuth", "penumbra", "parallax", "parsec", "magnetar", "pulsar",
        "syzygy",
    ],
    # ── Food, drinks, herbs ──────────────────────────────────────────
    "food_herbs": [
        "nectar", "elixir", "ambrosia", "mead", "absinthe", "matcha",
        "kombucha", "tahini", "miso", "umami", "harissa", "dukkah",
        "zaatar", "mezcal", "aquavit", "cardamom", "saffron", "turmeric",
        "fenugreek", "sumac", "tamarind", "rooibos", "hibiscus", "verbena",
        "lavender", "rosemary", "yarrow", "mugwort", "anise", "fennel",
        "coriander", "cumin", "clove", "nutmeg", "mace", "mochi", "brioche",
        "truffle", "ganache", "nougat",
    ],
    # ── Places & geography ───────────────────────────────────────────
    "places": [
        "tundra", "savanna", "taiga", "steppe", "fjord", "atoll", "lagoon",
        "estuary", "delta", "mesa", "butte", "canyon", "caldera", "isthmus",
        "strait", "basin", "vale", "glen", "moor", "heath", "tor", "scarp",
        "bluff", "haven", "cape", "shoal", "cove", "veldt", "karoo",
        "pampa", "chaparral", "escarpment", "bight", "promontory",
    ],
    # ── Tech / pop-culture vibe words ────────────────────────────────
    "tech_vibes": [
        "nexus", "prism", "helix", "apex", "nova", "cipher", "echo",
        "pulse", "flux", "surge", "wave", "dawn", "dusk", "veil", "relic",
        "rift", "shard", "ember", "flare", "nimbus", "verge", "drift",
        "shift", "spark", "relay", "beacon", "signal", "trace", "cache",
        "token", "frame", "layer", "stack", "node", "mesh", "grid",
        "weave", "strand", "thread", "fiber", "link", "bridge", "forge",
        "vault", "atlas", "orbit", "comet", "quanta",
    ],
    # ── Colors & light ───────────────────────────────────────────────
    "colors": [
        "azure", "cyan", "cobalt", "indigo", "violet", "crimson", "vermeil",
        "ochre", "umber", "sienna", "viridian", "celadon", "chartreuse",
        "magenta", "fuchsia", "cerise", "carmine", "argent", "ebony",
        "ivory", "scarlet", "tawny", "cerulean", "gamboge", "rufous",
        "mauve", "wisteria", "periwinkle", "glaucous",
    ],
    # ── Abstract concept "dimensions" (wide associative nets) ────────
    # These work best as Datamuse anchors; they pull verbs/adjectives from
    # across the language rather than just nouns.
    "concept_untangle": [
        "unravel", "untie", "decode", "bypass", "simplify", "clarify",
        "parse", "decipher", "distill", "extract", "refine", "glean",
    ],
    "concept_agency": [
        "delegate", "proxy", "envoy", "fetch", "retrieve", "scout", "pilot",
        "dispatch", "emissary", "shepherd", "weave", "tether", "splice",
    ],
    "concept_motion": [
        "glide", "seamless", "fluid", "sleek", "hover", "kinetic", "nimble",
        "propel", "momentum", "velocity", "surge", "brisk", "tempo", "sync",
        "cadence", "pulse",
    ],
    "concept_foundation": [
        "axiom", "bedrock", "core", "genesis", "prime", "crux", "origin",
        "source", "anchor", "keystone", "lattice", "nexus",
    ],
    "concept_light": [
        "illuminate", "beacon", "lucid", "aura", "flare", "spark", "reveal",
        "glimmer", "radiant", "haven", "oasis", "calm",
    ],

    # ── Food: cuisines, dishes, desserts ─────────────────────────────
    "food": [
        "ramen", "udon", "soba", "miso", "mochi", "gyoza", "tempura",
        "bento", "onigiri", "sushi", "wonton", "dumpling", "congee",
        "laksa", "satay", "rendang", "bibimbap", "kimchi", "bulgogi",
        "pho", "banh", "curry", "masala", "biryani", "tandoori", "naan",
        "samosa", "dosa", "paneer", "falafel", "shawarma", "kebab",
        "hummus", "tagine", "couscous", "paella", "tapas", "gazpacho",
        "risotto", "gnocchi", "polenta", "pesto", "focaccia", "ciabatta",
        "panini", "calzone", "ravioli", "lasagna", "carbonara", "gelato",
        "tiramisu", "cannoli", "macaron", "souffle", "crepe", "brioche",
        "croissant", "baguette", "praline", "ganache", "nougat", "fondue",
        "raclette", "goulash", "pierogi", "borscht", "schnitzel", "strudel",
        "empanada", "ceviche", "arepa", "tamale", "churro", "mole",
        "gumbo", "jambalaya", "chowder", "brisket", "pastrami",
    ],
    "fruits": [
        "mango", "papaya", "guava", "lychee", "rambutan", "durian",
        "longan", "mangosteen", "jackfruit", "tamarind", "persimmon",
        "pomelo", "kumquat", "loquat", "feijoa", "quince", "medlar",
        "damson", "sloe", "mulberry", "elderberry", "lingonberry",
        "cloudberry", "gooseberry", "currant", "bilberry", "boysenberry",
        "plantain", "apricot", "nectarine", "clementine", "tangelo",
        "pomegranate", "fig", "date", "olive", "cherry", "plum", "peach",
        "guarana", "acai", "physalis", "carambola", "soursop", "cherimoya",
        "passionfruit", "dragonfruit", "starfruit",
    ],
    "vegetables": [
        "endive", "radicchio", "chicory", "fennel", "arugula", "watercress",
        "kohlrabi", "rutabaga", "parsnip", "salsify", "celeriac", "daikon",
        "taro", "yam", "cassava", "okra", "edamame", "shallot", "leek",
        "scallion", "ramps", "samphire", "purslane", "sorrel", "chard",
        "kale", "collard", "fava", "lentil", "chickpea", "artichoke",
        "asparagus", "broccoli", "romanesco", "squash", "pumpkin",
        "zucchini", "aubergine", "capsicum", "pimento", "jicama",
    ],
    "spices": [
        "saffron", "cardamom", "turmeric", "cumin", "coriander", "fenugreek",
        "nutmeg", "mace", "clove", "cinnamon", "cassia", "allspice",
        "anise", "fennel", "caraway", "ajwain", "nigella", "sumac",
        "zaatar", "harissa", "dukkah", "berbere", "ras", "garam", "tamari",
        "wasabi", "horseradish", "paprika", "cayenne", "chipotle", "ancho",
        "guajillo", "szechuan", "galangal", "lemongrass", "kaffir",
        "vanilla", "tonka", "annatto", "asafoetida",
    ],
    "drinks_cocktails": [
        "negroni", "martini", "mojito", "daiquiri", "margarita", "spritz",
        "aperol", "campari", "vermouth", "absinthe", "amaretto", "sambuca",
        "grappa", "limoncello", "ouzo", "raki", "arak", "mezcal", "tequila",
        "pisco", "cachaca", "rum", "bourbon", "rye", "scotch", "cognac",
        "armagnac", "calvados", "sake", "soju", "shochu", "baijiu", "mead",
        "cider", "kombucha", "kefir", "horchata", "lassi", "chai", "matcha",
        "cortado", "macchiato", "affogato", "ristretto", "nectar", "tonic",
    ],
    "tea_coffee": [
        "matcha", "sencha", "genmaicha", "hojicha", "gyokuro", "oolong",
        "pekoe", "darjeeling", "assam", "rooibos", "yerba", "mate",
        "tisane", "chamomile", "verbena", "hibiscus", "jasmine", "chai",
        "masala", "arabica", "robusta", "espresso", "ristretto", "cortado",
        "macchiato", "cappuccino", "affogato", "lungo", "crema", "barista",
        "robust", "harrar", "yirgacheffe", "geisha", "bourbon", "typica",
    ],

    # ── Water bodies: seas, rivers, lakes, currents ──────────────────
    "water_bodies": [
        "aegean", "ionian", "adriatic", "tyrrhenian", "ligurian", "baltic",
        "caspian", "azov", "marmara", "andaman", "arafura", "celebes",
        "sulu", "banda", "coral", "tasman", "sargasso", "caribbean",
        "labrador", "barents", "kara", "laptev", "chukchi", "weddell",
        "ross", "amundsen", "amazon", "congo", "nile", "niger", "zambezi",
        "limpopo", "orinoco", "parana", "mekong", "irrawaddy", "salween",
        "brahmaputra", "ganges", "indus", "danube", "rhine", "rhone",
        "volga", "dnieper", "yangtze", "yenisei", "ob", "lena", "amur",
        "fjord", "lagoon", "estuary", "bayou", "delta", "atoll", "shoal",
        "reef", "cove", "inlet", "sound", "strait", "gulf", "bight",
        "tarn", "loch", "mere", "billabong", "cenote", "geyser", "cascade",
    ],

    # ── Animals: birds, big cats, reptiles, sea, insects, mythic ─────
    "birds": [
        "kestrel", "merlin", "osprey", "harrier", "goshawk", "peregrine",
        "caracara", "buzzard", "kite", "harpy", "condor", "vulture",
        "heron", "egret", "bittern", "ibis", "spoonbill", "stork",
        "crane", "avocet", "godwit", "curlew", "plover", "lapwing",
        "puffin", "guillemot", "petrel", "fulmar", "gannet", "shearwater",
        "albatross", "tern", "skua", "auk", "kingfisher", "hoopoe",
        "bee", "oriole", "tanager", "warbler", "finch", "siskin", "linnet",
        "bunting", "wren", "lark", "pipit", "swift", "swallow", "martin",
        "nightjar", "quetzal", "toucan", "macaw", "lorikeet", "kakapo",
        "kea", "weka", "takahe", "hoatzin", "shoebill", "secretarybird",
    ],
    "big_cats": [
        "panther", "leopard", "jaguar", "cougar", "puma", "ocelot",
        "serval", "caracal", "lynx", "bobcat", "margay", "jaguarundi",
        "cheetah", "lion", "tiger", "snowcat", "clouded", "pallas",
    ],
    "reptiles": [
        "gecko", "iguana", "chameleon", "skink", "monitor", "basilisk",
        "anole", "agama", "tegu", "komodo", "cobra", "mamba", "viper",
        "adder", "boa", "python", "anaconda", "krait", "taipan", "racer",
        "moccasin", "copperhead", "sidewinder", "gharial", "caiman",
        "alligator", "crocodile", "terrapin", "tortoise", "tuatara",
    ],
    "sea_creatures": [
        "orca", "narwhal", "beluga", "manatee", "dugong", "porpoise",
        "marlin", "sailfish", "barracuda", "wahoo", "tarpon", "grouper",
        "snapper", "wrasse", "tang", "lionfish", "clownfish", "manta",
        "stingray", "nautilus", "cuttlefish", "octopus", "squid",
        "krill", "copepod", "anemone", "coral", "urchin", "starfish",
        "seahorse", "lamprey", "sturgeon", "remora", "marl", "kelp",
        "plankton", "medusa", "abalone", "limpet", "periwinkle", "whelk",
    ],
    "insects": [
        "mantis", "cicada", "firefly", "dragonfly", "damselfly", "mayfly",
        "lacewing", "weevil", "scarab", "beetle", "chafer", "longhorn",
        "ladybird", "aphid", "thrips", "cricket", "katydid", "locust",
        "grasshopper", "moth", "luna", "atlas", "monarch", "swallowtail",
        "fritillary", "skipper", "hairstreak", "admiral", "comma",
        "hornet", "bumblebee", "carpenter", "mason", "leafcutter",
        "termite", "antlion", "glowworm",
    ],
    "mythical_creatures": [
        "phoenix", "griffin", "chimera", "hydra", "kraken", "leviathan",
        "basilisk", "wyvern", "drake", "wyrm", "manticore", "cockatrice",
        "sphinx", "minotaur", "centaur", "satyr", "faun", "naiad", "dryad",
        "nymph", "siren", "harpy", "gorgon", "cyclops", "titan", "golem",
        "djinn", "ifrit", "roc", "garuda", "kirin", "qilin", "fenrir",
        "jotun", "valkyrie", "banshee", "selkie", "kelpie", "pooka",
        "kitsune", "tengu", "oni", "yokai", "wendigo", "thunderbird",
        "unicorn", "pegasus", "hippogriff", "salamander", "undine", "sylph",
    ],

    # ── Plants: trees, flowers, fungi, ferns, succulents ─────────────
    "trees": [
        "alder", "aspen", "beech", "birch", "cedar", "cypress", "elm",
        "fir", "hemlock", "hornbeam", "larch", "linden", "maple", "oak",
        "pine", "poplar", "rowan", "spruce", "sycamore", "willow", "yew",
        "acacia", "baobab", "banyan", "ginkgo", "sequoia", "redwood",
        "mahogany", "teak", "ebony", "sandalwood", "camphor", "eucalyptus",
        "jacaranda", "magnolia", "mimosa", "tamarisk", "juniper", "holly",
        "hawthorn", "blackthorn", "elder", "hazel", "walnut", "chestnut",
        "catalpa", "tupelo", "sassafras", "ironwood", "kapok",
    ],
    "flowers": [
        "lotus", "lily", "iris", "peony", "dahlia", "zinnia", "aster",
        "marigold", "cosmos", "poppy", "tulip", "crocus", "freesia",
        "anemone", "ranunculus", "camellia", "azalea", "magnolia",
        "jasmine", "gardenia", "frangipani", "plumeria", "orchid",
        "protea", "banksia", "lavender", "verbena", "foxglove", "lupine",
        "delphinium", "snapdragon", "hollyhock", "wisteria", "clematis",
        "honeysuckle", "primrose", "violet", "pansy", "petunia", "begonia",
        "amaryllis", "hyacinth", "narcissus", "daffodil", "bluebell",
        "edelweiss", "heather", "thistle", "yarrow", "celosia", "salvia",
    ],
    "fungi": [
        "morel", "chanterelle", "porcini", "shiitake", "enoki", "maitake",
        "oyster", "truffle", "cremini", "portobello", "lions", "reishi",
        "chaga", "cordyceps", "amanita", "russula", "bolete", "puffball",
        "lichen", "mycelium", "spore", "hyphae", "psilocybe", "matsutake",
    ],
    "ferns_mosses": [
        "fern", "bracken", "maidenhair", "polypody", "osmunda", "frond",
        "moss", "sphagnum", "lichen", "liverwort", "hornwort", "clubmoss",
        "horsetail", "fiddlehead", "spore", "thallus", "verdure", "loam",
    ],
    "succulents": [
        "agave", "aloe", "echeveria", "sedum", "sempervivum", "haworthia",
        "kalanchoe", "crassula", "jade", "lithops", "euphorbia", "yucca",
        "cactus", "saguaro", "opuntia", "cereus", "prickly", "barrel",
        "ocotillo", " aeonium",
    ],

    # ── Mountains: peaks & ranges ────────────────────────────────────
    "mountains": [
        "denali", "rainier", "shasta", "whitney", "hood", "baker",
        "olympus", "etna", "vesuvius", "blanc", "matterhorn", "eiger",
        "jungfrau", "monte", "elbrus", "kazbek", "ararat", "kilimanjaro",
        "kenya", "atlas", "toubkal", "aconcagua", "chimborazo", "cotopaxi",
        "fitzroy", "torres", "andes", "rockies", "sierra", "cascade",
        "pyrenees", "dolomites", "carpathian", "balkan", "ural", "altai",
        "tian", "pamir", "karakoram", "annapurna", "everest", "lhotse",
        "makalu", "nanga", "fuji", "aso", "tateyama", "cook", "ruapehu",
        "tabor", "sinai", "carmel", "hermon",
    ],

    # ── Neighborhoods, cities, islands ───────────────────────────────
    "neighborhoods": [
        "soho", "tribeca", "noho", "chelsea", "harlem", "bronx", "bowery",
        "gramercy", "dumbo", "bushwick", "marais", "montmartre", "pigalle",
        "bastille", "shoreditch", "soho", "camden", "brixton", "peckham",
        "kreuzberg", "mitte", "prenzlauer", "trastevere", "brera",
        "navigli", "gracia", "raval", "chueca", "alfama", "chiado",
        "shibuya", "shinjuku", "ginza", "harajuku", "nakameguro",
        "gangnam", "hongdae", "itaewon", "lankwai", "chelsea", "mission",
        "haight", "soma", "tribeca", "wynwood", "deepellum", "highland",
    ],
    "cities": [
        "kyoto", "osaka", "nara", "sapporo", "seoul", "busan", "taipei",
        "hanoi", "saigon", "bangkok", "phuket", "bali", "ubud", "jakarta",
        "manila", "macau", "lhasa", "kashgar", "samarkand", "bukhara",
        "tbilisi", "yerevan", "baku", "petra", "amman", "cairo", "luxor",
        "fez", "marrakesh", "tangier", "tunis", "dakar", "accra",
        "nairobi", "zanzibar", "lagos", "lisbon", "porto", "seville",
        "granada", "valencia", "bilbao", "lyon", "nice", "geneva",
        "lucerne", "verona", "siena", "bologna", "naples", "palermo",
        "athens", "santorini", "mykonos", "dubrovnik", "split", "kotor",
        "tallinn", "riga", "vilnius", "krakow", "prague", "vienna",
        "salzburg", "oslo", "bergen", "helsinki", "reykjavik",
    ],
    "islands": [
        "santorini", "mykonos", "corfu", "crete", "rhodes", "ibiza",
        "majorca", "capri", "sicily", "sardinia", "malta", "corsica",
        "madeira", "azores", "canary", "bali", "lombok", "java", "sumatra",
        "borneo", "palawan", "boracay", "okinawa", "jeju", "hainan",
        "phuket", "samui", "langkawi", "maldives", "zanzibar", "seychelles",
        "mauritius", "reunion", "comoros", "fiji", "tahiti", "bora",
        "samoa", "tonga", "vanuatu", "palau", "guam", "aruba", "curacao",
        "bonaire", "barbados", "tobago", "nevis", "antigua", "bermuda",
        "iceland", "faroe", "shetland", "orkney", "hebrides", "skye",
    ],

    # ── Pop culture: music genres, dances, art movements ─────────────
    "music_genres": [
        "techno", "house", "trance", "ambient", "dubstep", "garage",
        "jungle", "breakbeat", "electro", "synthwave", "vaporwave",
        "lofi", "trap", "drill", "grime", "reggae", "dancehall", "ska",
        "dub", "soul", "funk", "disco", "boogie", "motown", "blues",
        "jazz", "bebop", "swing", "ragtime", "bossa", "samba", "salsa",
        "merengue", "cumbia", "tango", "flamenco", "fado", "rumba",
        "calypso", "soca", "afrobeat", "highlife", "kwaito", "gqom",
        "raga", "qawwali", "gamelan", "klezmer", "polka", "zydeco",
        "bluegrass", "honky", "grunge", "punk", "metal", "indie", "shoegaze",
    ],
    "dances": [
        "tango", "salsa", "rumba", "samba", "mambo", "cha", "bolero",
        "flamenco", "fandango", "bachata", "merengue", "cumbia", "zouk",
        "kizomba", "foxtrot", "waltz", "quickstep", "jive", "lindy",
        "charleston", "swing", "jitterbug", "twist", "polka", "mazurka",
        "polonaise", "gavotte", "minuet", "bourree", "ceilidh", "reel",
        "jig", "hornpipe", "tarantella", "kathak", "bharata", "odissi",
        "hula", "haka", "capoeira", "krump", "voguing", "breakdance",
    ],
    "art_movements": [
        "baroque", "rococo", "neoclassic", "romantic", "realism",
        "impressionism", "pointillism", "fauvism", "cubism", "futurism",
        "dada", "surrealism", "bauhaus", "constructivism", "suprematism",
        "expressionism", "abstraction", "minimalism", "brutalism",
        "deco", "nouveau", "gothic", "renaissance", "mannerism", "ukiyo",
        "sumi", "fresco", "mosaic", "tessera", "intaglio", "etching",
        "lithograph", "gouache", "tempera", "encaustic", "chiaroscuro",
        "sfumato", "trompe", "vignette", "palette", "pigment", "patina",
    ],

    # ── Non-obvious: constellations, winds, textiles, nautical, etc. ─
    "constellations": [
        "orion", "lyra", "cygnus", "aquila", "draco", "ursa", "leo",
        "virgo", "libra", "scorpius", "sagittarius", "capricorn", "aries",
        "taurus", "gemini", "cancer", "pisces", "andromeda", "perseus",
        "cassiopeia", "cepheus", "auriga", "bootes", "corona", "hercules",
        "pegasus", "phoenix", "vela", "carina", "puppis", "centaurus",
        "lupus", "ara", "hydra", "corvus", "crater", "antlia", "pyxis",
        "volans", "tucana", "grus", "pavo", "indus", "norma", "circinus",
        "fornax", "caelum", "pictor", "reticulum", "horologium", "mensa",
    ],
    "winds": [
        "zephyr", "sirocco", "mistral", "khamsin", "harmattan", "levanter",
        "tramontane", "bora", "foehn", "chinook", "santaana", "monsoon",
        "etesian", "meltemi", "pampero", "williwaw", "squall", "gale",
        "gust", "breeze", "doldrums", "trade", "westerly", "easterly",
        "aquilo", "boreas", "notus", "eurus", "favonius",
    ],
    "textiles_fabrics": [
        "linen", "cotton", "wool", "cashmere", "merino", "alpaca", "mohair",
        "angora", "silk", "satin", "chiffon", "organza", "taffeta",
        "velvet", "velour", "corduroy", "denim", "twill", "chambray",
        "poplin", "oxford", "flannel", "tweed", "herringbone", "houndstooth",
        "damask", "brocade", "jacquard", "paisley", "ikat", "batik",
        "shibori", "calico", "muslin", "gauze", "voile", "georgette",
        "crepe", "jersey", "boucle", "tartan", "gingham", "seersucker",
    ],
    "nautical": [
        "anchor", "mast", "helm", "rudder", "keel", "bow", "stern",
        "starboard", "port", "galley", "cabin", "hull", "prow", "rigging",
        "halyard", "jib", "spinnaker", "mainsail", "boom", "tiller",
        "compass", "sextant", "astrolabe", "fathom", "knot", "league",
        "harbor", "wharf", "jetty", "pier", "quay", "lagoon", "reef",
        "schooner", "clipper", "galleon", "frigate", "sloop", "ketch",
        "yawl", "cutter", "dinghy", "skiff", "trireme", "armada", "regatta",
    ],
    "alchemy": [
        "alembic", "athanor", "crucible", "retort", "elixir", "tincture",
        "philosopher", "quintessence", "aether", "azoth", "vitriol",
        "cinnabar", "antimony", "mercury", "sulphur", "salt", "nigredo",
        "albedo", "rubedo", "citrinitas", "calcination", "sublimation",
        "distillation", "coagulation", "solvent", "menstruum", "amalgam",
        "transmute", " formula", "essence", "potion", "philtre", "arcanum",
    ],
    "architecture": [
        "atrium", "portico", "colonnade", "rotunda", "cupola", "dome",
        "arch", "vault", "buttress", "gargoyle", "spire", "steeple",
        "minaret", "pagoda", "ziggurat", "obelisk", "pylon", "pilaster",
        "cornice", "frieze", "pediment", "architrave", "capital", "plinth",
        "soffit", "corbel", "lintel", "transom", "mullion", "oriel",
        "loggia", "veranda", "pergola", "gazebo", "belvedere", "mezzanine",
        "clerestory", "nave", "apse", "transept", "narthex", "cloister",
        "facade", "parapet", "balustrade", "newel", "finial", "keystone",
    ],
    "virtues": [
        "valor", "honor", "grace", "mercy", "candor", "vigor", "ardor",
        "merit", "amity", "unity", "clarity", "charity", "verity",
        "purity", "fidelity", "humility", "serenity", "felicity",
        "audacity", "tenacity", "veracity", "sagacity", "alacrity",
        "equity", "probity", "rectitude", "fortitude", "gratitude",
        "aptitude", "prudence", "patience", "temperance", "diligence",
        "eloquence", "radiance", "brilliance", "resolve", "resilience",
    ],
    "tarot": [
        "arcana", "fool", "magician", "priestess", "empress", "emperor",
        "hierophant", "lovers", "chariot", "strength", "hermit", "wheel",
        "justice", "hanged", "temperance", "tower", "star", "moon", "sun",
        "judgement", "world", "wands", "cups", "swords", "pentacles",
        "oracle", "augur", "sibyl", "omen", "portent", "divine", "rune",
    ],
    "gem_colors": [
        "amber", "jade", "coral", "pearl", "ivory", "onyx", "jet",
        "ruby", "garnet", "carnelian", "amethyst", "emerald", "sapphire",
        "topaz", "citrine", "peridot", "aquamarine", "turquoise", "lapis",
        "malachite", "azurite", "opal", "moonstone", "sunstone", "tiger",
        "obsidian", "jasper", "agate", "chalcedony", "tourmaline", "spinel",
        "zircon", "beryl", "morganite", "kunzite", "tanzanite", "alexandrite",
    ],
    "perfume_notes": [
        "amber", "musk", "civet", "ambergris", "oud", "sandalwood",
        "vetiver", "patchouli", "labdanum", "benzoin", "myrrh", "frankincense",
        "bergamot", "neroli", "petitgrain", "yuzu", "iris", "violet",
        "tuberose", "jasmine", "ylang", "osmanthus", "mimosa", "linden",
        "vanilla", "tonka", "heliotrope", "cassis", "galbanum", "elemi",
        "cedarwood", "guaiac", "tolu", "styrax", "castoreum", "saffron",
    ],
    "wine_terms": [
        "terroir", "tannin", "cuvee", "reserva", "crianza", "grand",
        "premier", "cru", "vintage", "sommelier", "decant", "bouquet",
        "finish", "legs", "body", "merlot", "syrah", "shiraz", "malbec",
        "tempranillo", "sangiovese", "nebbiolo", "barolo", "chianti",
        "rioja", "riesling", "viognier", "chenin", "gewurz", "muscat",
        "grenache", "carignan", "mourvedre", "zinfandel", "pinot", "gamay",
    ],
    "metals_alloys": [
        "iron", "steel", "bronze", "brass", "copper", "tin", "zinc",
        "nickel", "cobalt", "chrome", "titanium", "tungsten", "platinum",
        "palladium", "rhodium", "iridium", "osmium", "ruthenium",
        "tantalum", "niobium", "vanadium", "molybdenum", "gallium",
        "indium", "bismuth", "antimony", "mercury", "silver", "gold",
        "pewter", "solder", "amalgam", "electrum", "invar", "nichrome",
        "babbitt", "monel", "inconel", "duralumin", "gunmetal",
    ],
    "tools_crafts": [
        "anvil", "forge", "bellows", "chisel", "mallet", "awl", "plane",
        "lathe", "vise", "clamp", "rasp", "file", "burin", "graver",
        "scriber", "caliper", "gauge", "plumb", "level", "square",
        "trowel", "spatula", "scalpel", "needle", "spindle", "shuttle",
        "loom", "bobbin", "spool", "skein", "kiln", "crucible", "ladle",
        "tongs", "auger", "gimlet", "bradawl", "spokeshave", "drawknife",
    ],
    "pottery_glass": [
        "kiln", "wheel", "glaze", "slip", "bisque", "celadon", "raku",
        "porcelain", "stoneware", "earthenware", "terracotta", "faience",
        "majolica", "delft", "shard", "sherd", "kintsugi", "crackle",
        "cobalt", "underglaze", "sgraffito", "burnish", "temper", "grog",
        "murano", "millefiori", "lampwork", "annealing", "blowpipe",
        "frit", "cullet", "cristallo", "opaline", "cameo",
    ],
    "typography": [
        "serif", "italic", "roman", "kerning", "ligature", "ascender",
        "descender", "baseline", "leading", "tracking", "glyph", "letterform",
        "majuscule", "minuscule", "uncial", "blackletter", "didone",
        "garamond", "bodoni", "didot", "caslon", "baskerville", "futura",
        "helvetica", "univers", "gotham", "georgia", "palatino", "optima",
        "fraktur", "cursive", "swash", "terminal", "counter", "aperture",
    ],
    "instruments": [
        "lyre", "harp", "lute", "cittern", "mandolin", "bouzouki", "sitar",
        "tanpura", "veena", "koto", "shamisen", "erhu", "guzheng", "pipa",
        "oud", "kora", "ngoni", "balafon", "marimba", "vibraphone",
        "celesta", "glockenspiel", "carillon", "ocarina", " pan",
        "shakuhachi", "duduk", "ney", "kaval", "bagpipe", "bodhran",
        "djembe", "darbuka", "tabla", "cajon", "bongo", "conga", "timpani",
        "theremin", "harmonium", "accordion", "concertina", "bandoneon",
    ],
    "festivals": [
        "holi", "diwali", "navratri", "onam", "pongal", "vesak", "obon",
        "tanabata", "hanami", "matsuri", "lantern", "qingming", "dragon",
        "carnival", "carnaval", "mardi", "fasching", "beltane", "samhain",
        "solstice", "equinox", "lammas", "yule", "fiesta", "feria",
        "ferragosto", "walpurgis", "midsummer", "nowruz", "songkran",
        "loi", "diwali", "hogmanay", "calan", "ostara", "litha", "mabon",
    ],
    "time_seasons": [
        "dawn", "dusk", "twilight", "gloaming", "aurora", "vesper",
        "matins", "noon", "midnight", "equinox", "solstice", "zenith",
        "epoch", "era", "eon", "aeon", "season", "harvest", "verdant",
        "estival", "hibernal", "vernal", "autumnal", "lunar", "solar",
        "tide", "ebb", "flux", "cycle", "interim", "interlude", "moment",
    ],
    "currencies_historical": [
        "florin", "ducat", "guilder", "thaler", "drachma", "denarius",
        "sestertius", "aureus", "solidus", "obol", "stater", "shekel",
        "dinar", "dirham", "doubloon", "escudo", "real", "peso", "guinea",
        "sovereign", "groat", "farthing", "shilling", "crown", "louis",
        "napoleon", "ecu", "livre", "lira", "ruble", "kopeck", "rupee",
        "anna", "mohur", "tael", "ryo", "mon", "cowrie",
    ],
    "mythical_places": [
        "avalon", "elysium", "arcadia", "valhalla", "asgard", "olympus",
        "shangri", "shambhala", "xanadu", "eldorado", "atlantis", "lemuria",
        "hyperborea", "thule", "camelot", "tirnanog", "annwn", "agartha",
        "cockaigne", "lyonesse", "ys", "brigadoon", "midgard", "vanaheim",
        "alfheim", "niflheim", "elysian", "empyrean", "cathay", "ophir",
        "zion", "eden", "arcady", "utopia", "erewhon",
    ],
}


def clean(word: str) -> str | None:
    """Lowercase, strip, accept only letters, length 3-14. Else None."""
    w = (word or "").lower().strip()
    return w if re.match(r"^[a-z]{3,14}$", w) else None


def all_words() -> dict[str, set[str]]:
    """Return {word: {categories}} for the full deduped corpus."""
    out: dict[str, set[str]] = {}
    for cat, words in CATEGORIES.items():
        for raw in words:
            w = clean(raw)
            if w:
                out.setdefault(w, set()).add(cat)
    return out


def select(names: list[str] | None) -> dict[str, set[str]]:
    """Return {word: {categories}} restricted to the given category names.

    None or empty -> the full corpus. Unknown names are ignored.
    """
    if not names:
        return all_words()
    wanted = {n.strip().lower() for n in names if n.strip()}
    out: dict[str, set[str]] = {}
    for cat, words in CATEGORIES.items():
        if cat.lower() not in wanted:
            continue
        for raw in words:
            w = clean(raw)
            if w:
                out.setdefault(w, set()).add(cat)
    return out


def category_names() -> list[str]:
    return list(CATEGORIES.keys())
