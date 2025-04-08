import streamlit as st
from datetime import datetime
from PIL import Image
import os

st.set_page_config(page_title="Accueil - ALM", layout="wide")

# 🔧 CSS personnalisé pour agrandir les textes
st.markdown("""
<style>
h1 { font-size: 3rem !important; }
h2 { font-size: 2rem !important; }
h3 { font-size: 1.5rem !important; }
p, li, div, .stMarkdown { font-size: 1.3rem !important; }
button[kind="primary"] { font-size: 1.2rem !important; padding: 0.8rem 1.5rem; }
</style>
""", unsafe_allow_html=True)

# 📂 Barre latérale avec navigation personnalisée
with st.sidebar:
    st.title("📂 Navigation")

    with st.expander("📘 Risque de liquidité"):
        if st.button("💧 LCR"):
            st.switch_page("pages/LCR.py")
        if st.button("🏦 NSFR"):
            st.switch_page("pages/NSFR.py")

    with st.expander("📙 Risque de taux"):
        if st.button("📈 EVE"):
            st.switch_page("pages/EVE.py")
        if st.button("📊 MNI"):
            st.switch_page("pages/MNI.py")  

    with st.expander("📗 Risque de change"):
        if st.button("💱 Risque de change"):
            st.switch_page("pages/RISQUE_DE_CHANGE.py")

# 🖼️ Titre et logo
col_title, col_logo = st.columns([8, 1])
with col_title:
    st.title("📊 Application de gestion des indicateurs ALM")
with col_logo:
    try:
        logo_path = os.path.join(os.path.dirname(__file__), "Logo_esilv_png_blanc.png")
        st.image(Image.open(logo_path), width=90)
    except Exception as e:
        st.warning("Logo introuvable")

# 🕒 Date et heure actuelles
now = datetime.now().strftime("%d/%m/%Y %H:%M")
st.markdown(f"### 🕒 **Date et heure actuelles** : `{now}`")

# 📋 Présentation
st.markdown("""
Bienvenue dans votre tableau de bord de **gestion des indicateurs ALM**.  
Utilisez la barre latérale pour naviguer entre les différents modules :

- 📊 **LCR** : Liquidity Coverage Ratio  
- 📈 **EVE** : Economic Value of Equity  
- 🏦 **NSFR** : Net Stable Funding Ratio  
- 💱 **Risque de change** : Sensibilité au choc et GAP de change  
- 📊 **MNI** : Net Interest Margin
""")

# 🔗 Accès rapide
st.markdown("## 🚀 Accès rapide aux modules")
col1, col2 = st.columns(2)
with col1:
    st.page_link("pages/LCR.py", label="📊 LCR")
    st.page_link("pages/EVE.py", label="📈 EVE")
    st.page_link("pages/MNI.py", label="📊 MNI")
with col2:
    st.page_link("pages/NSFR.py", label="🏦 NSFR")
    st.page_link("pages/RISQUE_DE_CHANGE.py", label="💱 Risque de change")

# ❓ Expander ALM
with st.expander("❓ Qu’est-ce que l’ALM ?"):
    st.markdown("""
    La **gestion actif-passif (ALM)** vise à équilibrer les actifs et les passifs d'une institution financière
    pour garantir sa **solvabilité** et sa **liquidité**. Cette application permet de suivre les
    principaux indicateurs de stabilité financière :

    - **NSFR** : stabilité du financement à long terme  
    - **LCR** : liquidité à court terme  
    - **EVE** : sensibilité de la valeur économique à la variation des taux  
    - **VaR & Sensibilité** : exposition au risque de change
    """)

# 👤 Expander À propos
with st.expander("👤 À propos du projet"):
    st.markdown("""
    Cette application a été développée par **Mehdi Lahmer**, **Leo Bengorine**, **Cyprien Duceux**, **Damien Quidal**, **Mathieu Meunier**, **Ange Murielle Modjo Kamdjou**, élèves ingénieur en **M1 à l’ESILV**,
    dans le cadre d’un projet de **gestion des risques ALM**.

    Elle permet d’analyser et de visualiser rapidement les principaux indicateurs de stabilité financière,
    tels que le **LCR**, le **NSFR**, l'**EVE**, la **MNI** et l’exposition au **risque de change**.

    > *Objectif : offrir un outil intuitif pour piloter les indicateurs ALM.*
    """)

st.info("⬅️ Utilisez le menu à gauche ou les boutons ci-dessus pour accéder aux fonctionnalités.")