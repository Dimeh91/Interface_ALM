import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calcul de l'EVE", layout="wide")
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
                    st.switch_page("streamlit_app.py")  

    st.title("📁 Navigation")

    with st.expander("📘 Risque de liquidité"):
        if st.button("💧 LCR"):
            st.switch_page("LCR")
        if st.button("🏦 NSFR"):
            st.switch_page("NSFR")

    with st.expander("📙 Risque de taux"):
        if st.button("📈 EVE"):
            st.switch_page("EVE")
        if st.button("📊 MNI"):
            st.switch_page("MNI")

    with st.expander("📗 Risque de change"):
        if st.button("💱 Risque de change"):
            st.switch_page("RISQUE_DE_CHANGE")

st.title("📊 Calculateur d'EVE (Economic Value of Equity)")

st.subheader("📂 Charger le fichier Excel")
fichier_excel = st.file_uploader("Importer le fichier Excel (ex. Picarré2.xlsx)", type=["xlsx"])

def calculer_valeur_actualisee_cash_flows_correcte(fichier_excel, type_element="actif"):
    details = []
    structure_precise = {
        "B et EF": 2,
        "Crédits": 5,
        "Titres de Participation": 2,
        "B et EF Passif": 2,
        "Compte créditeur Passif": 2
    }

    for sheet_name, nombre_elements in structure_precise.items():
        if (type_element == "passif" and "passif" not in sheet_name.lower()) or \
           (type_element == "actif" and "passif" in sheet_name.lower()):
            continue

        df = pd.read_excel(fichier_excel, sheet_name=sheet_name)
        montant_indices = [i for i, val in enumerate(df.iloc[0]) if str(val).strip().lower() == "montant"]

        for index, col_index in enumerate(montant_indices):
            montant_col = df.iloc[0, col_index + 1]
            taux_actualisation_col = df.iloc[1, col_index + 1]
            maturite_col = df.iloc[2, col_index + 1]
            taux_interet_col = df.iloc[3, col_index + 1]

            montant = pd.to_numeric(montant_col, errors='coerce')
            taux_actualisation = pd.to_numeric(taux_actualisation_col, errors='coerce')
            maturite = pd.to_numeric(maturite_col, errors='coerce')
            taux_interet = pd.to_numeric(taux_interet_col, errors='coerce')

            if pd.isna(montant) or pd.isna(taux_actualisation) or pd.isna(maturite) or pd.isna(taux_interet):
                continue

            valeur_actualisee = (montant * taux_interet) / ((1 + taux_actualisation) ** maturite)

            details.append({
                "Feuille": sheet_name,
                "Élément": f"Élément {index + 1}",
                "Montant": montant,
                "Taux d'intérêt": taux_interet,
                "Taux d'actualisation": taux_actualisation,
                "Maturité": maturite,
                "Valeur actualisée": valeur_actualisee
            })

    return pd.DataFrame(details)

if fichier_excel and st.button("Calculer l'EVE"):
    try:
        actifs = calculer_valeur_actualisee_cash_flows_correcte(fichier_excel, "actif")
        passifs = calculer_valeur_actualisee_cash_flows_correcte(fichier_excel, "passif")

        somme_actifs = actifs["Valeur actualisée"].sum()
        somme_passifs = passifs["Valeur actualisée"].sum()
        eve = somme_actifs - somme_passifs

        st.success("✅ Calcul terminé")
        st.metric("💼 Actifs actualisés (€)", f"{somme_actifs:,.2f}")
        st.metric("📉 Passifs actualisés (€)", f"{somme_passifs:,.2f}")
        st.metric("📊 EVE (€)", f"{eve:,.2f}")

        # 🧠 Interprétation de l’EVE
        if eve > 0:
            st.success("🔍 **Interprétation** : L’EVE est positive. La banque dispose d'une marge de sécurité en cas de variation des taux.")
        elif eve < 0:
            st.warning("⚠️ **Interprétation** : L’EVE est négative. Cela signifie une perte de valeur potentielle si les taux évoluent défavorablement.")
        else:
            st.info("ℹ️ **Interprétation** : L’EVE est neutre. La valeur économique des capitaux propres reste stable face aux changements de taux.")

        with st.expander("🔍 Détail des actifs"):
            st.dataframe(actifs)

        with st.expander("🔍 Détail des passifs"):
            st.dataframe(passifs)

    except Exception as e:
        st.error(f"❌ Une erreur est survenue : {e}")
else:
    st.info("Charge un fichier Excel, puis clique sur le bouton pour calculer l'EVE.")
