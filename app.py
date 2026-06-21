import streamlit as st
import pandas as pd
import pulp

# --- PAGE CONFIG ---
st.set_page_config(page_title="Fantasy Optimizer", layout="wide", page_icon="🏆")

# --- SENIOR UI: CUSTOM CSS ---
st.markdown("""
    <style>
    /* Main Background and Font */
    .main { background-color: #0e1117; color: #ffffff; }
    
    /* Card Styling */
    .player-card {
        background-color: #1f2937;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
    }
    .player-name { font-size: 18px; font-weight: bold; color: #f9fafb; }
    .player-meta { font-size: 14px; color: #9ca3af; }
    
    /* Metric Styling */
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 12px;
    }
    
    /* Button Styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #ff4b4b 0%, #ff7676 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 12px;
        border-radius: 8px;
        transition: 0.3s;
    }
    .stButton>button:hover { opacity: 0.8; transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# --- 2026 DATA ENGINE ---
def get_squads():
    return {
        "Mumbai Indians (MI)": [
            ["Suryakumar Yadav", "BAT", 95, 11.0], ["Rohit Sharma", "BAT", 113, 10.5],
            ["Hardik Pandya", "AR", 88, 10.0], ["Jasprit Bumrah", "BOWL", 98, 11.0],
            ["Ishan Kishan", "WK", 95, 9.5], ["Tilak Varma", "BAT", 85, 9.0],
            ["Tim David", "BAT", 86, 8.5], ["Anshul Kamboj", "BOWL", 82, 8.0],
            ["Rashid Khan", "BOWL", 94, 10.5], ["N. Wadhera", "BAT", 80, 8.0]
        ],
        "Royal Challengers Bengaluru (RCB)": [
            ["Virat Kohli", "BAT", 97, 11.0], ["Rajat Patidar", "BAT", 87, 9.5],
            ["Phil Salt", "WK", 91, 10.0], ["Mohammed Siraj", "BOWL", 86, 9.5],
            ["Will Jacks", "AR", 85, 9.0], ["Yash Dayal", "BOWL", 79, 8.0],
            ["V. Vyshak", "BOWL", 84, 8.5], ["Krunal Pandya", "AR", 81, 8.5],
            ["Swapnil Singh", "AR", 78, 8.0], ["F. du Plessis", "BAT", 82, 9.0]
        ],
        "Punjab Kings (PBKS)": [
            ["Shreyas Iyer", "BAT", 89, 10.0], ["Arshdeep Singh", "BOWL", 92, 10.0],
            ["Shashank Singh", "BAT", 90, 8.5], ["Prabhsimran Singh", "WK", 82, 8.5],
            ["Harpreet Brar", "BOWL", 79, 8.0], ["Marcus Stoinis", "AR", 88, 10.0],
            ["Sam Curran", "AR", 85, 9.5], ["Kagiso Rabada", "BOWL", 88, 9.5],
            ["Ashutosh Sharma", "BAT", 81, 8.0], ["Harshal Patel", "BOWL", 84, 9.0]
        ],
        "Rajasthan Royals (RR)": [
            ["Yashasvi Jaiswal", "BAT", 93, 10.5], ["Riyan Parag", "AR", 91, 10.0],
            ["Ravi Bishnoi", "BOWL", 93, 9.5], ["Dhruv Jurel", "WK", 93, 9.0],
            ["Shimron Hetmyer", "BAT", 82, 9.0], ["Avesh Khan", "BOWL", 85, 9.0],
            ["Trent Boult", "BOWL", 89, 9.5], ["Sandeep Sharma", "BOWL", 80, 8.0],
            ["Nandre Burger", "BOWL", 84, 8.5], ["Sanju Samson", "WK", 90, 10.0]
        ]
    }

# --- OPTIMIZER (BINARY INTEGER PROGRAMMING) ---
def optimize_team(df):
    prob = pulp.LpProblem("DreamTeam", pulp.LpMaximize)
    player_vars = pulp.LpVariable.dicts("P", df.index, cat=pulp.LpBinary)
    prob += pulp.lpSum([df.loc[i, 'points'] * player_vars[i] for i in df.index])
    prob += pulp.lpSum([player_vars[i] for i in df.index]) == 11
    prob += pulp.lpSum([df.loc[i, 'credits'] * player_vars[i] for i in df.index]) <= 100
    # Role Logic
    prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'WK']) >= 1
    prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'BOWL']) >= 3
    prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'BAT']) >= 3
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    return df.loc[[i for i in df.index if player_vars[i].varValue == 1]]

# --- MAIN APP UI ---
st.title("🏆 AI Fantasy Squad Optimizer")
st.markdown("##### Integer Programming for Match-Winning Lineups (2026 Season)")

squads = get_squads()

# Match Selection
col_sel1, col_sel2 = st.columns(2)
with col_sel1:
    t1 = st.selectbox("Select Home Team", list(squads.keys()), index=0)
with col_sel2:
    t2 = st.selectbox("Select Away Team", list(squads.keys()), index=1)

if t1 == t2:
    st.error("Select two different teams.")
else:
    combined_df = pd.DataFrame(squads[t1] + squads[t2], columns=["name", "role", "points", "credits"])
    
    # 1. Display Squads Section
    with st.expander("👁️ View Full Squad Details", expanded=False):
        st.dataframe(combined_df.sort_values(by="points", ascending=False), use_container_width=True)

    st.divider()

    # 2. Optimized Result Section (THE HERO)
    if st.button("🚀 RUN AI OPTIMIZER"):
        best_11 = optimize_team(combined_df)
        
        # Dashboard Header
        m1, m2, m3 = st.columns(3)
        m1.metric("Projected Points", int(best_11['points'].sum()), delta="AI Max")
        m2.metric("Efficiency", f"{best_11['credits'].sum()}/100", delta="-0.5 Budget")
        m3.metric("Algorithm", "CBC Solver", delta="Optimal")

        st.markdown("### ⭐ THE OPTIMIZED 11")
        
        # Displaying as "Cards" for Senior UI look
        roles = ["WK", "BAT", "AR", "BOWL"]
        for role in roles:
            st.markdown(f"**{role}**")
            role_df = best_11[best_11['role'] == role]
            
            # Create sub-columns for cards
            cols = st.columns(4)
            for i, (_, row) in enumerate(role_df.iterrows()):
                with cols[i % 4]:
                    st.markdown(f"""
                        <div class="player-card">
                            <div class="player-name">{row['name']}</div>
                            <div class="player-meta">{row['role']} • {row['points']} pts • {row['credits']} cr</div>
                        </div>
                    """, unsafe_allow_html=True)
        
        st.balloons()