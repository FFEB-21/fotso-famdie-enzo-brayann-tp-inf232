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
    background: line
