from dataclasses import dataclass


@dataclass
class DownloadResult:
    total: int = 0
    fail: int = 0
    error_message: str = None

    @property
    def success(self) -> int:
        return self.total - self.fail

    @property
    def fatal_error(self) -> bool:
        return self.error_message is not None

    def merge(self, other: "DownloadResult"):
        if other.fatal_error:
            self.total += 1
            self.fail += 1
        else:
            self.total += other.total
            self.fail += other.fail

    def __repr__(self):
        if self.fatal_error:
            return self.error_message
        return f"{self.fail} from {self.total} downloads failed."
