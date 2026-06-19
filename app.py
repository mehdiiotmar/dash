import streamlit as st
import pandas as pd
import json
import os
import io
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hashlib

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WMCT – WI Training Dashboard",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Hide default Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Top bar */
.top-bar {
    background: linear-gradient(135deg, #00245D 0%, #003087 60%, #185FA5 100%);
    padding: 14px 24px;
    border-radius: 12px;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.top-bar-title { color: white; font-size: 22px; font-weight: 700; margin: 0; }
.top-bar-sub { color: #A8C7EE; font-size: 12px; margin: 0; letter-spacing: 1px; }

/* KPI cards */
.kpi-card {
    background: white;
    border-radius: 12px;
    padding: 18px 20px;
    border: 1px solid #E8EDF5;
    box-shadow: 0 2px 8px rgba(0,48,135,0.06);
    text-align: center;
    transition: transform .15s;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(0,48,135,0.1); }
.kpi-number { font-size: 32px; font-weight: 700; margin: 4px 0; }
.kpi-label { font-size: 11px; font-weight: 600; color: #6B7280; text-transform: uppercase; letter-spacing: .8px; }
.kpi-sub { font-size: 11px; color: #9CA3AF; margin-top: 2px; }

/* Status pills */
.pill-done   { background:#D1FAE5; color:#065F46; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; }
.pill-prog   { background:#FEF3C7; color:#92400E; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; }
.pill-none   { background:#FEE2E2; color:#991B1B; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; }
.pill-valid  { background:#DBEAFE; color:#1E40AF; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; }

/* Section headers */
.section-hdr {
    font-size: 13px; font-weight: 700; color: #003087;
    text-transform: uppercase; letter-spacing: .6px;
    padding: 6px 0 4px; border-bottom: 2px solid #003087;
    margin-bottom: 12px;
}

/* Sidebar */
.sidebar-logo {
    text-align: center;
    padding: 16px 0 8px;
}

/* Progress bar custom */
.prog-bar-wrap { background: #E5E7EB; border-radius: 6px; height: 8px; overflow: hidden; }
.prog-bar-fill { height: 8px; border-radius: 6px; background: linear-gradient(90deg, #003087, #185FA5); }

/* Table styling */
.wi-table th { background: #003087 !important; color: white !important; }

/* Scrollable container */
.scroll-table { max-height: 420px; overflow-y: auto; }

/* Alert boxes */
.alert-info    { background:#EFF6FF; border-left:4px solid #3B82F6; padding:10px 14px; border-radius:0 8px 8px 0; font-size:13px; color:#1E40AF; }
.alert-success { background:#F0FDF4; border-left:4px solid #22C55E; padding:10px 14px; border-radius:0 8px 8px 0; font-size:13px; color:#15803D; }
.alert-warn    { background:#FFFBEB; border-left:4px solid #F59E0B; padding:10px 14px; border-radius:0 8px 8px 0; font-size:13px; color:#92400E; }
</style>
""", unsafe_allow_html=True)

# ── Data file path ────────────────────────────────────────────────────────────
DATA_FILE = "wmct_data.json"

# ── Default data ──────────────────────────────────────────────────────────────
DEFAULT_BINOMES = [
    {"id": 1, "name": "Binôme 1", "members": "Ahmed & Sara",        "active": True},
    {"id": 2, "name": "Binôme 2", "members": "Khalid & Fatima",     "active": True},
    {"id": 3, "name": "Binôme 3", "members": "Youssef & Nadia",     "active": True},
    {"id": 4, "name": "Binôme 4", "members": "Omar & Leila",        "active": True},
    {"id": 5, "name": "Binôme 5", "members": "Hassan & Amina",      "active": True},
    {"id": 6, "name": "Binôme 6", "members": "Mehdi & Rim",         "active": True},
    {"id": 7, "name": "Binôme 7", "members": "Karim & Soukaina",    "active": True},
    {"id": 8, "name": "Binôme 8", "members": "Amine & Hajar",       "active": True},
]

DEFAULT_WIS = [
    {"id": 1, "title": "WI: Open Vessel",                    "phase": "Ship Planning", "nav": "CATOS Home → Ship Planning → Data → Vessel & Voyage",              "created": "2025-01-01", "validated": False},
    {"id": 2, "title": "WI: Create Scenario Vessel & Voyage","phase": "Ship Planning", "nav": "Ship Planning Home → DATA → Scenario for Vessel & Voyage",          "created": "2025-01-01", "validated": False},
    {"id": 3, "title": "WI: Create Stoppage",                "phase": "Planning",      "nav": "Ship Planning → Crane Working & Hatch Plan",                        "created": "2025-01-01", "validated": False},
    {"id": 4, "title": "WI: ROB to Restow / Restow to ROB", "phase": "Operations",    "nav": "Ship Planning → Plan View → Bay Plan",                              "created": "2025-01-01", "validated": False},
    {"id": 5, "title": "WI: Bay Split & Crane Assignment",   "phase": "Planning",      "nav": "Ship Planning → Crane Working → Split Mode → Crane Assignment",     "created": "2025-01-01", "validated": False},
]

DEFAULT_ASSIGNMENTS = {}
for wi in DEFAULT_WIS:
    DEFAULT_ASSIGNMENTS[str(wi["id"])] = {}
    sample = [
        [("Completed",5),("Completed",4),("In Progress",3),("Completed",5),("Not Started",0),("Completed",4),("In Progress",3),("Not Started",0)],
        [("Completed",4),("In Progress",2),("Completed",5),("Not Started",0),("Completed",3),("In Progress",2),("Not Started",0),("Completed",4)],
        [("In Progress",2),("Completed",5),("Not Started",0),("In Progress",3),("Completed",4),("Not Started",0),("Completed",5),("In Progress",2)],
        [("Not Started",0),("Not Started",0),("In Progress",2),("Completed",4),("In Progress",3),("Completed",5),("Not Started",0),("Completed",4)],
        [("Completed",5),("In Progress",3),("Completed",4),("Not Started",0),("Not Started",0),("In Progress",2),("Completed",5),("In Progress",3)],
    ]
    for j, b in enumerate(DEFAULT_BINOMES):
        s, sc = sample[wi["id"]-1][j]
        DEFAULT_ASSIGNMENTS[str(wi["id"])][str(b["id"])] = {
            "status": s, "score": sc, "notes": "", "updated": ""
        }

# ── Persistence helpers ───────────────────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "binomes": DEFAULT_BINOMES,
        "wis": DEFAULT_WIS,
        "assignments": DEFAULT_ASSIGNMENTS,
        "users": [
            {"username": "manager", "password": _hash("manager123"), "role": "manager", "binome_id": None},
            {"username": "binome1", "password": _hash("pass1"),      "role": "binome",  "binome_id": 1},
            {"username": "binome2", "password": _hash("pass2"),      "role": "binome",  "binome_id": 2},
            {"username": "binome3", "password": _hash("pass3"),      "role": "binome",  "binome_id": 3},
            {"username": "binome4", "password": _hash("pass4"),      "role": "binome",  "binome_id": 4},
            {"username": "binome5", "password": _hash("pass5"),      "role": "binome",  "binome_id": 5},
            {"username": "binome6", "password": _hash("pass6"),      "role": "binome",  "binome_id": 6},
        ],
    }

def save_data(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2, default=str)

def _hash(pw): return hashlib.sha256(pw.encode()).hexdigest()

# ── Session state init ────────────────────────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = load_data()
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

data = st.session_state.data

# ── Auth ──────────────────────────────────────────────────────────────────────
def login_page():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div style='text-align:center; padding: 30px 0 20px'>
            <div style='font-size:48px'>⚓</div>
            <div style='font-size:26px; font-weight:700; color:#00245D'>WMCT</div>
            <div style='font-size:12px; color:#6B7280; letter-spacing:2px; margin-bottom:24px'>WEST MED CONTAINER TERMINAL</div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("### Sign in to WI Dashboard")
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("🔐 Sign In", use_container_width=True)
            
            if submitted:
                users = data.get("users", [])
                matched = next((u for u in users if u["username"] == username and u["password"] == _hash(password)), None)
                if matched:
                    st.session_state.logged_in = True
                    st.session_state.user = matched
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
        
        st.markdown("""
        <div class='alert-info' style='margin-top:16px'>
            <b>Demo credentials:</b><br>
            Manager: <code>manager</code> / <code>manager123</code><br>
            Binôme 1: <code>binome1</code> / <code>pass1</code>  (up to binome6)
        </div>
        """, unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
STATUS_OPTS = ["Not Started", "In Progress", "Completed"]
PHASES      = ["Ship Planning", "Planning", "Operations", "CATOS Admin", "General"]

def status_pill(s):
    if s == "Completed":   return f"<span class='pill-done'>✅ Completed</span>"
    if s == "In Progress": return f"<span class='pill-prog'>🔄 In Progress</span>"
    return f"<span class='pill-none'>⭕ Not Started</span>"

def stars(n): return "★" * int(n) + "☆" * (5 - int(n)) if n else "—"

def get_binome_stats(bid):
    wis = data["wis"]
    done = prog = none = scores = 0
    score_list = []
    for wi in wis:
        a = data["assignments"].get(str(wi["id"]), {}).get(str(bid), {})
        s = a.get("status", "Not Started")
        sc = a.get("score", 0)
        if s == "Completed":   done += 1; score_list.append(sc) if sc else None
        elif s == "In Progress": prog += 1
        else: none += 1
    avg = sum(score_list)/len(score_list) if score_list else 0
    return {"done": done, "prog": prog, "none": none, "avg": avg, "total": len(wis)}

def get_wi_stats(wi_id):
    binomes = [b for b in data["binomes"] if b["active"]]
    done = prog = none = 0
    scores = []
    for b in binomes:
        a = data["assignments"].get(str(wi_id), {}).get(str(b["id"]), {})
        s = a.get("status", "Not Started")
        sc = a.get("score", 0)
        if s == "Completed":   done += 1; scores.append(sc) if sc else None
        elif s == "In Progress": prog += 1
        else: none += 1
    return {"done": done, "prog": prog, "none": none, "total": len(binomes), "scores": scores}

# ── Sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar():
    user = st.session_state.user
    is_manager = user["role"] == "manager"
    
    with st.sidebar:
        st.markdown("""
        <div class='sidebar-logo'>
            <div style='font-size:36px'>⚓</div>
            <div style='font-weight:700; font-size:18px; color:#00245D'>WMCT</div>
            <div style='font-size:10px; color:#6B7280; letter-spacing:1.5px'>WI TRAINING DASHBOARD</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='background:#EFF6FF; border-radius:8px; padding:10px 12px; margin:8px 0 16px; font-size:12px'>
            👤 <b>{user['username']}</b><br>
            <span style='color:#6B7280'>{'🏢 Manager' if is_manager else '👥 Binôme'}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**Navigation**")
        
        pages_manager = ["📊 Dashboard", "📋 WI Management", "👥 Binômes", "✅ Validate WIs", "📈 Analytics", "📥 Import / Export", "⚙️ Settings"]
        pages_binome  = ["📊 Dashboard", "📝 My Progress", "📥 Import / Export"]
        pages = pages_manager if is_manager else pages_binome
        
        for p in pages:
            key = p.split(" ", 1)[1] if " " in p else p
            is_active = st.session_state.page == key
            if st.button(p, key=f"nav_{p}", use_container_width=True,
                         type="primary" if is_active else "secondary"):
                st.session_state.page = key
                st.rerun()
        
        st.markdown("---")
        
        # Quick stats
        active_b = [b for b in data["binomes"] if b["active"]]
        total_cells = len(data["wis"]) * len(active_b)
        done_cells = sum(
            1 for wi in data["wis"] for b in active_b
            if data["assignments"].get(str(wi["id"]),{}).get(str(b["id"]),{}).get("status") == "Completed"
        )
        pct = int(done_cells/total_cells*100) if total_cells else 0
        
        st.markdown(f"""
        <div style='font-size:11px; color:#6B7280; margin-bottom:4px'>Overall completion</div>
        <div style='font-size:22px; font-weight:700; color:#003087'>{pct}%</div>
        <div class='prog-bar-wrap' style='margin-bottom:12px'>
            <div class='prog-bar-fill' style='width:{pct}%'></div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()

# ── Pages ─────────────────────────────────────────────────────────────────────

def page_dashboard():
    st.markdown("""
    <div class='top-bar'>
        <div>
            <div class='top-bar-title'>⚓ WMCT — WI Training Dashboard</div>
            <div class='top-bar-sub'>WEST MED CONTAINER TERMINAL · CATOS PRE-GO-LIVE TRAINING PHASE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ── KPIs ──
    active_b = [b for b in data["binomes"] if b["active"]]
    total_wi = len(data["wis"])
    total_cells = total_wi * len(active_b)
    
    done_c = sum(1 for wi in data["wis"] for b in active_b
                 if data["assignments"].get(str(wi["id"]),{}).get(str(b["id"]),{}).get("status")=="Completed")
    prog_c = sum(1 for wi in data["wis"] for b in active_b
                 if data["assignments"].get(str(wi["id"]),{}).get(str(b["id"]),{}).get("status")=="In Progress")
    none_c = total_cells - done_c - prog_c
    pct    = round(done_c/total_cells*100, 1) if total_cells else 0
    
    validated_wi = sum(1 for wi in data["wis"] if wi.get("validated"))
    
    k1, k2, k3, k4, k5 = st.columns(5)
    kpis = [
        (k1, str(total_wi),        "Total WIs",         f"{len(active_b)} binômes", "#185FA5"),
        (k2, str(done_c),          "Tasks Completed",   f"{pct}% overall",           "#1D9E75"),
        (k3, str(prog_c),          "In Progress",       "Actively working",          "#BA7517"),
        (k4, str(none_c),          "Not Started",       "Pending",                   "#E24B4A"),
        (k5, str(validated_wi),    "WIs Validated",     f"of {total_wi} total",      "#6366F1"),
    ]
    for col, val, label, sub, color in kpis:
        with col:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>{label}</div>
                <div class='kpi-number' style='color:{color}'>{val}</div>
                <div class='kpi-sub'>{sub}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ── Charts row ──
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("<div class='section-hdr'>📊 Binôme Completion</div>", unsafe_allow_html=True)
        rows = []
        for b in active_b:
            s = get_binome_stats(b["id"])
            rows.append({"Binôme": b["name"], "Members": b["members"],
                         "Completed": s["done"], "In Progress": s["prog"],
                         "Not Started": s["none"],
                         "Pct": round(s["done"]/s["total"]*100) if s["total"] else 0,
                         "Avg Score": round(s["avg"], 1)})
        df = pd.DataFrame(rows).sort_values("Pct", ascending=False)
        
        fig = px.bar(df, x="Binôme", y=["Completed","In Progress","Not Started"],
                     color_discrete_map={"Completed":"#1D9E75","In Progress":"#F59E0B","Not Started":"#EF4444"},
                     barmode="stack", height=300)
        fig.update_layout(margin=dict(l=0,r=0,t=10,b=0), legend=dict(orientation="h", y=-0.2),
                          plot_bgcolor="white", paper_bgcolor="white",
                          xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#F3F4F6"))
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        st.markdown("<div class='section-hdr'>🎯 WI Completion Rate</div>", unsafe_allow_html=True)
        wi_rows = []
        for wi in data["wis"]:
            s = get_wi_stats(wi["id"])
            pct_wi = round(s["done"]/s["total"]*100) if s["total"] else 0
            wi_rows.append({"WI": wi["title"].replace("WI: ",""), "Pct": pct_wi,
                            "Done": s["done"], "Total": s["total"]})
        df_wi = pd.DataFrame(wi_rows)
        
        fig2 = px.bar(df_wi, x="Pct", y="WI", orientation="h", height=300,
                      color="Pct", color_continuous_scale=["#FEE2E2","#FEF3C7","#D1FAE5"],
                      range_color=[0,100], text="Pct")
        fig2.update_traces(texttemplate="%{text}%", textposition="outside")
        fig2.update_layout(margin=dict(l=0,r=0,t=10,b=0), coloraxis_showscale=False,
                           plot_bgcolor="white", paper_bgcolor="white",
                           xaxis=dict(range=[0,115], showgrid=False), yaxis=dict(showgrid=False))
        st.plotly_chart(fig2, use_container_width=True)
    
    # ── Binôme progress table ──
    st.markdown("<div class='section-hdr'>👥 Binôme Progress Overview</div>", unsafe_allow_html=True)
    
    table_rows = []
    for b in active_b:
        s = get_binome_stats(b["id"])
        pct_b = round(s["done"]/s["total"]*100) if s["total"] else 0
        bar_html = f"<div class='prog-bar-wrap'><div class='prog-bar-fill' style='width:{pct_b}%'></div></div><small>{pct_b}%</small>"
        status = "🏆 Champion" if pct_b==100 else ("⭐ Excellent" if pct_b>=75 else ("✅ On Track" if pct_b>=50 else "📈 Improving"))
        table_rows.append({
            "Binôme": b["name"], "Members": b["members"],
            "✅ Done": s["done"], "🔄 Progress": s["prog"], "⭕ Pending": s["none"],
            "Completion": f"{pct_b}%", "⭐ Avg Score": f"{s['avg']:.1f}" if s["avg"] else "—",
            "Status": status
        })
    
    df_table = pd.DataFrame(table_rows)
    st.dataframe(df_table, use_container_width=True, hide_index=True,
                 column_config={
                     "Completion": st.column_config.ProgressColumn("Completion", min_value=0, max_value=100, format="%d%%"),
                     "⭐ Avg Score": st.column_config.NumberColumn("⭐ Avg Score", format="%.1f"),
                 })
    
    # ── Recent activity ──
    st.markdown("<div class='section-hdr'>🕐 Recent Updates</div>", unsafe_allow_html=True)
    recent = []
    for wi in data["wis"]:
        for b in active_b:
            a = data["assignments"].get(str(wi["id"]),{}).get(str(b["id"]),{})
            if a.get("updated"):
                recent.append({
                    "Date": a["updated"][:10],
                    "Binôme": b["name"],
                    "WI": wi["title"].replace("WI:","").strip(),
                    "Status": a["status"],
                    "Score": stars(a.get("score",0)) if a.get("score") else "—"
                })
    if recent:
        recent.sort(key=lambda x: x["Date"], reverse=True)
        st.dataframe(pd.DataFrame(recent[:15]), use_container_width=True, hide_index=True)
    else:
        st.info("No updates recorded yet.")


def page_wi_management():
    st.markdown("<div class='section-hdr'>📋 Work Instruction Management</div>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 All WIs", "➕ Add New WI"])
    
    with tab1:
        # Filter
        cf1, cf2, cf3 = st.columns([2,1,1])
        with cf1:
            search = st.text_input("🔍 Search WIs", placeholder="Search by title or phase...")
        with cf2:
            phase_filter = st.selectbox("Phase", ["All"] + PHASES)
        with cf3:
            status_filter = st.selectbox("Status", ["All", "Validated", "Not Validated"])
        
        wis = data["wis"]
        if search:
            wis = [w for w in wis if search.lower() in w["title"].lower() or search.lower() in w["phase"].lower()]
        if phase_filter != "All":
            wis = [w for w in wis if w["phase"] == phase_filter]
        if status_filter == "Validated":
            wis = [w for w in wis if w.get("validated")]
        elif status_filter == "Not Validated":
            wis = [w for w in wis if not w.get("validated")]
        
        st.markdown(f"**{len(wis)} WIs found**")
        
        for wi in wis:
            ws = get_wi_stats(wi["id"])
            pct = round(ws["done"]/ws["total"]*100) if ws["total"] else 0
            validated_tag = " 🔵 Validated" if wi.get("validated") else ""
            
            with st.expander(f"{'✅' if wi.get('validated') else '📄'} {wi['title']}{validated_tag}  —  {wi['phase']}  ({pct}% complete)"):
                c1, c2, c3 = st.columns([2,1,1])
                with c1:
                    st.markdown(f"**Navigation:** `{wi['nav']}`")
                    st.markdown(f"**Created:** {wi.get('created','—')}")
                with c2:
                    st.metric("Completed", ws["done"])
                    st.metric("In Progress", ws["prog"])
                with c3:
                    st.metric("Not Started", ws["none"])
                    avg_s = sum(ws["scores"])/len(ws["scores"]) if ws["scores"] else 0
                    st.metric("Avg Score", f"{avg_s:.1f}⭐" if avg_s else "—")
                
                # Per-binôme table for this WI
                active_b = [b for b in data["binomes"] if b["active"]]
                rows = []
                for b in active_b:
                    a = data["assignments"].get(str(wi["id"]),{}).get(str(b["id"]),{})
                    rows.append({
                        "Binôme": b["name"], "Members": b["members"],
                        "Status": a.get("status","Not Started"),
                        "Score": a.get("score",0) or 0,
                        "Notes": a.get("notes",""),
                        "Last Update": a.get("updated","")[:10] if a.get("updated") else "—"
                    })
                df_b = pd.DataFrame(rows)
                st.dataframe(df_b, use_container_width=True, hide_index=True,
                             column_config={
                                 "Status": st.column_config.SelectboxColumn("Status", options=STATUS_OPTS),
                                 "Score": st.column_config.NumberColumn("Score ⭐", min_value=0, max_value=5, step=1),
                             })
                
                # Edit & Delete
                ec1, ec2, ec3 = st.columns([1,1,2])
                with ec1:
                    if st.button(f"✏️ Edit", key=f"edit_{wi['id']}"):
                        st.session_state[f"editing_{wi['id']}"] = True
                with ec2:
                    if st.button(f"🗑️ Delete", key=f"del_{wi['id']}", type="secondary"):
                        st.session_state[f"confirm_del_{wi['id']}"] = True
                
                if st.session_state.get(f"confirm_del_{wi['id']}"):
                    st.warning(f"Confirm delete **{wi['title']}**?")
                    dc1, dc2 = st.columns(2)
                    with dc1:
                        if st.button("Yes, delete", key=f"yes_del_{wi['id']}", type="primary"):
                            data["wis"] = [w for w in data["wis"] if w["id"] != wi["id"]]
                            data["assignments"].pop(str(wi["id"]), None)
                            save_data(data)
                            st.success("Deleted!")
                            st.rerun()
                    with dc2:
                        if st.button("Cancel", key=f"no_del_{wi['id']}"):
                            st.session_state[f"confirm_del_{wi['id']}"] = False
                
                if st.session_state.get(f"editing_{wi['id']}"):
                    with st.form(f"edit_form_{wi['id']}"):
                        new_title = st.text_input("Title", value=wi["title"])
                        new_phase = st.selectbox("Phase", PHASES, index=PHASES.index(wi["phase"]) if wi["phase"] in PHASES else 0)
                        new_nav   = st.text_input("Navigation", value=wi["nav"])
                        if st.form_submit_button("💾 Save changes"):
                            for w in data["wis"]:
                                if w["id"] == wi["id"]:
                                    w["title"] = new_title
                                    w["phase"] = new_phase
                                    w["nav"]   = new_nav
                            save_data(data)
                            st.session_state[f"editing_{wi['id']}"] = False
                            st.success("Updated!")
                            st.rerun()
    
    with tab2:
        st.markdown("#### ➕ Add a New WI Subject")
        with st.form("add_wi_form"):
            new_title = st.text_input("WI Title *", placeholder="e.g. WI: Create Discharge List")
            c1, c2 = st.columns(2)
            with c1:
                new_phase = st.selectbox("Phase / Category", PHASES)
            with c2:
                new_date = st.date_input("Date", value=date.today())
            new_nav = st.text_input("Navigation Path", placeholder="CATOS Home → Module → Feature")
            
            st.markdown("**Assign to binômes:**")
            active_b = [b for b in data["binomes"] if b["active"]]
            cols = st.columns(4)
            checked = {}
            for idx, b in enumerate(active_b):
                with cols[idx % 4]:
                    checked[b["id"]] = st.checkbox(f"{b['name']}\n{b['members']}", value=True, key=f"chk_new_{b['id']}")
            
            submitted = st.form_submit_button("✅ Add WI", use_container_width=True, type="primary")
            if submitted:
                if not new_title.strip():
                    st.error("WI Title is required.")
                else:
                    new_id = max([w["id"] for w in data["wis"]], default=0) + 1
                    title_clean = new_title.strip()
                    if not title_clean.startswith("WI:"):
                        title_clean = "WI: " + title_clean
                    data["wis"].append({
                        "id": new_id, "title": title_clean, "phase": new_phase,
                        "nav": new_nav, "created": str(new_date), "validated": False
                    })
                    data["assignments"][str(new_id)] = {}
                    for b in active_b:
                        if checked.get(b["id"]):
                            data["assignments"][str(new_id)][str(b["id"])] = {
                                "status": "Not Started", "score": 0, "notes": "", "updated": ""
                            }
                    save_data(data)
                    st.success(f"✅ WI **{title_clean}** added successfully!")
                    st.rerun()


def page_binomes():
    st.markdown("<div class='section-hdr'>👥 Binôme Management</div>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["👥 View & Update", "➕ Manage Binômes"])
    
    with tab1:
        active_b = [b for b in data["binomes"] if b["active"]]
        selected_b = st.selectbox("Select Binôme", [b["name"] for b in active_b])
        b_obj = next(b for b in active_b if b["name"] == selected_b)
        
        s = get_binome_stats(b_obj["id"])
        pct = round(s["done"]/s["total"]*100) if s["total"] else 0
        
        st.markdown(f"""
        <div style='background:#EFF6FF; border-radius:12px; padding:16px 20px; margin-bottom:16px; display:flex; gap:30px; align-items:center'>
            <div><div style='font-size:22px; font-weight:700; color:#003087'>{selected_b}</div>
            <div style='color:#6B7280; font-size:13px'>{b_obj['members']}</div></div>
            <div style='text-align:center'><div style='font-size:24px; font-weight:700; color:#1D9E75'>{s['done']}</div><div style='font-size:11px; color:#6B7280'>Completed</div></div>
            <div style='text-align:center'><div style='font-size:24px; font-weight:700; color:#F59E0B'>{s['prog']}</div><div style='font-size:11px; color:#6B7280'>In Progress</div></div>
            <div style='text-align:center'><div style='font-size:24px; font-weight:700; color:#EF4444'>{s['none']}</div><div style='font-size:11px; color:#6B7280'>Not Started</div></div>
            <div style='text-align:center'><div style='font-size:24px; font-weight:700; color:#6366F1'>{pct}%</div><div style='font-size:11px; color:#6B7280'>Completion</div></div>
            <div style='text-align:center'><div style='font-size:24px; font-weight:700; color:#BA7517'>{s['avg']:.1f}⭐</div><div style='font-size:11px; color:#6B7280'>Avg Score</div></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**Update WI Progress for this Binôme:**")
        
        for wi in data["wis"]:
            a = data["assignments"].get(str(wi["id"]),{}).get(str(b_obj["id"]),{})
            if not a:
                continue
            
            status_icon = "✅" if a.get("status")=="Completed" else ("🔄" if a.get("status")=="In Progress" else "⭕")
            with st.expander(f"{status_icon} {wi['title']}"):
                uc1, uc2, uc3 = st.columns([2,1,2])
                with uc1:
                    new_status = st.selectbox("Status", STATUS_OPTS,
                                              index=STATUS_OPTS.index(a.get("status","Not Started")),
                                              key=f"st_{wi['id']}_{b_obj['id']}")
                with uc2:
                    new_score = st.number_input("Score (0-5)", min_value=0, max_value=5,
                                                value=int(a.get("score",0)),
                                                key=f"sc_{wi['id']}_{b_obj['id']}")
                with uc3:
                    new_notes = st.text_input("Notes", value=a.get("notes",""),
                                              key=f"no_{wi['id']}_{b_obj['id']}")
                
                if st.button("💾 Save", key=f"save_{wi['id']}_{b_obj['id']}"):
                    data["assignments"][str(wi["id"])][str(b_obj["id"])] = {
                        "status": new_status, "score": new_score,
                        "notes": new_notes, "updated": str(datetime.now())
                    }
                    save_data(data)
                    st.success("Saved!")
                    st.rerun()
    
    with tab2:
        st.markdown("#### Manage Binômes")
        
        # Edit existing
        for b in data["binomes"]:
            with st.expander(f"{'✅' if b['active'] else '❌'} {b['name']} — {b['members']}"):
                with st.form(f"edit_b_{b['id']}"):
                    en1, en2 = st.columns(2)
                    with en1:
                        new_name    = st.text_input("Binôme name", value=b["name"])
                        new_members = st.text_input("Members", value=b["members"])
                    with en2:
                        new_active = st.checkbox("Active", value=b["active"])
                    if st.form_submit_button("Update"):
                        b["name"] = new_name; b["members"] = new_members; b["active"] = new_active
                        save_data(data)
                        st.success("Updated!")
                        st.rerun()
        
        st.markdown("---")
        st.markdown("#### ➕ Add New Binôme")
        with st.form("add_binome"):
            nb1, nb2 = st.columns(2)
            with nb1:
                b_name    = st.text_input("Binôme name", placeholder="e.g. Binôme 9")
            with nb2:
                b_members = st.text_input("Members", placeholder="e.g. Ali & Mounir")
            if st.form_submit_button("Add Binôme", type="primary"):
                if b_name:
                    new_bid = max([b["id"] for b in data["binomes"]], default=0) + 1
                    data["binomes"].append({"id": new_bid, "name": b_name, "members": b_members, "active": True})
                    # Assign existing WIs to new binôme
                    for wi in data["wis"]:
                        data["assignments"].setdefault(str(wi["id"]),{})[str(new_bid)] = {
                            "status":"Not Started","score":0,"notes":"","updated":""
                        }
                    save_data(data)
                    st.success(f"Added {b_name}!")
                    st.rerun()


def page_validate():
    st.markdown("<div class='section-hdr'>✅ Validate Work Instructions</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='alert-info' style='margin-bottom:16px'>
        🔒 Manager only: Validate a WI once all binômes have completed and scored it satisfactorily.
    </div>
    """, unsafe_allow_html=True)
    
    active_b = [b for b in data["binomes"] if b["active"]]
    
    for wi in data["wis"]:
        ws = get_wi_stats(wi["id"])
        pct = round(ws["done"]/ws["total"]*100) if ws["total"] else 0
        avg = sum(ws["scores"])/len(ws["scores"]) if ws["scores"] else 0
        is_validated = wi.get("validated", False)
        
        color = "#D1FAE5" if is_validated else ("#FEF3C7" if pct >= 50 else "#FEE2E2")
        icon  = "✅" if is_validated else ("🔶" if pct >= 50 else "⭕")
        
        with st.expander(f"{icon} {wi['title']}  —  {pct}% done  —  Avg score: {avg:.1f}⭐"):
            vc1, vc2, vc3, vc4 = st.columns(4)
            vc1.metric("Completed", ws["done"])
            vc2.metric("In Progress", ws["prog"])
            vc3.metric("Not Started", ws["none"])
            vc4.metric("Avg Score", f"{avg:.1f}" if avg else "—")
            
            # Per-binôme status
            rows = []
            for b in active_b:
                a = data["assignments"].get(str(wi["id"]),{}).get(str(b["id"]),{})
                rows.append({
                    "Binôme": b["name"], "Status": a.get("status","Not Started"),
                    "Score": a.get("score",0), "Notes": a.get("notes",""),
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            
            st.markdown("---")
            val_c1, val_c2 = st.columns([3,1])
            with val_c1:
                if is_validated:
                    st.markdown(f"<div class='alert-success'>✅ This WI has been validated by manager.</div>", unsafe_allow_html=True)
                else:
                    if pct < 100:
                        st.markdown(f"<div class='alert-warn'>⚠️ {ws['none']} binôme(s) have not completed this WI yet.</div>", unsafe_allow_html=True)
            with val_c2:
                if not is_validated:
                    if st.button(f"✅ Validate WI", key=f"val_{wi['id']}", type="primary"):
                        for w in data["wis"]:
                            if w["id"] == wi["id"]:
                                w["validated"] = True
                                w["validated_date"] = str(date.today())
                        save_data(data)
                        st.success("WI validated!")
                        st.rerun()
                else:
                    if st.button(f"🔓 Unvalidate", key=f"unval_{wi['id']}"):
                        for w in data["wis"]:
                            if w["id"] == wi["id"]:
                                w["validated"] = False
                        save_data(data)
                        st.rerun()


def page_analytics():
    st.markdown("<div class='section-hdr'>📈 Analytics & Charts</div>", unsafe_allow_html=True)
    
    active_b = [b for b in data["binomes"] if b["active"]]
    
    tab1, tab2, tab3 = st.tabs(["🏆 Ranking", "📊 Heatmap", "📉 Score Analysis"])
    
    with tab1:
        st.markdown("#### 🏆 Binôme Ranking — Manager View")
        ranked = []
        for b in active_b:
            s = get_binome_stats(b["id"])
            pct = round(s["done"]/s["total"]*100) if s["total"] else 0
            ranked.append({**b, **s, "pct": pct})
        ranked.sort(key=lambda x: (x["pct"], x["avg"]), reverse=True)
        
        medals = ["🥇", "🥈", "🥉"] + [str(i) for i in range(4, 20)]
        for i, b in enumerate(ranked):
            bar_pct = b["pct"]
            perf = "🏆 Champion" if bar_pct==100 else ("⭐ Excellent" if bar_pct>=75 else ("✅ Good" if bar_pct>=50 else "📈 Improving"))
            st.markdown(f"""
            <div style='background:{"#F0FDF4" if i==0 else "white"}; border:1px solid {"#22C55E" if i==0 else "#E5E7EB"};
                        border-radius:10px; padding:12px 16px; margin-bottom:8px;
                        display:flex; align-items:center; gap:16px'>
                <div style='font-size:22px; min-width:32px'>{medals[i]}</div>
                <div style='flex:1'>
                    <div style='font-weight:600; color:#111827'>{b['name']} — {b['members']}</div>
                    <div style='display:flex; align-items:center; gap:8px; margin-top:4px'>
                        <div class='prog-bar-wrap' style='flex:1; height:6px'>
                            <div class='prog-bar-fill' style='width:{bar_pct}%; background:{"#22C55E" if i==0 else "#003087"}'></div>
                        </div>
                        <span style='font-size:12px; color:#6B7280'>{bar_pct}%</span>
                    </div>
                </div>
                <div style='text-align:center; min-width:60px'>
                    <div style='font-size:16px; font-weight:700; color:#F59E0B'>{b['avg']:.1f}⭐</div>
                    <div style='font-size:10px; color:#9CA3AF'>avg score</div>
                </div>
                <div style='min-width:90px; text-align:right'>
                    <span style='background:#EFF6FF; color:#1E40AF; padding:4px 10px; border-radius:20px; font-size:11px; font-weight:600'>{perf}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("#### 📊 Completion Heatmap")
        
        status_map = {"Completed": 3, "In Progress": 2, "Not Started": 1, None: 0}
        matrix = []
        wi_labels = [w["title"].replace("WI:","").strip()[:25] for w in data["wis"]]
        b_labels   = [b["name"] for b in active_b]
        
        for wi in data["wis"]:
            row = []
            for b in active_b:
                a = data["assignments"].get(str(wi["id"]),{}).get(str(b["id"]),{})
                row.append(status_map.get(a.get("status"), 0))
            matrix.append(row)
        
        if matrix:
            fig = go.Figure(data=go.Heatmap(
                z=matrix, x=b_labels, y=wi_labels,
                colorscale=[[0,"#F3F4F6"],[0.33,"#FEE2E2"],[0.66,"#FEF3C7"],[1,"#D1FAE5"]],
                text=[[["—","Not Started","In Progress","Completed"][v] for v in row] for row in matrix],
                texttemplate="%{text}", showscale=False,
                hovertemplate="WI: %{y}<br>%{x}: %{text}<extra></extra>"
            ))
            fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("#### 📉 Score Distribution by Binôme")
        score_rows = []
        for b in active_b:
            for wi in data["wis"]:
                a = data["assignments"].get(str(wi["id"]),{}).get(str(b["id"]),{})
                sc = a.get("score", 0)
                if sc and sc > 0:
                    score_rows.append({"Binôme": b["name"], "WI": wi["title"].replace("WI:","").strip(), "Score": sc})
        
        if score_rows:
            df_sc = pd.DataFrame(score_rows)
            fig = px.box(df_sc, x="Binôme", y="Score", color="Binôme",
                         points="all", height=320,
                         color_discrete_sequence=px.colors.qualitative.Bold)
            fig.update_layout(showlegend=False, margin=dict(l=0,r=0,t=10,b=0),
                              plot_bgcolor="white", paper_bgcolor="white",
                              yaxis=dict(range=[0,5.5], dtick=1))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No scores recorded yet.")


def page_import_export():
    st.markdown("<div class='section-hdr'>📥 Import & Export</div>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📤 Export to Excel", "📥 Import from Excel", "💾 JSON Backup"])
    
    with tab1:
        st.markdown("#### Export current data to Excel")
        active_b = [b for b in data["binomes"] if b["active"]]
        
        if st.button("📊 Generate Excel Report", type="primary"):
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
            from openpyxl.utils import get_column_letter
            
            wb = openpyxl.Workbook()
            
            # Sheet 1: Progress Matrix
            ws = wb.active; ws.title = "Progress Matrix"
            ws.column_dimensions["A"].width = 28
            
            # Header
            ws.cell(1,1,"WMCT – WI Progress Matrix").font = Font(bold=True,size=14,color="FFFFFF",name="Arial")
            ws.cell(1,1).fill = PatternFill("solid",fgColor="00245D")
            ws.merge_cells(f"A1:{get_column_letter(len(active_b)*3+1)}1")
            ws.row_dimensions[1].height = 28
            
            # Column headers
            ws.cell(2,1,"WI Title").font = Font(bold=True,color="FFFFFF",name="Arial")
            ws.cell(2,1).fill = PatternFill("solid",fgColor="003087")
            for i, b in enumerate(active_b):
                col = 2 + i*3
                ws.merge_cells(start_row=2,start_column=col,end_row=2,end_column=col+2)
                c = ws.cell(2,col,f"{b['name']} | {b['members']}")
                c.font = Font(bold=True,color="FFFFFF",name="Arial")
                c.fill = PatternFill("solid",fgColor="185FA5" if i%2==0 else "003087")
                c.alignment = Alignment(horizontal="center")
                ws.cell(3,col,"Status").font = Font(bold=True,color="FFFFFF",size=8,name="Arial")
                ws.cell(3,col).fill = PatternFill("solid",fgColor="185FA5" if i%2==0 else "003087")
                ws.cell(3,col+1,"Score").font = Font(bold=True,color="FFFFFF",size=8,name="Arial")
                ws.cell(3,col+1).fill = PatternFill("solid",fgColor="185FA5" if i%2==0 else "003087")
                ws.cell(3,col+2,"Notes").font = Font(bold=True,color="FFFFFF",size=8,name="Arial")
                ws.cell(3,col+2).fill = PatternFill("solid",fgColor="185FA5" if i%2==0 else "003087")
            
            for j, wi in enumerate(data["wis"]):
                row = j+4
                ws.cell(row,1,wi["title"]).font = Font(bold=True,size=9,name="Arial")
                for i, b in enumerate(active_b):
                    col = 2+i*3
                    a = data["assignments"].get(str(wi["id"]),{}).get(str(b["id"]),{})
                    status = a.get("status","Not Started")
                    score  = a.get("score",0)
                    notes  = a.get("notes","")
                    ws.cell(row,col,status)
                    ws.cell(row,col+1,score or "")
                    ws.cell(row,col+2,notes)
                    # Color by status
                    fc = "D1FAE5" if status=="Completed" else ("FEF3C7" if status=="In Progress" else "FEE2E2")
                    ws.cell(row,col).fill = PatternFill("solid",fgColor=fc)
                ws.row_dimensions[row].height = 16
            
            # Sheet 2: Ranking
            ws2 = wb.create_sheet("Ranking")
            ws2.column_dimensions["A"].width = 3
            ws2.column_dimensions["B"].width = 16
            ws2.column_dimensions["C"].width = 20
            ws2.column_dimensions["D"].width = 12
            ws2.column_dimensions["E"].width = 12
            ws2.column_dimensions["F"].width = 12
            
            hdrs = ["Rank","Binôme","Members","Done","In Progress","Completion %","Avg Score"]
            for i, h in enumerate(hdrs):
                c = ws2.cell(2,i+2,h)
                c.font = Font(bold=True,color="FFFFFF",name="Arial")
                c.fill = PatternFill("solid",fgColor="003087")
                c.alignment = Alignment(horizontal="center")
            
            ranked = []
            for b in active_b:
                s = get_binome_stats(b["id"])
                pct2 = round(s["done"]/s["total"]*100) if s["total"] else 0
                ranked.append({**b,**s,"pct":pct2})
            ranked.sort(key=lambda x:(x["pct"],x["avg"]),reverse=True)
            
            medals = ["🥇","🥈","🥉"]+[str(i) for i in range(4,20)]
            for i, b in enumerate(ranked):
                r = i+3
                ws2.cell(r,2,medals[i]).alignment = Alignment(horizontal="center")
                ws2.cell(r,3,b["name"]).font = Font(bold=True,name="Arial")
                ws2.cell(r,4,b["members"]).font = Font(size=9,name="Arial")
                ws2.cell(r,5,b["done"]).alignment = Alignment(horizontal="center")
                ws2.cell(r,6,b["prog"]).alignment = Alignment(horizontal="center")
                pct_v = b["pct"]/100
                ws2.cell(r,7,pct_v).number_format="0%"
                ws2.cell(r,7).alignment = Alignment(horizontal="center")
                ws2.cell(r,8,round(b["avg"],1) if b["avg"] else 0).number_format="0.0"
                ws2.cell(r,8).alignment = Alignment(horizontal="center")
                ws2.row_dimensions[r].height = 18
            
            buf = io.BytesIO()
            wb.save(buf)
            buf.seek(0)
            
            st.download_button(
                "⬇️ Download Excel Report",
                data=buf,
                file_name=f"WMCT_WI_Progress_{date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    with tab2:
        st.markdown("#### Import WI Progress from Excel")
        st.markdown("""
        <div class='alert-info'>
            Expected format: Excel with columns <b>WI_Title, Binome_Name, Status, Score, Notes</b>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded = st.file_uploader("Upload Excel file", type=["xlsx","xls"])
        if uploaded:
            try:
                df_imp = pd.read_excel(uploaded)
                st.dataframe(df_imp.head(10), use_container_width=True)
                
                required = {"WI_Title","Binome_Name","Status","Score","Notes"}
                if required.issubset(set(df_imp.columns)):
                    if st.button("📥 Import Data", type="primary"):
                        imported = 0
                        for _, row in df_imp.iterrows():
                            wi_match = next((w for w in data["wis"] if w["title"].lower() == str(row["WI_Title"]).lower()), None)
                            b_match  = next((b for b in data["binomes"] if b["name"].lower() == str(row["Binome_Name"]).lower()), None)
                            if wi_match and b_match:
                                data["assignments"].setdefault(str(wi_match["id"]),{})[str(b_match["id"])] = {
                                    "status": str(row["Status"]) if str(row["Status"]) in STATUS_OPTS else "Not Started",
                                    "score": int(row["Score"]) if pd.notna(row["Score"]) else 0,
                                    "notes": str(row["Notes"]) if pd.notna(row["Notes"]) else "",
                                    "updated": str(datetime.now())
                                }
                                imported += 1
                        save_data(data)
                        st.success(f"✅ Imported {imported} records!")
                else:
                    st.error(f"Missing columns. Found: {list(df_imp.columns)}")
            except Exception as e:
                st.error(f"Error reading file: {e}")
        
        st.markdown("---")
        st.markdown("##### Template Download")
        template_rows = []
        active_b = [b for b in data["binomes"] if b["active"]]
        for wi in data["wis"]:
            for b in active_b:
                template_rows.append({"WI_Title": wi["title"], "Binome_Name": b["name"],
                                       "Status": "Not Started", "Score": 0, "Notes": ""})
        df_tpl = pd.DataFrame(template_rows)
        buf_tpl = io.BytesIO()
        df_tpl.to_excel(buf_tpl, index=False)
        buf_tpl.seek(0)
        st.download_button("⬇️ Download Import Template", data=buf_tpl,
                           file_name="WMCT_Import_Template.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    with tab3:
        st.markdown("#### JSON Backup & Restore")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**📤 Export backup**")
            json_str = json.dumps(data, indent=2, default=str)
            st.download_button("⬇️ Download JSON Backup", data=json_str,
                               file_name=f"wmct_backup_{date.today()}.json",
                               mime="application/json", use_container_width=True)
        with c2:
            st.markdown("**📥 Restore from backup**")
            json_file = st.file_uploader("Upload JSON backup", type=["json"])
            if json_file:
                if st.button("Restore", type="primary"):
                    try:
                        restored = json.load(json_file)
                        with open(DATA_FILE,"w") as f:
                            json.dump(restored, f, indent=2)
                        st.session_state.data = restored
                        st.success("Restored!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")


def page_my_progress():
    user = st.session_state.user
    bid  = user.get("binome_id")
    if not bid:
        st.warning("No binôme assigned to your account.")
        return
    
    b_obj = next((b for b in data["binomes"] if b["id"] == bid), None)
    if not b_obj:
        st.warning("Binôme not found.")
        return
    
    s   = get_binome_stats(bid)
    pct = round(s["done"]/s["total"]*100) if s["total"] else 0
    
    st.markdown(f"""
    <div class='top-bar'>
        <div>
            <div class='top-bar-title'>👥 {b_obj['name']} — {b_obj['members']}</div>
            <div class='top-bar-sub'>MY WI PROGRESS · CATOS TRAINING PHASE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    k1, k2, k3, k4 = st.columns(4)
    for col, val, label, color in [
        (k1, s["done"],  "Completed",  "#1D9E75"),
        (k2, s["prog"],  "In Progress","#BA7517"),
        (k3, s["none"],  "Not Started","#E24B4A"),
        (k4, f"{pct}%",  "Completion", "#185FA5"),
    ]:
        with col:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>{label}</div>
                <div class='kpi-number' style='color:{color}'>{val}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-hdr'>📝 My Work Instructions</div>", unsafe_allow_html=True)
    
    for wi in data["wis"]:
        a = data["assignments"].get(str(wi["id"]),{}).get(str(bid),{})
        if not a:
            continue
        status = a.get("status","Not Started")
        icon = "✅" if status=="Completed" else ("🔄" if status=="In Progress" else "⭕")
        validated_tag = " 🔵 (Validated by Manager)" if wi.get("validated") else ""
        
        with st.expander(f"{icon} {wi['title']}{validated_tag}"):
            st.markdown(f"**Phase:** {wi['phase']}  |  **Navigation:** `{wi['nav']}`")
            
            with st.form(f"my_form_{wi['id']}"):
                fc1, fc2, fc3 = st.columns([2,1,2])
                with fc1:
                    new_status = st.selectbox("My Status", STATUS_OPTS,
                                              index=STATUS_OPTS.index(status), key=f"ms_{wi['id']}")
                with fc2:
                    new_score = st.number_input("Score (0-5)", 0, 5,
                                                value=int(a.get("score",0)), key=f"msc_{wi['id']}")
                with fc3:
                    new_notes = st.text_input("Notes / Comments", value=a.get("notes",""), key=f"mn_{wi['id']}")
                
                if st.form_submit_button("💾 Update My Progress", use_container_width=True, type="primary"):
                    data["assignments"][str(wi["id"])][str(bid)] = {
                        "status": new_status, "score": new_score,
                        "notes": new_notes, "updated": str(datetime.now())
                    }
                    save_data(data)
                    st.success("Progress saved!")
                    st.rerun()


def page_settings():
    st.markdown("<div class='section-hdr'>⚙️ Settings</div>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["👤 User Management", "🔑 Reset Password"])
    
    with tab1:
        st.markdown("#### Users")
        users = data.get("users", [])
        for u in users:
            with st.expander(f"{'🏢' if u['role']=='manager' else '👥'} {u['username']} — {u['role']}"):
                with st.form(f"edit_user_{u['username']}"):
                    ur1, ur2 = st.columns(2)
                    with ur1:
                        new_role = st.selectbox("Role", ["manager","binome"],
                                                index=0 if u["role"]=="manager" else 1)
                    with ur2:
                        binomes_opts = [None] + [b["id"] for b in data["binomes"] if b["active"]]
                        binomes_labels = ["None"] + [b["name"] for b in data["binomes"] if b["active"]]
                        idx = binomes_opts.index(u.get("binome_id")) if u.get("binome_id") in binomes_opts else 0
                        new_b_name = st.selectbox("Binôme", binomes_labels, index=idx)
                        new_bid2 = binomes_opts[binomes_labels.index(new_b_name)]
                    new_pw = st.text_input("New password (leave blank to keep)", type="password")
                    if st.form_submit_button("Update"):
                        u["role"] = new_role; u["binome_id"] = new_bid2
                        if new_pw: u["password"] = _hash(new_pw)
                        save_data(data)
                        st.success("Updated!")
        
        st.markdown("---")
        st.markdown("#### ➕ Add User")
        with st.form("add_user"):
            au1, au2 = st.columns(2)
            with au1:
                new_uname = st.text_input("Username")
                new_upw   = st.text_input("Password", type="password")
            with au2:
                new_urole = st.selectbox("Role", ["manager","binome"])
                b_opts2    = [None] + [b["id"] for b in data["binomes"] if b["active"]]
                b_lbls2    = ["None"] + [b["name"] for b in data["binomes"] if b["active"]]
                new_ub_lbl = st.selectbox("Binôme", b_lbls2)
                new_ubid   = b_opts2[b_lbls2.index(new_ub_lbl)]
            if st.form_submit_button("Add User", type="primary"):
                if new_uname and new_upw:
                    data["users"].append({"username":new_uname,"password":_hash(new_upw),
                                          "role":new_urole,"binome_id":new_ubid})
                    save_data(data)
                    st.success(f"User {new_uname} added!")
                    st.rerun()
    
    with tab2:
        st.markdown("#### 🔑 Change My Password")
        with st.form("change_pw"):
            old_pw  = st.text_input("Current password", type="password")
            new_pw1 = st.text_input("New password", type="password")
            new_pw2 = st.text_input("Confirm new password", type="password")
            if st.form_submit_button("Change Password", type="primary"):
                user = st.session_state.user
                if user["password"] != _hash(old_pw):
                    st.error("Current password incorrect.")
                elif new_pw1 != new_pw2:
                    st.error("New passwords don't match.")
                elif len(new_pw1) < 4:
                    st.error("Password too short.")
                else:
                    for u in data["users"]:
                        if u["username"] == user["username"]:
                            u["password"] = _hash(new_pw1)
                    save_data(data)
                    st.success("Password changed!")


# ── Main router ───────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    login_page()
else:
    render_sidebar()
    
    page = st.session_state.page
    user = st.session_state.user
    is_manager = user["role"] == "manager"
    
    if page == "Dashboard":
        page_dashboard()
    elif page == "WI Management" and is_manager:
        page_wi_management()
    elif page == "Binômes" and is_manager:
        page_binomes()
    elif page == "Validate WIs" and is_manager:
        page_validate()
    elif page == "Analytics" and is_manager:
        page_analytics()
    elif page == "Import / Export":
        page_import_export()
    elif page == "Settings" and is_manager:
        page_settings()
    elif page == "My Progress":
        page_my_progress()
    else:
        st.warning("Page not found or insufficient permissions.")
