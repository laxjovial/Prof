import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Student User Guide",
    page_icon="🧑‍🎓",
)

st.title("🧑‍🎓 Student User Guide")

try:
    user_guide_content = Path("docs/Student_User_Guide.md").read_text()
    st.markdown(user_guide_content, unsafe_allow_html=True)
except FileNotFoundError:
    st.error("The Student User Guide file was not found.")
