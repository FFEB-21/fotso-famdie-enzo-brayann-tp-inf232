import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="AgroStat Cameroun",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "records" not in st.session_state:
    st.session_state.records = []

REGIONS = ["Adamaoua","Centre","Est","Extreme-Nord","Littoral","Nord","Nord-Ouest","Ouest","Sud","Sud-Ouest"]
CULTURES = ["Mais","Manioc","Cacao","Cafe","Plantain","Igname","Arachide","Soja","Riz","Sorgho"]
SAISONS = ["Saison seche","Grande saison des pluies","Petite saison des pluies"]
MODES = ["Traditionnel","Semi-mecanise","Mecanise","Agroforesterie"]

def stats_desc(series):
    s = series.dropna()
    if s.empty:
        return {}
    return {
        "N": len(s),
        "Moyenne": round(s.mean(), 2),
        "Mediane": round(s.median(), 2),
        "Ecart-type": round(s.std(), 2),
        "Min": round(s.min(), 2),
        "Max": round(s.max(), 2),
        "Q1": round(s.quantile(.25), 2),
        "Q3": round(s.quantile(.75), 2),
        "Asymetrie": round(s.skew(), 3),
        "Kurtosis": round(s.kurtosis(), 3),
    }

def make_df():
    return pd.DataFrame(st.session_state.records)

with st.sidebar:
    st.markdown("### 🌿 AgroStat")
    page = st.radio("Navigation", ["Saisie", "Analyse", "Donnees", "A propos"])
    st.divider()
    f_region = st.multiselect("Region", REGIONS, default=REGIONS)
    f_culture = st.multiselect("Culture", CULTURES, default=CULTURES)
    st.divider()
    st.caption("TP INF232 - EC2 | Fotso Famdie Enzo Brayann | 23U2652")

st.title("🌿 AgroStat Cameroun")
st.markdown("Collecte et analyse des donnees agricoles | **Fotso Famdie Enzo Brayann** | Matricule **23U2652**")
st.divider()

# ===================== SAISIE =====================
if page == "Saisie":
    st.subheader("Formulaire de collecte")

    with st.form("saisie_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)

        with c1:
            nom = st.text_input("Nom de l'exploitant")
            region = st.selectbox("Region", REGIONS)
            culture = st.selectbox("Culture principale", CULTURES)

        with c2:
            superficie = st.number_input("Superficie (ha)", 0.1, 500.0, 2.0, step=0.1)
            rendement = st.number_input("Rendement (t/ha)", 0.1, 50.0, 3.0, step=0.1)
            production = st.number_input("Production totale (t)", 0.1, 5000.0, 6.0, step=0.1)

        with c3:
            saison = st.selectbox("Saison", SAISONS)
            mode = st.selectbox("Mode de culture", MODES)
            prix_kg = st.number_input("Prix FCFA/kg", 50, 5000, 350, step=10)

        c4, c5 = st.columns(2)

        with c4:
            cout_prod = st.number_input("Cout production FCFA", 0, 10000000, 150000, step=5000)
            nb_actifs = st.number_input("Nombre d'actifs", 1, 50, 3)

        with c5:
            acces_eau = st.checkbox("Irrigation")
            intrants = st.checkbox("Engrais")
            formation = st.checkbox("Formation")

        obs = st.text_area("Observations")

        submitted = st.form_submit_button("Enregistrer")

    if submitted:
        if not nom.strip():
            st.error("Nom requis")
        else:
            revenu = production * 1000 * prix_kg - cout_prod

            st.session_state.records.append({
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Exploitant": nom,
                "Region": region,
                "Culture": culture,
                "Superficie_ha": superficie,
                "Rendement_t_ha": rendement,
                "Production_t": production,
                "Saison": saison,
                "Mode": mode,
                "Prix_FCFA_kg": prix_kg,
                "Cout_prod_FCFA": cout_prod,
                "Nb_actifs": nb_actifs,
                "Irrigation": acces_eau,
                "Engrais": intrants,
                "Formation": formation,
                "Revenu_net_FCFA": revenu,
                "Observations": obs,
            })

            st.success("Fiche enregistrée !")
            st.balloons()

# ===================== ANALYSE =====================
elif page == "Analyse":
    st.subheader("Analyse")

    df = make_df()
    if df.empty:
        st.info("Pas de données")
        st.stop()

    df = df[df["Region"].isin(f_region) & df["Culture"].isin(f_culture)]

    st.metric("Fiches", len(df))
    st.metric("Production totale", round(df["Production_t"].sum(), 1))

    fig = px.histogram(df, x="Rendement_t_ha")
    st.plotly_chart(fig, use_container_width=True)

# ===================== DONNEES =====================
elif page == "Donnees":
    df = make_df()

    if df.empty:
        st.info("Aucune donnée")
    else:
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Télécharger CSV", csv, "agrostat.csv")

# ===================== A PROPOS =====================
else:
    st.subheader("A propos")
    st.write("AgroStat Cameroun - Projet INF232")
