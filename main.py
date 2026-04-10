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
import net

def load_csv():
    csv_path_original = os.path.join(os.path.dirname(__file__), "data", "all_games_original.csv")
    csv_path = os.path.join(os.path.dirname(__file__), "data", "all_games.csv")
    return (pd.read_csv(csv_path_original), pd.read_csv(csv_path))


def init():
    pgn_to_csv.main()

    # data_dir = os.path.join(os.path.dirname(__file__), "data")
    df = pd.read_csv("data/all_games_original.csv")
    df = modify_data.remove_non_traditional(df)
    df = modify_data.remove_missing_rounds(df)
    df = modify_data.truncate_rounds(df)
    df = modify_data.remove_variant_cols(df)
    df = modify_data.add_big_eco(df)
    df = modify_data.add_game_length(df)
    df = modify_data.add_win_streak(df)
    df = modify_data.add_game_features(df)

    # output_path = os.path.join(data_dir, "all_games.csv")
    output_path = "data/all_games.csv"
    df.to_csv(output_path, index=False)
    print(f"{Back.GREEN}Saved {len(df)} games to {output_path}{Style.RESET_ALL}")


def prep_data():
    """
    prep data. Also use pandas utils to print some stats

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


def save_cpds(df):
    # save untruncated version of cpds to txt file for testing
    players = upd.find_players(df)
    for player in players:
        last_name = player.split(",")[0].strip().lower()
        for color in ["White", "Black"]:
            model = net.Net(df, player, color)
            model.print_cpds(path=f"data/cpd_{last_name}_{color.lower()}.txt")  # just some formatting


def test(df):
    # BE=B20-B99 Naka white
    naka_white = df[df["White"] == "Nakamura, Hikaru"]
    total = len(naka_white)
    b20_99 = len(naka_white[naka_white["BigECO"] == "B20-B99 Sicilian defence"])
    print(f"BigECO test | BE=B20-B99 | Naka White | {b20_99/total:}")

    # QT=False, BE=B10-B19 Naka white
    naka_white_b10 = naka_white[naka_white["BigECO"] == "B10-B19 Caro-Kann defence"]
    total_b10 = len(naka_white_b10)
    qt_false = len(naka_white_b10[naka_white_b10["QueenTraded"] == False])
    print(f"QT test | BE=B10-B19 | QT=F | Naka White | {qt_false/total_b10:}")

    # Bal=True, BE=C45 Caruana black
    caru_black = df[df["Black"] == "Caruana, Fabiano"]
    caru_black_c45 = caru_black[caru_black["BigECO"] == "C45 Scotch game"]
    total_c45 = len(caru_black_c45)
    bal_true = len(caru_black_c45[caru_black_c45["Balanced"] == True])
    print(f"Bal test | BE=C45 | Bal=T | Caruana Black | {bal_true/total_c45:}")





def main():
    df = pd.read_csv("data/all_games.csv")
    # save_cpds(df)
    # test(df)
    model = net.Net(df, "Nakamura, Hikaru", "White")
    result = model.query(["Result"], {"BigECO": "B20-B99 Sicilian defence", "WhiteStreak": "Negative", "BlackStreak": "Positive"})
    print(result)


if __name__ == "__main__":
    # prep_data()
    main()

