import streamlit as st
import os
import base64

st.set_page_config(
    page_title="ODS Navigator Malaysia",
    page_icon="dist/jas-logo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { margin: 0; padding: 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

base_path = os.path.dirname(os.path.abspath(__file__))
dist_path = os.path.join(base_path, "dist")
index_path = os.path.join(dist_path, "index.html")

if not os.path.exists(index_path):
    st.error(f"Production build not found at {index_path}. Run 'npm run build' first.")
    st.stop()

# Build base64 data URI for the JAS logo so it works inside the iframe
logo_path = os.path.join(dist_path, "jas-logo.png")
if os.path.exists(logo_path):
    with open(logo_path, "rb") as lf:
        logo_b64 = base64.b64encode(lf.read()).decode("utf-8")
    logo_data_uri = f"data:image/png;base64,{logo_b64}"
else:
    logo_data_uri = "./dist/jas-logo.png"

with open(index_path, "r", encoding="utf-8") as f:
    html = f.read()

# Inline CSS asset
css_path = os.path.join(dist_path, "assets", "index-DRWDhQdW.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as cf:
        css = cf.read()
    html = html.replace(
        '<link rel="stylesheet" crossorigin href="/assets/index-DRWDhQdW.css">',
        f"<style>{css}</style>",
    )

# Inline JS asset
js_path = os.path.join(dist_path, "assets", "index-B-gRmubr.js")
if os.path.exists(js_path):
    with open(js_path, "r", encoding="utf-8") as jf:
        js = jf.read()
    # Patch the logo path inside the compiled bundle so React resolves it
    # to an embedded data URI at runtime (fixes both TopBar and Sidebar).
    js = js.replace('"/jas-logo.png"', f'"{logo_data_uri}"')
    js = js.replace("'/jas-logo.png'", f"'{logo_data_uri}'")
    # Rewrite the Compendium PDF URL prefix inside the bundle so React
    # points to Streamlit's static file endpoint (/app/static/references/).
    # Covers both the template literal `/references/${encodeURIComponent(yn[i])}`
    # and the pre-computed `/references/%5B...%5D...pdf` constants.
    js = js.replace("/references/", "/app/static/references/")
    html = html.replace(
        '<script type="module" crossorigin src="/assets/index-B-gRmubr.js"></script>',
        f"<script type=\"module\">{js}</script>",
    )

# Replace any static HTML references as a safety net
html = html.replace('src="/jas-logo.png"', f'src="{logo_data_uri}"')
html = html.replace('href="/jas-logo.png"', f'href="{logo_data_uri}"')

st.components.v1.html(html, height=1200, scrolling=True)
