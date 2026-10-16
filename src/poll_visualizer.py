"""Reusable data creation, cleaning, analysis, visualization and reporting functions."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

REQUIRED_COLUMNS = [
    "respondent_id", "response_date", "question", "selected_option",
    "region", "age_group", "gender"
]
VALID_OPTIONS = ["Dark Mode", "AI Assistant", "Faster Performance", "Custom Themes"]
QUESTION = "Which feature would you most like in our next mobile app update?"

def create_synthetic_dataset(n=1200, seed=42):
    """Create reproducible, fictional poll responses. These are not real survey results."""
    rng = np.random.default_rng(seed)
    regions = np.array(["North", "South", "East", "West", "Central"])
    age_groups = np.array(["18-24", "25-34", "35-44", "45+"])
    genders = np.array(["Woman", "Man", "Non-binary", "Prefer not to say"])
    dates = pd.date_range("2026-01-01", "2026-03-31", freq="D")

    region = rng.choice(regions, n, p=[.22, .24, .16, .22, .16])
    age = rng.choice(age_groups, n, p=[.34, .32, .20, .14])
    gender = rng.choice(genders, n, p=[.47, .45, .03, .05])
    response_dates = rng.choice(dates, n)

    # Preference probabilities vary by age group and region to create useful comparisons.
    probs = {
        "18-24": [.22, .38, .20, .20],
        "25-34": [.24, .30, .30, .16],
        "35-44": [.20, .20, .40, .20],
        "45+": [.18, .15, .47, .20],
    }
    selected = []
    for a, r in zip(age, region):
        p = np.array(probs[a], dtype=float)
        if r == "South":
            p[1] += .06
        elif r == "West":
            p[2] += .05
        elif r == "East":
            p[3] += .04
        p = p / p.sum()
        selected.append(rng.choice(VALID_OPTIONS, p=p))

    df = pd.DataFrame({
        "respondent_id": [f"R{i:05d}" for i in range(1, n + 1)],
        "response_date": pd.to_datetime(response_dates).strftime("%Y-%m-%d"),
        "question": QUESTION,
        "selected_option": selected,
        "region": region,
        "age_group": age,
        "gender": gender,
    })
    # Add a small number of deliberately imperfect rows for the cleaning demonstration.
    if n >= 100:
        df.loc[3, "region"] = " north "
        df.loc[7, "selected_option"] = "  " + str(df.loc[7, "selected_option"]).lower() + " "
        df.loc[11, "age_group"] = None
        df.loc[15, "respondent_id"] = df.loc[14, "respondent_id"]  # duplicate ID
    return df

def load_poll_data(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError("Input CSV is missing required columns: " + ", ".join(missing))
    return df

def clean_poll_data(raw):
    """Clean input and return (cleaned_df, report)."""
    df = raw.copy()
    original_rows = len(df)
    missing_columns = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_columns:
        raise ValueError("Missing required columns: " + ", ".join(missing_columns))

    for col in ["respondent_id", "question", "selected_option", "region", "age_group", "gender"]:
        df[col] = df[col].astype("string").str.strip()

    df["response_date"] = pd.to_datetime(df["response_date"], errors="coerce")
    df["selected_option"] = df["selected_option"].str.lower().str.strip()
    option_map = {o.lower(): o for o in VALID_OPTIONS}
    df["selected_option"] = df["selected_option"].map(option_map)
    df["region"] = df["region"].str.title()
    df["age_group"] = df["age_group"].replace({"<NA>": pd.NA, "nan": pd.NA})
    df["gender"] = df["gender"].replace({"<NA>": pd.NA, "nan": pd.NA})

    before_dedup = len(df)
    # Respondent IDs are expected to be unique for this one-question poll.
    df = df.drop_duplicates(subset=["respondent_id"], keep="first")
    duplicate_rows_removed = before_dedup - len(df)

    before_valid = len(df)
    df = df.dropna(subset=["respondent_id", "response_date", "question", "selected_option", "region"])
    invalid_rows_removed = before_valid - len(df)

    # Fill optional demographic blanks with an explicit label rather than silently dropping responses.
    for col in ["age_group", "gender"]:
        df[col] = df[col].fillna("Unknown")
        df[col] = df[col].replace({"": "Unknown", "<NA>": "Unknown"})

    report = {
        "original_rows": int(original_rows),
        "duplicate_rows_removed": int(duplicate_rows_removed),
        "invalid_required_rows_removed": int(invalid_rows_removed),
        "cleaned_rows": int(len(df)),
        "rows_removed_total": int(original_rows - len(df)),
    }
    return df.reset_index(drop=True), report

def analyze_poll(df):
    if df.empty:
        raise ValueError("No valid poll responses remain after cleaning.")
    total = len(df)
    option_summary = (
        df["selected_option"].value_counts()
        .rename_axis("selected_option").reset_index(name="votes")
    )
    option_summary["share_percent"] = (option_summary["votes"] / total * 100).round(2)
    option_summary["total_responses"] = total
    option_summary = option_summary.sort_values(["votes", "selected_option"], ascending=[False, True])

    region_counts = pd.crosstab(df["region"], df["selected_option"])
    region_pct = pd.crosstab(df["region"], df["selected_option"], normalize="index").mul(100).round(2)
    age_counts = pd.crosstab(df["age_group"], df["selected_option"])
    age_pct = pd.crosstab(df["age_group"], df["selected_option"], normalize="index").mul(100).round(2)
    trend = (
        df.assign(response_day=df["response_date"].dt.to_period("W").dt.start_time)
        .groupby("response_day").size().reset_index(name="responses")
        .sort_values("response_day")
    )
    return {
        "option_summary": option_summary,
        "region_counts": region_counts,
        "region_pct": region_pct,
        "age_counts": age_counts,
        "age_pct": age_pct,
        "trend": trend,
    }

def create_visualizations(df, summaries, images_dir):
    images_dir = Path(images_dir)
    images_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    summary = summaries["option_summary"]
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=summary, x="selected_option", y="votes", ax=ax)
    ax.set_title("Poll Votes by Option")
    ax.set_xlabel("Selected option")
    ax.set_ylabel("Number of votes")
    ax.tick_params(axis="x", rotation=18)
    fig.tight_layout()
    fig.savefig(images_dir / "vote_bar_chart.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(summary["votes"], labels=summary["selected_option"], autopct="%1.1f%%", startangle=90)
    ax.set_title("Share of Poll Responses")
    fig.tight_layout()
    fig.savefig(images_dir / "vote_pie_chart.png", dpi=160)
    plt.close(fig)

    region_pct = summaries["region_pct"]
    fig, ax = plt.subplots(figsize=(11, 6))
    region_pct.plot(kind="bar", stacked=True, ax=ax, colormap="Set2")
    ax.set_title("Option Preference by Region (100% stacked)")
    ax.set_xlabel("Region")
    ax.set_ylabel("Share of responses (%)")
    ax.legend(title="Selected option", bbox_to_anchor=(1.02, 1), loc="upper left")
    fig.tight_layout()
    fig.savefig(images_dir / "region_stacked_chart.png", dpi=160)
    plt.close(fig)

    age_pct = summaries["age_pct"]
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(age_pct, annot=True, fmt=".1f", cmap="YlGnBu", ax=ax, vmin=0, vmax=100)
    ax.set_title("Option Preference by Age Group (%)")
    ax.set_xlabel("Selected option")
    ax.set_ylabel("Age group")
    fig.tight_layout()
    fig.savefig(images_dir / "demographic_heatmap.png", dpi=160)
    plt.close(fig)

    trend = summaries["trend"]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(trend["response_day"], trend["responses"], marker="o")
    ax.set_title("Weekly Response Volume")
    ax.set_xlabel("Week starting")
    ax.set_ylabel("Responses")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(images_dir / "response_trend.png", dpi=160)
    plt.close(fig)

def generate_insights(df, summaries):
    summary = summaries["option_summary"]
    winner = summary.iloc[0]
    total = len(df)
    insights = [
        f'The most selected option is "{winner["selected_option"]}" with {int(winner["votes"]):,} votes ({winner["share_percent"]:.2f}% of valid responses).',
        f"A total of {total:,} valid responses were analyzed.",
    ]
    if len(summary) > 1:
        gap = int(summary.iloc[0]["votes"] - summary.iloc[1]["votes"])
        insights.append(f'The leading option is ahead of the second-place option by {gap:,} votes.')
    region_pct = summaries["region_pct"]
    if not region_pct.empty:
        for region in region_pct.index:
            top_option = region_pct.loc[region].idxmax()
            top_share = region_pct.loc[region].max()
            insights.append(f'In the {region} region, "{top_option}" has the highest within-region share ({top_share:.1f}%).')
    insights.append("These are descriptive results from the supplied dataset; synthetic data is fictional and should not be presented as real public opinion.")
    return insights

def save_outputs(df, summaries, insights, cleaning_report, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_dir / "cleaned_poll_responses.csv", index=False)
    for name, table in summaries.items():
        table.to_csv(output_dir / f"{name}.csv", index=True if name.endswith("_counts") or name.endswith("_pct") else False)
    (output_dir / "insights.txt").write_text("\n".join(f"- {x}" for x in insights), encoding="utf-8")
    (output_dir / "cleaning_report.json").write_text(json.dumps(cleaning_report, indent=2), encoding="utf-8")
