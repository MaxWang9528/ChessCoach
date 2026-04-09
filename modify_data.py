"""
Add or remove data to the big csv derived from existing data
"""

import os
import re
import chess
import pandas as pd
from colorama import Back, Style

PIECE_VALUE = {
    chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
    chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0,
}

# (range_start, range_end, bigECO_label)
BIG_ECO_RANGES = [
    ("A00", "A00", "A00 Polish (Sokolsky) opening"),
    ("A01", "A01", "A01 Nimzovich-Larsen attack"),
    ("A02", "A03", "A02-A03 Bird's opening"),
    ("A04", "A09", "A04-A09 Reti opening"),
    ("A10", "A39", "A10-A39 English opening"),
    ("A40", "A41", "A40-A41 Queen's pawn"),
    ("A42", "A42", "A42 Modern defence, Averbakh system"),
    ("A43", "A44", "A43-A44 Old Benoni defence"),
    ("A45", "A46", "A45-A46 Queen's pawn game"),
    ("A47", "A47", "A47 Queen's Indian defence"),
    ("A48", "A49", "A48-A49 King's Indian, East Indian defence"),
    ("A50", "A50", "A50 Queen's pawn game"),
    ("A51", "A52", "A51-A52 Budapest defence"),
    ("A53", "A55", "A53-A55 Old Indian defence"),
    ("A56", "A56", "A56 Benoni defence"),
    ("A57", "A59", "A57-A59 Benko gambit"),
    ("A60", "A79", "A60-A79 Benoni defence"),
    ("A80", "A99", "A80-A99 Dutch"),
    ("B00", "B00", "B00 King's pawn opening"),
    ("B01", "B01", "B01 Scandinavian defence"),
    ("B02", "B05", "B02-B05 Alekhine's defence"),
    ("B06", "B06", "B06 Robatsch (modern) defence"),
    ("B07", "B09", "B07-B09 Pirc defence"),
    ("B10", "B19", "B10-B19 Caro-Kann defence"),
    ("B20", "B99", "B20-B99 Sicilian defence"),
    ("C00", "C19", "C00-C19 French defence"),
    ("C20", "C20", "C20 King's pawn game"),
    ("C21", "C22", "C21-C22 Centre game"),
    ("C23", "C24", "C23-C24 Bishop's opening"),
    ("C25", "C29", "C25-C29 Vienna game"),
    ("C30", "C39", "C30-C39 King's gambit"),
    ("C40", "C40", "C40 King's knight opening"),
    ("C41", "C41", "C41 Philidor's defence"),
    ("C42", "C43", "C42-C43 Petrov's defence"),
    ("C44", "C44", "C44 King's pawn game"),
    ("C45", "C45", "C45 Scotch game"),
    ("C46", "C46", "C46 Three knights game"),
    ("C47", "C49", "C47-C49 Four knights, Scotch variation"),
    ("C50", "C50", "C50 Italian Game"),
    ("C51", "C52", "C51-C52 Evans gambit"),
    ("C53", "C54", "C53-C54 Giuoco Piano"),
    ("C55", "C59", "C55-C59 Two knights defence"),
    ("C60", "C99", "C60-C99 Ruy Lopez (Spanish opening)"),
    ("D00", "D00", "D00 Queen's pawn game"),
    ("D01", "D01", "D01 Richter-Veresov attack"),
    ("D02", "D03", "D02 Queen's pawn game"),
    ("D04", "D05", "D04-D05 Queen's pawn game"),
    ("D06", "D06", "D06 Queen's Gambit"),
    ("D07", "D09", "D07-D09 QGD, Chigorin defence"),
    ("D10", "D15", "D10-D15 QGD Slav defence"),
    ("D16", "D16", "D16 QGD Slav accepted, Alapin variation"),
    ("D17", "D19", "D17-D19 QGD Slav, Czech defence"),
    ("D20", "D29", "D20-D29 Queen's gambit accepted"),
    ("D30", "D42", "D30-D42 Queen's gambit declined"),
    ("D43", "D49", "D43-D49 QGD semi-Slav"),
    ("D50", "D69", "D50-D69 QGD, 4.Bg5"),
    ("D70", "D79", "D70-D79 Neo-Gruenfeld defence"),
    ("D80", "D99", "D80-D99 Gruenfeld defence"),
    ("E00", "E00", "E00 Queen's pawn game"),
    ("E01", "E09", "E01-E09 Catalan, closed"),
    ("E10", "E10", "E10 Queen's pawn game"),
    ("E11", "E11", "E11 Bogo-Indian defence"),
    ("E12", "E19", "E12-E19 Queen's Indian defence"),
    ("E20", "E59", "E20-E59 Nimzo-Indian defence"),
    ("E60", "E99", "E60-E99 King's Indian defence"),
]


def eco_to_big_eco(eco):
    if pd.isna(eco):
        return None
    eco = eco.strip()
    for start, end, label in BIG_ECO_RANGES:
        if start <= eco <= end:
            return label
    return None


def add_big_eco(df):
    df['bigECO'] = df['ECO'].apply(eco_to_big_eco)
    print(f"{Back.CYAN}add_big_eco done{Style.RESET_ALL}")
    return df


def remove_non_traditional(df):
    """Chess960 games etc"""
    mask = pd.Series(False, index=df.index)
    if 'Variant' in df.columns:
        mask = mask | df['Variant'].notna()
    if 'FEN' in df.columns:
        mask = mask | df['FEN'].notna()
    df = df[~mask].reset_index(drop=True)
    print(f"{Back.CYAN}remove_non_traditional done{Style.RESET_ALL}")
    return df


def remove_missing_rounds(df):
    """Remove games with missing or unknown round values."""
    mask = df['Round'].isna() | (df['Round'].astype(str).str.strip().isin(['', '?']))
    df = df[~mask].reset_index(drop=True)
    print(f"{Back.CYAN}remove_missing_rounds done{Style.RESET_ALL}")
    return df


def _get_game_length(moves):
    if pd.isna(moves):
        return None
    move_numbers = re.findall(r'(\d+)\.', moves)
    if not move_numbers:
        return None
    return int(move_numbers[-1])


def add_game_length(df):
    """Determine game length with PGN"""
    df['GameLength'] = df['Moves'].apply(_get_game_length)
    print(f"{Back.CYAN}add_game_length done{Style.RESET_ALL}")
    return df


def truncate_rounds(df):
    """Remove everything after the first '.'
    4.2 means round 4 board 2. There are some in the format x.x.x,
    idk what that means... ignore for now."""
    df['Round'] = df['Round'].astype(str).str.split('.').str[0]
    print(f"{Back.CYAN}truncate_rounds done{Style.RESET_ALL}")
    return df


def remove_variant_cols(df):
    """Remove Variant, FEN, and SetUp columns if present."""
    to_drop = [col for col in ['Variant', 'FEN', 'SetUp'] if col in df.columns]
    df = df.drop(columns=to_drop)
    print(f"{Back.CYAN}remove_variant_cols done{Style.RESET_ALL}")
    return df


def _analyze_game(moves_str, threshold=3, persist=4):
    """Single-pass replay: compute QueenTraded, OppositeCastle, Balanced."""
    if pd.isna(moves_str):
        return False, False, True

    moves_str = re.sub(r'\s*(1-0|0-1|1/2-1/2|\*)\s*$', '', moves_str)
    sans = [t for t in moves_str.split() if not re.match(r'^\d+\.+$', t)]
    if not sans:
        return False, False, True

    board = chess.Board()
    queen_traded = False
    white_castle = black_castle = None
    balance = 0
    streak = 0
    balanced = True

    for san in sans:
        try:
            move = board.parse_san(san)
        except (chess.InvalidMoveError, chess.AmbiguousMoveError):
            break

        # Castling (check before push — board.turn is the side to move)
        if board.is_kingside_castling(move):
            if board.turn == chess.WHITE:
                white_castle = 'K'
            else:
                black_castle = 'K'
        elif board.is_queenside_castling(move):
            if board.turn == chess.WHITE:
                white_castle = 'Q'
            else:
                black_castle = 'Q'

        # Material balance (check before push to see captured piece)
        if board.is_capture(move):
            if board.is_en_passant(move):
                cap_val = 1
            else:
                captured = board.piece_at(move.to_square)
                cap_val = PIECE_VALUE[captured.piece_type] if captured else 0
            if board.turn == chess.WHITE:
                balance += cap_val
            else:
                balance -= cap_val
        if move.promotion:
            diff = PIECE_VALUE[move.promotion] - PIECE_VALUE[chess.PAWN]
            if board.turn == chess.WHITE:
                balance += diff
            else:
                balance -= diff

        board.push(move)

        # Queen trade (check after push)
        if not queen_traded:
            if not board.pieces(chess.QUEEN, chess.WHITE) \
               and not board.pieces(chess.QUEEN, chess.BLACK):
                queen_traded = True

        # Balance streak
        if balanced:
            if abs(balance) >= threshold:
                streak += 1
                if streak >= persist:
                    balanced = False
            else:
                streak = 0

    opp_castle = (white_castle is not None and black_castle is not None
                  and white_castle != black_castle)
    return queen_traded, opp_castle, balanced


def add_game_features(df):
    """Add QueenTraded, OppositeCastle, Balanced in one replay pass."""
    results = df['Moves'].apply(_analyze_game)
    df['QueenTraded'] = results.apply(lambda r: r[0])
    df['OppositeCastle'] = results.apply(lambda r: r[1])
    df['Balanced'] = results.apply(lambda r: r[2])
    print(f"{Back.CYAN}add_game_features done (QueenTraded, OppositeCastle, Balanced){Style.RESET_ALL}")
    return df


def _compute_streak(results):
    """
    Compute the win/lose streak coming into each game.
    Returns a list of streak values (one per game).
    Positive = win streak, negative = lose streak, 0 = no streak (after draw or start).
    """
    streaks = []
    current_streak = 0
    for result in results:
        streaks.append(current_streak)
        if result == 'win':
            current_streak = current_streak + 1 if current_streak > 0 else 1
        elif result == 'loss':
            current_streak = current_streak - 1 if current_streak < 0 else -1
        else:
            current_streak = 0
    return streaks


def add_win_streak(df):
    """Add WhiteStreak and BlackStreak columns.
    Each is the streak of that player coming into the game, based on date and round order.
    """
    df = df.copy()

    # Build per-player game history: (original_index, date, round, result_for_player)
    player_games = {}
    for idx, row in df.iterrows():
        date, rk = row['Date'], int(row['Round'])
        white, black, result = row['White'], row['Black'], row['Result']

        if result == '1-0':
            w_res, b_res = 'win', 'loss'
        elif result == '0-1':
            w_res, b_res = 'loss', 'win'
        else:
            w_res, b_res = 'draw', 'draw'

        player_games.setdefault(white, []).append((idx, date, rk, w_res))
        player_games.setdefault(black, []).append((idx, date, rk, b_res))

    # Compute streaks per player
    white_streaks = {}
    black_streaks = {}
    # AAAHHHH
    for player, games in player_games.items():
        games.sort(key=lambda x: (x[1], x[2]))
        results = [g[3] for g in games]
        streaks = _compute_streak(results)
        for (idx, _, _, _), streak in zip(games, streaks):
            row = df.loc[idx]
            if row['White'] == player:
                white_streaks[idx] = streak
            else:
                black_streaks[idx] = streak

    df['WhiteStreak'] = pd.Series(white_streaks)
    df['BlackStreak'] = pd.Series(black_streaks)
    print(f"{Back.CYAN}add_win_streak done{Style.RESET_ALL}")
    return df


