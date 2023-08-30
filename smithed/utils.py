import logging
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import click
import typer
from beet import BeetException, WrappedException
from beet.core.utils import format_exc

from .theming import print

logger = logging.getLogger("weld")


def path_str(path: Path) -> str:
    """Returns str of a path, replacing the home directory with '~'"""

    return str(path).replace(str(Path.home()), "~")


def format_error(
    message: str,
    exception: BaseException | None = None,
    padding: int = 0,
) -> str:
    """Format a given error message and exception."""
    output = "\n" * padding
    output += f"[bold][error]Error: {message}[/bold][/error]\n"
    if exception:
        output += "\n" + format_exc(exception)
    output += "\n" * padding
    return output.replace(str(Path.home()), "~")


@contextmanager
def error_handler(should_exit: bool = False, format_padding: int = 0) -> Iterator[None]:
    """Context manager that catches and displays exceptions."""
    exception = None

    try:
        yield
    except WrappedException as exc:
        message = str(exc)
        if not exc.hide_wrapped_exception:
            exception = exc.__cause__
    except BeetException as exc:
        message = str(exc)
    except (typer.Abort, KeyboardInterrupt):
        print()
        message = "Aborted."
    except (click.ClickException, click.exceptions.Exit):
        raise
    except Exception as exc:
        message = "An unhandled exception occurred. This could be a bug."
        exception = exc
    else:
        return

    logger.error(
        format_error(message, exception, format_padding), extra={"markup": True}
    )

    if should_exit:
        typer.Exit(-1)
