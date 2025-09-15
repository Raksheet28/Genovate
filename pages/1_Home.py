# pages/1_Home.py
import streamlit as st

st.set_page_config(page_title="Genovate • Home", page_icon="🏠", layout="wide")

# Sidebar (links are valid pages only)
st.sidebar.page_link("pages/1_Home.py", label="🏠 Home")
st.sidebar.page_link("pages/2_Simulation.py", label="🎯 Simulation")
st.sidebar.page_link("pages/3_Gene_Detection.py", label="🧪 Gene Detection")
st.sidebar.page_link("pages/4_Sequence_Viewer.py", label="🧬 Sequence Viewer")
st.sidebar.page_link("pages/5_Learning_Mode.py", label="📘 Learning Mode")

st.markdown("## Welcome back to Genovate")
st.write("Use the links above to jump directly to a workflow.")
st.page_link("pages/2_Simulation.py", label="🚀 Open Simulation")
st.page_link("pages/3_Gene_Detection.py", label="🧪 Gene Detection")
st.page_link("pages/4_Sequence_Viewer.py", label="🧬 Sequence Viewer")
st.page_link("pages/5_Learning_Mode.py", label="📘 Learning Mode")
