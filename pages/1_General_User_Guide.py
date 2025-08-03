import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="General User Guide",
    page_icon="📖",
)

st.title("📖 General User Guide")

try:
    # Read the markdown file from the /docs directory
    user_guide_content = Path("docs/General_User_Guide.md").read_text()
    st.markdown(user_guide_content, unsafe_allow_html=True)
except FileNotFoundError:
    st.error("The General User Guide file was not found.")
