import hashlib
import base64

import click


def encode(prompt: str, salt: str):
    encoded = f"{salt}@{prompt}".encode()
    encoded = hashlib.sha256(encoded).digest()
    encoded = base64.b64encode(encoded)
    encoded = encoded.translate(bytes.maketrans(b"+/=", b"$%@"))
    return f"{encoded.decode()}MANGrove_123"


def gen_password(encoded: str, char=1, digit=3, lower=4, upper=4):
    counter = {0b000: char, 0b001: digit, 0b010: lower, 0b100: upper}
    total = char + digit + lower + upper

    rv = ""
    for ch in encoded:
        t = ch.isupper() << 2 | ch.islower() << 1 | ch.isdigit()
        if not counter[t]:
            continue

        counter[t] -= 1
        rv += ch
        if len(rv) == total:
            break
    return rv


@click.command
@click.argument("prompt", default="mangrove")
@click.option("--salt", "-s", default="salt")
def main(prompt, salt):
    password = gen_password(encode(prompt, salt))
    print(password)


if __name__ == "__main__":
    main()
