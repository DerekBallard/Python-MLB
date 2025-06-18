import pandas as pd
import matplotlib.pyplot as plt

# Load CSV file
df = pd.read_csv("mlb_data.csv")

def parse_expected(record):
    try:
        wins, losses = record.split('-')
        return int(wins), int(losses)
    except:
        return None, None

df[['expected_wins', 'expected_losses']] = df['expected_win_loss_record'].apply(
    lambda x: pd.Series(parse_expected(str(x)))
)

df.dropna(subset=['expected_wins'], inplace=True)
df['win_diff'] = df['wins'] - df['expected_wins']

# Average win difference per team
team_summary = (
    df.groupby('team_name')['win_diff']
    .mean()
    .reset_index()
    .rename(columns={'win_diff': 'avg_win_diff'})
    .sort_values(by='avg_win_diff', ascending=False)
)

top_10 = team_summary.head(10)
bottom_10 = team_summary.tail(10).sort_values(by='avg_win_diff')

# For bottom 10 teams, find worst single year
bottom_team_names = bottom_10['team_name'].tolist()
bottom_df = df[df['team_name'].isin(bottom_team_names)]
worst_years = bottom_df.loc[bottom_df.groupby('team_name')['win_diff'].idxmin()]
worst_years = worst_years.sort_values(by='win_diff')

print("Top 10 Overperforming Teams (Average Win Difference):")
print(top_10.to_string(index=False))
print("\nBottom 10 Underperforming Teams (Average Win Difference):")
print(bottom_10.to_string(index=False))
print("\nWorst Year Performances for Bottom 10 Teams:")
print(worst_years[['team_name', 'year', 'win_diff']].to_string(index=False))

# Prepare data for combined plotting

# For top 10 teams, create 'team_year' label and keep avg_win_diff
top_10_plot = top_10.copy()
top_10_plot['year'] = 'Avg'
top_10_plot['team_year'] = top_10_plot['team_name'] + " " + top_10_plot['year'].astype(str)
top_10_plot.rename(columns={'avg_win_diff': 'win_diff'}, inplace=True)
top_10_plot['type'] = 'Top Overperformer'

# For bottom 10 teams, use worst year data with 'team_year' label
bottom_plot = worst_years.copy()
bottom_plot['team_year'] = bottom_plot['team_name'] + " " + bottom_plot['year'].astype(str)
bottom_plot['type'] = 'Bottom Underperformer'

# Select only needed columns
bottom_plot = bottom_plot[['team_year', 'win_diff', 'type']]
top_10_plot = top_10_plot[['team_year', 'win_diff', 'type']]

# Combine and sort by win_diff descending
combined = pd.concat([top_10_plot, bottom_plot], ignore_index=True)
combined = combined.sort_values(by='win_diff', ascending=False)

# Plot
plt.figure(figsize=(16,7))
colors = combined['type'].map({'Top Overperformer': 'green', 'Bottom Underperformer': 'red'})

plt.bar(combined['team_year'], combined['win_diff'], color=colors)
plt.xticks(rotation=45, ha='right')
plt.ylabel('Win Difference (Actual - Expected)')
plt.title('Top 10 Overperforming vs Bottom 10 Underperforming Teams (Ordered)')
plt.tight_layout()
plt.show()
