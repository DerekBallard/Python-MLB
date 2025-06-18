import pandas as pd

# Load CSV file
df = pd.read_csv("mlb_data.csv")

# --- Parse expected_win_loss_record ('92-70' → 92 and 70) ---
def parse_expected(record):
    try:
        wins, losses = record.split('-')
        return int(wins), int(losses)
    except:
        return None, None

df[['expected_wins', 'expected_losses']] = df['expected_win_loss_record'].apply(
    lambda x: pd.Series(parse_expected(str(x)))
)

# Drop rows where parsing failed
df.dropna(subset=['expected_wins'], inplace=True)

# Calculate the difference between actual and expected wins
df['win_diff'] = df['wins'] - df['expected_wins']

# --- Team-level summary ---
team_summary = (
    df.groupby('team_name')['win_diff']
    .mean()
    .reset_index()
    .rename(columns={'win_diff': 'avg_win_diff'})
    .sort_values(by='avg_win_diff', ascending=False)
)

print("Top overperformers by average win difference:")
print(team_summary.head(10))

print("\nBiggest underperformers:")
print(team_summary.tail(10))

# Optional: Save summary to CSV
team_summary.to_csv("team_win_diff_summary.csv", index=False)
