class WeldError(Exception): ...


class InvalidMcmeta(WeldError):
    def __init__(self, pack: str, cause: str):
        super().__init__(f"Pack {pack}'s mcmeta file is not valid JSON:\n{cause}")
        self.pack = pack
        self.contents = cause


class InvalidPack(WeldError):
    def __init__(self, pack: str):
        super().__init__(
            f"Cannot determine if data or resource pack. Pack '{pack}' has neither assets nor data."
        )


class InvalidUpload(WeldError): ...
