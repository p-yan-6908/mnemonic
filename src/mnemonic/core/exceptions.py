class MnemonicError(Exception):
    pass


class MemoryFullError(MnemonicError):
    pass


class ValidationError(MnemonicError):
    pass


class StorageError(MnemonicError):
    pass


class StrategyError(MnemonicError):
    pass


class ExtractionError(MnemonicError):
    pass
