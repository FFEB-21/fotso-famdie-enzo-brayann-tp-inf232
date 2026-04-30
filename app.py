import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from datetime import datetime
import warnings
warnings.filterwarnings(“ignore”)

st.set_page_config(
page_title=“AgroStat Cameroun”,
page_icon=“🌿”,
layout=“wide”,
initial_sidebar_state=“expanded”
)

if “records” not in st.session_state:
st.session_state.records = []

REGIONS = [“Adamaoua”,“Centre”,“Est”,“Extreme-Nord”,“Littoral”,“Nord”,“Nord-Ouest”,“Ouest”,“Sud”,“Sud-Ouest”]
CULTURES = [“Mais”,“Manioc”,“Cacao”,“Cafe”,“Plantain”,“Igname”,“Arachide”,“Soja”,“Riz”,“Sorgho”]
SAISONS = [“Saison seche”,“Grande saison des pluies”,“Petite saison des pluies”]
MODES = [“Traditionnel”,“Semi-mecanise”,“Mecanise”,“Agroforesterie”]

def stats_desc(series):
s = series.dropna()
if s.empty:
return {}
return {
“N”: len(s),
“Moyenne”: round(s.mean(), 2),
“Mediane”: round(s.median(), 2),
“Ecart-type”: round(s.std(), 2),
“Min”: round(s.min(), 2),
“Max”: round(s.max(), 2),
“Q1”: round(s.quantile(.25), 2),
“Q3”: round(s.quantile(.75), 2),
“Asymetrie”: round(s.skew(), 3),
“Kurtosis”: round(s.kurtosis(), 3),
}

def make_df():
return pd.DataFrame(st.session_state.records)

with st.sidebar:
st.markdown(”### 🌿 AgroStat”)
page = st.radio(“Navigation”, [“Saisie”, “Analyse”, “Donnees”, “A propos”])
st.divider()
f_region = st.multiselect(“Region”, REGIONS, default=REGIONS)
f_culture = st.multiselect(“Culture”, CULTURES, default=CULTURES)
st.divider()
st.caption(“TP INF232 - EC2 | Fotso Famdie Enzo Brayann | 23U2652”)

st.title(“🌿 AgroStat Cameroun”)
st.markdown(“Collecte et analyse des donnees agricoles | **Fotso Famdie Enzo Brayann** | Matricule **23U2652**”)
st.divider()

if page == “Saisie”:
st.subheader(“Formulaire de collecte”)

```
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
        prix_kg = st.number_input("Prix de vente FCFA/kg", 50, 5000, 350, step=10)
    c4, c5 = st.columns(2)
    with c4:
        cout_prod = st.number_input("Cout de production FCFA", 0, 10000000, 150000, step=5000)
        nb_actifs = st.number_input("Nombre d'actifs agricoles", 1, 50, 3)
    with c5:
        acces_eau = st.checkbox("Acces a l'irrigation")
        intrants = st.checkbox("Utilisation d'engrais")
        formation = st.checkbox("Forme aux bonnes pratiques")
    obs = st.text_area("Observations", height=70)
    submitted = st.form_submit_button("Enregistrer la fiche", use_container_width=True)

if submitted:
    if not nom.strip():
        st.error("Veuillez entrer le nom de l'exploitant.")
    else:
        revenu = production * 1000 * prix_kg - cout_prod
        record = {
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Exploitant": nom.strip(),
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
        }
        st.session_state.records.append(record)
        st.success("Fiche enregistree ! Total : " + str(len(st.session_state.records)) + " fiche(s)")
        st.balloons()

st.divider()
col_demo, col_reset = st.columns(2)
with col_demo:
    if st.button("Generer 30 fiches demo", use_container_width=True):
        np.random.seed(42)
        demo = []
        for i in range(30):
            sup = round(np.random.uniform(0.5, 20), 1)
            rend = round(np.random.uniform(1, 8), 2)
            prod = round(sup * rend, 2)
            prix = int(np.random.choice([250, 300, 350, 400, 500, 750, 1200, 2000]))
            cout = int(np.random.uniform(50000, 800000))
            rev = prod * 1000 * prix - cout
            demo.append({
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Exploitant": "Exploitant_" + str(i + 1),
                "Region": str(np.random.choice(REGIONS)),
                "Culture": str(np.random.choice(CULTURES)),
                "Superficie_ha": sup,
                "Rendement_t_ha": rend,
                "Production_t": prod,
                "Saison": str(np.random.choice(SAISONS)),
                "Mode": str(np.random.choice(MODES)),
                "Prix_FCFA_kg": prix,
                "Cout_prod_FCFA": cout,
                "Nb_actifs": int(np.random.randint(1, 10)),
                "Irrigation": bool(np.random.choice([True, False])),
                "Engrais": bool(np.random.choice([True, False])),
                "Formation": bool(np.random.choice([True, False])),
                "Revenu_net_FCFA": int(rev),
                "Observations": "",
            })
        st.session_state.records.extend(demo)
        st.success("30 fiches de demonstration ajoutees !")
        st.rerun()
with col_reset:
    if st.button("Vider toutes les fiches", use_container_width=True):
        st.session_state.records = []
        st.warning("Toutes les fiches ont ete supprimees.")
        st.rerun()
```

elif page == “Analyse”:
st.subheader(“Analyse descriptive”)

```
df_all = make_df()
if df_all.empty:
    st.info("Aucune donnee disponible. Ajoutez des fiches dans la page Saisie.")
    st.stop()

df = df_all[df_all["Region"].isin(f_region) & df_all["Culture"].isin(f_culture)].copy()
if df.empty:
    st.warning("Aucune donnee ne correspond aux filtres.")
    st.stop()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Fiches", len(df))
c2.metric("Hectares totaux", round(df["Superficie_ha"].sum(), 1))
c3.metric("Rendement moy t/ha", round(df["Rendement_t_ha"].mean(), 2))
c4.metric("Production totale t", round(df["Production_t"].sum(), 1))
c5.metric("Revenu moy (MFCFA)", round(df["Revenu_net_FCFA"].mean() / 1e6, 2))

st.divider()
st.subheader("Statistiques descriptives")
var = st.selectbox("Variable a analyser", ["Rendement_t_ha", "Superficie_ha", "Production_t", "Prix_FCFA_kg", "Revenu_net_FCFA", "Nb_actifs"])
s = df[var]
stats = stats_desc(s)
if stats:
    cols = st.columns(len(stats))
    for col, (k, v) in zip(cols, stats.items()):
        col.metric(k, v)

st.divider()
st.subheader("Visualisations")
tab1, tab2, tab3, tab4 = st.tabs(["Distribution", "Par region", "Par culture", "Correlations"])

with tab1:
    fig = make_subplots(rows=1, cols=2, subplot_titles=["Histogramme", "Boite a moustaches"])
    fig.add_trace(go.Histogram(x=s, marker_color="#52b788", name="Frequence"), row=1, col=1)
    fig.add_trace(go.Box(y=s, marker_color="#2d6a4f", name=var), row=1, col=2)
    fig.update_layout(height=380, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    agg_r = df.groupby("Region")[var].mean().reset_index().sort_values(var, ascending=True)
    fig2 = px.bar(agg_r, x=var, y="Region", orientation="h",
                  color=var, color_continuous_scale=["#b7e4c7", "#1a3a2a"],
                  title="Moyenne par region")
    fig2.update_layout(height=380)
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    agg_c = df.groupby("Culture")[var].mean().reset_index().sort_values(var)
    fig3 = px.bar(agg_c, x="Culture", y=var,
                  color=var, color_continuous_scale=["#d8f3dc", "#1a3a2a"],
                  title="Moyenne par culture")
    fig3.update_layout(height=380)
    st.plotly_chart(fig3, use_container_width=True)

with tab4:
    num_cols = ["Superficie_ha", "Rendement_t_ha", "Production_t", "Prix_FCFA_kg", "Cout_prod_FCFA", "Nb_actifs", "Revenu_net_FCFA"]
    corr = df[num_cols].corr()
    fig4 = px.imshow(corr, text_auto=".2f", color_continuous_scale=["#fff", "#2d6a4f"],
                     title="Matrice de correlation", aspect="auto")
    fig4.update_layout(height=420)
    st.plotly_chart(fig4, use_container_width=True)

st.divider()
st.subheader("Repartitions categorielles")
c1, c2, c3 = st.columns(3)
with c1:
    fig_m = px.pie(df, names="Mode", title="Mode de culture")
    st.plotly_chart(fig_m, use_container_width=True)
with c2:
    fig_s = px.pie(df, names="Saison", title="Saison")
    st.plotly_chart(fig_s, use_container_width=True)
with c3:
    bool_data = pd.DataFrame({
        "Indicateur": ["Irrigation", "Engrais", "Formation"],
        "Oui (%)": [
            df["Irrigation"].mean() * 100,
            df["Engrais"].mean() * 100,
            df["Formation"].mean() * 100
        ]
    })
    fig_b = px.bar(bool_data, x="Indicateur", y="Oui (%)", title="Pratiques agricoles (%)", range_y=[0, 100])
    st.plotly_chart(fig_b, use_container_width=True)

st.divider()
st.subheader("Revenu net vs Superficie")
fig5 = px.scatter(df, x="Superficie_ha", y="Revenu_net_FCFA",
                  color="Culture", size="Production_t", hover_name="Exploitant",
                  trendline="ols",
                  title="Revenu net en fonction de la superficie")
fig5.update_layout(height=420)
st.plotly_chart(fig5, use_container_width=True)
```

elif page == “Donnees”:
st.subheader(“Table des donnees collectees”)
df = make_df()
if df.empty:
st.info(“Aucune donnee enregistree.”)
else:
df_f = df[df[“Region”].isin(f_region) & df[“Culture”].isin(f_culture)]
st.dataframe(df_f, use_container_width=True, height=450)
csv = df_f.to_csv(index=False).encode(“utf-8”)
st.download_button(“Telecharger CSV”, csv, “agrostat.csv”, “text/csv”, use_container_width=True)
buf = io.BytesIO()
with pd.ExcelWriter(buf, engine=“openpyxl”) as writer:
df_f.to_excel(writer, index=False, sheet_name=“Donnees”)
st.download_button(“Telecharger Excel”, buf.getvalue(), “agrostat.xlsx”,
“application/vnd.openxmlformats-officedocument.spreadsheetml.sheet”,
use_container_width=True)

elif page == “A propos”:
st.subheader(“A propos de l’application”)
st.markdown(”**Application :** AgroStat Cameroun”)
st.markdown(”**Description :** Collecte et analyse descriptive des donnees agricoles au Cameroun”)
st.markdown(”**Realise par :** Fotso Famdie Enzo Brayann”)
st.markdown(”**Matricule :** 23U2652”)
st.markdown(”**Cours :** INF 232 - EC2”)
st.markdown(”**Technologies :** Python - Streamlit - Pandas - Plotly - NumPy - OpenPyXL”)
st.markdown(”**Date limite :** 30 Avril 2026”)

st.divider()
st.caption(“🌿 AgroStat Cameroun - TP INF 232 EC2 - Fotso Famdie Enzo Brayann - Matricule 23U2652 - 2026”)
