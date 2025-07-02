import random
import string
import secrets
import re
import hashlib
import zxcvbn
from typing import Optional

def transform_name(name_part: str, level: int = 2) -> str:
    """Transform name parts with different security levels"""
    if not name_part:
        return ""
    
    transformed = name_part.lower()
    
    # Level 1: Basic transformations (still somewhat recognizable)
    if level >= 1:
        transformed = transformed.replace('a', '@').replace('e', '3').replace('i', '!')
    
    # Level 2: Moderate transformations (less recognizable)
    if level >= 2:
        if len(transformed) > 2:
            # Reverse every other character
            transformed = ''.join([c if i % 2 == 0 else transformed[i-1] for i, c in enumerate(reversed(transformed))])
        # Add random capitalization
        transformed = ''.join(c.upper() if random.random() > 0.7 else c for c in transformed)
    
    # Level 3: Heavy transformations (barely recognizable)
    if level >= 3:
        transformed = ''.join(random.choice('@#$%&*+-=_') + c for c in transformed)
        transformed = transformed[-12:]  # Keep last 12 characters
    
    return transformed

def generate_name_based_password(
    name_part1: str,  # City name
    name_part2: str,  # Catchy word (animal/bird/flower/etc)
    length: int = 12,
    complexity: int = 2,  # 1=simple, 2=moderate, 3=complex
    include_random: bool = True
) -> str:
    """
    Generate memorable password based on city + word combinations
    Examples:
    Montreal + Chicken → KendrealGhicken827&
    Toronto + Blue → GofontoFlue023*&
    """
    # Transform city name
    if complexity >= 2:
        # Moderate transformation: reverse first half and capitalize
        city_part = name_part1.lower()
        half = len(city_part) // 2
        transformed_city = city_part[half:][::-1] + city_part[:half]
        transformed_city = transformed_city.capitalize()
    else:
        # Simple transformation: just capitalize
        transformed_city = name_part1.capitalize()

    # Transform the catchy word
    word_part = name_part2.lower()
    if complexity >= 2:
        # Replace vowels with similar-looking numbers/symbols
        vowel_map = {'a': '@', 'e': '3', 'i': '1', 'o': '0', 'u': 'v'}
        transformed_word = ''.join(vowel_map.get(c, c) for c in word_part)
        # Capitalize random letters
        if complexity >= 3:
            transformed_word = ''.join(
                c.upper() if random.random() > 0.7 else c 
                for c in transformed_word
            )
    else:
        transformed_word = word_part.capitalize()

    # Combine the parts
    password = transformed_city + transformed_word

    # Add random characters if requested
    if include_random:
        # Add 2-4 random digits
        digits = ''.join(random.choice(string.digits) for _ in range(random.randint(2,4)))
        # Add 1-2 special characters
        specials = ''.join(random.choice('!@#$%&*+-=_') for _ in range(random.randint(1,2)))
        password += digits + specials

    # Ensure length requirement
    if len(password) > length:
        password = password[:length]
    elif len(password) < length:
        # Add extra random characters if too short
        extra = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) 
                     for _ in range(length - len(password)))
        password += extra

    # Final shuffle for security
    password_list = list(password)
    random.shuffle(password_list)
    password = ''.join(password_list)

    return password

def generate_random_password(
    length: int = 12,
    include_uppercase: bool = True,
    include_lowercase: bool = True,
    include_digits: bool = True,
    include_special: bool = True,
    exclude_similar: bool = True,
    exclude_ambiguous: bool = True
) -> str:
    """Generate a random password with customizable parameters"""
    character_sets = []
    
    if include_lowercase:
        character_sets.append(string.ascii_lowercase)
    if include_uppercase:
        character_sets.append(string.ascii_uppercase)
    if include_digits:
        character_sets.append(string.digits)
    if include_special:
        character_sets.append(string.punctuation)
    
    if not character_sets:
        raise ValueError("At least one character set must be included")
    
    # Characters to exclude
    excluded_chars = ""
    if exclude_similar:
        excluded_chars += "l1Io0O"
    if exclude_ambiguous:
        excluded_chars += "{}[]()/\\'\"`~,;:.<>"
    
    # Filter character sets
    filtered_sets = []
    for charset in character_sets:
        filtered = [c for c in charset if c not in excluded_chars]
        if filtered:
            filtered_sets.append(''.join(filtered))
    
    password = []
    # Ensure at least one character from each selected set
    for charset in filtered_sets:
        password.append(secrets.choice(charset))
    
    # Fill the rest of the password
    all_chars = ''.join(filtered_sets)
    password.extend(secrets.choice(all_chars) for _ in range(length - len(password)))
    
    # Shuffle to avoid predictable patterns
    random.shuffle(password)
    
    return ''.join(password)

def generate_passphrase(
    word_count: int = 4,
    separator: str = "-",
    capitalize: bool = True,
    add_number: bool = True,
    name_part1: Optional[str] = None,
    name_part2: Optional[str] = None
) -> str:
    """Generate a memorable passphrase with optional name parts"""
    words = [
        "apple", "banana", "carrot", "dog", "elephant", "flower", "giraffe",
        "house", "igloo", "jungle", "kangaroo", "lion", "mountain", "night",
        "ocean", "penguin", "queen", "river", "sun", "tree", "umbrella",
        "volcano", "water", "xylophone", "yacht", "zebra"
    ]
    
    selected_words = [secrets.choice(words) for _ in range(word_count)]
    
    # Add transformed name parts if provided
    if name_part1:
        selected_words.append(transform_name(name_part1, 1))
    if name_part2:
        selected_words.append(transform_name(name_part2, 1))
    
    if capitalize:
        selected_words = [word.capitalize() for word in selected_words]
    
    passphrase = separator.join(selected_words)
    
    if add_number:
        passphrase += str(secrets.randbelow(90) + 10)  # 10-99
    
    return passphrase

def generate_pin(length: int = 6) -> str:
    """Generate a numeric PIN"""
    if length < 4:
        raise ValueError("PIN length should be at least 4 digits")
    return ''.join(secrets.choice(string.digits) for _ in range(length))

def check_password_strength(password: str) -> dict:
    """Check password strength using zxcvbn"""
    result = zxcvbn.zxcvbn(password)
    return {
        "score": result["score"],
        "feedback": result["feedback"],
        "crack_time": result["crack_times_display"]["offline_slow_hashing_1e4_per_second"],
        "guesses": result["guesses"]
    }

def hash_password(password: str, algorithm: str = "sha256") -> str:
    """Hash a password using the specified algorithm"""
    hasher = hashlib.new(algorithm)
    hasher.update(password.encode('utf-8'))
    return hasher.hexdigest()

def validate_password_rules(password: str, rules: dict) -> dict:
    """Validate password against specific rules"""
    errors = []
    
    if rules.get("min_length") and len(password) < rules["min_length"]:
        errors.append(f"Password too short (min {rules['min_length']} chars)")
    
    if rules.get("require_upper") and not re.search(r'[A-Z]', password):
        errors.append("Password must contain uppercase letters")
    
    if rules.get("require_lower") and not re.search(r'[a-z]', password):
        errors.append("Password must contain lowercase letters")
    
    if rules.get("require_digit") and not re.search(r'[0-9]', password):
        errors.append("Password must contain digits")
    
    if rules.get("require_special") and not re.search(r'[^a-zA-Z0-9]', password):
        errors.append("Password must contain special characters")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }