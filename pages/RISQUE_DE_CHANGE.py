import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm

st.set_page_config(page_title="Risque de Change", layout="wide")

# 🔧 Style CSS pour agrandir la taille des textes
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
                    st.switch_page("streamlit_app.py") 

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

st.title("💱 Analyse du Risque de Change")

fichier = st.file_uploader("📂 Importer le fichier Excel (ex. Données_Risque_Change_ALM.xlsx)", type="xlsx")

if fichier and st.button("Analyser le risque de change"):
    try:
        df = pd.read_excel(fichier, sheet_name="Feuil1")

        # Nettoyage et préparation
        df["Classe"] = df["PCEC Code"].astype(str).str[:1]
        actifs_pcec = df[df["Classe"].isin(["3", "4", "5"])]
        passifs_pcec = df[df["Classe"].isin(["1", "2"])]

        actifs = actifs_pcec.groupby("currency")["CCY balance"].sum()
        passifs = passifs_pcec.groupby("currency")["CCY balance"].sum()
        enc = actifs - passifs
        enc_df = enc.reset_index()
        enc_df.columns = ["currency", "Exposition Nette de Change"]
        enc_df = enc_df.fillna(0)

        st.subheader("📈 Exposition Nette de Change (ENC)")
        st.dataframe(enc_df)

        # Graphe ENC par devise
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        enc_sorted = enc_df.sort_values(by="Exposition Nette de Change")
        bars = ax1.bar(enc_sorted["currency"], enc_sorted["Exposition Nette de Change"],
                       color="skyblue", edgecolor="black")
        ax1.axhline(0, color='red', linestyle="--", linewidth=1.5)
        for bar in bars:
            yval = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.2e}',
                     ha='center', va='bottom' if yval > 0 else 'top', fontsize=8)
        ax1.set_title("Exposition Nette de Change par Devise", fontsize=14)
        ax1.set_xlabel("Devise")
        ax1.set_ylabel("ENC")
        ax1.tick_params(axis='x', rotation=45)
        st.pyplot(fig1)

        # Maturité
        df["Maturity Date"] = df["Maturity Date"].replace("//", "2040-12-31")
        df["Maturity Date"] = pd.to_datetime(df["Maturity Date"], errors="coerce")
        df["Maturity Category"] = pd.cut(
            (df["Maturity Date"] - pd.Timestamp.today()).dt.days / 365,
            bins=[-1, 1, 5, 100],
            labels=["Court Terme", "Moyen Terme", "Long Terme"]
        )

        gap_par_periode_df = df.groupby(["currency", "Maturity Category"])["CCY balance"].sum().reset_index()
        gap_par_periode_df.rename(columns={"CCY balance": "Gap de Change"}, inplace=True)
        gap_par_periode_df["Gap de Change"] = gap_par_periode_df["Gap de Change"].fillna(0)

        st.subheader("📉 Gap de Change par Devise et Maturité")
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        sns.barplot(data=gap_par_periode_df, x="currency", y="Gap de Change",
                    hue="Maturity Category", palette="viridis", edgecolor="black", ax=ax2)
        ax2.axhline(0, color='red', linestyle="--", linewidth=1.5)
        ax2.set_title("Gap de Change par Maturité et Devise", fontsize=14)
        ax2.set_xlabel("Devise")
        ax2.set_ylabel("Gap de Change")
        ax2.tick_params(axis='x', rotation=45)
        st.pyplot(fig2)

        # VaR
        df = df.dropna(subset=["Exchange RATE"])
        df["Returns"] = df["Exchange RATE"].pct_change()
        confidence_level = 0.95
        var_historique = np.percentile(df["Returns"].dropna(), 100 * (1 - confidence_level))
        mean_return = df["Returns"].mean()
        std_dev = df["Returns"].std()
        var_parametrique = norm.ppf(1 - confidence_level) * std_dev

        st.subheader("📉 Valeur à Risque (VaR) - Taux de Change")
        var_results = pd.DataFrame({
            "Méthode": ["Historique", "Paramétrique"],
            "VaR 95%": [var_historique, var_parametrique]
        })
        st.dataframe(var_results)

        # Sensibilité +/- 5%
        variation = 0.05
        enc_df["Impact Choc +5%"] = enc_df["Exposition Nette de Change"] * (1 + variation)
        enc_df["Impact Choc -5%"] = enc_df["Exposition Nette de Change"] * (1 - variation)
        sensitivity_df = enc_df[["currency", "Exposition Nette de Change", "Impact Choc +5%", "Impact Choc -5%"]]

        st.subheader("📈 Sensibilité à une variation de ±5% des taux de change")
        st.dataframe(sensitivity_df)

        fig3, ax3 = plt.subplots(figsize=(12, 6))
        x = np.arange(len(enc_df["currency"]))
        bar_width = 0.3
        ax3.bar(x - bar_width, enc_df["Exposition Nette de Change"], width=bar_width, label="ENC Initiale", color="blue")
        ax3.bar(x, enc_df["Impact Choc +5%"], width=bar_width, label="Impact +5%", color="green")
        ax3.bar(x + bar_width, enc_df["Impact Choc -5%"], width=bar_width, label="Impact -5%", color="red")
        ax3.set_xticks(x)
        ax3.set_xticklabels(enc_df["currency"], rotation=45, ha="right")
        ax3.set_title("Sensibilité aux Variations de Taux de Change", fontsize=14)
        ax3.set_xlabel("Devise")
        ax3.set_ylabel("Exposition Nette de Change")
        ax3.legend()
        st.pyplot(fig3)

    except Exception as e:
        st.error(f"❌ Une erreur est survenue : {e}")
else:
    st.info("Veuillez importer un fichier Excel puis cliquer sur le bouton pour lancer l’analyse.")
