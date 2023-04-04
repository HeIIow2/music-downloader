from dataclasses import dataclass, field
from typing import List


@dataclass
class DownloadResult:
    total: int = 0
    fail: int = 0
    error_message: str = None

    _error_message_list: List[str] = field(default_factory=list)

    @property
    def success(self) -> int:
        return self.total - self.fail

    @property
    def fatal_error(self) -> bool:
        return self.error_message is not None

    def merge(self, other: "DownloadResult"):
        if other.fatal_error:
            self._error_message_list.append(other.error_message)
            self.total += 1
            self.fail += 1
        else:
            self.total += other.total
            self.fail += other.fail
            self._error_message_list.extend(other._error_message_list)

    def __repr__(self):
        if self.fatal_error:
            return self.error_message
        return f"{self.fail} from {self.total} downloads failed."
