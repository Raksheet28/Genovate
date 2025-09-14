# streamlit_app.py
import streamlit as st

st.set_page_config(page_title="Genovate", page_icon="🧬", layout="wide")

st.title("Genovate")
st.write("Welcome! Use the left navigation to explore pages.")
st.page_link("pages/1_Home.py", label="🏠 Go to Home", icon="🏠")
st.page_link("pages/2_Simulation.py", label="🎯 Simulation", icon="🎯")
st.page_link("pages/3_Gene_Detection.py", label="🧪 Gene Detection", icon="🧪")
st.page_link("pages/4_Sequence_Viewer.py", label="🧫 Sequence Viewer", icon="🧫")
st.page_link("pages/5_Learning_Mode.py", label="📘 Learning Mode", icon="📘")
