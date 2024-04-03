import time
from concurrent.futures import ThreadPoolExecutor
from importlib import resources
from pathlib import Path
from zipfile import ZipFile

import streamlit as st
import yaml
from streamlit.delta_generator import DeltaGenerator
from streamlit_extras.stateful_button import button as toggle_button
from streamlit_extras.streaming_write import write as streaming_write

from smithed import weld

from .log_helpers import init_logger
from .models import Columns, WebApp

icon = "https://github.com/Smithed-MC/smithed-python/blob/main/smithed/weld/resources/icon.png?raw=true"

webapp = WebApp.parse_obj(
    yaml.safe_load(
        (resources.files("smithed") / "weld/resources/webapp.yaml").read_text()
    )
)


def weld_packs(packs: list[ZipFile], make_fabric_mod: bool) -> Path | None:
    """Welds a list of zip files. Outputs a path"""

    with weld.run_weld(packs, as_fabric_mod=make_fabric_mod) as ctx:
        if make_fabric_mod:
            with ZipFile("output.jar", "w") as jar:
                ctx.data.dump(jar)
                ctx.assets.dump(jar)
                output = Path(str(jar.filename))

        # TODO: figure out what to do if user uploads both data and resource packs
        # prolly merge and download UNZIP ME or something
        if ctx.data:
            output = ctx.data.save(path="output", zipped=True, overwrite=True)

        if ctx.assets:
            output = ctx.assets.save(path="output", zipped=True, overwrite=True)

        return output  # type: ignore ikkk TODO


def build_packs(
    packs: list[ZipFile], cols: Columns, make_fabric_mod: bool = False
) -> Path | None:
    path = None

    with st.status(f"Welding {len(packs)} packs!", expanded=False) as status:
        try:
            t0 = time.perf_counter()
            stream = init_logger()

            with ThreadPoolExecutor() as executor:
                future = executor.submit(
                    weld_packs, packs=packs, make_fabric_mod=make_fabric_mod
                )
                while not future.done():
                    time.sleep(0.1)
                    streaming_write(val := stream.getvalue())
                    print(val)
                streaming_write(val := stream.getvalue())
                print(val)

                path = future.result()

            t1 = time.perf_counter()
            status.update(
                label=f"Merged in :green[{t1 - t0: 0.3f}s]. Click to see log."
            )

            return path

        except Exception as exc:
            status.update(label=":red[Error occured. Click to reveal error.]")
            status.error(f"# `{exc.__class__.__name__}`\n{exc.args[0]}")

    return path


def upload_flow(ui: DeltaGenerator):
    progress = ui.container()
    raw_packs = ui.file_uploader("Upload packs", accept_multiple_files=True, type="zip")
    packs = [ZipFile(pack) for pack in raw_packs] if raw_packs else []

    cols = Columns(*ui.columns(3))
    with cols.middle:
        if fabric_mod := toggle_button("Turn into Fabric Mod", key="toggle"):
            ui.warning(webapp.fabric)

    path = None
    if cols.left.button("Build Packs", disabled=not packs, key="build") and packs:
        path = build_packs(packs, cols, make_fabric_mod=fabric_mod)
    else:
        cols.right.button("Download Welded Packs", disabled=True, key="download")

    if not packs:
        progress.info("Waiting for uploaded packs")
    elif path is None:
        progress.success("Ready to Build!")

    if path is not None:
        with path.open(mode="rb") as file:
            cols.right.download_button(
                "Download Welded Packs",
                file,
                file_name=("welded-pack.zip" if not fabric_mod else "welded-mod.jar"),
            )


def main():
    st.set_page_config(
        page_title="Weld",
        page_icon=icon,
        layout="wide",
    )

    st.sidebar.title("Special Merging Rules")
    st.sidebar.write(webapp.conflicts)
    st.sidebar.write("----")
    st.sidebar.write("See [docs](https://wiki.smithed.dev/weld) for more info!")
    st.sidebar.write("----")
    st.sidebar.warning(webapp.warn)

    st.write(webapp.title.format(version=weld.__version__), unsafe_allow_html=True)

    st.write(webapp.intro, unsafe_allow_html=True)

    upload_flow(st.container())

    st.write("---")

    col1, col2 = st.columns(2)
    col1.markdown(webapp.footer.left, unsafe_allow_html=True)
    col2.markdown(webapp.footer.right, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
