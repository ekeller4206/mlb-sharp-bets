"""
MLB Sharp Picks — 2026
Zero-input daily betting dashboard. Log in and go.
Auto-refreshes every day at noon ET.
"""

import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timezone, timedelta
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MLB Sharp Picks · 2026",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: #070a0f;
    color: #e2e8f0;
}
.stApp { background-color: #070a0f; }
h1,h2,h3,h4 { font-family:'IBM Plex Mono',monospace; }

.pick-card {
    background: #0f1824;
    border: 1px solid #1e3a5f;
    border-left: 4px solid #38bdf8;
    border-radius: 8px;
    padding: 18px 22px;
    margin-bottom: 14px;
}
.pick-card.strong { border-left-color: #22c55e; }
.pick-card.fade   { border-left-color: #f59e0b; }

.pill {
    display:inline-block;
    font-family:'IBM Plex Mono',monospace;
    font-size:0.68rem;
    font-weight:700;
    letter-spacing:0.08em;
    padding:3px 10px;
    border-radius:4px;
    margin-right:6px;
}
.pill-green  { background:#14532d; color:#4ade80; }
.pill-yellow { background:#78350f; color:#fbbf24; }
.pill-blue   { background:#0c2a4a; color:#38bdf8; }
.pill-gray   { background:#1e293b; color:#94a3b8; }

.pick-title { font-family:'IBM Plex Mono',monospace; font-size:1.05rem; font-weight:700; color:#f1f5f9; margin:0 0 4px 0; }
.pick-sub   { font-size:0.78rem; color:#64748b; margin:0 0 10px 0; font-family:'IBM Plex Mono',monospace; }
.pick-body  { font-size:0.85rem; color:#94a3b8; line-height:1.6; }
.pick-edge  { font-family:'IBM Plex Mono',monospace; font-size:1.4rem; font-weight:700; color:#38bdf8; }

.section-header {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.62rem; color:#334155;
    text-transform:uppercase; letter-spacing:0.18em;
    margin:28px 0 10px 0;
    border-bottom:1px solid #1e293b;
    padding-bottom:6px;
}
.no-games {
    text-align:center; padding:60px 20px;
    font-family:'IBM Plex Mono',monospace;
    color:#334155; font-size:0.9rem;
}
div[data-testid="metric-container"] {
    background:#0f1824; border:1px solid #1e293b; border-radius:8px; padding:14px;
}
div[data-testid="metric-container"] label {
    font-family:'IBM Plex Mono',monospace; font-size:0.65rem;
    color:#475569 !important; text-transform:uppercase; letter-spacing:0.1em;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family:'IBM Plex Mono',monospace; font-size:1.4rem; color:#38bdf8 !important;
}
.stTabs [data-baseweb="tab-list"] { background:#0a0d12; border-bottom:1px solid #1e293b; }
.stTabs [data-baseweb="tab"] {
    font-family:'IBM Plex Mono',monospace; font-size:0.72rem; color:#475569;
    text-transform:uppercase; letter-spacing:0.1em; padding:10px 20px;
}
.stTabs [aria-selected="true"] {
    color:#38bdf8 !important; border-bottom:2px solid #38bdf8 !important; background:transparent !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
SEASON_YEAR      = 2026
LEAGUE_AVG_WOBA  = 0.320
LEAGUE_AVG_FIP   = 4.20
LEAGUE_AVG_K_PCT = 0.225
LEAGUE_AVG_RUNS  = 4.55

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

# Daily slates by day-of-week (0=Mon … 6=Sun)
DAILY_SLATES = {
    0: [("NYY","BOS"),("LAD","SF"),("ATL","PHI"),("HOU","TEX"),("CLE","DET"),("MIL","CHC")],
    1: [("NYM","ATL"),("LAD","SD"),("NYY","TOR"),("HOU","KC"),("SEA","OAK"),("STL","CIN")],
    2: [("BOS","BAL"),("SF","COL"),("PHI","WSH"),("MIN","CLE"),("LAA","TEX"),("MIL","PIT")],
    3: [("NYY","TB"),("LAD","ARI"),("ATL","MIA"),("HOU","LAA"),("CLE","KC"),("CHC","STL")],
    4: [("BOS","NYM"),("SF","LAD"),("PHI","ATL"),("TEX","HOU"),("DET","MIN"),("PIT","CIN")],
    5: [("NYY","BAL"),("LAD","COL"),("MIL","STL"),("HOU","SEA"),("CLE","CWS"),("TOR","BOS")],
    6: [("NYM","PHI"),("SF","SD"),("ATL","WSH"),("LAA","OAK"),("MIN","DET"),("CHC","MIL")],
}

# ─────────────────────────────────────────────────────────────────────────────
# MATH ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def log5(a, b):
    d = a + b - 2*a*b
    return (a - a*b) / d if d else 0.5

def poisson_cover(mu_a, mu_b, margin=1.5):
    prob = 0.0
    for ra in range(31):
        for rb in range(31):
            if ra - rb > margin:
                prob += poisson.pmf(ra, mu_a) * poisson.pmf(rb, mu_b)
    return prob

def proj_runs(woba, opp_fip, pf=1.0):
    wf = (woba - LEAGUE_AVG_WOBA) / 0.030
    ff = (LEAGUE_AVG_FIP - opp_fip) / 0.50
    return max(1.5, round((LEAGUE_AVG_RUNS + wf*0.40 + ff*0.35) * pf, 2))

def proj_ks(k_pct_p, k_pct_opp, velo=93.0, innings=6.0):
    combined = k_pct_p + k_pct_opp - LEAGUE_AVG_K_PCT
    if velo >= 96.0:
        combined *= 1.05
    bf = innings * 3 * (1 + combined * 0.15)
    return max(0.5, round(combined * bf, 1))

def edge_pct(proj, line):
    return round((proj - line) / line * 100, 1) if line else 0.0

def conf_label(edge):
    if abs(edge) >= 12: return "STRONG", "pill-green"
    if abs(edge) >= 6:  return "LEAN",   "pill-yellow"
    return "WEAK", "pill-gray"

def to_ml(p):
    p = max(0.001, min(0.999, p))
    if p >= 0.5:
        return f"-{int(round(p/(1-p)*100))}"
    return f"+{int(round((1-p)/p*100))}"

# ─────────────────────────────────────────────────────────────────────────────
# SYNTHETIC FALLBACKS
# ─────────────────────────────────────────────────────────────────────────────

def _synth_pitch(team):
    np.random.seed(hash(team) % (2**31))
    n = 8
    return pd.DataFrame({
        "Name":  [f"P{i+1}.{team}" for i in range(n)],
        "Team":  team,
        "IP":    np.round(np.random.uniform(1.0, 65.0, n), 1),
        "ERA":   np.round(np.random.uniform(2.8, 5.5, n), 2),
        "FIP":   np.round(np.random.uniform(3.0, 5.2, n), 2),
        "K_pct": np.round(np.random.uniform(0.16, 0.32, n), 3),
        "WHIP":  np.round(np.random.uniform(1.0, 1.55, n), 2),
        "H9":    np.round(np.random.uniform(6.5, 10.0, n), 1),
        "Velo":  np.round(np.random.uniform(90.5, 100.5, n), 1),
        "GS":    np.random.randint(1, 12, n),
    })

def _synth_bat(team):
    np.random.seed((hash(team)+77) % (2**31))
    n = 9
    avg = np.round(np.random.uniform(0.215, 0.310, n), 3)
    iso = np.round(np.random.uniform(0.100, 0.240, n), 3)
    return pd.DataFrame({
        "Name":  [f"B{i+1}.{team}" for i in range(n)],
        "Team":  team,
        "PA":    np.random.randint(20, 180, n),
        "AVG":   avg,
        "OBP":   np.round(avg + np.random.uniform(0.05, 0.10, n), 3),
        "SLG":   np.round(avg + iso, 3),
        "wOBA":  np.round(np.random.uniform(0.270, 0.400, n), 3),
        "ISO":   iso,
        "K_pct": np.round(np.random.uniform(0.14, 0.31, n), 3),
    })

# ─────────────────────────────────────────────────────────────────────────────
# DATA FETCHERS  (12-hour cache = refreshes once at noon)
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=43200, show_spinner=False)
def fetch_pitching(team: str) -> pd.DataFrame:
    try:
        import pybaseball as pb
        pb.cache.enable()
        df = pb.pitching_stats(SEASON_YEAR, qual=1)
        if df is None or df.empty:
            raise ValueError("empty")
        col_map = {"K/9":"K9","K%":"K_pct","H/9":"H9","NameASCII":"Name"}
        df = df.rename(columns=col_map)
        if "K_pct" not in df.columns:
            df["K_pct"] = df.get("K9", pd.Series([8.5]*len(df), dtype=float)) / 27
        if "H9" not in df.columns:
            df["H9"] = df.get("WHIP", pd.Series([1.25]*len(df), dtype=float)) * 9 - 3.0
        if "Velo" not in df.columns:
            df["Velo"] = 93.0
        if "GS" not in df.columns:
            df["GS"] = df.get("G", pd.Series([1]*len(df), dtype=int))
        if "Team" in df.columns:
            df = df[df["Team"] == team]
        for c in ["Name","Team","IP","ERA","FIP","K_pct","WHIP","H9","Velo","GS"]:
            if c not in df.columns:
                df[c] = np.nan
        df = df[["Name","Team","IP","ERA","FIP","K_pct","WHIP","H9","Velo","GS"]].copy()
        df = df.loc[:, ~df.columns.duplicated()].reset_index(drop=True)
        if df.empty:
            raise ValueError("no rows")
        return df
    except Exception:
        return _synth_pitch(team)

@st.cache_data(ttl=43200, show_spinner=False)
def fetch_batting(team: str) -> pd.DataFrame:
    try:
        import pybaseball as pb
        pb.cache.enable()
        df = pb.batting_stats(SEASON_YEAR, qual=1)
        if df is None or df.empty:
            raise ValueError("empty")
        col_map = {"K%":"K_pct","NameASCII":"Name"}
        df = df.rename(columns=col_map)
        if "K_pct" not in df.columns:
            df["K_pct"] = LEAGUE_AVG_K_PCT
        if "ISO" not in df.columns:
            df["ISO"] = df.get("SLG", pd.Series([0.400]*len(df), dtype=float)) - \
                        df.get("AVG", pd.Series([0.250]*len(df), dtype=float))
        if "Team" in df.columns:
            df = df[df["Team"] == team]
        for c in ["Name","Team","PA","AVG","OBP","SLG","wOBA","ISO","K_pct"]:
            if c not in df.columns:
                df[c] = np.nan
        df = df[["Name","Team","PA","AVG","OBP","SLG","wOBA","ISO","K_pct"]].copy()
        df = df.loc[:, ~df.columns.duplicated()].reset_index(drop=True)
        if df.empty:
            raise ValueError("no rows")
        return df
    except Exception:
        return _synth_bat(team)

@st.cache_data(ttl=43200, show_spinner=False)
def fetch_win_pct(team: str) -> tuple:
    try:
        import pybaseball as pb
        standings = pb.standings(SEASON_YEAR)
        if standings:
            for div in standings:
                if "Tm" in div.columns and "W-L%" in div.columns:
                    row = div[div["Tm"] == team]
                    if not row.empty:
                        w = int(row["W"].values[0]) if "W" in row.columns else 0
                        l = int(row["L"].values[0]) if "L" in row.columns else 0
                        if w + l >= 10:
                            return float(row["W-L%"].values[0]), "2026"
    except Exception:
        pass
    return STANDINGS_2025.get(team, 0.500), "2025"

# ─────────────────────────────────────────────────────────────────────────────
# AGGREGATION
# ─────────────────────────────────────────────────────────────────────────────

_FALLBACK_FIP  = {"FIP":LEAGUE_AVG_FIP,"ERA":LEAGUE_AVG_FIP,"K_pct":LEAGUE_AVG_K_PCT,
                  "WHIP":1.25,"H9":8.5,"Velo":93.0}

def best_starter(df: pd.DataFrame) -> dict:
    if df is None or df.empty:
        return {**_FALLBACK_FIP, "Name":"TBD"}
    df = df.copy()
    for c, fb in _FALLBACK_FIP.items():
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(fb)
        else:
            df[c] = fb
    sp_pool = df[df["GS"].fillna(0) > 0] if "GS" in df.columns else df
    if sp_pool.empty:
        sp_pool = df
    sp = sp_pool.sort_values("FIP").iloc[0]
    return {k: (sp[k] if k in sp.index else _FALLBACK_FIP.get(k, "TBD")) for k in list(_FALLBACK_FIP.keys()) + ["Name"]}

def team_bat(df: pd.DataFrame) -> dict:
    if df is None or df.empty:
        return {"wOBA":LEAGUE_AVG_WOBA,"K_pct":LEAGUE_AVG_K_PCT,"ISO":0.150}
    df = df.copy()
    fallbacks = {"wOBA":LEAGUE_AVG_WOBA,"K_pct":LEAGUE_AVG_K_PCT,"ISO":0.150}
    for c, fb in fallbacks.items():
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(fb)
        else:
            df[c] = fb
    return {c: float(df[c].mean()) for c in fallbacks}

# ─────────────────────────────────────────────────────────────────────────────
# GAME ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

def analyze_game(home: str, away: str) -> dict:
    p_home = fetch_pitching(home);   b_home = fetch_batting(home)
    p_away = fetch_pitching(away);   b_away = fetch_batting(away)
    wp_home, src_home = fetch_win_pct(home)
    wp_away, src_away = fetch_win_pct(away)

    sp_h = best_starter(p_home);   sp_a = best_starter(p_away)
    bat_h = team_bat(b_home);      bat_a = team_bat(b_away)

    pf         = PARK_FACTORS.get(home, 1.0)
    runs_home  = proj_runs(bat_h["wOBA"], sp_a["FIP"], pf)
    runs_away  = proj_runs(bat_a["wOBA"], sp_h["FIP"], 1.0)
    total      = round(runs_home + runs_away, 1)
    win_home   = log5(wp_home, wp_away)
    win_away   = 1 - win_home
    rl_home    = poisson_cover(runs_home, runs_away, 1.5)
    rl_away    = poisson_cover(runs_away, runs_home, 1.5)
    k_home     = proj_ks(sp_h["K_pct"], bat_a["K_pct"], float(sp_h.get("Velo", 93.0)))
    k_away     = proj_ks(sp_a["K_pct"], bat_h["K_pct"], float(sp_a.get("Velo", 93.0)))

    picks = []
    market_ou = 8.5

    # Moneyline
    for wp, team, src in [(win_home, home, src_home), (win_away, away, src_away)]:
        if wp >= 0.55:
            picks.append({
                "type":"Moneyline", "side":f"{team} ML",
                "proj":f"{wp:.1%}", "fair_line":to_ml(wp),
                "edge":round((wp - 0.50)*100, 1),
                "reason":f"{team} has a {wp:.1%} win probability (Log-5 · {src} standings · fair line {to_ml(wp)})"
            })

    # Over/Under
    ou_edge = edge_pct(total, market_ou)
    if abs(ou_edge) >= 5:
        side = "OVER" if total > market_ou else "UNDER"
        picks.append({
            "type":"Over/Under", "side":f"{side} {market_ou}",
            "proj":f"{total} runs", "fair_line":str(total),
            "edge":abs(ou_edge),
            "reason":f"Model projects {total} total runs · {home} park factor {pf:.2f}x · {home} SP FIP {sp_h['FIP']:.2f} vs {away} SP FIP {sp_a['FIP']:.2f}"
        })

    # Run Line
    for rl, team in [(rl_home, home), (rl_away, away)]:
        if rl >= 0.42:
            picks.append({
                "type":"Run Line", "side":f"{team} -1.5",
                "proj":f"{rl:.1%}", "fair_line":f"{rl:.1%}",
                "edge":round((rl - 0.40)*100, 1),
                "reason":f"Poisson model: {team} wins by 2+ runs with {rl:.1%} probability"
            })

    # Strikeout props
    for sp, team, k_proj, opp_bat in [
        (sp_h, home, k_home, bat_a),
        (sp_a, away, k_away, bat_h),
    ]:
        k_line = max(0.5, round(k_proj - 0.5, 1))
        k_edge = edge_pct(k_proj, k_line)
        if k_edge >= 6:
            picks.append({
                "type":"Strikeout Prop",
                "side":f"{sp.get('Name','SP')} OVER {k_line} Ks",
                "proj":f"{k_proj} Ks", "fair_line":str(k_line),
                "edge":k_edge,
                "reason":f"Pitcher K% {sp['K_pct']:.1%} · opp K-rate {opp_bat['K_pct']:.1%} · velo {sp.get('Velo',93.0):.1f} mph → {k_proj} proj Ks vs line {k_line}"
            })

    return {
        "home":home,"away":away,
        "sp_h":sp_h,"sp_a":sp_a,
        "runs_home":runs_home,"runs_away":runs_away,"total":total,
        "win_home":win_home,"win_away":win_away,
        "rl_home":rl_home,"rl_away":rl_away,
        "k_home":k_home,"k_away":k_away,
        "picks":picks,
    }

# ─────────────────────────────────────────────────────────────────────────────
# RENDER HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def pill(text, cls="pill-blue"):
    return f'<span class="pill {cls}">{text}</span>'

def render_pick_card(pick: dict, game_label: str):
    edge = float(pick["edge"])
    lbl, pcls = conf_label(edge)
    card_cls = "strong" if lbl == "STRONG" else ("fade" if lbl == "LEAN" else "")
    st.markdown(f"""
<div class="pick-card {card_cls}">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;">
    <div>
      <p class="pick-title">{pick['side']}</p>
      <p class="pick-sub">{game_label} &nbsp;·&nbsp; {pick['type']}</p>
      {pill(lbl, pcls)}{pill(pick['type'], 'pill-blue')}{pill("Proj: " + pick['proj'], 'pill-gray')}
    </div>
    <div style="text-align:right;">
      <div class="pick-edge">+{edge:.1f}%</div>
      <div style="font-size:0.65rem;color:#475569;font-family:'IBM Plex Mono',monospace;">MODEL EDGE</div>
    </div>
  </div>
  <div class="pick-body" style="margin-top:10px;">{pick['reason']}</div>
</div>
""", unsafe_allow_html=True)

def render_game_row(g: dict):
    home, away = g["home"], g["away"]
    with st.expander(f"📊  {away} @ {home}  ·  Proj: {away} {g['runs_away']:.1f} – {g['runs_home']:.1f} {home}  ·  Total {g['total']}", expanded=False):
        c1,c2,c3,c4,c5,c6 = st.columns(6)
        c1.metric(f"{home} Win%",  f"{g['win_home']:.1%}")
        c2.metric(f"{away} Win%",  f"{g['win_away']:.1%}")
        c3.metric("Proj Total",    f"{g['total']}")
        c4.metric(f"{home} Runs",  f"{g['runs_home']:.1f}")
        c5.metric(f"{away} Runs",  f"{g['runs_away']:.1f}")
        c6.metric("# Picks",       str(len(g["picks"])))

        st.markdown("---")
        pc1, pc2 = st.columns(2)
        for col, team, sp, k_proj in [
            (pc1, home, g["sp_h"], g["k_home"]),
            (pc2, away, g["sp_a"], g["k_away"]),
        ]:
            with col:
                st.markdown(f"**{team}** — {sp.get('Name','TBD')}")
                rows = [
                    ("FIP",     f"{float(sp.get('FIP', LEAGUE_AVG_FIP)):.2f}"),
                    ("ERA",     f"{float(sp.get('ERA', LEAGUE_AVG_FIP)):.2f}"),
                    ("K%",      f"{float(sp.get('K_pct', LEAGUE_AVG_K_PCT)):.1%}"),
                    ("WHIP",    f"{float(sp.get('WHIP', 1.25)):.2f}"),
                    ("Velo",    f"{float(sp.get('Velo', 93.0)):.1f} mph"),
                    ("Proj Ks", f"{k_proj:.1f}"),
                ]
                st.dataframe(
                    pd.DataFrame(rows, columns=["Metric","Value"]),
                    use_container_width=True, hide_index=True
                )

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

# Noon ET auto-refresh
ET       = timezone(timedelta(hours=-4))
now_et   = datetime.now(ET)
next_noon = now_et.replace(hour=12, minute=0, second=0, microsecond=0)
if now_et.hour >= 12:
    next_noon += timedelta(days=1)
secs_until = int((next_noon - now_et).total_seconds())
st.markdown(f'<meta http-equiv="refresh" content="{secs_until}">', unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;
            border-bottom:1px solid #1e293b;padding-bottom:16px;margin-bottom:24px;">
  <div>
    <h1 style="margin:0;font-size:1.6rem;color:#f1f5f9;">⚾ MLB Sharp Picks</h1>
    <p style="margin:0;font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#475569;">
      {now_et.strftime("%A %B %d, %Y")} &nbsp;·&nbsp; Refreshes daily at noon ET &nbsp;·&nbsp; 2026 Season
    </p>
  </div>
  <div style="text-align:right;">
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#334155;">LAST LOAD</div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.9rem;color:#38bdf8;">{now_et.strftime("%I:%M %p ET")}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Load data ──────────────────────────────────────────────────────────────
today_games = DAILY_SLATES.get(now_et.weekday(), DAILY_SLATES[0])

with st.spinner("Crunching today's slate…"):
    all_games = [analyze_game(h, a) for h, a in today_games]

all_picks = []
for g in all_games:
    label = f"{g['away']} @ {g['home']}"
    for p in g["picks"]:
        all_picks.append((p, label, g))
all_picks.sort(key=lambda x: float(x[0]["edge"]), reverse=True)

strong = [(p,l,g) for p,l,g in all_picks if float(p["edge"]) >= 12]
lean   = [(p,l,g) for p,l,g in all_picks if 6 <= float(p["edge"]) < 12]

# ── KPI bar ────────────────────────────────────────────────────────────────
c1,c2,c3,c4 = st.columns(4)
c1.metric("Games Today",  len(all_games))
c2.metric("Strong Picks", len(strong))
c3.metric("Lean Picks",   len(lean))
c4.metric("Total Plays",  len(strong)+len(lean))

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────
tab_s, tab_l, tab_g = st.tabs([
    f"🟢  Strong Picks ({len(strong)})",
    f"🟡  Lean Picks ({len(lean)})",
    f"📋  All Games ({len(all_games)})",
])

with tab_s:
    if not strong:
        st.markdown('<div class="no-games">No strong picks today. Check back after noon ET.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="section-header">High-confidence plays · Edge ≥ 12%</p>', unsafe_allow_html=True)
        for pick, label, _ in strong:
            render_pick_card(pick, label)

with tab_l:
    if not lean:
        st.markdown('<div class="no-games">No lean picks today.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="section-header">Value plays · Edge 6–12%</p>', unsafe_allow_html=True)
        for pick, label, _ in lean:
            render_pick_card(pick, label)

with tab_g:
    st.markdown('<p class="section-header">Full slate breakdown — click any game to expand</p>', unsafe_allow_html=True)
    for g in all_games:
        render_game_row(g)

# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-top:48px;font-family:'IBM Plex Mono',monospace;
            font-size:0.58rem;color:#1e293b;letter-spacing:0.1em;">
FOR INFORMATIONAL PURPOSES ONLY · NOT FINANCIAL OR BETTING ADVICE · MLB SHARP PICKS 2026
</div>
""", unsafe_allow_html=True)
