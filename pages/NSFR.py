import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ✅ Uniformisation
st.set_page_config(page_title="NSFR", layout="wide")
st.markdown("""
<style>
p, li, div, .stMarkdown, .css-1v0mbdj, .e1fqkh3o2 {
    font-size: 1.2rem !important;
}
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

st.title("Calculateur du NSFR (Net Stable Funding Ratio)")



fichier = st.file_uploader("📂 Importer le fichier Excel contenant les feuilles 'Actifs' et 'Passifs'", type="xlsx")

if fichier and st.button("Calculer le NSFR"):
    try:
        xls = pd.ExcelFile(fichier)
        passifs_df = pd.read_excel(xls, sheet_name='Passifs')
        actifs_df = pd.read_excel(xls, sheet_name='Actifs')

        passifs_df['ASF'] = passifs_df['Montant (€)'] * passifs_df['Pondération ASF']
        total_ASF = passifs_df['ASF'].sum()

        actifs_df['RSF'] = actifs_df['Montant (€)'] * actifs_df['Pondération RSF']
        total_RSF = actifs_df['RSF'].sum()

        NSFR = total_ASF / total_RSF if total_RSF != 0 else float('nan')

        st.subheader("📊 Résultats")
        st.metric("Total ASF (€)", f"{total_ASF:,.2f}")
        st.metric("Total RSF (€)", f"{total_RSF:,.2f}")
        st.metric("NSFR", f"{NSFR:.2f}", delta=None)

        if NSFR < 1:
            st.warning("🔻 Le NSFR est inférieur à 1 → besoin de financement plus stable.")
        else:
            st.success("✅ Le NSFR est supérieur ou égal à 1 → la banque a un financement stable suffisant.")

        st.subheader("📉 Répartition des Passifs (ASF)")
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        sns.barplot(x='Catégorie', y='ASF', data=passifs_df, palette="viridis", ax=ax1)
        ax1.set_title("Répartition des Passifs (ASF) par Catégorie")
        ax1.set_xlabel("Catégorie")
        ax1.set_ylabel("Montant ASF (€)")
        ax1.tick_params(axis='x', rotation=45)
        st.pyplot(fig1)

        st.subheader("📈 Répartition des Actifs (RSF)")
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        sns.barplot(x='Catégorie', y='RSF', data=actifs_df, palette="viridis", ax=ax2)
        ax2.set_title("Répartition des Actifs (RSF) par Catégorie")
        ax2.set_xlabel("Catégorie")
        ax2.set_ylabel("Montant RSF (€)")
        ax2.tick_params(axis='x', rotation=45)
        st.pyplot(fig2)

        st.subheader("📅 Évolution du NSFR sur 1 an")
        dates = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
        nsfr_values = [1.97, 2.43, 2.22, 2.11, 1.73, 1.75, 1.67, 2.36, 2.15, 2.24, 1.73, 2.51]
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        sns.lineplot(x=dates, y=nsfr_values, marker='o', color='b', ax=ax3)
        ax3.set_title("Évolution du NSFR sur 1 an")
        ax3.set_xlabel("Mois")
        ax3.set_ylabel("NSFR")
        st.pyplot(fig3)

    except Exception as e:
        st.error(f"❌ Une erreur est survenue : {e}")
else:
    st.info("Veuillez importer un fichier Excel et cliquer sur le bouton pour calculer le NSFR.")
