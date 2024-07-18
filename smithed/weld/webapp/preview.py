import json
from beet import Context, DataPack, JsonFile, NamespaceFile
import streamlit as st
from streamlit_elements import elements, editor
from streamlit.delta_generator import DeltaGenerator
from streamlit.runtime.uploaded_file_manager import UploadedFile

from smithed.weld.merging.handler import ConflictsHandler

from . import common
from smithed.weld import run_weld
from beet.contrib.vanilla import Vanilla, load_vanilla
from beet import LootTable

valid_file_types: dict[str, tuple[type[JsonFile], str]] = {
    "Loot Table": (LootTable, "loot_table")
}


def merge_files(
    ctx: Context,
    input_json: str,
    file_origin: str,
    file_type: str | None,
    file_path: str | None,
    base_json: UploadedFile | None,
):
    output = DataPack()

    DataType: type[JsonFile] = valid_file_types[file_type][0]
    data_scope = valid_file_types[file_type][1]

    if file_origin == "Vanilla":
        query = {data_scope: [file_path]}
        ctx.require(load_vanilla(match=query))
    else:
        file_path = "weld:default"
        ctx.data[DataType][file_path] = DataType(base_json.getvalue().decode("utf-8"))

    input = DataType(input_json)
    output: JsonFile = ctx.data[DataType][file_path]

    conflicts = ConflictsHandler(ctx)
    conflicts(ctx.data, file_path, output, input)
    conflicts.process()

    output.data["__smithed__"] = input.data["__smithed__"]

    return output.data


def upload_flow(ui: DeltaGenerator):
    file_type = ui.selectbox("Data Type", valid_file_types.keys())
    input_json = ui.file_uploader(
        "Upload Overriding JSON File", accept_multiple_files=False, type="json"
    )

    file_origin = ui.selectbox("Base File", ("Vanilla", "Custom"))
    file_path = None
    base_json = None

    if file_origin == "Vanilla":
        file_path = ui.text_input("Data Path", "minecraft:blocks/stone")
    else:
        base_json = ui.file_uploader(
            "Upload Base JSON File", accept_multiple_files=False, type="json"
        )

    merge_clicked = ui.button(
        "Merge",
        disabled=(not input_json)
        or (file_origin == "Custom" and not base_json)
        or (file_origin == "Vanilla" and len(file_path) == 0),
    )

    if merge_clicked and input_json:
        input_json = input_json.getvalue().decode("utf-8")
        with run_weld({}) as ctx:
            output = merge_files(
                ctx, input_json, file_origin, file_type, file_path, base_json
            )

            return (
                json.dumps(json.loads(input_json), sort_keys=True, indent=2),
                json.dumps(output, sort_keys=True, indent=2),
            )

    return None


def main():
    common.set_defaults()

    st.write(
        '<h1 style="text-align: center; color: #23A3FF;">Rules Previewer</h1>',
        unsafe_allow_html=True,
    )
    # st.write('<span style="text-align: center; width: 100%">View how your weld rules will run with a nicely formatted diff.</span>', unsafe_allow_html=True)

    with elements("editor"):
        res = upload_flow(st.container())

        if res:
            editor.MonacoDiff(
                height=500,
                originalLanguage="json",
                modifiedLanguage="json",
                theme="vs-dark",
                original=res[0],
                modified=res[1],
                className="foo",
            )
