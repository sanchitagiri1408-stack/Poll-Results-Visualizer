"""Interactive Streamlit dashboard for Poll Results Visualizer."""
from pathlib import Path
import sys
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from src.poll_visualizer import (
    create_synthetic_dataset, clean_poll_data, analyze_poll,
    REQUIRED_COLUMNS, VALID_OPTIONS
)

st.set_page_config(page_title="Poll Results Visualizer", page_icon="📊", layout="wide")
st.title("📊 Poll Results Visualizer")
st.caption("Explore poll responses, compare groups, and export summaries. Synthetic data is fictional.")

uploaded = st.file_uploader("Upload a poll CSV", type=["csv"])
if uploaded is not None:
    try:
        raw = pd.read_csv(uploaded)
    except Exception as exc:
        st.error(f"Could not read the CSV: {exc}")
        st.stop()
else:
    st.info("No CSV uploaded. Showing the built-in synthetic demonstration dataset.")
    raw = create_synthetic_dataset(n=1200, seed=42)

missing = [c for c in REQUIRED_COLUMNS if c not in raw.columns]
if missing:
    st.error("The CSV is missing required columns: " + ", ".join(missing))
    st.write("Required columns:", REQUIRED_COLUMNS)
    st.stop()

clean, cleaning_report = clean_poll_data(raw)
if clean.empty:
    st.error("No valid responses were found after cleaning.")
    st.stop()

st.sidebar.header("Filters")
regions = sorted(clean["region"].dropna().unique().tolist())
ages = sorted(clean["age_group"].dropna().unique().tolist())
selected_regions = st.sidebar.multiselect("Region", regions, default=regions)
selected_ages = st.sidebar.multiselect("Age group", ages, default=ages)
filtered = clean[clean["region"].isin(selected_regions) & clean["age_group"].isin(selected_ages)]
if filtered.empty:
    st.warning("No responses match these filters. Select at least one region and age group.")
    st.stop()

summary = analyze_poll(filtered)
total = len(filtered)
winner = summary["option_summary"].iloc[0]
c1, c2, c3 = st.columns(3)
c1.metric("Valid responses", f"{total:,}")
c2.metric("Leading option", winner["selected_option"])
c3.metric("Leading share", f'{winner["share_percent"]:.1f}%')

st.subheader("Option-wise results")
st.dataframe(summary["option_summary"], use_container_width=True, hide_index=True)
left, right = st.columns(2)
with left:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=summary["option_summary"], x="selected_option", y="votes", ax=ax)
    ax.set_title("Votes by option")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
with right:
    fig, ax = plt.subplots(figsize=(7, 5))
    s = summary["option_summary"]
    ax.pie(s["votes"], labels=s["selected_option"], autopct="%1.1f%%", startangle=90)
    ax.set_title("Share of responses")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

st.subheader("Regional comparison")
st.dataframe(summary["region_pct"], use_container_width=True)
fig, ax = plt.subplots(figsize=(10, 5))
summary["region_pct"].plot(kind="bar", stacked=True, ax=ax, colormap="Set2")
ax.set_ylabel("Within-region share (%)")
ax.set_xlabel("Region")
ax.legend(title="Option", bbox_to_anchor=(1.02, 1), loc="upper left")
fig.tight_layout()
st.pyplot(fig)
plt.close(fig)

st.subheader("Demographic comparison: age group")
st.dataframe(summary["age_pct"], use_container_width=True)
fig, ax = plt.subplots(figsize=(9, 4))
sns.heatmap(summary["age_pct"], annot=True, fmt=".1f", cmap="YlGnBu", ax=ax, vmin=0, vmax=100)
fig.tight_layout()
st.pyplot(fig)
plt.close(fig)

st.subheader("Data quality")
st.json(cleaning_report)
st.subheader("Automated insights")
for _, row in summary["option_summary"].head(1).iterrows():
    st.write(f'• **{row["selected_option"]}** leads with {int(row["votes"])} votes ({row["share_percent"]:.2f}%).')
st.write(f"• {total:,} valid responses are included after filters.")
st.write("• Interpret demographic differences carefully; group sizes and sampling method matter.")

st.download_button(
    "Download filtered responses (CSV)",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_poll_responses.csv",
    mime="text/csv",
)
st.download_button(
    "Download option summary (CSV)",
    data=summary["option_summary"].to_csv(index=False).encode("utf-8"),
    file_name="option_summary.csv",
    mime="text/csv",
)
