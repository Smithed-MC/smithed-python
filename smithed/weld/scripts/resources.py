from typing import ClassVar

from beet import DataPack, Drop, NamespaceFileScope, TextFile


class WeldScript(TextFile):
    scope: ClassVar[NamespaceFileScope] = {
        0: ("weld", "scripts"),
        45: ("weld", "script"),
    }
    extension: ClassVar[str] = ".bolt"


class WeldPyScript(TextFile):
    scope: ClassVar[NamespaceFileScope] = {
        0: ("weld", "scripts"),
        45: ("weld", "script"),
    }
    extension: ClassVar[str] = ".py"

    def bind(self, pack: DataPack, path: str):
        """Rebind file as a proper `Module` and drop current file."""

        super().bind(pack, path)

        if self.source_path:
            pack[path] = WeldScript(source_path=self.source_path)
        else:
            pack[path] = WeldScript(self.text)

        raise Drop()


class ResourceDefinition(TextFile):
    scope: ClassVar[NamespaceFileScope] = {
        0: ("weld", "resource_definitions"),
        45: ("weld", "resource_definition"),
    }
    extension: ClassVar[str] = ".py"


RESOURCES = [WeldScript, WeldPyScript, ResourceDefinition]
