import logging
import tempfile
import time
from importlib import resources
from io import StringIO
from pathlib import Path
from zipfile import ZipFile

import streamlit as st
import weld
import yaml
from streamlit.delta_generator import DeltaGenerator
from streamlit_extras.stateful_button import button as toggle_button

from .model import WebApp

icon = "https://github.com/Smithed-MC/smithed-python/blob/feat/weld-but-good/smithed/weld/resources/icon.png?raw=true"

logging.basicConfig(format="%(levelname)-8s %(message)s", level=logging.INFO)

webapp = WebApp.parse_obj(
    yaml.safe_load((resources.files("weld") / "resources" / "webapp.yaml").read_text())
)
temp_dir = tempfile.TemporaryDirectory()
temp = Path(temp_dir.name)

console = logging.StreamHandler(stream := StringIO())
logging.getLogger("weld").addHandler(console)


# def validate_zips(packs: list[str]):
#     for pack in packs:
#         try:
#             with pack.open("pack.mcmeta") as meta:
#                 print(meta.read(), "\n")
#         except FileNotFoundError:
#             return f"`pack.mcmeta` not found in pack {pack.filename}"

#     return False


def upload_flow(ui: DeltaGenerator):
    progress = ui.container()
    packs = ui.file_uploader("Upload packs", accept_multiple_files=True, type="zip")

    col1, col2, col3 = ui.columns(3)
    with col2:
        if fabric_mod := toggle_button("Turn into Fabric Mod", key="toggle"):
            ui.warning(webapp.fabric)

    path = None
    t0 = time.perf_counter()
    if col1.button("Build Packs", disabled=not packs, key="build") and packs:
        for pack in packs:
            with (temp / pack.name).with_suffix(".zip").open("wb") as temp_file:
                temp_file.write(pack.read())
        pack_paths = list(str(path) for path in temp.glob("*.zip"))
        # if error := validate_zips(pack_paths):
        #     st.error(error)
        #     return
        with st.status(f"Welding {len(packs)} packs!", expanded=True) as status:
            stream.seek(0)
            stream.truncate(0)
            with weld.run_weld(pack_paths, as_fabric_mod=fabric_mod) as ctx:
                if fabric_mod:
                    with ZipFile("output.jar", "w") as jar:
                        ctx.data.dump(jar)
                        ctx.assets.dump(jar)
                        path = Path(str(jar.filename))
                else:
                    if ctx.data:
                        path = ctx.data.save(path="output", zipped=True, overwrite=True)
                    if ctx.assets:
                        path = ctx.assets.save(
                            path="output", zipped=True, overwrite=True
                        )

            t1 = time.perf_counter()
            stream.seek(0)
            st.text_area("Build Log", stream.getvalue(), disabled=True, height=300)
            status.update(label=f"Merged in :green[{t1 - t0: 0.3f}s]")

        if path is not None:
            with path.open(mode="rb") as file:
                col3.download_button(
                    "Download Welded Packs",
                    file,
                    file_name="welded-pack.zip" if not fabric_mod else "welded-mod.jar",
                )
    else:
        col3.button("Download Welded Packs", disabled=True, key="download")

    if not packs:
        progress.info("Waiting for uploaded packs")
    elif path is None:
        progress.success("Ready to Build!")


def main():
    st.set_page_config(page_title="Weld", page_icon=icon, layout="wide")

    st.sidebar.title("Special Merging Rules")
    st.sidebar.write(webapp.conflicts)
    st.sidebar.write("----")
    st.sidebar.write("See [docs](https://wiki.smithed.dev/weld) for more info!")

    st.write(webapp.title.format(version=weld.__version__), unsafe_allow_html=True)

    st.write(webapp.intro, unsafe_allow_html=True)

    st.warning(webapp.warn)
    upload_flow(st.container())

    st.write("---")

    col1, col2 = st.columns(2)
    col1.markdown(webapp.footer.left, unsafe_allow_html=True)
    col2.markdown(webapp.footer.right, unsafe_allow_html=True)
