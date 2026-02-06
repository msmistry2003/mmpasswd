import secrets
import string
import threading
import pyperclip

def generate_password(length=16, use_upper=True, use_lower=True, use_digits=True, use_symbols=True):
    """Generates a secure random password."""
    chars = ""
    if use_lower: chars += string.ascii_lowercase
    if use_upper: chars += string.ascii_uppercase
    if use_digits: chars += string.digits
    if use_symbols: chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    if not chars:
        chars = string.ascii_letters + string.digits # Fallback
        
    return ''.join(secrets.choice(chars) for _ in range(length))

def check_password_strength(password):
    """
    Evaluates password strength.
    Returns: (score, label, color)
    Score: 0-4
    """
    if not password:
        return 0, "Empty", "gray"
        
    length = len(password)
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    score = 0
    if length >= 8: score += 1
    if length >= 12: score += 1
    if has_lower and has_upper: score += 1
    if has_digit and has_special: score += 1
    
    # Cap score at 4
    score = min(score, 4)
    
    if score == 0: return 1, "Very Weak", "#ef5350" # Red 400
    if score == 1: return 1, "Weak", "#ef5350"
    if score == 2: return 2, "Fair", "#ffa726" # Orange 400
    if score == 3: return 3, "Good", "#66bb6a" # Green 400
    if score == 4: return 4, "Strong", "#4caf50" # Green 500
    
    return 0, "Empty", "gray"

def secure_copy(text, timeout=30):
    """Copies text to clipboard and clears it after timeout."""
    pyperclip.copy(text)
    
    def clear():
        # Only clear if the clipboard still contains our text (to avoid clearing something user copied later)
        try:
            if pyperclip.paste() == text:
                pyperclip.copy("")
        except:
            pass
            
    threading.Timer(timeout, clear).start()
