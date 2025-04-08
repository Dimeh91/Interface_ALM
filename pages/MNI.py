import streamlit as st
import pandas as pd
import random
from PIL import Image
import os

st.set_page_config(page_title="Calcul de la MNI", layout="wide")
st.markdown("""
<style>
h1 { font-size: 3rem !important; }
h2 { font-size: 2rem !important; }
h3 { font-size: 1.5rem !important; }
p, li, div, .stMarkdown { font-size: 1.3rem !important; }
button[kind="primary"] { font-size: 1.2rem !important; padding: 0.8rem 1.5rem; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
        <style>
        .accueil-btn {
            font-size: 1.4rem;
            font-weight: bold;
            color: white;
            background-color: #F63366;
            border: none;
            padding: 0.6rem 1.2rem;
            border-radius: 5px;
            display: block;
            text-align: center;
            text-decoration: none;
            margin-bottom: 1rem;
        }
        .accueil-btn:hover {
            background-color: #ff4b80;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.button("🏠 Accueil", key="accueil", help="Revenir à l'accueil"):
        st.switch_page("ACCUEIL.py")

    st.title("📁 Navigation")

    with st.expander("📘 Risque de liquidité"):
        if st.button("📊 LCR"):
            st.switch_page("pages/LCR.py")
        if st.button("🏦 NSFR"):
            st.switch_page("pages/NSFR.py")

    with st.expander("📙 Risque de taux"):
        if st.button("📈 EVE"):
            st.switch_page("pages/EVE.py")
        if st.button("📈 MNI"):
            st.switch_page("pages/MNI.py")

    with st.expander("📗 Risque de change"):
        if st.button("💱 Risque de change"):
            st.switch_page("pages/RISQUE_DE_CHANGE.py")

st.title("📊 Calculateur de MNI (Marge Nette d'Intérêt)")

fichier_excel = st.file_uploader("📂 Importer le fichier Excel contenant les feuilles 'Actifs' et 'Passifs'", type="xlsx")

class Banque:
    def __init__(self, actifs, passifs):
        self.actifs = actifs
        self.passifs = passifs

    def calcul_mni(self):
        interets_produits = sum(self.actifs.values())
        interets_charges = sum(self.passifs.values())
        return round(interets_produits - interets_charges, 3)

    def ajuster_taux_interet(self):
        for key in self.actifs:
            facteur = round(random.uniform(1, 3), 2)
            self.actifs[key] *= facteur

        for key in self.passifs:
            facteur = round(random.uniform(0.1, 2), 2)
            self.passifs[key] *= facteur

if fichier_excel and st.button("Calculer la MNI"):
    try:
        df_actifs = pd.read_excel(fichier_excel, sheet_name="Actifs")
        df_passifs = pd.read_excel(fichier_excel, sheet_name="Passifs")

        data_actifs = dict(zip(df_actifs["Catégorie"], df_actifs["Montant (€)"]))
        data_passifs = dict(zip(df_passifs["Catégorie"], df_passifs["Montant (€)"]))

        banque = Banque(data_actifs, data_passifs)

        mni_avant = banque.calcul_mni()
        st.metric("📅 MNI avant ajustement des taux (€)", f"{mni_avant:,.2f}")

        banque.ajuster_taux_interet()
        mni_apres = banque.calcul_mni()
        st.metric("🔄 MNI après ajustement des taux (€)", f"{mni_apres:,.2f}")

        st.subheader("📈 Évolution de la MNI")
        st.line_chart({"Avant ajustement": [mni_avant], "Après ajustement": [mni_apres]})

        with st.expander("📊 Détail des données actuelles (après ajustement)"):
            st.write("### Actifs")
            st.dataframe(pd.DataFrame(list(banque.actifs.items()), columns=["Catégorie", "Montant ajusté (€)"]))

            st.write("### Passifs")
            st.dataframe(pd.DataFrame(list(banque.passifs.items()), columns=["Catégorie", "Montant ajusté (€)"]))

    except Exception as e:
        st.error(f"❌ Une erreur est survenue : {e}")
else:
    st.info("⬆️ Charge un fichier Excel, puis clique sur le bouton pour lancer le calcul.")
