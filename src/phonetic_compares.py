import jellyfish

TITLE_THRESHOLD_LEVENSHTEIN = 1


def match_titles(title_1: str, title_2: str) -> (bool, int):
    distance = jellyfish.levenshtein_distance(title_1, title_2)
    return distance > 1, distance
