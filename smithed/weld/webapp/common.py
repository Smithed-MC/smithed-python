from importlib import resources
import streamlit as st
import yaml

from smithed.weld.webapp.models import WebApp

icon = "https://github.com/Smithed-MC/smithed-python/blob/main/smithed/weld/resources/icon.png?raw=true"


webapp = WebApp.parse_obj(
    yaml.safe_load(
        (resources.files("smithed") / "weld/resources/webapp.yaml").read_text("utf-8")
    )
)


def set_defaults():
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
