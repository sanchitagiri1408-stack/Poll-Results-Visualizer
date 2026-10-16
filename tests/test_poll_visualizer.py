import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.poll_visualizer import create_synthetic_dataset, clean_poll_data, analyze_poll

def test_synthetic_data_has_required_columns():
    df = create_synthetic_dataset(n=100, seed=7)
    assert {"respondent_id", "response_date", "selected_option", "region", "age_group"}.issubset(df.columns)

def test_cleaning_removes_duplicate_ids():
    raw = create_synthetic_dataset(n=100, seed=7)
    clean, report = clean_poll_data(raw)
    assert clean["respondent_id"].is_unique
    assert report["cleaned_rows"] <= report["original_rows"]

def test_option_percentages_sum_to_100():
    raw = create_synthetic_dataset(n=200, seed=7)
    clean, _ = clean_poll_data(raw)
    summary = analyze_poll(clean)["option_summary"]
    assert round(summary["share_percent"].sum(), 1) == 100.0
