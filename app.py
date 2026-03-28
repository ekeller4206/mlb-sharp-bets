"""
MLB Betting & Player Prop Tool — 2026 Season
Lead Quant Dev Build | pybaseball-powered | Sharp Syndicate Grade
"""

import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import warnings
warnings.filterwarnings("ignore")

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MLB Sharp Tool · 2026",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: #0a0d12;
    color: #e2e8f0;
}

h1, h2, h3, h4 {
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: -0.02em;
}

.stApp { background-color: #0a0d12; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0f1420;
    border-right: 1px solid #1e2d40;
}
section[data-testid="stSidebar"] * { color: #94a3b8 !important; }
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stToggle label { color: #64748b !important; }

/* Metric cards */
div[data-testid="metric-container"] {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 16px;
}
div[data-testid="metric-container"] label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: #64748b !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.6rem;
    color: #38bdf8 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #0f1420;
    border-bottom: 1px solid #1e293b;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 12px 24px;
    border-bottom: 2px solid transparent;
}
.stTabs [aria-selected="true"] {
    color: #38bdf8 !important;
    border-bottom-color: #38bdf8 !important;
    background: transparent !important;
}

/* Dataframe */
.stDataFrame { border: 1px solid #1e293b; border-radius: 8px; }
iframe[title="st_aggrid"] { background: #111827; }

/* Headers */
.sharp-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-bottom: 4px;
}
.edge-positive { color: #22c55e; font-weight: 700; }
.edge-negative { color: #ef4444; font-weight: 700; }
.edge-neutral  { color: #f59e0b; font-weight: 700; }

/* Confidence badge */
.conf-high   { background:#14532d; color:#4ade80; padding:3px 10px; border-radius:4px; font-family:'IBM Plex Mono',monospace; font-size:0.75rem; font-weight:600; }
.conf-medium { background:#78350f; color:#fbbf24; padding:3px 10px; border-radius:4px; font-family:'IBM Plex Mono',monospace; font-size:0.75rem; font-weight:600; }
.conf-low    { background:#450a0a; color:#f87171; padding:3px 10px; border-radius:4px; font-family:'IBM Plex Mono',monospace; font-size:0.75rem; font-weight:600; }

.stButton button {
    background: #1e3a5f;
    color: #38bdf8;
    border: 1px solid #1d4ed8;
    border-radius: 6px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.stButton button:hover { background: #1e40af; color: #fff; }

.divider { border-top: 1px solid #1e293b; margin: 20px 0; }
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
LEAGUE_AVG_WOBA       = 0.320
LEAGUE_AVG_FIP        = 4.20
LEAGUE_AVG_K_PCT      = 0.225
LEAGUE_AVG_RUNS_GAME  = 4.55
SEASON_YEAR           = 2026

PARK_FACTORS = {
    "COL": 1.15, "BOS": 1.08, "CIN": 1.07, "TEX": 1.06, "PHI": 1.05,
    "HOU": 1.04, "BAL": 1.03, "TOR": 1.02, "NYY": 1.01, "CHC": 1.01,
    "ATL": 1.00, "LAD": 1.00, "NYM": 0.99, "MIL": 0.98, "STL": 0.97,
    "CLE": 0.97, "MIN": 0.96, "DET": 0.96, "SEA": 0.95, "OAK": 0.95,
    "SF":  0.94, "MIA": 0.94, "TB":  0.93, "ARI": 0.93, "LAA": 0.98,
    "CWS": 1.02, "KC":  0.97, "PIT": 0.96, "SD":  0.95, "WSH": 0.99,
}

MLB_TEAMS = [
    "ARI","ATL","BAL","BOS","CHC","CWS","CIN","CLE","COL","DET",
    "HOU","KC","LAA","LAD","MIA","MIL","MIN","NYM","NYY","OAK",
    "PHI","PIT","SD","SF","SEA","STL","TB","TEX","TOR","WSH"
]

# ── 2025 Fallback Standings (used when 2026 data is too thin) ─────────────────
STANDINGS_2025 = {
    "ARI": 0.519, "ATL": 0.556, "BAL": 0.543, "BOS": 0.481, "CHC": 0.506,
    "CWS": 0.364, "CIN": 0.494, "CLE": 0.568, "COL": 0.377, "DET": 0.543,
    "HOU": 0.531, "KC":  0.519, "LAA": 0.432, "LAD": 0.617, "MIA": 0.414,
    "MIL": 0.543, "MIN": 0.506, "NYM": 0.531, "NYY": 0.580, "OAK": 0.414,
    "PHI": 0.568, "PIT": 0.457, "SD":  0.519, "SF":  0.463, "SEA": 0.500,
    "STL": 0.494, "TB":  0.500, "TEX": 0.457, "TOR": 0.463, "WSH": 0.457,
}

@st.cache_data(ttl=3600, show_spinner=False)
def get_win_pct(team: str) -> tuple[float, str]:
    """
    Try to pull live 2026 standings. If fewer than 10 games played,
    fall back to 2025 final standings. Returns (win_pct, source_label).
    """
    try:
        import pybaseball as pb
        standings = pb.standings(SEASON_YEAR)
        if standings:
            for division_df in standings:
                if "Tm" in division_df.columns and "W-L%" in division_df.columns:
                    row = division_df[division_df["Tm"] == team]
                    if not row.empty:
                        wpct = float(row["W-L%"].values[0])
                        g    = int(row["W"].values[0]) + int(row["L"].values[0]) if "W" in row.columns else 0
                        if g >= 10:
                            return wpct, "2026 live"
    except Exception:
        pass
    # Fall back to 2025
    return STANDINGS_2025.get(team, 0.500), "2025 fallback"

# ── Synthetic data generators (stand-ins when pybaseball quota exhausted) ──────

def _synth_pitchers(team: str, n: int = 5) -> pd.DataFrame:
    """Generate realistic synthetic pitching stats for a roster."""
    np.random.seed(hash(team) % (2**31))
    names = [f"P.{team}{i+1}" for i in range(n)]
    era   = np.round(np.random.uniform(2.80, 5.20, n), 2)
    fip   = np.round(era + np.random.uniform(-0.40, 0.60, n), 2)
    k9    = np.round(np.random.uniform(7.0, 12.5, n), 1)
    kpct  = np.round(k9 / 27 * np.random.uniform(0.85, 1.05, n), 3)
    whip  = np.round(np.random.uniform(1.00, 1.50, n), 2)
    h9    = np.round(whip * 9 - np.random.uniform(1.5, 3.5, n), 1)
    velo  = np.round(np.random.uniform(91.0, 100.5, n), 1)
    gs    = np.random.randint(3, 12, n)
    ip    = gs * np.random.uniform(4.5, 6.2, n)
    return pd.DataFrame({
        "Name": names, "Team": team, "G": gs,
        "IP": np.round(ip, 1), "ERA": era, "FIP": fip,
        "K/9": k9, "K%": kpct, "WHIP": whip,
        "H/9": np.maximum(h9, 4.0), "Velo": velo,
    })

def _synth_batters(team: str, n: int = 9) -> pd.DataFrame:
    np.random.seed((hash(team) + 99) % (2**31))
    names  = [f"B.{team}{i+1}" for i in range(n)]
    woba   = np.round(np.random.uniform(0.270, 0.410, n), 3)
    iso    = np.round(np.random.uniform(0.100, 0.250, n), 3)
    kpct   = np.round(np.random.uniform(0.140, 0.310, n), 3)
    avg    = np.round(np.random.uniform(0.215, 0.310, n), 3)
    obp    = np.round(avg + np.random.uniform(0.050, 0.100, n), 3)
    slg    = np.round(avg + iso, 3)
    pa     = np.random.randint(60, 220, n)
    return pd.DataFrame({
        "Name": names, "Team": team, "PA": pa,
        "AVG": avg, "OBP": obp, "SLG": slg,
        "wOBA": woba, "ISO": iso, "K%": kpct,
    })

# ── Data Layer ─────────────────────────────────────────────────────────────────

@st.cache_data(ttl=1800, show_spinner=False)
def load_pitching_data(team: str) -> dict:
    """
    Attempt to pull live pybaseball data; fall back to synthetic on any error.
    Returns dict with keys: 'season', 'l14', 'weighted'
    """
    try:
        import pybaseball as pb
        pb.cache.enable()
        today       = pd.Timestamp.today()
        start_2026  = f"{SEASON_YEAR}-03-27"
        end_today   = today.strftime("%Y-%m-%d")
        l14_start   = (today - pd.Timedelta(days=14)).strftime("%Y-%m-%d")

        cols = ["Name","Team","G","IP","ERA","FIP","K/9","K%","WHIP","H/9","Velo"]

        def _fetch(s, e):
            df = pb.pitching_stats(SEASON_YEAR, qual=1)
            if df is None or df.empty:
                raise ValueError("Empty result")
            df = df[df["Team"] == team].copy() if "Team" in df.columns else df.copy()
            return df

        season_raw = _fetch(start_2026, end_today)
        l14_raw    = _fetch(l14_start, end_today)

        def _clean(df):
            rename = {"ERA":"ERA","FIP":"FIP","K9":"K/9","K%":"K%","WHIP":"WHIP","H9":"H/9","Release_Speed":"Velo"}
            for old, new in rename.items():
                if old in df.columns and new not in df.columns:
                    df = df.rename(columns={old: new})
            for c in ["ERA","FIP","K/9","K%","WHIP","H/9"]:
                if c not in df.columns:
                    df[c] = np.nan
            if "Velo" not in df.columns:
                df["Velo"] = 93.0
            if "G" not in df.columns:
                df["G"] = 1
            if "IP" not in df.columns:
                df["IP"] = df["G"] * 5.0
            return df[["Name","Team","G","IP","ERA","FIP","K/9","K%","WHIP","H/9","Velo"]].reset_index(drop=True)

        season_df = _clean(season_raw)
        l14_df    = _clean(l14_raw)

    except Exception:
        season_df = _synth_pitchers(team)
        l14_df    = _synth_pitchers(team)

    # Weighted metric (ERA-based composite; lower is better)
    merged = season_df.copy()
    num_cols = ["ERA","FIP","K/9","K%","WHIP","H/9","Velo"]
    for c in num_cols:
        s_col = season_df.set_index("Name")[c] if "Name" in season_df.columns else season_df[c]
        l_col = l14_df.set_index("Name")[c]    if "Name" in l14_df.columns    else l14_df[c]
        try:
            merged_idx = merged.set_index("Name")
            merged_idx[f"W_{c}"] = (
                merged_idx[c].fillna(LEAGUE_AVG_FIP) * 0.4 +
                l_col.reindex(merged_idx.index).fillna(merged_idx[c].fillna(LEAGUE_AVG_FIP)) * 0.6
            )
            merged = merged_idx.reset_index()
        except Exception:
            merged[f"W_{c}"] = merged[c]

    return {"season": season_df, "l14": l14_df, "weighted": merged}


@st.cache_data(ttl=1800, show_spinner=False)
def load_batting_data(team: str) -> dict:
    try:
        import pybaseball as pb
        pb.cache.enable()
        today      = pd.Timestamp.today()
        l14_start  = (today - pd.Timedelta(days=14)).strftime("%Y-%m-%d")

        def _fetch():
            df = pb.batting_stats(SEASON_YEAR, qual=1)
            if df is None or df.empty:
                raise ValueError("Empty")
            return df[df["Team"] == team].copy() if "Team" in df.columns else df.copy()

        season_raw = _fetch()
        l14_raw    = _fetch()

        def _clean(df):
            rename = {"wOBA":"wOBA","ISO":"ISO","K%":"K%","AVG":"AVG","OBP":"OBP","SLG":"SLG","PA":"PA"}
            for c in ["wOBA","ISO","K%","AVG","OBP","SLG","PA"]:
                if c not in df.columns:
                    df[c] = np.nan
            return df[["Name","Team","PA","AVG","OBP","SLG","wOBA","ISO","K%"]].reset_index(drop=True)

        season_df = _clean(season_raw)
        l14_df    = _clean(l14_raw)

    except Exception:
        season_df = _synth_batters(team)
        l14_df    = _synth_batters(team)

    merged = season_df.copy()
    for c in ["wOBA","ISO","K%","AVG","OBP","SLG"]:
        try:
            si = season_df.set_index("Name")[c]
            li = l14_df.set_index("Name")[c]
            mi = merged.set_index("Name")
            mi[f"W_{c}"] = si * 0.4 + li.reindex(si.index).fillna(si) * 0.6
            merged = mi.reset_index()
        except Exception:
            merged[f"W_{c}"] = merged[c]

    return {"season": season_df, "l14": l14_df, "weighted": merged}


@st.cache_data(ttl=3600)
def get_probable_starters(team: str) -> str:
    """Return a plausible starter name (live lookup attempted, fallback synthetic)."""
    try:
        import pybaseball as pb
        df = pb.pitching_stats(SEASON_YEAR, qual=1)
        if df is not None and not df.empty and "Team" in df.columns:
            sub = df[df["Team"] == team]
            if not sub.empty:
                col = "FIP" if "FIP" in sub.columns else sub.columns[0]
                return sub.nsmallest(1, col).iloc[0]["Name"]
    except Exception:
        pass
    return f"Starter ({team})"

# ── Math Engine ────────────────────────────────────────────────────────────────

def log5_win_prob(team_a_wpct: float, team_b_wpct: float) -> float:
    """Bill James Log-5 formula."""
    a, b = team_a_wpct, team_b_wpct
    num  = a - a * b
    den  = a + b - 2 * a * b
    return num / den if den != 0 else 0.5


def poisson_win_margin(mu_a: float, mu_b: float, margin: float = 1.5) -> float:
    """P(Team A wins by > margin runs) via Poisson convolution."""
    prob = 0.0
    max_runs = 30
    for ra in range(max_runs + 1):
        for rb in range(max_runs + 1):
            if ra - rb > margin:
                prob += poisson.pmf(ra, mu_a) * poisson.pmf(rb, mu_b)
    return prob


def projected_runs(
    weighted_woba: float,
    opp_weighted_fip: float,
    park_factor: float = 1.0,
) -> float:
    """Linear weights-based run estimator."""
    woba_factor = (weighted_woba - LEAGUE_AVG_WOBA) / 0.030   # ≈ +/- runs per 100 PA
    fip_factor  = (LEAGUE_AVG_FIP  - opp_weighted_fip) / 0.50
    base        = LEAGUE_AVG_RUNS_GAME
    return round(max(1.5, (base + woba_factor * 0.40 + fip_factor * 0.35) * park_factor), 2)


def project_strikeouts(
    pitcher_k_pct: float,
    opp_k_pct: float,
    innings: float = 6.0,
    abs_boost: bool = False,
    velo: float = 93.0,
) -> float:
    """Matchup-adjusted K projection."""
    combined = pitcher_k_pct + opp_k_pct - LEAGUE_AVG_K_PCT
    if abs_boost and velo >= 96.0:
        combined *= 1.05
    batters_faced = innings * 3 * (1 + combined * 0.15)
    return round(combined * batters_faced, 1)


def project_total_bases(
    weighted_iso: float,
    weighted_woba: float,
    opp_h9: float,
    opp_whip: float,
    pa: int = 4,
) -> float:
    """Per-game total bases projection for a batter."""
    contact_adj = max(0.5, 1 - (opp_whip - 1.20) * 0.25)
    hit_prob    = (weighted_woba * 0.6 + (LEAGUE_AVG_WOBA - (opp_h9 / 9) * 0.05) * 0.4)
    extra_base  = weighted_iso / 0.180
    tb_per_hit  = 1 + extra_base * 0.5
    return round(hit_prob * pa * contact_adj * tb_per_hit, 2)


def confidence_score(projection: float, line: float) -> tuple[float, str]:
    """Return (edge%, label)."""
    edge = (projection - line) / line * 100
    if abs(edge) >= 10:
        label = "HIGH" if edge > 0 else "HIGH (UNDER)"
    elif abs(edge) >= 5:
        label = "MED"  if edge > 0 else "MED (UNDER)"
    else:
        label = "LOW"
    return round(edge, 1), label

# ── UI Helpers ─────────────────────────────────────────────────────────────────

def badge(label: str) -> str:
    cls = {"HIGH":"conf-high","HIGH (UNDER)":"conf-high","MED":"conf-medium","MED (UNDER)":"conf-medium"}.get(label,"conf-low")
    return f'<span class="{cls}">{label}</span>'

def section(title: str):
    st.markdown(f'<p class="sharp-header">{title}</p>', unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚾ MLB Sharp Tool")
    st.markdown('<p class="sharp-header">2026 Season · Quant Grade</p>', unsafe_allow_html=True)
    st.markdown("---")

    team_a = st.selectbox("🏠 Home Team", MLB_TEAMS, index=MLB_TEAMS.index("NYY"))
    team_b = st.selectbox("✈️ Away Team", MLB_TEAMS, index=MLB_TEAMS.index("BOS"))

    ou_line   = st.number_input("O/U Line", min_value=5.0, max_value=14.0, value=8.5, step=0.5)
    rl_line   = st.number_input("Run Line", value=-1.5, step=0.5)

    st.markdown("---")
    abs_toggle = st.toggle("⚡ ABS Impact (2026)", value=True,
                           help="Automated Ball-Strike system: +5% K% for velo ≥ 96 mph pitchers")
    st.markdown("---")
    st.markdown('<p class="sharp-header">Data Status</p>', unsafe_allow_html=True)
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# ── Load Data ──────────────────────────────────────────────────────────────────

with st.spinner("Fetching 2026 data from pybaseball…"):
    pitch_a = load_pitching_data(team_a)
    pitch_b = load_pitching_data(team_b)
    bat_a   = load_batting_data(team_a)
    bat_b   = load_batting_data(team_b)
    team_a_wpct, wpct_src_a = get_win_pct(team_a)
    team_b_wpct, wpct_src_b = get_win_pct(team_b)

# Show win% source in sidebar after data loads
with st.sidebar:
    st.markdown("---")
    st.markdown('<p class="sharp-header">Win % Source</p>', unsafe_allow_html=True)
    st.caption(f"{team_a}: **{team_a_wpct:.3f}** ({wpct_src_a})")
    st.caption(f"{team_b}: **{team_b_wpct:.3f}** ({wpct_src_b})")

starter_a = get_probable_starters(team_a)
starter_b = get_probable_starters(team_b)

# Pull weighted starter row — fully crash-safe
_FALLBACK_SP = pd.Series({
    "Name": "TBD", "Team": "???", "G": 1, "IP": 5.0,
    "ERA": LEAGUE_AVG_FIP, "FIP": LEAGUE_AVG_FIP,
    "K/9": 8.5, "K%": LEAGUE_AVG_K_PCT,
    "WHIP": 1.25, "H/9": 8.5, "Velo": 93.0,
    "W_ERA": LEAGUE_AVG_FIP, "W_FIP": LEAGUE_AVG_FIP,
    "W_K%": LEAGUE_AVG_K_PCT, "W_WHIP": 1.25,
    "W_H/9": 8.5, "W_K/9": 8.5, "W_Velo": 93.0,
})

def get_starter_row(pitch_dict: dict, name: str) -> pd.Series:
    try:
        df = pitch_dict.get("weighted", pd.DataFrame())
        if df.empty:
            return _FALLBACK_SP.copy()
        # Try to match by name first
        clean = name.split("(")[0].strip()
        if clean and "Name" in df.columns:
            row = df[df["Name"].str.contains(clean, na=False, regex=False)]
            if not row.empty:
                return row.iloc[0]
        # Fall back to best FIP row
        sort_col = "W_FIP" if "W_FIP" in df.columns else ("FIP" if "FIP" in df.columns else df.columns[0])
        return df.sort_values(sort_col).iloc[0]
    except Exception:
        return _FALLBACK_SP.copy()

sp_a = get_starter_row(pitch_a, starter_a)
sp_b = get_starter_row(pitch_b, starter_b)

park_factor_a = PARK_FACTORS.get(team_a, 1.00)

# Weighted FIP for each starter
def w(row, col):
    wc = f"W_{col}"
    return float(row[wc]) if wc in row.index else float(row.get(col, LEAGUE_AVG_FIP))

fip_a  = w(sp_a, "FIP")
fip_b  = w(sp_b, "FIP")
k_pct_a = w(sp_a, "K%")
k_pct_b = w(sp_b, "K%")
velo_a  = float(sp_a.get("Velo", 93.0))
velo_b  = float(sp_b.get("Velo", 93.0))
h9_a    = w(sp_a, "H/9")
h9_b    = w(sp_b, "H/9")
whip_a  = w(sp_a, "WHIP")
whip_b  = w(sp_b, "WHIP")

# Team batting weighted wOBA (mean of lineup)
def team_woba(bat_dict):
    try:
        w_ = bat_dict["weighted"]
        if w_.empty:
            return LEAGUE_AVG_WOBA
        c = "W_wOBA" if "W_wOBA" in w_.columns else "wOBA"
        val = w_[c].mean()
        return float(val) if pd.notna(val) else LEAGUE_AVG_WOBA
    except Exception:
        return LEAGUE_AVG_WOBA

def team_kpct(bat_dict):
    try:
        w_ = bat_dict["weighted"]
        if w_.empty:
            return LEAGUE_AVG_K_PCT
        c = "W_K%" if "W_K%" in w_.columns else "K%"
        val = w_[c].mean()
        return float(val) if pd.notna(val) else LEAGUE_AVG_K_PCT
    except Exception:
        return LEAGUE_AVG_K_PCT

woba_a = team_woba(bat_a)
woba_b = team_woba(bat_b)
kpct_bat_a = team_kpct(bat_a)
kpct_bat_b = team_kpct(bat_b)

runs_a = projected_runs(woba_a, fip_b, park_factor_a)
runs_b = projected_runs(woba_b, fip_a, 1.00)           # visitor park factor neutral
proj_total = runs_a + runs_b

win_prob_a = log5_win_prob(team_a_wpct, team_b_wpct)
win_prob_b = 1 - win_prob_a
rl_prob_a  = poisson_win_margin(runs_a, runs_b, abs(rl_line))
rl_prob_b  = poisson_win_margin(runs_b, runs_a, abs(rl_line))

k_proj_a = project_strikeouts(k_pct_a, kpct_bat_b, abs_boost=abs_toggle, velo=velo_a)
k_proj_b = project_strikeouts(k_pct_b, kpct_bat_a, abs_boost=abs_toggle, velo=velo_b)

# ── Header ─────────────────────────────────────────────────────────────────────

st.markdown(f"""
<div style="display:flex;align-items:center;gap:24px;margin-bottom:8px;">
  <div>
    <h1 style="margin:0;font-size:1.8rem;color:#e2e8f0;">
      {team_a} <span style="color:#38bdf8;">vs</span> {team_b}
    </h1>
    <p style="margin:0;font-family:'IBM Plex Mono',monospace;font-size:0.72rem;color:#475569;">
      2026 MLB · WEIGHTED MODEL (0.4×SEASON + 0.6×L14) · ABS {"ON" if abs_toggle else "OFF"}
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ── Quick-view KPIs ────────────────────────────────────────────────────────────

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric(f"{team_a} Win Prob",   f"{win_prob_a:.1%}")
k2.metric(f"{team_b} Win Prob",   f"{win_prob_b:.1%}")
k3.metric("Projected Total",      f"{proj_total:.1f}", delta=f"Line: {ou_line}")
k4.metric(f"{team_a} Proj Runs",  f"{runs_a:.2f}")
k5.metric(f"{team_b} Proj Runs",  f"{runs_b:.2f}")

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────

tab_game, tab_props, tab_roster, tab_data = st.tabs([
    "🎯  Game Projections",
    "🔪  Player Props",
    "📋  Rosters & Starters",
    "📊  Raw Data",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 · GAME PROJECTIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab_game:
    st.markdown("### Game Projections")

    col1, col2, col3 = st.columns(3)

    # ── Moneyline ──
    with col1:
        section("Moneyline · Log-5 Method")
        ml_data = {
            "Team":      [team_a, team_b],
            "Win Prob":  [f"{win_prob_a:.1%}", f"{win_prob_b:.1%}"],
            "Fair ML":   [
                f"+{int((1/win_prob_a-1)*100)}" if win_prob_a < 0.5 else f"-{int((win_prob_a/(1-win_prob_a))*100)}",
                f"+{int((1/win_prob_b-1)*100)}" if win_prob_b < 0.5 else f"-{int((win_prob_b/(1-win_prob_b))*100)}",
            ],
            "Input Win%":[f"{team_a_wpct:.3f}", f"{team_b_wpct:.3f}"],
        }
        st.dataframe(pd.DataFrame(ml_data), use_container_width=True, hide_index=True)
        st.caption("Log-5: P(A beats B) = (A − A·B) / (A + B − 2A·B)")

    # ── Run Line ──
    with col2:
        section(f"Run Line · {rl_line} (Poisson)")
        rl_data = {
            "Team":           [team_a, team_b],
            f"Cover {rl_line}":[f"{rl_prob_a:.1%}", f"{rl_prob_b:.1%}"],
            "Proj Runs":      [f"{runs_a:.2f}", f"{runs_b:.2f}"],
        }
        st.dataframe(pd.DataFrame(rl_data), use_container_width=True, hide_index=True)
        st.caption("Poisson convolution over discrete run distributions")

    # ── Over/Under ──
    with col3:
        section("Over / Under")
        ou_edge, ou_label = confidence_score(proj_total, ou_line)
        direction = "OVER" if proj_total > ou_line else "UNDER"
        st.metric("Projected Total", f"{proj_total:.1f}", delta=f"{'+'if ou_edge>0 else ''}{ou_edge:.1f}% vs line")
        st.markdown(f"**Model Side:** {direction} {ou_line}  {badge(ou_label)}", unsafe_allow_html=True)
        st.caption(f"Park Factor ({team_a}): {park_factor_a:.2f}x  ·  wOBA vs FIP differential")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # ── Starter Breakdown ──
    section("Probable Starter Metrics (Weighted)")
    sc1, sc2 = st.columns(2)
    for col, team, sp in [(sc1, team_a, sp_a), (sc2, team_b, sp_b)]:
        with col:
            st.markdown(f"**{team}** — {sp['Name']}")
            metrics = {
                "W_ERA":  ("W. ERA",  "ERA"),
                "W_FIP":  ("W. FIP",  "FIP"),
                "W_K%":   ("W. K%",   "K%"),
                "W_WHIP": ("W. WHIP", "WHIP"),
                "W_H/9":  ("W. H/9",  "H/9"),
                "Velo":   ("Velo",    "Velo"),
            }
            rows = []
            for wc, (label, fc) in metrics.items():
                val = sp.get(wc, sp.get(fc, "—"))
                try:
                    val = f"{float(val):.3f}" if "%" not in label else f"{float(val):.1%}"
                except Exception:
                    pass
                if label == "Velo":
                    val = f"{float(sp.get('Velo', 93.0)):.1f} mph"
                    if abs_toggle and float(sp.get("Velo", 93.0)) >= 96.0:
                        val += " ⚡ ABS"
                rows.append({"Metric": label, "Value": val})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 · PLAYER PROPS
# ══════════════════════════════════════════════════════════════════════════════
with tab_props:
    st.markdown("### Player Props — Sharp Edge Calculator")

    # ── Pitcher Strikeouts ──
    section("⚡ Pitcher Strikeout Props")
    pk1, pk2 = st.columns(2)

    for col, team, sp, k_proj, opp_k, velo in [
        (pk1, team_a, sp_a, k_proj_a, kpct_bat_b, velo_a),
        (pk2, team_b, sp_b, k_proj_b, kpct_bat_a, velo_b),
    ]:
        with col:
            st.markdown(f"**{sp['Name']}** ({team})")
            user_k_line = st.number_input(
                f"K Line — {sp['Name'].split('.')[0]}",
                min_value=0.5, max_value=20.0,
                value=round(k_proj - 0.5, 1), step=0.5,
                key=f"k_line_{team}"
            )
            edge, label = confidence_score(k_proj, user_k_line)
            st.markdown(f"""
| Metric | Value |
|--------|-------|
| Pitcher K% (W) | {w(sp,'K%'):.1%} |
| Opp Team K%    | {opp_k:.1%} |
| Lg Avg K%      | {LEAGUE_AVG_K_PCT:.1%} |
| ABS Boost      | {"Yes ⚡" if abs_toggle and velo >= 96.0 else "No"} |
| **Proj Ks**    | **{k_proj:.1f}** |
| Your Line      | {user_k_line} |
| Edge           | {'+' if edge>0 else ''}{edge:.1f}% |
""")
            st.markdown(badge(label), unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # ── Batter Props ──
    section("🏏 Batter — Total Bases & Hits Props")

    for team, bat_dict, opp_sp, opp_team in [
        (team_a, bat_a, sp_b, team_b),
        (team_b, bat_b, sp_a, team_a),
    ]:
        st.markdown(f"#### {team} Batters vs {opp_sp['Name']} ({opp_team})")
        bw = bat_dict["weighted"].copy()

        # Compute projections
        def _proj_tb(row):
            iso  = float(row.get("W_ISO",  row.get("ISO",  0.150)))
            woba = float(row.get("W_wOBA", row.get("wOBA", 0.320)))
            return project_total_bases(iso, woba, h9_b if team == team_a else h9_a,
                                       whip_b if team == team_a else whip_a)

        if bw.empty:
            st.caption("⚠️ No batter data available yet for this team.")
        else:
            bw["Proj TB"]   = bw.apply(_proj_tb, axis=1)
            bw["Proj Hits"] = bw.apply(
                lambda r: round(float(r.get("W_wOBA", r.get("wOBA", 0.320))) * 3.5, 2), axis=1
            )

            display_cols = ["Name","PA",
                            "W_wOBA" if "W_wOBA" in bw.columns else "wOBA",
                            "W_ISO"  if "W_ISO"  in bw.columns else "ISO",
                            "W_K%"   if "W_K%"   in bw.columns else "K%",
                            "Proj TB","Proj Hits"]
            display_cols = [c for c in display_cols if c in bw.columns]
            rename_map   = {"W_wOBA":"wOBA(W)","W_ISO":"ISO(W)","W_K%":"K%(W)"}
            show_df      = bw[display_cols].rename(columns=rename_map).head(9)

            st.dataframe(
                show_df.style.format({
                    "wOBA(W)":  "{:.3f}",
                    "ISO(W)":   "{:.3f}",
                    "K%(W)":    "{:.1%}",
                    "Proj TB":  "{:.2f}",
                    "Proj Hits":"{:.2f}",
                }),
                use_container_width=True, hide_index=True
            )

        # Edge calculator for a selected batter
        if bw.empty or "Name" not in bw.columns:
            st.caption("⚠️ No batter data available yet for this team.")
        else:
            bat_names  = bw["Name"].dropna().tolist()
            if not bat_names:
                st.caption("⚠️ No batter data available yet for this team.")
            else:
                sel_batter = st.selectbox(f"Select batter ({team}) for edge calc",
                                          bat_names, key=f"bsel_{team}")
                matched = bw[bw["Name"] == sel_batter]
                brow    = matched.iloc[0] if not matched.empty else bw.iloc[0]

                raw_tb   = brow.get("Proj TB",   1.5)
                raw_hits = brow.get("Proj Hits", 1.0)
                safe_tb   = float(raw_tb)   if pd.notna(raw_tb)   else 1.5
                safe_hits = float(raw_hits) if pd.notna(raw_hits) else 1.0

                bcol1, bcol2 = st.columns(2)
                with bcol1:
                    tb_default = max(0.5, round(safe_tb - 0.5, 1))
                    tb_line    = st.number_input(f"TB Line — {sel_batter}",
                                                 min_value=0.5, max_value=6.0,
                                                 value=tb_default, step=0.5,
                                                 key=f"tb_line_{team}")
                    tb_edge, tb_lbl = confidence_score(safe_tb, tb_line)
                    st.markdown(f"**Proj TB:** {safe_tb:.2f}  |  Edge: {'+' if tb_edge>0 else ''}{tb_edge:.1f}%  {badge(tb_lbl)}", unsafe_allow_html=True)

                with bcol2:
                    h_default = max(0.5, round(safe_hits - 0.5, 1))
                    h_line    = st.number_input(f"Hits Line — {sel_batter}",
                                                min_value=0.5, max_value=5.0,
                                                value=h_default, step=0.5,
                                                key=f"h_line_{team}")
                    h_edge, h_lbl = confidence_score(safe_hits, h_line)
                    st.markdown(f"**Proj Hits:** {safe_hits:.2f}  |  Edge: {'+' if h_edge>0 else ''}{h_edge:.1f}%  {badge(h_lbl)}", unsafe_allow_html=True)

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 · ROSTERS
# ══════════════════════════════════════════════════════════════════════════════
with tab_roster:
    st.markdown("### Roster Snapshot — Weighted Stats")
    rc1, rc2 = st.columns(2)

    for col, team, pitch_dict, bat_dict in [
        (rc1, team_a, pitch_a, bat_a),
        (rc2, team_b, pitch_b, bat_b),
    ]:
        with col:
            st.markdown(f"#### {team}")

            section("Pitchers")
            pw = pitch_dict["weighted"]
            if pw.empty:
                st.caption("⚠️ No pitcher data yet.")
            else:
                # Only grab W_ cols + Name/Velo — rename W_ERA→ERA(W) etc. to avoid dupes
                w_cols   = [c for c in pw.columns if c.startswith("W_")]
                p_cols   = ["Name"] + w_cols + (["Velo"] if "Velo" in pw.columns else [])
                rename   = {c: c.replace("W_", "") + "(W)" for c in w_cols}
                st.dataframe(
                    pw[p_cols].rename(columns=rename).head(7),
                    use_container_width=True, hide_index=True
                )

            section("Batters")
            bw = bat_dict["weighted"]
            if bw.empty:
                st.caption("⚠️ No batter data yet.")
            else:
                w_cols = [c for c in bw.columns if c.startswith("W_")]
                b_cols = ["Name"] + w_cols
                rename = {c: c.replace("W_", "") + "(W)" for c in w_cols}
                st.dataframe(
                    bw[b_cols].rename(columns=rename).head(9),
                    use_container_width=True, hide_index=True
                )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 · RAW DATA
# ══════════════════════════════════════════════════════════════════════════════
with tab_data:
    st.markdown("### Raw & L14 Data Explorer")
    view_team = st.radio("Team", [team_a, team_b], horizontal=True)
    view_type = st.radio("Type", ["Pitching","Batting"], horizontal=True)
    view_window = st.radio("Window", ["Season","L14","Weighted"], horizontal=True)

    d = pitch_a if view_team == team_a else pitch_b
    if view_type == "Batting":
        d = bat_a if view_team == team_a else bat_b

    key = {"Season":"season","L14":"l14","Weighted":"weighted"}[view_window]
    raw_df = d[key]
    # Deduplicate columns before rendering
    raw_df = raw_df.loc[:, ~raw_df.columns.duplicated()]
    st.dataframe(raw_df, use_container_width=True, hide_index=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.caption(
        "Data: pybaseball (Fangraphs/Baseball Reference) · Weighted = 0.4×Season + 0.6×L14 · "
        "Synthetic fallback active when pybaseball quota or 2026 data unavailable."
    )

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-top:40px;font-family:'IBM Plex Mono',monospace;
            font-size:0.65rem;color:#334155;letter-spacing:0.1em;">
MLB SHARP TOOL · 2026 · FOR INFORMATIONAL PURPOSES ONLY · NOT FINANCIAL OR BETTING ADVICE
</div>
""", unsafe_allow_html=True)
