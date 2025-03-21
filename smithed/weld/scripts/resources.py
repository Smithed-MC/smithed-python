from typing import ClassVar

from beet import Context, DataPack, Drop, TextFile


class WeldScript(TextFile):
    scope: ClassVar[tuple[str, ...]] = ("weld", "plugins")
    extension: ClassVar[str] = ".bolt"


class WeldPyScript(TextFile):
    scope: ClassVar[tuple[str, ...]] = ("weld", "plugins")
    extension: ClassVar[str] = ".py"

    def bind(self, pack: DataPack, path: str):
        """Rebind file as a proper `Module` and drop current file."""

        super().bind(pack, path)

        if self.source_path:
            pack[path] = WeldScript(source_path=self.source_path)
        else:
            pack[path] = WeldScript(self.text)

        raise Drop()


class CustomResource(TextFile):
    scope: ClassVar[tuple[str, ...]] = ("weld", "resources")
    extension: ClassVar[str] = ".py"


def load_resources(ctx: Context):
    ctx.data.extend_namespace += [WeldScript, WeldPyScript, CustomResource]
    ctx.assets.extend_namespace += [WeldScript, WeldPyScript, CustomResource]
