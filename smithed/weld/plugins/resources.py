from typing import ClassVar

from beet import Context, DataPack, Drop, TextFile


class WeldPlugin(TextFile):
    scope: ClassVar[tuple[str, ...]] = ("weld", "plugins")
    extension: ClassVar[str] = ".bolt"


class WeldPyPlugin(TextFile):
    scope: ClassVar[tuple[str, ...]] = ("weld", "plugins")
    extension: ClassVar[str] = ".py"

    def bind(self, pack: DataPack, path: str):
        """Rebind file as a proper `Module` and drop current file."""

        super().bind(pack, path)

        if self.source_path:
            pack[path] = WeldPlugin(source_path=self.source_path)
        else:
            pack[path] = WeldPlugin(self.text)

        raise Drop()


class CustomResource(TextFile):
    scope: ClassVar[tuple[str, ...]] = ("weld", "resources")
    extension: ClassVar[str] = ".py"


def load_resources(ctx: Context):
    ctx.data.extend_namespace += [WeldPlugin, WeldPyPlugin, CustomResource]
    ctx.assets.extend_namespace += [WeldPlugin, WeldPyPlugin, CustomResource]
