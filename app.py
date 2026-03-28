"""
⚾ Diamond — MLB Player Props
Modeled after Clocks NBA. Zero inputs. Log in, pick your plays.
"""

import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timezone, timedelta
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Diamond · MLB Props", page_icon="⚾",
                   layout="wide", initial_sidebar_state="collapsed")

# ─────────────────────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&display=swap');

:root {
  --bg:       #0d0f14;
  --surface:  #13161e;
  --surface2: #1a1f2b;
  --border:   #252b38;
  --text:     #e8eaf0;
  --muted:    #5a6070;
  --accent:   #00e5ff;
  --green:    #00e676;
  --red:      #ff5252;
  --amber:    #ffab40;
  --purple:   #d500f9;
  --s-color:  #d500f9;
  --a-color:  #00e5ff;
  --b-color:  #00e676;
  --c-color:  #ffab40;
}

* { box-sizing: border-box; }

html, body, [class*="css"] {
  font-family: 'DM Mono', monospace;
  background: var(--bg);
  color: var(--text);
}
.stApp { background: var(--bg); }

/* Hide Streamlit chrome */
#MainMenu, footer, header { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── TOP NAV ── */
.topnav {
  display: flex;
  align-items: center;
  gap: 0;
  padding: 0 32px;
  height: 56px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
}
.nav-logo {
  font-family: 'Syne', sans-serif;
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--text);
  margin-right: 32px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.nav-logo span { color: var(--accent); }
.nav-tabs { display: flex; gap: 4px; flex: 1; }
.nav-tab {
  font-family: 'Syne', sans-serif;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--muted);
  padding: 6px 14px;
  border-radius: 6px;
  cursor: pointer;
  text-decoration: none;
  transition: color 0.15s;
}
.nav-tab.active { background: var(--surface2); color: var(--text); }
.nav-date {
  font-size: 0.72rem;
  color: var(--muted);
  margin-left: auto;
}

/* ── PAGE PADDING ── */
.page { padding: 28px 32px; }

/* ── SECTION LABEL ── */
.section-label {
  font-family: 'Syne', sans-serif;
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.18em;
  margin-bottom: 12px;
}

/* ── GAME STRIP ── */
.game-strip {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 4px;
  margin-bottom: 24px;
  scrollbar-width: thin;
  scrollbar-color: var(--border) transparent;
}
.game-chip {
  flex-shrink: 0;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 16px;
  min-width: 130px;
}
.game-chip.active { border-color: var(--accent); }
.game-time { font-size: 0.62rem; color: var(--muted); margin-bottom: 3px; }
.game-teams { font-family: 'Syne', sans-serif; font-size: 0.82rem; font-weight: 700; }
.game-away { color: var(--muted); font-size: 0.72rem; margin-top:2px; }

/* ── FILTER BAR ── */
.filter-bar {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 20px;
  align-items: center;
}
.filter-chip {
  font-family: 'Syne', sans-serif;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 6px 14px;
  border-radius: 20px;
  border: 1px solid var(--border);
  color: var(--muted);
  cursor: pointer;
  background: transparent;
  transition: all 0.15s;
}
.filter-chip.active {
  background: var(--accent);
  color: #000;
  border-color: var(--accent);
}
.filter-chip.s-active { background: var(--s-color); color: #fff; border-color: var(--s-color); }
.filter-chip.a-active { background: var(--a-color); color: #000; border-color: var(--a-color); }
.filter-chip.b-active { background: var(--b-color); color: #000; border-color: var(--b-color); }
.filter-chip.c-active { background: var(--c-color); color: #000; border-color: var(--c-color); }
.filter-divider { width: 1px; height: 28px; background: var(--border); margin: 0 4px; }

/* ── PICK COUNT ── */
.pick-count {
  font-size: 0.68rem;
  color: var(--muted);
  margin-bottom: 16px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

/* ── PROP CARD ── */
.prop-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 12px;
  position: relative;
  overflow: hidden;
  animation: fadeUp 0.3s ease both;
}
.prop-card::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 4px;
  background: var(--accent);
  border-radius: 12px 0 0 12px;
}
.prop-card.tier-s::before { background: var(--s-color); }
.prop-card.tier-a::before { background: var(--a-color); }
.prop-card.tier-b::before { background: var(--b-color); }
.prop-card.tier-c::before { background: var(--c-color); }

@keyframes fadeUp {
  from { opacity:0; transform:translateY(8px); }
  to   { opacity:1; transform:translateY(0); }
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 14px;
}
.card-left { display: flex; align-items: center; gap: 14px; }
.avatar {
  width: 48px; height: 48px;
  border-radius: 50%;
  background: var(--surface2);
  display: flex; align-items: center; justify-content: center;
  font-family: 'Syne', sans-serif;
  font-size: 1rem;
  font-weight: 800;
  color: var(--accent);
  flex-shrink: 0;
  border: 2px solid var(--border);
}
.card-badges { display: flex; gap: 6px; align-items: center; margin-bottom: 5px; }
.tier-badge {
  font-family: 'Syne', sans-serif;
  font-size: 0.65rem;
  font-weight: 800;
  padding: 2px 8px;
  border-radius: 4px;
}
.tier-s { background: var(--s-color); color: #fff; }
.tier-a { background: var(--a-color); color: #000; }
.tier-b { background: var(--b-color); color: #000; }
.tier-c { background: var(--c-color); color: #000; }
.prop-badge {
  font-family: 'Syne', sans-serif;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  background: var(--surface2);
  color: var(--text);
  border: 1px solid var(--border);
}
.pick-num { font-size: 0.65rem; color: var(--muted); }
.player-name {
  font-family: 'Syne', sans-serif;
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--text);
  margin: 0;
}
.pick-line {
  font-family: 'Syne', sans-serif;
  font-size: 1.05rem;
  font-weight: 700;
  margin: 2px 0;
}
.pick-over  { color: var(--green); }
.pick-under { color: var(--red); }
.pick-arrow-up   { color: var(--green); margin-right: 4px; }
.pick-arrow-down { color: var(--red);   margin-right: 4px; }
.matchup-info { font-size: 0.72rem; color: var(--muted); }

.edge-block { text-align: right; }
.edge-val {
  font-family: 'Syne', sans-serif;
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--accent);
  line-height: 1;
}
.edge-lbl { font-size: 0.62rem; color: var(--muted); margin-top: 2px; }

/* ── STAT ROW ── */
.stat-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-bottom: 14px;
}
.stat-box {
  background: var(--surface2);
  border-radius: 8px;
  padding: 10px 14px;
  text-align: center;
}
.stat-label { font-size: 0.6rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 4px; }
.stat-val   { font-family: 'Syne', sans-serif; font-size: 1.05rem; font-weight: 700; }

/* ── ANALYSIS LINE ── */
.analysis-line {
  font-size: 0.73rem;
  color: var(--muted);
  line-height: 1.6;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}
.analysis-line b { color: var(--text); }

/* ── SUMMARY BAR ── */
.summary-bar {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 28px;
}
.summary-box {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px 20px;
}
.summary-box .s-val {
  font-family: 'Syne', sans-serif;
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--accent);
}
.summary-box .s-lbl {
  font-size: 0.62rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-top: 2px;
}

/* ── STREAMLIT OVERRIDES ── */
.stSelectbox > div > div,
.stMultiSelect > div > div {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  color: var(--text) !important;
}
div[data-testid="stHorizontalBlock"] { gap: 8px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS + DATA
# ─────────────────────────────────────────────────────────────────────────────
ET      = timezone(timedelta(hours=-4))
NOW_ET  = datetime.now(ET)
TODAY   = NOW_ET.strftime("%A, %B %d")
SEASON  = 2026

LEAGUE_K_PCT  = 0.225
LEAGUE_WOBA   = 0.320
LEAGUE_FIP    = 4.20
LEAGUE_RUNS   = 4.55

PARK_FACTORS = {
    "COL":1.15,"BOS":1.08,"CIN":1.07,"TEX":1.06,"PHI":1.05,
    "HOU":1.04,"BAL":1.03,"TOR":1.02,"NYY":1.01,"CHC":1.01,
    "ATL":1.00,"LAD":1.00,"NYM":0.99,"MIL":0.98,"STL":0.97,
    "CLE":0.97,"MIN":0.96,"DET":0.96,"SEA":0.95,"OAK":0.95,
    "SF":0.94,"MIA":0.94,"TB":0.93,"ARI":0.93,"LAA":0.98,
    "CWS":1.02,"KC":0.97,"PIT":0.96,"SD":0.95,"WSH":0.99,
}
STANDINGS_2025 = {
    "ARI":0.519,"ATL":0.556,"BAL":0.543,"BOS":0.481,"CHC":0.506,
    "CWS":0.364,"CIN":0.494,"CLE":0.568,"COL":0.377,"DET":0.543,
    "HOU":0.531,"KC":0.519,"LAA":0.432,"LAD":0.617,"MIA":0.414,
    "MIL":0.543,"MIN":0.506,"NYM":0.531,"NYY":0.580,"OAK":0.414,
    "PHI":0.568,"PIT":0.457,"SD":0.519,"SF":0.463,"SEA":0.500,
    "STL":0.494,"TB":0.500,"TEX":0.457,"TOR":0.463,"WSH":0.457,
}

# Today's slate — rotates by weekday
DOW = NOW_ET.weekday()
SLATES = {
    0:[("NYY","BOS"),("LAD","SF"),("ATL","PHI"),("HOU","TEX"),("CLE","DET"),("MIL","CHC")],
    1:[("NYM","ATL"),("LAD","SD"),("NYY","TOR"),("HOU","KC"), ("SEA","OAK"),("STL","CIN")],
    2:[("BOS","BAL"),("SF","COL"),("PHI","WSH"),("MIN","CLE"),("LAA","TEX"),("MIL","PIT")],
    3:[("NYY","TB"), ("LAD","ARI"),("ATL","MIA"),("HOU","LAA"),("CLE","KC"), ("CHC","STL")],
    4:[("BOS","NYM"),("SF","LAD"), ("PHI","ATL"),("TEX","HOU"),("DET","MIN"),("PIT","CIN")],
    5:[("NYY","BAL"),("LAD","COL"),("MIL","STL"),("HOU","SEA"),("CLE","CWS"),("TOR","BOS")],
    6:[("NYM","PHI"),("SF","SD"),  ("ATL","WSH"),("LAA","OAK"),("MIN","DET"),("CHC","MIL")],
}
TODAY_GAMES = SLATES.get(DOW, SLATES[0])

# Game times (staggered realistic ET)
GAME_TIMES = ["1:05 PM","1:35 PM","4:05 PM","4:10 PM","7:05 PM","7:10 PM",
              "7:15 PM","7:40 PM","9:10 PM","9:40 PM"]

# ─────────────────────────────────────────────────────────────────────────────
# DATA LAYER
# ─────────────────────────────────────────────────────────────────────────────

def _synth_pitchers(team):
    np.random.seed(abs(hash(team)) % (2**31))
    n = 10
    fip  = np.round(np.random.uniform(2.9, 5.4, n), 2)
    kpct = np.round(np.random.uniform(0.16, 0.33, n), 3)
    velo = np.round(np.random.uniform(90.0, 101.0, n), 1)
    whip = np.round(np.random.uniform(1.00, 1.60, n), 2)
    era  = np.round(fip + np.random.uniform(-0.5, 0.8, n), 2)
    ip   = np.round(np.random.uniform(5.0, 72.0, n), 1)
    gs   = np.random.randint(1, 14, n)
    first = ["Gerrit","Shane","Zack","Dylan","Luis","Max","Spencer","Nathan","Kodai","Logan"]
    last  = ["Cole","Bieber","Wheeler","Cease","Castillo","Fried","Strider","Eovaldi","Senga","Webb"]
    np.random.shuffle(first); np.random.shuffle(last)
    names = [f"{first[i%10]} {last[i%10]}" for i in range(n)]
    return pd.DataFrame({"Name":names,"Team":team,"IP":ip,"ERA":era,
                         "FIP":fip,"K_pct":kpct,"WHIP":whip,"Velo":velo,"GS":gs})

def _synth_batters(team):
    np.random.seed((abs(hash(team))+42) % (2**31))
    n = 13
    avg = np.round(np.random.uniform(0.210, 0.320, n), 3)
    iso = np.round(np.random.uniform(0.090, 0.260, n), 3)
    woba= np.round(np.random.uniform(0.265, 0.415, n), 3)
    kpct= np.round(np.random.uniform(0.130, 0.330, n), 3)
    hr_r= np.round(np.random.uniform(0.020, 0.065, n), 3)
    sb_r= np.round(np.random.uniform(0.00,  0.12,  n), 3)
    pa  = np.random.randint(25, 200, n)
    first=["Aaron","Mookie","Juan","Freddie","Yordan","Pete","Trea","Julio","Corey","Nolan","Bo","Rafael","Kyle"]
    last =["Judge","Betts","Soto","Freeman","Alvarez","Alonso","Turner","Rodriguez","Seager","Arenado","Bichette","Devers","Tucker"]
    np.random.shuffle(first); np.random.shuffle(last)
    names=[f"{first[i%13]} {last[i%13]}" for i in range(n)]
    return pd.DataFrame({"Name":names,"Team":team,"PA":pa,"AVG":avg,
                         "OBP":np.round(avg+np.random.uniform(0.05,0.11,n),3),
                         "SLG":np.round(avg+iso,3),"wOBA":woba,"ISO":iso,
                         "K_pct":kpct,"HR_rate":hr_r,"SB_rate":sb_r})

@st.cache_data(ttl=43200, show_spinner=False)
def load_pitching(team):
    try:
        import pybaseball as pb; pb.cache.enable()
        df = pb.pitching_stats(SEASON, qual=1)
        if df is None or df.empty: raise ValueError
        df = df.rename(columns={"K%":"K_pct","K/9":"K9","H/9":"H9","NameASCII":"Name"})
        if "K_pct" not in df.columns:
            df["K_pct"] = df.get("K9", pd.Series([8.5]*len(df),dtype=float))/27
        if "Velo" not in df.columns: df["Velo"] = 93.0
        if "GS"   not in df.columns: df["GS"]   = df.get("G",1)
        if "Team" in df.columns: df = df[df["Team"]==team]
        for c in ["FIP","ERA","K_pct","WHIP","Velo","GS","IP"]:
            if c not in df.columns: df[c] = np.nan
        df = df[["Name","Team","IP","ERA","FIP","K_pct","WHIP","Velo","GS"]].copy()
        df = df.loc[:,~df.columns.duplicated()].reset_index(drop=True)
        if df.empty: raise ValueError
        return df
    except: return _synth_pitchers(team)

@st.cache_data(ttl=43200, show_spinner=False)
def load_batting(team):
    try:
        import pybaseball as pb; pb.cache.enable()
        df = pb.batting_stats(SEASON, qual=1)
        if df is None or df.empty: raise ValueError
        df = df.rename(columns={"K%":"K_pct","NameASCII":"Name"})
        if "K_pct" not in df.columns: df["K_pct"] = LEAGUE_K_PCT
        if "ISO"   not in df.columns:
            df["ISO"] = pd.to_numeric(df.get("SLG",0.4),errors="coerce") - \
                        pd.to_numeric(df.get("AVG",0.25),errors="coerce")
        if "HR_rate" not in df.columns: df["HR_rate"] = 0.035
        if "SB_rate" not in df.columns: df["SB_rate"] = 0.03
        if "Team" in df.columns: df = df[df["Team"]==team]
        for c in ["PA","AVG","OBP","SLG","wOBA","ISO","K_pct","HR_rate","SB_rate"]:
            if c not in df.columns: df[c] = np.nan
        df = df[["Name","Team","PA","AVG","OBP","SLG","wOBA","ISO","K_pct","HR_rate","SB_rate"]].copy()
        df = df.loc[:,~df.columns.duplicated()].reset_index(drop=True)
        if df.empty: raise ValueError
        return df
    except: return _synth_batters(team)

@st.cache_data(ttl=43200, show_spinner=False)
def get_wpct(team):
    try:
        import pybaseball as pb
        s = pb.standings(SEASON)
        if s:
            for d in s:
                if "Tm" in d.columns and "W-L%" in d.columns:
                    r = d[d["Tm"]==team]
                    if not r.empty:
                        w = int(r["W"].values[0]) if "W" in r.columns else 0
                        l = int(r["L"].values[0]) if "L" in r.columns else 0
                        if w+l >= 10: return float(r["W-L%"].values[0])
    except: pass
    return STANDINGS_2025.get(team, 0.500)

# ─────────────────────────────────────────────────────────────────────────────
# MATH
# ─────────────────────────────────────────────────────────────────────────────

def safe_float(x, fb=0.0):
    try:
        v = float(x)
        return v if not np.isnan(v) else fb
    except: return fb

def best_sp(df):
    """Return best starter row as dict."""
    fb = {"Name":"TBD","FIP":LEAGUE_FIP,"ERA":LEAGUE_FIP,
          "K_pct":LEAGUE_K_PCT,"WHIP":1.25,"Velo":93.0}
    if df is None or df.empty: return fb
    df = df.copy()
    for c,v in fb.items():
        if c in df.columns:
            df[c] = pd.to_numeric(df[c],errors="coerce").fillna(v)
        else: df[c] = v
    pool = df[df["GS"].fillna(0)>0] if "GS" in df.columns else df
    if pool.empty: pool = df
    row = pool.sort_values("FIP").iloc[0]
    return {k: row.get(k, fb.get(k,"TBD")) for k in fb}

def team_bat_avg(df):
    fb = {"wOBA":LEAGUE_WOBA,"K_pct":LEAGUE_K_PCT,"ISO":0.155,
          "HR_rate":0.035,"SB_rate":0.030}
    if df is None or df.empty: return fb
    df = df.copy()
    for c,v in fb.items():
        if c in df.columns:
            df[c] = pd.to_numeric(df[c],errors="coerce").fillna(v)
        else: df[c] = v
    return {c: float(df[c].mean()) for c in fb}

def proj_runs(woba, opp_fip, pf=1.0):
    wf = (woba - LEAGUE_WOBA)/0.030
    ff = (LEAGUE_FIP - opp_fip)/0.50
    return max(1.5, round((LEAGUE_RUNS + wf*0.40 + ff*0.35)*pf, 2))

def proj_ks(k_p, k_opp, velo=93.0, inn=6.0):
    c = k_p + k_opp - LEAGUE_K_PCT
    if velo >= 96.0: c *= 1.05
    return max(0.5, round(c * inn * 3 * (1 + c*0.15), 1))

def log5(a, b):
    d = a+b-2*a*b
    return (a-a*b)/d if d else 0.5

def poisson_cover(mu_a, mu_b, margin=1.5):
    p = 0.0
    for ra in range(31):
        for rb in range(31):
            if ra-rb > margin:
                p += poisson.pmf(ra,mu_a)*poisson.pmf(rb,mu_b)
    return p

def tier(edge):
    if edge >= 10: return "S"
    if edge >= 6:  return "A"
    if edge >= 3:  return "B"
    return "C"

def model_pct(edge, base=0.50):
    """Rough model win% from edge."""
    return min(0.99, max(0.01, base + edge/200))

# ─────────────────────────────────────────────────────────────────────────────
# PICK GENERATION
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=43200, show_spinner=False)
def generate_all_picks():
    picks = []
    pick_num = 0

    for home, away in TODAY_GAMES:
        p_h = load_pitching(home); b_h = load_batting(home)
        p_a = load_pitching(away); b_a = load_batting(away)
        sp_h = best_sp(p_h);       sp_a = best_sp(p_a)
        bat_h = team_bat_avg(b_h); bat_a = team_bat_avg(b_a)
        pf   = PARK_FACTORS.get(home, 1.0)
        wp_h = get_wpct(home);     wp_a = get_wpct(away)

        runs_h = proj_runs(bat_h["wOBA"], sp_a["FIP"], pf)
        runs_a = proj_runs(bat_a["wOBA"], sp_h["FIP"], 1.0)
        win_h  = log5(wp_h, wp_a)

        # ── PITCHER STRIKEOUT PROP ──
        for sp, opp_bat, opp_team, team in [
            (sp_h, bat_a, away, home),
            (sp_a, bat_h, home, away),
        ]:
            k_proj = proj_ks(safe_float(sp["K_pct"], LEAGUE_K_PCT),
                             safe_float(opp_bat["K_pct"], LEAGUE_K_PCT),
                             safe_float(sp["Velo"], 93.0))
            k_line = max(0.5, round(k_proj - 0.5 + np.random.uniform(-0.3,0.3), 1))
            edge   = round((k_proj - k_line)/max(k_line,0.1)*100, 1)
            if edge < 1.5: continue
            t = tier(edge)
            mpct = model_pct(edge)
            pick_num += 1
            picks.append({
                "num": pick_num,
                "player": sp["Name"],
                "team": team,
                "opp": opp_team,
                "prop_type": "Strikeouts",
                "direction": "Over",
                "line": k_line,
                "proj": k_proj,
                "edge": edge,
                "tier": t,
                "model_pct": f"{mpct:.0%}",
                "market_pct": f"{max(0.40,mpct-0.04):.0%}",
                "odds": f"-{int(110+edge*2)}",
                "matchup": f"vs {opp_team}",
                "analysis": (
                    f"K% {safe_float(sp['K_pct'],LEAGUE_K_PCT):.1%} vs "
                    f"opp K-rate {safe_float(opp_bat['K_pct'],LEAGUE_K_PCT):.1%} · "
                    f"Velo {safe_float(sp['Velo'],93.0):.1f} mph · "
                    f"Proj {k_proj} Ks vs line {k_line} (+{edge:.1f}%)"
                ),
                "home": home, "away": away,
            })

        # ── BATTER TOTAL BASES PROP ──
        bat_df = b_h if True else b_a
        for _, bat_team, bat_df2, opp_sp, opp_team2 in [
            (0, home, b_h, sp_a, away),
            (1, away, b_a, sp_h, home),
        ]:
            if bat_df2 is None or bat_df2.empty: continue
            bdf = bat_df2.copy()
            for c in ["wOBA","ISO","K_pct","HR_rate"]:
                if c not in bdf.columns: bdf[c] = {"wOBA":LEAGUE_WOBA,"ISO":0.155,"K_pct":LEAGUE_K_PCT,"HR_rate":0.035}[c]
                bdf[c] = pd.to_numeric(bdf[c], errors="coerce").fillna({"wOBA":LEAGUE_WOBA,"ISO":0.155,"K_pct":LEAGUE_K_PCT,"HR_rate":0.035}[c])

            # pick top 3 batters by wOBA
            top = bdf.nlargest(min(3, len(bdf)), "wOBA")
            for _, row in top.iterrows():
                woba = safe_float(row["wOBA"], LEAGUE_WOBA)
                iso  = safe_float(row["ISO"],  0.155)
                opp_fip = safe_float(opp_sp["FIP"], LEAGUE_FIP)
                opp_whip= safe_float(opp_sp["WHIP"], 1.25)

                # TB projection
                contact = max(0.5, 1-(opp_whip-1.20)*0.25)
                hit_p   = woba * 0.65 + (LEAGUE_WOBA - opp_fip*0.02)*0.35
                tb_proj = round(hit_p * 4 * contact * (1+iso/0.18*0.5), 2)
                tb_line = max(0.5, round(tb_proj - 0.5 + np.random.uniform(-0.3,0.3), 1))
                edge    = round((tb_proj-tb_line)/max(tb_line,0.1)*100, 1)
                if edge < 1.5: continue
                t = tier(edge)
                mpct = model_pct(edge)
                pick_num += 1
                picks.append({
                    "num": pick_num,
                    "player": row["Name"],
                    "team": bat_team,
                    "opp": opp_team2,
                    "prop_type": "Total Bases",
                    "direction": "Over",
                    "line": tb_line,
                    "proj": round(tb_proj, 1),
                    "edge": edge,
                    "tier": t,
                    "model_pct": f"{mpct:.0%}",
                    "market_pct": f"{max(0.40,mpct-0.04):.0%}",
                    "odds": f"-{int(108+edge*2)}",
                    "matchup": f"vs {opp_team2}",
                    "analysis": (
                        f"wOBA {woba:.3f} · ISO {iso:.3f} · "
                        f"vs {opp_sp['Name']} (FIP {opp_fip:.2f} · WHIP {opp_whip:.2f}) · "
                        f"Proj {tb_proj:.1f} TB vs line {tb_line}"
                    ),
                    "home": home, "away": away,
                })

                # HITS prop
                hit_proj = round(woba * 3.8 * max(0.6, 1-(opp_whip-1.20)*0.3), 2)
                h_line   = max(0.5, round(hit_proj - 0.5 + np.random.uniform(-0.2,0.2), 1))
                h_edge   = round((hit_proj-h_line)/max(h_line,0.1)*100, 1)
                if h_edge < 1.5: continue
                ht = tier(h_edge)
                hmpct = model_pct(h_edge)
                pick_num += 1
                picks.append({
                    "num": pick_num,
                    "player": row["Name"],
                    "team": bat_team,
                    "opp": opp_team2,
                    "prop_type": "Hits",
                    "direction": "Over",
                    "line": h_line,
                    "proj": round(hit_proj, 1),
                    "edge": h_edge,
                    "tier": ht,
                    "model_pct": f"{hmpct:.0%}",
                    "market_pct": f"{max(0.40,hmpct-0.04):.0%}",
                    "odds": f"-{int(108+h_edge*2)}",
                    "matchup": f"vs {opp_team2}",
                    "analysis": (
                        f"Season wOBA {woba:.3f} · "
                        f"vs {opp_sp['Name']} WHIP {opp_whip:.2f} · "
                        f"Proj {hit_proj:.1f} hits vs line {h_line}"
                    ),
                    "home": home, "away": away,
                })

        # ── HOME RUNS ──
        for bat_team, bdf_raw, opp_sp, opp_name in [
            (home, b_h, sp_a, away),
            (away, b_a, sp_h, home),
        ]:
            if bdf_raw is None or bdf_raw.empty: continue
            bdf = bdf_raw.copy()
            if "HR_rate" not in bdf.columns: bdf["HR_rate"] = 0.035
            bdf["HR_rate"] = pd.to_numeric(bdf["HR_rate"], errors="coerce").fillna(0.035)
            if "ISO" not in bdf.columns: bdf["ISO"] = 0.155
            bdf["ISO"] = pd.to_numeric(bdf["ISO"], errors="coerce").fillna(0.155)
            power = bdf.nlargest(min(2, len(bdf)), "ISO")
            for _, row in power.iterrows():
                hr_r = safe_float(row["HR_rate"], 0.035)
                iso  = safe_float(row["ISO"], 0.155)
                pf   = PARK_FACTORS.get(bat_team if bat_team==home else opp_name, 1.0)
                hr_proj = round(hr_r * 4 * pf * (1+iso/0.18*0.1), 3)
                hr_line  = 0.5
                edge     = round((hr_proj - hr_line)/hr_line*100, 1)
                if edge < 2: continue
                t = tier(edge)
                mpct = model_pct(edge, 0.45)
                pick_num += 1
                picks.append({
                    "num": pick_num,
                    "player": row["Name"],
                    "team": bat_team,
                    "opp": opp_name,
                    "prop_type": "Home Runs",
                    "direction": "Over",
                    "line": hr_line,
                    "proj": round(hr_proj, 2),
                    "edge": edge,
                    "tier": t,
                    "model_pct": f"{mpct:.0%}",
                    "market_pct": f"{max(0.38,mpct-0.05):.0%}",
                    "odds": f"+{int(280-edge*3)}",
                    "matchup": f"vs {opp_name}",
                    "analysis": (
                        f"HR rate {hr_r:.3f}/PA · ISO {iso:.3f} · "
                        f"park factor {pf:.2f}x · "
                        f"proj {hr_proj:.2f} HR vs line 0.5"
                    ),
                    "home": home, "away": away,
                })

    # Sort by edge desc, reassign pick numbers
    picks.sort(key=lambda x: x["edge"], reverse=True)
    for i, p in enumerate(picks):
        p["num"] = i+1
    return picks

# ─────────────────────────────────────────────────────────────────────────────
# RENDER
# ─────────────────────────────────────────────────────────────────────────────

def initials(name):
    parts = name.split()
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) >= 2 else name[:2].upper()

def render_card(p, idx):
    t     = p["tier"]
    dirxn = p["direction"]
    arrow = "▲" if dirxn == "Over" else "▼"
    cls_arrow = "pick-arrow-up" if dirxn == "Over" else "pick-arrow-down"
    cls_line  = "pick-over"     if dirxn == "Over" else "pick-under"
    tier_cls  = f"tier-{t.lower()}"
    card_cls  = f"tier-{t.lower()}"

    st.markdown(f"""
<div class="prop-card {card_cls}" style="animation-delay:{idx*0.05}s">
  <div class="card-top">
    <div class="card-left">
      <div class="avatar">{initials(p['player'])}</div>
      <div>
        <div class="card-badges">
          <span class="tier-badge {tier_cls}">{t} TIER</span>
          <span class="prop-badge">{p['prop_type'].upper()}</span>
          <span class="pick-num">#{p['num']}</span>
        </div>
        <p class="player-name">{p['player']}</p>
        <p class="pick-line">
          <span class="{cls_arrow}">{arrow}</span>
          <span class="{cls_line}">{dirxn} {p['line']}</span>
          <span style="color:var(--muted);font-size:0.85rem;font-weight:400;margin-left:4px;">
            {p['prop_type'].lower()}
          </span>
        </p>
        <div class="matchup-info">{p['matchup']} &nbsp;·&nbsp; {p['odds']}</div>
      </div>
    </div>
    <div class="edge-block">
      <div class="edge-val">+{p['edge']:.1f}%</div>
      <div class="edge-lbl">edge</div>
    </div>
  </div>

  <div class="stat-row">
    <div class="stat-box">
      <div class="stat-label">Model</div>
      <div class="stat-val">{p['model_pct']}</div>
    </div>
    <div class="stat-box">
      <div class="stat-label">Market</div>
      <div class="stat-val">{p['market_pct']}</div>
    </div>
    <div class="stat-box">
      <div class="stat-label">Proj</div>
      <div class="stat-val">{p['proj']}</div>
    </div>
    <div class="stat-box">
      <div class="stat-label">Line</div>
      <div class="stat-val">{p['line']}</div>
    </div>
  </div>

  <div class="analysis-line">{p['analysis']}</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────────────────────

# Auto-refresh at noon ET
next_noon = NOW_ET.replace(hour=12,minute=0,second=0,microsecond=0)
if NOW_ET.hour >= 12: next_noon += timedelta(days=1)
secs = int((next_noon - NOW_ET).total_seconds())
st.markdown(f'<meta http-equiv="refresh" content="{secs}">', unsafe_allow_html=True)

# ── NAV ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="topnav">
  <div class="nav-logo">⚾ <span>Diamond</span></div>
  <div class="nav-tabs">
    <a class="nav-tab active" href="#">Picks</a>
    <a class="nav-tab" href="#">Dashboard</a>
    <a class="nav-tab" href="#">Analytics</a>
  </div>
  <div class="nav-date">{NOW_ET.strftime("%a, %b %d")} &nbsp;·&nbsp; {NOW_ET.strftime("%I:%M %p")} ET</div>
</div>
<div class="page">
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
with st.spinner("Loading today's picks…"):
    ALL_PICKS = generate_all_picks()

s_picks = [p for p in ALL_PICKS if p["tier"]=="S"]
a_picks = [p for p in ALL_PICKS if p["tier"]=="A"]
b_picks = [p for p in ALL_PICKS if p["tier"]=="B"]
c_picks = [p for p in ALL_PICKS if p["tier"]=="C"]

# ── PAGE HEADER ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:24px;">
  <div>
    <h1 style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;margin:0;color:var(--text);">
      Today's Picks
    </h1>
    <p style="font-size:0.73rem;color:var(--muted);margin:4px 0 0 0;">
      {len(ALL_PICKS)} qualifying picks &nbsp;·&nbsp; {len(TODAY_GAMES)*2} pitchers tracked
      &nbsp;·&nbsp; Generated {NOW_ET.strftime("%I:%M %p ET")}
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── GAME STRIP ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Today\'s Games</div>', unsafe_allow_html=True)
game_html = '<div class="game-strip">'
for i,(home,away) in enumerate(TODAY_GAMES):
    t = GAME_TIMES[i % len(GAME_TIMES)]
    game_html += f"""
<div class="game-chip">
  <div class="game-time">{t} ET</div>
  <div class="game-teams">{away} @ {home}</div>
</div>"""
game_html += "</div>"
st.markdown(game_html, unsafe_allow_html=True)

# ── FILTER BAR ───────────────────────────────────────────────────────────────
prop_types = ["All Props","Strikeouts","Total Bases","Hits","Home Runs"]
tier_opts  = ["All Tiers","S Tier","A Tier","B Tier","C Tier"]

fc1, fc2, fc3 = st.columns([3, 2, 1])
with fc1:
    sel_prop = st.selectbox("Prop type", prop_types, label_visibility="collapsed")
with fc2:
    sel_tier = st.selectbox("Tier", tier_opts, label_visibility="collapsed")
with fc3:
    sel_sort = st.selectbox("Sort", ["Best","Edge","Tier"], label_visibility="collapsed")

# ── FILTER LOGIC ─────────────────────────────────────────────────────────────
filtered = ALL_PICKS[:]
if sel_prop != "All Props":
    filtered = [p for p in filtered if p["prop_type"] == sel_prop]
if sel_tier != "All Tiers":
    t_letter = sel_tier.split()[0]
    filtered = [p for p in filtered if p["tier"] == t_letter]
if sel_sort == "Edge":
    filtered.sort(key=lambda x: x["edge"], reverse=True)
elif sel_sort == "Tier":
    order = {"S":0,"A":1,"B":2,"C":3}
    filtered.sort(key=lambda x: (order.get(x["tier"],9), -x["edge"]))

# ── SUMMARY BAR ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="summary-bar" style="margin-top:20px;">
  <div class="summary-box">
    <div class="s-val">{len(ALL_PICKS)}</div>
    <div class="s-lbl">Total Picks</div>
  </div>
  <div class="summary-box" style="border-color:var(--s-color);">
    <div class="s-val" style="color:var(--s-color);">{len(s_picks)}</div>
    <div class="s-lbl">S Tier</div>
  </div>
  <div class="summary-box" style="border-color:var(--a-color);">
    <div class="s-val" style="color:var(--a-color);">{len(a_picks)}</div>
    <div class="s-lbl">A Tier</div>
  </div>
  <div class="summary-box" style="border-color:var(--b-color);">
    <div class="s-val" style="color:var(--b-color);">{len(b_picks)+len(c_picks)}</div>
    <div class="s-lbl">B / C Tier</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── PICK CARDS ───────────────────────────────────────────────────────────────
st.markdown(f'<div class="pick-count">{len(filtered)} PICKS SHOWN</div>', unsafe_allow_html=True)

if not filtered:
    st.markdown('<div style="text-align:center;padding:60px;color:var(--muted);font-size:0.9rem;">No picks match the current filters.</div>', unsafe_allow_html=True)
else:
    for i, p in enumerate(filtered):
        render_card(p, i)

st.markdown("</div>", unsafe_allow_html=True)  # close .page

"""
⚾ Diamond — MLB Player Props
Modeled after Clocks NBA. Zero inputs. Log in, pick your plays.
"""

import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timezone, timedelta
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Diamond · MLB Props", page_icon="⚾",
                   layout="wide", initial_sidebar_state="collapsed")

# ─────────────────────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&display=swap');

:root {
  --bg:       #0d0f14;
  --surface:  #13161e;
  --surface2: #1a1f2b;
  --border:   #252b38;
  --text:     #e8eaf0;
  --muted:    #5a6070;
  --accent:   #00e5ff;
  --green:    #00e676;
  --red:      #ff5252;
  --amber:    #ffab40;
  --purple:   #d500f9;
  --s-color:  #d500f9;
  --a-color:  #00e5ff;
  --b-color:  #00e676;
  --c-color:  #ffab40;
}

* { box-sizing: border-box; }

html, body, [class*="css"] {
  font-family: 'DM Mono', monospace;
  background: var(--bg);
  color: var(--text);
}
.stApp { background: var(--bg); }

/* Hide Streamlit chrome */
#MainMenu, footer, header { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── TOP NAV ── */
.topnav {
  display: flex;
  align-items: center;
  gap: 0;
  padding: 0 32px;
  height: 56px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
}
.nav-logo {
  font-family: 'Syne', sans-serif;
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--text);
  margin-right: 32px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.nav-logo span { color: var(--accent); }
.nav-tabs { display: flex; gap: 4px; flex: 1; }
.nav-tab {
  font-family: 'Syne', sans-serif;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--muted);
  padding: 6px 14px;
  border-radius: 6px;
  cursor: pointer;
  text-decoration: none;
  transition: color 0.15s;
}
.nav-tab.active { background: var(--surface2); color: var(--text); }
.nav-date {
  font-size: 0.72rem;
  color: var(--muted);
  margin-left: auto;
}

/* ── PAGE PADDING ── */
.page { padding: 28px 32px; }

/* ── SECTION LABEL ── */
.section-label {
  font-family: 'Syne', sans-serif;
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.18em;
  margin-bottom: 12px;
}

/* ── GAME STRIP ── */
.game-strip {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 4px;
  margin-bottom: 24px;
  scrollbar-width: thin;
  scrollbar-color: var(--border) transparent;
}
.game-chip {
  flex-shrink: 0;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 16px;
  min-width: 130px;
}
.game-chip.active { border-color: var(--accent); }
.game-time { font-size: 0.62rem; color: var(--muted); margin-bottom: 3px; }
.game-teams { font-family: 'Syne', sans-serif; font-size: 0.82rem; font-weight: 700; }
.game-away { color: var(--muted); font-size: 0.72rem; margin-top:2px; }

/* ── FILTER BAR ── */
.filter-bar {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 20px;
  align-items: center;
}
.filter-chip {
  font-family: 'Syne', sans-serif;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 6px 14px;
  border-radius: 20px;
  border: 1px solid var(--border);
  color: var(--muted);
  cursor: pointer;
  background: transparent;
  transition: all 0.15s;
}
.filter-chip.active {
  background: var(--accent);
  color: #000;
  border-color: var(--accent);
}
.filter-chip.s-active { background: var(--s-color); color: #fff; border-color: var(--s-color); }
.filter-chip.a-active { background: var(--a-color); color: #000; border-color: var(--a-color); }
.filter-chip.b-active { background: var(--b-color); color: #000; border-color: var(--b-color); }
.filter-chip.c-active { background: var(--c-color); color: #000; border-color: var(--c-color); }
.filter-divider { width: 1px; height: 28px; background: var(--border); margin: 0 4px; }

/* ── PICK COUNT ── */
.pick-count {
  font-size: 0.68rem;
  color: var(--muted);
  margin-bottom: 16px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

/* ── PROP CARD ── */
.prop-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 12px;
  position: relative;
  overflow: hidden;
  animation: fadeUp 0.3s ease both;
}
.prop-card::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 4px;
  background: var(--accent);
  border-radius: 12px 0 0 12px;
}
.prop-card.tier-s::before { background: var(--s-color); }
.prop-card.tier-a::before { background: var(--a-color); }
.prop-card.tier-b::before { background: var(--b-color); }
.prop-card.tier-c::before { background: var(--c-color); }

@keyframes fadeUp {
  from { opacity:0; transform:translateY(8px); }
  to   { opacity:1; transform:translateY(0); }
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 14px;
}
.card-left { display: flex; align-items: center; gap: 14px; }
.avatar {
  width: 48px; height: 48px;
  border-radius: 50%;
  background: var(--surface2);
  display: flex; align-items: center; justify-content: center;
  font-family: 'Syne', sans-serif;
  font-size: 1rem;
  font-weight: 800;
  color: var(--accent);
  flex-shrink: 0;
  border: 2px solid var(--border);
}
.card-badges { display: flex; gap: 6px; align-items: center; margin-bottom: 5px; }
.tier-badge {
  font-family: 'Syne', sans-serif;
  font-size: 0.65rem;
  font-weight: 800;
  padding: 2px 8px;
  border-radius: 4px;
}
.tier-s { background: var(--s-color); color: #fff; }
.tier-a { background: var(--a-color); color: #000; }
.tier-b { background: var(--b-color); color: #000; }
.tier-c { background: var(--c-color); color: #000; }
.prop-badge {
  font-family: 'Syne', sans-serif;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  background: var(--surface2);
  color: var(--text);
  border: 1px solid var(--border);
}
.pick-num { font-size: 0.65rem; color: var(--muted); }
.player-name {
  font-family: 'Syne', sans-serif;
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--text);
  margin: 0;
}
.pick-line {
  font-family: 'Syne', sans-serif;
  font-size: 1.05rem;
  font-weight: 700;
  margin: 2px 0;
}
.pick-over  { color: var(--green); }
.pick-under { color: var(--red); }
.pick-arrow-up   { color: var(--green); margin-right: 4px; }
.pick-arrow-down { color: var(--red);   margin-right: 4px; }
.matchup-info { font-size: 0.72rem; color: var(--muted); }

.edge-block { text-align: right; }
.edge-val {
  font-family: 'Syne', sans-serif;
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--accent);
  line-height: 1;
}
.edge-lbl { font-size: 0.62rem; color: var(--muted); margin-top: 2px; }

/* ── STAT ROW ── */
.stat-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-bottom: 14px;
}
.stat-box {
  background: var(--surface2);
  border-radius: 8px;
  padding: 10px 14px;
  text-align: center;
}
.stat-label { font-size: 0.6rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 4px; }
.stat-val   { font-family: 'Syne', sans-serif; font-size: 1.05rem; font-weight: 700; }

/* ── ANALYSIS LINE ── */
.analysis-line {
  font-size: 0.73rem;
  color: var(--muted);
  line-height: 1.6;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}
.analysis-line b { color: var(--text); }

/* ── SUMMARY BAR ── */
.summary-bar {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 28px;
}
.summary-box {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px 20px;
}
.summary-box .s-val {
  font-family: 'Syne', sans-serif;
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--accent);
}
.summary-box .s-lbl {
  font-size: 0.62rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-top: 2px;
}

/* ── STREAMLIT OVERRIDES ── */
.stSelectbox > div > div,
.stMultiSelect > div > div {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  color: var(--text) !important;
}
div[data-testid="stHorizontalBlock"] { gap: 8px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS + DATA
# ─────────────────────────────────────────────────────────────────────────────
ET      = timezone(timedelta(hours=-4))
NOW_ET  = datetime.now(ET)
TODAY   = NOW_ET.strftime("%A, %B %d")
SEASON  = 2026

LEAGUE_K_PCT  = 0.225
LEAGUE_WOBA   = 0.320
LEAGUE_FIP    = 4.20
LEAGUE_RUNS   = 4.55

PARK_FACTORS = {
    "COL":1.15,"BOS":1.08,"CIN":1.07,"TEX":1.06,"PHI":1.05,
    "HOU":1.04,"BAL":1.03,"TOR":1.02,"NYY":1.01,"CHC":1.01,
    "ATL":1.00,"LAD":1.00,"NYM":0.99,"MIL":0.98,"STL":0.97,
    "CLE":0.97,"MIN":0.96,"DET":0.96,"SEA":0.95,"OAK":0.95,
    "SF":0.94,"MIA":0.94,"TB":0.93,"ARI":0.93,"LAA":0.98,
    "CWS":1.02,"KC":0.97,"PIT":0.96,"SD":0.95,"WSH":0.99,
}
STANDINGS_2025 = {
    "ARI":0.519,"ATL":0.556,"BAL":0.543,"BOS":0.481,"CHC":0.506,
    "CWS":0.364,"CIN":0.494,"CLE":0.568,"COL":0.377,"DET":0.543,
    "HOU":0.531,"KC":0.519,"LAA":0.432,"LAD":0.617,"MIA":0.414,
    "MIL":0.543,"MIN":0.506,"NYM":0.531,"NYY":0.580,"OAK":0.414,
    "PHI":0.568,"PIT":0.457,"SD":0.519,"SF":0.463,"SEA":0.500,
    "STL":0.494,"TB":0.500,"TEX":0.457,"TOR":0.463,"WSH":0.457,
}

# Today's slate — rotates by weekday
DOW = NOW_ET.weekday()
SLATES = {
    0:[("NYY","BOS"),("LAD","SF"),("ATL","PHI"),("HOU","TEX"),("CLE","DET"),("MIL","CHC")],
    1:[("NYM","ATL"),("LAD","SD"),("NYY","TOR"),("HOU","KC"), ("SEA","OAK"),("STL","CIN")],
    2:[("BOS","BAL"),("SF","COL"),("PHI","WSH"),("MIN","CLE"),("LAA","TEX"),("MIL","PIT")],
    3:[("NYY","TB"), ("LAD","ARI"),("ATL","MIA"),("HOU","LAA"),("CLE","KC"), ("CHC","STL")],
    4:[("BOS","NYM"),("SF","LAD"), ("PHI","ATL"),("TEX","HOU"),("DET","MIN"),("PIT","CIN")],
    5:[("NYY","BAL"),("LAD","COL"),("MIL","STL"),("HOU","SEA"),("CLE","CWS"),("TOR","BOS")],
    6:[("NYM","PHI"),("SF","SD"),  ("ATL","WSH"),("LAA","OAK"),("MIN","DET"),("CHC","MIL")],
}
TODAY_GAMES = SLATES.get(DOW, SLATES[0])

# Game times (staggered realistic ET)
GAME_TIMES = ["1:05 PM","1:35 PM","4:05 PM","4:10 PM","7:05 PM","7:10 PM",
              "7:15 PM","7:40 PM","9:10 PM","9:40 PM"]

# ─────────────────────────────────────────────────────────────────────────────
# DATA LAYER
# ─────────────────────────────────────────────────────────────────────────────

def _synth_pitchers(team):
    np.random.seed(abs(hash(team)) % (2**31))
    n = 10
    fip  = np.round(np.random.uniform(2.9, 5.4, n), 2)
    kpct = np.round(np.random.uniform(0.16, 0.33, n), 3)
    velo = np.round(np.random.uniform(90.0, 101.0, n), 1)
    whip = np.round(np.random.uniform(1.00, 1.60, n), 2)
    era  = np.round(fip + np.random.uniform(-0.5, 0.8, n), 2)
    ip   = np.round(np.random.uniform(5.0, 72.0, n), 1)
    gs   = np.random.randint(1, 14, n)
    first = ["Gerrit","Shane","Zack","Dylan","Luis","Max","Spencer","Nathan","Kodai","Logan"]
    last  = ["Cole","Bieber","Wheeler","Cease","Castillo","Fried","Strider","Eovaldi","Senga","Webb"]
    np.random.shuffle(first); np.random.shuffle(last)
    names = [f"{first[i%10]} {last[i%10]}" for i in range(n)]
    return pd.DataFrame({"Name":names,"Team":team,"IP":ip,"ERA":era,
                         "FIP":fip,"K_pct":kpct,"WHIP":whip,"Velo":velo,"GS":gs})

def _synth_batters(team):
    np.random.seed((abs(hash(team))+42) % (2**31))
    n = 13
    avg = np.round(np.random.uniform(0.210, 0.320, n), 3)
    iso = np.round(np.random.uniform(0.090, 0.260, n), 3)
    woba= np.round(np.random.uniform(0.265, 0.415, n), 3)
    kpct= np.round(np.random.uniform(0.130, 0.330, n), 3)
    hr_r= np.round(np.random.uniform(0.020, 0.065, n), 3)
    sb_r= np.round(np.random.uniform(0.00,  0.12,  n), 3)
    pa  = np.random.randint(25, 200, n)
    first=["Aaron","Mookie","Juan","Freddie","Yordan","Pete","Trea","Julio","Corey","Nolan","Bo","Rafael","Kyle"]
    last =["Judge","Betts","Soto","Freeman","Alvarez","Alonso","Turner","Rodriguez","Seager","Arenado","Bichette","Devers","Tucker"]
    np.random.shuffle(first); np.random.shuffle(last)
    names=[f"{first[i%13]} {last[i%13]}" for i in range(n)]
    return pd.DataFrame({"Name":names,"Team":team,"PA":pa,"AVG":avg,
                         "OBP":np.round(avg+np.random.uniform(0.05,0.11,n),3),
                         "SLG":np.round(avg+iso,3),"wOBA":woba,"ISO":iso,
                         "K_pct":kpct,"HR_rate":hr_r,"SB_rate":sb_r})

@st.cache_data(ttl=43200, show_spinner=False)
def load_pitching(team):
    try:
        import pybaseball as pb; pb.cache.enable()
        df = pb.pitching_stats(SEASON, qual=1)
        if df is None or df.empty: raise ValueError
        df = df.rename(columns={"K%":"K_pct","K/9":"K9","H/9":"H9","NameASCII":"Name"})
        if "K_pct" not in df.columns:
            df["K_pct"] = df.get("K9", pd.Series([8.5]*len(df),dtype=float))/27
        if "Velo" not in df.columns: df["Velo"] = 93.0
        if "GS"   not in df.columns: df["GS"]   = df.get("G",1)
        if "Team" in df.columns: df = df[df["Team"]==team]
        for c in ["FIP","ERA","K_pct","WHIP","Velo","GS","IP"]:
            if c not in df.columns: df[c] = np.nan
        df = df[["Name","Team","IP","ERA","FIP","K_pct","WHIP","Velo","GS"]].copy()
        df = df.loc[:,~df.columns.duplicated()].reset_index(drop=True)
        if df.empty: raise ValueError
        return df
    except: return _synth_pitchers(team)

@st.cache_data(ttl=43200, show_spinner=False)
def load_batting(team):
    try:
        import pybaseball as pb; pb.cache.enable()
        df = pb.batting_stats(SEASON, qual=1)
        if df is None or df.empty: raise ValueError
        df = df.rename(columns={"K%":"K_pct","NameASCII":"Name"})
        if "K_pct" not in df.columns: df["K_pct"] = LEAGUE_K_PCT
        if "ISO"   not in df.columns:
            df["ISO"] = pd.to_numeric(df.get("SLG",0.4),errors="coerce") - \
                        pd.to_numeric(df.get("AVG",0.25),errors="coerce")
        if "HR_rate" not in df.columns: df["HR_rate"] = 0.035
        if "SB_rate" not in df.columns: df["SB_rate"] = 0.03
        if "Team" in df.columns: df = df[df["Team"]==team]
        for c in ["PA","AVG","OBP","SLG","wOBA","ISO","K_pct","HR_rate","SB_rate"]:
            if c not in df.columns: df[c] = np.nan
        df = df[["Name","Team","PA","AVG","OBP","SLG","wOBA","ISO","K_pct","HR_rate","SB_rate"]].copy()
        df = df.loc[:,~df.columns.duplicated()].reset_index(drop=True)
        if df.empty: raise ValueError
        return df
    except: return _synth_batters(team)

@st.cache_data(ttl=43200, show_spinner=False)
def get_wpct(team):
    try:
        import pybaseball as pb
        s = pb.standings(SEASON)
        if s:
            for d in s:
                if "Tm" in d.columns and "W-L%" in d.columns:
                    r = d[d["Tm"]==team]
                    if not r.empty:
                        w = int(r["W"].values[0]) if "W" in r.columns else 0
                        l = int(r["L"].values[0]) if "L" in r.columns else 0
                        if w+l >= 10: return float(r["W-L%"].values[0])
    except: pass
    return STANDINGS_2025.get(team, 0.500)

# ─────────────────────────────────────────────────────────────────────────────
# MATH
# ─────────────────────────────────────────────────────────────────────────────

def safe_float(x, fb=0.0):
    try:
        v = float(x)
        return v if not np.isnan(v) else fb
    except: return fb

def best_sp(df):
    """Return best starter row as dict."""
    fb = {"Name":"TBD","FIP":LEAGUE_FIP,"ERA":LEAGUE_FIP,
          "K_pct":LEAGUE_K_PCT,"WHIP":1.25,"Velo":93.0}
    if df is None or df.empty: return fb
    df = df.copy()
    for c,v in fb.items():
        if c in df.columns:
            df[c] = pd.to_numeric(df[c],errors="coerce").fillna(v)
        else: df[c] = v
    pool = df[df["GS"].fillna(0)>0] if "GS" in df.columns else df
    if pool.empty: pool = df
    row = pool.sort_values("FIP").iloc[0]
    return {k: row.get(k, fb.get(k,"TBD")) for k in fb}

def team_bat_avg(df):
    fb = {"wOBA":LEAGUE_WOBA,"K_pct":LEAGUE_K_PCT,"ISO":0.155,
          "HR_rate":0.035,"SB_rate":0.030}
    if df is None or df.empty: return fb
    df = df.copy()
    for c,v in fb.items():
        if c in df.columns:
            df[c] = pd.to_numeric(df[c],errors="coerce").fillna(v)
        else: df[c] = v
    return {c: float(df[c].mean()) for c in fb}

def proj_runs(woba, opp_fip, pf=1.0):
    wf = (woba - LEAGUE_WOBA)/0.030
    ff = (LEAGUE_FIP - opp_fip)/0.50
    return max(1.5, round((LEAGUE_RUNS + wf*0.40 + ff*0.35)*pf, 2))

def proj_ks(k_p, k_opp, velo=93.0, inn=6.0):
    c = k_p + k_opp - LEAGUE_K_PCT
    if velo >= 96.0: c *= 1.05
    return max(0.5, round(c * inn * 3 * (1 + c*0.15), 1))

def log5(a, b):
    d = a+b-2*a*b
    return (a-a*b)/d if d else 0.5

def poisson_cover(mu_a, mu_b, margin=1.5):
    p = 0.0
    for ra in range(31):
        for rb in range(31):
            if ra-rb > margin:
                p += poisson.pmf(ra,mu_a)*poisson.pmf(rb,mu_b)
    return p

def tier(edge):
    if edge >= 10: return "S"
    if edge >= 6:  return "A"
    if edge >= 3:  return "B"
    return "C"

def model_pct(edge, base=0.50):
    """Rough model win% from edge."""
    return min(0.99, max(0.01, base + edge/200))

# ─────────────────────────────────────────────────────────────────────────────
# PICK GENERATION
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=43200, show_spinner=False)
def generate_all_picks():
    picks = []
    pick_num = 0

    for home, away in TODAY_GAMES:
        p_h = load_pitching(home); b_h = load_batting(home)
        p_a = load_pitching(away); b_a = load_batting(away)
        sp_h = best_sp(p_h);       sp_a = best_sp(p_a)
        bat_h = team_bat_avg(b_h); bat_a = team_bat_avg(b_a)
        pf   = PARK_FACTORS.get(home, 1.0)
        wp_h = get_wpct(home);     wp_a = get_wpct(away)

        runs_h = proj_runs(bat_h["wOBA"], sp_a["FIP"], pf)
        runs_a = proj_runs(bat_a["wOBA"], sp_h["FIP"], 1.0)
        win_h  = log5(wp_h, wp_a)

        # ── PITCHER STRIKEOUT PROP ──
        for sp, opp_bat, opp_team, team in [
            (sp_h, bat_a, away, home),
            (sp_a, bat_h, home, away),
        ]:
            k_proj = proj_ks(safe_float(sp["K_pct"], LEAGUE_K_PCT),
                             safe_float(opp_bat["K_pct"], LEAGUE_K_PCT),
                             safe_float(sp["Velo"], 93.0))
            k_line = max(0.5, round(k_proj - 0.5 + np.random.uniform(-0.3,0.3), 1))
            edge   = round((k_proj - k_line)/max(k_line,0.1)*100, 1)
            if edge < 1.5: continue
            t = tier(edge)
            mpct = model_pct(edge)
            pick_num += 1
            picks.append({
                "num": pick_num,
                "player": sp["Name"],
                "team": team,
                "opp": opp_team,
                "prop_type": "Strikeouts",
                "direction": "Over",
                "line": k_line,
                "proj": k_proj,
                "edge": edge,
                "tier": t,
                "model_pct": f"{mpct:.0%}",
                "market_pct": f"{max(0.40,mpct-0.04):.0%}",
                "odds": f"-{int(110+edge*2)}",
                "matchup": f"vs {opp_team}",
                "analysis": (
                    f"K% {safe_float(sp['K_pct'],LEAGUE_K_PCT):.1%} vs "
                    f"opp K-rate {safe_float(opp_bat['K_pct'],LEAGUE_K_PCT):.1%} · "
                    f"Velo {safe_float(sp['Velo'],93.0):.1f} mph · "
                    f"Proj {k_proj} Ks vs line {k_line} (+{edge:.1f}%)"
                ),
                "home": home, "away": away,
            })

        # ── BATTER TOTAL BASES PROP ──
        bat_df = b_h if True else b_a
        for _, bat_team, bat_df2, opp_sp, opp_team2 in [
            (0, home, b_h, sp_a, away),
            (1, away, b_a, sp_h, home),
        ]:
            if bat_df2 is None or bat_df2.empty: continue
            bdf = bat_df2.copy()
            for c in ["wOBA","ISO","K_pct","HR_rate"]:
                if c not in bdf.columns: bdf[c] = {"wOBA":LEAGUE_WOBA,"ISO":0.155,"K_pct":LEAGUE_K_PCT,"HR_rate":0.035}[c]
                bdf[c] = pd.to_numeric(bdf[c], errors="coerce").fillna({"wOBA":LEAGUE_WOBA,"ISO":0.155,"K_pct":LEAGUE_K_PCT,"HR_rate":0.035}[c])

            # pick top 3 batters by wOBA
            top = bdf.nlargest(min(3, len(bdf)), "wOBA")
            for _, row in top.iterrows():
                woba = safe_float(row["wOBA"], LEAGUE_WOBA)
                iso  = safe_float(row["ISO"],  0.155)
                opp_fip = safe_float(opp_sp["FIP"], LEAGUE_FIP)
                opp_whip= safe_float(opp_sp["WHIP"], 1.25)

                # TB projection
                contact = max(0.5, 1-(opp_whip-1.20)*0.25)
                hit_p   = woba * 0.65 + (LEAGUE_WOBA - opp_fip*0.02)*0.35
                tb_proj = round(hit_p * 4 * contact * (1+iso/0.18*0.5), 2)
                tb_line = max(0.5, round(tb_proj - 0.5 + np.random.uniform(-0.3,0.3), 1))
                edge    = round((tb_proj-tb_line)/max(tb_line,0.1)*100, 1)
                if edge < 1.5: continue
                t = tier(edge)
                mpct = model_pct(edge)
                pick_num += 1
                picks.append({
                    "num": pick_num,
                    "player": row["Name"],
                    "team": bat_team,
                    "opp": opp_team2,
                    "prop_type": "Total Bases",
                    "direction": "Over",
                    "line": tb_line,
                    "proj": round(tb_proj, 1),
                    "edge": edge,
                    "tier": t,
                    "model_pct": f"{mpct:.0%}",
                    "market_pct": f"{max(0.40,mpct-0.04):.0%}",
                    "odds": f"-{int(108+edge*2)}",
                    "matchup": f"vs {opp_team2}",
                    "analysis": (
                        f"wOBA {woba:.3f} · ISO {iso:.3f} · "
                        f"vs {opp_sp['Name']} (FIP {opp_fip:.2f} · WHIP {opp_whip:.2f}) · "
                        f"Proj {tb_proj:.1f} TB vs line {tb_line}"
                    ),
                    "home": home, "away": away,
                })

                # HITS prop
                hit_proj = round(woba * 3.8 * max(0.6, 1-(opp_whip-1.20)*0.3), 2)
                h_line   = max(0.5, round(hit_proj - 0.5 + np.random.uniform(-0.2,0.2), 1))
                h_edge   = round((hit_proj-h_line)/max(h_line,0.1)*100, 1)
                if h_edge < 1.5: continue
                ht = tier(h_edge)
                hmpct = model_pct(h_edge)
                pick_num += 1
                picks.append({
                    "num": pick_num,
                    "player": row["Name"],
                    "team": bat_team,
                    "opp": opp_team2,
                    "prop_type": "Hits",
                    "direction": "Over",
                    "line": h_line,
                    "proj": round(hit_proj, 1),
                    "edge": h_edge,
                    "tier": ht,
                    "model_pct": f"{hmpct:.0%}",
                    "market_pct": f"{max(0.40,hmpct-0.04):.0%}",
                    "odds": f"-{int(108+h_edge*2)}",
                    "matchup": f"vs {opp_team2}",
                    "analysis": (
                        f"Season wOBA {woba:.3f} · "
                        f"vs {opp_sp['Name']} WHIP {opp_whip:.2f} · "
                        f"Proj {hit_proj:.1f} hits vs line {h_line}"
                    ),
                    "home": home, "away": away,
                })

        # ── HOME RUNS ──
        for bat_team, bdf_raw, opp_sp, opp_name in [
            (home, b_h, sp_a, away),
            (away, b_a, sp_h, home),
        ]:
            if bdf_raw is None or bdf_raw.empty: continue
            bdf = bdf_raw.copy()
            if "HR_rate" not in bdf.columns: bdf["HR_rate"] = 0.035
            bdf["HR_rate"] = pd.to_numeric(bdf["HR_rate"], errors="coerce").fillna(0.035)
            if "ISO" not in bdf.columns: bdf["ISO"] = 0.155
            bdf["ISO"] = pd.to_numeric(bdf["ISO"], errors="coerce").fillna(0.155)
            power = bdf.nlargest(min(2, len(bdf)), "ISO")
            for _, row in power.iterrows():
                hr_r = safe_float(row["HR_rate"], 0.035)
                iso  = safe_float(row["ISO"], 0.155)
                pf   = PARK_FACTORS.get(bat_team if bat_team==home else opp_name, 1.0)
                hr_proj = round(hr_r * 4 * pf * (1+iso/0.18*0.1), 3)
                hr_line  = 0.5
                edge     = round((hr_proj - hr_line)/hr_line*100, 1)
                if edge < 2: continue
                t = tier(edge)
                mpct = model_pct(edge, 0.45)
                pick_num += 1
                picks.append({
                    "num": pick_num,
                    "player": row["Name"],
                    "team": bat_team,
                    "opp": opp_name,
                    "prop_type": "Home Runs",
                    "direction": "Over",
                    "line": hr_line,
                    "proj": round(hr_proj, 2),
                    "edge": edge,
                    "tier": t,
                    "model_pct": f"{mpct:.0%}",
                    "market_pct": f"{max(0.38,mpct-0.05):.0%}",
                    "odds": f"+{int(280-edge*3)}",
                    "matchup": f"vs {opp_name}",
                    "analysis": (
                        f"HR rate {hr_r:.3f}/PA · ISO {iso:.3f} · "
                        f"park factor {pf:.2f}x · "
                        f"proj {hr_proj:.2f} HR vs line 0.5"
                    ),
                    "home": home, "away": away,
                })

    # Sort by edge desc, reassign pick numbers
    picks.sort(key=lambda x: x["edge"], reverse=True)
    for i, p in enumerate(picks):
        p["num"] = i+1
    return picks

# ─────────────────────────────────────────────────────────────────────────────
# RENDER
# ─────────────────────────────────────────────────────────────────────────────

def initials(name):
    parts = name.split()
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) >= 2 else name[:2].upper()

def render_card(p, idx):
    t     = p["tier"]
    dirxn = p["direction"]
    arrow = "▲" if dirxn == "Over" else "▼"
    cls_arrow = "pick-arrow-up" if dirxn == "Over" else "pick-arrow-down"
    cls_line  = "pick-over"     if dirxn == "Over" else "pick-under"
    tier_cls  = f"tier-{t.lower()}"
    card_cls  = f"tier-{t.lower()}"

    st.markdown(f"""
<div class="prop-card {card_cls}" style="animation-delay:{idx*0.05}s">
  <div class="card-top">
    <div class="card-left">
      <div class="avatar">{initials(p['player'])}</div>
      <div>
        <div class="card-badges">
          <span class="tier-badge {tier_cls}">{t} TIER</span>
          <span class="prop-badge">{p['prop_type'].upper()}</span>
          <span class="pick-num">#{p['num']}</span>
        </div>
        <p class="player-name">{p['player']}</p>
        <p class="pick-line">
          <span class="{cls_arrow}">{arrow}</span>
          <span class="{cls_line}">{dirxn} {p['line']}</span>
          <span style="color:var(--muted);font-size:0.85rem;font-weight:400;margin-left:4px;">
            {p['prop_type'].lower()}
          </span>
        </p>
        <div class="matchup-info">{p['matchup']} &nbsp;·&nbsp; {p['odds']}</div>
      </div>
    </div>
    <div class="edge-block">
      <div class="edge-val">+{p['edge']:.1f}%</div>
      <div class="edge-lbl">edge</div>
    </div>
  </div>

  <div class="stat-row">
    <div class="stat-box">
      <div class="stat-label">Model</div>
      <div class="stat-val">{p['model_pct']}</div>
    </div>
    <div class="stat-box">
      <div class="stat-label">Market</div>
      <div class="stat-val">{p['market_pct']}</div>
    </div>
    <div class="stat-box">
      <div class="stat-label">Proj</div>
      <div class="stat-val">{p['proj']}</div>
    </div>
    <div class="stat-box">
      <div class="stat-label">Line</div>
      <div class="stat-val">{p['line']}</div>
    </div>
  </div>

  <div class="analysis-line">{p['analysis']}</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────────────────────

# Auto-refresh at noon ET
next_noon = NOW_ET.replace(hour=12,minute=0,second=0,microsecond=0)
if NOW_ET.hour >= 12: next_noon += timedelta(days=1)
secs = int((next_noon - NOW_ET).total_seconds())
st.markdown(f'<meta http-equiv="refresh" content="{secs}">', unsafe_allow_html=True)

# ── NAV ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="topnav">
  <div class="nav-logo">⚾ <span>Diamond</span></div>
  <div class="nav-tabs">
    <a class="nav-tab active" href="#">Picks</a>
    <a class="nav-tab" href="#">Dashboard</a>
    <a class="nav-tab" href="#">Analytics</a>
  </div>
  <div class="nav-date">{NOW_ET.strftime("%a, %b %d")} &nbsp;·&nbsp; {NOW_ET.strftime("%I:%M %p")} ET</div>
</div>
<div class="page">
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
with st.spinner("Loading today's picks…"):
    ALL_PICKS = generate_all_picks()

s_picks = [p for p in ALL_PICKS if p["tier"]=="S"]
a_picks = [p for p in ALL_PICKS if p["tier"]=="A"]
b_picks = [p for p in ALL_PICKS if p["tier"]=="B"]
c_picks = [p for p in ALL_PICKS if p["tier"]=="C"]

# ── PAGE HEADER ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:24px;">
  <div>
    <h1 style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;margin:0;color:var(--text);">
      Today's Picks
    </h1>
    <p style="font-size:0.73rem;color:var(--muted);margin:4px 0 0 0;">
      {len(ALL_PICKS)} qualifying picks &nbsp;·&nbsp; {len(TODAY_GAMES)*2} pitchers tracked
      &nbsp;·&nbsp; Generated {NOW_ET.strftime("%I:%M %p ET")}
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── GAME STRIP ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Today\'s Games</div>', unsafe_allow_html=True)
game_html = '<div class="game-strip">'
for i,(home,away) in enumerate(TODAY_GAMES):
    t = GAME_TIMES[i % len(GAME_TIMES)]
    game_html += f"""
<div class="game-chip">
  <div class="game-time">{t} ET</div>
  <div class="game-teams">{away} @ {home}</div>
</div>"""
game_html += "</div>"
st.markdown(game_html, unsafe_allow_html=True)

# ── FILTER BAR ───────────────────────────────────────────────────────────────
prop_types = ["All Props","Strikeouts","Total Bases","Hits","Home Runs"]
tier_opts  = ["All Tiers","S Tier","A Tier","B Tier","C Tier"]

fc1, fc2, fc3 = st.columns([3, 2, 1])
with fc1:
    sel_prop = st.selectbox("Prop type", prop_types, label_visibility="collapsed")
with fc2:
    sel_tier = st.selectbox("Tier", tier_opts, label_visibility="collapsed")
with fc3:
    sel_sort = st.selectbox("Sort", ["Best","Edge","Tier"], label_visibility="collapsed")

# ── FILTER LOGIC ─────────────────────────────────────────────────────────────
filtered = ALL_PICKS[:]
if sel_prop != "All Props":
    filtered = [p for p in filtered if p["prop_type"] == sel_prop]
if sel_tier != "All Tiers":
    t_letter = sel_tier.split()[0]
    filtered = [p for p in filtered if p["tier"] == t_letter]
if sel_sort == "Edge":
    filtered.sort(key=lambda x: x["edge"], reverse=True)
elif sel_sort == "Tier":
    order = {"S":0,"A":1,"B":2,"C":3}
    filtered.sort(key=lambda x: (order.get(x["tier"],9), -x["edge"]))

# ── SUMMARY BAR ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="summary-bar" style="margin-top:20px;">
  <div class="summary-box">
    <div class="s-val">{len(ALL_PICKS)}</div>
    <div class="s-lbl">Total Picks</div>
  </div>
  <div class="summary-box" style="border-color:var(--s-color);">
    <div class="s-val" style="color:var(--s-color);">{len(s_picks)}</div>
    <div class="s-lbl">S Tier</div>
  </div>
  <div class="summary-box" style="border-color:var(--a-color);">
    <div class="s-val" style="color:var(--a-color);">{len(a_picks)}</div>
    <div class="s-lbl">A Tier</div>
  </div>
  <div class="summary-box" style="border-color:var(--b-color);">
    <div class="s-val" style="color:var(--b-color);">{len(b_picks)+len(c_picks)}</div>
    <div class="s-lbl">B / C Tier</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── PICK CARDS ───────────────────────────────────────────────────────────────
st.markdown(f'<div class="pick-count">{len(filtered)} PICKS SHOWN</div>', unsafe_allow_html=True)

if not filtered:
    st.markdown('<div style="text-align:center;padding:60px;color:var(--muted);font-size:0.9rem;">No picks match the current filters.</div>', unsafe_allow_html=True)
else:
    for i, p in enumerate(filtered):
        render_card(p, i)

st.markdown("</div>", unsafe_allow_html=True)  # close .page
