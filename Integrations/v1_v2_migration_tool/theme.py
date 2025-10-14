from pathlib import Path
import streamlit as st

def load_css(path: str = "styles/iriusrisk.css"):
    css = Path(path).read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def hero(title: str, subtitle: str = "", left=None, right=None):
    st.markdown('<div class="irius-hero irius-container">', unsafe_allow_html=True)
    st.markdown(f"<h1 class='irius-h1' style='margin:0 0 .5rem'>{title}</h1>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<p style='margin:0 0 1rem; font-size:1.05rem'>{subtitle}</p>", unsafe_allow_html=True)
    c1, c2 = st.columns([1,1], gap="large")
    if left: left(c1)
    if right: right(c2)
    st.markdown("</div>", unsafe_allow_html=True)

def card(title: str, body: str):
    st.markdown(f"""
    <div class="irius-card">
      <h3 class="irius-h3" style="margin:.25rem 0 .5rem">{title}</h3>
      <p style="margin:0">{body}</p>
    </div>
    """, unsafe_allow_html=True)

def outline_button(label: str, href: str):
    st.markdown(f'<a class="btn-outline" href="{href}">{label}</a>', unsafe_allow_html=True)