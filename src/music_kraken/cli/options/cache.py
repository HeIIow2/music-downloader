from logging import getLogger

from ...connection.cache import Cache


def clear_cache():
    """
    Deletes the cache.
    :return:
    """

    Cache("main", getLogger("cache")).clear()


def clean_cache():
    """
    Deletes the outdated cache. (all expired cached files, and not indexed files)
    :return:
    """

    Cache("main", getLogger("cache")).clean()
