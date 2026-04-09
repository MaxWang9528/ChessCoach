"""
ChessCoach: A Bayesian Network for coaching chess players
in the 2026 Candidates Tournament.

"""


import os
import pandas as pd
import numpy as np
from itertools import product as iter_product
import pgn_to_csv
import modify_data
import utils_pandas as upd
from colorama import Back, Style


def load_csv():
    csv_path_original = os.path.join(os.path.dirname(__file__), 'data', 'all_games_original.csv')
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'all_games.csv')
    return (pd.read_csv(csv_path_original), pd.read_csv(csv_path))


def init():
    pgn_to_csv.main()

    # data_dir = os.path.join(os.path.dirname(__file__), 'data')
    df = pd.read_csv("data/all_games_original.csv")
    df = modify_data.remove_non_traditional(df)
    df = modify_data.remove_missing_rounds(df)
    df = modify_data.truncate_rounds(df)
    df = modify_data.remove_variant_cols(df)
    df = modify_data.add_big_eco(df)
    df = modify_data.add_game_length(df)
    df = modify_data.add_win_streak(df)
    df = modify_data.add_game_features(df)

    # output_path = os.path.join(data_dir, 'all_games.csv')
    output_path = "data/all_games.csv"
    df.to_csv(output_path, index=False)
    print(f"{Back.GREEN}Saved {len(df)} games to {output_path}{Style.RESET_ALL}")


def prep_data():
    """
    prep data.

    """
    init()
    df_original, df = load_csv()
    upd.missing_round_count(df_original)
    upd.non_traditional_count(df_original)
    upd.head_to_head(df)
    # upd.eco_counts(df)
    upd.win_rates(df)
    upd.queen_trade_pct(df)
    upd.balanced_pct(df)
    upd.big_eco_counts(df)


def main():
    """ actual bayes net stuff"""
    pass




if __name__ == "__main__":
    prep_data()
    main()

