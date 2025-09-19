# ui_nav.py — Sleek top navigation bar for Streamlit multipage apps
# How to use (in each page, near the top, right after set_page_config):
#   from ui_nav import render_top_nav
#   render_top_nav(active="Family Chart")  # pass the current page label
#
# Notes
# - Uses st.page_link to link to other pages; adjust paths/labels to match your app.
# - Works alongside the default sidebar; you can also hide the default sidebar header.
# - Keep labels short (max ~18 chars) for clean layout.

import streamlit as st

# ---------- THEMEABLE SETTINGS ----------
PRIMARY = "#0F766E"     # teal-700
PRIMARY_HOVER = "#115E59"  # teal-800
TEXT = "#0A0A0A"
MUTED = "#6B7280"       # gray-500
BG = "#FFFFFF"
BORDER = "#E5E7EB"      # gray-200
ACTIVE_BG = "#ECFEFF"   # cyan-50

NAV_ITEMS = [
    {"label": "Home",            "icon": "🏠", "page": "app.py"},
    {"label": "Gene Detection",  "icon": "🧫", "page": "pages/2_Gene_Detection.py"},
    {"label": "Delivery Lab",    "icon": "🚚", "page": "pages/3_Delivery_Lab.py"},
    {"label": "Reports",         "icon": "📄", "page": "pages/4_Reports.py"},
    {"label": "Learning Mode",   "icon": "📚", "page": "pages/5_Learning_Mode.py"},
    {"label": "Family Chart",    "icon": "👪", "page": "pages/6_Family_Chart.py"},
]


def _inject_css():
    st.markdown(
        f"""
        <style>
        /* Reset spacing at the very top */
        .block-container {{padding-top: 1.2rem;}}

        /* Top nav wrapper */
        .gnv-nav {{
            position: sticky;
            top: 0;
            z-index: 100;
            background: {BG};
            border-bottom: 1px solid {BORDER};
            padding: 0.5rem 0.25rem;
        }}
        .gnv-inner {{
            display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
        }}
        .gnv-brand {{
            display: flex; align-items: center; gap: .6rem; margin-right: .5rem;
        }}
        .gnv-logo {{
            width: 28px; height: 28px; border-radius: 8px; background: linear-gradient(135deg, {PRIMARY}, #22D3EE);
        }}
        .gnv-title {{
            font-weight: 700; color: {TEXT}; letter-spacing: .2px;
        }}
        .gnv-spacer {{ flex: 1; }}

        /* Pills */
        .gnv-pill {{
            display: inline-flex; align-items: center; gap: .4rem;
            padding: 8px 12px; border-radius: 999px;
            color: {TEXT}; border: 1px solid {BORDER}; background: #fff;
            text-decoration: none; font-weight: 600; font-size: 0.92rem;
            transition: all .15s ease;
        }}
        .gnv-pill:hover {{
            border-color: {PRIMARY}; box-shadow: 0 1px 0 rgba(0,0,0,.03);
        }}
        .gnv-pill.active {{
            color: {PRIMARY_HOVER}; background: {ACTIVE_BG}; border-color: {PRIMARY};
        }}

        /* Optional right actions (e.g., link to docs) */
        .gnv-action {{
            padding: 8px 10px; border-radius: 8px; border: 1px dashed {BORDER}; color: {MUTED};
            text-decoration: none; font-weight: 600; font-size: 0.9rem;
        }}
        .gnv-action:hover {{ border-color: {PRIMARY}; color: {PRIMARY_HOVER}; }}

        /* Hide default sidebar title bar */
        [data-testid="stSidebarNav"] > div:first-child {{ display: none; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_top_nav(active: str = ""):
    """Render a sleek top navigation bar.

    Args:
        active: the label of the page that is currently open (e.g., "Family Chart").
    """
    _inject_css()

    # Build HTML nav; we use st.page_link for actual links below to keep keyboard/ARIA support.
    st.markdown(
        """
        <div class="gnv-nav">
          <div class="gnv-inner">
            <div class="gnv-brand">
              <div class="gnv-logo"></div>
              <div class="gnv-title">Genovate</div>
            </div>
            <div class="gnv-spacer"></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Render pills with st.page_link so they are real links but styled as pills
    cols = st.columns(len(NAV_ITEMS))
    for i, item in enumerate(NAV_ITEMS):
        is_active = (item["label"].lower() == (active or "").lower())
        klass = "gnv-pill active" if is_active else "gnv-pill"
        with cols[i]:
            # st.page_link renders a standard link; we wrap it in a styled container
            st.markdown(
                f"<div class='{klass}'>" \
                f"{item['icon']}" \
                f" {st.page_link(item['page'], label=item['label'])}</div>",
                unsafe_allow_html=True,
            )

    # Optional: right-aligned actions (docs/about). Uncomment if needed.
    # st.markdown("<div style='text-align:right; margin-top:.5rem'>"
    #             "<a class='gnv-action' href='https://your-docs-url' target='_blank'>Docs</a>"
    #             "</div>", unsafe_allow_html=True)
