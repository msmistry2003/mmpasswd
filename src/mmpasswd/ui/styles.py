# shared styles and constants

THEMES = {
    "Dark": {
        "mode": "Dark",
        "colors": {
            "bg": "#0F1419",
            "sidebar": "#1A1F2E",
            "primary": "#5865F2",
            "primary_hover": "#4752C4",
            "danger": "#FF4444",
            "danger_hover": "#CC3333",
            "text": "#FFFFFF",
            "text_dim": "#888888",
            "text_button": "#FFFFFF",
            "input_bg": "#1A1F2E",
            "success": "#4CAF50",
            "warning": "#FF8C00",
        }
    },
    "Light": {
        "mode": "Light",
        "colors": {
            "bg": "#F5F5F7",
            "sidebar": "#FFFFFF",
            "primary": "#007AFF",
            "primary_hover": "#0056B3",
            "danger": "#FF3B30",
            "danger_hover": "#C92A1E",
            "text": "#000000",
            "text_dim": "#555555",
            "text_button": "#FFFFFF",
            "input_bg": "#E5E5EA",
            "success": "#34C759",
            "warning": "#FF9500",
        }
    }
}

# Current active colors - defaults to Midnight
COLORS = THEMES["Dark"]["colors"].copy()

WEBSITE_ICONS = {
    "gmail": "📧", "google": "🔍", "facebook": "👤", "twitter": "🐦",
    "instagram": "📷", "linkedin": "💼", "amazon": "🛒", "apple": "🍎",
    "microsoft": "🪟", "github": "🐙", "youtube": "🎥", "netflix": "🎬",
    "spotify": "🎵", "discord": "💬", "whatsapp": "💬", "telegram": "📱",
    "bank": "🏦", "paypal": "💳", "stripe": "💳", "crypto": "₿",
    "wallet": "👛", "password": "🔐", "vault": "🔒", "security": "🛡️"
}

def get_website_icon(name):
    name_lower = name.lower()
    return next((v for k, v in WEBSITE_ICONS.items() if k in name_lower), "🔐")
