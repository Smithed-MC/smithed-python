class WeldError(Exception): ...


class InvalidMcmeta(WeldError):
    def __init__(self, pack: str, contents: str):
        super().__init__(f"Pack {pack}'s mcmeta file is not valid JSON:\n{contents}")
        self.pack = pack
        self.contents = contents


class InvalidPack(WeldError):
    def __init__(self, pack: str):
        super().__init__(
            f"Cannot determine if data or resource pack. Pack '{pack}' has neither assets nor data."
        )


class InvalidUpload(WeldError): ...
