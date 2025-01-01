from logging import Filter


class LevelFilter(Filter):
    def __init__(self, level=None):
        super().__init__()
        self.level = level

    def filter(self, record):
        if self.level is None:
            return True  # No filtering applied if level is not specified
        return record.levelno == self.level
