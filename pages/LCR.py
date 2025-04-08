import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Calculateur du LCR", layout="wide")
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

    with st.container():
        col = st.container()
        with col:
            accueil_col = st.columns([1])[0]
            with accueil_col:
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
        if st.button("📊 MNI"):
            st.switch_page("pages/MNI.py")

    with st.expander("📗 Risque de change"):
        if st.button("💱 Risque de change"):
            st.switch_page("pages/RISQUE_DE_CHANGE.py")

st.title("Calculateur du LCR (Liquidity Coverage Ratio)")

# Upload des fichiers depuis l'utilisateur
st.subheader("📂 Chargement des fichiers Excel")

col1, col2 = st.columns(2)
with col1:
    file_encours = st.file_uploader("Balance Globale", type="xlsx")
    file_echeancier = st.file_uploader("Échéancier (04.LDSCHED_20211231 Paris+Chypre.xlsx)", type="xlsx")
with col2:
    file_emplois = st.file_uploader("Emplois Interbancaires (03.Base Emplois Interbancaires 31122021.xlsx)", type="xlsx")

# Entrées manuelles (idée 5)
st.subheader("⚙️ Modifier manuellement HQLA ou Sorties si besoin")
hqla_override = st.number_input("Valeur manuelle des HQLA (laisser vide pour valeur automatique)", min_value=0.0, step=1000.0, format="%.2f")
sorties_override = st.number_input("Valeur manuelle des Sorties nettes de trésorerie", min_value=0.0, step=1000.0, format="%.2f")

if st.button("🔍 Calculer le LCR"):
    if not all([file_encours, file_echeancier, file_emplois]):
        st.error("⚠️ Merci de charger les 4 fichiers requis.")
    else:
        try:
            df_balance = pd.read_excel(file_encours, sheet_name="Balance")
            df_echeancier = pd.read_excel(file_echeancier, sheet_name="LDSCHED_20211231")
            df_emplois = pd.read_excel(file_emplois, sheet_name="Feuil1")

            if "Level" not in df_balance.columns:
                st.error("La colonne 'Level' est absente dans le fichier de balance.")
                st.stop()

            df_balance["c/v LCY balance"] = df_balance["c/v LCY balance"].abs()
            list_1 = df_balance[df_balance["Level"] == 1]["c/v LCY balance"].sum()
            list_2a = df_balance[df_balance["Level"] == "2a"]["c/v LCY balance"].sum() * 0.85
            list_2b = df_balance[df_balance["Level"] == "2b"]["c/v LCY balance"].sum() * 0.5
            total_HQLA = list_1 + list_2a + list_2b

            df_balance["c/v LCY balance"] = df_balance["c/v LCY balance"].abs()
            ponderations_sorties = {
    40: 100, 60: 10, 70: 15, 80: 5, 90: 3, 110: 10, 140: 5, 150: 25, 170: 25, 180: 100, 190: 25,
    200: 25, 220: 100, 230: 100, 250: 20, 260: 40, 280: 20, 290: 10, 300: 100, 320: 100, 330: 100,
    340: 100, 370: 100, 380: 100, 390: 100, 400: 100, 420: 100, 430: 100, 440: 100, 450: 50,
    480: 5, 490: 10, 510: 5, 520: 10, 530: 200, 540: 200, 560: 75, 590: 5, 600: 30, 610: 200,
    630: 10, 640: 100, 660: 5, 670: 30, 680: 200, 700: 75, 710: 100, 900: 100, 910: 100, 1040: 7,
    1050: 15, 1060: 25, 1070: 30, 1080: 35, 1090: 50, 1110: 25, 1120: 100
}  # Même dictionnaire qu'avant
            sorties_treso = sum(
                df_balance[df_balance["Code category"] == cat]["c/v LCY balance"].sum() * (weight / 100)
                for cat, weight in ponderations_sorties.items()
            )

            for df in [df_echeancier, df_emplois]:
                df["c/v LCY balance"] = df["c/v LCY balance"].abs()

            ponderations_entrees = {
    40: 100, 60: 50, 70: 50, 80: 50, 90: 50, 130: 5, 150: 100, 160: 100, 170: 100, 180: 100, 190: 100,
    200: 20, 210: 100, 220: 100, 230: 100, 260: 100, 290: 100, 300: 93, 310: 85, 320: 75, 330: 70,
    340: 65, 350: 50, 380: 50, 390: 100, 400: 100
}  # Même dictionnaire qu'avant
            entree_treso = 0
            for df in [df_echeancier, df_emplois]:
                for cat, weight in ponderations_entrees.items():
                    filtered_sum = df[df["Code category"] == cat]["c/v LCY balance"].sum()
                    entree_treso += filtered_sum * (weight / 100)

            if entree_treso > 0.75 * sorties_treso:
                sorties_nettes_LCR = sorties_treso * 0.25
            else:
                sorties_nettes_LCR = sorties_treso - entree_treso

            # Override manuel si précisé
            if hqla_override > 0:
                total_HQLA = hqla_override
            if sorties_override > 0:
                sorties_nettes_LCR = sorties_override

            LCR = (total_HQLA / sorties_nettes_LCR) * 100 if sorties_nettes_LCR != 0 else 0

            # Résultats
            st.success("✅ Calcul terminé !")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("🔒 Total HQLA pondéré (€)", f"{total_HQLA:,.2f}")
            col2.metric("📤 Sorties de trésorerie (€)", f"{sorties_treso:,.2f}")
            col3.metric("📥 Entrées de trésorerie (€)", f"{entree_treso:,.2f}")
            st.metric("📊 Sorties nettes de trésorerie (€)", f"{sorties_nettes_LCR:,.2f}")
            col4.metric("🧮 LCR (%)", f"{LCR:.2f} %")

            # Interprétation (idée 3)
            if LCR < 100:
                st.warning("⚠️ Le LCR est inférieur à 100% → la banque ne respecte pas les exigences réglementaires.")
            else:
                st.success("✅ Le LCR est conforme aux exigences réglementaires (≥ 100%).")

            # Histogramme des niveaux HQLA (idée 2)
            st.subheader("📊 Répartition des HQLA")
            fig, ax = plt.subplots()
            ax.bar(["Niveau 1", "Niveau 2a", "Niveau 2b"], [list_1, list_2a, list_2b], color=['#1f77b4', '#ff7f0e', '#2ca02c'])
            ax.set_ylabel("Montant (€)")
            ax.set_title("Répartition des HQLA par niveau")
            st.pyplot(fig)

        except Exception as e:
            st.error(f"❌ Une erreur est survenue : {e}")
else:
    st.info("⬆️ Charge les fichiers, puis clique sur le bouton pour lancer le calcul.")
