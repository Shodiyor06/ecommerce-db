def validate_name(text: str) -> bool:
    return text.replace(" ", "").isalpha()


def validate_email(email: str) -> bool:
    return "@" in email and "." in email.split("@")[1]


def validate_username(username: str) -> bool:
    return len(username) >= 3 and username.replace("_", "").isalnum()
