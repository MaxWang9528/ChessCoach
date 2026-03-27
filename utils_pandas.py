"""
Get stats from the one large csv file. Does not modify the csv.
"""


import os
import pandas as pd


PLAYERS = [
    "Nakamura, Hikaru",
    "Caruana, Fabiano",
    "Giri, Anish",
    "Bluebaum, Matthias",
    "Sindarov, Javokhir",
    "Wei, Yi",
    "Esipenko, Andrey",
    "Praggnanandhaa R",
]



def find_players(df):
    """Match PLAYERS list to exact names in the dataset."""
    all_names = set(df['White'].unique()) | set(df['Black'].unique())
    matched = []
    for p in PLAYERS:
        for name in all_names:
            if name.strip().startswith(p):
                matched.append(name)
                break
    return sorted(set(matched))


def head_to_head(df):
    """Count how many games each of the 8 players has played against every other player."""
    player_names = find_players(df)

    # Build head-to-head matrix
    h2h = pd.DataFrame(0, index=player_names, columns=player_names)

    for _, row in df.iterrows():
        w, b = row['White'], row['Black']
        if w in player_names and b in player_names:
            h2h.loc[w, b] += 1
            h2h.loc[b, w] += 1

    print("=== Head-to-Head Game Counts ===")
    print(h2h.to_string())
    print()


def eco_counts(df):
    """Count ECO codes for every player (as White and Black combined)."""
    player_names = find_players(df)

    print("=== ECO Counts Per Player ===")
    for player in player_names:
        mask = (df['White'] == player) | (df['Black'] == player)
        player_games = df[mask]
        counts = player_games['ECO'].value_counts()
        print(f"\n{player}:")
        print(counts.to_string())
    print()


def big_eco_counts(df):
    """Count bigECO categories for every player (as White and Black combined)."""
    player_names = find_players(df)

    print("=== bigECO Counts Per Player ===")
    for player in player_names:
        mask = (df['White'] == player) | (df['Black'] == player)
        player_games = df[mask]
        counts = player_games['bigECO'].value_counts()
        print(f"\n{player}:")
        print(counts.to_string())
    print()


def non_traditional_count(df):
    """Count non-traditional games by checking Variant and FEN columns."""
    variant_mask = df['Variant'].notna() if 'Variant' in df.columns else pd.Series(False, index=df.index)
    fen_mask = df['FEN'].notna() if 'FEN' in df.columns else pd.Series(False, index=df.index)
    mask = variant_mask | fen_mask
    count = mask.sum()
    print(f"=== Non-Traditional Games: {count} ===")
    if 'Variant' in df.columns:
        print(df.loc[mask, 'Variant'].value_counts().to_string())
    print()


def missing_round_count(df):
    """Count entries missing a round value."""
    missing = df['Round'].isna() | (df['Round'].astype(str).str.strip().isin(['', '?']))
    count = missing.sum()
    print(f"=== Missing Round Entries: {count} ===")
    print()


def win_rates(df):
    """Calculate win rate for every player."""
    player_names = find_players(df)

    print("=== Win Rates ===")
    results = []
    for player in player_names:
        white_games = df[df['White'] == player]
        black_games = df[df['Black'] == player]

        white_wins = (white_games['Result'] == '1-0').sum()
        black_wins = (black_games['Result'] == '0-1').sum()
        white_draws = (white_games['Result'] == '1/2-1/2').sum()
        black_draws = (black_games['Result'] == '1/2-1/2').sum()
        white_losses = (white_games['Result'] == '0-1').sum()
        black_losses = (black_games['Result'] == '1-0').sum()

        total_wins = white_wins + black_wins
        total_draws = white_draws + black_draws
        total_losses = white_losses + black_losses
        total_games = len(white_games) + len(black_games)

        win_rate = total_wins / total_games * 100 if total_games > 0 else 0
        draw_rate = total_draws / total_games * 100 if total_games > 0 else 0
        loss_rate = total_losses / total_games * 100 if total_games > 0 else 0

        results.append({
            'Player': player,
            'Games': total_games,
            'Wins': total_wins,
            'Draws': total_draws,
            'Losses': total_losses,
            'Win%': round(win_rate, 1),
            'Draw%': round(draw_rate, 1),
            'Loss%': round(loss_rate, 1),
        })

    results_df = pd.DataFrame(results).sort_values('Win%', ascending=False)
    print(results_df.to_string(index=False))
    print()
