import logging
import traceback as tb

from beet import Context, DataPack, Draft, Pack, ResourcePack
import beet
import bolt_expressions
from bolt import Runtime
from bolt.contrib.sandbox import Sandbox, public_attrs
from mecha import CompilationError, Mecha

from .resources import RESOURCES, ResourceDefinition, WeldScript

logger = logging.getLogger("weld")

ALLOWED_TYPES = (DataPack, ResourcePack)
WELD_SCRIPTS_OVERLAY_NAME = "weld_generated"


def process_scripting(ctx: Context):
    """Load scripting stuff"""

    mc = ctx.inject(Mecha)
    runtime = ctx.inject(Runtime)

    # TODO: move to new file, and write up comments for everything allowed. make more specific
    sandbox = ctx.inject(Sandbox)
    sandbox.allow_basics()
    sandbox.allow_pipeline_context()

    sandbox.allowed_type_attrs[Draft] |= {field for field in public_attrs(Draft)}

    sandbox.allowed_obj_attrs[beet] |= {field for field in public_attrs(beet)}
    sandbox.allowed_obj_attrs[bolt_expressions] |= {
        field for field in public_attrs(bolt_expressions)
    }

    for _type in ALLOWED_TYPES:
        sandbox.allowed_type_attrs[_type] |= {field for field in public_attrs(_type)}

    sandbox.allowed_imports |= {"beet", "bolt_expressions"}
    sandbox.allowed_builtins |= {"breakpoint"}
    sandbox.activate()

    # load all ctx content into a draft so that it doesn't merge
    with ctx.generate.draft() as draft:
        # we shallow copy everything into a draft so we can shadow ctx
        for draft_pack, ctx_pack in zip((draft.assets, draft.data), ctx.packs):
            for resource, file in ctx_pack.all():
                draft_pack[resource] = file.copy()

        # pretend draft is ctx so that people can't change ctx stuff
        # the draft has shallow copies of all content
        runtime.globals["ctx"] = draft
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

        # delete files that have not changed in our draft (if `._content` exists, it's changed)
        for pack in [draft.assets, draft.data]:
            for resource, file in list(pack.all()):
                if hasattr(file, "_content") and not file._content:
                    del pack[type(file)][resource]

        # merge all draft content into our global overlay. the draft needs to
        #  be cleared so that it doesn't merge into the actual pack.
        for overlay_pack, draft_pack in zip(
            (overlay.assets, overlay.data), (draft.assets, draft.data)
        ):
            overlay_pack.merge(draft_pack)  # type: ignore
            draft_pack.clear()


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
