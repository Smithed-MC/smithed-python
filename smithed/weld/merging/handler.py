import json
import logging
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Literal, cast

from beet import Context, DataPack, JsonFile, NamespaceFile
from beet.contrib.format_json import get_formatter
from beet.contrib.vanilla import Vanilla
from jsonpath_ng import parse

from smithed.type import JsonDict, JsonType

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

        smithed_current = SmithedJsonFile.parse_obj(current.data)
        smithed_conflict = SmithedJsonFile.parse_obj(conflict.data)

        # Store the pack.id on the last entry in the list
        if current_entries := smithed_current.smithed.entries():
            current_entries[-1].id = pack.mcmeta.data.get("id", "")

        # Grab conflicts to throw with the current file
        if conflict_entries := smithed_conflict.smithed.entries():
            current_entries.extend(conflict_entries)

        # Cache paths for latest use
        json_file_type = cast(type[NamespaceFile], type(current))
        self.cache[json_file_type].add(path)

        raw: JsonType = json.loads(smithed_current.json(by_alias=True))

        # TODO: fix
        # Cache vanilla paths
        if path not in self.vanilla:
            vanilla = self.ctx.inject(Vanilla)
            raw |= vanilla.data[json_file_type][path].data  # type: ignore
            self.vanilla.add(path)

        # Save back to current file
        current.data["__smithed__"] = raw

        return True

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

        raw = file.dict(by_alias=True)
        for id, rule in rules.items():
            if applied := self.apply_rule(raw, id, rule):
                raw = applied

        return raw

    def pre_process_priorities(self, file: SmithedJsonFile):
        """Gathers models by id. Pre-processes models for ease of use.

        Converts each 'before' priority into 'after' (as it's easier to resolve)
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

        parsed_target = parse(rule.target)

        # Handle whether the target path exists or not
        try:
            root = parsed_target.find(raw).pop(0)
        except IndexError:
            logger.warn(f"Target Path: {rule.target} was not found. Ignoring Rule.")
            return False

        # Apply each rule's logic
        match rule:
            case MergeRule(source=ValueSource(value=value)):
                match root.value:
                    case {} if isinstance(value, dict):
                        root.value |= value
                    case [] if isinstance(value, list):
                        root.value.extend(value)  # type: ignore
                    case _ if type(value) not in {dict, list}:
                        parsed_target.update(raw, value)
                    case _:
                        raise MergingError(
                            f"Unable to merge weld rules from pack {current}\n"
                            f"Current `{type(value)}` is not `{type(root.value)}`\n"
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
