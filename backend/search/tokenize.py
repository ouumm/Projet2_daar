import re

WORD = re.compile(r"[^\W\d_]{3,}", re.UNICODE)  # mots alphabetiques de 3 lettres ou plus


def tokenize(text: str):
    return (w.lower() for w in WORD.findall(text))
