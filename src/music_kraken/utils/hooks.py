from typing import List, Iterable, Dict, TypeVar, Generic, Iterator, Any, Type
from enum import Enum
from dataclasses import dataclass
from collections import defaultdict


class HookEventTypes(Enum):
    pass


@dataclass
class Event:
    target: Any


class Hooks:
    def __init__(self, target) -> None:
        self.target = target

        self._callbacks: Dict[HookEventTypes, List[callable]] = defaultdict(list)

    def add_event_listener(self, event_type: HookEventTypes, callback: callable):
        self._callbacks[event_type].append(callback)

    def trigger_event(self, event_type: HookEventTypes, *args, **kwargs):
        event: Event = Event(target=self.target)

        for callback in self._callbacks[event_type]:
            callback(event, *args, **kwargs)
