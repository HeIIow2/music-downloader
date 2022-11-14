import jellyfish
import string

TITLE_THRESHOLD_LEVENSHTEIN = 2
UNIFY_TO = " "


def unify_punctuation(to_unify: str) -> str:
    for char in string.punctuation:
        to_unify = to_unify.replace(char, UNIFY_TO)
    return to_unify


def remove_feature_part_from_track(title: str) -> str:
    if ")" != title[-1]:
        return title
    if "(" not in title:
        return title

    return title[:title.index("(")]


def modify_title(to_modify: str) -> str:
    to_modify = to_modify.strip()
    to_modify = to_modify.lower()
    to_modify = remove_feature_part_from_track(to_modify)
    to_modify = unify_punctuation(to_modify)
    return to_modify


def match_titles(title_1: str, title_2: str):
    title_1, title_2 = modify_title(title_1), modify_title(title_2)
    distance = jellyfish.levenshtein_distance(title_1, title_2)
    return distance > TITLE_THRESHOLD_LEVENSHTEIN, distance


def match_artists(artist_1, artist_2: str):
    if type(artist_1) == list:
        distances = []

        for artist_1_ in artist_1:
            match, distance = match_titles(artist_1_, artist_2)
            if not match:
                return match, distance

            distances.append(distance)
        return True, min(distances)
    return match_titles(artist_1, artist_2)
