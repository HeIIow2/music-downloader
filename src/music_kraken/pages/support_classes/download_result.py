from dataclasses import dataclass, field
from typing import List

from ...utils.shared import SHOW_DOWNLOAD_ERRORS_THRESHOLD, DOWNLOAD_LOGGER as LOGGER


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
    def success_percentage(self) -> float:
        return self.success / self.total

    @property
    def failure_percentage(self) -> float:
        return self.fail / self.total

    @property
    def is_fatal_error(self) -> bool:
        return self.error_message is not None

    @property
    def is_mild_failure(self) -> bool:
        return self.failure_percentage > SHOW_DOWNLOAD_ERRORS_THRESHOLD

    def merge(self, other: "DownloadResult"):
        if other.is_fatal_error:
            LOGGER.debug(other.error_message)
            self._error_message_list.append(other.error_message)
            self.total += 1
            self.fail += 1
        else:
            self.total += other.total
            self.fail += other.fail
            self._error_message_list.extend(other._error_message_list)

    def __str__(self):
        if self.is_fatal_error:
            return self.error_message
        head = f"{self.fail} from {self.total} downloads failed:\n" \
               f"successrate:\t{int(self.success_percentage*100)}%\n" \
               f"failrate:\t{int(self.failure_percentage*100)}%"

        if not self.is_mild_failure:
            return head

        _lines = [head]
        _lines.extend(self._error_message_list)
        return "\n".join(_lines)
