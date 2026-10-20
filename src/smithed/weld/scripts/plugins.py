import json
import logging
import traceback as tb

from beet import Context, DataPack, JsonFileBase, Pack, ResourcePack
from bolt import Runtime
from bolt.contrib.sandbox import Sandbox
from mecha import CompilationError, Mecha

from .resources import RESOURCES, ResourceDefinition, WeldScript
from .sandbox import configure_sandbox

logger = logging.getLogger("weld")

WELD_SCRIPTS_OVERLAY_NAME = "weld_generated"


def process_scripting(ctx: Context):
    """Load scripting stuff"""

    if not any(
        pack[WeldScript]
        for root in ctx.packs
        for pack in (root, *root.overlays.values())
    ):
        return

    mc = ctx.inject(Mecha)
    runtime = ctx.inject(Runtime)

    configure_sandbox(ctx.inject(Sandbox))

    # load all ctx content into a draft so that it doesn't merge
    with ctx.generate.draft() as draft:
        copied_files = {}
        # we shallow copy everything into a draft so we can shadow ctx
        for draft_pack, ctx_pack in zip((draft.assets, draft.data), ctx.packs):
            for resource, file in ctx_pack.all():
                copied = file.copy()
                draft_pack[resource] = copied
                copied_files[copied] = file

        # pretend draft is ctx so that people can't change ctx stuff
        # the draft has shallow copies of all content
        runtime.globals["ctx"] = draft
        for pack in ctx.packs:
            pack.overlays.setdefault(
                WELD_SCRIPTS_OVERLAY_NAME,
                supported_formats=pack.supported_formats or pack.pack_format,
                min_format=pack.min_format,
                max_format=pack.max_format,
            )
        overlay = ctx.generate.overlays[WELD_SCRIPTS_OVERLAY_NAME]

        # processing packs for compliation
        for pack in [
            ctx.data,
            *ctx.data.overlays.values(),
            ctx.assets,
            *ctx.assets.overlays.values(),
        ]:
            for resource_location, script in list(pack[WeldScript].items()):
                logger.info('Executing Weld Script: "%s"', resource_location)

                # compile with recovery to ensure we can compile other modules
                try:
                    with overlay.push():
                        mc.compile(script)

                except CompilationError as err:
                    # TODO: better error reporting for weld script writers
                    logger.error(err.__cause__)

                except Exception as err:
                    # if something errors (like mecha), log error AND traceback
                    logger.error(err)
                    logger.error("\n".join(tb.format_tb(err.__traceback__)))

        # Lazy reads populate _content too; only retain copies with changed content.
        for pack in [draft.assets, draft.data]:
            for resource, file in list(pack.all()):
                original = copied_files.get(file)
                if original is None:
                    continue
                if isinstance(file, JsonFileBase) and isinstance(
                    original, JsonFileBase
                ):
                    unchanged = (
                        file.source_path is not None
                        and file.source_path == original.source_path
                    ) or json.dumps(file.data, sort_keys=True) == json.dumps(
                        original.data, sort_keys=True
                    )
                else:
                    unchanged = file == original
                if unchanged:
                    del pack[type(file)][resource]

        # merge all draft content into our global overlay. the draft needs to
        #  be cleared so that it doesn't merge into the actual pack.
        for overlay_pack, draft_pack in zip(
            (overlay.assets, overlay.data), (draft.assets, draft.data)
        ):
            overlay_pack.merge(draft_pack)  # type: ignore
            draft_pack.clear()
            draft_pack.extra.clear()

    for pack in ctx.packs:
        if not pack.overlays[WELD_SCRIPTS_OVERLAY_NAME]:
            del pack.overlays[WELD_SCRIPTS_OVERLAY_NAME]


def clear_resources(ctx: Context):
    """Clear weld script resources"""

    for pack in [
        ctx.data,
        *ctx.data.overlays.values(),
        ctx.assets,
        *ctx.assets.overlays.values(),
    ]:
        for resource in [WeldScript, ResourceDefinition]:
            pack[resource].clear()


def load_resources(ctx: Context | Pack):
    """Load all of the custom resource types for weld scripts"""

    match ctx:
        case Context():
            for pack in ctx.packs:
                pack.extend_namespace += RESOURCES

        case DataPack() | ResourcePack() as pack:
            pack.extend_namespace += RESOURCES
