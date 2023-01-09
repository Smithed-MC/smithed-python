import time
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from weld import run_weld

st.set_page_config(page_title="Smithed • Weld", page_icon="random")

st.write(
    '<h1 style="text-align: center; color: #104db4;">Weld (beta)</h1>',
    unsafe_allow_html=True,
)


st.write(
    "Merge all your data and resource packs!"
    " This tool will intelligently merge your packs to produce an easy to use zip."
    " It will also handle the following conflict types:\n"
    " - Tag files will merge exactly the same as vanilla\n"
    " - Lang files will extend each other\n"
    " - Model files will extend and sort overrides with `custom_model_data` defined\n"
    " - (Future) Custom `__smithed__` definitions will apply (see [vanilla-overides](https://wiki.smithed.dev/conventions/vanilla-overrides))\n"
)
st.warning(
    "⚠️ This tool is in **heavy beta** and should be used with caution.\n\nPlease forward all feedback to our [Discord](https://discord.com)!"
)


def upload_flow(label, pack_type: str, tab: DeltaGenerator):
    progress = tab.container()
    if pack_type == "all":
        tab.warning("🧪 This feature is experimental, use with caution!")
    packs: list[BytesIO] = tab.file_uploader(f"Upload {label}", accept_multiple_files=True, type="zip")  # type: ignore
    col1, col2 = tab.columns(2)
    t0 = time.perf_counter()
    path = None
    if col1.button("Build Packs", disabled=not packs, key=f"build-{label}"):
        progress.info(f"Building {len(packs)} packs!")
        pack_types = (
            ["data_pack", "resource_pack"] if pack_type == "all" else [pack_type]
        )
        with run_weld((ZipFile(pack) for pack in packs), pack_types=pack_types) as ctx:  # type: ignore
            match pack_type:
                case "data_pack":
                    path = ctx.data.save(path="output", zipped=True, overwrite=True)
                case "resource_pack":
                    path = ctx.assets.save(path="output", zipped=True, overwrite=True)
                case "all":
                    with ZipFile("output.jar", "w") as jar:
                        ctx.data.dump(jar)
                        ctx.assets.dump(jar)
                        path = Path(str(jar.filename))

        t1 = time.perf_counter()
        progress.success(f"Merged in {t1 - t0: 0.2f}s")
        if path is not None:
            with path.open(mode="rb") as file:
                col2.download_button(
                    "Download Welded Packs",
                    file,
                    file_name="welded-pack.zip"
                    if pack_type != "all"
                    else "welded-mod.jar",
                )
    else:
        col2.button("Download Welded Packs", disabled=True, key=f"download-{label}")

    if not packs:
        progress.info("Waiting for uploaded packs")
    elif path is None:
        progress.success("Ready to Build!")


data_col, resource_col, combined_col = st.tabs(
    ["Data Packs", "Resource Packs", "Combined (Fabric Jar)"]
)
upload_flow("Data Packs", "data_pack", data_col)
upload_flow("Resource Packs", "resource_pack", resource_col)
upload_flow("Any Packs", "all", combined_col)

st.write("---")

col1, col2 = st.columns(2, gap="medium")
col1.markdown(
    """
    <h4 style="text-align: center; color: #104db4;">Built with ♥️ by Smithed</h4>
    Smithed is a open-source ecosystem to support data and resource pack creators. Check us out at <a href="https://smithed.dev">here</a>!
    <br><br>
    Check out our <a href="https://wiki.smithed.dev/weld">documentation</a> to learn more about weld!
    """,
    unsafe_allow_html=True,
)

col2.markdown(
    """
    <iframe
     src="https://discord.com/widget?id=511303648119226382&amp;theme=dark"
     title="Discord Embed"
     sandbox="allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts"
     style="width: 325px; height: 400px; border: 2px solid white; border-radius: 16px;">
    </iframe>
    """,
    unsafe_allow_html=True,
)
