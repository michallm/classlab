class AppError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class QuotaExceededError(AppError):
    pass
