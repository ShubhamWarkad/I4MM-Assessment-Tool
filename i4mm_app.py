import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import pi

# --- Page setup ---
st.set_page_config(page_title='I4.0 Maturity Assessment (I4MM)', layout='centered')
st.title('🏭 Industry 4.0 Maturity Assessment (I4MM) — Prototype')

st.markdown("""
This interactive tool lets an SME (or consultant) score five dimensions of Industry 4.0 readiness, 
set weights, and compute the **I4.0 Readiness Index (I4RI)**.  
The app also shows a radar chart and gives high-level recommendations.
""")

# --- Dimensions ---
dims = ['Technology', 'Process Integration', 'People & Skills', 'Data & Analytics', 'Strategy & Governance']

st.sidebar.header('Input: Scores and Weights')
st.sidebar.markdown('Scores: 1 (Manual) — 5 (Smart/Autonomous)')

scores = {}
weights = {}
for d in dims:
    scores[d] = st.sidebar.slider(f'{d} — Score (1–5)', min_value=1, max_value=5, value=2, step=1)
    weights[d] = st.sidebar.slider(f'{d} — Weight (importance)', min_value=0.0, max_value=1.0, value=0.2, step=0.05)

# --- Normalize weights ---
w_sum = sum(weights.values())
if w_sum == 0:
    norm_weights = {d: 1/len(dims) for d in dims}
else:
    norm_weights = {d: weights[d]/w_sum for d in dims}

# --- Compute Readiness Index ---
weighted_sum = sum(norm_weights[d] * scores[d] for d in dims)
i4ri = weighted_sum

st.header('Results')
st.metric('I4.0 Readiness Index (I4RI)', f'{i4ri:.2f} / 5.00')

# --- Maturity Levels ---
if i4ri < 1.5:
    level = 'Level 1 — Manual / Basic'
    rec = ['Run awareness sessions', 'Start digital literacy training', 'Basic housekeeping and data recording']
elif i4ri < 2.5:
    level = 'Level 2 — Digital Initiation'
    rec = ['Introduce basic sensors & data logging', 'Standardize processes', 'Start small pilot (single machine)']
elif i4ri < 3.5:
    level = 'Level 3 — Connected Operations'
    rec = ['Integrate machines via IoT', 'Implement simple dashboards', 'Plan MES-lite pilot']
elif i4ri < 4.25:
    level = 'Level 4 — Predictive / Smart'
    rec = ['Deploy predictive maintenance', 'Start analytics for scheduling', 'Train staff on data interpretation']
else:
    level = 'Level 5 — Smart / Autonomous'
    rec = ['Move towards digital twin & AI optimization', 'Continuous improvement culture', 'Share learnings across clusters']

st.write('**Maturity Level:**', level)
st.write('**Top recommendations:**')
for r in rec:
    st.write('-', r)
    
# --- Simulation-Based Performance Insights ---
import os

st.subheader('📊 Simulation-Based Performance Insights')

# Map maturity levels to precomputed simulation CSVs
level_to_csv = {
    'Level 1 — Manual / Basic': 'simulation/precomputed_results/level1_baseline.csv',
    'Level 2 — Digital Initiation': 'simulation/precomputed_results/level1_baseline.csv',
    'Level 3 — Connected Operations': 'simulation/precomputed_results/level3_connected.csv',
    'Level 4 — Predictive / Smart': 'simulation/precomputed_results/level4_predictive.csv',
    'Level 5 — Smart / Autonomous': 'simulation/precomputed_results/level4_predictive.csv'
}

csv_path = level_to_csv.get(level)

if csv_path and os.path.exists(csv_path):
    df_sim = pd.read_csv(csv_path)
    st.success(f"Simulation results for: **{level}**")
    st.write(f"**Average Throughput (units/hour):** {df_sim['throughput_per_hr'].mean():.2f}")
    st.write(f"**Average Lead Time (minutes):** {df_sim['avg_lead_time_min'].mean():.1f}")

    # Show comparison chart
    st.bar_chart(df_sim[['throughput_per_hr', 'avg_lead_time_min']])

    # Show raw data toggle
    with st.expander('See detailed simulation data'):
        st.dataframe(df_sim.head(10))
else:
    st.info('⚠️ Simulation data not available for this maturity level. Run `simulation_runner.py` to generate it.')


# --- Data Table ---
df = pd.DataFrame({
    'Dimension': dims,
    'Score (1-5)': [scores[d] for d in dims],
    'Weight (normalized)': [norm_weights[d] for d in dims]
})
st.subheader('Dimension Scores & Weights')
st.dataframe(df.style.format({'Weight (normalized)': '{:.2f}', 'Score (1-5)': '{:.0f}'}))

# --- Radar Chart ---
def make_radar_chart(categories, values, title='Radar: I4.0 Dimensions'):
    N = len(categories)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]
    vals = values + values[:1]
    fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)
    ax.set_rlabel_position(0)
    ax.set_ylim(0,5)
    ax.plot(angles, vals, linewidth=2)
    ax.fill(angles, vals, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_title(title)
    return fig

values = [scores[d] for d in dims]
fig = make_radar_chart(dims, values, title=f'I4.0 Dimension Scores — I4RI={i4ri:.2f}')
st.pyplot(fig)

st.markdown('---')
st.markdown('**Note:** This is a prototype tool. For real assessments, validate scores with shop-floor data or expert consultation.')
