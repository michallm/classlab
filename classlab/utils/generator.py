import string

from django.contrib.auth.base_user import BaseUserManager
from django.utils.crypto import get_random_string

CHARACTERS = string.ascii_lowercase + string.digits


def generate_random_id(length=12) -> str:
    """Generate random string of given length that always starts with a letter"""
    return get_random_string(
        length=1,
        allowed_chars=string.ascii_lowercase,
    ) + get_random_string(
        length=length - 1,
        allowed_chars=CHARACTERS,
    )


def generate_random_password(length=12) -> str:
    """Generate random password of given length"""
    return BaseUserManager().make_random_password(length=length)


def generate_username(first_name):
    """Generate username from first name"""
    # revove special characters and polish diacritics
    to_replace = {
        "ą": "a",
        "ć": "c",
        "ę": "e",
        "ł": "l",
        "ń": "n",
        "ó": "o",
        "ś": "s",
        "ź": "z",
        "ż": "z",
        " ": "",
        "-": "",
        "_": "",
    }
    for key, value in to_replace.items():
        first_name = first_name.replace(key, value)
    return first_name.lower()
