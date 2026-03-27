"""
Convert the 8 original pgn files into one large csv file. No new data is added, and original data is preserved.

"""


import os
import re
import glob
import pandas as pd
import numpy as np
from itertools import product as iter_product


def pgn_to_df(pgn_path):
    with open(pgn_path, 'r', encoding='latin-1') as f:
        content = f.read()

    games = []
    # Split into individual games by finding sequences of header tags
    # Each game starts with [Event ...] after a blank section
    game_chunks = re.split(r'\n(?=\[Event )', content.strip())

    for chunk in game_chunks:
        if not chunk.strip():
            continue
        game = {}
        # Extract all header tags
        headers = re.findall(r'\[(\w+)\s+"([^"]*)"\]', chunk)
        for key, value in headers:
            game[key] = value

        # Extract moves: everything after the last header line
        lines = chunk.strip().split('\n')
        move_lines = []
        for line in lines:
            if not line.startswith('[') and line.strip():
                move_lines.append(line.strip())
        game['Moves'] = ' '.join(move_lines)

        games.append(game)

    df = pd.DataFrame(games)
    return df


def main():
    pgn_dir = os.path.join(os.path.dirname(__file__), 'data')
    paths = sorted(glob.glob(os.path.join(pgn_dir, '*.pgn')))

    dfs = []
    for path in paths:
        df = pgn_to_df(path)
        dfs.append(df)
        print(f"Loaded {os.path.basename(path)}: {len(df)} games")

    combined = pd.concat(dfs, ignore_index=True)
    print(f"\nTotal games: {len(combined)}")

    output_path = os.path.join(pgn_dir, 'all_games_original.csv')
    combined.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")
