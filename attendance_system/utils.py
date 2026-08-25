import random
import string
from .models import User


def generate_username(prefix):
    while True:
        username = prefix + ''.join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=6
            )
        )
        if not User.objects.filter(username=username).exists():
            return username


def generate_password():
    chars = (
        string.ascii_letters +
        string.digits +
        "@#$%"
    )
    return ''.join(
        random.choices(chars, k=8)
    )