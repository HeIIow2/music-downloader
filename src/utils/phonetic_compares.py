import jellyfish
import string

TITLE_THRESHOLD_LEVENSHTEIN = 2
UNIFY_TO = " "


def unify_punctuation(to_unify: str) -> str:
    for char in string.punctuation:
        to_unify = to_unify.replace(char, UNIFY_TO)
    return to_unify


def match_titles(title_1: str, title_2: str) -> (bool, int):
    title_1, title_2 = unify_punctuation(title_1).lower(), unify_punctuation(title_2).lower()
    distance = jellyfish.levenshtein_distance(title_1, title_2)
    return distance > TITLE_THRESHOLD_LEVENSHTEIN, distance


def match_artists(artist_1, artist_2: str) -> (bool, int):
    if type(artist_1) == list:
        distances = []

        for artist_1_ in artist_1:
            match, distance = match_titles(artist_1_, artist_2)
            if not match:
                return match, distance

            distances.append(distance)
        return True, min(distances)
    return match_titles(artist_1, artist_2)
