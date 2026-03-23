from dotenv import load_dotenv
import os

load_dotenv()

class Config:

    # ====================================
    # API
    # ====================================

    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    TOKEN = os.getenv("TOKEN")
    BASE_URL = "https://api.deepseek.com"

    # ====================================
    # MODEL SETTINGS
    # ====================================

    MODEL_NAME = "deepseek-chat"
    TEMPERATURE = 0.8
    MAX_TOKENS = 800

    # ====================================
    # SAVE DIRECTORY SETTINGS
    # ====================================

    SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saves")
    os.makedirs(SAVE_DIR, exist_ok=True)


    ROLES = [
        "student",
        "field_sorcerer",
        "special_grade_sorcerer",
        "clan_head",
        "clan_heir",
        "assistant_manager",
        "window"
    ]

    RELATIONSHIP_TYPES = [
        "unknown",
        "acquaintance",
        "ally",
        "rival",
        "enemy",
        "mentor",
        "student",
        "ward",
        "guardian",
        "superior",
        "subordinate",
        "senior",
        "junior",
        "colleague",
        "friend",
        "close_friend",
        "partner",
        "family",
        "complicated"
    ]

    RELATIONSHIP_TYPE_SUPERSEDES = {
        "acquaintance":     ["unknown"],
        "ally":             ["unknown", "acquaintance"],
        "friend":           ["unknown", "acquaintance", "ally"],
        "close_friend":     ["unknown", "acquaintance", "ally", "friend"],
        "rival":            ["unknown", "acquaintance"],
        "enemy":            ["unknown", "acquaintance", "rival"],
        "mentor":           ["unknown", "acquaintance", "student"],
        "student":          ["unknown", "acquaintance", "mentor"],
        "colleague":        ["unknown", "acquaintance"],
        "complicated":      ["unknown"],  # complicated coexists with everything
        "family":           ["unknown"],  # family coexists with everything
        "ward":             ["unknown", "acquaintance", "guardian"],
        "guardian":         ["unknown", "acquaintance", "ward"],
        "superior":         ["unknown", "acquaintance", "subordinate"],
        "subordinate":      ["unknown", "acquaintance", "superior"],
        "senior":           ["unknown", "acquaintance", "junior"],
        "junior":           ["unknown", "acquaintance", "senior"],
        "partner":          ["unknown", "acquaintance", "ally", "friend", "close_friend"]
    }

    # ====================================
    # STAT BUILDING CONSTANTS
    # ====================================

    GRADES = [
        "grade_4",
        "grade_3",
        "grade_2",
        "grade_1",
        "special_grade"
    ]

    PERSONALITIES = [
        "disciplined",
        "reserved",
        "impulsive",
        "aggressive",
        "analytical",
        "peaceful"
    ]

    ORIGINS = [
        "clan",
        "independent",
        "student",
        "awakened"
    ]

    PERSONALITY_TYPES = {
        "disciplined": {"ce_mod": -5,  "control_mod": 15,  "stability_mod": 1},
        "reserved":    {"ce_mod": -10, "control_mod": 10,  "stability_mod": 1},
        "impulsive":   {"ce_mod": 15,  "control_mod": -10, "stability_mod": -2},
        "aggressive":  {"ce_mod": 5,   "control_mod": 5,   "stability_mod": -2},
        "analytical":  {"ce_mod": 0,   "control_mod": 10,  "stability_mod": 1},
        "peaceful":    {"ce_mod": -10, "control_mod": 0,   "stability_mod": 3},
    }

    GRADE_BANDS = {
        "grade_4":       {"ce": (50, 75),   "control": (20, 50), "stability_base": 3},
        "grade_3":       {"ce": (65, 90),   "control": (30, 55), "stability_base": 4},
        "semi_grade_2":  {"ce": (70, 100),  "control": (40, 60), "stability_base": 5},
        "grade_2":       {"ce": (85, 110),  "control": (45, 70), "stability_base": 6},
        "semi_grade_1":  {"ce": (90, 120),  "control": (55, 75), "stability_base": 6},
        "grade_1":       {"ce": (100, 130), "control": (65, 90), "stability_base": 7},
        "special_grade": {"ce": (125, 160), "control": (80, 100),"stability_base": 8},
    }
    GRADE_CONVERSION = {
        "none": 0,
        "grade_4": 1,
        "grade_3": 2,
        "semi_grade_2": 3,
        "grade_2": 4,
        "semi_grade_1": 5,
        "grade_1": 6,
        "special_grade": 7
    }

    ORIGIN_MODIFIERS = {
        "clan":      {"ce_mod": 5,  "control_mod": 5},
        "student":   {"ce_mod": -5, "control_mod": -5},
        "awakened":  {"ce_mod": 0,  "control_mod": -10},
        "independent": {"ce_mod": 0, "control_mod": 0},
    }

    CE_DELTA = {
        "none":             0,
        "minor":            10,
        "moderate":         20,
        "major":            40,
        "domain_expansion": 100,
    }

    PASSIVE_REGEN_RATE = 0.01  # 1% of max CE per turn

    ACTIVE_REGEN = {
        "sleep":      1.0,   # full restore
        "meditate":   0.4,   # 40% restore
        "rest":       0.2,   # 20% restore
        "breathwork": 0.15,  # 15% restore
        "eat":        0.05,  # 5% restore
    }

    ACTIVE_REGEN_KEYWORDS = {
        "sleep":      ["sleep", "slept", "rest for the night", "go to bed", "pass out"],
        "meditate":   ["meditate", "clear my mind", "centre myself", "center myself", "focus my energy"],
        "rest":       ["rest", "sit down", "take a break", "recover", "catch my breath"],
        "breathwork": ["breathe", "breathing", "exhale", "inhale", "calm down"],
        "eat":        ["eat", "drink", "food", "meal", "snack"],
    }
    PRESSURE_MULTIPLIERS = {
        "none": 0,
        "minor": 0.05,
        "moderate": 0.10,
        "major": 0.20,
        "domain_expansion": 0.60,
    }

    # ====================================
    # DISCORD IDS
    # ====================================

    GUILD_ID = 1483657481115926660

    CATEGORIES = {
        "🔴 Tokyo": 1483680290181480468,
        "🟠 Tokyo Landmarks": 1483836792951144650,
        "🟡 Other Locales": 1483834622033789018,
        "🟢 Jujutsu Society": 1483832496612442202,
        "🔵 Mission Sites": 1483837326319947839,
        "🟣 The Garden": 1483827015667945544,
        "Logs": 1483841311864918121
    }

    LOCATION_CHANNELS = {
        "shibuya": 1483680342140387349,
        "shinjuku": 1483832539641806919,
        "harajuku": 1483833996336037932,
        "roppongi": 1483834014900027495,
        "chiyoda": 1483834112296091738,
        "nerima": 1483834192528937192,
        "nakano": 1483834272791007314,
        "minato": 1483836027998048488,
        "shibuya_crossing": 1483833955097772143,
        "shibuya_station": 1483833974294839429,
        "shinjuku_station": 1483836262170492949,
        "kabuchiko": 1483835827053138010,
        "roppongi_hills": 1483836084592054364,
        "meiji_shrine": 1483834776854200493,
        "kyoto": 1483834661036757156,
        "sendai": 1483834688844988489,
        "gachinko_fight_club": 1483835864567120102,
        "tokyo_jujutsu_high": 1483832589650235493,
        "kyoto_jujutsu_high": 1483832615336284343,
        "tombs_of_the_star": 1483832644948201483,
        "tombs_of_the_star_corridor": 1483835542314553474,
        "gojo_estate": 1483835655917277234,
        "zenin_estate": 1483835673227038880,
        "kamo_estate": 1483835686778835044,
        "takahashi_estate": 1483835703728017409,
        "abandoned_building": 1483837617278812331,
        "alleyway": 1483839077139742910, 
        "cursed_artifact_vault": 1483838884940087297,
        "grade_school": 1483838628667981905,
        "greenhouse": 1483838553229230222,
        "high_school": 1483838642576294100,
        "hospital": 1483838996735066244,
        "hostel": 1483838676839698455,
        "love_hotel": 1483838610376491080,
        "maintenance_room": 1483839234078019684,
        "museum": 1483838656534937713,
        "nightclub": 1483839305456685177,
        "platform": 1483839324788359179,
        "sewer": 1483838566571184308,
        "shopping_mall": 1483839383932239933,
        "skyscraper_construction_site": 1483838719436783707,
        "underground_tunnel": 1483838587186184232,
        "warehouse": 1485094071767797840
    }

    LOG_CHANNELS = {
        605781662390943745: 1483841404038942760,
        683029047672176711: 1483841425647866038,
        747569767325630506: 1485346940362428647
    }

    LOBBY_CHANNEL = 1483657482105651202

    PLAYERS = {
        605781662390943745: "Mitsuki",
        683029047672176711: "Xiomara",
        747569767325630506: "Day"
    }