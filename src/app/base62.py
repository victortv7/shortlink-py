

BASE62_ALPHABET = tuple("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
BASE62_LEN = 62
BASE62_DICT = dict((c, v) for v, c in enumerate(BASE62_ALPHABET))


def encode(num: int) -> str:
    if not num:
        return BASE62_ALPHABET[0]

    encoding = ""
    while num:
        num, rem = divmod(num, BASE62_LEN)
        encoding = BASE62_ALPHABET[rem] + encoding
    return encoding

def decode(base62_str: str) -> int:
    num = 0
    for char in base62_str:
        num = num * BASE62_LEN + BASE62_DICT[char]
    return num