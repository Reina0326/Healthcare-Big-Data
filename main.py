import streamlit as st
from streamlit_option_menu import option_menu
from desc import show_descriptive_statistics
from ICD10 import show_food
from home import level_diseace
from PIL import Image
st.set_page_config(layout="wide")

# 📌 CSS: Streamlit default menu, toolbar, footer hide
hide_menu = """
<style>
#MainMenu, footer {visibility: hidden;}
header {visibility: hidden;}
.css-1rs6os.edgvbvh3 {padding-top: 0rem;}
div.block-container {padding-top: 1rem;}
</style>
"""
st.markdown(hide_menu, unsafe_allow_html=True)

image = Image.open('mnums.png')
st.sidebar.image(image,width=250)

# 🎨 Option Menu (Top horizontal)
selected = option_menu(
    menu_title=None,
    options=["🏠 Home", "📊 Descriptive", "🦠 ICD-10 Diseases"],
    icons=["house-fill", "bar-chart-line-fill", "heart-pulse-fill"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {
            "padding": "0!important", 
            "background": "linear-gradient(to right, #fdfbfb, #ebedee)",
            "border-radius": "10px",
            "box-shadow": "0 2px 5px rgba(0,0,0,0.1)",
        },
        "icon": {"color": "#E69F00", "font-size": "18px"},
        "nav-link": {
            "font-size": "16px",
            "font-weight": "500",
            "text-align": "center",
            "margin": "5px",
            "color": "#000",
        },
        "nav-link-selected": {
            "background-color": "#FFB000",
            "color": "white",
            "border-radius": "8px",
        }
    }
)

if selected == "📊 Descriptive":
    show_descriptive_statistics()

elif selected == "🦠 ICD-10 Diseases":
    st.markdown("## 🔍 ICD-10 Disease Categories")
    sub_task = st.selectbox(
        "ICD-10 кодчилолтой disease сонгох:",
        [
            "Diseases of the digestive system (K00-K95)",
            "Certain infectious and parasitic diseases (A00-B99)",
            "Neoplasms (C00-D49)"
        ]
    )
    show_food()

elif selected == "🏠 Home":
    level_diseace()


