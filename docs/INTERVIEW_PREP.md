# Interview Preparation

## HR / non-technical explanation

“I built a Poll Results Visualizer using Python to turn raw survey responses into clean summaries and charts. It can generate demonstration data or accept a CSV file. It calculates vote counts and percentages, compares preferences across regions and age groups, and produces a Streamlit dashboard. I also documented data-cleaning decisions and made it clear that the included sample data is synthetic.”

## Technical explanation

“The pipeline separates data generation/loading, cleaning, aggregation, visualization and report export into reusable functions. Pandas handles tabular transformations and crosstabs, NumPy generates reproducible sample data, Matplotlib and Seaborn create static charts, and Streamlit provides interactive filtering. I test important properties, including unique respondent IDs after cleaning and percentages summing to 100%.”

## Ten interview questions and sample answers

1. **What problem does the project solve?**  
   It automates repetitive survey summarization and makes response patterns easier to communicate through charts and tables.

2. **Why use Pandas?**  
   Pandas provides convenient CSV input, missing-value handling, category transformations, grouping, and crosstab operations.

3. **How do you calculate vote share?**  
   For a single-choice poll, option share = option vote count / total valid responses × 100.

4. **How do you handle missing data?**  
   Missing required fields are excluded because they prevent reliable vote classification. Missing optional demographic fields are labelled Unknown so those votes can still be counted.

5. **Why remove duplicate respondent IDs?**  
   The example assumes one response per respondent. The assumption must be changed if the survey permits multiple submissions.

6. **Why use a 100% stacked bar chart?**  
   It compares within-region preference distributions even when the number of responses per region differs.

7. **What is EDA?**  
   Exploratory Data Analysis uses summaries and visualizations to understand distributions, spot data-quality issues and identify patterns before drawing conclusions.

8. **Can the leading option be called the winner?**  
   It is the most selected option in this dataset. Whether it represents a broader population depends on sampling, response bias, sample size and uncertainty.

9. **What are the limitations?**  
   The built-in data is synthetic, the basic pipeline analyzes one single-choice question, and the current analysis is descriptive rather than causal.

10. **How would you improve it?**  
    Add multi-question support, confidence intervals, weighted results, privacy-aware text analysis, API/database ingestion and deployment monitoring.
