class YandexError(Exception):
    def __init__(self, *args) -> None:
        self.message = args[0] if args else None

    def __str__(self) -> str:
        return self.message


class InvalidMaxLengthError(YandexError):
    def __init__(self, *args) -> None:
        if args:
            self.max_len = args[0]
            self.cur_len = args[1]
        else:
            self.max_len = None
            self.cur_len = None
        super().__init__(args[1:])

    def __str__(self) -> str:
        if self.max_len:
            return f"Length must be less than {self.max_len}, current length: {self.cur_len}"
        else:
            return ""
