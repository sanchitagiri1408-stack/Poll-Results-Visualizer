"""Command-line entry point for Poll Results Visualizer."""
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.poll_visualizer import (
    create_synthetic_dataset, load_poll_data, clean_poll_data,
    analyze_poll, create_visualizations, generate_insights, save_outputs
)

def main():
    parser = argparse.ArgumentParser(description="Analyze poll results from a CSV file.")
    parser.add_argument("--input", type=str, default="", help="Path to input CSV. If omitted, synthetic data is generated.")
    parser.add_argument("--generate", action="store_true", help="Generate a fresh synthetic poll dataset.")
    args = parser.parse_args()

    data_dir = ROOT / "data"
    output_dir = ROOT / "outputs"
    images_dir = ROOT / "images"
    data_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    images_dir.mkdir(exist_ok=True)

    if args.input:
        raw = load_poll_data(Path(args.input))
        print(f"Loaded input file: {args.input}")
    else:
        synthetic_path = data_dir / "synthetic_poll_responses.csv"
        if args.generate or not synthetic_path.exists():
            raw = create_synthetic_dataset(n=1200, seed=42)
            raw.to_csv(synthetic_path, index=False)
            print(f"Created synthetic dataset: {synthetic_path}")
        else:
            raw = load_poll_data(synthetic_path)
            print(f"Loaded existing synthetic dataset: {synthetic_path}")

    print(f"Raw rows: {len(raw):,}")
    clean, cleaning_report = clean_poll_data(raw)
    summaries = analyze_poll(clean)
    create_visualizations(clean, summaries, images_dir)
    insights = generate_insights(clean, summaries)
    save_outputs(clean, summaries, insights, cleaning_report, output_dir)

    print("\n=== POLL RESULTS SUMMARY ===")
    print(summaries["option_summary"].to_string(index=False))
    print("\n=== AUTOMATED INSIGHTS ===")
    for item in insights:
        print(f"- {item}")
    print(f"\nCleaned rows: {len(clean):,}")
    print(f"Outputs saved in: {output_dir}")
    print(f"Charts saved in: {images_dir}")

if __name__ == "__main__":
    main()
