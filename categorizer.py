import re

KEYWORDS = {
    "food": [
        "lunch",
        "dinner",
        "breakfast",
        "snack",
        "coffee",
        "jollibee",
        "mcdo",
        "restaurant",
        "grocery",
        "pizza",
        "burger",
        "milktea",
    ],
    "transport": [
        "grab",
        "taxi",
        "jeepney",
        "bus",
        "fuel",
        "gas",
        "parking",
        "toll",
        "mrt",
        "lrt",
        "fare",
    ],
    "bills": [
        "electric",
        "electricity",
        "water",
        "internet",
        "wifi",
        "rent",
        "load",
        "phone",
    ],
    "shopping": ["clothes", "shoes", "mall", "shopee", "lazada", "shirt"],
    "health": ["medicine", "doctor", "pharmacy", "clinic", "hospital", "vitamins"],
    "entertainment": ["movie", "netflix", "spotify", "game", "concert"],
}


def suggest_category(description: str) -> str:
    words = set(re.findall(r"[a-z]+", description.lower()))
    for category, keywords in KEYWORDS.items():
        if words & set(keywords):
            return category
    return "other"
