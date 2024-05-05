# type: ignore


class WeldPluginError(Exception):
    namespace: str
    __cause__: Exception

    def __init__(self, *args, namespace: str, cause: Exception):
        super().__init__(*args)
        self.namespace = namespace
        self.__cause__ = cause

    def __str__(self) -> str:
        return f"{self.namespace}: {self.args[0]}\n{self.__cause__}"
