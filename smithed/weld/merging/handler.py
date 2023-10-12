"""This is the main logic for weld's custom merging logic.

It uses the beet's merge policies to implement a conflict handler that registers
 conflicts, merging all `__smithed__` into a base file (whether it's vanilla or not).
 In a later invocation, it then processes all of the registered conflicts, determines
 the ordering via the priority and stage system, and applies each defined rule onto
 the base file.

 TODO: Likely refactor into multiple files, I can see each file handling being it's own
  class since several methods based on each file are passing similar parameters with
  each other.
"""

import json
import logging
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from importlib import resources
from typing import Literal, cast

from beet import Context, DataPack, JsonFile, NamespaceFile
from beet.contrib.format_json import get_formatter
from beet.contrib.vanilla import Vanilla
from pydantic import ValidationError

from smithed.type import JsonDict, JsonTypeT

from ..models import (
    AppendRule,
    Condition,
    ConditionInverted,
    ConditionPackCheck,
    InsertRule,
    MergeRule,
    PrependRule,
    RemoveRule,
    ReplaceRule,
    Rule,
    SmithedJsonFile,
    ValueSource,
    deserialize,
)
from .errors import PriorityError
from .parser import append, get, insert, merge, prepend, remove, replace

logger = logging.getLogger("weld")

PRIORITY_STAGES = ["early", "standard", "late"]
YELLOW_SHULKER_BOX = (
    resources.files("smithed") / "weld/resources/yellow_shulker_box.json"
)


@dataclass
class ConflictsHandler:
    ctx: Context

    formatter: Callable[..., str] = get_formatter()
    cache: defaultdict[type[NamespaceFile], set[str]] = field(
        default_factory=lambda: defaultdict(set)
    )
    vanilla: set[str] = field(default_factory=set)
    overrides: set[str] = field(default_factory=set)

    def __call__(
        self, pack: DataPack, path: str, current: JsonFile, conflict: JsonFile, /
    ):
        """Register conflicts.."""

        logger.debug(f"Registering conflict: {path!r}")
        if path in self.overrides:
            logger.debug("Skipping due to override")
            return True

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

        current_entries = smithed_current.smithed.entries()

        if len(current_entries) > 0 and current_entries[0].override:
            logger.critical(
                f"Overriding base file at `{path}` with {current_entries[0].id}"
            )
            self.overrides.add(path)
            return True

        conflict_entries = smithed_conflict.smithed.entries()
        if len(conflict_entries) > 0 and conflict_entries[0].override:
            logger.critical(
                f"Overriding base file at `{path}` with {conflict_entries[0].id}"
            )
            self.overrides.add(path)
            current.data = conflict.data
            return True

        # Cache paths for latest use
        json_file_type = cast(type[NamespaceFile], type(current))
        self.cache[json_file_type].add(path)

        # Handle vanilla paths as the base / current file
        if path.startswith("minecraft:"):
            if path not in self.vanilla:
                current.data = self.grab_vanilla(path, json_file_type)
                if path == "minecraft:blocks/yellow_shulker_box":
                    logger.warn(
                        f"Weld is ignoring [bold]'{path}'[/bold] for now.",
                        extra={"markup": True},
                    )
                    return True

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
                if smithed_conflict.dict() != smithed_current.dict():
                    logger.warn(
                        f"Conflict unresolved at '{path}'.\nContents are different and"
                        f" contain no smithed rules which is likely unintended."
                    )
            else:
                logger.info(f"Swapping base file at `{path}`")
                current.data, conflict.data = conflict.data, current.data
                smithed_current, smithed_conflict = smithed_conflict, smithed_current

        # Grab conflicts to throw with the current file
        if conflict_entries := smithed_conflict.smithed.entries():
            current_entries.extend(conflict_entries)

        # Save back to current file
        raw: JsonDict = deserialize(smithed_current)
        current.data["__smithed__"] = raw["__smithed__"]

        return True

    def parse_smithed_file(self, file: JsonFile) -> SmithedJsonFile | Literal[False]:
        """Parses a smithed file and returns the parsed file or False if invalid."""

        try:
            return SmithedJsonFile.parse_obj(file.data)
        except ValidationError:
            logger.error("Failed to parse smithed file ", exc_info=True)
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
            logger.info(f"Resolving {json_file_type.__name__}: {path!r}")

            namespace_file = self.ctx.data[json_file_type]
            smithed_file = SmithedJsonFile.parse_obj(
                namespace_file[path].data  # type: ignore
            )

            if smithed_file.smithed.entries():
                processed = self.process_file(smithed_file)

                # reorder so `__smithed__` is at the bottom in output
                temp = processed["__smithed__"]
                del processed["__smithed__"]
                processed["__smithed__"] = temp

                namespace_file[path].data = processed  # type: ignore

    def process_file(self, file: SmithedJsonFile) -> JsonDict:
        """Process each file's rules"""

        logger.debug("Resolving priorities")
        rules = self.resolve_priorities(file)
        logger.debug(
            "Rules: %s",
            ", ".join(f"{id} {type(rule).__name__}" for id, rule in rules.items()),
        )

        logger.debug("Injecting `_index`")
        raw = self.manage_indexes(deserialize(file, defaults=False))

        logger.debug(f"Pack order: {', '.join(rules)}")
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
                            item.pop("_index", None)
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

    def pre_process_condition(
        self, rules: dict[str, Rule], condition: Condition
    ) -> bool:
        """Returns true if all conditions satisfy their criteria."""

        match condition:
            case ConditionPackCheck(id=id):
                return id in rules
            case ConditionInverted(conditions=conditions):
                return not all(
                    self.pre_process_condition(rules, condition)
                    for condition in conditions
                )

    def pre_process_rules(self, file: SmithedJsonFile):
        """Gathers models by id. Pre-processes models for ease of use.

        Converts each 'before' priority into 'after' (as it's easier to resolve).
        """

        # refactor to be cleaner
        rules = {
            model.id: rule for model in file.smithed.entries() for rule in model.rules
        }
        removed_ids: set[str] = set()
        for current_id, rule in rules.items():
            if not all(
                self.pre_process_condition(rules, condition)
                for condition in rule.conditions
            ):
                logging.info("Skipping rule from %s due to conditions", current_id)
                removed_ids.add(current_id)
                continue

            assert rule.priority is not None
            if before := rule.priority.before.entries():
                for id in before:
                    if id not in rules:
                        logger.warn(f"Priority: {id} was not found. Ignoring Rule.")
                        continue
                    other_rule = rules[id]
                    assert other_rule.priority is not None
                    if current_id not in other_rule.priority.after.entries():
                        other_rule.priority.after.entries().append(current_id)
                before.clear()

        return {id: rule for id, rule in rules.items() if id not in removed_ids}

    def resolve_priorities(self, file: SmithedJsonFile):
        """Resolves priorities for each stage."""

        pre_processed_rules = self.pre_process_rules(file)
        rules: dict[str, Rule] = {}

        for stage in PRIORITY_STAGES:
            logger.debug(f"Stage: `{stage}`")
            for id, rule in pre_processed_rules.items():
                assert rule.priority is not None
                if rule.priority.stage == stage:
                    self.resolve_stage(stage, pre_processed_rules, id, rules, [])

        return rules

    def resolve_stage(
        self,
        stage: str,
        pre_processed_rules: dict[str, Rule],
        current: str,
        processed: dict[str, Rule],
        processing: list[str],
    ):
        """Resolves priorities within a specific stage.

        ⚠️ Raises PriorityError if a dependency loop is found.
        ⚠️ Raises PriorityError if a pack depends on another pack from a different stage.
        ⚠️ Logs warning if a pack depends on a pack that does not exist.
        """

        current_rule = pre_processed_rules[current]

        assert current_rule.priority is not None
        if after := current_rule.priority.after.entries():
            for id in after:
                if id in processing:
                    raise PriorityError(
                        "Dependency loop found while resolving"
                        f" `{current}` in stage `{stage}`.\n"
                        "The following loop was discovered: "
                        + " -> ".join(f"`{id}`" for id in processing)
                        + f" -> `{id}`"
                    )
                if stage != current_rule.priority.stage and id not in processed:
                    raise PriorityError(
                        f"Cannot resolve priority for rule during stage `{stage}`."
                        "\nPacks must only depend on packs in `before` or `after`"
                        " thah are in the same stage. You likely shouldn't specify"
                        " both `stage` AND `before/after` unless you know what"
                        " you are doing."
                    )
                elif id in pre_processed_rules:
                    processing.append(id)
                    self.resolve_stage(
                        stage, pre_processed_rules, id, processed, processing
                    )
                    processing.remove(id)
                else:
                    logger.warn(f"Priority: {id} was not found. Ignoring Rule.")

        # dict insertion order for the win
        if current not in processed:
            processed[current] = pre_processed_rules[current]

    def apply_rule(
        self, raw: JsonDict, current: str, rule: Rule
    ) -> JsonDict | Literal[False]:
        """Rule application uses `jsonpath_ng` for parsing target paths.

        TODO: extract outward, maybe bundle rule application with the rule itself
        """

        # Handle whether the target path exists or not
        try:
            get(raw, rule.target, True)
        except ValueError:
            logger.warn(
                f"Target Path: {rule.target} was not found. Ignoring...", exc_info=True
            )
            return False

        # Apply each rule's logic
        match rule:
            case MergeRule(source=ValueSource(value=value)):
                merge(raw, rule.target, value)

            case AppendRule(source=ValueSource(value=value)):
                append(raw, rule.target, value)

            case PrependRule(source=ValueSource(value=value)):
                prepend(raw, rule.target, value)

            case InsertRule(source=ValueSource(value=value), index=index):
                insert(raw, rule.target, index, value)

            case ReplaceRule(source=ValueSource(value=value)):
                replace(raw, rule.target, value)

            case RemoveRule():
                remove(raw, rule.target)

        return raw

    def __iter__(self):
        for json_file_type, paths in self.cache.items():
            yield from [(json_file_type, path) for path in paths]
