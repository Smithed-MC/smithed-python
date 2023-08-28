import json
import logging
import re
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from importlib import resources
from typing import Literal, cast

from beet import Context, DataPack, JsonFile, NamespaceFile
from beet.contrib.format_json import get_formatter
from beet.contrib.vanilla import Vanilla
from jsonpath_ng.ext import parse
from pydantic import ValidationError

from smithed.type import JsonDict, JsonTypeT

from ..models import SmithedJsonFile
from ..models.rules import (
    AppendRule,
    InsertRule,
    MergeRule,
    PrependRule,
    RemoveRule,
    Rule,
)
from ..models.sources import ValueSource
from .errors import MergingError, PriorityError

logger = logging.getLogger(__name__)

PRIORITY_STAGES = ["early", "standard", "late"]
YELLOW_SHULKER_BOX = resources.files("weld") / "resources" / "yellow_shulker_box.json"


@dataclass
class ConflictsHandler:
    ctx: Context

    formatter: Callable[..., str] = get_formatter()
    cache: defaultdict[type[NamespaceFile], set[str]] = field(
        default_factory=lambda: defaultdict(set)
    )
    vanilla: set[str] = field(default_factory=set)

    def __call__(
        self, pack: DataPack, path: str, current: JsonFile, conflict: JsonFile, /
    ):
        """TODO: DOCSTRING"""

        # Parse the files and handle validation errors. We need to ensure that `current`
        #  is left with a valid file. If a file has an incorrect `smithed` definition.
        smithed_current = self.parse_smithed_file(current)
        smithed_conflict = self.parse_smithed_file(conflict)

        if smithed_current is False and smithed_conflict is False:
            logger.warn(
                "Both the current and conflict files are invalid. Undefined Behavior"
            )
            return False

        elif smithed_current is False:
            current.data = conflict.data
            return True

        elif smithed_conflict is False:
            return True

        # Store the pack.id on the last entry in the list
        if current_entries := smithed_current.smithed.entries():
            current_entries[-1].id = pack.mcmeta.data.get("id", "missing")

        # Cache paths for latest use
        json_file_type = cast(type[NamespaceFile], type(current))
        self.cache[json_file_type].add(path)

        # Handle vanilla paths as the base / current file
        if path.startswith("minecraft:"):
            if path not in self.vanilla:
                current.data = self.grab_vanilla(path, json_file_type)
                self.vanilla.add(path)

        # Handle non-vanilla paths, swap conflict w/ current if no smithed rules exist
        # This is to ensure that non-vanilla files can work with weld.
        # Example:
        #   TCC has a loot table for iceologer
        #   Pack B wants to weld the loot table for iceologer
        #   This will ensure that TCC is the base reference even if Pack B is
        #    loaded first as TCC will not have any weld rules defined but Pack B will.
        #
        # ⚠️ It's important that either the current or conflict files have smithed rules
        #  though it be odd if two packs are writing to the same namespace.
        elif not smithed_conflict.smithed.entries():
            if not current_entries:
                logger.warn(
                    "Both files have no smithed rules which is likely not intended."
                    f" Path: {path}"
                )
            else:
                logging.info(f"Swapping base file at `{path}`")
                current.data, conflict.data = conflict.data, current.data
                smithed_current, smithed_conflict = smithed_conflict, smithed_current

        raw: JsonDict = json.loads(smithed_conflict.json(by_alias=True))

        # Grab conflicts to throw with the current file
        if conflict_entries := smithed_conflict.smithed.entries():
            current_entries.extend(conflict_entries)

        # Save back to current file
        current.data["__smithed__"] = raw["__smithed__"]

        return True

    def parse_smithed_file(self, file: JsonFile) -> SmithedJsonFile | Literal[False]:
        try:
            return SmithedJsonFile.parse_obj(file.data)
        except ValidationError:
            return False

    def grab_vanilla(self, path: str, json_file_type: type[NamespaceFile]) -> JsonDict:
        """Grabs the vanilla file to load as the current file (aka the base).

        ⚠️ Uses the bundled `yellow_shulker_box.json` as an override over vanilla's.
        """
        if path == "minecraft:blocks/yellow_shulker_box":
            return json.loads(YELLOW_SHULKER_BOX.read_text())

        vanilla = self.ctx.inject(Vanilla)
        return cast(JsonFile, vanilla.data[json_file_type][path]).data

    def process(self):
        """Main entrypoint for smithed merge solving"""

        for json_file_type, path in self:
            logger.info(f"Resolving: {json_file_type.__name__!r} {path!r}")

            namespace_file = self.ctx.data[json_file_type]
            smithed_file = SmithedJsonFile.parse_obj(
                namespace_file[path].data  # type: ignore
            )

            if smithed_file.smithed.entries():
                processed = self.process_file(smithed_file)
                namespace_file[path].data = processed  # type: ignore

    def process_file(self, file: SmithedJsonFile) -> JsonDict:
        """Process each file's rules"""

        logger.info("Resolving priorities..")
        rules: dict[str, Rule] = {}
        for id in (pre_processed_rules := self.pre_process_priorities(file)):
            self.resolve_priorities(pre_processed_rules, id, rules, [])

        logger.info("Injecting `_index`..")
        raw = self.manage_indexes(file.dict(by_alias=True))

        for id, rule in rules.items():
            if applied := self.apply_rule(raw, id, rule):
                raw = applied

        return self.manage_indexes(raw, strip=True)

    def manage_indexes(self, data: JsonTypeT, strip: bool = False) -> JsonTypeT:
        """Adds / removes `_index` field to every item in a list"""

        match data:
            case list(value):
                for index, item in enumerate(value):
                    if isinstance(item, dict):
                        if strip:
                            del item["_index"]
                        else:
                            item["_index"] = index

                return [
                    self.manage_indexes(item, strip) for item in value  # type: ignore
                ]

            case dict(value):
                return {
                    key: self.manage_indexes(val, strip)  # type: ignore
                    for key, val in value.items()
                }

            case other:
                return other

    def pre_process_priorities(self, file: SmithedJsonFile):
        """Gathers models by id. Pre-processes models for ease of use.

        Converts each 'before' priority into 'after' (as it's easier to resolve).
        """

        # refactor to be cleaner
        rules = {
            model.id: rule for model in file.smithed.entries() for rule in model.rules
        }
        for current_id, rule in rules.items():
            if before := rule.priority.before:
                for id in before:
                    rules[id].priority.after.add(current_id)
                before.clear()

        return rules

    def resolve_priorities(
        self,
        rules: dict[str, Rule],
        current: str,
        resolved: dict[str, Rule],
        processing: list[str],
    ):
        """Resolves priorities for each stage."""

        for stage in PRIORITY_STAGES:
            logger.info(f"Resolving stage: `{stage}`")
            self.resolve_stage(stage, rules, current, resolved, processing)

    def resolve_stage(
        self,
        stage: str,
        rules: dict[str, Rule],
        current: str,
        resolved: dict[str, Rule],
        processing: list[str],
    ):
        """Resolves priorities within a specific stage.

        ⚠️ Raises PriorityError if a dependency loop is found.
        ⚠️ Raises PriorityError if a pack depends on another pack from a different stage.
        ⚠️ Logs warning if a pack depends on a pack that does not exist.
        """

        if stage != rules[current].priority.stage:
            raise PriorityError(
                f"Cannot resolve priority for rule during stage {stage}."
                " Packs must only depend on packs in `before` or `after` that are in"
                " the same stage. You likely shouldn't specify both `stage`"
                " AND `before/after` unless you know what you are doing."
            )

        if after := rules[current].priority.after:
            for id in after:
                if id in processing:
                    raise PriorityError(
                        "Dependency loop found while resolving"
                        f" `{current}` in stage `{stage}`.\n"
                        "The following loop was discovered: "
                        + " -> ".join(f"`{id}`" for id in processing)
                        + f" -> `{id}`"
                    )
                elif id in rules:
                    processing.append(id)
                    self.resolve_stage(stage, rules, id, resolved, processing)
                    processing.remove(id)
                else:
                    logger.warn(f"Priority: {id} was not found. Ignoring Rule.")

        # dict insertion order for the win
        if current not in resolved:
            resolved[current] = rules[current]

    def apply_rule(
        self, raw: JsonDict, current: str, rule: Rule
    ) -> JsonDict | Literal[False]:
        """Rule application uses `jsonpath_ng` for parsing target paths."""

        normalized_target = re.sub(r"\[(\d+)\]", r"[?_index=\1]", "rule.target")
        parsed_target = parse(normalized_target)

        # Handle whether the target path exists or not
        try:
            root = parsed_target.find(raw).pop(0)
        except IndexError:
            logger.warn(
                f"Target Path: {rule.target} ({normalized_target}) was not found."
                " Ignoring..."
            )
            return False

        # Apply each rule's logic
        match rule:
            case MergeRule(source=ValueSource(value=value)):
                match root.value, value:
                    case dict(), dict(value):
                        root.value |= value
                    case list(), list(value):
                        root.value.extend(value)
                    case _ if type(value) not in {dict, list}:
                        parsed_target.update(raw, value)
                    case _:
                        raise MergingError(
                            f"Unable to merge weld rules from pack {current}.\n"
                            f"Current `{type(value)}` is not `{type(root.value)}`."
                        )

            case AppendRule(source=ValueSource(value=value)):
                root.value.append(value)

            case PrependRule(source=ValueSource(value=value)):
                root.value.prepend(value)

            case InsertRule(source=ValueSource(value=value), index=index):
                root.value.insert(index, value)

            case RemoveRule():
                root.value.remove()

        return raw

    def __iter__(self):
        for json_file_type, paths in self.cache.items():
            yield from [(json_file_type, path) for path in paths]
