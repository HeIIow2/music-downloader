from types import FunctionType
from functools import wraps

from typing import Dict

class Lake:
    def __init__(self):
        self.redirects: Dict[int, int] = {}
        self.id_to_object: Dict[int, object] = {}

    def get_real_object(self, db_object: object) -> object:
        _id = id(db_object)
        while _id in self.redirects:
            _id = self.redirects[_id]

        try:
            return self.id_to_object[_id]
        except KeyError:
            self.add(db_object)
            return db_object

    def add(self, db_object: object):
        self.id_to_object[id(db_object)] = db_object

    def override(self, to_override: object, new_db_object: object):
        self.redirects[id(to_override)] = id(new_db_object)
        if id(to_override) in self.id_to_object:
            del self.id_to_object[id(to_override)]


lake = Lake()


def wrapper(method):
    @wraps(method)
    def wrapped(*args, **kwargs):
        return method(*(lake.get_real_object(args[0]), *args[1:]), **kwargs)
    return wrapped



class BaseClass:
    def _risky_merge(self, to_replace):
        lake.override(to_replace, self)


class MetaClass(type):
    def __new__(meta, classname, bases, classDict):
        bases = (*bases, BaseClass)
        newClassDict = {}

        for attributeName, attribute in classDict.items():
            if isinstance(attribute, FunctionType) and attributeName not in ("__new__", "__init__"):
                attribute = wrapper(attribute)
            newClassDict[attributeName] = attribute

        for key, value in object.__dict__.items( ):
            if hasattr( value, '__call__' ) and value not in newClassDict and key not in ("__new__", "__init__"):
                newClassDict[key] = wrapper(value)

        new_instance = type.__new__(meta, classname, bases, newClassDict)

        lake.add(new_instance)

        return new_instance