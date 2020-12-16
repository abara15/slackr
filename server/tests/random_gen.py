import string
import random
import datetime


def random_string(string_length=10):
    """Generates a random string of length 'string_length', default length is 10."""
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(string_length))


def random_date():
    """Returns the current datetime."""
    return datetime.datetime.now()
