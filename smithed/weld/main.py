from collections import defaultdict
from dataclasses import dataclass, field, replace
from typing import Any, Callable, Dict, Iterable, List, Union

from beet import Context, DataPack, LootTable, NamespaceFile, NamespaceProxy
from beet.contrib.format_json import get_formatter
from beet.contrib.vanilla import Vanilla
from beet.core.file import JsonFile, JsonFileBase
from jsonpath_ng import parse

from .models import (
    SmithedAppendRule,
    SmithedInsertRule,
    SmithedJsonFile,
    SmithedMergeRule,
    SmithedModel,
    SmithedPrependRule,
    SmithedRule,
    SmithedValueSource,
)


class WeldError(Exception):
    ...


class DependencyError(WeldError):
    ...


class WeldMergeError(WeldError):
    ...


@dataclass
class ConflictsHandler:
    ctx: Context

    formatter: Callable[..., str] = get_formatter()
    cache: dict[type[JsonFile], str] = field(default_factory=dict)
    vanilla: set[str] = field(default_factory=set)

    def __call__(
        self, pack: DataPack, path: str, current: JsonFile, conflict: JsonFile, /
    ):
        smithed_current = SmithedJsonFile.parse_obj(current.data)
        smithed_conflict = SmithedJsonFile.parse_obj(conflict.data)

        smithed_current.smithed.entries()[-1].id = pack.mcmeta.data.get("id", "")
        if smithed_conflict.smithed:
            smithed_current.smithed.entries().extend(smithed_conflict.smithed.entries())

        json_file_type = type(current)
        self.cache[json_file_type] = path

        raw = smithed_current.dict(by_alias=True)
        if path not in self.vanilla and path.startswith("minecraft:"):
            vanilla = self.ctx.inject(Vanilla)
            raw |= vanilla.data[json_file_type][path].data
            self.vanilla.add(path)

        pack[json_file_type][path] = json_file_type(raw)

        return True

    def handle_files(self):
        for json_file_type, path in self:
            namespace_file: NamespaceProxy = self.ctx.data[json_file_type]  # type: ignore
            smithed_file = SmithedJsonFile.parse_obj(namespace_file[path].data)
            smithed_file.smithed.entries()[-1].id = self.ctx.data.mcmeta.data["id"]

            self.handle_file(smithed_file, path, json_file_type)

    def handle_file(
        self, file: SmithedJsonFile, path: str, json_file_type: type[JsonFile]
    ):
        models = {model.id: model for model in file.smithed.entries()}
        self.convert_to_after(models)
        resolved, processing = set(), []
        for current in models.keys():
            file = self.resolve(file, current, models, resolved, processing)
        self.ctx.data[json_file_type][path] = json_file_type(
            self.formatter(file.dict(by_alias=True, exclude={"smithed"}))
        )

    def convert_to_after(self, models: dict[str, SmithedModel]):
        for current_id, model in models.items():
            if before := model.priority.before:
                for id in before:
                    models[id].priority.after.add(current_id)
                model.priority.before.clear()

    def resolve(
        self,
        state: SmithedJsonFile,
        current: str,
        models: dict[str, SmithedModel],
        resolved: set[str],
        processing: list[str],  # we need to maintain order
    ):
        if after := models[current].priority.after:
            for id in after:
                if id in processing:
                    raise DependencyError(
                        f"Dependency loop found while resolving `{current}`.\n"
                        "The following loop was discovered: "
                        + " -> ".join(f"`{id}`" for id in processing)
                        + f" -> `{id}`"
                    )

                processing.append(id)
                state = SmithedJsonFile.parse_obj(
                    self.resolve(state, id, models, resolved, processing)
                )
                processing.remove(id)

        if current not in resolved:
            resolved.add(current)
            return SmithedJsonFile.parse_obj(self.apply_rule(state, models[current]))
        return state

    def apply_rule(self, state: SmithedJsonFile, model: SmithedModel):
        raw = state.dict(by_alias=True)
        for rule in model.rules:
            parsed_target = parse(rule.target)
            root = parsed_target.find(raw).pop(0)
            match rule:
                case SmithedMergeRule(source=SmithedValueSource(value=value)):
                    match root.value:
                        case {} if type(value) is dict:
                            root.value |= value
                        case [] if type(value) is list:
                            root.value.extend(value)
                        case _ if type(value) not in {dict, list}:
                            parsed_target.update(raw, value)
                        case _:
                            raise WeldMergeError(
                                f"Unable to merge weld rules from pack {model.id}\n"
                                f"Current `{type(value)}` is not `{type(root.value)}`\n"
                            )

                case SmithedAppendRule(source=SmithedValueSource(value=value)):
                    root.value.append(value)

                case SmithedPrependRule(source=SmithedValueSource(value=value)):
                    root.value.prepend(value)

                case SmithedInsertRule(
                    source=SmithedValueSource(value=value), index=index
                ):
                    root.value.insert(index, value)

        return raw

    def __iter__(self):
        yield from self.cache.items()


def setup(ctx: Context):
    handler = ctx.inject(ConflictsHandler)
    ctx.data.merge_policy.extend_namespace(LootTable, handler)


def beet_default(ctx: Context):
    handler = ctx.inject(ConflictsHandler)
    handler.handle_files()
