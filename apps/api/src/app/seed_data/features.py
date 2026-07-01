"""Curated feature pool used to seed the `features` table and to decide, per variant,
which features to attach. `category` and `tier` are seed-time metadata only -- they are
not persisted, they just help `pick_features_for` choose a realistic, segment-appropriate
spread instead of a random one.
"""

# (name, category, tier) -- tier "basic" features appear across all segments,
# "advanced" features are reserved for mid/premium/luxury/ev cars.
FEATURE_POOL = [
    # Safety
    ("ABS with EBD", "safety", "basic"),
    ("Dual Front Airbags", "safety", "basic"),
    ("Rear Parking Sensors", "safety", "basic"),
    ("Rear View Camera", "safety", "basic"),
    ("Hill Hold Assist", "safety", "basic"),
    ("ISOFIX Child Seat Mounts", "safety", "basic"),
    ("Electronic Stability Control", "safety", "advanced"),
    ("Hill Descent Control", "safety", "advanced"),
    ("TPMS (Tyre Pressure Monitoring)", "safety", "advanced"),
    ("360-Degree Camera", "safety", "advanced"),
    ("ADAS (Level 2)", "safety", "advanced"),
    ("Automatic Emergency Braking", "safety", "advanced"),
    ("Lane Keep Assist", "safety", "advanced"),
    ("Blind Spot Monitor", "safety", "advanced"),
    # Comfort
    ("Manual Air Conditioning", "comfort", "basic"),
    ("Power Windows", "comfort", "basic"),
    ("Keyless Entry with Push Button Start", "comfort", "basic"),
    ("Automatic Climate Control", "comfort", "advanced"),
    ("Rear AC Vents", "comfort", "advanced"),
    ("Ventilated Front Seats", "comfort", "advanced"),
    ("Heated Front Seats", "comfort", "advanced"),
    ("Power Adjustable Driver Seat", "comfort", "advanced"),
    ("Cruise Control", "comfort", "advanced"),
    ("Adaptive Cruise Control", "comfort", "advanced"),
    ("Rain-Sensing Wipers", "comfort", "advanced"),
    ("Wireless Phone Charger", "comfort", "advanced"),
    # Infotainment
    ("Basic Audio System with USB/Bluetooth", "infotainment", "basic"),
    ("Touchscreen Infotainment System", "infotainment", "basic"),
    ("Wireless Android Auto & Apple CarPlay", "infotainment", "advanced"),
    ("Connected Car Tech (App-Based)", "infotainment", "advanced"),
    ("Premium Sound System (Harman/Bose/JBL)", "infotainment", "advanced"),
    ("Digital Instrument Cluster", "infotainment", "advanced"),
    ("Head-Up Display", "infotainment", "advanced"),
    ("Ambient Interior Lighting", "infotainment", "advanced"),
    # Exterior
    ("Halogen Headlamps", "exterior", "basic"),
    ("Body-Colored ORVMs with Turn Indicators", "exterior", "basic"),
    ("LED Projector Headlamps", "exterior", "advanced"),
    ("LED DRLs", "exterior", "advanced"),
    ("Alloy Wheels", "exterior", "advanced"),
    ("Sunroof", "exterior", "advanced"),
    ("Panoramic Sunroof", "exterior", "advanced"),
    ("Roof Rails", "exterior", "advanced"),
]

# (min, max) feature count per segment -- entry/economy cars are feature-sparse,
# premium/luxury/ev cars come loaded.
RICHNESS_TIER_COUNTS = {
    "entry": (4, 6),
    "economy": (6, 9),
    "mid": (9, 13),
    "premium": (13, 17),
    "luxury": (17, 22),
    "ev": (12, 18),
}
