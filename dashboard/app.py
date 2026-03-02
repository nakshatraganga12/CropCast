import streamlit as st
import pandas as pd
import plotly.express as px
import statsmodels.formula.api as smf
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

st.set_page_config(page_title="CropCast", layout="wide")

# -----------------------------
# Load Data
# -----------------------------
panel = pd.read_csv("../data/processed/merged_panel.csv")

st.title("🌾 CropCast — Climate Sensitivity Explorer")
st.markdown("State-level rainfall–yield modeling (2000–2019)")

# -----------------------------
# Sidebar
# -----------------------------
state = st.sidebar.selectbox(
    "Select State",
    sorted(panel["State"].unique())
)

# -----------------------------
# Feature Engineering
# -----------------------------
panel["Rain_Mean_State"] = panel.groupby("State")["Kharif_Rain_mm"].transform("mean")
panel["Rain_Std_State"] = panel.groupby("State")["Kharif_Rain_mm"].transform("std")
panel["Rain_Z"] = (
    panel["Kharif_Rain_mm"] - panel["Rain_Mean_State"]
) / panel["Rain_Std_State"]

df = panel[panel["State"] == state]

# -----------------------------
# Regression
# -----------------------------
model = smf.ols("Yield_t_ha ~ Rain_Z", data=df).fit()
beta = model.params["Rain_Z"]
pval = model.pvalues["Rain_Z"]
r2 = model.rsquared

# -----------------------------
# Visual Layout
# -----------------------------
st.markdown("## 📈 Climate Response Analysis")

col1, col2 = st.columns(2)

with col1:
    fig1 = px.line(
        df,
        x="Year",
        y=["Kharif_Rain_mm", "Yield_t_ha"],
        title=f"{state}: Rainfall vs Yield Trend",
        markers=True
    )
    fig1.update_layout(legend_title_text="")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.scatter(
        df,
        x="Rain_Z",
        y="Yield_t_ha",
        trendline="ols",
        title="Rainfall Shock vs Yield Response"
    )
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# Sensitivity Metrics
# -----------------------------
st.markdown("## 📊 Rainfall Sensitivity Metrics")

m1, m2, m3 = st.columns(3)

# Color logic
beta_color = "normal"
if beta > 0:
    beta_color = "normal"
else:
    beta_color = "inverse"

significance = "Significant" if pval < 0.05 else "Not Significant"

with m1:
    st.metric(
        label="β (Yield change per 1 SD rainfall)",
        value=f"{beta:.3f} t/ha",
        delta="Positive impact" if beta > 0 else "Negative impact"
    )

with m2:
    st.metric(
        label="p-value",
        value=f"{pval:.4f}",
        delta=significance
    )

with m3:
    st.metric(
        label="Model R²",
        value=f"{r2:.3f}"
    )

# Interpretation box
if pval < 0.05:
    st.success(f"Rainfall shocks significantly affect crop yield in {state}.")
else:
    st.info(f"No statistically significant rainfall-yield relationship detected in {state}.")

# -----------------------------
# Clustering
# -----------------------------
st.markdown("## 🧭 Regional Climate-Yield Clustering")

state_summary = panel.groupby("State").agg(
    Rain_Variability=("Kharif_Rain_mm", "std"),
    Yield_Variability=("Yield_t_ha", "std"),
    Mean_Yield=("Yield_t_ha", "mean")
).reset_index()

features = state_summary[
    ["Rain_Variability", "Yield_Variability", "Mean_Yield"]
]

scaled = StandardScaler().fit_transform(features)
kmeans = KMeans(n_clusters=3, random_state=42)
state_summary["Cluster"] = kmeans.fit_predict(scaled)

cluster_id = state_summary[
    state_summary["State"] == state
]["Cluster"].values[0]

c1, c2 = st.columns([1, 3])

with c1:
    st.metric("Cluster ID", cluster_id)

with c2:
    fig_cluster = px.scatter(
        state_summary,
        x="Rain_Variability",
        y="Yield_Variability",
        color=state_summary["Cluster"].astype(str),
        hover_name="State",
        title="State Clusters (Rain vs Yield Volatility)"
    )
    st.plotly_chart(fig_cluster, use_container_width=True)
# -----------------------------
# Cluster Interpretation
# -----------------------------
st.markdown("## What Does This Cluster Mean?")

cluster_summary = state_summary.groupby("Cluster").agg(
    Avg_Rain_Variability=("Rain_Variability", "mean"),
    Avg_Yield_Variability=("Yield_Variability", "mean"),
    Avg_Mean_Yield=("Mean_Yield", "mean"),
    States_Count=("State", "count")
).reset_index()

selected_cluster_info = cluster_summary[
    cluster_summary["Cluster"] == cluster_id
].iloc[0]

# Interpretation Logic
if selected_cluster_info["Avg_Rain_Variability"] > cluster_summary["Avg_Rain_Variability"].mean():
    rain_desc = "high rainfall variability"
else:
    rain_desc = "low rainfall variability"

if selected_cluster_info["Avg_Yield_Variability"] > cluster_summary["Avg_Yield_Variability"].mean():
    yield_desc = "high yield volatility"
else:
    yield_desc = "stable yield patterns"

st.info(
    f"""
    **Cluster {cluster_id} Interpretation:**

    States in this cluster typically exhibit **{rain_desc}** and 
    **{yield_desc}**.

    This suggests that agricultural outcomes in these regions are 
    {'more climate-sensitive' if rain_desc == 'high rainfall variability' else 'relatively climate-resilient'}.

    Number of states in this cluster: {int(selected_cluster_info['States_Count'])}
    """
)

# Optional: Show Cluster Comparison Table
st.markdown("### 📋 Cluster Profile Comparison")
st.dataframe(cluster_summary.style.format({
    "Avg_Rain_Variability": "{:.2f}",
    "Avg_Yield_Variability": "{:.2f}",
    "Avg_Mean_Yield": "{:.2f}"
}))