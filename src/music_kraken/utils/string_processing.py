from transliterate.exceptions import LanguageDetectionError
from transliterate import translit

from pathvalidate import sanitize_filename


def unify(string: str) -> str:
    """
    returns a unified str, to make comparisons easy.
    a unified string has the following attributes:
     - is lowercase
    """

    try:
        string = translit(string, reversed=True)
    except LanguageDetectionError:
        pass

    return string.lower()


def fit_to_file_system(string: str) -> str:
    string = string.strip()

    while string[0] == ".":
        if len(string) == 0:
            return string

        string = string[1:]

    string = string.replace("/", "|").replace("\\", "|")

    string = sanitize_filename(string)

    return string
