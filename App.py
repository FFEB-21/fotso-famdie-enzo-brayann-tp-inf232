import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AgroStat Cameroun | TP INF232",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --green-dark: #1a3a2a;
    --green-mid:  #2d6a4f;
    --green-light:#52b788;
    --gold:       #d4a017;
    --cream:      #f8f4ec;
    --text-dark:  #1c1c1c;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--cream);
    color: var(--text-dark);
}

/* ── HEADER BANNER ── */
.hero-banner {
    background: linear-gradient(135deg, #1a3a2a 0%, #2d6a4f 60%, #52b788 100%);
    border-radius: 16px;
    padding: 2.5rem 2rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: "🌾";
    font-size: 8rem;
    position: absolute;
    right: 2rem;
    top: 50%;
    transform: translateY(-50%);
    opacity: 0.15;
}
.hero-banner h1 {
    font-family: 'Playfair Display', serif;
    color: #fff;
    font-size: 2.4rem;
    margin: 0 0 .3rem;
    letter-spacing: -0.5px;
}
.hero-banner p  { color: #b7e4c7; margin: 0; font-size: .95rem; }
.badge {
    display: inline-block;
    background: var(--gold);
    color: #fff;
    font-size: .72rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: .25rem .8rem;
    border-radius: 99px;
    margin-bottom: .75rem;
}

/* ── METRIC CARDS ── */
.metric-grid { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
.metric-card {
    background: white;
    border-left: 5px solid var(--green-light);
    border-radius: 12px;
    padding: 1rem 1.4rem;
    flex: 1 1 140px;
    box-shadow: 0 2px 12px rgba(0,0,0,.06);
}
.metric-card .val { font-size: 1.9rem; font-weight: 700; color: var(--green-dark); }
.metric-card .lbl { font-size: .78rem; color: #777; text-transform: uppercase; letter-spacing: .8px; }

/* ── SECTION TITLES ── */
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.35rem;
    color: var(--green-dark);
    border-bottom: 2px solid var(--green-light);
    padding-bottom: .4rem;
    margin: 1.5rem 0 1rem;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: var(--green-dark) !important;
    padding-top: 1rem;
}
[data-testid="stSidebar"] * { color: #d8f3dc !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label { color: #b7e4c7 !important; }

/* ── FORM ELEMENTS ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div { border-radius: 8px !important; }

/* ── FOOTER ── */
.footer {
    text-align: center;
    font-size: .78rem;
    color: #aaa;
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid #e0d8cc;
}
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
if "records" not in st.session_state:
    st.session_state.records = []

# ─── HELPERS ──────────────────────────────────────────────────────────────────
REGIONS = ["Adamaoua","Centre","Est","Extrême-Nord","Littoral",
           "Nord","Nord-Ouest","Ouest","Sud","Sud-Ouest"]
CULTURES = ["Maïs","Manioc","Cacao","Café","Plantain","Igname",
            "Arachide","Soja","Riz","Sorgho"]
SAISONS  = ["Saison sèche","Grande saison des pluies","Petite saison des pluies"]
MODES    = ["Traditionnel","Semi-mécanisé","Mécanisé","Agroforesterie"]

def stats_desc(series: pd.Series) -> dict:
    s = series.dropna()
    if s.empty:
        return {}
    return {
        "N": len(s), "Moyenne": round(s.mean(),2),
        "Médiane": round(s.median(),2), "Écart-type": round(s.std(),2),
        "Min": round(s.min(),2), "Max": round(s.max(),2),
        "Q1": round(s.quantile(.25),2), "Q3": round(s.quantile(.75),2),
        "Asymétrie": round(s.skew(),3), "Kurtosis": round(s.kurtosis(),3),
    }

def make_df() -> pd.DataFrame:
    return pd.DataFrame(st.session_state.records)

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌿 AgroStat")
    st.markdown("**Navigation**")
    page = st.radio("", ["📋 Saisie", "📊 Analyse", "📂 Données", "ℹ️ À propos"], label_visibility="collapsed")
    st.divider()
    st.markdown("**Filtres globaux**")
    f_region  = st.multiselect("Région", REGIONS, default=REGIONS)
    f_culture = st.multiselect("Culture", CULTURES, default=CULTURES)
    st.divider()
    st.caption("TP INF232 — EC2\nFotso Famdie Enzo Brayann\n#23U2652")

# ─── HERO ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
  <div class="badge">TP INF 232 · EC2 · 2026</div>
  <h1>🌿 AgroStat Cameroun</h1>
  <p>Plateforme de collecte & analyse descriptive des données agricoles · Réalisée par <strong>Fotso Famdie Enzo Brayann</strong> · Matricule 23U2652</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE : SAISIE
# ══════════════════════════════════════════════════════════════════════════════
if "Saisie" in page:
    st.markdown('<div class="section-title">📋 Formulaire de collecte</div>', unsafe_allow_html=True)
    st.markdown("Renseignez les données d'une exploitation agricole camerounaise.")

    with st.form("saisie_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            nom      = st.text_input("Nom de l'exploitant", placeholder="Jean Nkono")
            region   = st.selectbox("Région", REGIONS)
            culture  = st.selectbox("Culture principale", CULTURES)
        with c2:
            superficie = st.number_input("Superficie (ha)", 0.1, 500.0, 2.0, step=0.1)
            rendement  = st.number_input("Rendement (t/ha)", 0.1, 50.0, 3.0, step=0.1)
            production = st.number_input("Production totale (t)", 0.1, 5000.0, 6.0, step=0.1)
        with c3:
            saison    = st.selectbox("Saison", SAISONS)
            mode      = st.selectbox("Mode de culture", MODES)
            prix_kg   = st.number_input("Prix de vente (FCFA/kg)", 50, 5000, 350, step=10)

        c4, c5 = st.columns(2)
        with c4:
            cout_prod  = st.number_input("Coût de production (FCFA)", 0, 10_000_000, 150_000, step=5000)
            nb_actifs  = st.number_input("Nombre d'actifs agricoles", 1, 50, 3)
        with c5:
            acces_eau  = st.checkbox("Accès à l'irrigation")
            intrants   = st.checkbox("Utilisation d'engrais/pesticides")
            formation  = st.checkbox("Formé aux bonnes pratiques agricoles")

        obs = st.text_area("Observations", placeholder="Remarques libres…", height=70)
        submitted = st.form_submit_button("✅ Enregistrer la fiche", use_container_width=True)

    if submitted:
        if not nom.strip():
            st.error("Veuillez entrer le nom de l'exploitant.")
        else:
            revenu = production * 1000 * prix_kg - cout_prod
            record = {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Exploitant": nom.strip(), "Région": region, "Culture": culture,
                "Superficie_ha": superficie, "Rendement_t_ha": rendement,
                "Production_t": production, "Saison": saison, "Mode": mode,
                "Prix_FCFA_kg": prix_kg, "Coût_prod_FCFA": cout_prod,
                "Nb_actifs": nb_actifs, "Irrigation": acces_eau,
                "Engrais": intrants, "Formation": formation,
                "Revenu_net_FCFA": revenu, "Observations": obs,
            }
            st.session_state.records.append(record)
            st.success(f"✅ Fiche de **{nom}** enregistrée ! ({len(st.session_state.records)} fiche(s) au total)")
            st.balloons()

    # Démo data
    st.divider()
    col_demo, col_reset = st.columns([1, 1])
    with col_demo:
        if st.button("🎲 Générer 30 fiches de démonstration", use_container_width=True):
            np.random.seed(42)
            demo = []
            for i in range(30):
                sup  = round(np.random.uniform(0.5, 20), 1)
                rend = round(np.random.uniform(1, 8), 2)
                prod = round(sup * rend, 2)
                prix = int(np.random.choice([250,300,350,400,500,750,1200,2000]))
                cout = int(np.random.uniform(50_000, 800_000))
                rev  = prod * 1000 * prix - cout
                demo.append({
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Exploitant": f"Exploitant_{i+1:02d}",
                    "Région": np.random.choice(REGIONS),
                    "Culture": np.random.choice(CULTURES),
                    "Superficie_ha": sup, "Rendement_t_ha": rend,
                    "Production_t": prod,
                    "Saison": np.random.choice(SAISONS),
                    "Mode": np.random.choice(MODES),
                    "Prix_FCFA_kg": prix, "Coût_prod_FCFA": cout,
                    "Nb_actifs": int(np.random.randint(1,10)),
                    "Irrigation": bool(np.random.choice([True,False])),
                    "Engrais":    bool(np.random.choice([True,False])),
                    "Formation":  bool(np.random.choice([True,False])),
                    "Revenu_net_FCFA": int(rev),
                    "Observations": "",
                })
            st.session_state.records.extend(demo)
            st.success("30 fiches de démonstration ajoutées !")
            st.rerun()
    with col_reset:
        if st.button("🗑️ Vider toutes les fiches", use_container_width=True):
            st.session_state.records = []
            st.warning("Toutes les fiches ont été supprimées.")
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE : ANALYSE
# ══════════════════════════════════════════════════════════════════════════════
elif "Analyse" in page:
    st.markdown('<div class="section-title">📊 Analyse descriptive</div>', unsafe_allow_html=True)

    df_all = make_df()
    if df_all.empty:
        st.info("⚠️ Aucune donnée disponible. Ajoutez des fiches dans la page **Saisie**.")
        st.stop()

    # Filtres
    df = df_all[df_all["Région"].isin(f_region) & df_all["Culture"].isin(f_culture)].copy()
    if df.empty:
        st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
        st.stop()

    n = len(df)
    # ── KPI ────────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="metric-grid">
      <div class="metric-card"><div class="val">{n}</div><div class="lbl">Fiches</div></div>
      <div class="metric-card"><div class="val">{df['Superficie_ha'].sum():.1f}</div><div class="lbl">Hectares totaux</div></div>
      <div class="metric-card"><div class="val">{df['Rendement_t_ha'].mean():.2f}</div><div class="lbl">Rendement moy (t/ha)</div></div>
      <div class="metric-card"><div class="val">{df['Production_t'].sum():.1f}</div><div class="lbl">Production totale (t)</div></div>
      <div class="metric-card"><div class="val">{df['Revenu_net_FCFA'].mean()/1e6:.2f}M</div><div class="lbl">Revenu net moy (FCFA)</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── STATISTIQUES DESCRIPTIVES ───────────────────────────────────────────────
    st.markdown('<div class="section-title">Statistiques descriptives</div>', unsafe_allow_html=True)
    var = st.selectbox("Variable à analyser", ["Rendement_t_ha","Superficie_ha","Production_t","Prix_FCFA_kg","Revenu_net_FCFA","Nb_actifs"])
    s = df[var]
    stats = stats_desc(s)
    if stats:
        cols = st.columns(len(stats))
        for col, (k,v) in zip(cols, stats.items()):
            col.metric(k, v)

    # ── GRAPHIQUES ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Visualisations</div>', unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["Distribution","Par région","Par culture","Corrélations"])

    with tab1:
        fig = make_subplots(rows=1, cols=2,
                            subplot_titles=[f"Histogramme – {var}", f"Boîte à moustaches – {var}"])
        fig.add_trace(go.Histogram(x=s, marker_color="#52b788", name="Fréquence"), row=1, col=1)
        fig.add_trace(go.Box(y=s, marker_color="#2d6a4f", name=var), row=1, col=2)
        fig.update_layout(height=380, showlegend=False, plot_bgcolor="#f8f4ec", paper_bgcolor="#f8f4ec")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        agg_r = df.groupby("Région")[var].mean().reset_index().sort_values(var, ascending=True)
        fig2 = px.bar(agg_r, x=var, y="Région", orientation="h",
                      color=var, color_continuous_scale=["#b7e4c7","#1a3a2a"],
                      title=f"Moyenne de {var} par région")
        fig2.update_layout(plot_bgcolor="#f8f4ec", paper_bgcolor="#f8f4ec", height=380)
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        agg_c = df.groupby("Culture")[var].mean().reset_index().sort_values(var)
        fig3 = px.bar(agg_c, x="Culture", y=var,
                      color=var, color_continuous_scale=["#d8f3dc","#1a3a2a"],
                      title=f"Moyenne de {var} par culture")
        fig3.update_layout(plot_bgcolor="#f8f4ec", paper_bgcolor="#f8f4ec", height=380)
        st.plotly_chart(fig3, use_container_width=True)

    with tab4:
        num_cols = ["Superficie_ha","Rendement_t_ha","Production_t","Prix_FCFA_kg",
                    "Coût_prod_FCFA","Nb_actifs","Revenu_net_FCFA"]
        corr = df[num_cols].corr()
        fig4 = px.imshow(corr, text_auto=".2f", color_continuous_scale=["#fff","#2d6a4f"],
                         title="Matrice de corrélation", aspect="auto")
        fig4.update_layout(height=420, paper_bgcolor="#f8f4ec")
        st.plotly_chart(fig4, use_container_width=True)

    # ── RÉPARTITIONS CATÉGORIELLES ──────────────────────────────────────────────
    st.markdown('<div class="section-title">Répartitions catégorielles</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        fig_m = px.pie(df, names="Mode", title="Mode de culture", color_discrete_sequence=px.colors.sequential.Greens)
        fig_m.update_layout(paper_bgcolor="#f8f4ec", height=300)
        st.plotly_chart(fig_m, use_container_width=True)
    with c2:
        fig_s = px.pie(df, names="Saison", title="Saison", color_discrete_sequence=px.colors.sequential.YlGn)
        fig_s.update_layout(paper_bgcolor="#f8f4ec", height=300)
        st.plotly_chart(fig_s, use_container_width=True)
    with c3:
        bool_data = pd.DataFrame({
            "Indicateur": ["Irrigation","Engrais","Formation"],
            "Oui (%)": [df["Irrigation"].mean()*100, df["Engrais"].mean()*100, df["Formation"].mean()*100]
        })
        fig_b = px.bar(bool_data, x="Indicateur", y="Oui (%)", title="Pratiques agricoles (%)",
                       color="Oui (%)", color_continuous_scale=["#b7e4c7","#1a3a2a"], range_y=[0,100])
        fig_b.update_layout(paper_bgcolor="#f8f4ec", height=300)
        st.plotly_chart(fig_b, use_container_width=True)

    # ── SCATTER REVENU vs SUPERFICIE ───────────────────────────────────────────
    st.markdown('<div class="section-title">Revenu net vs Superficie</div>', unsafe_allow_html=True)
    fig5 = px.scatter(df, x="Superficie_ha", y="Revenu_net_FCFA",
                      color="Culture", size="Production_t", hover_name="Exploitant",
                      trendline="ols",
                      color_discrete_sequence=px.colors.qualitative.Dark24,
                      title="Revenu net (FCFA) en fonction de la superficie")
    fig5.update_layout(paper_bgcolor="#f8f4ec", plot_bgcolor="#f8f4ec", height=420)
    st.plotly_chart(fig5, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE : DONNÉES
# ══════════════════════════════════════════════════════════════════════════════
elif "Données" in page:
    st.markdown('<div class="section-title">📂 Table des données collectées</div>', unsafe_allow_html=True)
    df = make_df()
    if df.empty:
        st.info("Aucune donnée enregistrée.")
    else:
        df_f = df[df["Région"].isin(f_region) & df["Culture"].isin(f_culture)]
        st.dataframe(df_f, use_container_width=True, height=450)

        # Export CSV
        csv = df_f.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Télécharger en CSV", csv, "agrostat_donnees.csv", "text/csv", use_container_width=True)

        # Export Excel
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df_f.to_excel(writer, index=False, sheet_name="Données")
        st.download_button("⬇️ Télécharger en Excel", buf.getvalue(),
                           "agrostat_donnees.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE : À PROPOS
# ══════════════════════════════════════════════════════════════════════════════
elif "propos" in page:
    st.markdown('<div class="section-title">ℹ️ À propos de l\'application</div>', unsafe_allow_html=True)
    st.markdown("""
**AgroStat Cameroun** est une application web de collecte et d'analyse descriptive des données agricoles au Cameroun,
développée dans le cadre du **TP INF 232 – EC2 (2026)**.

### 🎯 Objectif
Permettre aux agents de terrain de saisir les données d'exploitations agricoles et d'obtenir
instantanément des **statistiques descriptives** et des **visualisations** interactives.

### 📐 Fonctionnalités
| Fonctionnalité | Description |
|---|---|
| 📋 Saisie | Formulaire structuré multi-champs |
| 📊 Analyse | Statistiques, histogrammes, boîtes, corrélations |
| 🗺️ Filtres | Par région et culture |
| 📂 Export | CSV et Excel téléchargeables |
| 🎲 Démo | Génération de données aléatoires |

### 🛠️ Technologies
- **Python 3.11** · **Streamlit** · **Pandas** · **Plotly** · **NumPy** · **OpenPyXL**

---
**👨‍💻 Réalisé par :** Fotso Famdie Enzo Brayann  
**🎓 Matricule :** 23U2652  
**📚 Cours :** INF 232 – EC2  
**🗓️ Date limite :** 30 Avril 2026  
""")

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  🌿 AgroStat Cameroun · TP INF 232 EC2 · Fotso Famdie Enzo Brayann · Matricule 23U2652 · 2026
</div>
""", unsafe_allow_html=True)
